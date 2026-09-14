"""Run sweep levels in parallel, highest n first: `python runlevels.py k nlo nhi jobs [nodecap]`

Levels are independent decisions ("does any shape reach exactly this n?"), so
they parallelise freely.  Output goes to level-k<k>-n<n>.txt, one file per level,
so a level that is still running is never mistaken for a level that answered.
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
        subprocess.run([sys.executable, "-u", os.path.join(HERE, "level.py"),
                        str(k), str(n), nodecap], stdout=fh, stderr=subprocess.STDOUT,
                       cwd=HERE)
    line = [l for l in open(out) if l.startswith("LEVEL")]
    print(line[-1].strip() if line else f"LEVEL k={k} n={n} NO-OUTPUT", flush=True)


with ThreadPoolExecutor(max_workers=jobs) as ex:
    list(ex.map(run, range(nhi, nlo - 1, -1)))
