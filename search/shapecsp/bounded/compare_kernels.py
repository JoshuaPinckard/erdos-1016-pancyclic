"""Paired comparison of the production and bounded kernels on THE SAME shapes.

Two modes, because they answer different questions and mixing them gives a
meaningless ratio (the two kernels cut a tier into different shapes-per-unit,
so a fixed wall budget lands on different shapes and the ranks/s are not
comparable):

  throughput  identical shapes, identical rank COUNT through each kernel.
              Isolates cost per rank, which is the only thing the new unrank
              changes.  End-to-end gain = prune factor x this ratio.

  exhaust     identical shapes, each kernel run over its OWN whole space to
              completion.  This is the real end-to-end number and the real
              differential test: both kernels must report the same hits.

Nothing here writes a state file; both engines are driven directly.
"""
import argparse
import json
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.dirname(__file__))

import gpu_search as GP           # production kernel, imported read-only
import gpu_search_bounded as GB
import bounded_caps as BC

CHUNK = 20_000_000_000


def scan(engine, n, rec, total, limit=None):
    """Run ranks 0..min(total,limit)-1 through one engine; return hits, seconds."""
    end = total if limit is None else min(total, limit)
    off = 0
    hits = []
    secs = 0.0
    while off < end:
        cnt = min(CHUNK, end - off)
        found, el, _ = engine.run(n, [rec], [off], [1], cnt)
        hits.extend(found)
        secs += el
        off += cnt
    return hits, secs, end


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--b", type=int, required=True)
    p.add_argument("--mode", choices=["throughput", "exhaust"], required=True)
    p.add_argument("--shapes", type=int, default=6)
    p.add_argument("--ranks", type=int, default=20_000_000_000,
                   help="throughput mode only: ranks pushed through EACH kernel")
    p.add_argument("--seed", type=int, default=1016)
    args = p.parse_args()

    src = os.path.join(os.path.dirname(__file__), "..", "gpu-blast", f"n{args.n}.jsonl")
    rows = [json.loads(l) for l in open(src, encoding="utf-8")]
    rows = [r for r in rows if r["b"] == args.b]
    rng = random.Random(args.seed)
    pick = sorted(rng.sample(range(len(rows)), min(args.shapes, len(rows))))
    print(json.dumps({"caps_declared": {
        "tier": f"n={args.n} b={args.b}", "shapes_in_tier": len(rows),
        "shapes_sampled": len(pick), "sampling": f"random.Random({args.seed}).sample",
        "mode": args.mode,
        "ranks_per_kernel_per_shape": args.ranks if args.mode == "throughput" else "whole space",
        "gpu_is_shared": "the production chain is running on the same GPU; both "
                         "kernels are measured back to back under that load"}}), flush=True)

    ep = GP.Engine(12, 70, 127)
    eb = GB.Engine(12, 70, 127)
    tot_u_ranks = tot_b_ranks = 0
    tot_u_secs = tot_b_secs = 0.0
    hits_u = hits_b = 0
    for i in pick:
        row = rows[i]
        chords = [tuple(c) for c in row["chords"]]
        pr = GP.record(row["b"], chords)
        bx = BC.shape_box(args.n, row["b"], chords, row["lows"])
        u_total = math.comb(args.n - sum(pr["lows"]) + row["b"] - 1, row["b"] - 1)
        if u_total != row["total"]:
            raise SystemExit("manifest total disagreement")
        limit = args.ranks if args.mode == "throughput" else None
        hu, su, du = scan(ep, args.n, pr, u_total, limit)
        hb, sb, db = scan(eb, args.n, bx, bx["total"], limit)
        tot_u_ranks += du
        tot_b_ranks += db
        tot_u_secs += su
        tot_b_secs += sb
        hits_u += len(hu)
        hits_b += len(hb)
        print(json.dumps({"shape_index": row["shape_index"], "b": row["b"],
                          "unrestricted_total": u_total, "bounded_total": bx["total"],
                          "prune_factor": round(u_total / bx["total"], 4),
                          "unrestricted_ranks_run": du, "unrestricted_gpu_seconds": round(su, 2),
                          "bounded_ranks_run": db, "bounded_gpu_seconds": round(sb, 2),
                          "unrestricted_hits": len(hu), "bounded_hits": len(hb),
                          "hits_agree": len(hu) == len(hb)}), flush=True)

    out = {"mode": args.mode, "n": args.n, "b": args.b, "shapes": len(pick),
           "unrestricted_ranks": tot_u_ranks, "unrestricted_gpu_seconds": round(tot_u_secs, 2),
           "unrestricted_ranks_per_second": round(tot_u_ranks / tot_u_secs) if tot_u_secs else None,
           "bounded_ranks": tot_b_ranks, "bounded_gpu_seconds": round(tot_b_secs, 2),
           "bounded_ranks_per_second": round(tot_b_ranks / tot_b_secs) if tot_b_secs else None,
           "unrestricted_hits": hits_u, "bounded_hits": hits_b,
           "hits_agree": hits_u == hits_b}
    if args.mode == "throughput":
        out["per_rank_throughput_ratio_bounded_over_unrestricted"] = round(
            (tot_b_ranks / tot_b_secs) / (tot_u_ranks / tot_u_secs), 4)
        out["note"] = ("equal rank counts through each kernel; multiply this ratio by the "
                       "tier prune factor from measure_prune.py for the end-to-end gain")
    else:
        out["end_to_end_wall_speedup"] = round(tot_u_secs / tot_b_secs, 4)
        out["rank_space_prune_on_these_shapes"] = round(tot_u_ranks / tot_b_ranks, 4)
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
