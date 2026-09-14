import networkx as nx, itertools
from localsearch import search
from extend import insert_vertex, canon, pancyclic, lengths
w37=[(27,30),(9,29),(0,9),(28,36),(0,35)]
print("37 ok:", pancyclic(37,w37), "missing38-lengths per insertion:")
for pos in range(37):
    n1,c1=insert_vertex(37,w37,pos)
    miss=set(range(3,39))-lengths(38,c1)
    print(pos, sorted(miss))
# two-step: insert + move one endpoint by +-1..2
best=None
for pos in range(37):
    n1,c1=insert_vertex(37,w37,pos)
    for i in range(5):
        for da in (-2,-1,0,1,2):
            for db in (-2,-1,0,1,2):
                c2=list(c1); a,b=c2[i]; a=(a+da)%38; b=(b+db)%38
                if a==b or (b-a)%38 in (1,37): continue
                c2[i]=tuple(sorted((a,b)))
                if len(set(c2))<5: continue
                m=len(set(range(3,39))-lengths(38,c2))
                if best is None or m<best[0]: best=(m,c2)
                if m==0: print("38 WITNESS", c2)
print("best missing count after insert+shift:", best)
