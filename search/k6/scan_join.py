"""Exhaustive scan: fix the 5 GKW shortcuts (0,2)(2,5)(5,10)(10,19)(19,36) (K=4) and try EVERY
possible 6th chord (a,b) on n vertices, checking full pancyclicity. This tests whether some
non-obvious 6th chord (not just the "join first-of-e0 to second-of-eK" edge) patches the length-5
gap for a given n, without adding a 7th chord.
Usage: python scan_join.py n
"""
import sys, itertools, networkx as nx

SHORTCUTS = [(0, 2), (2, 5), (5, 10), (10, 19), (19, 36)]

def lengths(n, chords):
    G = nx.cycle_graph(n); G.add_edges_from(chords)
    return {len(c) for c in nx.simple_cycles(G)}

def main():
    n = int(sys.argv[1])
    base = set(tuple(sorted(c)) for c in SHORTCUTS)
    found = []
    checked = 0
    for a in range(n):
        for b in range(a + 2, n):
            if (b - a) % n in (1, n - 1):
                continue
            e = (a, b)
            if e in base:
                continue
            chords = SHORTCUTS + [e]
            checked += 1
            L = lengths(n, chords)
            missing = set(range(3, n + 1)) - L
            if not missing:
                found.append(e)
    print(f"n={n}: checked {checked} candidate 6th chords; pancyclic witnesses found: {len(found)}")
    if found:
        print("examples:", found[:20])
    else:
        print("NONE: no single 6th chord (with these 5 fixed shortcuts) makes n=%d pancyclic" % n)

if __name__ == "__main__":
    main()
