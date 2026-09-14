"""Independent n=25,k=4 exhaustive check using the three triangle normal forms."""
from itertools import combinations
from check import spectrum

def chords(n):
    return [(a,b) for a in range(n) for b in range(a+2,n) if not (a==0 and b==n-1)]
def sp(n,e):
    d=min(e[1]-e[0],n-(e[1]-e[0])); return d
def run():
    n=25; allc=chords(n); nos=[e for e in allc if sp(n,e)!=2]
    tested=0
    def test(fixed,cand):
        nonlocal tested
        for x in combinations([e for e in cand if e not in fixed],4-len(fixed)):
            tested+=1; w=fixed+list(x)
            if len(spectrum(n,w))==n-2: print('WITNESS',w); return True
        return False
    # A: fixed span-2 chord.
    if test([(0,2)],allc): return
    # B: fixed (0,b),(1,b), with no span-2 chord.
    for b in range(3,n-1):
        if test([(0,b),(1,b)],nos): return
    # C: fixed chord triangle, with no span-2 chord.
    for b in range(3,n-4):
        for c in range(b+3,n-2):
            f=[(0,b),(b,c),(0,c)]
            if all(e in nos for e in f) and test(f,nos): return
    print('NONE tested',tested)
if __name__=='__main__': run()
