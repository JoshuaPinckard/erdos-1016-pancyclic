"""Same-card comparison of the pairwise kernel against the production kernel.

For K sampled shapes of one tier (tables already built under --tables):

  pairwise     the whole admissible space of the shape, in launches of
               UNIT_PREFIX prefixes: gpu seconds and compositions counted;
  production   gpu_search.Engine over a fixed number of UNRESTRICTED ranks of
               the same shape: gpu seconds and ranks.

Reports compositions/s, ranks/s, the tier totals from the tier manifest and the
gpu-blast manifest, and the projected hours for the tier under each method.
Run this only inside an exclusive GPU window (rebalance/benchmark-window.ps1):
a shared card measures contention, not kernels.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROD = HERE.parent
for p in (str(HERE), str(PROD)):
    if p not in sys.path:
        sys.path.insert(0, p)
import pairwise_tables as PT        # noqa: E402
import gpu_search_pairwise as G     # noqa: E402
import gpu_search as GP             # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--b", type=int, required=True)
    p.add_argument("--tables", type=Path, default=HERE / "tables")
    p.add_argument("--shapes", type=int, default=6)
    p.add_argument("--ranks", type=int, default=20_000_000_000, help="unrestricted ranks per shape for the production kernel")
    p.add_argument("--max-prefixes", type=int, default=0, help="cap pairwise prefixes per shape (0 = whole shape)")
    p.add_argument("--seed", type=int, default=1016)
    p.add_argument("--seconds", type=float, default=420, help="stop sampling new shapes after this many wall seconds")
    p.add_argument("--out", type=Path, default=HERE / "perf-pairwise.json")
    args = p.parse_args()

    tdir = args.tables / f"n{args.n}-b{args.b}"
    manifest = json.loads((tdir / "tier-manifest.json").read_text(encoding="utf-8")) if (tdir / "tier-manifest.json").exists() else None
    built = sorted(int(f.stem.split("-")[1]) for f in tdir.glob("shape-*.npz"))
    rows = {r["shape_index"]: r for r in (json.loads(l) for l in (PROD / "gpu-blast" / f"n{args.n}.jsonl").read_text(encoding="utf-8").splitlines()) if r["b"] == args.b}
    rng = random.Random(args.seed)
    pick = sorted(rng.sample(built, min(args.shapes, len(built))))
    eng_p = G.Engine()
    eng_u = GP.Engine(12, 70, 127)
    t_start = time.perf_counter()
    per, tot = [], dict(comps=0, comp_s=0.0, ranks=0, rank_s=0.0, hits_p=0, hits_u=0)
    for idx in pick:
        if time.perf_counter() - t_start > args.seconds:
            break
        tab = PT.load(tdir / f"shape-{idx}.npz")
        row = rows[idx]
        # pairwise: whole shape (or capped), unit by unit
        total = tab["total_prefixes"]
        limit = total if not args.max_prefixes else min(total, args.max_prefixes)
        off, cs, comps, hp = 0, 0.0, 0, 0
        while off < limit:
            cnt = min(PT.UNIT_PREFIX, limit - off)
            hits, el, c, _ = eng_p.run(tab, off, cnt)
            cs += el
            comps += c
            hp += len(hits)
            off += cnt
        # production: fixed rank count of the same shape
        rec = GP.record(row["b"], [tuple(c) for c in row["chords"]])
        u_total = row["total"]
        uranks = min(args.ranks, u_total)
        uoff, us, hu = 0, 0.0, 0
        while uoff < uranks:
            cnt = min(20_000_000_000, uranks - uoff)
            h, el, _ = eng_u.run(args.n, [rec], [uoff], [1], cnt)
            us += el
            hu += len(h)
            uoff += cnt
        per.append(dict(shape_index=idx, unrestricted_total=u_total, admissible_total=tab["total_compositions"],
                        total_prefixes=total, prune=round(u_total / max(1, tab["total_compositions"]), 2),
                        pairwise_prefixes_run=limit, pairwise_compositions=comps, pairwise_gpu_s=round(cs, 3),
                        pairwise_comps_per_s=round(comps / cs) if cs else None, pairwise_hits=hp,
                        production_ranks_run=uranks, production_gpu_s=round(us, 3),
                        production_ranks_per_s=round(uranks / us) if us else None, production_hits=hu,
                        shape_hours_pairwise=round(tab["total_compositions"] / (comps / cs) / 3600, 4) if cs and comps else None,
                        shape_hours_production=round(u_total / (uranks / us) / 3600, 4) if us else None))
        print(json.dumps(per[-1]), flush=True)
        tot["comps"] += comps; tot["comp_s"] += cs; tot["ranks"] += uranks; tot["rank_s"] += us
        tot["hits_p"] += hp; tot["hits_u"] += hu
    cps = tot["comps"] / tot["comp_s"] if tot["comp_s"] else None
    rps = tot["ranks"] / tot["rank_s"] if tot["rank_s"] else None
    out = dict(n=args.n, b=args.b, shapes=len(per), shapes_built=len(built),
               pairwise_compositions=tot["comps"], pairwise_gpu_s=round(tot["comp_s"], 2),
               pairwise_comps_per_s=round(cps) if cps else None,
               production_ranks=tot["ranks"], production_gpu_s=round(tot["rank_s"], 2),
               production_ranks_per_s=round(rps) if rps else None,
               per_composition_cost_ratio_production_over_pairwise=round(cps / rps, 3) if cps and rps else None,
               hits_pairwise=tot["hits_p"], hits_production=tot["hits_u"], per_shape=per)
    if manifest:
        out["tier_admissible_total"] = manifest["tier_total_compositions"]
        out["tier_unrestricted_total"] = manifest["tier_unrestricted_ranks"]
        out["tier_prune"] = round(manifest["tier_unrestricted_ranks"] / manifest["tier_total_compositions"], 2)
        if cps:
            out["tier_hours_pairwise"] = round(manifest["tier_total_compositions"] / cps / 3600, 2)
        if rps:
            out["tier_hours_production"] = round(manifest["tier_unrestricted_ranks"] / rps / 3600, 2)
        if cps and rps:
            out["end_to_end_speedup"] = round(out["tier_hours_production"] / out["tier_hours_pairwise"], 1)
    args.out.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "per_shape"}), flush=True)


if __name__ == "__main__":
    main()
