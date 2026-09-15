"""False-negative control: the solver MUST return SAT on the shape of every known
witness, at that witness's own n.  `python satcheck.py [nodecap]`

bb.exe treats its n argument as a lower cutoff and returns the largest feasible
value >= it, so the pass condition is "SAT at some n >= the witness's n", and the
value it returns is printed rather than assumed.  If any line comes back UNSAT,
the solver has a false negative and every sat=0 level it has produced is void.  Runs the cases one at a time in a single process
pinned to one core at BelowNormal.  A GAVEUP is inconclusive, not a pass.
"""
from __future__ import annotations
import os, subprocess, sys, time
import shapes as S
import bound as B
import verify as V

try:
    import psutil
    psutil.Process().cpu_affinity([0])
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
except Exception as e:
    print(f"WARNING could not pin: {e!r}", flush=True)

HERE = os.path.dirname(os.path.abspath(__file__))
BB = os.path.join(HERE, "bb.exe")
nodecap = sys.argv[1] if len(sys.argv) > 1 else "8000000000"

CASES = [   # (n, b, canonical chords) -- shape of a witness verified in this lane
    (56,  7, ((0,1),(0,3),(0,6),(2,4),(4,5),(5,6))),
    (60,  8, ((0,1),(0,6),(1,2),(2,4),(3,5),(4,7))),
    (61,  9, ((0,1),(0,7),(1,3),(2,6),(3,5),(4,8))),
    (63,  9, ((0,1),(0,7),(1,3),(2,5),(4,6),(4,8))),
    (64, 10, ((0,1),(0,8),(1,3),(2,6),(4,9),(5,7))),
    (66, 11, ((0,2),(0,8),(1,5),(3,9),(4,6),(7,10))),
    (67, 11, ((0,2),(0,8),(1,5),(3,9),(4,6),(7,10))),
]

fails = []
for n, b, ch in CASES:
    forms = sorted(set(S.cycle_forms(b, ch)))
    iv, lows = B.intervals(b, ch, forms=forms)
    cap = len(forms) + 2
    if cap < n:
        print(f"n={n} b={b}: FALSE NEGATIVE -- cap {cap} < n", flush=True)
        fails.append(n); continue
    if not B.hall_ok(iv, n):
        print(f"n={n} b={b}: FALSE NEGATIVE -- refuted by the Hall bound", flush=True)
        fails.append(n); continue
    payload = "\n".join([" ".join(map(str, [b, len(forms)] + lows))] +
                        [f"{m} {c}" for m, c in forms]) + "\n"
    t = time.time()
    p = subprocess.Popen([BB, str(n), nodecap, "2"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, text=True)
    try:
        psutil.Process(p.pid).cpu_affinity([0])
        psutil.Process(p.pid).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass
    out = p.communicate(payload)[0].strip()
    dt = round(time.time() - t, 1)
    if " SAT " in out:
        # bb.exe returns the LARGEST feasible n >= the cutoff, so got >= n is the pass
        got = int(out.split()[3].split("=")[1])
        arcs = [int(x) for x in out.split()[4].split("=")[1].split(",")]
        ok, nn, chE, why = V.check(b, ch, arcs)
        good = ok and nn == got and got >= n
        print(f"n={n} b={b} cap={cap}: {'PASS' if good else 'BAD'} SAT at n={got} "
              f"arcs={arcs} sum={sum(arcs)} -> {why}  [{dt}s]", flush=True)
        if not good:
            fails.append(n)
    elif "GAVEUP" in out:
        print(f"n={n} b={b} cap={cap}: INCONCLUSIVE -- node budget hit  [{dt}s]", flush=True)
        fails.append(n)
    else:
        print(f"n={n} b={b} cap={cap}: *** FALSE NEGATIVE -- UNSAT *** [{dt}s]", flush=True)
        fails.append(n)

print()
print("SATCHECK: all witness shapes returned SAT" if not fails
      else f"SATCHECK FAILED at n={fails}")
