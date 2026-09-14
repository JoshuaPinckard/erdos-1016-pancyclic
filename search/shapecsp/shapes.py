"""Shape enumeration and cycle-space analysis for C_n-plus-k-chords graphs.

A "C_n plus k chords" graph G has n vertices, the cycle edges of C_n, and k extra
(chord) edges.  Let P be the set of chord endpoints, b = |P|.  Every vertex of G
outside P has degree 2, so G is a subdivision of the multigraph

    H = (cycle on the b points of P, in their cyclic order along C_n)
        + (the k chords, as a simple graph M on those b points, min degree >= 1).

Subdividing an edge does not change which edge sets are cycles, so the cycle
*structure* of G is determined by H alone; only the *lengths* depend on n.
Writing a_0..a_{b-1} for the arc lengths of C_n between consecutive points of P
(a_i >= 1, sum a_i = n) and giving every chord length 1, a cycle C of H of
arc-set A_C and chord-set X_C has length in G

    L_C(a) = sum_{i in A_C} a_i + |X_C|      -- a 0/1 linear form in the a_i.

dim(cycle space of H) = (b + k) - b + 1 = k + 1, so H has at most 2^(k+1) - 1
cycles regardless of n.

This module produces, for each k, the list of shapes (H up to the dihedral
symmetry of the cycle, INCLUDING the degenerate families b < 2k where chords
share endpoints) together with the cycle forms of each shape.
"""
from __future__ import annotations
from itertools import combinations


# ---------------------------------------------------------------- shape enum

def _dihedral(b):
    """The 2b maps of D_b on positions 0..b-1 (rotations and reflections)."""
    out = []
    for r in range(b):
        out.append(tuple((i + r) % b for i in range(b)))
        out.append(tuple((r - i) % b for i in range(b)))
    return out


def canon(b, edges):
    """Canonical form of a chord set under D_b: the lex-least relabelling."""
    best = None
    for g in _dihedral(b):
        img = tuple(sorted(tuple(sorted((g[u], g[v]))) for u, v in edges))
        if best is None or img < best:
            best = img
    return best


def _graphs_min_deg1(b, k):
    """All simple graphs on 0..b-1 with exactly k edges and no isolated vertex.

    Edges are chosen in lex order; we prune as soon as the smallest still
    uncovered vertex can no longer be covered by any remaining candidate edge.
    """
    pool = [(u, v) for u in range(b) for v in range(u + 1, b)]
    npool = len(pool)
    # last position in `pool` at which vertex v can still be picked up
    last = [max(i for i, e in enumerate(pool) if v in e) for v in range(b)]
    out = []

    def rec(pos, chosen, covered):
        need = k - len(chosen)
        if need == 0:
            if len(covered) == b:
                out.append(tuple(chosen))
            return
        if npool - pos < need:
            return
        uncovered = [v for v in range(b) if v not in covered]
        if len(uncovered) > 2 * need:
            return
        for v in uncovered:                       # v can never be covered again
            if last[v] < pos:
                return
        for i in range(pos, npool - need + 1):
            u, v = pool[i]
            chosen.append(pool[i])
            rec(i + 1, chosen, covered | {u, v})
            chosen.pop()

    rec(0, [], frozenset())
    return out


def shapes(k, b_values=None):
    """All shapes for a given k, up to D_b, as (b, chords) pairs.

    b ranges over every value for which a simple k-edge graph with no isolated
    vertex exists on b points: k <= C(b,2) and b <= 2k.  b < 2k is exactly the
    degenerate family where two or more chords share an endpoint.
    """
    res = []
    lo = min(b for b in range(2, 2 * k + 1) if b * (b - 1) // 2 >= k)
    rng = range(lo, 2 * k + 1) if b_values is None else b_values
    for b in rng:
        if b * (b - 1) // 2 < k:
            continue
        seen = set()
        for edges in _graphs_min_deg1(b, k):
            c = canon(b, edges)
            if c not in seen:
                seen.add(c)
                res.append((b, c))
    return res


# ------------------------------------------------------------- cycle forms

def cycle_forms(b, chords):
    """Every cycle of H, as (arc_mask, n_chords).

    Edges of H: index i in [0,b) is the arc from point i to point i+1 mod b;
    index b+j is chord j.  Enumerates the whole cycle space (dimension k+1) and
    keeps the elements that are a single cycle (all degrees 0 or 2, connected).
    """
    ends = [(i, (i + 1) % b) for i in range(b)] + [tuple(c) for c in chords]
    m = len(ends)

    parent = list(range(b))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    tree, extra = [], []
    for idx, (u, v) in enumerate(ends):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            tree.append(idx)
        else:
            extra.append(idx)

    # fundamental cycle of each non-tree edge, as an edge bitmask
    adj = {v: [] for v in range(b)}
    for idx in tree:
        u, v = ends[idx]
        adj[u].append((v, idx))
        adj[v].append((u, idx))

    def tree_path(s, t):
        prev = {s: (None, None)}
        stack = [s]
        while stack:
            x = stack.pop()
            if x == t:
                break
            for y, idx in adj[x]:
                if y not in prev:
                    prev[y] = (x, idx)
                    stack.append(y)
        mask, x = 0, t
        while prev[x][0] is not None:
            px, idx = prev[x]
            mask |= 1 << idx
            x = px
        return mask

    basis = []
    for idx in extra:
        u, v = ends[idx]
        basis.append(tree_path(u, v) | (1 << idx))

    forms = []
    for sel in range(1, 1 << len(basis)):
        mask = 0
        s = sel
        i = 0
        while s:
            if s & 1:
                mask ^= basis[i]
            s >>= 1
            i += 1
        deg = [0] * b
        edges = []
        for idx in range(m):
            if mask >> idx & 1:
                u, v = ends[idx]
                deg[u] += 1
                deg[v] += 1
                edges.append(idx)
        if any(d not in (0, 2) for d in deg):
            continue
        # connectivity among the used edges
        used = [v for v in range(b) if deg[v] == 2]
        nb = {v: [] for v in used}
        for idx in edges:
            u, v = ends[idx]
            nb[u].append(v)
            nb[v].append(u)
        seen, stack = {used[0]}, [used[0]]
        while stack:
            x = stack.pop()
            for y in nb[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        if len(seen) != len(used):
            continue
        arc_mask = mask & ((1 << b) - 1)
        forms.append((arc_mask, len(edges) - bin(arc_mask).count("1")))
    return forms


def parallel_arcs(b, chords):
    """Arc indices that a chord duplicates.  G is simple only if such an arc has
    length >= 2 (otherwise the chord would be a second copy of a cycle edge)."""
    out = set()
    for u, v in chords:
        if (u + 1) % b == v:
            out.add(u)
        elif (v + 1) % b == u:
            out.add(v)
    return out
