"""Predict the descent's cost curve before paying for it.

    python3 costcurve.py <k> <nhi> <nlo>

Eligibility is a cap test, a lower-bound-sum test and a Hall test, all cheap, so
the whole curve can be computed in seconds even though the levels themselves take
hours.  That is worth doing before committing the machine: the decision to stop
the descent is a decision about the levels not yet run.

Two columns, because the shape COUNT alone understates the wall.  A level hands
each eligible shape the range [n, cap], and the solver has to refute every rung
of it, so the work is closer to the sum of (cap - n + 1) over eligible shapes than
to the count.  `rungs` is that sum.  Neither is time: cost per rung grows as the
arcs get longer and the DFS deepens, so both columns are LOWER bounds on how the
real curve bends.  They say where the knee is, not what it costs.
"""
from __future__ import annotations
import os, pickle, sys, time
import shapes as S
import bound as B

k, nhi, nlo = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
HERE = os.path.dirname(os.path.abspath(__file__))
cache = os.path.join(HERE, f"forms-k{k}.pkl")
t0 = time.time()
if os.path.exists(cache):
    with open(cache, "rb") as fh:
        data = pickle.load(fh)
else:
    data = []
    for b, ch in S.shapes(k):
        forms = sorted(set(S.cycle_forms(b, ch)))
        iv, lows = B.intervals(b, ch, forms=forms)
        data.append((len(forms) + 2, b, ch, forms, lows, iv))
    with open(cache, "wb") as fh:
        pickle.dump(data, fh)

print(f"k={k} shapes={len(data)} max_cap={max(d[0] for d in data)} "
      f"loaded in {round(time.time()-t0,1)}s")
print(f"{'n':>5} {'eligible':>9} {'rungs':>9} {'x prev':>7}")
prev = None
for n in range(nhi, nlo - 1, -1):
    elig = [d for d in data if d[0] >= n and sum(d[4]) <= n and B.hall_ok(d[5], n)]
    rungs = sum(d[0] - n + 1 for d in elig)
    ratio = "" if prev in (None, 0) else f"{rungs / prev:6.2f}x"
    print(f"{n:>5} {len(elig):>9} {rungs:>9} {ratio:>7}", flush=True)
    prev = rungs
