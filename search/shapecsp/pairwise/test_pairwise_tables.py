"""Exact-set evidence for the pairwise tables, on the CPU.  Prints counts.

  ORDER   iterate_compositions(tab) (prefix unrank + completions) equals the
          reference recursion enumerate_admissible as an ORDERED sequence:
          no duplicates, nothing missing, nothing extra.
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
                    tab = PT.build(n, b, chords, row["lows"], shape_index=row["shape_index"])
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
            tab = PT.build(n, b, chords, None, shape_index=None)
            cases.append((f"witness shape b={b} at n={n}", n, chords, tab, math.comb(n - sum(tab["lows"]) + b - 1, b - 1)))
    return cases


def run_case(label, n, chords, tab, unrestricted_size):
    b = tab["b"]
    ref = PT.enumerate_admissible(n, tab["lows"], tab["hi"], tab["Tarr"])
    seq = list(PT.iterate_compositions(tab))
    ordered_equal = seq == ref
    dup = len(seq) - len({tuple(x) for x in seq})
    missing = len({tuple(x) for x in ref} - {tuple(x) for x in seq})
    extra = len({tuple(x) for x in seq} - {tuple(x) for x in ref})
    rank_ok = 0
    for r in range(tab["total_prefixes"]):
        a, st, s = PT.unrank_prefix(tab, r)
        r2, st2, s2 = PT.rank_prefix(tab, a)
        rank_ok += int(r2 == r and st2 == st and s2 == s)
    indep, _ = PP.pair_count_dp(n, tab["lows"], tab["hi"],
                                {(i, j): [int(x) for x in tab["Tarr"][i, j, tab["lows"][i]:tab["hi"][i] + 1]]
                                 for i in range(b) for j in range(b) if i != j})
    rec = dict(case=label, n=n, b=b, unrestricted=unrestricted_size,
               total_prefixes=tab["total_prefixes"], total_compositions=tab["total_compositions"],
               reference_size=len(ref), sequence_size=len(seq), ordered_sequence_identical=ordered_equal,
               duplicates=dup, missing=missing, extra=extra,
               ranks_round_tripped=rank_ok, rank_round_trip_ok=rank_ok == tab["total_prefixes"],
               pair_count_dp=indep, counts_agree=(indep == tab["total_compositions"] == len(ref)),
               nstates=tab["nstates"], prune=round(unrestricted_size / max(1, tab["total_compositions"]), 3))
    if unrestricted_size <= LIMIT_U:
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


if __name__ == "__main__":
    source = str(HERE.parent / "gpu-blast" / "n68.jsonl")
    cases = pick_cases(source, want_sat=True)
    recs = [run_case(*c) for c in cases]
    fails = [r for r in recs if not (r["ordered_sequence_identical"] and r["duplicates"] == 0
                                     and r["missing"] == 0 and r["extra"] == 0 and r["rank_round_trip_ok"]
                                     and r["counts_agree"] and r.get("sat_lost_by_A", 0) == 0
                                     and r["io_round_trip_hash"] and r["io_round_trip_arrays"])]
    print(json.dumps({"cases": len(recs),
                      "compositions_compared_against_reference": sum(r["sequence_size"] for r in recs),
                      "prefix_ranks_round_tripped": sum(r["ranks_round_tripped"] for r in recs),
                      "unrestricted_scanned_for_lost_sat": sum(r.get("unrestricted_enumerated", 0) for r in recs),
                      "sat_found": sum(r.get("sat_in_unrestricted", 0) for r in recs),
                      "sat_lost": sum(r.get("sat_lost_by_A", 0) for r in recs),
                      "failing_cases": len(fails)}), flush=True)
    raise SystemExit(1 if fails else 0)
