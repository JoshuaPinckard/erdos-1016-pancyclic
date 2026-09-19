"""Measure how much the composition space shrinks under per-arc UPPER bounds
derived from the same Hall necessary condition already in bound.py.

bound.intervals treats `lows[i]` as "arc i has length >= lows[i]".  So raising
lows[i] to v and re-running hall_ok tests the hypothesis "a_i >= v".  If that
fails, no realisation has a_i >= v, i.e. a_i <= v-1 -- a rigorous per-arc upper
bound, obtained from machinery already in the tree and already trusted.

The GPU enumerates unrestricted compositions of n with a_i >= lows[i], count
C(n - sum(lows) + b - 1, b - 1).  With upper bounds too, the count is the
inclusion-exclusion over which arcs overflow.  The ratio is the prune factor.
"""
import json, sys, math, statistics
sys.path.insert(0, sys.argv[1])
import bound as B
import shapes as S

src, n, b, limit = sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])

def bounded_count(n, lo, hi):
    b = len(lo)
    slack = n - sum(lo)
    if slack < 0:
        return 0
    caps = [hi[i] - lo[i] for i in range(b)]
    tot = 0
    for mask in range(1 << b):
        s = slack
        bits = 0
        for i in range(b):
            if mask >> i & 1:
                s -= caps[i] + 1
                bits += 1
        if s < 0:
            continue
        tot += (-1) ** bits * math.comb(s + b - 1, b - 1)
    return tot

rows = [json.loads(l) for l in open(src, encoding="utf-8")]
rows = [r for r in rows if r["b"] == b][:limit]
ratios, base_tot, new_tot = [], 0, 0
for r in rows:
    chords = [tuple(c) for c in r["chords"]]
    forms = sorted(set(S.cycle_forms(r["b"], chords)))
    lows = list(r["lows"])
    hi = []
    for i in range(r["b"]):
        v = lows[i]
        # largest v with "a_i >= v" still passing Hall; a_i <= that v
        while v < n:
            probe = list(lows); probe[i] = v + 1
            if sum(probe) > n:
                break
            iv, _ = B.intervals(r["b"], chords, forms, probe)
            if not B.hall_ok(iv, n):
                break
            v += 1
        hi.append(v)
    base = math.comb(n - sum(lows) + r["b"] - 1, r["b"] - 1)
    assert base == r["total"], (base, r["total"])
    new = bounded_count(n, lows, hi)
    base_tot += base; new_tot += new
    ratios.append(base / new if new else float("inf"))
    print(json.dumps({"shape_index": r["shape_index"], "lows": lows, "hi": hi,
                      "total": base, "bounded_total": new,
                      "prune_factor": round(base / new, 2) if new else None}))
print(json.dumps({"n": n, "b": b, "shapes": len(rows),
                  "total_ranks": base_tot, "bounded_ranks": new_tot,
                  "aggregate_prune_factor": round(base_tot / new_tot, 2) if new_tot else None,
                  "median_per_shape": round(statistics.median(ratios), 2)}))

# Measured 2026-09-19 on the whole manifest (laptop, nice 19, seconds of CPU):
#   n=70 b=12  281 shapes  4.573e14 -> 2.388e14 ranks  aggregate 1.91x, median 1.37x
#   n=70 b=11 1138 shapes  3.528e14 -> 2.175e14 ranks  aggregate 1.62x, median 1.07x
# Spread is wide: shape 21335 prunes 27918x, shape 21349 only 1.37x.  Taking the
# prune would need a bounded-composition unrank in the CUDA kernel (the current
# one unranks unrestricted compositions), so the ~1.8x is not free.
