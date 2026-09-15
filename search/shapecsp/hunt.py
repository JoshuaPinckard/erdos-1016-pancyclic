"""Best-first level at a fixed cutoff, parallel, early-stop on the first SAT.

    python3 hunt.py <k> <cutoff> <jobs> [nodecap] [exact]

`exact=1` tests ONLY n=cutoff on each shape, one search instead of
(cap - cutoff + 1) of them.  A hit is then immediate proof that t_k >= cutoff; a
miss says only that this shape misses that one value, so exact mode can HUNT but
cannot prove non-existence.  `exact=0` (default) is the range mode and is the one
whose UNSAT supports a non-existence claim.

Shapes eligible at the cutoff (cap, then Hall -- both rigorous necessary
conditions) are ordered by cap DESCENDING and handed to `jobs` workers one shape
at a time.  Rationale for that order: on the six shapes whose exact maximum is
known, the maximum sits at 0.77-0.95 of the shape's cap and rises with it
(caps 59,70,74,74,78,87 give maxima 56,62,61,63,64,67), so a high cap is the best
available predictor that a shape can reach the cutoff.

Note the strong asymmetry in cost, which is what `nodecap` is for.  bb walks a
shape from its cap down and STOPS at the first feasible n, so a shape that CAN
reach the cutoff is answered quickly, while one that cannot must have its whole
range [cutoff, cap] refuted -- and that is where the hours go.  A modest node
budget therefore keeps almost all the hunting power (hits stay cheap) while
capping the cost of the refutations, at the price of turning some of them into
GAVEUP/UNKNOWN.  Use a large budget only when the goal is the non-existence
proof rather than the hunt.

The first SAT stops the run and prints the arc lengths; anything else is a
per-shape UNSAT or -- if the node budget is hit -- a GAVEUP, which is UNKNOWN and
is counted separately.  A single GAVEUP voids any "no shape reaches the cutoff"
conclusion, so the summary reports it loudly rather than folding it into UNSAT.
"""
from __future__ import annotations
import os, pickle, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor

import shapes as S
import bound as B

k, cutoff, jobs = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
nodecap = sys.argv[4] if len(sys.argv) > 4 else "8000000000"
exact = sys.argv[5] if len(sys.argv) > 5 else "0"
HERE = os.path.dirname(os.path.abspath(__file__))
BB = os.path.join(HERE, "bb")
if not os.path.exists(BB):
    BB = os.path.join(HERE, "bb.exe")

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

elig = [d for d in data if d[0] >= cutoff and sum(d[4]) <= cutoff and B.hall_ok(d[5], cutoff)]
elig.sort(key=lambda d: -d[0])
print(f"hunt k={k} cutoff={cutoff} jobs={jobs} nodecap={nodecap}/shape "
      f"mode={'EXACT n=%d only' % cutoff if exact == '1' else 'range [cutoff, cap]'}", flush=True)
print(f"shapes={len(data)} eligible={len(elig)} caps {elig[0][0]}..{elig[-1][0]} "
      f"setup={round(time.time()-t0,1)}s", flush=True)

lock = threading.Lock()
done = [0]
gaveup = []
hit = []
stop = threading.Event()
t1 = time.time()


def run(d):
    if stop.is_set():
        return
    cap, b, ch, forms, lows, iv = d
    payload = "\n".join([" ".join(map(str, [b, len(forms)] + lows))] +
                        [f"{m} {c}" for m, c in forms]) + "\n"
    out = subprocess.run([BB, str(cutoff), nodecap, "2", exact], input=payload,
                         capture_output=True, text=True).stdout.strip()
    with lock:
        done[0] += 1
        n = done[0]
        if " SAT " in out:
            got = out.split()[3].split("=")[1]
            arcs = out.split()[4].split("=")[1]
            hit.append((got, b, ch, arcs))
            print(f"*** SAT n={got} b={b} chords={ch} arcs={arcs} cap={cap} ***", flush=True)
            stop.set()
        elif "GAVEUP" in out:
            gaveup.append((b, ch, cap))
            print(f"GAVEUP b={b} chords={ch} cap={cap}  (UNKNOWN, not UNSAT)", flush=True)
        if n <= 50 or n % 50 == 0:
            el = time.time() - t1
            rate = n / el
            print(f"# {n}/{len(elig)} elapsed={round(el)}s rate={rate:.3f} shapes/s "
                  f"projected_total={round(len(elig)/rate/3600,1)}h "
                  f"gaveup={len(gaveup)}", flush=True)


with ThreadPoolExecutor(max_workers=jobs) as ex:
    list(ex.map(run, elig))

el = round(time.time() - t1, 1)
if hit:
    print(f"RESULT SAT -- t_{k} >= {hit[0][0]}; {len(hit)} hit(s); {done[0]}/{len(elig)} shapes run; {el}s")
elif gaveup:
    print(f"RESULT INCONCLUSIVE -- {len(gaveup)} shape(s) hit the node budget; {el}s")
elif exact == "1":
    print(f"RESULT no eligible shape is feasible at exactly n={cutoff}; all {len(elig)} "
          f"decided, gaveup=0; {el}s.  This does NOT rule out a shape reaching some larger n.")
else:
    print(f"RESULT no eligible shape reaches n >= {cutoff}; all {len(elig)} decided, gaveup=0; {el}s")
