"""Same as scan_join.py but loops over a range of n in one process (to respect the one-process-
at-a-time compute rule) and reports, for each n, whether ANY single 6th chord (added to the 5
fixed GKW shortcuts) makes the graph fully pancyclic, and if so the smallest example found.
Usage: python scan_join_range.py nlo nhi
"""
import sys, networkx as nx

SHORTCUTS = [(0, 2), (2, 5), (5, 10), (10, 19), (19, 36)]

def lengths(n, chords):
    G = nx.cycle_graph(n); G.add_edges_from(chords)
    return {len(c) for c in nx.simple_cycles(G)}

def scan(n):
    base = set(tuple(sorted(c)) for c in SHORTCUTS)
    for a in range(n):
        for b in range(a + 2, n):
            if (b - a) % n in (1, n - 1):
                continue
            e = (a, b)
            if e in base:
                continue
            chords = SHORTCUTS + [e]
            missing = set(range(3, n + 1)) - lengths(n, chords)
            if not missing:
                return e
    return None

def main():
    nlo, nhi = int(sys.argv[1]), int(sys.argv[2])
    for n in range(nlo, nhi + 1):
        w = scan(n)
        if w:
            print(f"n={n}: WITNESS 6th chord={w}  chords={SHORTCUTS + [w]}", flush=True)
        else:
            print(f"n={n}: none found", flush=True)

if __name__ == "__main__":
    main()
