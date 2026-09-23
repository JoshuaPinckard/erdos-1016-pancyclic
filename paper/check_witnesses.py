"""Independent check of the witnesses cited in paper/main.pdf.

Every cycle of a graph is an element of its cycle space, so the cycle lengths
of C_n plus k chords can be read off the 2^(k+1) - 1 nonzero sums of its
fundamental cycles: keep a sum if it is 2-regular and connected. No search
code from this repository is used. Standard library only.

Usage: python3 paper/check_witnesses.py
"""
from itertools import combinations


def cycle_lengths(n, chords):
    key = lambda a, b: (min(a, b), max(a, b))
    for a, b in chords:
        assert (b - a) % n not in (0, 1, n - 1), "chord is a cycle edge"
    assert len({key(a, b) for a, b in chords}) == len(chords), "repeated chord"
    # Spanning tree: the path 0-1-...-(n-1). Non-tree edges: (n-1, 0) and the chords.
    path = lambda a, b: {key(i, i + 1) for i in range(min(a, b), max(a, b))}
    fundamental = [frozenset(path(a, b) | {key(a, b)}) for a, b in [(n - 1, 0), *chords]]
    lengths = set()
    for r in range(1, len(fundamental) + 1):
        for subset in combinations(fundamental, r):
            edges = set()
            for f in subset:
                edges ^= f
            adj = {}
            for a, b in edges:
                adj.setdefault(a, []).append(b)
                adj.setdefault(b, []).append(a)
            if any(len(v) != 2 for v in adj.values()):
                continue
            start = next(iter(adj))
            seen, stack = {start}, [start]
            while stack:
                for w in adj[stack.pop()]:
                    if w not in seen:
                        seen.add(w)
                        stack.append(w)
            if len(seen) == len(adj):
                lengths.add(len(edges))
    return lengths


def missing(n, chords):
    found = cycle_lengths(n, chords)
    return [l for l in range(3, n + 1) if l not in found]


def family(n):
    return [(0, 2), (0, n - 7), (1, 13), (3, n - 6), (4, 31), (n - 8, n - 5)]


if __name__ == "__main__":
    ok = True
    for n in range(41, 68):
        spectrum = cycle_lengths(n, family(n))
        expected = set(range(3, 33)) | set(range(n - 34, n + 1))
        if missing(n, family(n)) or spectrum != expected:
            ok = False
            print(f"family F_{n}: FAIL")
    print("F_n pancyclic, spectrum [3,32] u [n-34,n], for every 41 <= n <= 67:", ok)
    print("F_68 missing lengths:", missing(68, family(68)))
    witnesses = {
        "n=38, 5 chords": (38, [(0, 2), (0, 18), (1, 12), (3, 19), (17, 20)]),
        "n=39, 5 chords": (39, [(0, 2), (0, 18), (1, 12), (3, 19), (17, 20)]),
        "n=40, 5 chords": (40, [(0, 5), (1, 5), (2, 30), (3, 10), (4, 11)]),
        "n=41, 6 chords": (41, [(4, 13), (28, 30), (12, 26), (17, 31), (12, 29), (24, 27)]),
        "n=56, 6 chords": (56, [(0, 2), (0, 53), (1, 39), (20, 39), (39, 48), (48, 53)]),
        "n=67, 6 chords, second witness": (67, [(0, 27), (18, 30), (28, 37), (29, 37), (31, 38), (32, 39)]),
    }
    for name, (n, chords) in witnesses.items():
        m = missing(n, chords)
        print(f"{name}: {'pancyclic' if not m else 'MISSING ' + str(m)}")
