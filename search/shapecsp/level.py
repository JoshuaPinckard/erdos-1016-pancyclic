"""One level of the sweep: `python level.py k n [nodecap]`

`n` is a LOWER CUTOFF handed to bb, which per shape searches down from that
shape's own cap and stops at the first feasible value.  So for the shapes this
level actually searched, `sat=0` means none of them admits ANY value >= n, not
merely that none admits exactly n.  A SAT line reports the n actually found,
which can exceed the cutoff.

WHAT ONE LEVEL DOES NOT SAY.  Eligibility is decided AT THE CUTOFF by two
rigorous necessary conditions (cap, then Hall), and Hall at the cutoff is not
monotone in n: a shape can fail Hall at cutoff n and still be feasible at some
larger n0, in which case this level never searched it.  A single `sat=0` level
therefore does NOT establish "no shape reaches any value >= n".  What does
establish it is the CONTIGUOUS BLOCK of levels n, n+1, ..., N_max all returning
sat=0 with gaveup=0, where N_max is the largest cap over all shapes: a shape
feasible at n0 in that range is eligible at the level whose cutoff is n0 --
because Hall is a necessary condition evaluated at that same n0 -- and would
have been searched there.  Cite the block, never a single level.

gaveup counts shapes abandoned on the node budget.  They are UNKNOWN and a level
with gaveup > 0 supports no non-existence claim.

RESULT INTEGRITY.  A level is a certificate only if the run actually happened,
so the driver requires: the solver exits 0; every eligible shape has exactly one
terminal record, none missing, duplicated, out of range or malformed; and every
SAT is re-derived independently by verify.check_record, which materialises the
graph and tests pancyclicity without the reformulation.  Any violation prints
`LEVEL ... FAILED` and exits non-zero -- it is never folded into sat=0, which is
the shape a spoiled run would otherwise take.
"""
from __future__ import annotations
import os, pickle, subprocess, sys, time
import shapes as S
import bound as B
import verify as V

ARCORDER = "2"
HERE = os.path.dirname(os.path.abspath(__file__))
BB = os.path.join(HERE, "bb")           # Linux build
if not os.path.exists(BB):
    BB = os.path.join(HERE, "bb.exe")   # Windows build

k, n = int(sys.argv[1]), int(sys.argv[2])
nodecap = sys.argv[3] if len(sys.argv) > 3 else "4000000000"


def fail(msg):
    print(f"LEVEL k={k} n={n} FAILED -- {msg}", flush=True)
    sys.exit(1)


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

sat, gu = [], []
if elig:
    p = subprocess.run([BB, str(n), nodecap, ARCORDER], input="\n".join(lines) + "\n",
                       capture_output=True, text=True)
    if p.returncode != 0:
        fail(f"solver exited {p.returncode} after {round(time.time()-t1,1)}s; "
             f"stderr={p.stderr.strip()[:300]!r}")
    # Exactly one terminal record per eligible shape, indexed 1..len(elig).
    recs = {}
    for line in p.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 3 or parts[0] != "SHAPE" or not parts[1].isdigit():
            fail(f"unrecognised solver output line {line!r}")
        i = int(parts[1])
        if not 1 <= i <= len(elig):
            fail(f"solver reported shape {i}, outside 1..{len(elig)}")
        if i in recs:
            fail(f"solver reported shape {i} twice: {recs[i]!r} and {line!r}")
        if parts[2] not in ("SAT", "UNSAT", "GAVEUP"):
            fail(f"unrecognised verdict in {line!r}")
        recs[i] = line
    missing = [i for i in range(1, len(elig) + 1) if i not in recs]
    if missing:
        fail(f"{len(missing)} of {len(elig)} eligible shapes produced no terminal record "
             f"(first: shape {missing[0]}); an incomplete run is UNKNOWN, not sat=0")
    for i in range(1, len(elig) + 1):
        line, (cap, b, ch, forms, lows, iv) = recs[i], elig[i - 1]
        if line.split()[2] == "SAT":
            got, why = V.check_record(line, b, ch, lows, cap, n)
            if why is not None:
                fail(f"shape {i} b={b} chords={ch}: {why}")
            nv, arcs, che, expl = got
            sat.append(line)
            print(f"   SAT n={nv} (cutoff {n}) b={b} chords={ch} "
                  f"arcs={','.join(map(str, arcs))} VERIFIED {che} -> {expl}", flush=True)
        elif line.split()[2] == "GAVEUP":
            gu.append(line)
            print(f"   GAVEUP cutoff={n} b={b} chords={ch}  (UNKNOWN, not UNSAT)", flush=True)

print(f"LEVEL k={k} n={n} shapes={len(data)} eligible={len(elig)} sat={len(sat)} "
      f"gaveup={len(gu)} search_seconds={round(time.time()-t1,1)} "
      f"total_seconds={round(time.time()-t0,1)}", flush=True)
sys.exit(1 if gu else 0)
