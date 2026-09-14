"""Heuristic upper bounds: extend pancyclic witnesses from n to n+1 by inserting one vertex into
an arc (all 2k positions tried), keeping the chord count.  Iterates as far as it can, keeping
a pool of witnesses per n.  Output: extend.csv  (n, k, witness).
Usage: python extend.py n0 "(a,b) (c,d) ..." nmax
"""
import sys, itertools, networkx as nx

def lengths(n, chords):
    G = nx.cycle_graph(n); G.add_edges_from(chords)
    return {len(c) for c in nx.simple_cycles(G)}

def pancyclic(n, chords):
    return set(range(3, n + 1)) <= lengths(n, chords)

def canon(n, chords):
    """canonical form under rotation+reflection"""
    best = None
    for r in range(n):
        for refl in (1, -1):
            cs = tuple(sorted(tuple(sorted(((refl * a + r) % n, (refl * b + r) % n))) for a, b in chords))
            if best is None or cs < best: best = cs
    return best

def insert_vertex(n, chords, pos):
    """insert a new vertex between pos and pos+1 (mod n); chords with endpoint > pos shift up"""
    def sh(v): return v + 1 if v > pos else v
    return n + 1, [tuple(sorted((sh(a), sh(b)))) for a, b in chords]

if __name__ == "__main__":
    n = int(sys.argv[1])
    chords = [tuple(map(int, s.strip("()").split(","))) for s in sys.argv[2].split()]
    nmax = int(sys.argv[3])
    k = len(chords)
    assert pancyclic(n, chords), "seed is not pancyclic"
    pool = {canon(n, chords)}
    out = open("extend.csv", "a")
    while n < nmax and pool:
        newpool = set()
        for cs in pool:
            for pos in range(n):
                n1, c1 = insert_vertex(n, list(cs), pos)
                if pancyclic(n1, c1):
                    newpool.add(canon(n1, c1))
        n += 1
        if not newpool:
            print(f"n={n}: no extension with {k} chords from {len(pool)} witnesses at n-1"); out.write(f"{n},{k},NONE-BY-EXTENSION\n"); break
        pool = newpool
        w = sorted(pool)[0]
        print(f"n={n}: {len(pool)} witnesses, e.g. {w}"); out.write(f"{n},{k},\"{' '.join(str(c) for c in w)}\"\n"); out.flush()
