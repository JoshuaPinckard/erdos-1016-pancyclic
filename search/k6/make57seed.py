import networkx as nx
def lengths(n, chords):
    G = nx.cycle_graph(n); G.add_edges_from(chords)
    return {len(c) for c in nx.simple_cycles(G)}
def insert_vertex(n, chords, pos):
    def sh(v): return v + 1 if v > pos else v
    return n + 1, [tuple(sorted((sh(a), sh(b)))) for a, b in chords]
n0 = 56
chords0 = [(0,2),(0,53),(1,39),(20,39),(39,48),(48,53)]
best = None
for pos in range(n0):
    n1, c1 = insert_vertex(n0, chords0, pos)
    L = lengths(n1, c1)
    missing = sorted(set(range(3, n1 + 1)) - L)
    if best is None or len(missing) < best[0]:
        best = (len(missing), pos, c1, missing)
print("best insertion position:", best[1], "missing_count:", best[0], "missing:", best[3])
print("chords:", best[2])
