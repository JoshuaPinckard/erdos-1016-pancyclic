"""Strict-improvement hill-climb (never accepts a worse or equal missing-count except a small
occasional sideways move to escape plateaus), seeded from a given chord set, for one n.
Usage: python strict_climb.py n seconds "(a,b) (c,d) ..."
"""
import sys, random, time, networkx as nx

def lengths(n, chords):
    G = nx.cycle_graph(n); G.add_edges_from(chords)
    return {len(c) for c in nx.simple_cycles(G)}

def missing_set(n, chords):
    return sorted(set(range(3, n + 1)) - lengths(n, chords))

def valid(n, chords):
    s = set()
    for a, b in chords:
        if a == b or (b - a) % n in (1, n - 1): return False
        e = tuple(sorted((a, b)))
        if e in s: return False
        s.add(e)
    return True

def random_chord(n):
    while True:
        a, b = random.randrange(n), random.randrange(n)
        if a != b and (b - a) % n not in (1, n - 1): return tuple(sorted((a, b)))

def main():
    n = int(sys.argv[1]); secs = float(sys.argv[2])
    seed = [tuple(map(int, s.strip("()").split(","))) for s in sys.argv[3].split()]
    k = len(seed)
    cur = list(seed); ms = missing_set(n, cur)
    best = (len(ms), list(cur))
    print(f"start n={n} k={k} missing_count={len(ms)}", flush=True)
    t0 = time.time(); stale = 0
    while ms and time.time() - t0 < secs:
        cand = list(cur); i = random.randrange(k); a, b = cand[i]
        move = random.random()
        if move < 0.6:
            d = random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
            if random.random() < 0.5: a = (a + d) % n
            else: b = (b + d) % n
            cand[i] = tuple(sorted((a, b)))
        elif move < 0.85:
            cand[i] = random_chord(n)
        else:
            # move two chords at once
            j = random.randrange(k)
            for idx in (i, j):
                aa, bb = cand[idx]
                d = random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
                if random.random() < 0.5: aa = (aa + d) % n
                else: bb = (bb + d) % n
                cand[idx] = tuple(sorted((aa, bb)))
        if not valid(n, cand): continue
        cms = missing_set(n, cand)
        if len(cms) < len(ms):
            cur, ms, stale = cand, cms, 0
            if len(ms) < best[0]:
                best = (len(ms), list(cur))
                print(f"  improved: missing_count={len(ms)} missing={ms[:12]} chords={cur}", flush=True)
        else:
            stale += 1
            if stale > 200 and random.random() < 0.15:
                cur, ms = cand, cms  # rare sideways/backward move to escape plateau
                stale = 0
            if stale > 4000:
                cur, ms = list(best[1]), missing_set(n, best[1]); stale = 0
    if not ms:
        print(f"WITNESS n={n} k={k} : " + " ".join(f"({a},{b})" for a, b in cur))
    else:
        print(f"NOTFOUND n={n} k={k} in {secs}s, best missing_count={best[0]} missing={missing_set(n, best[1])} chords={best[1]}")

if __name__ == "__main__":
    main()
