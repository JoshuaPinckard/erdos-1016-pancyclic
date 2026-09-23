"""Independent recomputation of the expected unit set for one (n, b) tier,
compared against a runner's state file. Does not trust the runner's own
"exhausted" self-report; re-derives the unit key set from the hashed source
manifest using the same UNIT the runner uses.

Usage: python verify_tier_exhaustion.py <source_dir> <state_file> --n N --b B
"""
import argparse
import hashlib
import json
from pathlib import Path

UNIT = 50_000_000_000


def main():
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path)
    p.add_argument("state", type=Path)
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--b", type=int, required=True)
    args = p.parse_args()

    raw = (args.source / f"n{args.n}.jsonl").read_bytes()
    source_sha256 = hashlib.sha256(raw).hexdigest()
    rows = [json.loads(line) for line in raw.splitlines()]
    rows = [r for r in rows if r["b"] == args.b]

    expected = set()
    manifest_rank_total = 0
    for row in rows:
        manifest_rank_total += row["total"]
        for offset in range(0, row["total"], UNIT):
            count = min(UNIT, row["total"] - offset)
            expected.add((row["shape_index"], offset, count))

    state = json.loads(args.state.read_text(encoding="utf-8"))
    if state["source_sha256"] != source_sha256:
        print(json.dumps({"error": "source_sha256 mismatch",
                           "manifest_sha256": source_sha256,
                           "state_sha256": state["source_sha256"]}))
        return
    if state["n"] != args.n or state["min_b"] > args.b or state["max_b"] < args.b:
        print(json.dumps({"error": "state does not cover requested (n,b)",
                           "state_n": state["n"], "state_min_b": state["min_b"],
                           "state_max_b": state["max_b"]}))
        return

    covered = {tuple(x) for x in state["complete"] if
               x[0] in {r["shape_index"] for r in rows}}
    covered_rank_total = sum(c[2] for c in covered)

    missing = expected - covered
    extra = covered - expected

    result = {
        "n": args.n, "b": args.b,
        "source_sha256": source_sha256,
        "expected_unit_count": len(expected),
        "covered_unit_count": len(covered),
        "missing_unit_count": len(missing),
        "extra_unit_count": len(extra),
        "manifest_rank_total": manifest_rank_total,
        "covered_rank_total": covered_rank_total,
        "rank_totals_match": manifest_rank_total == covered_rank_total,
        "exact_match": len(missing) == 0 and len(extra) == 0 and manifest_rank_total == covered_rank_total,
        "hits": state.get("hits", []),
        "missing_sample": sorted(missing)[:5],
        "extra_sample": sorted(extra)[:5],
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
