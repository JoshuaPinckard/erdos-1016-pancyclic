import re
def canon(w,n=24):
    ans=[]
    for refl in (False,True):
        for t in range(n):
            z=[]
            for a,b in w:
                if refl: a,b=n-a,n-b
                a=(a+t)%n; b=(b+t)%n
                z.append((min(a,b),max(a,b)))
            ans.append(tuple(sorted(z)))
    return min(ans)
ws=[]
for x in open('indep-n24.log'):
    if x.startswith('WITNESS'):
        ws.append([(int(a),int(b)) for a,b in re.findall(r'\((\d+),(\d+)\)',x)])
print('raw',len(ws),'dihedral',len({canon(w) for w in ws}))
for x in sorted({canon(w) for w in ws}): print(x)
