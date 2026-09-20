"""Independent verification of one (n, b) tier exhausted under the pairwise plan.

Does not trust the runner's own summary line.  From the gpu-blast manifest and
the tier manifest it re-derives the expected unit set, then checks the state:

  * enumeration tag and plan hash are the pairwise ones;
  * zero missing and zero extra units;
  * per shape, the sum of the compositions the kernel counted equals the tier
    manifest's total_compositions, and the tier total matches;
  * every gpu-blast shape of the tier is present in the tier manifest and the
    manifest's unrestricted totals equal the gpu-blast rows;
  * optionally (--rebuild K) rebuilds the tables of K shapes from scratch and
    compares their hashes with the manifest, so the manifest is not taken on
    trust either.

Usage: python verify_tier_exhaustion_pairwise.py <source_dir> <state_file> --n N --b B [--tables DIR] [--rebuild K]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROD = HERE.parent
for p in (str(HERE), str(PROD)):
    if p not in sys.path:
        sys.path.insert(0, p)
import pairwise_tables as PT     # noqa: E402

UNIT = PT.UNIT_PREFIX
ENUMERATION = "pairwise-v1"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path)
    p.add_argument("state", type=Path)
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--b", type=int, required=True)
    p.add_argument("--tables", type=Path, default=HERE / "tables")
    p.add_argument("--rebuild", type=int, default=0, help="rebuild this many random shapes' tables and compare hashes")
    args = p.parse_args()

    raw = (args.source / f"n{args.n}.jsonl").read_bytes()
    source_sha256 = hashlib.sha256(raw).hexdigest()
    rows = [json.loads(line) for line in raw.splitlines()]
    rows = [r for r in rows if r["b"] == args.b]
    mpath = args.tables / f"n{args.n}-b{args.b}" / "tier-manifest.json"
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    state = json.loads(args.state.read_text(encoding="utf-8"))
    out = {"n": args.n, "b": args.b, "source_sha256": source_sha256, "errors": []}

    if manifest["source_sha256"] != source_sha256:
        out["errors"].append("tier manifest source_sha256 != gpu-blast manifest")
    if manifest.get("partial"):
        out["errors"].append("tier manifest is partial")
    if state.get("enumeration") != ENUMERATION:
        out["errors"].append(f"state enumeration {state.get('enumeration')!r} != {ENUMERATION!r}")
    if state.get("source_sha256") != source_sha256 or state.get("n") != args.n or state.get("b") != args.b:
        out["errors"].append("state source/n/b mismatch")
    if state.get("only_shapes") is not None:
        out["errors"].append("state was restricted with --only-shapes; it is not a tier exhaustion by itself")
    mshapes = {int(k): v for k, v in manifest["shapes"].items()}
    tshapes = {r["shape_index"]: r for r in rows}
    if set(mshapes) != set(tshapes):
        out["errors"].append(f"manifest shapes {len(mshapes)} != gpu-blast tier shapes {len(tshapes)}")
    for idx, r in tshapes.items():
        if idx in mshapes and int(mshapes[idx]["unrestricted_total"]) != int(r["total"]):
            out["errors"].append(f"unrestricted total mismatch for shape {idx}")

    unit = int(manifest["unit_prefix"])
    if state.get("unit_prefix") != unit:
        out["errors"].append(f"state unit_prefix {state.get('unit_prefix')} != manifest unit_prefix {unit}")
    expected = {}
    for idx, meta in mshapes.items():
        total = int(meta["total_prefixes"])
        for offset in range(0, total, unit):
            expected[(idx, offset, min(unit, total - offset))] = meta["tables_sha256"]
    covered = {}
    for entry in state["complete"]:
        key = tuple(int(x) for x in entry[:3])
        if key in covered:
            out["errors"].append(f"duplicate unit {key}")
        covered[key] = int(entry[3]) if len(entry) > 3 else None
    missing = sorted(set(expected) - set(covered))
    extra = sorted(set(covered) - set(expected))
    per_shape = {}
    for key, comps in covered.items():
        if key in expected and comps is not None:
            per_shape[key[0]] = per_shape.get(key[0], 0) + comps
    comp_mismatch = [idx for idx, meta in mshapes.items()
                     if int(meta["total_prefixes"]) > 0 and per_shape.get(idx, -1) != int(meta["total_compositions"])]
    tier_total = sum(int(m["total_compositions"]) for m in mshapes.values())
    counted = sum(per_shape.values())
    recomputed_plan = None
    try:
        import gpu_state_runner_pairwise as R
        units = R.build_units(manifest, None)
        recomputed_plan = R.plan_hash(args.n, args.b, manifest, source_sha256, units, None)
        if state.get("plan_sha256") != recomputed_plan:
            out["errors"].append("state plan_sha256 != plan recomputed from the tier manifest")
    except Exception as exc:
        out["errors"].append(f"could not recompute plan hash: {exc!r}")

    rebuilt = []
    if args.rebuild:
        rng = random.Random(args.n * 1000 + args.b)
        for idx in rng.sample(sorted(mshapes), min(args.rebuild, len(mshapes))):
            r = tshapes[idx]
            tab = PT.build(args.n, r["b"], r["chords"], r["lows"], shape_index=idx)
            ok = (tab["tables_sha256"] == mshapes[idx]["tables_sha256"]
                  and tab["total_prefixes"] == int(mshapes[idx]["total_prefixes"])
                  and tab["total_compositions"] == int(mshapes[idx]["total_compositions"]))
            rebuilt.append({"shape_index": idx, "hash_and_totals_match": ok})
            if not ok:
                out["errors"].append(f"rebuilt tables for shape {idx} disagree with the manifest")

    out.update({
        "tier_manifest_sha256": hashlib.sha256(mpath.read_bytes()).hexdigest(),
        "state_tier_manifest_sha256": state.get("tier_manifest_sha256"),
        "expected_unit_count": len(expected), "covered_unit_count": len(covered),
        "missing_unit_count": len(missing), "extra_unit_count": len(extra),
        "shapes_in_tier": len(mshapes), "shapes_with_empty_admissible_set": len(manifest.get("excluded", [])),
        "tier_total_compositions_manifest": tier_total, "compositions_counted_by_kernel": counted,
        "composition_totals_match": counted == tier_total and not comp_mismatch,
        "shapes_with_composition_mismatch": comp_mismatch[:10],
        "tier_unrestricted_ranks": manifest.get("tier_unrestricted_ranks"),
        "prune_factor": round(manifest["tier_unrestricted_ranks"] / tier_total, 3) if tier_total else None,
        "hits": state.get("hits", []),
        "rebuilt_shapes": rebuilt,
        "missing_sample": missing[:5], "extra_sample": extra[:5],
    })
    out["exact_match"] = (not out["errors"] and not missing and not extra and out["composition_totals_match"])
    print(json.dumps(out, indent=1))
    return 0 if out["exact_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
