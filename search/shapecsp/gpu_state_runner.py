"""Restartable bounded-unit exhaustive GPU runner.

Each invocation claims no more than wall_budget seconds.  Completion is
recorded atomically after every rank sub-range, so process loss can only lose
the current unit, never completed work.
"""
import argparse
import hashlib
import json
import math
import os
import time
from pathlib import Path

import gpu_search as G


UNIT = 50_000_000_000


def atomic_json(path, value):
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, indent=2)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path)
    p.add_argument("state", type=Path)
    p.add_argument("--n", type=int, choices=(68, 69), required=True)
    p.add_argument("--min-b", type=int, default=6)
    p.add_argument("--max-b", type=int, default=9)
    p.add_argument("--wall-budget", type=float, default=50.0)
    p.add_argument("--lock-stale", type=float, default=180.0)
    args = p.parse_args()
    lock = args.state.with_suffix(args.state.suffix + ".lock")
    args.state.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
    except FileExistsError:
        if time.time() - lock.stat().st_mtime < args.lock_stale:
            print("LOCKED", flush=True)
            return 2
        lock.unlink()
        return main()
    try:
        raw = (args.source / f"n{args.n}.jsonl").read_bytes()
        source_sha256 = hashlib.sha256(raw).hexdigest()
        rows = [json.loads(line) for line in raw.splitlines()]
        rows = [r for r in rows if args.min_b <= r["b"] <= args.max_b]
        units = []
        for row in rows:
            for offset in range(0, row["total"], UNIT):
                units.append({"shape_index": row["shape_index"], "b": row["b"],
                              "offset": offset, "count": min(UNIT, row["total"] - offset),
                              "total": row["total"]})
        if args.state.exists():
            state = json.loads(args.state.read_text(encoding="utf-8"))
            if state["source_sha256"] != source_sha256 or state["n"] != args.n:
                raise ValueError("state source or n mismatch")
        else:
            state = {"version": 1, "n": args.n, "min_b": args.min_b,
                     "max_b": args.max_b, "source_sha256": source_sha256,
                     "complete": [], "hits": []}
            atomic_json(args.state, state)
        # Older states carried the full deterministic unit plan.  Drop it on
        # the next checkpoint: regenerating it from the hashed source keeps
        # each atomic write proportional to completed work, not total work.
        state.pop("units", None)
        done = {tuple(x) for x in state["complete"]}
        by_shape = {r["shape_index"]: r for r in rows}
        engine = G.Engine(12, 70, 127)
        control = G.controls(engine)
        if control["positive_control"] != "PASS" or control["mismatches"] != 0:
            raise RuntimeError("POSITIVE CONTROL FAILED")
        start = time.monotonic()
        tested = 0
        for unit in units:
            key = (unit["shape_index"], unit["offset"], unit["count"])
            if key in done:
                continue
            if tested and time.monotonic() - start >= args.wall_budget:
                break
            row = by_shape[unit["shape_index"]]
            d = G.record(row["b"], row["chords"])
            found, elapsed, _ = engine.run(args.n, [d], [unit["offset"]], [1], unit["count"])
            for hit in found:
                hit["shape_index"] = row["shape_index"]
                state["hits"].append(hit)
                print("VERIFIED SAT", json.dumps(hit), flush=True)
            state["complete"].append(list(key))
            atomic_json(args.state, state)
            tested += unit["count"]
            print(json.dumps({"complete_units": len(state["complete"]),
                              "total_units": len(units),
                              "tested_this_invocation": tested,
                              "gpu_seconds": elapsed}), flush=True)
        print(json.dumps({"complete_units": len(state["complete"]),
                          "total_units": len(units),
                          "exhausted": len(state["complete"]) == len(units),
                          "tested_this_invocation": tested}), flush=True)
    finally:
        try:
            lock.unlink()
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    main()
