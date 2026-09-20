"""Render papers/verification/*.json (claim files) into markdown tables plus a
one-line verdict per level, so the exhaustion report quotes the claim files
rather than a person's summary of them.

Two kinds of claim file:
  n{N}-b{B}-unrestricted.json   search/shapecsp/verify_tier_exhaustion.py on the
                                unrestricted plan's state (tiers below the
                                cutover b): unit set re-derived from the census
                                manifest, rank totals compared.
  n{N}-b{B}-combined.json       pairwise-prod/verify_tier_combined.py --rebuild -1
                                on the cutover tiers: unrestricted-done shapes
                                re-derived, pairwise units and compositions
                                re-derived, every pairwise shape's tables rebuilt
                                from source and hash-compared.

Usage: python render_claims.py [--dir papers/verification] [--levels 68,69,70]
A level is stated EXHAUSTED only when every b of that level in the gpu-blast
manifest has its claim file with exact_match true and zero hits (and, for the
pairwise tiers, a full source rebuild with zero mismatches); anything less is
printed as INCOMPLETE with the reason.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SC = HERE.parent
REPO = SC.parent.parent


def load(d, suffix):
    out = {}
    for f in sorted(Path(d).glob(f"n*-b*-{suffix}.json")):
        try:
            j = json.loads(f.read_text(encoding="utf-8"))
        except Exception as exc:
            out[f.name] = {"error": repr(exc)}
            continue
        if "n" in j and "b" in j:
            out[(int(j["n"]), int(j["b"]))] = dict(j, _file=f.name)
    return out


def tiers_of_level(n, source_dir):
    raw = (Path(source_dir) / f"n{n}.jsonl").read_text(encoding="utf-8").splitlines()
    return sorted({json.loads(l)["b"] for l in raw})


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dir", type=Path, default=REPO / "papers" / "verification")
    p.add_argument("--source", type=Path, default=SC / "gpu-blast")
    p.add_argument("--levels", default="68,69,70")
    p.add_argument("--exhausted-b-below", type=int, default=11,
                   help="b values below this were exhausted by the unrestricted plan before the cutover")
    args = p.parse_args()
    levels = [int(x) for x in args.levels.split(",")]
    unres = load(args.dir, "unrestricted")
    claims = load(args.dir, "combined")
    reasons = {n: [] for n in levels}

    print("Unrestricted plan (b below the cutover), unit set re-derived from the census manifest:")
    print()
    print("| tier | units | ranks covered = manifest | hits | exact_match | claim file |")
    print("|---|---|---|---|---|---|")
    for n in levels:
        for b in tiers_of_level(n, args.source):
            if b >= args.exhausted_b_below:
                continue
            j = unres.get((n, b))
            if j is None:
                reasons[n].append(f"b={b}: no unrestricted claim file")
                continue
            if not (j.get("exact_match") and j.get("rank_totals_match") and not j.get("hits")):
                reasons[n].append(f"b={b}: exact_match={j.get('exact_match')} hits={len(j.get('hits') or [])}")
            print(f"| n={n} b={b} | {j['covered_unit_count']} of {j['expected_unit_count']} | {j['covered_rank_total']:,}"
                  f"{' = manifest' if j['rank_totals_match'] else ' MISMATCH'} | {len(j.get('hits') or [])} | {j['exact_match']} | {j['_file']} |")
    print()
    print("Pairwise plan (cutover tiers), claim tool verify_tier_combined.py --rebuild -1:")
    print()
    print("| tier | shapes | unrestricted-done shapes | pairwise shapes | pairwise units | compositions (manifest = counted) | rebuilt shapes | mismatches | hits | exact_match | claim file |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for n in levels:
        for b in tiers_of_level(n, args.source):
            if b < args.exhausted_b_below:
                continue
            c = claims.get((n, b))
            if c is None:
                reasons[n].append(f"b={b}: no claim file")
                continue
            full = (bool(c.get("exact_match")) and not c.get("hits") and bool(c.get("rebuild_covers_every_pairwise_shape"))
                    and int(c.get("rebuilt_mismatches", 1)) == 0)
            if not full:
                reasons[n].append(f"b={b}: exact_match={c.get('exact_match')} hits={len(c.get('hits') or [])} "
                                  f"rebuild_full={c.get('rebuild_covers_every_pairwise_shape')} mismatches={c.get('rebuilt_mismatches')} errors={c.get('errors')}")
            same = c.get("pairwise_compositions_manifest") == c.get("pairwise_compositions_counted")
            print(f"| n={n} b={b} | {c.get('shapes')} | {c.get('unrestricted_done_shapes')} | {c.get('pairwise_shapes')} | "
                  f"{c.get('pairwise_covered_units')} of {c.get('pairwise_expected_units')} | {c.get('pairwise_compositions_manifest'):,}"
                  f"{' = counted' if same else ' != counted ' + str(c.get('pairwise_compositions_counted'))} | {c.get('rebuilt_count')} | "
                  f"{c.get('rebuilt_mismatches')} | {len(c.get('hits') or [])} | {c.get('exact_match')} | {c['_file']} |")
    print()
    for n in levels:
        if not reasons[n]:
            print(f"* n = {n}: EXHAUSTED. Every tier of the gpu-blast census manifest is covered: b < {args.exhausted_b_below} by the "
                  f"unrestricted plan (unit sets re-derived, rank totals equal), b >= {args.exhausted_b_below} by the pairwise plan "
                  f"(every pairwise shape's tables rebuilt from its gpu-blast row with matching hashes, unrestricted-done shapes "
                  f"re-derived from the unrestricted state). Zero hits in every tier.")
        else:
            print(f"* n = {n}: INCOMPLETE -- " + "; ".join(reasons[n]))


if __name__ == "__main__":
    main()
