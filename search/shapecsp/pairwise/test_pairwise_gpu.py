"""GPU exact-set evidence for gpu_search_pairwise.  Prints counts.

  VISIT     the compositions the kernel visits for prefix ranks 0..total-1, in
            visiting order, equal pairwise_tables.iterate_compositions (which
            test_pairwise_tables.py already equates with the plain reference
            recursion): no duplicates, nothing missing, nothing extra.
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


def run_case(engine, label, n, chords, tab, unrestricted):
    ref = list(PT.iterate_compositions(tab))
    rows, flags, comps = visit_all(engine, tab)
    forms = [tuple(f) for f in tab["forms"]]
    cpu_flags = [PT.sat(n, forms, a) for a in rows]
    rec = dict(case=label, n=n, b=tab["b"], total_prefixes=tab["total_prefixes"],
               total_compositions=tab["total_compositions"], gpu_visited=len(rows),
               ordered_sequence_identical=rows == ref,
               duplicates=len(rows) - len({tuple(x) for x in rows}),
               missing=len({tuple(x) for x in ref} - {tuple(x) for x in rows}),
               extra=len({tuple(x) for x in rows} - {tuple(x) for x in ref}),
               kernel_compositions_counter=comps, counter_matches=comps == tab["total_compositions"],
               gpu_sat=sum(flags), cpu_sat=sum(cpu_flags), flags_identical=flags == cpu_flags)
    print(json.dumps(rec), flush=True)
    return rec


def family(engine):
    ok, checked = 0, 0
    for n in range(41, 68):
        ch = [(0, 2), (0, n - 7), (1, 13), (3, n - 6), (4, 31), (n - 8, n - 5)]
        b, canonical, a = G.canonical_witness(n, ch)
        tab = PT.build(n, b, canonical)
        admitted = PT.admitted(tab, a)
        r, st, s = PT.rank_prefix(tab, a[:b - 2]) if admitted else (None, None, None)
        hits = engine.run(tab, r, 1)[0] if admitted else []
        good = admitted and any(h["arcs"] == a for h in hits) and G.V.pancyclic(n, ch)
        checked += 1
        ok += int(good)
        if not good:
            print(json.dumps({"family_failure": n, "admitted": admitted, "hits": len(hits)}), flush=True)
    return checked, ok


if __name__ == "__main__":
    mutate = "--mutate-forms" in sys.argv
    engine = G.Engine()
    t0 = time.perf_counter()
    control = G.controls(engine, mutate=mutate)
    print(json.dumps({"controls": {k: control[k] for k in ("positive_control", "soundness_control_on_witnesses", "sample", "mismatches")}}), flush=True)
    cases = pick_cases(str(HERE.parent / "gpu-blast" / "n68.jsonl"), want_sat=True)
    recs = [run_case(engine, *c) for c in cases]
    checked, ok = family(engine)
    fails = [r for r in recs if not (r["ordered_sequence_identical"] and r["duplicates"] == 0 and r["missing"] == 0
                                     and r["extra"] == 0 and r["counter_matches"] and r["flags_identical"]
                                     and r["gpu_sat"] == r["cpu_sat"])]
    print(json.dumps({"cases": len(recs), "compositions_visited": sum(r["gpu_visited"] for r in recs),
                      "sat_compositions": sum(r["gpu_sat"] for r in recs),
                      "family_witnesses_checked": checked, "family_witnesses_found": ok,
                      "failing_cases": len(fails), "seconds": round(time.perf_counter() - t0, 1)}), flush=True)
    raise SystemExit(1 if fails or ok != checked else 0)
