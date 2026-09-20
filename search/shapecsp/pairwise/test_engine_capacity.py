"""The GPU engine sized for a level above 70 enumerates exactly what the CPU
tables enumerate, and the standard controls still pass on it.

The frozen runner built G.Engine() with its defaults (max_n=70), which refused
every level-71+ table ("tables exceed engine capacity", laptop chain v9 at
21:58 on 2026-09-19).  Sizing the engine by the level changes the kernel's
compile-time constants, so this test compiles that larger engine and checks it
against the CPU on real high-level shapes.

Usage: python test_engine_capacity.py [--prod DIR] [--tables tables-ext] [--source gpu-blast-ext] [--max-n 90]
Picks the smallest shape (by total_prefixes) of each named tier and visits every
prefix in debug mode: rows, flags and the compositions counter must equal
pairwise_tables.iterate_compositions and pairwise_tables.sat; then runs
gpu_search_pairwise.controls on the same engine (witnesses n=67, n=56).
Exit 0 only if every check passes.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prod", type=Path, default=HERE.parent / "pairwise-prod")
    p.add_argument("--tables", type=Path, default=HERE / "tables-ext")
    p.add_argument("--source", type=Path, default=HERE / "gpu-blast-ext")
    p.add_argument("--tiers", default="71:6,71:7,73:7,89:10,88:10")
    p.add_argument("--max-n", type=int, default=90)
    p.add_argument("--max-prefixes", type=int, default=200000, help="skip a shape whose prefix count exceeds this")
    args = p.parse_args()
    sys.path.insert(0, str(args.prod))
    sys.path.insert(0, str(args.prod.parent))
    import pairwise_tables as PT     # noqa: E402  (frozen)
    import gpu_search_pairwise as G  # noqa: E402  (frozen)

    eng = G.Engine(max_n=args.max_n)
    recs, fails = [], 0
    for spec in args.tiers.split(","):
        n, b = (int(x) for x in spec.split(":"))
        mpath = args.tables / f"n{n}-b{b}" / "tier-manifest.json"
        if not mpath.exists():
            recs.append(dict(tier=spec, skipped="no manifest"))
            continue
        m = json.loads(mpath.read_text(encoding="utf-8"))
        cands = sorted(m["shapes"].items(), key=lambda kv: int(kv[1]["total_prefixes"]))
        cands = [kv for kv in cands if 0 < int(kv[1]["total_prefixes"]) <= args.max_prefixes]
        if not cands:
            recs.append(dict(tier=spec, skipped=f"no shape with 0 < prefixes <= {args.max_prefixes}"))
            continue
        idx, meta = cands[0]
        tab = PT.load(args.tables / f"n{n}-b{b}" / f"shape-{idx}.npz", expected_sha256=meta["tables_sha256"])
        t0 = time.perf_counter()
        rows, flags, comps = [], [], 0
        off, total = 0, tab["total_prefixes"]
        while off < total:
            cnt = min(G.DEBUG_MAX, total - off)
            _, _, c, (r, f, _, _) = eng.run(tab, off, cnt, debug=True, verify_hits=False)
            rows.extend(r)
            flags.extend(f)
            comps += c
            off += cnt
        ref = list(PT.iterate_compositions(tab))
        forms = [tuple(x) for x in tab["forms"]]
        cpu_flags = [PT.sat(n, forms, a) for a in rows]
        rec = dict(tier=spec, shape=int(idx), n=n, b=b, vmax=tab["vmax"], forms=len(forms),
                   total_prefixes=total, total_compositions=tab["total_compositions"],
                   gpu_visited=len(rows), ordered_sequence_identical=(rows == ref),
                   counter_matches=(comps == tab["total_compositions"]),
                   flags_identical=(flags == cpu_flags), gpu_sat=sum(flags), cpu_sat=sum(cpu_flags),
                   seconds=round(time.perf_counter() - t0, 1))
        ok = rec["ordered_sequence_identical"] and rec["counter_matches"] and rec["flags_identical"]
        rec["ok"] = ok
        fails += int(not ok)
        recs.append(rec)
        print(json.dumps(rec), flush=True)
    control = G.controls(eng)
    print(json.dumps({"controls_on_large_engine": {k: control[k] for k in ("positive_control", "soundness_control_on_witnesses", "sample", "mismatches")}}), flush=True)
    control_ok = control["positive_control"] == "PASS" and control["mismatches"] == 0
    checked = [r for r in recs if "ok" in r]
    print(json.dumps({"engine_max_n": args.max_n, "shapes_checked": len(checked), "compositions_visited": sum(r["gpu_visited"] for r in checked),
                      "skipped": [r for r in recs if "skipped" in r], "failing": fails, "controls_ok": control_ok}), flush=True)
    return 0 if (checked and fails == 0 and control_ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
