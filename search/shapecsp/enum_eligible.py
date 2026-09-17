"""Verifier re-enumeration: replicate hunt.py's eligible-shape filter and order for
a cutoff, without launching bb, and print one line per eligible index:
    <idx> cap=<cap> b=<b> nforms=<n>
Usage: python enum_eligible.py <repo_dir> <k> <cutoff> [--nocache]
"""
import os, pickle, sys
repo, k, cutoff = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
sys.path.insert(0, repo)
import shapes as S, bound as B
cache = os.path.join(repo, f"forms-k{k}.pkl")
if "--nocache" in sys.argv or not os.path.exists(cache):
    data = []
    for b, ch in S.shapes(k):
        forms = sorted(set(S.cycle_forms(b, ch)))
        iv, lows = B.intervals(b, ch, forms=forms)
        data.append((len(forms) + 2, b, ch, forms, lows, iv))
    src = "regenerated"
else:
    data = pickle.load(open(cache, "rb"))
    src = "cache"
elig = [d for d in data if d[0] >= cutoff and sum(d[4]) <= cutoff and B.hall_ok(d[5], cutoff)]
elig.sort(key=lambda d: -d[0])
print(f"# source={src} shapes={len(data)} eligible={len(elig)} caps {elig[0][0]}..{elig[-1][0]}")
for i, d in enumerate(elig):
    print(f"{i} cap={d[0]} b={d[1]} nforms={len(d[3])}")
