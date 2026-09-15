"""Differential check of two bb builds: `python difftest.py <binA> <binB> <k> <nlo> <nhi>`

An optimisation to the C search is only acceptable if it changes no answer, so
this runs both builds over every shape of the given k at every cutoff in
[nlo, nhi] and compares the terminal records with the node counts stripped -- the
node count is exactly what an optimisation is meant to change, and the verdict is
exactly what it must not.

Every SAT either build returns is also materialised and checked by verify.check,
so the comparison cannot be satisfied by two builds agreeing on a wrong answer.
Exits non-zero on any disagreement or any rejected witness.
"""
from __future__ import annotations
import re, subprocess, sys
import shapes as S
import bound as B
import verify as V

binA, binB, k, nlo, nhi = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])

data = []
for b, ch in S.shapes(k):
    forms = sorted(set(S.cycle_forms(b, ch)))
    iv, lows = B.intervals(b, ch, forms=forms)
    data.append((len(forms) + 2, b, ch, forms, lows, iv))
print(f"k={k} shapes={len(data)} cutoffs {nlo}..{nhi} A={binA} B={binB}", flush=True)


def records(binary, cutoff, elig):
    lines = []
    for cap, b, ch, forms, lows, iv in elig:
        lines.append(" ".join(map(str, [b, len(forms)] + lows)))
        lines += [f"{mm} {cc}" for mm, cc in forms]
    p = subprocess.run([binary, str(cutoff), "4000000000", "2"],
                       input="\n".join(lines) + "\n", capture_output=True, text=True)
    if p.returncode != 0:
        print(f"FAIL {binary} exited {p.returncode} at cutoff {cutoff}")
        sys.exit(1)
    return [l for l in p.stdout.splitlines() if l.startswith("SHAPE ")]


strip = lambda l: re.sub(r" nodes=\d+", "", l)
cmp_n = sat_n = 0
for cutoff in range(nlo, nhi + 1):
    elig = [d for d in data if d[0] >= cutoff and sum(d[4]) <= cutoff and B.hall_ok(d[5], cutoff)]
    if not elig:
        continue
    ra, rb = records(binA, cutoff, elig), records(binB, cutoff, elig)
    if len(ra) != len(elig) or len(rb) != len(elig):
        print(f"FAIL cutoff {cutoff}: {len(ra)}/{len(rb)} records for {len(elig)} eligible shapes")
        sys.exit(1)
    for i, (la, lb) in enumerate(zip(ra, rb)):
        cmp_n += 1
        if strip(la) != strip(lb):
            print(f"DISAGREE cutoff={cutoff} shape={i+1}: A={la!r} B={lb!r}")
            sys.exit(1)
        if " SAT " in la:
            cap, b, ch, forms, lows, iv = elig[i]
            for tag, line in (("A", la), ("B", lb)):
                got, why = V.check_record(line, b, ch, lows, cap, cutoff)
                if why is not None:
                    print(f"FAIL cutoff={cutoff} shape={i+1} build {tag}: {why}")
                    sys.exit(1)
            sat_n += 1
    print(f"  cutoff {cutoff}: {len(elig)} shapes agree", flush=True)

print(f"DIFFTEST OK -- {cmp_n} record comparisons agree, {sat_n} SAT witness(es) "
      f"independently checked on both builds")
