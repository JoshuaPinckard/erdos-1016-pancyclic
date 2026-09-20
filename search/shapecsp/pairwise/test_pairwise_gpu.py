"""GPU exact-set evidence for gpu_search_pairwise.  Prints counts.

  VISIT     the compositions the kernel visits for prefix ranks 0..total-1, in
            visiting order, equal pairwise_tables.iterate_compositions (which
            test_pairwise_tables.py already equates with the plain reference
            recursion), and as a SET equal the reference recursion directly:
            no duplicates, nothing missing, nothing extra.
  ORDER     every case runs twice: once with the natural arc order and once with
            a reversed one, which sends the kernel permuted form masks, permuted
            lows and a different Tlast, and whose arc vectors must come back in
            natural order.  Both must visit the same SET and the same SAT count.
  BLOCK     the visited rows are exactly the per-prefix completion blocks in
            prefix-rank order.
  VERIFY    on a bounded sample per case, the kernel's SAT flag equals
            search/verify.py pancyclic.
  SAT       the kernel's SAT flag equals the CPU coverage rule on every visited
            composition, and the number of SAT compositions equals the CPU count.
  COUNT     the kernel's compositions counter equals total_compositions.
  CONTROLS  gpu_search_pairwise.controls: both real witnesses lie in A, are hit
            at their prefix rank, and 44 sampled prefix ranks unrank identically
            on CPU and GPU with flags equal to search/verify.py.
  FAMILY    all 27 family witnesses n=41..67 are admissible and are found.
  MUTATION  --mutate-forms makes the positive control fail (exit 1).
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import pairwise_tables as PT            # noqa: E402
import gpu_search_pairwise as G         # noqa: E402
import test_pairwise_tables as TT            # noqa: E402
from test_pairwise_tables import pick_cases   # noqa: E402


def visit_all(engine, tab):
    rows, flags, comps = [], [], 0
    off, total = 0, tab["total_prefixes"]
    while off < total:
        cnt = min(G.DEBUG_MAX, total - off)
        found, _, c, (r, f, _, _) = engine.run(tab, off, cnt, debug=True, verify_hits=False)
        rows.extend(r)
        flags.extend(f)
        comps += c
        off += cnt
    return rows, flags, comps


ORDERS = ("natural", "reversed")
VERIFY_SAMPLE = 60          # declared cap: search/verify.py calls per case, not every composition


def blocks_ok(tab, rows):
    """The visited rows are exactly the per-prefix completion blocks, in prefix
    rank order, each block in increasing first completion value and mapped back
    to natural arc order."""
    cursor = 0
    for r in range(tab["total_prefixes"]):
        a, st, s = PT.unrank_prefix(tab, r)
        want = [PT.natural(tab, list(a) + [v, w]) for v, w in PT.completions(tab, st, s)]
        if rows[cursor:cursor + len(want)] != want:
            return False
        cursor += len(want)
    return cursor == len(rows)


def run_case(engine, label, n, chords, tab_nat, unrestricted):
    recs = []
    for which in TT.orders_for_format() if TT.FMT == PT.FORMAT else ORDERS:
        order = None if which == "natural" else list(range(tab_nat["b"]))[::-1]
        tab = tab_nat if order is None else PT.build(
            n, tab_nat["b"], chords, tab_nat["lows"], shape_index=tab_nat["shape_index"], order=order,
            fmt=PT.FORMAT_V2)
        ref = list(PT.iterate_compositions(tab))
        # the reference recursion is computed in NATURAL order from lows/hi/Tarr,
        # which no order touches, so it is the same set for both runs
        ref_set = {tuple(x) for x in PT.enumerate_admissible(n, tab["lows"], tab["hi"], tab["Tarr"])}
        rows, flags, comps = visit_all(engine, tab)
        forms = [tuple(f) for f in tab["forms"]]
        cpu_flags = [PT.sat(n, forms, a) for a in rows]
        rowset = {tuple(x) for x in rows}
        # search/verify.py on a bounded sample: every SAT row up to the cap (a
        # wrong flag there becomes a false claim) plus an even spread of others
        sat_idx = [i for i, f in enumerate(flags) if f][:VERIFY_SAMPLE]
        spread = list(range(0, len(rows), max(1, len(rows) // max(1, VERIFY_SAMPLE))))[:VERIFY_SAMPLE]
        sample = sorted(set(sat_idx + spread))
        verify_bad = sum(int(bool(flags[i]) != G.V.pancyclic(n, G.materialise(tab["chords"], rows[i])))
                         for i in sample)
        rec = dict(case=label, order_name=which, order=list(tab["order"]), n=n, b=tab["b"],
                   total_prefixes=tab["total_prefixes"],
                   total_compositions=tab["total_compositions"], gpu_visited=len(rows),
                   ordered_sequence_identical=rows == ref,
                   set_identical=(rowset == ref_set and len(rows) == len(ref_set)),
                   duplicates=len(rows) - len(rowset),
                   missing=len(ref_set - rowset), extra=len(rowset - ref_set),
                   prefix_blocks_ok=blocks_ok(tab, rows),
                   kernel_compositions_counter=comps, counter_matches=comps == tab["total_compositions"],
                   gpu_sat=sum(flags), cpu_sat=sum(cpu_flags), flags_identical=flags == cpu_flags,
                   verify_py_sampled=len(sample), verify_py_disagreements=verify_bad)
        print(json.dumps(rec), flush=True)
        recs.append(rec)
    if len(recs) == 1:
        return recs
    same_set = len({r["gpu_visited"] for r in recs}) == 1 and len({r["gpu_sat"] for r in recs}) == 1
    cmp_rec = dict(case=label, comparison="orders", n=n, b=tab_nat["b"],
                   orders={r["order_name"]: r["order"] for r in recs},
                   total_prefixes={r["order_name"]: r["total_prefixes"] for r in recs},
                   gpu_sat={r["order_name"]: r["gpu_sat"] for r in recs},
                   permuted_is_non_trivial=recs[1]["order"] != list(range(tab_nat["b"])),
                   orders_agree=same_set)
    print(json.dumps(cmp_rec), flush=True)
    return recs + [cmp_rec]


def family(engine):
    ok, checked = 0, 0
    for n in range(41, 68):
        ch = [(0, 2), (0, n - 7), (1, 13), (3, n - 6), (4, 31), (n - 8, n - 5)]
        b, canonical, a = G.canonical_witness(n, ch)
        tab = PT.build(n, b, canonical)
        admitted = PT.admitted(tab, a)
        # the prefix is the first b-2 arcs in ASSIGNMENT order
        r, st, s = PT.rank_prefix(tab, PT.permuted(tab, a)[:b - 2]) if admitted else (None, None, None)
        hits = engine.run(tab, r, 1)[0] if admitted else []
        good = admitted and any(h["arcs"] == a for h in hits) and G.V.pancyclic(n, ch)
        checked += 1
        ok += int(good)
        if not good:
            print(json.dumps({"family_failure": n, "admitted": admitted, "hits": len(hits)}), flush=True)
    return checked, ok


if __name__ == "__main__":
    mutate = "--mutate-forms" in sys.argv
    TT.set_format(sys.argv)
    engine = G.Engine()
    t0 = time.perf_counter()
    controls = []
    for rule in (None, "min-width"):        # an explicit rule: the default is "natural"
        control = G.controls(engine, mutate=mutate, rule=rule)
        controls.append(dict(order_rule=rule or "natural",
                             **{k: control[k] for k in ("positive_control", "soundness_control_on_witnesses",
                                                        "sample", "mismatches")}))
        print(json.dumps({"controls": controls[-1]}), flush=True)
    cases = pick_cases(str(HERE.parent / "gpu-blast" / "n68.jsonl"), want_sat=True)
    recs = [r for c in cases for r in run_case(engine, *c)]
    runs = [r for r in recs if "order_name" in r]
    comps = [r for r in recs if r.get("comparison") == "orders"]
    checked, ok = family(engine)
    fails = [r for r in runs if not (r["ordered_sequence_identical"] and r["set_identical"]
                                     and r["duplicates"] == 0 and r["missing"] == 0
                                     and r["extra"] == 0 and r["prefix_blocks_ok"]
                                     and r["counter_matches"] and r["flags_identical"]
                                     and r["gpu_sat"] == r["cpu_sat"] and r["verify_py_disagreements"] == 0)]
    bad_cmp = [r for r in comps if not (r["orders_agree"] and r["permuted_is_non_trivial"])]
    print(json.dumps({"cases": len(cases), "order_runs": len(runs), "format": TT.FMT,
                      "orders": sorted({r["order_name"] for r in runs}),
                      "compositions_visited": sum(r["gpu_visited"] for r in runs),
                      "sat_compositions": sum(r["gpu_sat"] for r in runs),
                      "verify_py_calls": sum(r["verify_py_sampled"] for r in runs),
                      "verify_py_disagreements": sum(r["verify_py_disagreements"] for r in runs),
                      "duplicates": sum(r["duplicates"] for r in runs),
                      "missing": sum(r["missing"] for r in runs), "extra": sum(r["extra"] for r in runs),
                      "control_mismatches": sum(c["mismatches"] for c in controls),
                      "family_witnesses_checked": checked, "family_witnesses_found": ok,
                      "order_comparisons_bad": len(bad_cmp),
                      "failing_cases": len(fails), "seconds": round(time.perf_counter() - t0, 1)}), flush=True)
    raise SystemExit(1 if fails or bad_cmp or ok != checked else 0)
