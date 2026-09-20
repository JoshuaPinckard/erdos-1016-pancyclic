"""Rank/unit census for the (level, tier) jobs, and progress against it.

Re-derives the unit plan the same way gpu_state_runner.py and
verify_tier_exhaustion.py do -- from the hashed manifest with the same UNIT --
so a count here is comparable to what either of those reports.  Nothing is
taken from a runner's self-report.

Usage:
  python census.py <gpu-blast-dir> [--state-dir DIR] [--state-glob PATTERN]

Prints one JSON document: per (n, b) manifest totals, and for every state file
found, how many of that tier's units it covers.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path

UNIT = 50_000_000_000


def tier_plan(src: Path, n: int):
    """Return (sha256, {b: {"shapes", "ranks", "units", "keys"}}) for level n."""
    raw = (src / f"n{n}.jsonl").read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    rows = [json.loads(line) for line in raw.splitlines()]
    tiers = {}
    for row in rows:
        t = tiers.setdefault(row["b"], {"shapes": 0, "ranks": 0, "keys": set()})
        t["shapes"] += 1
        t["ranks"] += row["total"]
        for offset in range(0, row["total"], UNIT):
            t["keys"].add((row["shape_index"], offset,
                           min(UNIT, row["total"] - offset)))
    return sha, tiers


def main():
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path)
    p.add_argument("--levels", type=int, nargs="+", default=[68, 69, 70])
    p.add_argument("--state-dir", type=Path, action="append", default=[])
    p.add_argument("--state-glob", default="*state*.json")
    # Write the document ourselves rather than through a shell redirect:
    # PowerShell's ">" produces UTF-16LE with a BOM, which json.load rejects
    # with "Expecting value: line 1 column 1", a failure that looks like a
    # corrupt census rather than a corrupt redirect.
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args()

    out = {
        "sampled_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "unit_ranks": UNIT,
        "levels": {},
        "states": [],
    }

    plans = {}
    for n in args.levels:
        sha, tiers = tier_plan(args.source, n)
        plans[n] = (sha, tiers)
        out["levels"][str(n)] = {
            "source_sha256": sha,
            "tiers": {str(b): {"shapes": t["shapes"], "ranks": t["ranks"],
                               "units": len(t["keys"])}
                      for b, t in sorted(tiers.items())},
        }

    for d in args.state_dir:
        for f in sorted(Path(d).glob(args.state_glob)):
            try:
                state = json.loads(f.read_text(encoding="utf-8"))
            except (ValueError, OSError) as exc:
                # Not a silent skip: name the file and why it was not counted.
                out["states"].append({"path": str(f), "unreadable": str(exc)})
                continue
            n = state.get("n")
            rec = {
                "path": str(f),
                "n": n,
                "min_b": state.get("min_b"),
                "max_b": state.get("max_b"),
                "complete_units": len(state.get("complete", [])),
                "hits": len(state.get("hits", [])),
                "mtime_utc": datetime.datetime.fromtimestamp(
                    f.stat().st_mtime, datetime.timezone.utc).isoformat(),
                "state_sha256": state.get("source_sha256"),
            }
            if n in plans:
                sha, tiers = plans[n]
                rec["manifest_sha256"] = sha
                rec["source_matches_manifest"] = (sha == state.get("source_sha256"))
                covered = {tuple(x) for x in state.get("complete", [])}
                per_tier = {}
                for b, t in sorted(tiers.items()):
                    hit = len(covered & t["keys"])
                    if hit:
                        per_tier[str(b)] = {
                            "covered_units": hit,
                            "tier_units": len(t["keys"]),
                            "remaining_units": len(t["keys"]) - hit,
                            "covered_ranks": sum(
                                k[2] for k in covered & t["keys"]),
                            "tier_ranks": t["ranks"],
                        }
                rec["per_tier"] = per_tier
            else:
                rec["manifest_sha256"] = None
                rec["source_matches_manifest"] = None
                rec["note"] = "level not in --levels; coverage not computed"
            out["states"].append(rec)

    text = json.dumps(out, indent=2)
    if args.out is not None:
        args.out.write_text(text + "\n", encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
