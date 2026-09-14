"""Independent check of a shape solution.

Takes a shape (b, chords) and arc lengths, materialises the ACTUAL graph
C_n + k chords, and tests pancyclicity by enumerating its simple cycles with
networkx -- i.e. without using the cycle-space reformulation at all.  This is
the cross-check that the shape/CSP model is solving the right problem.
"""
from __future__ import annotations
import networkx as nx


def materialise(b, chords, arcs):
    """Return (n, chord_edge_list) for the C_n + k chords graph of this shape."""
    assert len(arcs) == b
    pos, p = [], 0
    for i in range(b):
        pos.append(p)
        p += arcs[i]
    n = p
    ch = []
    for u, v in chords:
        e = tuple(sorted((pos[u], pos[v])))
        ch.append(e)
    return n, ch, pos


def is_simple_cn_plus_chords(n, ch):
    """The chords must be distinct, non-loop, and not duplicate a cycle edge."""
    if len(set(ch)) != len(ch):
        return False, "duplicate chord"
    for a, b_ in ch:
        if a == b_:
            return False, "loop"
        if (b_ - a) % n in (1, n - 1):
            return False, f"chord {(a, b_)} duplicates a cycle edge"
    return True, "ok"


def cycle_lengths(n, ch):
    G = nx.cycle_graph(n)
    G.add_edges_from(ch)
    return {len(c) for c in nx.simple_cycles(G)}


def check(b, chords, arcs, verbose=False):
    n, ch, pos = materialise(b, chords, arcs)
    ok, why = is_simple_cn_plus_chords(n, ch)
    if not ok:
        return False, n, ch, why
    L = cycle_lengths(n, ch)
    missing = sorted(set(range(3, n + 1)) - L)
    if verbose:
        print(f"n={n} chords={ch} branch_points={pos} lengths={sorted(L)}")
    return (not missing), n, ch, ("pancyclic" if not missing else f"missing {missing}")
