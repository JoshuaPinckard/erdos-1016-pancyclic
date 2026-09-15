"""Controls-first exhaustive completion of one n and a bounded b range.

The source manifest must be a complete gpu_search.py census.  Only the
requested b levels are copied and exhausted; no claim is made for b>=10.
"""
import argparse
import hashlib
import json
import time
from pathlib import Path

import gpu_search as G


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--n", type=int, choices=(68, 69), default=68)
    p.add_argument("--b", type=int, default=None)
    p.add_argument("--min-b", type=int, default=6)
    p.add_argument("--max-b", type=int, default=9)
    p.add_argument("--first", type=int, default=0)
    p.add_argument("--last", type=int, default=None)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    engine = G.Engine(12, 70, 127)
    control = G.controls(engine)
    (args.output / "controls.json").write_text(
        json.dumps(control, indent=2) + "\n", encoding="utf-8"
    )
    print("POSITIVE CONTROL PASS", flush=True)

    raw = (args.source / f"n{args.n}.jsonl").read_bytes()
    source_sha256 = hashlib.sha256(raw).hexdigest()
    rows = [json.loads(line) for line in raw.splitlines()]
    rows = [row for row in rows if args.min_b <= row["b"] <= args.max_b]
    summary = dict(
        scope="all eligible n=68 b=8 and b=9 shapes",
        source_sha256=source_sha256,
        levels=[],
    )
    levels = (args.b,) if args.b is not None else tuple(range(args.min_b, args.max_b + 1))
    for b in levels:
        level_rows = [row for row in rows if row["b"] == b]
        last = len(level_rows) if args.last is None else min(args.last, len(level_rows))
        level_rows = level_rows[args.first:last]
        t0 = time.time()
        gpu_seconds = 0.0
        hits = []
        manifest = args.output / f"n{args.n}-b{b}.jsonl"
        completed = 0
        if manifest.exists():
            prior = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines()]
            expected = [row["shape_index"] for row in level_rows[: len(prior)]]
            actual = [row["shape_index"] for row in prior]
            if actual != expected:
                raise ValueError(f"resume manifest is not a prefix for b={b}")
            completed = len(prior)
        with manifest.open("a", encoding="utf-8", newline="\n") as out:
            for index, row in enumerate(level_rows[completed:], completed + 1):
                d = G.record(row["b"], row["chords"])
                found, elapsed, _ = engine.run(
                    args.n, [d], [row["start"]], [row["step"]], row["total"]
                )
                for hit in found:
                    hit["shape_index"] = row["shape_index"]
                    print("VERIFIED SAT", json.dumps(hit), flush=True)
                hits.extend(found)
                gpu_seconds += elapsed
                row["count"] = row["total"]
                out.write(json.dumps(row) + "\n")
                out.flush()
                if index == 1 or index % 32 == 0 or index == len(level_rows):
                    print(
                        json.dumps(
                            dict(
                                progress=b,
                                shape=index,
                                shapes=len(level_rows),
                                tested=sum(r["count"] for r in level_rows[:index]),
                                gpu_seconds=gpu_seconds,
                            )
                        ),
                        flush=True,
                    )
        level = dict(
            n=args.n,
            b=b,
            eligible=len(level_rows),
            first=args.first,
            last=last,
            tested=sum(row["count"] for row in level_rows),
            gpu_seconds=gpu_seconds,
            wall_seconds=time.time() - t0,
            start_time=t0,
            end_time=time.time(),
            hits=hits,
        )
        summary["levels"].append(level)
        (args.output / "summary.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(level), flush=True)


if __name__ == "__main__":
    main()
