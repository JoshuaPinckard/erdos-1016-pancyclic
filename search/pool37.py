import subprocess, sys, re, random
from localsearch import search, missing, lengths
from extend import insert_vertex, canon, pancyclic
random.seed(1)
pool=set()
import time
t0=time.time()
while time.time()-t0 < 240:
    w = search(37,5,60)
    if w: pool.add(canon(37,w)); print("37 witness", canon(37,w), flush=True)
print("pool size", len(pool))
# try single insertion to 38
found=False
for cs in pool:
    for pos in range(37):
        n1,c1 = insert_vertex(37,list(cs),pos)
        if pancyclic(n1,c1): print("38 WITNESS by insertion", c1); found=True
print("insertion found:", found)
# seeded local search at 38 from each pool member
for cs in pool:
    w = search(38,5,60,seed=list(cs))
    if w: print("38 WITNESS seeded", w); break
else:
    print("no 38 witness from seeds")
