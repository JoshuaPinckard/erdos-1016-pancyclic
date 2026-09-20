"""Integrity and cross-machine determinism of built table sets.

  integrity <dir>       every shape-*.npz under <dir>/n*-b*/ loads, its hash
                        recomputed from the arrays equals the tier manifest's
                        tables_sha256, and its totals match the manifest.
  compare <dirA> <dirB> tier manifests present in both: every common shape has
                        the same tables_sha256, total_prefixes and
                        total_compositions (the builds were on two machines).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import pairwise_tables as PT   # noqa: E402


def integrity(root):
    out = {}
    for tdir in sorted(Path(root).glob("n*-b*")):
        mp = tdir / "tier-manifest.json"
        if not mp.exists():
            out[tdir.name] = "no manifest"
            continue
        m = json.loads(mp.read_text(encoding="utf-8"))
        bad, checked, missing = [], 0, 0
        for idx, meta in m["shapes"].items():
            f = tdir / f"shape-{idx}.npz"
            if not f.exists():
                missing += 1
                continue
            try:
                tab = PT.load(f, expected_sha256=meta["tables_sha256"])
                if tab["total_prefixes"] != meta["total_prefixes"] or tab["total_compositions"] != meta["total_compositions"] \
                        or tab["shape_index"] != int(idx) if tab.get("shape_index") is not None else False:
                    bad.append(idx)
            except Exception as exc:
                bad.append(f"{idx}:{exc!r}")
            checked += 1
        out[tdir.name] = dict(shapes=len(m["shapes"]), checked=checked, missing=missing, bad=bad[:5], bad_count=len(bad),
                              tier_total_compositions=m["tier_total_compositions"])
    print(json.dumps(out, indent=1))
    return all(isinstance(v, dict) and v["bad_count"] == 0 and v["missing"] == 0 for v in out.values())


def compare(a, b):
    out = {}
    for ta in sorted(Path(a).glob("n*-b*")):
        tb = Path(b) / ta.name
        ma, mb = ta / "tier-manifest.json", tb / "tier-manifest.json"
        if not (ma.exists() and mb.exists()):
            out[ta.name] = "manifest missing on one side"
            continue
        A = json.loads(ma.read_text(encoding="utf-8"))["shapes"]
        B = json.loads(mb.read_text(encoding="utf-8"))["shapes"]
        common = sorted(set(A) & set(B), key=int)
        diff = [i for i in common if (A[i]["tables_sha256"], A[i]["total_prefixes"], A[i]["total_compositions"])
                != (B[i]["tables_sha256"], B[i]["total_prefixes"], B[i]["total_compositions"])]
        out[ta.name] = dict(shapes_a=len(A), shapes_b=len(B), common=len(common), differing=len(diff), differing_sample=diff[:5])
    print(json.dumps(out, indent=1))
    return all(isinstance(v, dict) and v["differing"] == 0 for v in out.values())


def compare_partial(built_dir, manifest_dir):
    """Shapes built so far on this machine (no manifest yet) against another
    machine's finished manifest: recompute each file's hash and compare."""
    out = {}
    for tdir in sorted(Path(built_dir).glob("n*-b*")):
        mp = Path(manifest_dir) / tdir.name / "tier-manifest.json"
        if not mp.exists():
            continue
        M = json.loads(mp.read_text(encoding="utf-8"))["shapes"]
        files = sorted(tdir.glob("shape-*.npz"))
        diff, checked = [], 0
        for f in files:
            idx = f.stem.split("-")[1]
            try:
                tab = PT.load(f)
            except Exception as exc:
                diff.append(f"{idx}:{exc!r}")
                continue
            checked += 1
            if idx not in M or tab["tables_sha256"] != M[idx]["tables_sha256"] or tab["total_compositions"] != M[idx]["total_compositions"]:
                diff.append(idx)
        out[tdir.name] = dict(files=len(files), checked=checked, differing=len(diff), sample=diff[:5])
    print(json.dumps(out, indent=1))
    return all(v["differing"] == 0 for v in out.values())


if __name__ == "__main__":
    cmd = sys.argv[1]
    ok = {"integrity": lambda: integrity(sys.argv[2]),
          "compare": lambda: compare(sys.argv[2], sys.argv[3]),
          "compare-partial": lambda: compare_partial(sys.argv[2], sys.argv[3])}[cmd]()
    raise SystemExit(0 if ok else 1)
