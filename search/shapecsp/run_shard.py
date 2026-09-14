"""Shard of the per-shape sweep: `python run_shard.py k target shard nshards [tl] [workers]`

Every shape whose cap (#distinct cycle forms + 2) is >= target is tested for
"is there an arc assignment with n >= target?".  Shards are independent because
the target is fixed, so the union of the shards is the exact answer to
"t_k >= target?".  Output is one line per non-INFEASIBLE shape plus a summary.
"""
from __future__ import annotations
import sys, time
import shapes as S
import solve as SV

k, target, shard, nsh = map(int, sys.argv[1:5])
tl = float(sys.argv[5]) if len(sys.argv) > 5 else 300.0
wk = int(sys.argv[6]) if len(sys.argv) > 6 else 1

sh = S.shapes(k)
caps = sorted(((len(set(S.cycle_forms(b, c))) + 2, b, c) for b, c in sh), reverse=True)
mine = [x for i, x in enumerate(caps) if i % nsh == shard and x[0] >= target]
print(f"k={k} target={target} shard={shard}/{nsh} shapes_total={len(sh)} "
      f"above_cap={sum(1 for c in caps if c[0] >= target)} mine={len(mine)}", flush=True)

t0 = time.time()
sat = unk = 0
for j, (cap, b, c) in enumerate(mine):
    st, n, arcs = SV.solve_shape(b, c, target, tl, wk)
    if st in ("FEASIBLE", "OPTIMAL"):
        sat += 1
        print(f"SAT n={n} b={b} chords={c} arcs={arcs} cap={cap}", flush=True)
    elif st == "UNKNOWN":
        unk += 1
        print(f"UNKNOWN b={b} chords={c} cap={cap} tl={tl}", flush=True)
    if j % 100 == 99:
        print(f"# progress {j+1}/{len(mine)} elapsed={round(time.time()-t0)}s "
              f"sat={sat} unknown={unk}", flush=True)
print(f"DONE shard={shard} done={len(mine)} sat={sat} unknown={unk} "
      f"seconds={round(time.time()-t0,1)}", flush=True)
