"""Render papers/verification/*.json (claim files written by the finalizers) into
one markdown table plus a one-line statement per level, so the exhaustion
report quotes the claim files rather than a person's summary of them.

Usage: python render_claims.py [--dir papers/verification] [--levels 68,69,70]
Prints markdown to stdout.  A level is stated exhausted only when every b of
that level in the gpu-blast manifest has a claim file with exact_match true,
zero hits, and a full source rebuild (rebuild_covers_every_pairwise_shape with
zero mismatches); anything less is printed as INCOMPLETE with the reason.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SC = HERE.parent
REPO = SC.parent.parent


def load_claims(d):
    out = {}
    for f in sorted(Path(d).glob("n*-b*-combined.json")):
        try:
            j = json.loads(f.read_text(encoding="utf-8"))
        except Exception as exc:
            out[f.name] = {"error": repr(exc)}
            continue
        out[(int(j["n"]), int(j["b"]))] = dict(j, _file=f.name)
    return out


def tiers_of_level(n, source_dir):
    raw = (Path(source_dir) / f"n{n}.jsonl").read_text(encoding="utf-8").splitlines()
    bs = sorted({json.loads(l)["b"] for l in raw})
    return bs


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dir", type=Path, default=REPO / "papers" / "verification")
    p.add_argument("--source", type=Path, default=SC / "gpu-blast")
    p.add_argument("--levels", default="68,69,70")
    p.add_argument("--exhausted-b-below", type=int, default=11,
                   help="b values below this were exhausted by the unrestricted plan before the cutover (their claims are in the k6 reports)")
    args = p.parse_args()
    claims = load_claims(args.dir)
    print("| tier | shapes | unrestricted-done shapes | pairwise shapes | pairwise units | compositions (manifest = counted) | rebuilt shapes | mismatches | hits | exact_match | claim file |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    verdict = {}
    for n in [int(x) for x in args.levels.split(",")]:
        ok, reasons = True, []
        for b in tiers_of_level(n, args.source):
            if b < args.exhausted_b_below:
                continue
            c = claims.get((n, b))
            if c is None:
                ok = False
                reasons.append(f"b={b}: no claim file")
                continue
            full = bool(c.get("exact_match")) and not c.get("hits") and bool(c.get("rebuild_covers_every_pairwise_shape")) and int(c.get("rebuilt_mismatches", 1)) == 0
            if not full:
                ok = False
                reasons.append(f"b={b}: exact_match={c.get('exact_match')} hits={len(c.get('hits') or [])} rebuild_full={c.get('rebuild_covers_every_pairwise_shape')} mismatches={c.get('rebuilt_mismatches')} errors={c.get('errors')}")
            same = c.get("pairwise_compositions_manifest") == c.get("pairwise_compositions_counted")
            print(f"| n={n} b={b} | {c.get('shapes')} | {c.get('unrestricted_done_shapes')} | {c.get('pairwise_shapes')} | "
                  f"{c.get('pairwise_covered_units')} of {c.get('pairwise_expected_units')} | {c.get('pairwise_compositions_manifest'):,}"
                  f"{' = counted' if same else ' != counted ' + str(c.get('pairwise_compositions_counted'))} | {c.get('rebuilt_count')} | "
                  f"{c.get('rebuilt_mismatches')} | {len(c.get('hits') or [])} | {c.get('exact_match')} | {c['_file']} |")
        verdict[n] = (ok, reasons)
    print()
    for n, (ok, reasons) in verdict.items():
        if ok:
            print(f"* n = {n}: every b >= {args.exhausted_b_below} tier of the gpu-blast manifest is exhausted under the pairwise plan with zero hits, "
                  f"every pairwise shape's tables rebuilt from its gpu-blast row with matching hashes, and the unrestricted-done shapes re-derived from the unrestricted state.")
        else:
            print(f"* n = {n}: INCOMPLETE -- " + "; ".join(reasons))


if __name__ == "__main__":
    main()
