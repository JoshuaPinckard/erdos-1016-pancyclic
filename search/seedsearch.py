"""Structured search for k-chord pancyclic graphs on n vertices: seed from a known extremal graph on
n0 vertices by scaling its gaps to sum n (optionally adding one chord), then hill-climb with
endpoint moves.  Usage: python seedsearch.py n k seconds"""
import sys, random, time, itertools, networkx as nx
from localsearch import lengths, missing, valid, random_chord
n=int(sys.argv[1]); k=int(sys.argv[2]); secs=float(sys.argv[3]); random.seed(int(time.time()))
seeds40=[[(0,2),(1,5),(1,7),(3,34),(24,39)],[(0,2),(0,33),(1,13),(3,34),(32,35)],[(0,7),(1,8),(2,10),(2,11),(9,21)],[(0,4),(0,5),(1,34),(2,35),(3,15)]]
def scale(chords, n0, n):
    pts=sorted(set(v for c in chords for v in c)); gaps=[(pts[(i+1)%len(pts)]-pts[i])%n0 for i in range(len(pts))]
    # scale gaps >2 proportionally so total = n
    big=[i for i,g in enumerate(gaps) if g>2]; small=sum(g for g in gaps if g<=2); bigsum=sum(gaps[i] for i in big)
    target=n-small; ng=list(gaps)
    for i in big: ng[i]=max(3, round(gaps[i]*target/bigsum))
    diff=n-sum(ng); ng[big[0]]+=diff
    newpos={}; p=0
    for i,v in enumerate(pts): newpos[v]=p; p+=ng[i]
    return [tuple(sorted((newpos[a],newpos[b]))) for a,b in chords]
def climb(cur, deadline):
    sc=missing(n,cur); best=(sc,list(cur))
    while sc>0 and time.time()<deadline:
        cand=list(cur); i=random.randrange(k); a,b=cand[i]
        d=random.choice([-4,-3,-2,-1,1,2,3,4])
        if random.random()<0.5: a=(a+d)%n
        else: b=(b+d)%n
        cand[i]=tuple(sorted((a,b)))
        if not valid(n,cand): continue
        s2=missing(n,cand)
        if s2<=sc or random.random()<0.02:
            cur,sc=cand,s2
            if sc<best[0]: best=(sc,list(cur))
    return best
t0=time.time(); overall=None
while time.time()-t0<secs:
    s=random.choice(seeds40); ch=scale(s,40,n)
    while len(ch)<k: ch.append(random_chord(n))
    if not valid(n,ch): continue
    b=climb(ch, min(t0+secs, time.time()+30))
    if overall is None or b[0]<overall[0]: overall=b; print("best so far missing", b[0], b[1], flush=True)
    if b[0]==0: print("WITNESS n=%d k=%d : "%(n,k)+" ".join("(%d,%d)"%c for c in b[1])); break
else:
    print("NOTFOUND n=%d k=%d best missing %d"%(n,k,overall[0] if overall else -1))
