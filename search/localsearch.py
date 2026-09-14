"""Randomised local search for pancyclic C_n + k chords (upper bounds on h(n)).
Usage: python localsearch.py n k [seconds] [seed_chords]
Score = number of missing cycle lengths in 3..n.  Moves: shift one chord endpoint by a small
amount, or replace one chord at random.  Restarts from seed / random when stuck.
"""
import sys, random, time, networkx as nx

def lengths(n, chords):
    G = nx.cycle_graph(n); G.add_edges_from(chords)
    return {len(c) for c in nx.simple_cycles(G)}

def missing(n, chords):
    return len(set(range(3, n + 1)) - lengths(n, chords))

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

def search(n, k, seconds, seed=None):
    t0 = time.time(); best_overall = None
    while time.time() - t0 < seconds:
        cur = list(seed) if seed else [random_chord(n) for _ in range(k)]
        if seed:  # perturb the seed a little
            i = random.randrange(k); cur[i] = random_chord(n)
        if not valid(n, cur): continue
        sc = missing(n, cur)
        stale = 0
        while sc > 0 and stale < 400 and time.time() - t0 < seconds:
            cand = list(cur); i = random.randrange(k)
            if random.random() < 0.7:
                a, b = cand[i]; d = random.choice([-3, -2, -1, 1, 2, 3])
                if random.random() < 0.5: a = (a + d) % n
                else: b = (b + d) % n
                cand[i] = tuple(sorted((a, b)))
            else:
                cand[i] = random_chord(n)
            if not valid(n, cand): continue
            s2 = missing(n, cand)
            if s2 <= sc:
                stale = 0 if s2 < sc else stale + 1
                cur, sc = cand, s2
            else:
                stale += 1
        if best_overall is None or sc < best_overall[0]: best_overall = (sc, cur)
        if sc == 0:
            return cur
    return None if best_overall[0] > 0 else best_overall[1]

if __name__ == "__main__":
    n, k = int(sys.argv[1]), int(sys.argv[2])
    secs = float(sys.argv[3]) if len(sys.argv) > 3 else 60
    seed = [tuple(map(int, s.strip("()").split(","))) for s in sys.argv[4].split()] if len(sys.argv) > 4 else None
    w = search(n, k, secs, seed)
    if w: print(f"WITNESS n={n} k={k} : " + " ".join(f"({a},{b})" for a, b in w))
    else: print(f"NOTFOUND n={n} k={k} in {secs}s")
