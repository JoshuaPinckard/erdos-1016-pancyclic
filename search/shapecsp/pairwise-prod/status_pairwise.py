"""Progress and projection for the pairwise chains, from state files and manifests.

Usage: python status_pairwise.py [--tables DIR] [--states DIR] [--partitions DIR] [--log FILE]
For each tier with a pairwise-state file: units and compositions done against
the plan (only_shapes-restricted), the rate over the last units of the chain
log, and the projected hours for the machine's remaining tiers.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gpu_state_runner_pairwise as R   # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tables", type=Path, default=HERE / "tables")
    p.add_argument("--states", type=Path, default=HERE)
    p.add_argument("--partitions", type=Path, default=HERE / "partitions")
    p.add_argument("--log", type=Path, default=HERE.parent / "chain-desktop.log")
    p.add_argument("--tiers", default="69:11,68:12,69:12")
    p.add_argument("--last", type=int, default=200, help="units of the log to average the rate over")
    args = p.parse_args()

    rate = None
    if args.log.exists():
        comps = secs = 0
        n = 0
        for line in reversed(args.log.read_text(encoding="utf-8", errors="replace").splitlines()):
            if '"compositions"' in line and '"gpu_seconds"' in line:
                try:
                    j = json.loads(line)
                except json.JSONDecodeError:
                    continue
                comps += j["compositions"]
                secs += j["gpu_seconds"]
                n += 1
                if n >= args.last:
                    break
        if secs:
            rate = comps / secs
    total_left = 0
    rows = []
    for t in args.tiers.split(","):
        n_, b_ = (int(x) for x in t.split(":"))
        mpath = args.tables / f"n{n_}-b{b_}" / "tier-manifest.json"
        if not mpath.exists():
            rows.append({"tier": t, "error": "no manifest"})
            continue
        m = json.loads(mpath.read_text(encoding="utf-8"))
        ppath = args.partitions / f"n{n_}-b{b_}-remaining.json"
        subset = set(json.loads(ppath.read_text())) if ppath.exists() else None
        units = R.build_units(m, subset)
        plan_comps = sum(int(m["shapes"][str(i)]["total_compositions"]) for i in (subset if subset is not None else map(int, m["shapes"])))
        spath = args.states / f"pairwise-state-n{n_}-b{b_}.json"
        done_units = done_comps = 0
        hits = None
        if spath.exists():
            s = json.loads(spath.read_text(encoding="utf-8"))
            done_units = len(s["complete"])
            done_comps = sum(int(e[3]) for e in s["complete"] if len(e) > 3)
            hits = len(s.get("hits", []))
        left = plan_comps - done_comps
        total_left += max(0, left)
        rows.append({"tier": t, "shapes_in_plan": len(subset) if subset is not None else len(m["shapes"]),
                     "units": f"{done_units}/{len(units)}", "compositions_done": done_comps,
                     "compositions_plan": plan_comps, "fraction": round(done_comps / plan_comps, 4) if plan_comps else None,
                     "hits": hits, "hours_left_at_rate": round(left / rate / 3600, 2) if rate and left > 0 else None})
    for r in rows:
        print(json.dumps(r))
    print(json.dumps({"rate_compositions_per_gpu_second": round(rate) if rate else None,
                      "compositions_left": total_left,
                      "hours_left_at_rate": round(total_left / rate / 3600, 2) if rate else None}))


if __name__ == "__main__":
    main()
