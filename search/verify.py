"""Independent brute-force check of pancyclicity for C_n plus chords, using networkx simple cycles.
Usage: python verify.py n k            -> exhaustively search all k-chord sets (no symmetry), report min/witness
       python verify.py n "(a,b) (c,d)" -> check one chord set
"""
import sys, itertools, networkx as nx

def cycle_lengths(n, chords):
    G = nx.cycle_graph(n)
    G.add_edges_from(chords)
    return {len(c) for c in nx.simple_cycles(G)}

def pancyclic(n, chords):
    return set(range(3, n + 1)) <= cycle_lengths(n, chords)

def all_chords(n):
    return [(a, b) for a in range(n) for b in range(a + 2, n) if not (a == 0 and b == n - 1)]

if __name__ == "__main__":
    n = int(sys.argv[1])
    if len(sys.argv) > 2 and sys.argv[2].startswith("("):
        chords = [tuple(map(int, s.strip("()").split(","))) for s in sys.argv[2].split()]
        print(n, chords, "pancyclic" if pancyclic(n, chords) else "NOT pancyclic", sorted(cycle_lengths(n, chords)))
    else:
        k = int(sys.argv[2])
        cnt = 0
        for S in itertools.combinations(all_chords(n), k):
            cnt += 1
            if pancyclic(n, list(S)):
                print("WITNESS", n, k, S, "after", cnt); break
        else:
            print("NONE", n, k, "sets", cnt)
