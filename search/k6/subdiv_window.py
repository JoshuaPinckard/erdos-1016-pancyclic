"""For a given base graph (n0 vertices, k chords), test every Hamilton-cycle edge (i,i+1) as the
flexible 'uv' edge of the subdivision lemma: a witness at n0 extends, with the SAME chords, to
every n in [n0, 2*n0 - a] by inserting (n-n0) extra vertices into that one edge, PROVIDED
(1) every length in [3, n0-1] is achieved by some simple cycle NOT using edge uv, and
(2) the lengths achieved by simple cycles that DO use edge uv form a contiguous interval [a, n0]
    (a cycle of length L through uv becomes length L+(n-n0) after subdividing uv by (n-n0) vertices).
Reports, for each candidate uv edge, whether (1) holds, and if so the best interval [a,n0] and the
resulting reachable range [n0, 2*n0-a].
Usage: python subdiv_window.py n0 "(a,b) (c,d) ..."
"""
import sys
import networkx as nx

def main():
    n0 = int(sys.argv[1])
    chords = [tuple(map(int, s.strip("()").split(","))) for s in sys.argv[2].split()]
    G = nx.cycle_graph(n0)
    G.add_edges_from(chords)
    cycles = list(nx.simple_cycles(G))
    print(f"n0={n0} k={len(chords)} chords={chords}")
    print(f"total simple cycles enumerated: {len(cycles)}")
    lengths_all = sorted({len(c) for c in cycles})
    missing_all = sorted(set(range(3, n0 + 1)) - set(lengths_all))
    print(f"lengths present at n0 itself: {lengths_all}")
    print(f"missing at n0 itself (should be empty if base is pancyclic): {missing_all}")

    def uses_edge(cycle_nodes, u, v):
        # cycle_nodes is a list of vertices in cyclic order (as returned by simple_cycles);
        # edge u-v is used iff u,v are adjacent in that cyclic order
        m = len(cycle_nodes)
        for i in range(m):
            a, b = cycle_nodes[i], cycle_nodes[(i + 1) % m]
            if {a, b} == {u, v}:
                return True
        return False

    best = None  # (window_size, uv, a, n0)
    results = []
    for i in range(n0):
        u, v = i, (i + 1) % n0
        if (u, v) in [tuple(sorted(c)) for c in chords] or tuple(sorted((u, v))) in [tuple(sorted(c)) for c in chords]:
            continue  # not a Hamilton-cycle edge (shouldn't happen for consecutive i,i+1, but guard)
        without = set()
        through = set()
        for c in cycles:
            L = len(c)
            if uses_edge(c, u, v):
                through.add(L)
            else:
                without.add(L)
        need = set(range(3, n0))  # 3..n0-1
        covers_short = need <= without
        if not covers_short:
            missing_short = sorted(need - without)
        else:
            missing_short = []
        if through:
            a = min(through)
            b = max(through)
            contiguous = (b - a + 1) == len(through)
            reach = 2 * n0 - a
        else:
            a = b = None
            contiguous = False
            reach = n0
        results.append((u, v, covers_short, missing_short, sorted(through), a, b, contiguous, reach))
        if covers_short and contiguous and (best is None or reach > best[0]):
            best = (reach, (u, v), a)

    print("\nper-edge analysis (u,v, short-range covered w/o uv?, missing-if-not, through-uv lengths contiguous?, a=min through-uv length, reach=2*n0-a):")
    for u, v, covers_short, missing_short, through, a, b, contiguous, reach in results:
        flag = "OK" if (covers_short and contiguous) else "no"
        print(f"  uv=({u},{v}) covers_short={covers_short} missing_short={missing_short[:8]}{'...' if len(missing_short)>8 else ''} through={through} contiguous={contiguous} a={a} reach={reach if covers_short and contiguous else '-'} [{flag}]")

    if best:
        reach, uv, a = best
        print(f"\nBEST: uv={uv}, a={a}, reachable range = [{n0}, {reach}] using the SAME {len(chords)} chords for every n in that range (subdivide uv).")
    else:
        print("\nNo Hamilton-cycle edge gives a valid subdivision window (short range not fully covered without it, or through-range not contiguous, for every candidate edge).")

if __name__ == "__main__":
    main()
