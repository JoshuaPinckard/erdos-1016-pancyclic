"""Per-arc upper bounds (caps) and the bounded-composition rank space they define.

The cap rule is the one prune_probe.py measured and nothing more: bound.intervals
reads lows[i] as "arc i has length >= lows[i]", so raising lows[i] to v+1 and
re-running bound.hall_ok asks "can any pancyclic realisation have a_i >= v+1?".
When that fails, a_i <= v for every pancyclic realisation.  hall_ok is a pure
necessary condition, so the resulting box

    lows[i] <= a_i <= hi[i]

CONTAINS every pancyclic composition.  Enumerating the box is therefore a
superset of the solutions and skips no witness -- that, and only that, is what
makes the pruned search still an exhaustion proof.

The GPU needs to unrank inside the box.  Substituting y_i = a_i - lows[i] gives
0 <= y_i <= cap_i, sum y_i = rem, and

    T[k][s] = #{ (y_k..y_{b-1}) : 0 <= y_i <= cap_i, sum = s }
            = sum_{y=0}^{min(cap_k,s)} T[k+1][s-y],      T[b][s] = [s == 0]

with prefix sums S[k][j] = sum_{i<=j} T[k][i].  Unranking digit k in
lexicographic order then costs one binary search over S[k+1] instead of a
per-y linear scan, which is what keeps the pruned kernel as cheap per rank as
the unrestricted one.
"""
from __future__ import annotations

import math

import bound as B
import shapes as S


def arc_caps(n, b, chords, forms, lows):
    """Largest v with "a_i >= v" still surviving Hall, per arc.

    Same probe as prune_probe.py.  Returned hi[i] >= lows[i] always: the box is
    never empty by construction, because lows itself passed Hall to be in the
    manifest at all.
    """
    hi = []
    for i in range(b):
        v = lows[i]
        while v < n:
            probe = list(lows)
            probe[i] = v + 1
            if sum(probe) > n:
                break
            iv, _ = B.intervals(b, chords, forms, probe)
            if not B.hall_ok(iv, n):
                break
            v += 1
        hi.append(v)
    return hi


def prefix_tables(rem, caps):
    """S[k][j] for k in 0..b, j in 0..rem, as a list of lists of ints.

    S[k][j] = number of (y_k..y_{b-1}) in the caps box summing to at most j.
    S[0][rem] - S[0][rem-1] is the bounded total.
    """
    b = len(caps)
    T = [[0] * (rem + 1) for _ in range(b + 1)]
    T[b][0] = 1
    for k in range(b - 1, -1, -1):
        row, nxt = T[k], T[k + 1]
        for s in range(rem + 1):
            hi = min(caps[k], s)
            row[s] = sum(nxt[s - y] for y in range(hi + 1))
    out = []
    for k in range(b + 1):
        acc, pref = 0, []
        for j in range(rem + 1):
            acc += T[k][j]
            pref.append(acc)
        out.append(pref)
    return out


def total_from_tables(tables, rem):
    """T[0][rem], recovered from the prefix sums."""
    return tables[0][rem] - (tables[0][rem - 1] if rem else 0)


def bounded_total_inclusion_exclusion(n, lows, hi):
    """Independent count of the same box, by inclusion-exclusion over overflow.

    This is prune_probe.bounded_count.  It shares no code with prefix_tables,
    so agreement between the two is real cross-validation of the rank space
    size, not a tautology.
    """
    b = len(lows)
    slack = n - sum(lows)
    if slack < 0:
        return 0
    caps = [hi[i] - lows[i] for i in range(b)]
    tot = 0
    for mask in range(1 << b):
        s, bits = slack, 0
        for i in range(b):
            if mask >> i & 1:
                s -= caps[i] + 1
                bits += 1
        if s < 0:
            continue
        tot += (-1) ** bits * math.comb(s + b - 1, b - 1)
    return tot


def unrank_bounded(rank, rem, caps, tables):
    """rank -> y, lexicographic on (y_0, .., y_{b-1}).  CPU reference.

    Mirrors the kernel's search exactly so a kernel/CPU disagreement is a real
    disagreement and not two different orderings.
    """
    b = len(caps)
    total = total_from_tables(tables, rem)
    if not 0 <= rank < total:
        raise ValueError("rank out of bounded range")
    y = [0] * b
    r, s = rank, rem
    for k in range(b - 1):
        sk = tables[k + 1]
        target = sk[s] - r
        lo, hi = -1, s - 1
        while lo < hi:                       # largest z with S[k+1][z] < target
            mid = (lo + hi + 1) >> 1
            if sk[mid] < target:
                lo = mid
            else:
                hi = mid - 1
        z = lo
        y[k] = s - 1 - z
        r -= sk[s] - sk[z + 1]
        s -= y[k]
    y[b - 1] = s
    return y


def rank_bounded(y, rem, caps, tables):
    """y -> rank.  Inverse of unrank_bounded; raises on a y outside the box."""
    b = len(caps)
    if len(y) != b or sum(y) != rem:
        raise ValueError("y is not a composition of rem")
    for k in range(b):
        if not 0 <= y[k] <= caps[k]:
            raise ValueError(f"y[{k}]={y[k]} outside cap {caps[k]}")
    rank, s = 0, rem
    for k in range(b - 1):
        sk = tables[k + 1]
        rank += sk[s] - sk[s - y[k]]         # all choices with a smaller y_k
        s -= y[k]
    return rank


def box_from_hi(n, b, chords, lows, hi):
    """Assemble a box from caps already computed, skipping the Hall probe.

    Only for a cache hit whose hi was produced by arc_caps for this exact n and
    shape; the caller is responsible for proving that, and gpu_state_runner_
    bounded re-probes a sample on every load to keep it honest.
    """
    forms = sorted(set(S.cycle_forms(b, chords)))
    iv, derived = B.intervals(b, chords, forms)
    if list(lows) != list(derived):
        raise ValueError("manifest lows disagree with bound.intervals")
    rem = n - sum(derived)
    caps = [hi[i] - derived[i] for i in range(b)]
    if any(c < 0 for c in caps):
        raise ValueError("cached hi below lows")
    tables = prefix_tables(rem, caps)
    return dict(b=b, chords=chords, forms=forms, iv=iv, lows=derived, hi=list(hi),
                caps=caps, rem=rem, tables=tables,
                total=total_from_tables(tables, rem),
                unrestricted_total=math.comb(rem + b - 1, b - 1))


def shape_box(n, b, chords, lows=None):
    """Everything the GPU and the unit planner need for one manifest shape."""
    forms = sorted(set(S.cycle_forms(b, chords)))
    iv, derived = B.intervals(b, chords, forms)
    if lows is not None and list(lows) != list(derived):
        raise ValueError("manifest lows disagree with bound.intervals")
    lows = derived
    hi = arc_caps(n, b, chords, forms, lows)
    rem = n - sum(lows)
    caps = [hi[i] - lows[i] for i in range(b)]
    tables = prefix_tables(rem, caps)
    total = total_from_tables(tables, rem)
    unrestricted = math.comb(rem + b - 1, b - 1)
    return dict(b=b, chords=chords, forms=forms, iv=iv, lows=lows, hi=hi,
                caps=caps, rem=rem, tables=tables, total=total,
                unrestricted_total=unrestricted)
