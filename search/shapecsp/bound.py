"""A cheap rigorous per-shape upper bound on n, much tighter than #forms + 2.

For a form f with arc set A_f and chord count |X_f|, and arc lower bounds low_i
(1, or 2 when a chord duplicates that arc):

    L_f   = sum_{i in A_f}    a_i + |X_f|  >=  mu_f := sum_{i in A_f}    low_i + |X_f|
    n-L_f = sum_{i notin A_f} a_i - |X_f|  >=  nu_f := sum_{i notin A_f} low_i - |X_f|

so whatever the arc lengths are, form f can only ever realise a length in the
interval [mu_f, n - max(nu_f, 0)].  Pancyclicity needs each of the n-2 values in
[3, n] realised by a different form -- one form has one length -- i.e. a matching
saturating [3, n] in the bipartite graph value <-> form.  Neighbourhoods are
intervals, so Hall's condition only has to be checked on intervals of values:

    for all 3 <= x <= y <= n:  #{f : mu_f <= y and n - max(nu_f,0) >= x} >= y-x+1

`hall_ok(iv, n)` is that test; `hall_cap` is the largest n passing it.  Both are
pure necessary conditions, so a shape failing at n cannot reach n.
"""
from __future__ import annotations
import shapes as S


def intervals(b, chords, forms=None, lows=None):
    """(mu_f, nu_f) per form, plus the arc lower bounds used."""
    if forms is None:
        forms = sorted(set(S.cycle_forms(b, chords)))
    if lows is None:
        par = S.parallel_arcs(b, chords)
        lows = [2 if i in par else 1 for i in range(b)]
    tot = sum(lows)
    out = []
    for mask, ch in forms:
        inside = sum(lows[i] for i in range(b) if mask >> i & 1)
        out.append((max(3, inside + ch), max(0, (tot - inside) - ch)))
    return out, lows


def hall_ok(iv, n):
    items = [(mu, n - nu) for mu, nu in iv if mu <= n - nu and mu <= n]
    if len(items) < n - 2:
        return False
    by_hi = {}
    for lo, hi in items:
        by_hi.setdefault(min(hi, n), []).append(max(lo, 3))
    hist = [0] * (n + 2)
    for x in range(n, 2, -1):                     # active set = {hi >= x}
        for lo in by_hi.get(x, ()):
            hist[lo] += 1
        run = sum(hist[3:x + 1])                  # #{lo <= x} among active
        if run < 1:
            return False
        for y in range(x + 1, n + 1):
            run += hist[y]
            if run < y - x + 1:
                return False
    return True


def hall_cap(b, chords, forms=None, lows=None, nmax=None):
    iv, lows = intervals(b, chords, forms, lows)
    if nmax is None:
        nmax = len(iv) + 2
    for n in range(nmax, max(2, sum(lows) - 1), -1):
        if hall_ok(iv, n):
            return n
    return 0
