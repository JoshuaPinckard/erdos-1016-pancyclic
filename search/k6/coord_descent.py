"""Greedy coordinate descent: repeatedly pick the chord slot whose full replacement (trying every
possible chord for that slot, holding the other 5 fixed) most reduces the missing-length count;
apply it; repeat until no single-slot replacement helps or missing=0. Much more systematic than
random hill-climbing for closing the last few gaps.
Usage: python coord_descent.py n "(a,b) (c,d) ..." [max_rounds]
"""
import sys, networkx as nx

def lengths(n, chords):
    G = nx.cycle_graph(n); G.add_edges_from(chords)
    return {len(c) for c in nx.simple_cycles(G)}

def missing_count(n, chords):
    return len(set(range(3, n + 1)) - lengths(n, chords))

def main():
    n = int(sys.argv[1])
    chords = [tuple(map(int, s.strip("()").split(","))) for s in sys.argv[2].split()]
    max_rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    k = len(chords)
    cur = list(chords)
    cur_mc = missing_count(n, cur)
    print(f"start n={n} k={k} missing_count={cur_mc}", flush=True)
    for rnd in range(max_rounds):
        improved = False
        for slot in range(k):
            others = set(tuple(sorted(c)) for i, c in enumerate(cur) if i != slot)
            best_e, best_mc = cur[slot], cur_mc
            for a in range(n):
                for b in range(a + 2, n):
                    if (b - a) % n in (1, n - 1):
                        continue
                    e = (a, b)
                    if e in others:
                        continue
                    trial = list(cur); trial[slot] = e
                    mc = missing_count(n, trial)
                    if mc < best_mc:
                        best_mc, best_e = mc, e
            if best_mc < cur_mc:
                cur[slot] = best_e
                cur_mc = best_mc
                improved = True
                print(f"  round {rnd} slot {slot}: missing_count -> {cur_mc}  chords={cur}", flush=True)
                if cur_mc == 0:
                    break
        if cur_mc == 0 or not improved:
            break
    if cur_mc == 0:
        print(f"WITNESS n={n} k={k} : " + " ".join(f"({a},{b})" for a, b in cur))
    else:
        print(f"STALLED n={n} k={k} missing_count={cur_mc} chords={cur} missing={sorted(set(range(3,n+1))-lengths(n,cur))}")

if __name__ == "__main__":
    main()
