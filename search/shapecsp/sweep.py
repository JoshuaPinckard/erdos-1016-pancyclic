"""t_k by descending n: `python sweep.py k [floor] [nodecap]`

Loops n from the largest per-shape cap downward.  At each n the shapes that can
still reach it (cap >= n, and Hall's condition satisfied at n) are handed to bb,
which decides each one exactly.  The first n with a SAT shape is t_k -- every
larger n has been refuted for every shape, including the degenerate ones.  The
descending sweep is also what makes the eligibility filter safe here: a shape is
tested at every n it could be feasible at, because Hall is evaluated at that same
n, so no value slips past it.

Anything bb abandons on its node budget is reported as GAVEUP, never as UNSAT.

RESULT INTEGRITY.  This is the driver behind the t_k positive control, so the
same contract as level.py applies: the solver must exit 0, every eligible shape
must return exactly one well-formed terminal record, and every SAT is re-derived
by verify.check_record -- which materialises the graph and tests pancyclicity
without the reformulation -- before it is allowed to end the sweep.  A violation
aborts with a non-zero exit instead of being read as a refutation.
"""
from __future__ import annotations
import subprocess, sys, time, os
import shapes as S
import bound as B
import verify as V

ARCORDER = "2"          # arcs assigned fewest-forms-first; measured fastest

k = int(sys.argv[1])
floor_n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
nodecap = sys.argv[3] if len(sys.argv) > 3 else "400000000"
HERE = os.path.dirname(os.path.abspath(__file__))
BB = os.path.join(HERE, "bb")           # Linux build
if not os.path.exists(BB):
    BB = os.path.join(HERE, "bb.exe")   # Windows build

t0 = time.time()
cache = os.path.join(HERE, f"forms-k{k}.pkl")
if os.path.exists(cache):
    import pickle
    data = pickle.load(open(cache, "rb"))
else:
    data = []
    for b, ch in S.shapes(k):
        forms = sorted(set(S.cycle_forms(b, ch)))
        iv, lows = B.intervals(b, ch, forms=forms)
        data.append((len(forms) + 2, b, ch, forms, lows, iv))
    import pickle
    pickle.dump(data, open(cache, "wb"))
print(f"k={k} shapes={len(data)} max_cap={max(d[0] for d in data)} "
      f"forms_built_in={round(time.time()-t0,1)}s", flush=True)

gaveup_total = []
for n in range(max(d[0] for d in data), floor_n - 1, -1):
    elig = [d for d in data if d[0] >= n and sum(d[4]) <= n and B.hall_ok(d[5], n)]
    if not elig:
        print(f"n={n}: 0 shapes survive cap+Hall", flush=True)
        continue
    lines = []
    for cap, b, ch, forms, lows, iv in elig:
        lines.append(" ".join(map(str, [b, len(forms)] + lows)))
        lines += [f"{mm} {cc}" for mm, cc in forms]
    payload = "\n".join(lines) + "\n"
    t1 = time.time()
    proc = subprocess.run([BB, str(n), nodecap, ARCORDER], input=payload,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"SWEEP k={k} FAILED -- solver exited {proc.returncode} at n={n}; "
              f"stderr={proc.stderr.strip()[:300]!r}", flush=True)
        sys.exit(1)
    recs = {}
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if (len(parts) < 3 or parts[0] != "SHAPE" or not parts[1].isdigit()
                or parts[2] not in ("SAT", "UNSAT", "GAVEUP")):
            print(f"SWEEP k={k} FAILED -- unrecognised solver line {line!r} at n={n}", flush=True)
            sys.exit(1)
        idx = int(parts[1])
        if not 1 <= idx <= len(elig) or idx in recs:
            print(f"SWEEP k={k} FAILED -- shape index {idx} out of range or repeated at n={n}",
                  flush=True)
            sys.exit(1)
        recs[idx] = line
    if len(recs) != len(elig):
        print(f"SWEEP k={k} FAILED -- {len(elig) - len(recs)} of {len(elig)} eligible shapes "
              f"produced no terminal record at n={n}; that is UNKNOWN, not a refutation",
              flush=True)
        sys.exit(1)
    out = [recs[j] for j in range(1, len(elig) + 1)]
    sat = [l for l in out if " SAT " in l]
    gu = [l for l in out if "GAVEUP" in l]
    print(f"n={n}: eligible={len(elig)} sat={len(sat)} gaveup={len(gu)} "
          f"[{round(time.time()-t1,1)}s, cum {round(time.time()-t0,1)}s]", flush=True)
    for l in gu:
        i = int(l.split()[1]) - 1
        gaveup_total.append((n, elig[i][1], elig[i][2]))
        print(f"   GAVEUP n={n} b={elig[i][1]} chords={elig[i][2]}", flush=True)
    if sat:
        for l in sat:
            i = int(l.split()[1]) - 1
            cap, b, ch, forms, lows, iv = elig[i]
            got, why = V.check_record(l, b, ch, lows, cap, n)
            if why is not None:
                print(f"SWEEP k={k} FAILED -- n={n} b={b} chords={ch}: {why}", flush=True)
                sys.exit(1)
            nv, arcs, che, expl = got
            print(f"   SAT n={nv} b={b} chords={ch} arcs={','.join(map(str, arcs))} "
                  f"VERIFIED {che} -> {expl}", flush=True)
        print(f"RESULT t_{k} = {n}" + (" (with unresolved GAVEUP shapes above)" if gaveup_total else ""),
              flush=True)
        break
else:
    print(f"RESULT no shape reaches n >= {floor_n}", flush=True)
print(f"gaveup_records={len(gaveup_total)} total_seconds={round(time.time()-t0,1)}", flush=True)
sys.exit(1 if gaveup_total else 0)
