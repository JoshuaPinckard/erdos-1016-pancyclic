"""Independent check of a shape solution.

Takes a shape (b, chords) and arc lengths, materialises the ACTUAL graph
C_n + k chords, and tests pancyclicity by enumerating its simple cycles with
networkx -- i.e. without using the cycle-space reformulation at all.  This is
the cross-check that the shape/CSP model is solving the right problem.

`check_record` is the same cross-check applied to one line of solver output, and
it is the ONLY route by which a driver may accept a SAT.  Reading the solver's
own claim is not acceptance: the arcs are re-checked against the shape's lower
bounds, the requested n and the shape's cap, and then the graph they describe is
built and tested here.  A SAT this function refuses is a solver defect, and the
drivers stop on it rather than counting it.
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


def check_record(rec, b, chords, lows, cap, cutoff, exact=False):
    """Re-derive one `SHAPE i SAT n=N arcs=...` record from scratch.

    Always returns a pair.  On acceptance it is ((n, arcs, chord_edges,
    explanation), None); on rejection (None, why).  The uniform shape is
    deliberate: a caller cannot unpack a rejection as though it were a witness.
    """
    try:
        n = int(rec.split()[3].split("=")[1])
        arcs = [int(x) for x in rec.split()[4].split("=")[1].split(",")]
    except Exception as e:
        return None, f"unparseable SAT record {rec!r} ({e!r})"
    if len(arcs) != b:
        return None, f"SAT gives {len(arcs)} arcs, shape has {b}"
    if any(x < lo for x, lo in zip(arcs, lows)):
        return None, f"SAT arcs {arcs} violate the lower bounds {list(lows)}"
    if sum(arcs) != n:
        return None, f"SAT arcs sum to {sum(arcs)}, record says n={n}"
    if n < cutoff or n > cap:
        return None, f"SAT n={n} outside [cutoff {cutoff}, cap {cap}]"
    if exact and n != cutoff:
        return None, f"exact mode asked for n={cutoff}, record says n={n}"
    ok, nv, che, why = check(b, chords, arcs)
    if not ok:
        return None, f"verify.check REJECTS the materialised graph: n={nv} {why}"
    if nv != n:
        return None, f"materialised graph has n={nv}, record says n={n}"
    return (n, arcs, che, why), None
