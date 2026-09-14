"""Erdos problem #617 (Erdos-Gyarfas 1999): r-colour the edges of K_{r^2+1}; must some K_{r+1} miss a colour?
CNF: SAT <=> a counterexample exists (an r-colouring of K_{r^2+1} in which every K_{r+1} sees all r colours).
Usage: python gen617.py r > k617_r.cnf
"""
import sys, itertools
r = int(sys.argv[1]); N = r*r + 1
V = range(N)
edges = list(itertools.combinations(V, 2))
eid = {e: i for i, e in enumerate(edges)}
def var(e, c): return eid[e] * r + c + 1
clauses = []
for e in edges:
    clauses.append([var(e, c) for c in range(r)])
    for c1 in range(r):
        for c2 in range(c1 + 1, r):
            clauses.append([-var(e, c1), -var(e, c2)])
for S in itertools.combinations(V, r + 1):
    es = list(itertools.combinations(S, 2))
    for c in range(r):
        clauses.append([var(e, c) for e in es])
# symmetry breaking on colours: edge (0,1) has colour 0; edge (0,2) has colour 0 or 1;
# more generally colour of edge (0,j) is at most j-1 (first-occurrence ordering along the star at 0)
for j in range(1, N):
    for c in range(min(j, r), r):
        clauses.append([-var((0, j), c)])
nv = len(edges) * r
out = sys.stdout
out.write(f"p cnf {nv} {len(clauses)}\n")
out.write("\n".join(" ".join(map(str, cl)) + " 0" for cl in clauses) + "\n")
sys.stderr.write(f"r={r} N={N} vars={nv} clauses={len(clauses)}\n")
