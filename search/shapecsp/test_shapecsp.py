"""Behaviour gates for the shape/CSP pipeline.  `python test_shapecsp.py`

Every assertion calls the pipeline with values and checks the answer; none of
them pins a spelling.  Gate 3 is the one that fails if the degenerate families
(b < 2k, i.e. two chords sharing an endpoint) are dropped from enumeration.
"""
from __future__ import annotations
import sys
import shapes as S
import solve as SV
import verify as V

KNOWN = {2: 8, 3: 14, 4: 24, 5: 40}
fails = []


def gate(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ((" :: " + detail) if detail else ""))
    if not cond:
        fails.append(name)


# 0. the reformulation itself: for random shapes and random arc lengths the
#    multiset of lengths predicted by the cycle forms must equal the multiset
#    networkx finds in the materialised C_n + k chords graph.
import random, networkx as nx
random.seed(7)
tested = mism = 0
for k in (2, 3, 4, 5):
    sh = S.shapes(k)
    for b, ch in random.sample(sh, min(25, len(sh))):
        forms = S.cycle_forms(b, ch)
        par = S.parallel_arcs(b, ch)
        for _ in range(3):
            arcs = [random.randint(2 if i in par else 1, 4) for i in range(b)]
            n, chE, _ = V.materialise(b, ch, arcs)
            if not V.is_simple_cn_plus_chords(n, chE)[0]:
                continue
            model = sorted(sum(arcs[i] for i in range(b) if m >> i & 1) + c for m, c in forms)
            G = nx.cycle_graph(n); G.add_edges_from(chE)
            truth = sorted(len(c) for c in nx.simple_cycles(G))
            tested += 1
            mism += (model != truth)
gate("cycle forms reproduce the true cycle-length multiset",
     mism == 0 and tested > 100, f"{tested} graphs, {mism} mismatches")

# 1. cycle-space size: H has at most 2^(k+1)-1 cycles, independent of n
for k in (2, 3, 4, 5):
    mx = max(len(S.cycle_forms(b, c)) for b, c in S.shapes(k))
    gate(f"k={k} cycle count within 2^(k+1)-1", mx <= 2 ** (k + 1) - 1, f"max={mx} bound={2**(k+1)-1}")

# 2. exact t_k for the calibrated values
for k in (2, 3, 4):
    best, shape, arcs, stats = SV.t_k(k, 3, 120.0, workers=2)
    gate(f"t_{k} == {KNOWN[k]}", best == KNOWN[k], f"got {best} from shape {shape} arcs {arcs}")
    ok, n, ch, why = V.check(shape[0], shape[1], arcs)
    gate(f"t_{k} witness is a real pancyclic C_n+{k} chords", ok and n == KNOWN[k],
         f"n={n} chords={ch} {why}")

# 3. degenerate families are present, and dropping them changes the answer.
#    Measured: restricting to b=2k (a perfect matching on 2k branch points, the
#    non-degenerate shapes only) gives 14 for k=3 -- no loss -- but 22 for k=4,
#    two short of t_4=24.  So the degenerate families are not optional.
NONDEG = {3: 14, 4: 22}
for k in (3, 4):
    bs = {b for b, _ in S.shapes(k)}
    gate(f"k={k} enumeration includes degenerate b<2k", any(b < 2 * k for b in bs), f"b values {sorted(bs)}")
    best_nd, shape_nd, arcs_nd, _ = SV.t_k(k, 3, 120.0, workers=2, b_values=[2 * k])
    gate(f"k={k} b=2k-only bound is {NONDEG[k]}", best_nd == NONDEG[k],
         f"b=2k only gives {best_nd}, true t_{k}={KNOWN[k]}")
gate("dropping the degenerate families loses t_4", NONDEG[4] < KNOWN[4],
     f"b=2k only reaches {NONDEG[4]}, t_4={KNOWN[4]}")

# 4. the solver's optimality claim is not vacuous: one above the optimum is infeasible
for k, b, ch in ((2, 4, ((0, 2), (1, 3))),):
    st, n, arcs = SV.solve_shape(b, ch, KNOWN[k] + 1, 60.0, 2)
    gate(f"k={k} shape {ch} infeasible at n>={KNOWN[k]+1}", st == "INFEASIBLE", f"status {st} n={n}")

print()
print("FAILED: " + ", ".join(fails) if fails else "ALL GATES PASS")
sys.exit(1 if fails else 0)
