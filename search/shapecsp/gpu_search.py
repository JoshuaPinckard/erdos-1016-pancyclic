"""Bounded CuPy search over canonical shapes; exact colex rank coverage in JSONL.

Run from any directory: python gpu_search.py --output <new directory>.
Each shape uses a coprime affine permutation of all legal composition ranks.
Only its recorded prefix is searched. A miss is not a non-existence proof.
"""
from __future__ import annotations
import argparse
import importlib.util
import hashlib
import json
import math
import random
import time
from pathlib import Path
import numpy as np
import cupy as cp
import psutil
import shapes as S
import bound as B

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('independent_verify', HERE.parent / 'verify.py')
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)

CUDA = r'''
typedef unsigned long long U;
extern "C" __global__ void scan(int n, int stride_b, int stride_f,
 const int* bs, const int* nf, const int* lows, const int* masks,
 const int* cs, const U* choose, const U* totals, const U* starts,
 const U* steps, U count, int* nhit, U* hits, int maxhit,
 int debug, int* arcs_out, int* flags) {
 int s=blockIdx.y, b=bs[s];
 U t=(U)blockIdx.x*blockDim.x+threadIdx.x;
 if(t>=count || t>=totals[s]) return;
 U rank=(starts[s]+t*steps[s])%totals[s], remrank=rank;
 int a[MAX_B], cuts[MAX_B];
 int rem=n;
 for(int j=0;j<b;j++) rem-=lows[s*stride_b+j];
 int m=rem+b-1, hi=m-1;
 for(int j=b-1;j>=1;j--) {
   int lo=j-1, h=hi;
   while(lo<h) {int mid=(lo+h+1)/2;
     if(choose[mid*stride_b+j]<=remrank) lo=mid; else h=mid-1;}
   cuts[j-1]=lo; remrank-=choose[lo*stride_b+j]; hi=lo-1;
 }
 int prev=-1;
 for(int j=0;j<b-1;j++) {a[j]=cuts[j]-prev-1+lows[s*stride_b+j]; prev=cuts[j];}
 a[b-1]=m-prev-1+lows[s*stride_b+b-1];
 U cov0=0,cov1=0;
 for(int f=0;f<nf[s];f++) {
   int mask=masks[s*stride_f+f], len=cs[s*stride_f+f];
   while(mask) {int j=__ffs(mask)-1; len+=a[j]; mask&=mask-1;}
   if(len>=3 && len<=n) {if(len<64) cov0|=1ULL<<len; else cov1|=1ULL<<(len-64);}
 }
 U need0=n>=63 ? (~7ULL) : (((1ULL<<(n+1))-1)&~7ULL);
 U need1=n>=64 ? ((1ULL<<(n-63))-1) : 0;
 int sat=((cov0&need0)==need0 && (cov1&need1)==need1);
 if(debug) {flags[t]=sat; for(int j=0;j<b;j++) arcs_out[t*stride_b+j]=a[j];}
 if(sat) {int slot=atomicAdd(nhit,1); if(slot<maxhit) {hits[slot*2]=s; hits[slot*2+1]=rank;}}
}
'''


def unrank(rank, n, lows):
    b=len(lows); m=n-sum(lows)+b-1; cuts=[0]*(b-1); hi=m-1
    for j in range(b-1,0,-1):
        x=hi
        while math.comb(x,j)>rank: x-=1
        cuts[j-1]=x; rank-=math.comb(x,j); hi=x-1
    points=[-1]+cuts+[m]
    return [points[i+1]-points[i]-1+lows[i] for i in range(b)]


def rank_arcs(arcs,lows):
    cut=-1; rank=0
    for j,(a,low) in enumerate(zip(arcs[:-1],lows),1):
        cut+=a-low+1; rank+=math.comb(cut,j)
    return rank


def materialise(ch,arcs):
    points=[0]
    for a in arcs[:-1]: points.append(points[-1]+a)
    return sorted(tuple(sorted((points[u],points[v]))) for u,v in ch)


def canonical_witness(n,ch):
    pts=sorted({v for e in ch for v in e}); b=len(pts)
    edges=[(pts.index(u),pts.index(v)) for u,v in ch]
    raw=[(pts[(i+1)%b]-pts[i])%n for i in range(b)]
    canonical=S.canon(b,edges)
    for g in S._dihedral(b):
        img=tuple(sorted(tuple(sorted((g[u],g[v]))) for u,v in edges))
        if img!=canonical: continue
        arcs=[0]*b
        for i,a in enumerate(raw):
            j=g[i] if g[(i+1)%b]==(g[i]+1)%b else g[(i+1)%b]
            arcs[j]=a
        return record(b,canonical),arcs


def record(b,ch):
    forms=sorted(set(S.cycle_forms(b,ch))); iv,lows=B.intervals(b,ch,forms)
    return dict(b=b,chords=ch,forms=forms,lows=lows,iv=iv)


class Engine:
    def __init__(self,max_b,max_n,max_f):
        if not 3<=max_n<=126 or not 2<=max_b<=max_n:
            raise ValueError('unsupported dimensions')
        self.b=max_b; self.f=max_f
        self.done=cp.cuda.Event(block=True,disable_timing=True)
        self.kernel=cp.RawKernel(CUDA.replace('MAX_B',str(max_b)),'scan')
        table=np.zeros((max_n+1,max_b),dtype=np.uint64)
        for x in range(max_n+1):
            for j in range(max_b):
                v=math.comb(x,j)
                if v>=2**64: raise ValueError('binomial overflow')
                table[x,j]=v
        self.table=cp.asarray(table)
        self.max_n=max_n

    def run(self,n,records,starts,steps,count,debug=False):
        if not records or n>self.max_n or n<3 or count<1:
            raise ValueError('invalid launch')
        bs=np.array([d['b'] for d in records],np.int32)
        if max(bs)>self.b or (debug and len(records)!=1): raise ValueError('array capacity')
        nf=np.array([len(d['forms']) for d in records],np.int32)
        if max(nf)>self.f: raise ValueError('forms capacity')
        lows=np.zeros((len(bs),self.b),np.int32)
        masks=np.zeros((len(bs),self.f),np.int32); cs=masks.copy(); totals=[]
        for s,d in enumerate(records):
            if sum(d['lows'])>n: raise ValueError('infeasible composition')
            lows[s,:bs[s]]=d['lows']
            masks[s,:nf[s]]=[x[0] for x in d['forms']]
            cs[s,:nf[s]]=[x[1] for x in d['forms']]
            total=math.comb(n-sum(d['lows'])+d['b']-1,d['b']-1); totals.append(total)
            if not 0<=starts[s]<total or steps[s]<1 or math.gcd(steps[s],total)!=1:
                raise ValueError('invalid permutation')
            if starts[s]+(min(count,total)-1)*steps[s]>=2**64: raise ValueError('rank overflow')
        arrays=[cp.asarray(x) for x in (bs,nf,lows,masks,cs)]
        rr=[cp.asarray(x,dtype=cp.uint64) for x in (totals,starts,steps)]
        nhit=cp.zeros(1,cp.int32); hits=cp.zeros((1024,2),cp.uint64)
        arcs=cp.zeros((count if debug else 1,self.b),cp.int32)
        flags=cp.zeros(count if debug else 1,cp.int32)
        t0=time.perf_counter()
        self.kernel(((count+127)//128,len(bs)),(128,),
            (np.int32(n),np.int32(self.b),np.int32(self.f),*arrays,self.table,*rr,
             np.uint64(count),nhit,hits,np.int32(len(hits)),np.int32(debug),arcs,flags))
        self.done.record()
        self.done.synchronize()
        elapsed=time.perf_counter()-t0
        found=int(nhit.get()[0])
        if found>len(hits): raise RuntimeError('hit output overflow; run smaller chunks')
        verified=[]
        for s,r in hits.get()[:found]:
            d=records[int(s)]; a=unrank(int(r),n,d['lows']); ch=materialise(d['chords'],a)
            if not V.pancyclic(n,ch): raise RuntimeError('independent verifier rejected GPU SAT')
            verified.append(dict(shape=int(s),rank=int(r),arcs=a,chords=ch,n=n,verification='search/verify.py pancyclic=True'))
        return verified,elapsed,(arcs.get(),flags.get()) if debug else None


def controls(engine,mutate=False):
    witnesses=[(67,[(0,2),(0,60),(1,13),(3,61),(4,31),(59,62)]),
               (56,[(0,2),(0,53),(1,39),(20,39),(39,48),(48,53)])]
    evidence=[]; mismatches=0; sampled=0
    for n,ch in witnesses:
        d,a=canonical_witness(n,ch); rank=rank_arcs(a,d['lows'])
        test=dict(d)
        if mutate: test['forms']=[(0,0)]
        hits,_,debug=engine.run(n,[test],[rank],[1],1,True)
        if not hits or list(debug[0][0,:d['b']])!=a: raise RuntimeError('POSITIVE CONTROL FAILED')
        evidence.append(dict(n=n,shape=d['chords'],arcs=a,rank=rank,result='SAT',verified=hits))
        total=math.comb(n-sum(d['lows'])+d['b']-1,d['b']-1)
        for r in [0,total-1]+[random.Random(i+n).randrange(total) for i in range(20)]:
            _,_,(aa,ff)=engine.run(n,[d],[r],[1],1,True)
            expected=unrank(r,n,d['lows']); got=list(map(int,aa[0,:d['b']]))
            truth=V.pancyclic(n,materialise(d['chords'],expected))
            mismatches+=int(got!=expected or bool(ff[0])!=truth); sampled+=1
    if mismatches: raise RuntimeError(f'{mismatches} GPU/verify mismatches')
    return dict(positive_control='PASS',witnesses=evidence,sample=sampled,mismatches=mismatches)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--count',type=int,default=262144,help='rank prefix per eligible shape')
    p.add_argument('--mutate-control',action='store_true')
    p.add_argument('--control-only',action='store_true')
    p.add_argument('--replay',type=Path,help='reuse eligible shape manifests from a completed fresh census')
    args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    proc=psutil.Process(); proc.cpu_affinity([proc.cpu_affinity()[0]])
    if hasattr(psutil,'BELOW_NORMAL_PRIORITY_CLASS'): proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    # Soft CPU duty budget at checkpoints; launch with the external hard-cap supervisor.
    engine=Engine(2*6,70,2**7-1)
    control=controls(engine,args.mutate_control)
    (args.output/'controls.json').write_text(json.dumps(control,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(control),flush=True)
    if args.control_only: return
    replay={}
    if args.replay:
        prior=json.loads((args.replay/'summary.json').read_text())
        summary=dict(shapes=prior['shapes'],max_b=prior['max_b'],levels=[],count=args.count,replay_sources={})
        cache={}
        for level in prior['levels']:
            n=level['n']; path=args.replay/f'n{n}.jsonl'
            raw=path.read_bytes(); rows=[json.loads(x) for x in raw.splitlines()]
            if len(rows)!=level['eligible'] or len({x['shape_index'] for x in rows})!=len(rows):
                raise ValueError('incomplete or duplicate replay census')
            summary['replay_sources'][str(n)]=dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest())
            replay[n]=[]
            for row in rows:
                i=row['shape_index']
                if i not in cache: cache[i]=record(row['b'],row['chords'])
                d=cache[i]
                if d['b']!=row['b'] or d['chords']!=row['chords'] or d['lows']!=row['lows']:
                    raise ValueError('replay shape conflict')
                if len(d['forms'])+2<n or sum(d['lows'])>n or not B.hall_ok(d['iv'],n):
                    raise ValueError('replay eligibility conflict')
                replay[n].append((i,d))
            print('replay prepared',n,len(rows),flush=True)
    else:
        print('Enumerating S.shapes(6)',flush=True)
        shapes=S.shapes(6)
        data=[]
        for i,(b,ch) in enumerate(shapes):
            data.append(record(b,ch))
            if i%1000==0: print('forms',i,flush=True)
        assert max(d['b'] for d in data)==engine.b
        summary=dict(shapes=len(data),max_b=max(d['b'] for d in data),levels=[],count=args.count)
    rng=random.Random(1016)
    for n in (68,69,70):
        eligible=replay[n] if args.replay else [(i,d) for i,d in enumerate(data) if len(d['forms'])+2>=n and sum(d['lows'])<=n and B.hall_ok(d['iv'],n)]
        print('eligible',n,len(eligible),flush=True)
        level_start=time.time()
        tested=0; seconds=0; sat=[]
        with (args.output/f'n{n}.jsonl').open('w',encoding='utf-8',newline='\n') as f:
            for pos in range(0,len(eligible),16):
                group=eligible[pos:pos+16]; starts=[]; steps=[]; rows=[]
                for i,d in group:
                    total=math.comb(n-sum(d['lows'])+d['b']-1,d['b']-1)
                    start=rng.randrange(total)
                    step=rng.randrange(1,min(total,(2**64-1-total)//args.count))
                    while math.gcd(step,total)!=1: step+=1
                    starts.append(start); steps.append(step)
                    rows.append(dict(shape_index=i,b=d['b'],chords=d['chords'],lows=d['lows'],total=total,start=start,step=step,count=min(args.count,total)))
                hits,dt,_=engine.run(n,[d for _,d in group],starts,steps,args.count)
                for hit in hits: hit['shape_index']=group[hit['shape']][0]
                for hit in hits:
                    with (args.output/'verified-hits.jsonl').open('a',encoding='utf-8',newline='\n') as hf:
                        hf.write(json.dumps(hit)+'\n')
                    print('VERIFIED SAT',json.dumps(hit),flush=True)
                sat.extend(hits); seconds+=dt
                for row in rows: f.write(json.dumps(row)+'\n'); tested+=row['count']
                f.flush()
                if pos%256==0: print('progress',n,pos,'tested',tested,'GPU seconds',seconds,flush=True)
        result=dict(n=n,eligible=len(eligible),tested=tested,gpu_seconds=seconds,assignments_per_second=tested/seconds,hits=sat,wall_seconds=time.time()-level_start,start_time=level_start,end_time=time.time())
        summary['levels'].append(result)
        (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result),flush=True)


if __name__=='__main__': main()
