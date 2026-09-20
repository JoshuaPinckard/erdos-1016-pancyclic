"""Blind positive control: judge one control-state-n{N}-b{B}.json.

A control run applies the production pairwise plan to a level that is KNOWN to
contain 6-chord pancyclic witnesses (level 67 by default).  The run passes when

  * every unit of the tier plan (re-derived from the tier manifest) is covered,
    with nothing extra, and the state was planned from the census file on disk;
  * every hit re-verifies under search/verify.py here, independently of the
    runner's own verification;
  * the family witness of this level, if its shape has this b, is among the
    hits of its own shape with exactly its arc vector.

Exit 0 = complete and passed, 2 = not started or incomplete, 1 = complete but
failed.  Reads only state, manifest and census files; the frozen production
modules under ../pairwise-prod supply the unit plan and the witness canonical
form.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SC = HERE.parent
for p in (str(SC / "pairwise-prod"), str(SC)):
    if p not in sys.path:
        sys.path.insert(0, p)
import gpu_state_runner_pairwise as R    # noqa: E402  (frozen)
import gpu_search_pairwise as G          # noqa: E402  (frozen)

FAMILY = {67: [(0, 2), (0, 60), (1, 13), (3, 61), (4, 31), (59, 62)]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--n", type=int, default=67)
    p.add_argument("--b", type=int, required=True)
    p.add_argument("--source", type=Path, default=HERE / "gpu-blast-ext")
    p.add_argument("--tables", type=Path, default=HERE / "tables-ext")
    p.add_argument("--state", type=Path, default=None)
    args = p.parse_args()
    state_path = args.state or HERE / f"control-state-n{args.n}-b{args.b}.json"
    out = dict(n=args.n, b=args.b, state=str(state_path))
    if not state_path.exists():
        out["status"] = "not-started"
        print(json.dumps(out, indent=1))
        return 2
    st = json.loads(state_path.read_text(encoding="utf-8"))
    mpath = args.tables / f"n{args.n}-b{args.b}" / "tier-manifest.json"
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    raw = (args.source / f"n{args.n}.jsonl").read_bytes()
    rows_b = {r["shape_index"]: r for r in (json.loads(l) for l in raw.splitlines()) if r["b"] == args.b}
    only = st.get("only_shapes")
    units = R.build_units(manifest, set(int(x) for x in only) if only is not None else None)
    expected = {(u["shape_index"], u["offset"], u["count"]) for u in units}
    covered = {tuple(int(x) for x in e[:3]) for e in st["complete"]}
    missing, extra = expected - covered, covered - expected
    out.update(enumeration_ok=(st.get("enumeration") == R.ENUMERATION),
               source_sha256_matches=(st.get("source_sha256") == hashlib.sha256(raw).hexdigest()),
               tier_manifest_sha256_matches=(st.get("tier_manifest_sha256") == hashlib.sha256(mpath.read_bytes()).hexdigest()),
               shapes=len(rows_b), expected_units=len(expected), covered_units=len(covered),
               missing_units=len(missing), extra_units=len(extra))
    hits = st.get("hits") or []
    failing = [h for h in hits if not G.V.pancyclic(args.n, [tuple(c) for c in h["chords"]])]
    out.update(hits=len(hits), hit_shapes=len({h.get("shape_index") for h in hits}),
               hits_failing_independent_verifier=len(failing))
    fam = FAMILY.get(args.n)
    if fam is not None:
        fb, canonical, a = G.canonical_witness(args.n, fam)
        out["family_witness_b"] = fb
        if fb == args.b:
            idx = [i for i, r in rows_b.items() if [list(c) for c in r["chords"]] == canonical]
            want = sorted(tuple(c) for c in G.materialise(canonical, a))
            found = [h for h in hits if list(h["arcs"]) == list(a)
                     and (h.get("shape_index") in idx if h.get("shape_index") is not None
                          else sorted(tuple(c) for c in h["chords"]) == want)]
            out.update(family_witness_shape_index=idx, family_witness_arcs=a, family_witness_found=bool(found))
    complete = (not missing and not extra and out["source_sha256_matches"]
                and out["tier_manifest_sha256_matches"] and out["enumeration_ok"])
    passed = complete and not failing and out.get("family_witness_found", True)
    out["complete"] = complete
    out["status"] = "passed" if passed else ("failed" if complete else "incomplete")
    print(json.dumps(out, indent=1))
    return 0 if passed else (1 if complete else 2)


if __name__ == "__main__":
    raise SystemExit(main())
