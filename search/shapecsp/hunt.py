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

RESULT INTEGRITY.  Every eligible shape must produce exactly one terminal record
from a child that exited 0.  Anything else -- a non-zero exit, no record, several
records, an unparseable record -- is an ERROR, which is UNKNOWN and is counted
with GAVEUP, never silently as UNSAT.  Every SAT is re-derived independently: the
arcs are checked against the shape's lower bounds and the requested n, then
materialised into the actual C_n + k chords graph and tested for pancyclicity by
verify.check, which does not use this reformulation at all.  A SAT the checker
rejects is a defect in the solver, and it aborts the run rather than being
reported as a hit.  A single UNKNOWN voids any "no shape reaches the cutoff"
conclusion, so the summary reports it loudly rather than folding it into UNSAT,
and the exit status is non-zero for anything that is not a clean decision.

Each DECIDED shape is also written to a per-run .done file keyed by its index in
the eligible order, which makes the run resumable: on restart the decided shapes
are skipped, so changing the worker count or the binary does not throw away
completed work.  GAVEUP and ERROR are deliberately not recorded there, so a rerun
retries exactly the shapes that are still unknown.
"""
from __future__ import annotations
import os, pickle, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor

import shapes as S
import bound as B
import verify as V

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

elig = [d for d in data if d[0] >= cutoff and sum(d[4]) <= cutoff and B.hall_ok(d[5], cutoff)]
elig.sort(key=lambda d: -d[0])
print(f"hunt k={k} cutoff={cutoff} jobs={jobs} nodecap={nodecap}/shape "
      f"mode={'EXACT n=%d only' % cutoff if exact == '1' else 'range [cutoff, cap]'}", flush=True)
print(f"shapes={len(data)} eligible={len(elig)} caps {elig[0][0]}..{elig[-1][0]} "
      f"setup={round(time.time()-t0,1)}s", flush=True)

DONE = os.path.join(HERE, f"hunt-k{k}-n{cutoff}-{'exact' if exact == '1' else 'range'}.done")
seen = set()
if os.path.exists(DONE):
    for line in open(DONE):
        parts = line.split()
        if len(parts) >= 2 and parts[0].isdigit():
            seen.add(int(parts[0]))
    print(f"resume: {len(seen)} shape(s) already decided in {os.path.basename(DONE)}", flush=True)
todo = [(i, d) for i, d in enumerate(elig) if i not in seen]

lock = threading.Lock()
donef = open(DONE, "a", buffering=1)
done = [len(seen)]
gaveup, errors, hit = [], [], []
stop = threading.Event()
t1 = time.time()


def run(item):
    if stop.is_set():
        return
    i, d = item
    cap, b, ch, forms, lows, iv = d
    payload = "\n".join([" ".join(map(str, [b, len(forms)] + lows))] +
                        [f"{m} {c}" for m, c in forms]) + "\n"
    p = subprocess.run([BB, str(cutoff), nodecap, "2", exact], input=payload,
                       capture_output=True, text=True)
    recs = [l for l in p.stdout.splitlines() if l.startswith("SHAPE ")]
    ok_sat, why, claimed_sat = None, None, False
    if p.returncode != 0:
        why = f"child exited {p.returncode}"
    elif len(recs) != 1:
        why = f"{len(recs)} terminal record(s), expected exactly 1"
    else:
        claimed_sat = " SAT " in recs[0]
        if claimed_sat:
            ok_sat, why = V.check_record(recs[0], b, ch, lows, cap, cutoff,
                                         exact=(exact == "1"))
    with lock:
        done[0] += 1
        n = done[0]
        if why is not None:
            errors.append((b, ch, cap, why))
            print(f"ERROR b={b} chords={ch} cap={cap}: {why}  (UNKNOWN, not UNSAT)", flush=True)
            if claimed_sat:
                print("*** the solver claimed SAT and the independent checker refused it; "
                      "that is a solver defect, stopping the run ***", flush=True)
                stop.set()
        elif ok_sat is not None:
            got, arcs, che, expl = ok_sat
            hit.append((got, b, ch, arcs, che))
            donef.write(f"{i} SAT n={got} arcs={','.join(map(str, arcs))}\n")
            print(f"*** SAT n={got} b={b} chords={ch} arcs={','.join(map(str,arcs))} cap={cap} "
                  f"VERIFIED graph chords={che} -> {expl} ***", flush=True)
            stop.set()
        elif "GAVEUP" in recs[0]:
            gaveup.append((b, ch, cap))
            print(f"GAVEUP b={b} chords={ch} cap={cap}  (UNKNOWN, not UNSAT)", flush=True)
        elif "UNSAT" in recs[0]:
            donef.write(f"{i} UNSAT\n")
        else:
            errors.append((b, ch, cap, f"unrecognised record {recs[0]!r}"))
            print(f"ERROR b={b} chords={ch} cap={cap}: unrecognised record {recs[0]!r}", flush=True)
        if n <= 50 or n % 50 == 0:
            el = time.time() - t1
            fresh = n - len(seen)
            rate = fresh / el if el > 0 else 0.0
            proj = (len(elig) - len(seen)) / rate / 3600 if rate else float("inf")
            print(f"# {n}/{len(elig)} elapsed={round(el)}s rate={rate:.3f} shapes/s "
                  f"projected_total={proj:.1f}h "
                  f"gaveup={len(gaveup)} errors={len(errors)}", flush=True)


with ThreadPoolExecutor(max_workers=jobs) as ex:
    list(ex.map(run, todo))
donef.close()

el = round(time.time() - t1, 1)
unknown = len(gaveup) + len(errors)
if hit:
    print(f"RESULT SAT -- t_{k} >= {hit[0][0]}; {len(hit)} independently verified hit(s); "
          f"{done[0]}/{len(elig)} shapes decided; {el}s")
    sys.exit(0)
if unknown:
    print(f"RESULT INCONCLUSIVE -- {len(gaveup)} shape(s) hit the node budget, "
          f"{len(errors)} execution/validation error(s); {el}s")
    sys.exit(1)
if done[0] != len(elig):
    print(f"RESULT INCOMPLETE -- {done[0]} of {len(elig)} eligible shapes decided; {el}s")
    sys.exit(1)
if exact == "1":
    print(f"RESULT no eligible shape is feasible at exactly n={cutoff}; all {len(elig)} "
          f"decided, gaveup=0 errors=0; {el}s.  This does NOT rule out a shape reaching "
          f"some larger n.")
else:
    print(f"RESULT no eligible shape reaches n >= {cutoff}; all {len(elig)} decided, "
          f"gaveup=0 errors=0; {el}s")
