"""The exhaustion statement for one (n, b) tier after the pairwise cutover.

    unrestricted-exhausted shapes (per the unrestricted state file, re-derived
    from the gpu-blast manifest, never from the runner's own summary)
  + pairwise-exhausted shapes (per the pairwise state file, re-derived from the
    tier manifest with per-unit composition counts)
  = every gpu-blast shape of the tier, each covered by exactly one of the two.

Both state files are checked by the same rules verify_tier_exhaustion.py and
verify_tier_exhaustion_pairwise.py apply, restricted to their shape sets, and
the pairwise state's --only-shapes list must equal the complement of the
unrestricted-done set computed here (partition_tier.partition), not the list
some earlier tool wrote to disk.

Usage: python verify_tier_combined.py <source_dir> --n N --b B --unrestricted-state FILE --pairwise-state FILE [--tables DIR] [--rebuild K]
Exit 0 only on an exact tier-wide match with zero hits in either state.
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
import pairwise_tables as PT             # noqa: E402
import partition_tier as PART            # noqa: E402
import gpu_state_runner_pairwise as R    # noqa: E402

UNIT = PART.UNIT
UNIT_PREFIX = PT.UNIT_PREFIX


def main():
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path)
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--b", type=int, required=True)
    p.add_argument("--unrestricted-state", type=Path, default=None)
    p.add_argument("--pairwise-state", type=Path, required=True)
    p.add_argument("--tables", type=Path, default=HERE / "tables")
    p.add_argument("--rebuild", type=int, default=0)
    args = p.parse_args()
    errors = []
    raw = (args.source / f"n{args.n}.jsonl").read_bytes()
    source_sha256 = hashlib.sha256(raw).hexdigest()
    rows = {r["shape_index"]: r for r in (json.loads(l) for l in raw.splitlines()) if r["b"] == args.b}

    # ---- unrestricted side, re-derived
    part = PART.partition(args.source, args.unrestricted_state, args.n, args.b)
    done = set(part["done"])
    remaining = set(part["remaining"])
    u_ranks_done = 0
    if args.unrestricted_state and args.unrestricted_state.exists():
        st = json.loads(args.unrestricted_state.read_text(encoding="utf-8"))
        covered = {tuple(x) for x in st["complete"]}
        for idx in done:
            exp = PART.unrestricted_units(rows[idx])
            if not exp <= covered:
                errors.append(f"unrestricted shape {idx} classified done but units missing")
            u_ranks_done += rows[idx]["total"]
        if st.get("hits"):
            errors.append("unrestricted state has hits")

    # ---- pairwise side, re-derived
    ps = json.loads(args.pairwise_state.read_text(encoding="utf-8"))
    if ps.get("enumeration") != R.ENUMERATION:
        errors.append("pairwise state enumeration tag wrong")
    if ps.get("source_sha256") != source_sha256 or ps.get("n") != args.n or ps.get("b") != args.b:
        errors.append("pairwise state source/n/b mismatch")
    only = ps.get("only_shapes")
    if only is None:
        if remaining != set(rows):
            errors.append("pairwise state covers the whole tier but the unrestricted side also claims shapes")
        only_set = set(rows)
    else:
        only_set = set(int(x) for x in only)
        if only_set != remaining:
            errors.append(f"pairwise --only-shapes ({len(only_set)}) != complement of unrestricted-done ({len(remaining)})")
    mpath = args.tables / f"n{args.n}-b{args.b}" / "tier-manifest.json"
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    if manifest["source_sha256"] != source_sha256 or manifest.get("partial"):
        errors.append("tier manifest source mismatch or partial")
    mshapes = {int(k): v for k, v in manifest["shapes"].items()}
    if set(mshapes) != set(rows):
        errors.append("tier manifest shape set != gpu-blast tier")
    for idx, r in rows.items():
        if idx in mshapes and int(mshapes[idx]["unrestricted_total"]) != int(r["total"]):
            errors.append(f"unrestricted total mismatch in manifest for shape {idx}")
    if ps.get("unit_prefix") != int(manifest["unit_prefix"]):
        errors.append("pairwise state unit_prefix != manifest unit_prefix")
    # The state recorded the hash of the manifest file it planned from; the
    # file on disk must still be that file (review finding 3: reported but
    # never compared).
    mfile_sha = hashlib.sha256(mpath.read_bytes()).hexdigest()
    if ps.get("tier_manifest_sha256") != mfile_sha:
        errors.append("pairwise state tier_manifest_sha256 != hash of the tier manifest on disk")
    # This is the CLAIM tool: it accepts nothing less than a full rebuild of
    # every pairwise shape's tables from the gpu-blast row (review finding 1).
    if args.rebuild != -1:
        errors.append("the combined claim requires --rebuild -1 (every pairwise shape rebuilt from source)")
    units = R.build_units(manifest, only_set)
    digest = R.plan_hash(args.n, args.b, manifest, source_sha256, units, sorted(only_set) if only is not None else None)
    if ps.get("plan_sha256") != digest:
        errors.append("pairwise plan_sha256 != plan recomputed from the tier manifest and the derived shape set")
    expected = {(u["shape_index"], u["offset"], u["count"]) for u in units}
    covered_p = {}
    for e in ps["complete"]:
        key = tuple(int(x) for x in e[:3])
        if key in covered_p:
            errors.append(f"duplicate pairwise unit {key}")
        covered_p[key] = int(e[3]) if len(e) > 3 else None
    missing = expected - set(covered_p)
    extra = set(covered_p) - expected
    per_shape = {}
    for key, c in covered_p.items():
        if key in expected and c is not None:
            per_shape[key[0]] = per_shape.get(key[0], 0) + c
    comp_bad = [idx for idx in only_set if int(mshapes[idx]["total_prefixes"]) > 0
                and per_shape.get(idx, -1) != int(mshapes[idx]["total_compositions"])]
    p_total = sum(int(mshapes[i]["total_compositions"]) for i in only_set)
    if ps.get("hits"):
        errors.append("pairwise state has hits")
    # Every pairwise shape's npz must describe its gpu-blast row at this n
    # (review finding D2), and --rebuild -1 rebuilds every one of them from the
    # source and requires hash and total equality (review finding D1).
    header_bad = []
    for idx in sorted(only_set):
        f = args.tables / f"n{args.n}-b{args.b}" / f"shape-{idx}.npz"
        try:
            tab = PT.load(f, expected_sha256=mshapes[idx]["tables_sha256"])
        except Exception as exc:
            header_bad.append(f"{idx}:{exc!r}")
            continue
        r = rows[idx]
        if (tab["n"] != args.n or tab["b"] != r["b"] or [list(c) for c in tab["chords"]] != [list(c) for c in r["chords"]]
                or list(tab["lows"]) != list(r["lows"]) or tab["total_prefixes"] != int(mshapes[idx]["total_prefixes"])
                or tab["total_compositions"] != int(mshapes[idx]["total_compositions"])):
            header_bad.append(str(idx))
    if header_bad:
        errors.append(f"{len(header_bad)} shape table files do not describe their gpu-blast shape: {header_bad[:5]}")
    rebuilt = []
    rebuilt_count = rebuilt_bad = 0
    if args.rebuild:
        picked = sorted(only_set) if args.rebuild < 0 else \
            random.Random(args.n * 1000 + args.b).sample(sorted(only_set), min(args.rebuild, len(only_set)))
        for idx in picked:
            r = rows[idx]
            tab = PT.build(args.n, r["b"], r["chords"], r["lows"], shape_index=idx)
            ok = (tab["tables_sha256"] == mshapes[idx]["tables_sha256"]
                  and tab["total_prefixes"] == int(mshapes[idx]["total_prefixes"])
                  and tab["total_compositions"] == int(mshapes[idx]["total_compositions"]))
            rebuilt_count += 1
            rebuilt_bad += int(not ok)
            if not ok or len(picked) <= 50:
                rebuilt.append({"shape_index": idx, "match": ok})
            if not ok:
                errors.append(f"rebuilt tables disagree for shape {idx}")

    union_ok = (done | remaining) == set(rows) and not (done & remaining)
    out = dict(n=args.n, b=args.b, source_sha256=source_sha256, shapes=len(rows),
               unrestricted_done_shapes=len(done), unrestricted_ranks_done=u_ranks_done,
               pairwise_shapes=len(only_set), pairwise_expected_units=len(expected),
               pairwise_covered_units=len(covered_p), pairwise_missing=len(missing), pairwise_extra=len(extra),
               pairwise_compositions_manifest=p_total, pairwise_compositions_counted=sum(per_shape.values()),
               composition_mismatch_shapes=comp_bad[:10], union_covers_tier=union_ok,
               hits=(ps.get("hits") or []), rebuilt=rebuilt, rebuilt_count=rebuilt_count,
               rebuilt_mismatches=rebuilt_bad, rebuild_covers_every_pairwise_shape=rebuilt_count == len(only_set),
               errors=errors)
    out["exact_match"] = union_ok and not errors and not missing and not extra and not comp_bad \
        and sum(per_shape.values()) == p_total
    print(json.dumps(out, indent=1))
    return 0 if out["exact_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
