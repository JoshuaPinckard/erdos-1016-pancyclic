"""Targeted hill-climb that starts EXACTLY from a given seed (no initial random perturbation,
unlike localsearch.py's restart loop) and tries small endpoint moves to eliminate the last few
missing lengths. Meant for the GKW-6 base construction, which is missing only length 5 for most
n in [37,69]. Usage: python patch5.py n seconds "(a,b) (c,d) ..."
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
    chords = [tuple(map(int, s.strip("()").split(","))) for s in sys.argv[3].split()]
    k = len(chords)
    cur = list(chords)
    ms = missing_set(n, cur)
    print(f"start n={n} k={k} missing={ms}", flush=True)
    best = (len(ms), list(cur))
    t0 = time.time()
    stale = 0
    while len(ms) > 0 and time.time() - t0 < secs:
        cand = list(cur)
        i = random.randrange(k)
        a, b = cand[i]
        move = random.random()
        if move < 0.85:
            d = random.choice([-3, -2, -1, 1, 2, 3])
            if random.random() < 0.5:
                a = (a + d) % n
            else:
                b = (b + d) % n
            cand[i] = tuple(sorted((a, b)))
        else:
            cand[i] = random_chord(n)
        if not valid(n, cand):
            continue
        cms = missing_set(n, cand)
        if len(cms) <= len(ms) or random.random() < 0.03:
            if len(cms) < len(ms):
                stale = 0
                print(f"  improved: missing={cms} chords={cand}", flush=True)
            else:
                stale += 1
            cur, ms = cand, cms
            if len(ms) < best[0]:
                best = (len(ms), list(cur))
        else:
            stale += 1
        if stale > 3000:
            # restart from the original seed, not from scratch, to keep exploiting locality
            cur = list(chords); ms = missing_set(n, cur); stale = 0
    if not ms:
        print(f"WITNESS n={n} k={k} : " + " ".join(f"({a},{b})" for a, b in cur))
    else:
        print(f"NOTFOUND n={n} k={k} in {secs}s, best missing={best[0]} chords={best[1]}")

if __name__ == "__main__":
    main()
