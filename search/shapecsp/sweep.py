"""t_k by descending n: `python sweep.py k [floor] [nodecap]`

Loops n from the largest per-shape cap downward.  At each n the shapes that can
still reach it (cap >= n, and Hall's condition satisfied at n) are handed to
bb.exe, which decides each one exactly.  The first n with a SAT shape is t_k --
every larger n has been refuted for every shape, including the degenerate ones.
Anything bb.exe abandons on its node budget is reported as GAVEUP, never as
UNSAT.
"""
from __future__ import annotations
import subprocess, sys, time, os
import shapes as S
import bound as B

ARCORDER = "2"          # arcs assigned fewest-forms-first; measured fastest

k = int(sys.argv[1])
floor_n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
nodecap = sys.argv[3] if len(sys.argv) > 3 else "400000000"
HERE = os.path.dirname(os.path.abspath(__file__))
BB = os.path.join(HERE, "bb.exe")

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
    t1 = time.time()
    out = subprocess.run([BB, str(n), nodecap, ARCORDER], input="\n".join(lines) + "\n",
                         capture_output=True, text=True).stdout.splitlines()
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
            print(f"   SAT n={n} b={elig[i][1]} chords={elig[i][2]} "
                  f"arcs={l.split()[4].split('=')[1]}", flush=True)
        print(f"RESULT t_{k} = {n}" + (" (with unresolved GAVEUP shapes above)" if gaveup_total else ""),
              flush=True)
        break
else:
    print(f"RESULT no shape reaches n >= {floor_n}", flush=True)
print(f"gaveup_records={len(gaveup_total)} total_seconds={round(time.time()-t0,1)}", flush=True)
