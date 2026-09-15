"""One level of the sweep: `python level.py k n [nodecap]`

`n` is a LOWER CUTOFF handed to bb.exe, which per shape searches down from that
shape's own cap and stops at the first feasible value.  So `sat=0` for a level
means no eligible shape admits ANY value >= n, not merely that none admits
exactly n -- a stronger statement, and the one the sweep's conclusions rest on.
A SAT line reports the n actually found, which can exceed the cutoff.

Eligibility is by two rigorous necessary conditions at the cutoff (cap, then
Hall), so a shape feasible at some n0 is always eligible at the level whose
cutoff is n0.  gaveup counts shapes abandoned on the node budget: they are
UNKNOWN and a level with gaveup > 0 supports no non-existence claim.
"""
from __future__ import annotations
import os, pickle, subprocess, sys, time
import shapes as S
import bound as B

ARCORDER = "2"
HERE = os.path.dirname(os.path.abspath(__file__))
BB = os.path.join(HERE, "bb.exe")

k, n = int(sys.argv[1]), int(sys.argv[2])
nodecap = sys.argv[3] if len(sys.argv) > 3 else "4000000000"

cache = os.path.join(HERE, f"forms-k{k}.pkl")
t0 = time.time()
if os.path.exists(cache):
    data = pickle.load(open(cache, "rb"))
else:
    data = []
    for b, ch in S.shapes(k):
        forms = sorted(set(S.cycle_forms(b, ch)))
        iv, lows = B.intervals(b, ch, forms=forms)
        data.append((len(forms) + 2, b, ch, forms, lows, iv))
    pickle.dump(data, open(cache, "wb"))

elig = [d for d in data if d[0] >= n and sum(d[4]) <= n and B.hall_ok(d[5], n)]
lines = []
for cap, b, ch, forms, lows, iv in elig:
    lines.append(" ".join(map(str, [b, len(forms)] + lows)))
    lines += [f"{mm} {cc}" for mm, cc in forms]
t1 = time.time()
out = ([] if not elig else
       subprocess.run([BB, str(n), nodecap, ARCORDER], input="\n".join(lines) + "\n",
                      capture_output=True, text=True).stdout.splitlines())
sat = [l for l in out if " SAT " in l]
gu = [l for l in out if "GAVEUP" in l]
for l in sat + gu:
    i = int(l.split()[1]) - 1
    if " SAT " in l:
        # bb.exe reports the largest feasible n >= the cutoff, which may exceed it
        got, arcs = l.split()[3].split("=")[1], l.split()[4].split("=")[1]
        print(f"   SAT n={got} (cutoff {n}) b={elig[i][1]} chords={elig[i][2]} arcs={arcs}",
              flush=True)
    else:
        print(f"   GAVEUP cutoff={n} b={elig[i][1]} chords={elig[i][2]}", flush=True)
print(f"LEVEL k={k} n={n} shapes={len(data)} eligible={len(elig)} sat={len(sat)} "
      f"gaveup={len(gu)} search_seconds={round(time.time()-t1,1)} "
      f"total_seconds={round(time.time()-t0,1)}", flush=True)
