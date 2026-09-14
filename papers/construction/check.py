"""Cycle-space verifier and CSV runner for construction.py."""
from __future__ import annotations
import csv
import os
import sys


def basis(n, chords):
    # Edge index is an integer bit; basis element is Hamilton path plus chord.
    def eid(a, b):
        a, b = sorted((a % n, b % n)); return (a, b)
    edges = [eid(i, (i + 1) % n) for i in range(n)] + [eid(a, b) for a, b in chords]
    index = {e: i for i, e in enumerate(edges)}
    out = []
    ham = 0
    for i in range(n):
        ham |= 1 << index[eid(i, (i + 1) % n)]
    out.append(ham)
    for a, b in chords:
        x = 1 << index[eid(a, b)]
        i = a
        while i != b:
            j = (i + 1) % n
            x ^= 1 << index[eid(i, j)]; i = j
        out.append(x)
    return out, edges


def cycle_length(x, n, edges):
    deg = [0] * n; chosen = []
    while x:
        bit = x & -x; i = bit.bit_length() - 1; x ^= bit
        a, b = edges[i]; deg[a] += 1; deg[b] += 1
        if deg[a] > 2 or deg[b] > 2:
            return None
        chosen.append((a, b))
    if not chosen or any(d not in (0, 2) for d in deg):
        return None
    seen = {chosen[0][0]}; stack = [chosen[0][0]]
    adj = [[] for _ in range(n)]
    for a, b in chosen: adj[a].append(b); adj[b].append(a)
    while stack:
        v = stack.pop()
        for w in adj[v]:
            if w not in seen: seen.add(w); stack.append(w)
    vertices = {v for e in chosen for v in e}
    return len(chosen) if len(seen) == len(vertices) else None


def spectrum(n, chords):
    bs, edge_list = basis(n, chords); result = set(); total = 1 << len(bs)
    for mask in range(1, total):
        x = 0
        for i, b in enumerate(bs):
            if mask >> i & 1: x ^= b
        l = cycle_length(x, n, edge_list)
        if l is not None: result.add(l)
    return result


def run(lo=3, hi=2000, output=None, sampled=False):
    from construction import construct
    output = output or os.path.join(os.path.dirname(__file__), "construction_u.csv")
    with open(output, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["n", "k_construction", "verified"])
        ns = list(range(lo, min(hi, 300) + 1))
        if sampled and hi > 300:
            ns += [n for n in range(350, hi + 1, 50)]
            # first increases in the executable chord count (measured by
            # construction output); include them even if not on the grid.
            counts = {}
            for n in range(3, hi + 1):
                counts.setdefault(len(construct(n)), n)
            ns += list(counts.values())
            ns = sorted(set(ns))
        else:
            ns = range(lo, hi + 1)
        for n in ns:
            c = construct(n); ok = len(spectrum(n, c)) == n - 2
            w.writerow([n, len(c), "yes" if ok else "no"]); f.flush()


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 3,
        int(sys.argv[2]) if len(sys.argv) > 2 else 2000,
        sys.argv[3] if len(sys.argv) > 3 else None,
        bool(len(sys.argv) > 4 and sys.argv[4] == 'sampled'))
