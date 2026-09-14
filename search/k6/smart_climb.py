"""Combined climb: from a witness at n, try every single-vertex insertion (n candidates), take the
few with lowest missing-count, and for each try to close the remaining gap with a capped
coordinate-descent repair (try every replacement for each chord in turn, a few rounds). If any
candidate reaches missing=0, advance n and repeat. Stops and reports the stall point (best missing
count/set found among the tried candidates) when no candidate closes.
Usage: python smart_climb.py n0 "(a,b) ..." nmax [top_k] [cd_rounds]
"""
import sys, networkx as nx

def lengths(n, chords):
    G = nx.cycle_graph(n); G.add_edges_from(chords)
    return {len(c) for c in nx.simple_cycles(G)}

def missing_set(n, chords):
    return sorted(set(range(3, n + 1)) - lengths(n, chords))

def insert_vertex(n, chords, pos):
    def sh(v): return v + 1 if v > pos else v
    return n + 1, [tuple(sorted((sh(a), sh(b)))) for a, b in chords]

def coord_descent(n, chords, max_rounds):
    k = len(chords)
    cur = list(chords)
    cur_ms = missing_set(n, cur)
    for rnd in range(max_rounds):
        improved = False
        for slot in range(k):
            others = set(tuple(sorted(c)) for i, c in enumerate(cur) if i != slot)
            best_e, best_ms = cur[slot], cur_ms
            for a in range(n):
                for b in range(a + 2, n):
                    if (b - a) % n in (1, n - 1):
                        continue
                    e = (a, b)
                    if e in others:
                        continue
                    trial = list(cur); trial[slot] = e
                    ms = missing_set(n, trial)
                    if len(ms) < len(best_ms):
                        best_ms, best_e = ms, e
            if len(best_ms) < len(cur_ms):
                cur[slot] = best_e
                cur_ms = best_ms
                improved = True
                if not cur_ms:
                    return cur, cur_ms
        if not improved:
            break
    return cur, cur_ms

def main():
    n = int(sys.argv[1])
    chords = [tuple(map(int, s.strip("()").split(","))) for s in sys.argv[2].split()]
    nmax = int(sys.argv[3])
    top_k = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    cd_rounds = int(sys.argv[5]) if len(sys.argv) > 5 else 2
    print(f"start n={n} chords={chords}", flush=True)
    while n < nmax:
        cands = []
        for pos in range(n):
            n1, c1 = insert_vertex(n, chords, pos)
            ms = missing_set(n1, c1)
            cands.append((len(ms), pos, c1, ms))
        cands.sort(key=lambda t: t[0])
        n1 = n + 1
        solved = None
        tried_best = None
        for mc, pos, c1, ms in cands[:top_k]:
            if mc == 0:
                solved = (c1, ms)
                break
            fixed, fms = coord_descent(n1, c1, cd_rounds)
            if tried_best is None or len(fms) < len(tried_best[1]):
                tried_best = (fixed, fms)
            if not fms:
                solved = (fixed, fms)
                break
        if solved:
            chords, ms = solved
            n = n1
            print(f"n={n}: WITNESS {chords}", flush=True)
        else:
            print(f"n={n1}: STALL best_missing={tried_best[1]} chords={tried_best[0]}", flush=True)
            break
    print(f"FINAL largest n reached: {n}", flush=True)
    print(f"FINAL chords: {chords}", flush=True)

if __name__ == "__main__":
    main()
