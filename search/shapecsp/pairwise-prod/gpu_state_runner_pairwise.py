"""Restartable bounded-unit exhaustive GPU runner over the PAIRWISE-ADMISSIBLE
composition space of one (level, tier).

Contract, same as gpu_state_runner.py: claim at most --wall-budget seconds
(0 = run to completion), record completion atomically after every unit, exit 2
when another instance holds the state lock.  Differences that callers must
understand:

  * a unit is (shape_index, prefix_offset, prefix_count) over PREFIX RANKS of
    the pairwise tables, not over unrestricted composition ranks;
  * every completed unit records the number of compositions the kernel
    actually visited, so a tier's per-shape sum can be checked against the
    tier manifest's total_compositions by verify_tier_exhaustion_pairwise.py;
  * the state carries enumeration = "pairwise-v1" and plan_sha256 over the
    manifest hash, every shape's tables hash, UNIT_PREFIX and the unit layout.
    A state file without that tag, or with a different plan hash, is refused
    outright: the failure mode is a refusal to run, never a quietly reduced
    search.

Tables come from <tables>/n{N}-b{B}/shape-{idx}.npz built by pairwise_tables.py
build-tier, whose tier-manifest.json is the plan's source of truth.  Each file's
hash is re-derived from its arrays on load and must match the manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROD = HERE.parent
for p in (str(HERE), str(PROD)):
    if p not in sys.path:
        sys.path.insert(0, p)
import pairwise_tables as PT            # noqa: E402
import gpu_search_pairwise as G         # noqa: E402

ENUMERATION = "pairwise-v1"
# The unit size (prefix ranks per unit) is taken from the tier manifest's
# unit_prefix at run time and hashed into the plan; see load_manifest.


def atomic_json(path, value):
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, indent=1)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def pid_alive(pid):
    try:
        import psutil
        return psutil.pid_exists(pid)
    except Exception:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


def load_manifest(tables_dir, n, b):
    path = Path(tables_dir) / f"n{n}-b{b}" / "tier-manifest.json"
    m = json.loads(path.read_text(encoding="utf-8"))
    if m["format"] != PT.FORMAT or m["n"] != n or m["b"] != b:
        raise ValueError("tier manifest does not describe this tier")
    unit = int(m["unit_prefix"])
    if not (1 << 20) <= unit <= (1 << 40):
        raise ValueError(f"tier manifest unit_prefix {unit} is outside the sane range")
    return path, m


def build_units(manifest, subset=None):
    unit = int(manifest["unit_prefix"])
    units = []
    for idx_s, meta in sorted(manifest["shapes"].items(), key=lambda kv: int(kv[0])):
        idx = int(idx_s)
        if subset is not None and idx not in subset:
            continue
        total = int(meta["total_prefixes"])
        for offset in range(0, total, unit):
            units.append({"shape_index": idx, "offset": offset, "count": min(unit, total - offset),
                          "total_prefixes": total, "tables_sha256": meta["tables_sha256"]})
    return units


def plan_hash(n, b, manifest, source_sha256, units, subset):
    h = hashlib.sha256()
    h.update(f"{ENUMERATION}\nn={n}\nb={b}\nunit={int(manifest['unit_prefix'])}\nsource={source_sha256}\n".encode())
    for u in units:
        h.update(json.dumps([u["shape_index"], u["offset"], u["count"], u["total_prefixes"], u["tables_sha256"]],
                            separators=(",", ":")).encode())
        h.update(b"\n")
    if subset is not None:
        h.update(("subset=" + json.dumps(sorted(subset))).encode())
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path, help="gpu-blast manifest directory (n{N}.jsonl)")
    p.add_argument("state", type=Path)
    p.add_argument("--tables", type=Path, default=HERE / "tables")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--b", type=int, required=True)
    p.add_argument("--wall-budget", type=float, default=0.0)
    p.add_argument("--lock-stale", type=float, default=180.0)
    p.add_argument("--only-shapes", type=Path,
                   help="JSON list of shape_index to restrict the tier to; recorded in the state and "
                        "hashed into the plan, so a partial state cannot pass for a complete tier")
    p.add_argument("--skip-controls", action="store_true", help="tests only; production always runs them")
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
            if pid_alive(owner_pid):
                print("LOCKED", flush=True)
                return 2
        except ValueError:
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
        tier_rows = [json.loads(l) for l in raw.splitlines()]
        tier_rows = [r for r in tier_rows if r["b"] == args.b]
        manifest_path, manifest = load_manifest(args.tables, args.n, args.b)
        if manifest["source_sha256"] != source_sha256:
            raise ValueError("tier manifest was built from a different gpu-blast manifest")
        if manifest.get("partial"):
            raise ValueError("tier manifest is partial (built with --shapes); refusing to run a tier from it")
        manifest_shapes = {int(k) for k in manifest["shapes"]}
        tier_shapes = {r["shape_index"] for r in tier_rows}
        if manifest_shapes != tier_shapes:
            raise ValueError(f"tier manifest covers {len(manifest_shapes)} shapes, gpu-blast tier has {len(tier_shapes)}")
        for r in tier_rows:
            if int(manifest["shapes"][str(r["shape_index"])]["unrestricted_total"]) != int(r["total"]):
                raise ValueError(f"unrestricted total disagreement for shape {r['shape_index']}")
        subset = None
        if args.only_shapes:
            subset = sorted(json.loads(args.only_shapes.read_text(encoding="utf-8")))
            if not set(subset) <= manifest_shapes:
                raise ValueError("only-shapes names a shape absent from this tier")
        units = build_units(manifest, set(subset) if subset is not None else None)
        digest = plan_hash(args.n, args.b, manifest, source_sha256, units, subset)
        manifest_sha256 = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        if args.state.exists():
            state = json.loads(args.state.read_text(encoding="utf-8"))
            if state.get("enumeration") != ENUMERATION:
                raise ValueError(f"state file enumeration is {state.get('enumeration')!r}, not {ENUMERATION!r}; "
                                 "its completed units mean different work here")
            if state["source_sha256"] != source_sha256 or state["n"] != args.n or state["b"] != args.b:
                raise ValueError("state source, n or b mismatch")
            if state.get("plan_sha256") != digest:
                raise ValueError("state plan_sha256 mismatch: the tables, the tier or the unit layout changed "
                                 "since this state was written")
        else:
            state = {"version": 1, "enumeration": ENUMERATION, "n": args.n, "b": args.b,
                     "unit_prefix": int(manifest["unit_prefix"]), "source_sha256": source_sha256,
                     "tier_manifest_sha256": manifest_sha256, "plan_sha256": digest,
                     "only_shapes": subset, "complete": [], "hits": []}
            atomic_json(args.state, state)
        done = {tuple(x[:3]) for x in state["complete"]}
        by_shape = {r["shape_index"]: r for r in tier_rows}
        # max_n is a bookkeeping bound only (MAX_N never reaches the CUDA source;
        # MAX_B, MAX_V, MAX_F are unchanged, so the compiled kernel is identical);
        # the default 70 refused every level-71+ table with "tables exceed engine
        # capacity" (laptop chain v9, 21:58 on 2026-09-19).  Size it by the level.
        engine = G.Engine(max_n=max(70, args.n))
        if not args.skip_controls:
            control = G.controls(engine)
            if control["positive_control"] != "PASS" or control["mismatches"] != 0:
                raise RuntimeError("POSITIVE CONTROL FAILED")
        start = time.monotonic()
        tested = 0
        gpu_seconds = 0.0
        comps_total = 0
        current = None
        current_idx = None
        for unit in units:
            key = (unit["shape_index"], unit["offset"], unit["count"])
            if key in done:
                continue
            if args.wall_budget and tested and time.monotonic() - start >= args.wall_budget:
                break
            if current is None or current_idx != unit["shape_index"]:
                path = args.tables / f"n{args.n}-b{args.b}" / f"shape-{unit['shape_index']}.npz"
                current = PT.load(path, expected_sha256=unit["tables_sha256"])
                current_idx = unit["shape_index"]
                if current["total_prefixes"] != unit["total_prefixes"]:
                    raise ValueError("tables total_prefixes disagrees with the manifest")
                # The tables must describe THIS shape at THIS level.  A manifest
                # and npz that agree with each other but were built for another
                # shape or another n would pass the hash check (review finding
                # D2, 2026-09-19); the gpu-blast row is the ground truth here.
                row = by_shape[unit["shape_index"]]
                if (current["n"] != args.n or current["b"] != row["b"]
                        or [list(c) for c in current["chords"]] != [list(c) for c in row["chords"]]
                        or list(current["lows"]) != list(row["lows"])):
                    raise ValueError(f"tables for shape {unit['shape_index']} do not describe the gpu-blast "
                                     f"shape at n={args.n} (n={current['n']} b={current['b']} chords={current['chords']})")
            if current["total_prefixes"] == 0:
                continue
            found, elapsed, comps, _ = engine.run(current, unit["offset"], unit["count"])
            gpu_seconds += elapsed
            comps_total += comps
            for hit in found:
                hit["shape_index"] = unit["shape_index"]
                state["hits"].append(hit)
                print("VERIFIED SAT", json.dumps(hit), flush=True)
            state["complete"].append([unit["shape_index"], unit["offset"], unit["count"], comps])
            atomic_json(args.state, state)
            tested += unit["count"]
            print(json.dumps({"complete_units": len(state["complete"]), "total_units": len(units),
                              "shape_index": unit["shape_index"], "prefixes": unit["count"],
                              "compositions": comps, "gpu_seconds": round(elapsed, 3),
                              "tested_this_invocation": tested}), flush=True)
        wall = time.monotonic() - start
        print(json.dumps({"complete_units": len(state["complete"]), "total_units": len(units),
                          "exhausted": len(state["complete"]) == len(units),
                          "enumeration": ENUMERATION, "prefixes_this_invocation": tested,
                          "compositions_this_invocation": comps_total,
                          "gpu_seconds": round(gpu_seconds, 1), "wall_seconds": round(wall, 1),
                          "compositions_per_gpu_second": round(comps_total / gpu_seconds) if gpu_seconds else None,
                          "hits": len(state["hits"])}), flush=True)
    finally:
        heartbeat_stop.set()
        if heartbeat_thread is not None:
            heartbeat_thread.join(timeout=1)
        try:
            lock.unlink()
        except FileNotFoundError:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
