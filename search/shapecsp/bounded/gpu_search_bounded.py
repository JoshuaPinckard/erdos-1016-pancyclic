"""Bounded-composition variant of gpu_search.Engine.

Difference from gpu_search.py, and the only one: the kernel unranks inside the
per-arc box lows[i] <= a_i <= hi[i] that bound.hall_ok already implies (see
bounded_caps.py), instead of unranking all compositions with a_i >= lows[i].
The satisfaction test, the coverage bitmap, the hit path and the independent
verifier call are byte-for-byte the same logic as the production kernel.

The kernel carries a permanent cap guard: every unranked digit is compared
against its cap and a violation increments a counter that the host turns into a
RuntimeError.  A mis-sized or mis-strided table therefore fails loudly on real
production data instead of silently enumerating a wrong set.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import random
import sys
import time
from pathlib import Path

import numpy as np
import cupy as cp

HERE = Path(__file__).resolve().parent
PROD = HERE.parent
sys.path.insert(0, str(PROD))

import shapes as S            # noqa: E402  (production modules, imported read-only)
import bound as B             # noqa: E402
import bounded_caps as BC     # noqa: E402

spec = importlib.util.spec_from_file_location("independent_verify", PROD.parent / "verify.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)

CUDA = r'''
typedef unsigned long long U;
extern "C" __global__ void scan(int n, int stride_b, int stride_f, int stride_k, int stride_s,
 const int* bs, const int* nf, const int* lows, const int* caps, const int* masks,
 const int* cs, const U* sums, const U* totals, const U* starts,
 const U* steps, U count, int* nhit, U* hits, int maxhit,
 int debug, int* arcs_out, int* flags, int* viol) {
 /* The prefix table is read straight from global memory.  Staging it in shared
    memory per block was MEASURED SLOWER on an RTX 5060 Ti: a 128-thread block
    covers only 128 ranks, so copying (MAX_B+1)*stride_k table entries per block
    costs far more than the handful of L1/L2-resident loads the binary search
    makes.  n=68 b=12, 5e10 ranks: 233e6 ranks/s staged, against 414e6 for the
    production kernel reading its own binomial table the same unstaged way. */
 int s=blockIdx.y, b=bs[s];
 const U* base=sums+(U)s*stride_s;
 U t=(U)blockIdx.x*blockDim.x+threadIdx.x;
 if(t>=count || t>=totals[s]) return;
 U rank=(starts[s]+t*steps[s])%totals[s], r=rank;
 int a[MAX_B];
 int srem=n;
 for(int j=0;j<b;j++) srem-=lows[s*stride_b+j];
 for(int k=0;k<b-1;k++) {
   const U* sk=base+(k+1)*stride_k;
   U target=sk[srem]-r;                       /* > 0 whenever r < T[k][srem] */
   int lo=-1, hh=srem-1;                      /* largest z with S[k+1][z] < target */
   while(lo<hh) {int mid=(lo+hh+1)>>1;
     if(sk[mid]<target) lo=mid; else hh=mid-1;}
   int y=srem-1-lo;
   r-=sk[srem]-sk[lo+1];
   if(y>caps[s*stride_b+k]) atomicAdd(viol,1);
   a[k]=y+lows[s*stride_b+k];
   srem-=y;
 }
 if(srem>caps[s*stride_b+b-1]) atomicAdd(viol,1);
 a[b-1]=srem+lows[s*stride_b+b-1];
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

MAX_SHARED_BYTES = 48 * 1024


def record(b, chords, n):
    """gpu_search.record plus the box.  n matters now: the caps depend on it."""
    return BC.shape_box(n, b, [tuple(c) for c in chords])


def materialise(ch, arcs):
    points = [0]
    for a in arcs[:-1]:
        points.append(points[-1] + a)
    return sorted(tuple(sorted((points[u], points[v]))) for u, v in ch)


def canonical_witness(n, ch):
    pts = sorted({v for e in ch for v in e})
    b = len(pts)
    edges = [(pts.index(u), pts.index(v)) for u, v in ch]
    raw = [(pts[(i + 1) % b] - pts[i]) % n for i in range(b)]
    canonical = S.canon(b, edges)
    for g in S._dihedral(b):
        img = tuple(sorted(tuple(sorted((g[u], g[v]))) for u, v in edges))
        if img != canonical:
            continue
        arcs = [0] * b
        for i, a in enumerate(raw):
            j = g[i] if g[(i + 1) % b] == (g[i] + 1) % b else g[(i + 1) % b]
            arcs[j] = a
        return record(b, canonical, n), arcs
    raise RuntimeError("no dihedral image matched the canonical form")


class Engine:
    def __init__(self, max_b, max_n, max_f):
        if not 3 <= max_n <= 126 or not 2 <= max_b <= max_n:
            raise ValueError("unsupported dimensions")
        self.b = max_b
        self.f = max_f
        self.max_n = max_n
        self.done = cp.cuda.Event(block=True, disable_timing=True)
        self.kernel = cp.RawKernel(CUDA.replace("MAX_B", str(max_b)), "scan")

    def run(self, n, records, starts, steps, count, debug=False, verify_hits=True):
        """verify_hits=False returns the SAT count in place of verified hits.

        Only the set-exactness harness uses it, where a space can contain far
        more solutions than the 1024-slot hit buffer holds.  The production
        runner always leaves it True, so a real SAT is always materialised and
        put through search/verify.py before anything calls it a hit.
        """
        if not records or n > self.max_n or n < 3 or count < 1:
            raise ValueError("invalid launch")
        bs = np.array([d["b"] for d in records], np.int32)
        if max(bs) > self.b or (debug and len(records) != 1):
            raise ValueError("array capacity")
        nf = np.array([len(d["forms"]) for d in records], np.int32)
        if max(nf) > self.f:
            raise ValueError("forms capacity")
        lows = np.zeros((len(bs), self.b), np.int32)
        caps = np.zeros((len(bs), self.b), np.int32)
        masks = np.zeros((len(bs), self.f), np.int32)
        cs = masks.copy()
        totals = []
        stride_k = max(d["rem"] for d in records) + 1
        stride_s = (self.b + 1) * stride_k
        if stride_s * 8 > MAX_SHARED_BYTES:
            raise ValueError("prefix table exceeds shared memory")
        sums = np.zeros((len(bs), stride_s), np.uint64)
        for s, d in enumerate(records):
            if sum(d["lows"]) > n or d["rem"] != n - sum(d["lows"]):
                raise ValueError("infeasible composition")
            lows[s, :bs[s]] = d["lows"]
            caps[s, :bs[s]] = d["caps"]
            masks[s, :nf[s]] = [x[0] for x in d["forms"]]
            cs[s, :nf[s]] = [x[1] for x in d["forms"]]
            for k, row in enumerate(d["tables"]):
                sums[s, k * stride_k:k * stride_k + len(row)] = row
            total = d["total"]
            if total != BC.total_from_tables(d["tables"], d["rem"]):
                raise ValueError("record total disagrees with its own tables")
            totals.append(total)
            if not 0 <= starts[s] < total or steps[s] < 1 or math.gcd(steps[s], total) != 1:
                raise ValueError("invalid permutation")
            if starts[s] + (min(count, total) - 1) * steps[s] >= 2 ** 64:
                raise ValueError("rank overflow")
        arrays = [cp.asarray(x) for x in (bs, nf, lows, caps, masks, cs)]
        gsums = cp.asarray(sums)
        rr = [cp.asarray(x, dtype=cp.uint64) for x in (totals, starts, steps)]
        nhit = cp.zeros(1, cp.int32)
        hits = cp.zeros((1024, 2), cp.uint64)
        viol = cp.zeros(1, cp.int32)
        arcs = cp.zeros((count if debug else 1, self.b), cp.int32)
        flags = cp.zeros(count if debug else 1, cp.int32)
        t0 = time.perf_counter()
        self.kernel(((count + 127) // 128, len(bs)), (128,),
                    (np.int32(n), np.int32(self.b), np.int32(self.f),
                     np.int32(stride_k), np.int32(stride_s),
                     *arrays, gsums, *rr,
                     np.uint64(count), nhit, hits, np.int32(len(hits)),
                     np.int32(debug), arcs, flags, viol))
        self.done.record()
        self.done.synchronize()
        elapsed = time.perf_counter() - t0
        broke = int(viol.get()[0])
        if broke:
            raise RuntimeError(f"cap guard tripped {broke} times: unranked digit exceeded its cap")
        found = int(nhit.get()[0])
        if not verify_hits:
            return found, elapsed, (arcs.get(), flags.get()) if debug else None
        if found > len(hits):
            raise RuntimeError("hit output overflow; run smaller chunks")
        verified = []
        for s, r in hits.get()[:found]:
            d = records[int(s)]
            y = BC.unrank_bounded(int(r), d["rem"], d["caps"], d["tables"])
            a = [y[i] + d["lows"][i] for i in range(d["b"])]
            ch = materialise(d["chords"], a)
            if not V.pancyclic(n, ch):
                raise RuntimeError("independent verifier rejected GPU SAT")
            verified.append(dict(shape=int(s), bounded_rank=int(r), arcs=a, chords=ch, n=n,
                                 enumeration="bounded", caps=list(d["caps"]), lows=list(d["lows"]),
                                 verification="search/verify.py pancyclic=True"))
        return verified, elapsed, (arcs.get(), flags.get()) if debug else None


def controls(engine, mutate=False):
    """Positive control, cap-soundness control, and a CPU/GPU unrank sample.

    The two witnesses are real pancyclic graphs.  Their arcs MUST lie inside the
    caps box; if a witness fell outside, the cap rule would be unsound and every
    exhaustion claim built on it void, so that case raises rather than warns.
    """
    witnesses = [(67, [(0, 2), (0, 60), (1, 13), (3, 61), (4, 31), (59, 62)]),
                 (56, [(0, 2), (0, 53), (1, 39), (20, 39), (39, 48), (48, 53)])]
    evidence = []
    mismatches = 0
    sampled = 0
    for n, ch in witnesses:
        d, a = canonical_witness(n, ch)
        y = [a[i] - d["lows"][i] for i in range(d["b"])]
        outside = [i for i in range(d["b"]) if not 0 <= y[i] <= d["caps"][i]]
        if outside:
            raise RuntimeError(
                f"CAP SOUNDNESS FAILED: pancyclic witness n={n} has arcs {a} outside "
                f"box lows={d['lows']} hi={d['hi']} at arc(s) {outside}")
        rank = BC.rank_bounded(y, d["rem"], d["caps"], d["tables"])
        test = dict(d)
        if mutate:
            test["forms"] = [(0, 0)]
        hits, _, debug = engine.run(n, [test], [rank], [1], 1, True)
        if not hits or list(debug[0][0, :d["b"]]) != a:
            raise RuntimeError("POSITIVE CONTROL FAILED")
        evidence.append(dict(n=n, shape=d["chords"], arcs=a, lows=d["lows"], hi=d["hi"],
                             bounded_rank=rank, bounded_total=d["total"],
                             unrestricted_total=d["unrestricted_total"], result="SAT",
                             verified=hits))
        for r in [0, d["total"] - 1] + [random.Random(i + n).randrange(d["total"]) for i in range(20)]:
            _, _, (aa, ff) = engine.run(n, [d], [r], [1], 1, True)
            ey = BC.unrank_bounded(r, d["rem"], d["caps"], d["tables"])
            expected = [ey[i] + d["lows"][i] for i in range(d["b"])]
            got = list(map(int, aa[0, :d["b"]]))
            truth = V.pancyclic(n, materialise(d["chords"], expected))
            mismatches += int(got != expected or bool(ff[0]) != truth)
            sampled += 1
    if mismatches:
        raise RuntimeError(f"{mismatches} GPU/verify mismatches")
    return dict(positive_control="PASS", cap_soundness_on_witnesses="PASS",
                witnesses=evidence, sample=sampled, mismatches=mismatches)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mutate-control", action="store_true")
    args = p.parse_args()
    eng = Engine(12, 70, 127)
    print(json.dumps(controls(eng, args.mutate_control), indent=2))
