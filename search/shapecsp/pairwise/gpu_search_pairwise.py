"""CuPy kernel over the pairwise-admissible composition space of one shape.

One thread per PREFIX (a_0..a_{b-3}), unranked through the DP-state tables of
pairwise_tables.py; the two completion arcs are enumerated inside the thread.

The coverage test is the production one (gpu_search.scan: two 64-bit words,
need0/need1 over [3, n]) but it is not re-evaluated form by form for every
composition.  For a fixed prefix with sum s, a form's length is

    n_chords + sum_{i in f, i < b-2} a_i  +  [b-2 in f] v  +  [b-1 in f] (n - s - v)

so as v steps by one the length is constant (both or neither completion arc in
f), rises by one (only b-2) or falls by one (only b-1).  The thread builds three
128-bit masks once per prefix and then, per completion, shifts the "rising" mask
left, the "falling" mask right, ORs the three and tests.  That is what makes a
composition cost a handful of instructions instead of ~127 form evaluations.

Guards (all counted into `viol`, which the host turns into a RuntimeError):
a rank the transitions cannot unrank, a prefix sum overflow, a prefix with no
completion, a completion outside its bounds.  Every SAT is materialised on the
host from (prefix rank, v), unranked on the CPU by the mirror code, and checked
by search/verify.py (NetworkX simple cycles) before anything calls it a hit.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
import sys
import time
from pathlib import Path

import numpy as np
import cupy as cp

HERE = Path(__file__).resolve().parent
PROD = HERE.parent
for p in (str(HERE), str(PROD)):
    if p not in sys.path:
        sys.path.insert(0, p)
import shapes as S                  # noqa: E402
import pairwise_tables as PT        # noqa: E402

spec = importlib.util.spec_from_file_location("independent_verify", PROD.parent / "verify.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)

MAXC = 80          # debug mode: completions recorded per prefix (a_{b-2} takes <= n values)
DEBUG_MAX = 1 << 14   # prefixes per debug launch: 16384 * 80 * 13 ints = 68 MB of records
CUDA = r'''
typedef unsigned long long U;
extern "C" __global__ void scan(int n, int b, int vmax, int nf,
 const int* lows_g, const int* trans_flat, const long long* trans_off,
 const U* P_flat, const long long* P_off, const int* capA, const int* capB,
 const int* Tlast_g, const int* masks_g, const int* cs_g,
 U total_prefixes, U offset, U count,
 int* nhit, U* hits, int maxhit, U* ncomp, int* viol,
 int debug, int* arcs_out, int* cnt_out) {
 __shared__ int lows[MAX_B];
 __shared__ int Tlast[MAX_V];
 __shared__ int masks[MAX_F];
 __shared__ int cs[MAX_F];
 __shared__ U block_comp;
 for (int i = threadIdx.x; i < b; i += blockDim.x) lows[i] = lows_g[i];
 for (int i = threadIdx.x; i <= vmax; i += blockDim.x) Tlast[i] = Tlast_g[i];
 for (int i = threadIdx.x; i < nf; i += blockDim.x) { masks[i] = masks_g[i]; cs[i] = cs_g[i]; }
 if (threadIdx.x == 0) block_comp = 0;
 __syncthreads();
 U t = (U)blockIdx.x * blockDim.x + threadIdx.x;
 U mycomp = 0;
 if (t < count && offset + t < total_prefixes) {
   U r = offset + t, rank = r;
   int a[MAX_B];
   int st = 0, s = 0, bad = 0;
   for (int k = 0; k < b - 2; k++) {
     const int* tr = trans_flat + trans_off[k] + (long long)st * (vmax + 1);
     const U* Pn = P_flat + P_off[k + 1];
     int picked = -1, st2 = -1;
     for (int v = lows[k]; v <= vmax; v++) {
       st2 = tr[v];
       if (st2 < 0 || s + v > n) break;
       U c = Pn[(long long)st2 * (n + 1) + (s + v)];
       if (r < c) { picked = v; break; }
       r -= c;
     }
     if (picked < 0) { bad = 1; break; }
     a[k] = picked; st = st2; s += picked;
   }
   if (bad) { atomicAdd(viol, 1); }
   else {
     int cA = capA[st], cB = capB[st];
     int vlo = lows[b - 2], vhi = cA;
     if (n - s - cB > vlo) vlo = n - s - cB;
     if (n - s - lows[b - 1] < vhi) vhi = n - s - lows[b - 1];
     /* three 128-bit masks at v = vlo */
     U c0 = 0, c1 = 0, p0 = 0, p1 = 0, m0 = 0, m1 = 0;
     int lowmask = (1 << (b - 2)) - 1;
     for (int f = 0; f < nf; f++) {
       int mask = masks[f], len = cs[f];
       int mm = mask & lowmask;
       while (mm) { int j = __ffs(mm) - 1; len += a[j]; mm &= mm - 1; }
       int hasA = (mask >> (b - 2)) & 1, hasB = (mask >> (b - 1)) & 1;
       if (hasA && hasB) len += n - s;
       else if (hasA) len += vlo;
       else if (hasB) len += n - s - vlo;
       if (len < 0 || len > 127) continue;      /* cannot happen for a real composition */
       U bit = 1ULL << (len & 63);
       if (hasA == hasB) { if (len < 64) c0 |= bit; else c1 |= bit; }
       else if (hasA)    { if (len < 64) p0 |= bit; else p1 |= bit; }
       else              { if (len < 64) m0 |= bit; else m1 |= bit; }
     }
     U need0 = n >= 63 ? (~7ULL) : (((1ULL << (n + 1)) - 1) & ~7ULL);
     U need1 = n >= 64 ? ((1ULL << (n - 63)) - 1) : 0;
     int j = 0;
     for (int v = vlo; v <= vhi; v++) {
       int w = n - s - v;
       if (w <= Tlast[v]) {
         mycomp++;
         U cov0 = c0 | p0 | m0, cov1 = c1 | p1 | m1;
         int sat = ((cov0 & need0) == need0) && ((cov1 & need1) == need1);
         if (sat) { int slot = atomicAdd(nhit, 1); if (slot < maxhit) { hits[slot * 2] = rank; hits[slot * 2 + 1] = (U)v; } }
         if (debug && j < MAXC) {
           int* row = arcs_out + ((long long)t * MAXC + j) * (MAX_B + 1);
           for (int i = 0; i < b - 2; i++) row[i] = a[i];
           row[b - 2] = v; row[b - 1] = w;
           row[MAX_B] = sat;
         }
         j++;
       }
       /* shift for v+1: rising forms up one bit, falling forms down one bit */
       p1 = (p1 << 1) | (p0 >> 63); p0 <<= 1;
       m0 = (m0 >> 1) | (m1 << 63); m1 >>= 1;
     }
     if (debug) cnt_out[t] = j;
     if (mycomp == 0) atomicAdd(viol, 1);
   }
 }
 /* block-level reduction of the composition count: one atomic per block */
 for (int o = 16; o > 0; o >>= 1) mycomp += __shfl_down_sync(0xffffffffu, mycomp, o);
 if ((threadIdx.x & 31) == 0) atomicAdd(&block_comp, mycomp);
 __syncthreads();
 if (threadIdx.x == 0 && block_comp) atomicAdd(ncomp, block_comp);
}
'''


class Engine:
    def __init__(self, max_b=12, max_n=70, max_f=127, max_v=128):
        if not 4 <= max_b <= 12 or not 3 <= max_n <= 120 or max_v > 1024:
            raise ValueError("unsupported dimensions")
        self.b, self.n, self.f, self.v = max_b, max_n, max_f, max_v
        src = (CUDA.replace("MAX_B", str(max_b)).replace("MAX_V", str(max_v))
               .replace("MAX_F", str(max_f)).replace("MAXC", str(MAXC)))
        self.kernel = cp.RawKernel(src, "scan")
        self.done = cp.cuda.Event(block=True, disable_timing=True)
        self._cache = {}

    def upload(self, tab):
        """Device copies of one shape's tables, cached by tables hash."""
        key = tab["tables_sha256"]
        if key in self._cache:
            return self._cache[key]
        pk = PT.kernel_pack(tab)
        dev = dict(pk)
        for name in ("lows", "trans_flat", "trans_off", "P_flat", "P_off", "capA", "capB", "Tlast", "masks", "cs"):
            dev[name] = cp.asarray(pk[name])
        self._cache = {key: dev}          # one shape resident at a time
        return dev

    def run(self, tab, offset, count, debug=False, verify_hits=True):
        """Prefix ranks [offset, offset+count) of one shape.

        Returns (verified hits or raw SAT count, gpu seconds, compositions
        counted, debug tuple or None).  In debug mode every visited composition
        is returned in visiting order with its SAT flag.
        """
        n, b = tab["n"], tab["b"]
        if n > self.n or b > self.b or len(tab["forms"]) > self.f or tab["vmax"] + 1 > self.v:
            raise ValueError("tables exceed engine capacity")
        if count < 1 or offset < 0 or offset >= max(1, tab["total_prefixes"]):
            raise ValueError("invalid launch")
        if debug and count > DEBUG_MAX:
            raise ValueError(f"debug launches are bounded to {DEBUG_MAX} prefixes")
        dev = self.upload(tab)
        nhit = cp.zeros(1, cp.int32)
        hits = cp.zeros((4096, 2), cp.uint64)
        ncomp = cp.zeros(1, cp.uint64)
        viol = cp.zeros(1, cp.int32)
        arcs = cp.full((count * MAXC * (self.b + 1) if debug else 1,), -1, cp.int32)
        cnt = cp.zeros(count if debug else 1, cp.int32)
        t0 = time.perf_counter()
        self.kernel(((count + 127) // 128,), (128,),
                    (np.int32(n), np.int32(b), np.int32(tab["vmax"]), np.int32(len(tab["forms"])),
                     dev["lows"], dev["trans_flat"], dev["trans_off"], dev["P_flat"], dev["P_off"],
                     dev["capA"], dev["capB"], dev["Tlast"], dev["masks"], dev["cs"],
                     np.uint64(tab["total_prefixes"]), np.uint64(offset), np.uint64(count),
                     nhit, hits, np.int32(len(hits)), ncomp, viol,
                     np.int32(debug), arcs, cnt))
        self.done.record()
        self.done.synchronize()
        elapsed = time.perf_counter() - t0
        broke = int(viol.get()[0])
        if broke:
            raise RuntimeError(f"kernel guard tripped {broke} times (unrankable rank, sum overflow or empty prefix)")
        found = int(nhit.get()[0])
        comps = int(ncomp.get()[0])
        dbg = None
        if debug:
            arr = arcs.get().reshape(count, MAXC, self.b + 1)
            cn = cnt.get()
            rows, flags = [], []
            for t in range(count):
                if int(cn[t]) > MAXC:
                    raise RuntimeError("debug record overflow: a prefix had more completions than MAXC")
                for j in range(int(cn[t])):
                    row = arr[t, j]
                    rows.append([int(x) for x in row[:b]])
                    flags.append(bool(row[self.b]))
            dbg = (rows, flags, cn)
        if not verify_hits:
            return found, elapsed, comps, dbg
        if found > len(hits):
            raise RuntimeError("hit output overflow; run smaller chunks")
        verified = []
        for rk, v in hits.get()[:found]:
            a, st, s = PT.unrank_prefix(tab, int(rk))
            v = int(v)
            w = n - s - v
            if (v, w) not in PT.completions(tab, st, s):
                raise RuntimeError("GPU hit names a completion the CPU tables do not admit")
            full = a + [v, w]
            ch = materialise(tab["chords"], full)
            if not V.pancyclic(n, ch):
                raise RuntimeError("independent verifier rejected GPU SAT")
            verified.append(dict(prefix_rank=int(rk), v=v, arcs=full, chords=ch, n=n,
                                 enumeration="pairwise", tables_sha256=tab["tables_sha256"],
                                 verification="search/verify.py pancyclic=True"))
        return verified, elapsed, comps, dbg


def materialise(ch, arcs):
    points = [0]
    for a in arcs[:-1]:
        points.append(points[-1] + a)
    return sorted(tuple(sorted((points[u], points[v]))) for u, v in ch)


def canonical_witness(n, ch):
    """(canonical chords, arcs) of a real witness, same map as gpu_search."""
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
        return b, [list(c) for c in canonical], arcs
    raise RuntimeError("no dihedral image matched the canonical form")


WITNESSES = [(67, [(0, 2), (0, 60), (1, 13), (3, 61), (4, 31), (59, 62)]),
             (56, [(0, 2), (0, 53), (1, 39), (20, 39), (39, 48), (48, 53)])]


def controls(engine, mutate=False, sample=20):
    """Before every run: both witnesses lie in A, are found from a one-thread
    launch at their prefix rank, and sampled prefix ranks unrank identically on
    the CPU and the GPU with SAT flags equal to search/verify.py."""
    evidence, mismatches, sampled = [], 0, 0
    for n, ch in WITNESSES:
        b, canonical, a = canonical_witness(n, ch)
        tab = PT.build(n, b, canonical)
        if not PT.admitted(tab, a):
            raise RuntimeError(f"SOUNDNESS CONTROL FAILED: witness n={n} arcs {a} not in A "
                               f"(lows {tab['lows']}, hi {tab['hi']})")
        r, st, s = PT.rank_prefix(tab, a[:b - 2])
        test = dict(tab)
        if mutate:
            test["forms"] = [[0, 0]]
            test["tables_sha256"] = "mutated-" + tab["tables_sha256"]
        hits, _, comps, dbg = engine.run(test, r, 1, debug=True)
        rows, flags, _ = dbg
        if not any(h["arcs"] == a for h in hits) or a not in rows or not flags[rows.index(a)]:
            raise RuntimeError("POSITIVE CONTROL FAILED")
        evidence.append(dict(n=n, shape=canonical, arcs=a, prefix_rank=r, completions=comps,
                             total_prefixes=tab["total_prefixes"], total_compositions=tab["total_compositions"],
                             result="SAT", verified=[dict(h, chords=[list(c) for c in h["chords"]]) for h in hits]))
        rng = random.Random(n)
        ranks = [0, tab["total_prefixes"] - 1] + [rng.randrange(tab["total_prefixes"]) for _ in range(sample)]
        for rk in ranks:
            _, _, comps, (rows, flags, _) = engine.run(tab, rk, 1, debug=True, verify_hits=False)
            pa, pst, ps = PT.unrank_prefix(tab, rk)
            expected = [pa + [v, w] for v, w in PT.completions(tab, pst, ps)]
            truth = [V.pancyclic(n, materialise(tab["chords"], e)) for e in expected]
            mismatches += int(rows != expected or list(flags) != truth or comps != len(expected))
            sampled += 1
    if mismatches:
        raise RuntimeError(f"{mismatches} GPU/CPU disagreements in the control sample")
    return dict(positive_control="PASS", soundness_control_on_witnesses="PASS",
                witnesses=evidence, sample=sampled, mismatches=mismatches)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mutate-control", action="store_true")
    args = p.parse_args()
    eng = Engine()
    print(json.dumps(controls(eng, args.mutate_control), indent=1))
