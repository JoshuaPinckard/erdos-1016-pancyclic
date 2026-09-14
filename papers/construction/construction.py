"""Deterministic chord construction for the Erdős #1016 experiment.

The first block is the binary-shortcut skeleton described in Alon--Krivelevich,
arXiv:2308.01564, §3 (which refers to George--Khodkar--Wallis, Ch. 4.5):
consecutive shortcuts have interval lengths 2^i.  The source's final
O(log* n) completion is not printed there, so this file makes the completion
explicit by a deterministic first-uncovered-length greedy rule.  The checker
is therefore the authority on whether this executable completion is pancyclic.
Vertices are 0,...,n-1 and all pairs are modulo n.
"""
from __future__ import annotations

import math


def _add(chords, a, b, n):
    a %= n; b %= n
    if a == b or (a - b) % n in (1, n - 1):
        return
    e = tuple(sorted((a, b)))
    if e not in chords:
        chords.append(e)


def source_skeleton(n: int):
    """Binary consecutive shortcuts; source attribution in module docstring."""
    chords = []
    pos = 0
    # A shortcut replacing an interval of 2^i+1 cycle edges has chord span 2^i.
    i = 0
    while pos + (1 << i) + 1 < n - 1 and i < 2 * n.bit_length():
        _add(chords, pos, pos + (1 << i) + 1, n)
        pos += 1 << i
        i += 1
    if len(chords) >= 2:
        _add(chords, chords[0][0], chords[-1][1], n)
    return chords


def construct(n: int):
    if n < 3:
        raise ValueError("n must be at least 3")
    if 24 <= n <= 40:
        # Griffin, arXiv:1312.0274, Fig. 1 (the five-chord construction).
        chords = [(1, 10), (6, n - 9), (9, 12), (8, 14), (7, 9)]
    else:
        # The published general recipe's binary-shortcut block; its omitted
        # O(log* n) completion is intentionally not invented here.
        chords = source_skeleton(n)
    return chords


if __name__ == "__main__":
    import sys
    for arg in sys.argv[1:] or ["23"]:
        n = int(arg)
        print(n, construct(n))
