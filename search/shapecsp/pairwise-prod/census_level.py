"""Write the eligible-shape manifest n{N}.jsonl for one level N, in the exact
format of search/shapecsp/gpu-blast/n68.jsonl, so the pairwise pipeline can run
levels other than 68, 69, 70.

Eligibility is gpu_search.py's, verbatim: len(forms) + 2 >= n, sum(lows) <= n,
and bound.hall_ok(iv, n).  shape_index is the position in shapes.shapes(6),
which is what every existing manifest uses.  The affine-permutation fields
(start, step, count) are not used by the pairwise plan and are written as
0/1/0 so the row shape matches.

Self-check: --check reproduces an existing manifest's (shape_index, b, chords,
lows, total) rows exactly (the census is deterministic and the eligibility rule
must not drift).

Usage: python census_level.py --n 71 --out gpu-blast-ext
       python census_level.py --check ../gpu-blast/n68.jsonl
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pickle
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROD = HERE.parent
if str(PROD) not in sys.path:
    sys.path.insert(0, str(PROD))
import shapes as S    # noqa: E402
import bound as B     # noqa: E402

CACHE = HERE / "shapes-k6-forms.pkl"


def all_shapes():
    """(b, chords, forms, lows, iv) for every k=6 shape, cached on disk."""
    if CACHE.exists():
        return pickle.loads(CACHE.read_bytes())
    data = []
    for b, ch in S.shapes(6):
        forms = sorted(set(S.cycle_forms(b, ch)))
        iv, lows = B.intervals(b, ch, forms)
        data.append((b, [list(c) for c in ch], forms, lows, iv))
    CACHE.write_bytes(pickle.dumps(data))
    return data


def rows_for(n, data):
    out = []
    for i, (b, ch, forms, lows, iv) in enumerate(data):
        if len(forms) + 2 >= n and sum(lows) <= n and B.hall_ok(iv, n):
            total = math.comb(n - sum(lows) + b - 1, b - 1)
            out.append(dict(shape_index=i, b=b, chords=ch, lows=lows, total=total, start=0, step=1, count=0))
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--n", type=int)
    p.add_argument("--out", type=Path, default=HERE / "gpu-blast-ext")
    p.add_argument("--check", type=Path, help="existing manifest to reproduce")
    args = p.parse_args()
    t0 = time.perf_counter()
    data = all_shapes()
    print(json.dumps({"shapes": len(data), "max_b": max(d[0] for d in data), "seconds": round(time.perf_counter() - t0, 1)}))
    if args.check:
        n = int(args.check.stem[1:])
        have = [json.loads(l) for l in args.check.read_text(encoding="utf-8").splitlines()]
        mine = rows_for(n, data)
        key = lambda r: (r["shape_index"], r["b"], [list(c) for c in r["chords"]], list(r["lows"]), r["total"])
        same = [key(r) for r in have] == [key(r) for r in mine]
        print(json.dumps({"check": str(args.check), "n": n, "rows_existing": len(have), "rows_census": len(mine), "identical": same}))
        return 0 if same else 1
    n = args.n
    rows = rows_for(n, data)
    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / f"n{n}.jsonl"
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    by_b = {}
    for r in rows:
        by_b[r["b"]] = by_b.get(r["b"], 0) + 1
    print(json.dumps({"n": n, "eligible": len(rows), "by_b": by_b, "path": str(path),
                      "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                      "unrestricted_ranks": sum(r["total"] for r in rows)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
