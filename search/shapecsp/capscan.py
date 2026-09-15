"""Decide every shape whose cap is at most `capmax`, at every n above `floor`.

`python capscan.py k floor capmax [nodecap] [jobs]`

A shape with cap C is irrelevant to any n > C, so deciding it means deciding
n = C, C-1, ..., floor+1.  Cost grows sharply with the coverage slack C - n, so
the low-cap shapes are the cheap ones; doing them first narrows where a
better-than-`floor` graph could possibly live, even when the full sweep is out of
reach.  Prints one line per shape that is SAT somewhere, and a summary of how
many shapes were fully decided versus abandoned on the node budget.
"""
from __future__ import annotations
import os, pickle, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
import shapes as S
import bound as B

k, floor_n, capmax = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
nodecap = sys.argv[4] if len(sys.argv) > 4 else "2000000000"
jobs = int(sys.argv[5]) if len(sys.argv) > 5 else 4
HERE = os.path.dirname(os.path.abspath(__file__))
BB = os.path.join(HERE, "bb")           # Linux build
if not os.path.exists(BB):
    BB = os.path.join(HERE, "bb.exe")   # Windows build

with open(os.path.join(HERE, f"forms-k{k}.pkl"), "rb") as fh:
    data = pickle.load(fh)
todo = [d for d in data if floor_n < d[0] <= capmax]
print(f"k={k} floor={floor_n} capmax={capmax} shapes_in_range={len(todo)} "
      f"(of {len(data)}; {sum(1 for d in data if d[0] > capmax)} have cap > capmax "
      f"and are NOT covered here)", flush=True)

t0 = time.time()
lock_out = []


def one(d):
    cap, b, ch, forms, lows, iv = d
    for n in range(cap, floor_n, -1):
        if sum(lows) > n or not B.hall_ok(iv, n):
            continue
        lines = [" ".join(map(str, [b, len(forms)] + lows))] + [f"{m} {c}" for m, c in forms]
        out = subprocess.run([BB, str(n), nodecap, "2"], input="\n".join(lines) + "\n",
                             capture_output=True, text=True).stdout.strip()
        if "GAVEUP" in out:
            return ("GAVEUP", n, b, ch, out)
        if " SAT " in out:
            return ("SAT", n, b, ch, out)
    return ("UNSAT", None, b, ch, "")


sat = gave = 0
with ThreadPoolExecutor(max_workers=jobs) as ex:
    for i, r in enumerate(ex.map(one, todo)):
        if r[0] == "SAT":
            sat += 1
            print(f"SAT n={r[1]} b={r[2]} chords={r[3]} :: {r[4]}", flush=True)
        elif r[0] == "GAVEUP":
            gave += 1
            print(f"GAVEUP n={r[1]} b={r[2]} chords={r[3]}", flush=True)
        if i % 250 == 249:
            print(f"# {i+1}/{len(todo)} elapsed={round(time.time()-t0)}s sat={sat} gaveup={gave}",
                  flush=True)
print(f"CAPSCAN k={k} floor={floor_n} capmax={capmax} shapes={len(todo)} "
      f"sat={sat} gaveup={gave} fully_decided={len(todo)-gave} "
      f"seconds={round(time.time()-t0,1)}", flush=True)
