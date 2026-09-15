"""Exact maximum n for a single named shape: `python oneshape.py b "chords" nhi nlo [nodecap]`

Runs one shape only, descending, stopping at the first SAT -- that n is the
shape's exact maximum.  Pins itself and its child to one core at BelowNormal so
it stays inside the machine-wide CPU cap.
"""
from __future__ import annotations
import ast, os, subprocess, sys, time
import shapes as S
import bound as B

try:
    import psutil
    _p = psutil.Process()
    _p.cpu_affinity([0])
    _p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    print("pinned to core 0 at BelowNormal", flush=True)
except Exception as e:                      # never let the cap plumbing kill the run
    print(f"WARNING could not pin: {e!r}", flush=True)

HERE = os.path.dirname(os.path.abspath(__file__))
BB = os.path.join(HERE, "bb.exe")

b = int(sys.argv[1])
ch = ast.literal_eval(sys.argv[2])
nhi, nlo = int(sys.argv[3]), int(sys.argv[4])
nodecap = sys.argv[5] if len(sys.argv) > 5 else "4000000000"

forms = sorted(set(S.cycle_forms(b, ch)))
iv, lows = B.intervals(b, ch, forms=forms)
cap = len(forms) + 2
print(f"shape b={b} chords={ch} forms={len(forms)} cap={cap}", flush=True)
payload = "\n".join([" ".join(map(str, [b, len(forms)] + lows))] +
                    [f"{m} {c}" for m, c in forms]) + "\n"

for n in range(min(nhi, cap), nlo - 1, -1):
    if sum(lows) > n or not B.hall_ok(iv, n):
        print(f"n={n}: refuted by bound, no search", flush=True)
        continue
    t = time.time()
    proc = subprocess.Popen([BB, str(n), nodecap, "2"], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, text=True)
    try:
        psutil.Process(proc.pid).cpu_affinity([0])
        psutil.Process(proc.pid).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass
    out = proc.communicate(payload)[0].strip()
    print(f"n={n}: {out}  [{round(time.time()-t,1)}s]", flush=True)
    if " SAT " in out:
        print(f"RESULT shape maximum = {n}", flush=True)
        break
    if "GAVEUP" in out:
        print(f"RESULT UNKNOWN at n={n} -- node budget hit, this is NOT an UNSAT", flush=True)
        break
else:
    print(f"RESULT no n in [{nlo},{min(nhi,cap)}] is feasible for this shape", flush=True)
