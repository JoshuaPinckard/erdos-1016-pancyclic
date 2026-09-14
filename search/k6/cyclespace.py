"""Cycle-space evaluator for pancyclicity of C_n plus k chords (CPU reference implementation).

Replaces the nx.simple_cycles enumeration used by verify.py / smart_climb.py.  C_n + k chords has
n vertices and n+k edges, so the cyclomatic number is (n+k) - n + 1 = k+1 and the cycle space has
exactly 2^(k+1)-1 nonzero elements (127 for k=6).  Every cycle of the graph is one of those
elements, so enumerating the cycle space and keeping the elements that are a *single* cycle gives
the exact set of cycle lengths.

Basis: element 0 = the Hamilton cycle C_n (all n cycle edges); element j+1 = chord j together with
the cycle path A[j]..B[j].  Elements are enumerated in Gray-code order so each step is one XOR.

"Is this element a single cycle" = (every vertex has degree 0 or 2) AND (the support is connected).
The degree test is done with whole-mask bit operations, not a per-vertex loop:
  R = rot1(E) has bit v = bit v-1 of E, so the two cycle edges at vertex v are bits v of E and R.
  D1 = E ^ R  -- vertices with exactly one incident cycle edge
  D2 = E & R  -- vertices with two incident cycle edges
  ch1 / ch2   -- vertices with exactly one / exactly two incident selected chords (maintained
                 incrementally along the Gray code), nbad = vertices with three or more.
  degrees are all in {0,2}  <=>  nbad == 0  and  D1 == ch1  and  (D2 & ch2) == 0.
Masks are Python ints, so there is no 60-vertex word-size limit here (see gpu_pancyc128.py for the
two-word 128-bit form of the same evaluator on the GPU, and fastcyc.c for the C form).

Usage:
  python cyclespace.py control              -- positive control (see control() below)
  python cyclespace.py check N "(a,b) ..."  -- print the cycle-length set for one chord set
"""
import sys, random

# ---------------------------------------------------------------- evaluator

def _connected(n, E, full, chords, S):
    """True iff the edge set (cycle-edge mask E, selected-chord mask S) is connected."""
    if E == full:
        return S == 0           # the whole Hamilton cycle; the degree test already forces S == 0
    edges = []
    if E:
        R = ((E << 1) | (E >> (n - 1))) & full
        starts = E & ~R         # edge p starts a maximal run  ->  path from vertex p to vertex q+1
        s = starts
        while s:
            p = (s & -s).bit_length() - 1
            s &= s - 1
            q = p
            while (E >> ((q + 1) % n)) & 1:
                q = (q + 1) % n
            edges.append((p, (q + 1) % n))
    SS = S
    while SS:
        j = (SS & -SS).bit_length() - 1
        SS &= SS - 1
        edges.append(chords[j])
    parent = {}
    for u, v in edges:
        parent.setdefault(u, u)
        parent.setdefault(v, v)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    comp = len(parent)
    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            comp -= 1
    return comp == 1


def cycle_length_mask(n, chords):
    """Bit L of the result is set iff C_n + chords has a cycle of length L."""
    chords = [tuple(sorted(c)) for c in chords]
    k = len(chords)
    full = (1 << n) - 1
    basis = [full] + [((1 << b) - (1 << a)) for (a, b) in chords]
    lens = 0
    E = 0
    S = 0
    cdeg = [0] * n
    ch1 = ch2 = 0
    nbad = 0
    for g in range(1, 1 << (k + 1)):
        bit = (g & -g).bit_length() - 1
        E ^= basis[bit]
        if bit:
            j = bit - 1
            S ^= 1 << j
            d = 1 if (S >> j) & 1 else -1
            for v in chords[j]:
                old = cdeg[v]
                new = old + d
                cdeg[v] = new
                if old == 1:
                    ch1 &= ~(1 << v)
                elif old == 2:
                    ch2 &= ~(1 << v)
                elif old >= 3:
                    nbad -= 1
                if new == 1:
                    ch1 |= 1 << v
                elif new == 2:
                    ch2 |= 1 << v
                elif new >= 3:
                    nbad += 1
        if nbad:
            continue
        R = ((E << 1) | (E >> (n - 1))) & full
        if (E ^ R) != ch1:
            continue
        if (E & R) & ch2:
            continue
        ne = E.bit_count() + S.bit_count()
        if ne < 3:
            continue
        if _connected(n, E, full, chords, S):
            lens |= 1 << ne
    return lens


def cycle_lengths(n, chords):
    m = cycle_length_mask(n, chords)
    return {L for L in range(3, n + 1) if (m >> L) & 1}


def missing(n, chords):
    return sorted(set(range(3, n + 1)) - cycle_lengths(n, chords))


def pancyclic(n, chords):
    need = ((1 << (n + 1)) - 1) & ~7
    return (cycle_length_mask(n, chords) & need) == need


def parse(s):
    return [tuple(map(int, t.strip("()").split(","))) for t in s.split()]

# ---------------------------------------------------------------- controls

# Recorded witnesses this evaluator must reproduce before any new claim is made.
W56 = (56, parse("(0,2) (0,53) (1,39) (20,39) (39,48) (48,53)"))   # search/k6/verify-56.txt
W40_5 = (40, parse("(0,5) (1,5) (2,30) (3,10) (4,11)"))            # search/gpu-40-5-all.txt


def control(verbose=True):
    """Positive control.  Returns True only if every check passes.

    (1) the recorded n=56 6-chord witness is pancyclic;
    (2) t_5 = 40 lower side: a recorded 5-chord witness is pancyclic at n=40, and the same chords
        are NOT pancyclic at n=41.  (The t_5 upper side -- exhaustive non-existence over ALL
        5-chord sets at n=41 -- is re-derived by gpu_pancyc128.py.  DECLARED CAP: this CPU control
        does not enumerate the 1.5e10 chord sets that requires.)
    (3) the evaluator agrees with networkx.simple_cycles on the FULL cycle-length set for random
        chord sets -- behaviour, not a spelling: any correct evaluator passes this.
    """
    ok = True
    n, ch = W56
    r = pancyclic(n, ch)
    ok &= r
    if verbose:
        print(f"[{'PASS' if r else 'FAIL'}] n=56 6-chord witness pancyclic: {r}  missing={missing(n, ch)}")
    n, ch = W40_5
    r = pancyclic(n, ch)
    ok &= r
    if verbose:
        print(f"[{'PASS' if r else 'FAIL'}] t_5 lower side: n=40 5-chord witness pancyclic: {r}")
    r = not pancyclic(41, ch)
    ok &= r
    if verbose:
        print(f"[{'PASS' if r else 'FAIL'}] those same 5 chords NOT pancyclic at n=41: {r}  missing={missing(41, ch)}")
    import networkx as nx
    rng = random.Random(20260914)
    bad = 0
    trials = 0
    for _ in range(300):
        n = rng.randint(7, 16)
        k = rng.randint(1, 6)
        pool = [(a, b) for a in range(n) for b in range(a + 2, n) if not (a == 0 and b == n - 1)]
        if len(pool) < k:
            continue
        ch = rng.sample(pool, k)
        G = nx.cycle_graph(n)
        G.add_edges_from(ch)
        ref = {len(c) for c in nx.simple_cycles(G)}
        got = cycle_lengths(n, ch)
        trials += 1
        if ref != got:
            bad += 1
            if verbose and bad <= 3:
                print(f"    MISMATCH n={n} chords={ch} nx={sorted(ref)} cyclespace={sorted(got)}")
    r = (bad == 0)
    ok &= r
    if verbose:
        print(f"[{'PASS' if r else 'FAIL'}] agrees with nx.simple_cycles on {trials} random graphs: {bad} mismatches")
    if verbose:
        print("CONTROL " + ("GREEN" if ok else "RED"))
    return bool(ok)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "control":
        sys.exit(0 if control() else 1)
    elif len(sys.argv) > 2 and sys.argv[1] == "check":
        n = int(sys.argv[2])
        ch = parse(sys.argv[3])
        ms = missing(n, ch)
        print(n, ch, "pancyclic" if not ms else "NOT pancyclic", "missing=" + str(ms))
    else:
        print(__doc__)
