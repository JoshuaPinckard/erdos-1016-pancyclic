"""Exact per-shape maximisation of n by CP-SAT, and the t_k driver.

For one shape the model is:
    a_i         integer arc lengths, a_i >= 1 (>= 2 when a chord duplicates arc i)
    n           = sum a_i
    L_f         = sum_{i in mask(f)} a_i + chords(f)   for every distinct cycle form f
    coverage    for every l in [3, n] there is a form f with L_f = l
    objective   maximise n

Because every cycle of G has length <= n and >= 3, coverage forces a surjection
from the cycle forms onto [3, n]; hence n <= (#distinct forms) + 2, which is the
per-shape cap NMAX used to bound the variables.  That cap is also the pruning
rule of the driver: a shape whose cap does not exceed the incumbent cannot beat
it and is never handed to the solver.
"""
from __future__ import annotations
import sys, time
from ortools.sat.python import cp_model

import shapes as S


def build(b, chords, forms, lows, nmax, target, maximize=True):
    m = cp_model.CpModel()
    base = sum(lows)
    a = [m.NewIntVar(lows[i], nmax - (base - lows[i]), f"a{i}") for i in range(b)]
    n = m.NewIntVar(max(target, b, 3), nmax, "n")
    m.Add(n == sum(a))

    L = []
    for mask, ch in forms:
        idx = [i for i in range(b) if mask >> i & 1]
        lo = sum(lows[i] for i in idx) + ch
        v = m.NewIntVar(max(3, lo), nmax, "L")
        m.Add(v == sum(a[i] for i in idx) + ch)
        m.Add(v <= n)              # valid: a cycle of G has at most n vertices
        L.append((v, max(3, lo)))

    # hit[f][l] <=> L_f == l
    hits = {l: [] for l in range(3, nmax + 1)}
    for v, vlo in L:
        lit = {}
        for l in range(vlo, nmax + 1):
            x = m.NewBoolVar("")
            m.Add(v == l).OnlyEnforceIf(x)
            m.Add(v != l).OnlyEnforceIf(x.Not())
            lit[l] = x
            hits[l].append(x)
        m.AddExactlyOne(lit.values())

    for l in range(3, nmax + 1):
        if l <= target:
            if not hits[l]:
                return None, None, None          # l unreachable: model infeasible
            m.AddBoolOr(hits[l])
        else:
            inr = m.NewBoolVar("")                 # inr <=> n >= l
            m.Add(n >= l).OnlyEnforceIf(inr)
            m.Add(n <= l - 1).OnlyEnforceIf(inr.Not())
            m.Add(sum(hits[l]) >= 1).OnlyEnforceIf(inr)
    if maximize:
        m.Maximize(n)
    return m, a, n


def _feasible(b, chords, forms, lows, nmax, target, time_limit, workers):
    m, a, n = build(b, chords, forms, lows, nmax, target, maximize=False)
    if m is None:
        return "INFEASIBLE", None, None
    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = time_limit
    sv.parameters.num_workers = workers
    st = sv.Solve(m)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return "SAT", sv.Value(n), [sv.Value(x) for x in a]
    if st == cp_model.INFEASIBLE:
        return "INFEASIBLE", None, None
    return "UNKNOWN", None, None


def solve_shape(b, chords, target, time_limit=60.0, workers=8):
    """Max n for this shape subject to n >= target.

    Answered by a ladder of pure-feasibility solves rather than one optimisation:
    the first call at `target` is the one that matters (almost every shape is
    infeasible there and the proof is cheap), and each success raises the bar to
    the n just achieved plus one.  The final INFEASIBLE is the optimality proof.
    Returns (status, n, arcs) with status OPTIMAL / INFEASIBLE / UNKNOWN.
    """
    forms = sorted(set(cycle_forms_cached(b, chords)))
    nmax = len(forms) + 2
    if nmax < target:
        return "PRUNED", None, None
    par = S.parallel_arcs(b, chords)
    lows = [2 if i in par else 1 for i in range(b)]
    if sum(lows) > nmax:
        return "PRUNED", None, None

    best_n, best_a, t = None, None, target
    while t <= nmax:
        st, n, arcs = _feasible(b, chords, forms, lows, nmax, t, time_limit, workers)
        if st == "INFEASIBLE":
            break
        if st == "UNKNOWN":
            return ("UNKNOWN" if best_n is None else "FEASIBLE"), best_n, best_a
        best_n, best_a, t = n, arcs, n + 1
    if best_n is None:
        return "INFEASIBLE", None, None
    return "OPTIMAL", best_n, best_a


_form_cache = {}


def cycle_forms_cached(b, chords):
    key = (b, chords)
    if key not in _form_cache:
        _form_cache[key] = S.cycle_forms(b, chords)
    return _form_cache[key]


def t_k(k, start=3, time_limit=60.0, workers=8, b_values=None, log=None, order=True):
    """Exact t_k: max over shapes.  `start` is a lower bound already known (a
    witness), used only to prune; the result is independent of it whenever it is
    a true lower bound.  Returns (best_n, best_shape, best_arcs, stats)."""
    sh = S.shapes(k, b_values=b_values)
    caps = []
    for b, ch in sh:
        caps.append((len(set(S.cycle_forms(b, ch))) + 2, b, ch))
    if order:
        caps.sort(reverse=True)
    best, bshape, barcs = start - 1, None, None
    solved = pruned = unknown = 0
    t0 = time.time()
    for cap, b, ch in caps:
        if cap <= best:
            pruned += 1
            continue
        st, n, arcs = solve_shape(b, ch, best + 1, time_limit, workers)
        if st == "PRUNED":
            pruned += 1
            continue
        solved += 1
        if st == "UNKNOWN":
            unknown += 1
            if log:
                log(f"  UNKNOWN b={b} chords={ch} cap={cap}")
            continue
        if n is not None and n > best:
            best, bshape, barcs = n, (b, ch), arcs
            if log:
                log(f"  new best n={n} b={b} chords={ch} arcs={arcs}")
        if st == "FEASIBLE" and log:
            log(f"  TIMEOUT-not-proved-optimal b={b} chords={ch} cap={cap} n={n}")
    return best, bshape, barcs, dict(shapes=len(sh), solved=solved, pruned=pruned,
                                     unknown=unknown, seconds=round(time.time() - t0, 1))


if __name__ == "__main__":
    k = int(sys.argv[1])
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    tl = float(sys.argv[3]) if len(sys.argv) > 3 else 60.0
    best, bshape, barcs, stats = t_k(k, start, tl, log=lambda s: print(s, flush=True))
    print(f"t_{k} = {best}  shape={bshape}  arcs={barcs}  {stats}", flush=True)
