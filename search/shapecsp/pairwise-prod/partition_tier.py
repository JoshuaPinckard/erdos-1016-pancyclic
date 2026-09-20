"""Split one (n, b) tier between the finished unrestricted work and the pairwise plan.

Reads the unrestricted runner's state file for the tier and the gpu-blast
manifest, and classifies every shape of the tier:

  done       every unrestricted unit of the shape is complete: the shape is
             exhausted under the unrestricted plan and is NOT re-run;
  remaining  anything else (untouched, or partially covered -- at 10-47x it is
             cheaper to redo a partial shape under the pairwise plan than to
             finish it unrestricted).

Writes <out>/n{N}-b{B}-remaining.json, the JSON list gpu_state_runner_pairwise
takes as --only-shapes, plus a sidecar summary.  The exhaustion statement for
the tier is then

    verify_tier_exhaustion.py (unrestricted state) exact on the done shapes
  + verify_tier_exhaustion_pairwise.py (pairwise state) exact on the remaining
  = every shape of the tier.

check_partition() re-derives the same split and is what the final verifier
calls, so the file written here is never taken on trust.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

UNIT = 50_000_000_000


def unrestricted_units(row):
    return {(row["shape_index"], off, min(UNIT, row["total"] - off)) for off in range(0, row["total"], UNIT)}


def partition(source, state_path, n, b):
    raw = (Path(source) / f"n{n}.jsonl").read_bytes()
    source_sha256 = hashlib.sha256(raw).hexdigest()
    rows = [r for r in (json.loads(l) for l in raw.splitlines()) if r["b"] == b]
    done_units = set()
    if state_path and Path(state_path).exists():
        state = json.loads(Path(state_path).read_text(encoding="utf-8"))
        if state.get("source_sha256") != source_sha256 or state.get("n") != n:
            raise ValueError("unrestricted state does not belong to this manifest/level")
        if state.get("enumeration") not in (None,):
            raise ValueError("state file is not an unrestricted-plan state")
        if not (state["min_b"] <= b <= state["max_b"]):
            raise ValueError("state does not cover this tier")
        done_units = {tuple(x) for x in state["complete"]}
        if state.get("hits"):
            raise ValueError("state has hits; a partition is not the right tool here")
    done, remaining, partial = [], [], []
    ranks_done = ranks_remaining = 0
    for r in rows:
        units = unrestricted_units(r)
        have = units & done_units
        if have == units:
            done.append(r["shape_index"])
            ranks_done += r["total"]
        else:
            remaining.append(r["shape_index"])
            ranks_remaining += r["total"]
            if have:
                partial.append(r["shape_index"])
    return dict(n=n, b=b, source_sha256=source_sha256, shapes=len(rows),
                done=sorted(done), remaining=sorted(remaining), partial_abandoned=sorted(partial),
                unrestricted_ranks_done=ranks_done, unrestricted_ranks_remaining=ranks_remaining,
                state_file=str(state_path) if state_path else None,
                state_complete_units=len(done_units))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--state", default=None, help="unrestricted state file for the tier (omit if the tier never started)")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--b", type=int, required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    part = partition(args.source, args.state, args.n, args.b)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"n{args.n}-b{args.b}-remaining.json").write_text(json.dumps(part["remaining"]) + "\n", encoding="utf-8")
    (out / f"n{args.n}-b{args.b}-partition.json").write_text(json.dumps(part, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in part.items() if k not in ("done", "remaining", "partial_abandoned")}
                     | {"done_shapes": len(part["done"]), "remaining_shapes": len(part["remaining"]),
                        "partial_abandoned": len(part["partial_abandoned"])}))


if __name__ == "__main__":
    main()
