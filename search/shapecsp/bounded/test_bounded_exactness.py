"""Exact-set evidence for the bounded unrank.  Prints counts, never booleans.

Three separate claims, each checked against something that shares no code with
the thing it checks:

  SET      the ranks 0..bounded_total-1 unranked ON THE GPU are exactly the
           compositions a with lows[i] <= a[i] <= hi[i] and sum a == n, as an
           ordered sequence -- so duplicates, gaps and ordering are all covered.
           The reference side is a plain recursive enumeration that knows
           nothing about ranks, DP tables or prefix sums.

  SOUND    every composition the UNRESTRICTED space contains that satisfies the
           coverage test (i.e. every solution the old kernel could have found)
           lies inside the box.  This is the claim the whole prune rests on: if
           one SAT composition fell outside, the pruned search would be a
           weaker claim than the unpruned one, not an equal one.

  COUNT    the DP rank-space size equals prune_probe's independent
           inclusion-exclusion count.

Sizes are chosen so SET and SOUND are exhaustive, not sampled.  Every bound
applied is printed.
"""
from __future__ import annotations

import itertools
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.dirname(__file__))

import bounded_caps as BC          # noqa: E402
import gpu_search_bounded as GB    # noqa: E402

CHUNK = 1 << 21


def enumerate_box(n, lows, hi):
    """Independent reference: all a with lows<=a<=hi and sum a == n.

    Plain recursion over arcs in index order.  No ranks, no DP, no prefix sums.
    Yields in lexicographic order on a, which matches lexicographic on y.
    """
    b = len(lows)
    out = []
    cur = [0] * b

    def rec(k, left):
        if k == b - 1:
            if lows[k] <= left <= hi[k]:
                cur[k] = left
                out.append(tuple(cur))
            return
        for v in range(lows[k], hi[k] + 1):
            if left - v < 0:
                break
            cur[k] = v
            rec(k + 1, left - v)

    rec(0, n)
    return out


def enumerate_unrestricted(n, lows):
    """All a with a[i] >= lows[i] and sum a == n."""
    b = len(lows)
    out = []
    cur = [0] * b

    def rec(k, left):
        if k == b - 1:
            if left >= lows[k]:
                cur[k] = left
                out.append(tuple(cur))
            return
        for v in range(lows[k], left + 1):
            cur[k] = v
            rec(k + 1, left - v)

    rec(0, n)
    return out


def sat(n, forms, a):
    """The kernel's satisfaction rule, written out independently on the CPU."""
    seen = set()
    for mask, ch in forms:
        ln = ch
        for j in range(len(a)):
            if mask >> j & 1:
                ln += a[j]
        if 3 <= ln <= n:
            seen.add(ln)
    return all(x in seen for x in range(3, n + 1))


def gpu_enumerate(engine, n, box):
    """Every arc vector the GPU produces for ranks 0..total-1, in rank order.

    Also returns the GPU's own SAT count over the whole bounded space, which the
    caller compares against a CPU count of the same thing.
    """
    got = []
    nsat = 0
    total = box["total"]
    off = 0
    while off < total:
        cnt = min(CHUNK, total - off)
        found, _, (arcs, _) = engine.run(n, [box], [off], [1], cnt, True, verify_hits=False)
        nsat += found
        got.extend(tuple(int(x) for x in row[:box["b"]]) for row in arcs[:cnt])
        off += cnt
    return got, nsat


def run_case(engine, label, n, chords, do_sound):
    box = GB.record(len({v for e in chords for v in e}), chords, n)
    b = box["b"]
    ref = enumerate_box(n, box["lows"], box["hi"])
    ie = BC.bounded_total_inclusion_exclusion(n, box["lows"], box["hi"])
    got, gpu_sat = gpu_enumerate(engine, n, box)
    cpu_sat_in_box = sum(1 for a in ref if sat(n, box["forms"], a))
    dup = len(got) - len(set(got))
    missing = sorted(set(ref) - set(got))
    extra = sorted(set(got) - set(ref))
    ordered_equal = got == ref
    bad_sum = sum(1 for a in got if sum(a) != n)
    outside = sum(1 for a in got
                  if any(not box["lows"][i] <= a[i] <= box["hi"][i] for i in range(b)))
    rec = dict(case=label, n=n, b=b,
               unrestricted_total=box["unrestricted_total"],
               bounded_total_dp=box["total"],
               bounded_total_inclusion_exclusion=ie,
               dp_vs_ie_equal=box["total"] == ie,
               reference_enumeration_size=len(ref),
               gpu_enumeration_size=len(got),
               duplicates=dup, missing_from_gpu=len(missing), extra_in_gpu=len(extra),
               ordered_sequence_identical=ordered_equal,
               wrong_sum=bad_sum, outside_box=outside,
               gpu_sat_count=gpu_sat, cpu_sat_count_in_box=cpu_sat_in_box,
               gpu_cpu_sat_agree=gpu_sat == cpu_sat_in_box,
               prune_factor=round(box["unrestricted_total"] / box["total"], 4),
               lows=list(box["lows"]), hi=list(box["hi"]),
               arcs_whose_cap_binds=sum(1 for i in range(b)
                                        if box["hi"][i] < n - sum(box["lows"]) + box["lows"][i]))
    if do_sound:
        allc = enumerate_unrestricted(n, box["lows"])
        sats = [a for a in allc if sat(n, box["forms"], a)]
        lost = [a for a in sats
                if any(not box["lows"][i] <= a[i] <= box["hi"][i] for i in range(b))]
        rec.update(unrestricted_enumerated=len(allc),
                   sat_compositions_in_unrestricted_space=len(sats),
                   sat_compositions_lost_by_the_box=len(lost),
                   sat_examples_lost=lost[:3])
    print(json.dumps(rec), flush=True)
    return rec


def pick_cases(limit_set, limit_sound):
    """Real manifest chord sets, each at the largest n whose spaces fit the caps."""
    src = os.path.join(os.path.dirname(__file__), "..", "gpu-blast", "n68.jsonl")
    rows = [json.loads(l) for l in open(src, encoding="utf-8")]
    picked = []
    for b in (6, 7, 8, 9, 10, 11, 12):
        for row in rows:
            if row["b"] != b:
                continue
            chords = [tuple(c) for c in row["chords"]]
            best = None
            for n in range(sum(row["lows"]), 69):
                try:
                    box = BC.shape_box(n, b, chords)
                except Exception:
                    continue
                if box["total"] == 0:
                    continue
                if box["unrestricted_total"] <= limit_sound and box["total"] <= limit_set:
                    best = (n, box)
            if best:
                n, box = best
                picked.append((f"manifest n68 shape_index={row['shape_index']} b={b} run at n={n}",
                               n, chords, box["unrestricted_total"] <= limit_sound))
                break
    return picked


if __name__ == "__main__":
    engine = GB.Engine(12, 70, 127)
    print(json.dumps({"caps_declared": {
        "set_check": "exhaustive over the whole bounded space of each case",
        "sound_check": "exhaustive over the whole unrestricted space of each case",
        "case_size_limit_bounded": 400000,
        "case_size_limit_unrestricted": 400000,
        "case_selection": "first manifest shape at each b in 6..12, run at the largest "
                          "n whose spaces fit those limits"}}), flush=True)
    cases = pick_cases(400000, 400000)
    recs = [run_case(engine, *c) for c in cases]
    fails = [r for r in recs if not (r["dp_vs_ie_equal"] and r["ordered_sequence_identical"]
                                     and r["duplicates"] == 0 and r["missing_from_gpu"] == 0
                                     and r["extra_in_gpu"] == 0 and r["wrong_sum"] == 0
                                     and r["outside_box"] == 0 and r["gpu_cpu_sat_agree"]
                                     and r.get("sat_compositions_lost_by_the_box", 0) == 0)]
    print(json.dumps({"cases": len(recs),
                      "ranks_compared_against_reference": sum(r["gpu_enumeration_size"] for r in recs),
                      "unrestricted_compositions_scanned_for_lost_sat":
                          sum(r.get("unrestricted_enumerated", 0) for r in recs),
                      "sat_compositions_found": sum(r.get("sat_compositions_in_unrestricted_space", 0) for r in recs),
                      "sat_compositions_lost": sum(r.get("sat_compositions_lost_by_the_box", 0) for r in recs),
                      "failing_cases": len(fails)}), flush=True)
    raise SystemExit(1 if fails else 0)
