"""Prune factor and cap-computation cost per (n, b) tier, over the WHOLE tier.

No sampling: every shape in the tier is measured, so the printed prune factor is
the tier's aggregate, not an estimate.  Cross-checks the DP rank-space size
against prune_probe's independent inclusion-exclusion count on every shape.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.dirname(__file__))

import bounded_caps as BC

SRC = os.path.join(os.path.dirname(__file__), "..", "gpu-blast")

for spec in sys.argv[1:]:
    n, b = (int(x) for x in spec.split(":"))
    rows = [json.loads(l) for l in open(os.path.join(SRC, f"n{n}.jsonl"), encoding="utf-8")]
    sel = [r for r in rows if r["b"] == b]
    t0 = time.perf_counter()
    ub = bd = ie_ok = 0
    worst = None
    for r in sel:
        box = BC.shape_box(n, r["b"], [tuple(c) for c in r["chords"]], r["lows"])
        if box["unrestricted_total"] != r["total"]:
            raise SystemExit(f"manifest total disagreement shape {r['shape_index']}")
        ub += r["total"]
        bd += box["total"]
        if box["total"] == BC.bounded_total_inclusion_exclusion(n, box["lows"], box["hi"]):
            ie_ok += 1
        f = r["total"] / box["total"] if box["total"] else float("inf")
        if worst is None or f < worst[1]:
            worst = (r["shape_index"], f)
    dt = time.perf_counter() - t0
    print(json.dumps({"n": n, "b": b, "shapes": len(sel), "caps_cpu_seconds": round(dt, 1),
                      "caps_cpu_seconds_per_shape": round(dt / len(sel), 4),
                      "unrestricted_ranks": ub, "bounded_ranks": bd,
                      "aggregate_prune_factor": round(ub / bd, 4) if bd else None,
                      "dp_equals_inclusion_exclusion": f"{ie_ok}/{len(sel)}",
                      "least_pruned_shape": worst[0],
                      "least_prune_factor": round(worst[1], 4)}), flush=True)
