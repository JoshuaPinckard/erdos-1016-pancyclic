"""Literal implementation of the GKW/Bondy shortcut recipe (as reproduced in Alon-Krivelevich
arXiv:2308.01564 Section 3) for K=4, i.e. K+1=5 shortcuts e_0..e_4 (e_i a 2^i-shortcut, chained
through shared vertices) plus 1 joining edge = 6 chords total. Predicted (by hand algebra in
REPORT-bondy-construction.md) to be pancyclic for n in [v_4, 2*v_4] roughly where v_4=2^5+4=36,
i.e. reach up to 2^6+4=68, MINUS a leftover gap at cycle length 5 (since K+1=5 is the one value
in [5,K+1]=[5,5] that stage 1-2 alone does not cover). This script builds the graph for each n and
reports the exact missing lengths, to see whether the analytic prediction is right and how it
actually fails.
Usage: python gkw_construction.py nlo nhi
"""
import sys, networkx as nx

def build(n, K=4):
    v = [0]
    for i in range(K + 1):
        v.append(v[-1] + 2 ** i + 1)
    chords = [(v[i], v[i + 1]) for i in range(K + 1)]
    chords.append((v[0], v[-1]))  # joining edge: first vertex of e_0 to second vertex of e_K
    # all endpoints must be < n and the construction needs n >= v[-1]
    return chords, v[-1]

def lengths(n, chords):
    G = nx.cycle_graph(n)
    G.add_edges_from([(a % n, b % n) for a, b in chords])
    return {len(c) for c in nx.simple_cycles(G)}

def main():
    nlo, nhi = int(sys.argv[1]), int(sys.argv[2])
    chords, vmax = build(0)  # K=4 fixed; v computed once (doesn't depend on n)
    print(f"chords (fixed shape, K=4): {chords}   requires n >= {vmax}")
    for n in range(max(nlo, vmax), nhi + 1):
        L = lengths(n, chords)
        missing = sorted(set(range(3, n + 1)) - L)
        status = "PANCYCLIC" if not missing else f"missing {missing}"
        print(f"n={n}: {status}")

if __name__ == "__main__":
    main()
