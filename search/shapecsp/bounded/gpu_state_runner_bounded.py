"""Restartable bounded-unit GPU runner over the BOUNDED composition space.

Same contract as gpu_state_runner.py -- claim at most wall_budget seconds,
record completion atomically after every rank sub-range, exit 2 on LOCKED --
with one deliberate difference that callers must understand:

    A COMPLETED UNIT MEANS SOMETHING DIFFERENT HERE.

gpu_state_runner.py records (shape_index, offset, count) over the UNRESTRICTED
rank space of a shape.  This runner records the same triple over the BOUNDED
rank space.  The two spaces have different sizes and different rank->arcs maps,
so the same triple names a different set of compositions in each.  Unit
(i, 0, 50000000000) exists in both plans whenever the shape is larger than one
unit, and the two mean different work.

state["source_sha256"] cannot separate them: it hashes gpu-blast/nNN.jsonl,
which is identical either way.  Reusing an unrestricted state file here would
therefore mark bounded ranks complete that were never tested -- a silent gap in
an exhaustion claim.  So the state carries two extra fields:

    enumeration  "bounded-v1"; a state file without it was written by the
                 unrestricted runner and is refused outright
    plan_sha256  hash of the whole unit plan INCLUDING the per-arc caps, so a
                 change in the cap rule also invalidates the file

Both are checked before any unit is skipped.  The failure mode is a refusal to
run, never a quietly reduced search.
"""
import argparse
import hashlib
import json
import os
import random
import threading
import time
from pathlib import Path

import gpu_search_bounded as G
import bounded_caps as BC

UNIT = 50_000_000_000
ENUMERATION = "bounded-v1"
CACHE_AUDIT = 25           # shapes re-probed from scratch on every cache load


def atomic_json(path, value):
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, indent=2)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def load_boxes(source, n, rows, source_sha256, cache_dir):
    """Per-shape caps and DP tables, cached: the Hall probe costs ~0.2 s a shape.

    The cache is keyed by the manifest hash and n, so it can never be served for
    a manifest or a level it was not computed from.  Cached caps are re-checked
    against a freshly computed box for a sample of shapes on every load.
    """
    cache = Path(cache_dir) / f"caps-{n}-{source_sha256[:16]}.json"
    have = {}
    if cache.exists():
        raw = json.loads(cache.read_text(encoding="utf-8"))
        if raw.get("n") == n and raw.get("source_sha256") == source_sha256:
            have = {int(k): v for k, v in raw["hi"].items()}
    audit = set(random.Random(n).sample(range(len(rows)), min(CACHE_AUDIT, len(rows))))
    boxes = {}
    fresh = 0
    rechecked = 0
    for pos, row in enumerate(rows):
        chords = [tuple(c) for c in row["chords"]]
        idx = row["shape_index"]
        if idx in have and pos not in audit:
            box = BC.box_from_hi(n, row["b"], chords, row["lows"], have[idx])
        else:
            box = BC.shape_box(n, row["b"], chords, row["lows"])
            if idx in have:
                rechecked += 1
                if have[idx] != box["hi"]:
                    raise ValueError(f"cap cache disagrees with a fresh Hall probe "
                                     f"for shape {idx}: cached {have[idx]} probed {box['hi']}")
            else:
                fresh += 1
        if box["unrestricted_total"] != row["total"]:
            raise ValueError(f"manifest total disagreement for shape {idx}")
        boxes[idx] = box
    merged = dict(have)
    merged.update({i: b["hi"] for i, b in boxes.items()})
    atomic_json(cache, {"n": n, "source_sha256": source_sha256,
                        "hi": {str(k): v for k, v in merged.items()}})
    return boxes, fresh, rechecked


def build_units(rows, boxes):
    units = []
    for row in rows:
        box = boxes[row["shape_index"]]
        for offset in range(0, box["total"], UNIT):
            units.append({"shape_index": row["shape_index"], "b": row["b"],
                          "offset": offset, "count": min(UNIT, box["total"] - offset),
                          "bounded_total": box["total"], "unrestricted_total": row["total"]})
    return units


def plan_hash(n, units, boxes):
    h = hashlib.sha256()
    h.update(f"{ENUMERATION}\nn={n}\n".encode())
    for u in units:
        box = boxes[u["shape_index"]]
        h.update(json.dumps([u["shape_index"], u["b"], u["offset"], u["count"],
                             box["lows"], box["hi"], box["total"]],
                            separators=(",", ":")).encode())
        h.update(b"\n")
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path)
    p.add_argument("state", type=Path)
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--min-b", type=int, default=6)
    p.add_argument("--max-b", type=int, default=9)
    p.add_argument("--wall-budget", type=float, default=0.0)
    p.add_argument("--lock-stale", type=float, default=180.0)
    p.add_argument("--only-shapes", type=Path,
                   help="JSON list of shape_index to restrict the tier to; the "
                        "restriction is recorded in the state and hashed into "
                        "the plan, so a partial state cannot be mistaken for a "
                        "complete tier")
    args = p.parse_args()
    lock = args.state.with_suffix(args.state.suffix + ".lock")
    args.state.parent.mkdir(parents=True, exist_ok=True)
    heartbeat_stop = threading.Event()
    heartbeat_thread = None
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
    except FileExistsError:
        try:
            owner_pid = int(lock.read_text(encoding="utf-8"))
            os.kill(owner_pid, 0)
            print("LOCKED", flush=True)
            return 2
        except (ValueError, OSError, ProcessLookupError):
            pass
        if time.time() - lock.stat().st_mtime < args.lock_stale:
            print("LOCKED", flush=True)
            return 2
        lock.unlink()
        return main()
    try:
        def heartbeat():
            while not heartbeat_stop.wait(5.0):
                try:
                    os.utime(lock, None)
                except FileNotFoundError:
                    return
        heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
        heartbeat_thread.start()
        raw = (args.source / f"n{args.n}.jsonl").read_bytes()
        source_sha256 = hashlib.sha256(raw).hexdigest()
        rows = [json.loads(line) for line in raw.splitlines()]
        rows = [r for r in rows if args.min_b <= r["b"] <= args.max_b]
        subset = None
        if args.only_shapes:
            subset = sorted(json.loads(args.only_shapes.read_text(encoding="utf-8")))
            keep = set(subset)
            rows = [r for r in rows if r["shape_index"] in keep]
            if len(rows) != len(keep):
                raise ValueError("only-shapes names a shape absent from this tier")
        # Identity checks that do not need the caps run first: computing them
        # costs minutes on a large tier, and a refusal should not.
        prior = None
        if args.state.exists():
            prior = json.loads(args.state.read_text(encoding="utf-8"))
            if prior.get("enumeration") != ENUMERATION:
                raise ValueError(
                    "state file was not written by the bounded runner "
                    f"(enumeration={prior.get('enumeration')!r}); its completed units "
                    "index the unrestricted rank space and mean different work here")
            if prior["source_sha256"] != source_sha256 or prior["n"] != args.n:
                raise ValueError("state source or n mismatch")
        t_caps = time.monotonic()
        boxes, fresh, rechecked = load_boxes(args.source, args.n, rows, source_sha256,
                                             args.state.parent)
        caps_seconds = time.monotonic() - t_caps
        units = build_units(rows, boxes)
        digest = plan_hash(args.n, units, boxes)
        if subset is not None:
            digest = hashlib.sha256((digest + json.dumps(subset)).encode()).hexdigest()
        if prior is not None:
            state = prior
            if state.get("plan_sha256") != digest:
                raise ValueError("state plan_sha256 mismatch: the caps, the tier or the "
                                 "unit layout changed since this state was written")
        else:
            state = {"version": 1, "enumeration": ENUMERATION, "n": args.n,
                     "min_b": args.min_b, "max_b": args.max_b,
                     "source_sha256": source_sha256, "plan_sha256": digest,
                     "only_shapes": subset, "complete": [], "hits": []}
            atomic_json(args.state, state)
        state.pop("units", None)
        done = {tuple(x) for x in state["complete"]}
        by_shape = {r["shape_index"]: r for r in rows}
        engine = G.Engine(12, 70, 127)
        control = G.controls(engine)
        if control["positive_control"] != "PASS" or control["mismatches"] != 0:
            raise RuntimeError("POSITIVE CONTROL FAILED")
        if control["cap_soundness_on_witnesses"] != "PASS":
            raise RuntimeError("CAP SOUNDNESS CONTROL FAILED")
        start = time.monotonic()
        tested = 0
        gpu_seconds = 0.0
        for unit in units:
            key = (unit["shape_index"], unit["offset"], unit["count"])
            if key in done:
                continue
            if args.wall_budget and tested and time.monotonic() - start >= args.wall_budget:
                break
            box = boxes[unit["shape_index"]]
            found, elapsed, _ = engine.run(args.n, [box], [unit["offset"]], [1], unit["count"])
            gpu_seconds += elapsed
            for hit in found:
                hit["shape_index"] = unit["shape_index"]
                state["hits"].append(hit)
                print("VERIFIED SAT", json.dumps(hit), flush=True)
            state["complete"].append(list(key))
            atomic_json(args.state, state)
            tested += unit["count"]
            print(json.dumps({"complete_units": len(state["complete"]),
                              "total_units": len(units),
                              "tested_this_invocation": tested,
                              "gpu_seconds": elapsed}), flush=True)
        wall = time.monotonic() - start
        print(json.dumps({"complete_units": len(state["complete"]),
                          "total_units": len(units),
                          "exhausted": len(state["complete"]) == len(units),
                          "tested_this_invocation": tested,
                          "enumeration": ENUMERATION,
                          "shapes_in_tier": len(rows),
                          "bounded_ranks_in_tier": sum(b["total"] for b in boxes.values()),
                          "unrestricted_ranks_in_tier": sum(r["total"] for r in rows),
                          "caps_cpu_seconds": round(caps_seconds, 1),
                          "caps_computed_fresh": fresh,
                          "caps_cache_audited_against_fresh_probe": rechecked,
                          "scan_wall_seconds": round(wall, 1),
                          "gpu_seconds": round(gpu_seconds, 1),
                          "ranks_per_second": round(tested / gpu_seconds) if gpu_seconds else None,
                          "units_per_hour": round(tested / UNIT / (wall / 3600), 2)
                          if wall else None}), flush=True)
    finally:
        heartbeat_stop.set()
        if heartbeat_thread is not None:
            heartbeat_thread.join(timeout=1)
        try:
            lock.unlink()
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
