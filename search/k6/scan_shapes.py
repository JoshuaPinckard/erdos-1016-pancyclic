"""For each of several 5-chord empirical extremal shapes (given at their native n0=40), scale to
a target n (stretching the >2 "geometric" gaps proportionally, keeping gaps<=2 fixed -- exactly
seedsearch.py's scale()), then exhaustively try every possible 6th chord. Loops over a shape index
and an n range in one process. Usage: python scan_shapes.py shape_idx nlo nhi
shape_idx: 0..4, one per SHAPES entry below.
"""
import sys, networkx as nx

SHAPES = [
    [(0, 2), (1, 5), (1, 7), (3, 34), (24, 39)],
    [(0, 2), (0, 37), (1, 35), (3, 18), (8, 39)],
    [(0, 2), (0, 33), (1, 13), (3, 34), (32, 35)],
    [(0, 4), (0, 5), (1, 34), (2, 35), (3, 15)],
    [(0, 7), (1, 8), (2, 10), (2, 11), (9, 21)],
]
N0 = 40

def scale(chords, n0, n):
    pts = sorted(set(v for c in chords for v in c))
    gaps = [(pts[(i + 1) % len(pts)] - pts[i]) % n0 for i in range(len(pts))]
    big = [i for i, g in enumerate(gaps) if g > 2]
    small = sum(g for g in gaps if g <= 2)
    bigsum = sum(gaps[i] for i in big)
    target = n - small
    ng = list(gaps)
    for i in big:
        ng[i] = max(3, round(gaps[i] * target / bigsum))
    diff = n - sum(ng)
    ng[big[0]] += diff
    newpos = {}
    p = 0
    for i, v in enumerate(pts):
        newpos[v] = p
        p += ng[i]
    return [tuple(sorted((newpos[a], newpos[b]))) for a, b in chords]

def lengths(n, chords):
    G = nx.cycle_graph(n); G.add_edges_from(chords)
    return {len(c) for c in nx.simple_cycles(G)}

def scan_one(n, base5):
    base = set(tuple(sorted(c)) for c in base5)
    for a in range(n):
        for b in range(a + 2, n):
            if (b - a) % n in (1, n - 1):
                continue
            e = (a, b)
            if e in base:
                continue
            chords = base5 + [e]
            missing = set(range(3, n + 1)) - lengths(n, chords)
            if not missing:
                return e
    return None

def main():
    shape_idx = int(sys.argv[1])
    nlo, nhi = int(sys.argv[2]), int(sys.argv[3])
    shape = SHAPES[shape_idx]
    print(f"shape {shape_idx} = {shape}", flush=True)
    for n in range(nlo, nhi + 1):
        base5 = scale(shape, N0, n)
        w = scan_one(n, base5)
        if w:
            print(f"n={n}: WITNESS base5={base5} 6th={w}", flush=True)
        else:
            print(f"n={n}: none found (base5={base5})", flush=True)

if __name__ == "__main__":
    main()
