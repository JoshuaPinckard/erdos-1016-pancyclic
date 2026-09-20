"""Word-boundary (63/64) carry test for the kernel's shifted coverage masks.

The completion loop shifts the "rising" forms' mask left and the "falling"
forms' mask right by one bit per step of a_{b-2}.  A form whose length passes
from 63 to 64 (or 64 to 63) must carry between the two 64-bit words; the
existing exact-set cases all run at n <= 42, where no length ever reaches 64,
so review probe w20_probe_carry_mutation showed that dropping the carry terms
is NOT detected by any existing check.  This test:

  1. takes real manifest shapes at n = 64..70 and finds, on the CPU, prefixes
     whose completion loop contains a form length crossing 63/64 in each
     direction;
  2. runs those prefixes through the stock kernel in debug mode and demands the
     visited compositions, SAT flags AND the two 64-bit coverage words equal
     the CPU's (a verdict alone cannot see a lost bit when the composition is
     not pancyclic anyway, which at n >= 64 is nearly always);
  3. runs the same prefixes through a kernel with the carry terms removed and
     demands at least one flag DIFFERENCE, so the test is proven able to see
     the fault it is written for.

Prints counts; exit 1 on any failure.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import pairwise_tables as PT            # noqa: E402
import gpu_search_pairwise as G         # noqa: E402

RISING = "p1 = (p1 << 1) | (p0 >> 63); p0 <<= 1;"
FALLING = "m0 = (m0 >> 1) | (m1 << 63); m1 >>= 1;"
assert RISING in G.CUDA and FALLING in G.CUDA, "kernel carry lines changed; update this test"


def crossing_prefixes(tab, want=6, scan=200000):
    """Prefix ranks whose completions include a rising form passing 63->64 and a
    falling form passing 64->63, found by direct CPU evaluation."""
    n, b, forms = tab["n"], tab["b"], [tuple(f) for f in tab["forms"]]
    found = []
    for r in range(min(scan, tab["total_prefixes"])):
        a, st, s = PT.unrank_prefix(tab, r)
        comps = PT.completions(tab, st, s)
        if len(comps) < 2:
            continue
        rise = fall = False
        for mask, ch in forms:
            hasA = (mask >> (b - 2)) & 1
            hasB = (mask >> (b - 1)) & 1
            if hasA == hasB:
                continue
            base = ch + sum(a[j] for j in range(b - 2) if mask >> j & 1)
            lengths = [base + (v if hasA else n - s - v) for v, w in comps]
            lo, hi = min(lengths), max(lengths)
            if lo <= 63 < hi or lo <= 64 <= hi and lo < 64:
                if hasA:
                    rise = True
                else:
                    fall = True
        if rise and fall:
            found.append(r)
            if len(found) >= want:
                break
    return found


def run_prefixes(engine, tab, ranks):
    rows, flags, covs = [], [], []
    for r in ranks:
        _, _, _, (rr, ff, _, cc) = engine.run(tab, r, 1, debug=True, verify_hits=False)
        rows.extend(rr)
        flags.extend(ff)
        covs.extend(cc)
    return rows, flags, covs


def cpu_coverage(n, forms, a):
    """The two 64-bit coverage words the kernel should produce for composition a."""
    c0 = c1 = 0
    for mask, ch in forms:
        ln = ch + sum(a[j] for j in range(len(a)) if mask >> j & 1)
        if 3 <= ln <= n:
            if ln < 64:
                c0 |= 1 << ln
            else:
                c1 |= 1 << (ln - 64)
    return (c0, c1)


# A dihedral image of the n=67 family witness whose long arc sits at index b-2:
# the kernel reaches the SAT composition only after 27 sweep steps, and the
# required length 64 is realised solely by a form carried across the word
# boundary (found by review/w20_probe_carry_case.py: 4 carry-critical images
# among the 110 usable dihedral images of the five n>=64 witnesses).
CARRY_WITNESS = dict(n=67, chords=[[0, 3], [1, 6], [2, 10], [3, 5], [4, 8], [7, 9]],
                     arcs=[1, 1, 5, 1, 1, 1, 1, 9, 18, 28, 1])


def carry_witness_case(stock, mutant):
    """Verdict-level check: the stock kernel must report this composition SAT,
    the carry mutant must not, and search/verify.py must agree it is pancyclic."""
    n, chords, arcs = CARRY_WITNESS["n"], CARRY_WITNESS["chords"], CARRY_WITNESS["arcs"]
    b = len(arcs)
    tab = PT.build(n, b, chords)
    ok_admitted = PT.admitted(tab, arcs)
    truth = G.V.pancyclic(n, G.materialise(tab["chords"], arcs))
    r, st, s = PT.rank_prefix(tab, arcs[:b - 2])
    hits, _, _, (rows, flags, _, _) = stock.run(tab, r, 1, debug=True)
    _, _, _, (mrows, mflags, _, _) = mutant.run(tab, r, 1, debug=True, verify_hits=False)
    idx = rows.index(arcs) if arcs in rows else -1
    midx = mrows.index(arcs) if arcs in mrows else -1
    rec = dict(case="carry-critical witness (dihedral image of the n=67 family witness)", n=n, b=b,
               prefix_rank=r, admitted=ok_admitted, pancyclic_by_verify=truth,
               visited_by_stock=idx >= 0, stock_flag=bool(flags[idx]) if idx >= 0 else None,
               stock_verified_hit=any(h["arcs"] == arcs for h in hits),
               mutant_flag=bool(mflags[midx]) if midx >= 0 else None,
               sweep_steps_before_verdict=arcs[b - 2] - PT.completions(tab, st, s)[0][0])
    rec["passes"] = bool(ok_admitted and truth and rec["stock_flag"] and rec["stock_verified_hit"] and rec["mutant_flag"] is False)
    print(json.dumps(rec), flush=True)
    return rec


def main():
    src = HERE.parent / "gpu-blast"
    stock = G.Engine()
    mutated_src = G.CUDA.replace(RISING, "p1 = (p1 << 1); p0 <<= 1;").replace(FALLING, "m0 = (m0 >> 1); m1 >>= 1;")
    orig = G.CUDA
    G.CUDA = mutated_src
    try:
        mutant = G.Engine()
    finally:
        G.CUDA = orig
    total_rows = total_prefixes = 0
    stock_ok = True
    mutant_diffs = 0
    cases = []
    # chord sets come from the n68 manifest for every n: a shape is level
    # independent, only its eligibility and tables depend on n
    rows68 = [json.loads(l) for l in (src / "n68.jsonl").read_text(encoding="utf-8").splitlines()]
    for n in (64, 67, 70):
        rows = rows68
        picked = 0
        for row in rows:
            if row["b"] < 8:
                continue
            tab = PT.build(n, row["b"], row["chords"], None, shape_index=row["shape_index"])
            if tab["total_prefixes"] == 0:
                continue
            ranks = crossing_prefixes(tab)
            if not ranks:
                continue
            forms = [tuple(f) for f in tab["forms"]]
            expected_rows, expected_flags, expected_cov = [], [], []
            for r in ranks:
                a, st, s = PT.unrank_prefix(tab, r)
                for v, w in PT.completions(tab, st, s):
                    expected_rows.append(a + [v, w])
                    expected_flags.append(PT.sat(n, forms, a + [v, w]))
                    expected_cov.append(cpu_coverage(n, forms, a + [v, w]))
            s_rows, s_flags, s_cov = run_prefixes(stock, tab, ranks)
            m_rows, m_flags, m_cov = run_prefixes(mutant, tab, ranks)
            same = s_rows == expected_rows and list(map(bool, s_flags)) == expected_flags and s_cov == expected_cov
            diffs = (sum(int(bool(x) != bool(y)) for x, y in zip(m_flags, s_flags)) + int(m_rows != s_rows)
                     + sum(int(x != y) for x, y in zip(m_cov, s_cov)))
            cases.append(dict(n=n, shape_index=row["shape_index"], b=row["b"], prefixes=len(ranks), compositions=len(expected_rows),
                              stock_matches_cpu=same, coverage_words_identical=s_cov == expected_cov,
                              sat_in_window=sum(expected_flags), mutant_differences=diffs))
            print(json.dumps(cases[-1]), flush=True)
            stock_ok &= same
            mutant_diffs += diffs
            total_rows += len(expected_rows)
            total_prefixes += len(ranks)
            picked += 1
            if picked >= 3:
                break
    witness = carry_witness_case(stock, mutant)
    summary = dict(cases=len(cases), crossing_prefixes=total_prefixes, compositions_checked=total_rows,
                   stock_all_match=stock_ok, mutant_differences=mutant_diffs,
                   mutation_detected=mutant_diffs > 0,
                   carry_witness_sat_on_stock_and_not_on_mutant=witness["passes"],
                   note="coverage words compared bit-exactly against the CPU; the carry mutant must differ, "
                        "and the carry-critical witness must flip its verdict")
    print(json.dumps(summary), flush=True)
    return 0 if stock_ok and mutant_diffs > 0 and cases and witness["passes"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
