"""Exact-set evidence for the pairwise tables, on the CPU.  Prints counts.

  SET     iterate_compositions(tab) (prefix unrank + completions), mapped back
          to natural arc order, equals the reference recursion
          enumerate_admissible as a SET: no duplicates, nothing missing,
          nothing extra.  Under the natural order it is also equal as an
          ORDERED sequence; under a permuted order it is not, and must not be.
  BLOCK   per-prefix ordered check: for every prefix rank the block of
          compositions the tables emit equals, in order, the completions
          computed straight from the definition of A (box plus every pair
          constraint in both directions) with no C, no states and no caps.
  ORDER   every case runs under three orders -- natural, choose_order's, and a
          reversed permutation that is non-trivial for every b -- and all three
          must agree on total_compositions, which does not depend on the order,
          while total_prefixes may and should differ.
  RANK    rank_prefix(unrank_prefix(r)) == r for every prefix rank.
  COUNT   len(reference) == total_compositions == prune_pairwise.pair_count_dp.
  SOUND   every composition of the UNRESTRICTED space that passes the full
          coverage test lies in A (so the pruned search is the same claim as
          the unpruned one), measured where SAT compositions actually exist.
  IO      save/load round-trips and reproduces tables_sha256.

Cases are real manifest chord sets at an n small enough that every check is
exhaustive, chosen the same way bounded/test_bounded_exactness.py chooses.
"""
from __future__ import annotations

import json
import math
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import pairwise_tables as PT      # noqa: E402
import prune_pairwise as PP       # noqa: E402

LIMIT_A = 300_000          # admissible compositions per case (exhaustive ORDER/RANK)
LIMIT_U = 400_000          # unrestricted compositions per case (exhaustive SOUND)

# Header format under test.  The legacy v1 header cannot record an arc order, so
# under --format pairwise-tables-v1 the permuted orders are refused BY NAME
# rather than silently dropped; the arrays themselves do not depend on the
# header, which is what makes that refusal safe.
FMT = PT.FORMAT_V2


def set_format(argv):
    global FMT
    if "--format" in argv:
        FMT = argv[argv.index("--format") + 1]
    if FMT not in PT.FORMATS:
        raise SystemExit(f"--format must be one of {PT.FORMATS}")
    return FMT


def orders_for_format():
    if FMT == PT.FORMAT:
        print(json.dumps({"refusal": "permuted orders not run",
                          "reason": f"{PT.FORMAT} has no order header key, so a permuted build is "
                                    f"unrepresentable in it; build() refuses rather than writing one",
                          "orders": ["natural"]}), flush=True)
        return ("natural",)
    return ORDERS


def enumerate_unrestricted(n, lows):
    b = len(lows)
    out, cur = [], [0] * b

    def rec(k, left):
        if k == b - 1:
            if left >= lows[k]:
                cur[k] = left
                out.append(list(cur))
            return
        for v in range(lows[k], left + 1):
            cur[k] = v
            rec(k + 1, left - v)

    rec(0, n)
    return out


def pick_cases(source, want_sat):
    rows = [json.loads(l) for l in open(source, encoding="utf-8")]
    cases = []
    for b in (4, 5, 6, 7, 8):
        for row in rows:
            if row["b"] != b:
                continue
            chords = [tuple(c) for c in row["chords"]]
            best = None
            for n in range(sum(row["lows"]) + 1, 69):
                unrestricted = math.comb(n - sum(row["lows"]) + b - 1, b - 1)
                if unrestricted > LIMIT_U:
                    break
                try:
                    tab = PT.build(n, b, chords, row["lows"], shape_index=row["shape_index"], fmt=FMT)
                except Exception as exc:
                    print(json.dumps({"skip": row["shape_index"], "n": n, "why": repr(exc)}))
                    continue
                if tab["total_compositions"] == 0 or tab["total_compositions"] > LIMIT_A:
                    continue
                best = (n, tab, unrestricted)
            if best:
                cases.append((f"manifest n68 shape_index={row['shape_index']} b={b}", best[0], chords, best[1], best[2]))
                break
    if want_sat:
        # a case whose feasible set is NOT empty, so SOUND has something to contain:
        # the t_2 witness shape (0,2)(1,3) at n=8, and the n=14 k=3 shape.
        for n, chords in ((8, [(0, 2), (1, 3)]), (14, [(0, 2), (0, 3), (1, 4)]), (24, [(0, 2), (1, 4), (1, 5), (3, 6)])):
            b = len({v for e in chords for v in e})
            tab = PT.build(n, b, chords, None, shape_index=None, fmt=FMT)
            cases.append((f"witness shape b={b} at n={n}", n, chords, tab, math.comb(n - sum(tab["lows"]) + b - 1, b - 1)))
    return cases


ORDERS = ("natural", "chosen", "reversed")


def build_for(n, chords, tab, which):
    """The same shape under one of the orders under test.  "reversed" is
    deliberately adversarial and is non-trivial for every b >= 2, so no case can
    score green by happening to have a natural chosen order."""
    b = tab["b"]
    if which == "natural":
        return tab
    # an explicit rule, not DEFAULT_ORDER_RULE: the default is "natural" (no
    # cheap rule beat it, see papers/REPORT-pairwise-order.md) and this case
    # exists to exercise a rule-DERIVED permutation, so it must stay permuted
    order = (PT.choose_order(n, b, chords, tab["lows"], rule="min-width") if which == "chosen"
             else list(range(b))[::-1])
    # a permuted build is v2 by construction: v1 cannot record the order
    return PT.build(n, b, chords, tab["lows"], shape_index=tab["shape_index"], order=order,
                    fmt=PT.FORMAT_V2)


def reference_block(tab, a_nat, s):
    """The completions of one prefix straight from the definition of A: the box
    on the two completion arcs plus every pair constraint in both directions,
    against each other and against the arcs already fixed.  Reads only lows, hi
    and Tarr -- never C, states or caps -- so it is independent of the DP whose
    output it is checking."""
    n, b, order = tab["n"], tab["b"], tab["order"]
    lows, hi, Tarr = tab["lows"], tab["hi"], tab["Tarr"]
    i, j = order[b - 2], order[b - 1]
    fixed = list(order[:b - 2])
    out = []
    for x in range(lows[i], hi[i] + 1):
        y = n - s - x
        if not lows[j] <= y <= hi[j]:
            continue
        if y > int(Tarr[i, j, x]) or x > int(Tarr[j, i, y]):
            continue
        if all(not (x > int(Tarr[k, i, a_nat[k]]) or a_nat[k] > int(Tarr[i, k, x])
                    or y > int(Tarr[k, j, a_nat[k]]) or a_nat[k] > int(Tarr[j, k, y]))
               for k in fixed):
            out.append((x, y))
    return out


def run_case(label, n, chords, tab, unrestricted_size):
    recs = [check_one(label, n, chords, build_for(n, chords, tab, w), unrestricted_size, w)
            for w in orders_for_format()]
    base = recs[0]
    if len(recs) == 1:
        return recs
    cmp_rec = dict(case=label, n=n, b=tab["b"], comparison="orders",
                   orders={r["order_name"]: r["order"] for r in recs},
                   total_compositions={r["order_name"]: r["total_compositions"] for r in recs},
                   total_prefixes={r["order_name"]: r["total_prefixes"] for r in recs},
                   compositions_invariant=len({r["total_compositions"] for r in recs}) == 1,
                   chosen_is_non_trivial=recs[1]["order"] != list(range(tab["b"])),
                   reversed_is_non_trivial=recs[2]["order"] != list(range(tab["b"])),
                   prefix_gain_chosen=round(base["total_prefixes"] / max(1, recs[1]["total_prefixes"]), 4),
                   compositions_per_prefix={r["order_name"]:
                                            round(r["total_compositions"] / max(1, r["total_prefixes"]), 4)
                                            for r in recs})
    print(json.dumps(cmp_rec), flush=True)
    return recs + [cmp_rec]


def check_one(label, n, chords, tab, unrestricted_size, order_name):
    b = tab["b"]
    # the reference recursion is always computed in NATURAL arc order, from
    # lows/hi/Tarr, which the order does not touch
    ref = PT.enumerate_admissible(n, tab["lows"], tab["hi"], tab["Tarr"])
    seq = list(PT.iterate_compositions(tab))
    ordered_equal = seq == ref
    dup = len(seq) - len({tuple(x) for x in seq})
    missing = len({tuple(x) for x in ref} - {tuple(x) for x in seq})
    extra = len({tuple(x) for x in seq} - {tuple(x) for x in ref})
    rank_ok = 0
    blocks_ok = blocks_checked = block_comps = 0
    cursor = 0
    for r in range(tab["total_prefixes"]):
        a, st, s = PT.unrank_prefix(tab, r)
        r2, st2, s2 = PT.rank_prefix(tab, a)
        rank_ok += int(r2 == r and st2 == st and s2 == s)
        a_nat = PT.natural(tab, list(a) + [0, 0])
        got = PT.completions(tab, st, s)
        want = reference_block(tab, a_nat, s)
        emitted = seq[cursor:cursor + len(got)]
        expected_rows = [PT.natural(tab, list(a) + [v, w]) for v, w in got]
        blocks_ok += int(got == want and emitted == expected_rows)
        blocks_checked += 1
        block_comps += len(got)
        cursor += len(got)
    round_trip_vec = all(PT.natural(tab, PT.permuted(tab, x)) == x for x in seq[:64])
    indep, _ = PP.pair_count_dp(n, tab["lows"], tab["hi"],
                                {(i, j): [int(x) for x in tab["Tarr"][i, j, tab["lows"][i]:tab["hi"][i] + 1]]
                                 for i in range(b) for j in range(b) if i != j})
    rec = dict(case=label, order_name=order_name, order=list(tab["order"]), fmt=tab["format"], n=n, b=b,
               unrestricted=unrestricted_size,
               total_prefixes=tab["total_prefixes"], total_compositions=tab["total_compositions"],
               reference_size=len(ref), sequence_size=len(seq), ordered_sequence_identical=ordered_equal,
               ordered_identity_required=(order_name == "natural"),
               set_identical=(dup == 0 and missing == 0 and extra == 0 and len(seq) == len(ref)),
               duplicates=dup, missing=missing, extra=extra,
               prefix_blocks_checked=blocks_checked, prefix_blocks_ok=blocks_ok,
               block_check_ok=(blocks_ok == blocks_checked and block_comps == len(seq)),
               block_compositions=block_comps, natural_permuted_round_trip=round_trip_vec,
               ranks_round_tripped=rank_ok, rank_round_trip_ok=rank_ok == tab["total_prefixes"],
               pair_count_dp=indep, counts_agree=(indep == tab["total_compositions"] == len(ref)),
               nstates=tab["nstates"], nstates_sum=sum(tab["nstates"]), nstates_peak=max(tab["nstates"]),
               prune=round(unrestricted_size / max(1, tab["total_compositions"]), 3))
    # SOUND is mandatory: a case too large for it is a failure, not a skip
    # (review finding 4: a missing key used to score green by default).
    rec["sound_evaluated"] = unrestricted_size <= LIMIT_U
    if rec["sound_evaluated"]:
        allc = enumerate_unrestricted(n, tab["lows"])
        sats = [a for a in allc if PT.sat(n, [tuple(f) for f in tab["forms"]], a)]
        lost = [a for a in sats if not PT.admitted(tab, a)]
        rec.update(unrestricted_enumerated=len(allc), sat_in_unrestricted=len(sats),
                   sat_lost_by_A=len(lost), sat_examples_lost=lost[:3])
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "t.npz"
        PT.save(path, tab)
        back = PT.load(path, expected_sha256=tab["tables_sha256"])
        rec["io_round_trip_hash"] = back["tables_sha256"] == tab["tables_sha256"]
        rec["io_round_trip_arrays"] = all(np.array_equal(x, y) for (_, x), (_, y)
                                          in zip(PT._array_items(tab), PT._array_items(back)))
    print(json.dumps(rec), flush=True)
    return rec


def failed(r):
    """A case fails on set identity, the per-prefix ordered check, ranks, counts,
    soundness or IO -- and additionally on ordered identity when the order is
    natural, where the sequence really is lexicographic."""
    bad = not (r["set_identical"] and r["duplicates"] == 0 and r["missing"] == 0 and r["extra"] == 0
               and r["block_check_ok"] and r["natural_permuted_round_trip"] and r["rank_round_trip_ok"]
               and r["counts_agree"] and r["sound_evaluated"] and r["sat_lost_by_A"] == 0
               and r["io_round_trip_hash"] and r["io_round_trip_arrays"])
    if r["ordered_identity_required"] and not r["ordered_sequence_identical"]:
        bad = True
    return bad


if __name__ == "__main__":
    set_format(sys.argv)
    source = str(HERE.parent / "gpu-blast" / "n68.jsonl")
    cases = pick_cases(source, want_sat=True)
    recs = [r for c in cases for r in run_case(*c)]
    checks = [r for r in recs if "order_name" in r]
    comps = [r for r in recs if r.get("comparison") == "orders"]
    fails = [r for r in checks if failed(r)]
    bad_cmp = [r for r in comps if not (r["compositions_invariant"] and r["reversed_is_non_trivial"])]
    print(json.dumps({"cases": len(cases), "order_runs": len(checks), "format": FMT,
                      "orders": sorted({r["order_name"] for r in checks}),
                      "compositions_compared_against_reference": sum(r["sequence_size"] for r in checks),
                      "prefix_blocks_checked": sum(r["prefix_blocks_checked"] for r in checks),
                      "prefix_blocks_ok": sum(r["prefix_blocks_ok"] for r in checks),
                      "prefix_ranks_round_tripped": sum(r["ranks_round_tripped"] for r in checks),
                      "unrestricted_scanned_for_lost_sat": sum(r.get("unrestricted_enumerated", 0) for r in checks),
                      "sat_found": sum(r.get("sat_in_unrestricted", 0) for r in checks),
                      "sat_lost": sum(r.get("sat_lost_by_A", 0) for r in checks),
                      "duplicates": sum(r["duplicates"] for r in checks),
                      "missing": sum(r["missing"] for r in checks),
                      "extra": sum(r["extra"] for r in checks),
                      "cases_with_non_trivial_chosen_order": sum(int(r["chosen_is_non_trivial"]) for r in comps),
                      "order_comparisons_bad": len(bad_cmp),
                      "failing_cases": len(fails)}), flush=True)
    raise SystemExit(1 if fails or bad_cmp else 0)
