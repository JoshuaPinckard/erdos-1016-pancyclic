"""Run sweep levels in parallel, highest n first: `python runlevels.py k nlo nhi jobs [nodecap]`

Levels are independent decisions ("does any shape ELIGIBLE AT THIS CUTOFF reach
any n >= it?"), so they parallelise freely.  Output goes to level-k<k>-n<n>.txt,
one file per level, so a level that is still running is never mistaken for a
level that answered.  A non-existence claim needs the whole contiguous block of
levels up to the largest cap, not one level -- see level.py.

The child's exit status is reported with its summary line: level.py exits
non-zero for a spoiled or inconclusive level, and that must not be lost here.
"""
from __future__ import annotations
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

k, nlo, nhi, jobs = map(int, sys.argv[1:5])
nodecap = sys.argv[5] if len(sys.argv) > 5 else "4000000000"
HERE = os.path.dirname(os.path.abspath(__file__))


def run(n):
    out = os.path.join(HERE, f"level-k{k}-n{n}.txt")
    with open(out, "w") as fh:
        rc = subprocess.run([sys.executable, "-u", os.path.join(HERE, "level.py"),
                             str(k), str(n), nodecap], stdout=fh, stderr=subprocess.STDOUT,
                            cwd=HERE).returncode
    line = [l for l in open(out) if l.startswith("LEVEL")]
    summary = line[-1].strip() if line else f"LEVEL k={k} n={n} NO-OUTPUT"
    print(summary if rc == 0 else f"{summary}  [child exit {rc} -- NOT a clean level]",
          flush=True)
    return rc


with ThreadPoolExecutor(max_workers=jobs) as ex:
    codes = list(ex.map(run, range(nhi, nlo - 1, -1)))
bad = [c for c in codes if c != 0]
print(f"RUNLEVELS k={k} {nlo}..{nhi}: {len(codes)-len(bad)} clean, {len(bad)} not clean",
      flush=True)
sys.exit(1 if bad else 0)
