"""GPU exhaustive search for pancyclic C_n + k chords -- 128-bit (two-word) port of
search/gpu_pancyc.py.

Why this file exists: search/gpu_pancyc.py keeps the cycle-edge mask, the per-element edge mask and
the achieved-length mask in single 64-bit words, and asserts "3 <= n <= 60"; the draft records that
limit.  Here every one of those masks is a pair of unsigned long long (lo, hi), so n up to 120 is
representable and n > 60 is reachable.  Nothing else about the algorithm changes: same case split
(every pancyclic graph has a triangle, so up to rotation either a span-2 chord (0,2), or chords
(0,b),(1,b), or a chord triangle (0,b),(b,c),(0,c)), same colex unranking of r-combinations, same
cycle-space Gray code over 2^(k+1) subsets, same degree-plus-walk "is a single cycle" test.

State is written to gpu128-state-{n}-{k}.json in the working directory, deliberately a different
name from the gpu-state-{n}-{k}.json files of the 64-bit script, so the recorded runs of the
original are not touched.

Usage: python gpu_pancyc128.py n k [--all] [--chunk 2^26]
"""
import sys, time, itertools, math
import numpy as np, cupy as cp
try:  # block instead of spinning while the GPU works, to keep host CPU near zero
    cp.cuda.runtime.setDeviceFlags(4)  # cudaDeviceScheduleBlockingSync
except Exception:
    pass

KERNEL = r'''
typedef unsigned long long u64;

__device__ __forceinline__ int getbit(u64 lo, u64 hi, int i) {
    return (i < 64) ? (int)((lo >> i) & 1ULL) : (int)((hi >> (i - 64)) & 1ULL);
}

extern "C" __global__
void search(const int n, const int k, const int nfixed, const int r,
            const int* fa, const int* fb,             // fixed chords
            const int* ca, const int* cb, const int M, // candidate chords
            const unsigned long long* binom,           // binom[c*5 + i] = C(c,i), c < BINOM_ROWS, i <= 4; host checks M <= BINOM_ROWS before launch
            const unsigned long long start, const unsigned long long count,
            int* found_count, int* found_chords, const int max_found)
{
    unsigned long long tid = blockIdx.x * (unsigned long long)blockDim.x + threadIdx.x;
    if (tid >= count) return;
    unsigned long long N = start + tid;
    int A[8], B[8];
    for (int i = 0; i < nfixed; i++) { A[i] = fa[i]; B[i] = fb[i]; }
    // unrank colex r-combination of {0..M-1}
    int idx[4];
    for (int i = r; i >= 1; i--) {
        int lo = i - 1, hi = M - 1;             // largest c with C(c,i) <= N
        while (lo < hi) { int mid = (lo + hi + 1) >> 1; if (binom[mid*5 + i] <= N) lo = mid; else hi = mid - 1; }
        idx[i-1] = lo; N -= binom[lo*5 + i];
    }
    for (int i = 0; i < r; i++) { A[nfixed + i] = ca[idx[i]]; B[nfixed + i] = cb[idx[i]]; }

    // basis: element 0 = Hamilton cycle; element j+1 = chord j + cycle path A[j]..B[j]
    u64 bce_lo[9], bce_hi[9]; unsigned int bch[9];
    u64 full_lo = (n >= 64) ? ~0ULL : ((1ULL << n) - 1ULL);
    u64 full_hi = (n > 64) ? ((1ULL << (n - 64)) - 1ULL) : 0ULL;
    bce_lo[0] = full_lo; bce_hi[0] = full_hi; bch[0] = 0;
    for (int j = 0; j < k; j++) {
        u64 mlo = 0, mhi = 0;
        for (int i = A[j]; i < B[j]; i++) { if (i < 64) mlo |= 1ULL << i; else mhi |= 1ULL << (i - 64); }
        bce_lo[j+1] = mlo; bce_hi[j+1] = mhi; bch[j+1] = 1u << j;
    }

    u64 lens_lo = 0, lens_hi = 0, cur_lo = 0, cur_hi = 0; unsigned int cur_ch = 0;
    unsigned int total = 1u << (k + 1);
    for (unsigned int g = 1; g < total; g++) {
        int bit = __ffs(g) - 1;
        cur_lo ^= bce_lo[bit]; cur_hi ^= bce_hi[bit]; cur_ch ^= bch[bit];
        int ne = __popcll(cur_lo) + __popcll(cur_hi) + __popc(cur_ch);
        if (ne < 3) continue;
        unsigned char deg[128];
        for (int v = 0; v < n; v++) deg[v] = 0;
        for (int i = 0; i < n; i++) if (getbit(cur_lo, cur_hi, i)) { deg[i]++; deg[(i+1) % n]++; }
        for (int j = 0; j < k; j++) if ((cur_ch >> j) & 1u) { deg[A[j]]++; deg[B[j]]++; }
        int ok = 1, start_v = -1;
        for (int v = 0; v < n; v++) { if (deg[v] != 0 && deg[v] != 2) { ok = 0; break; } if (deg[v] == 2 && start_v < 0) start_v = v; }
        if (!ok || start_v < 0) continue;
        // walk the support; it is a single cycle iff we return to start after exactly ne steps
        int v = start_v, prev = -1, cnt = 0;
        while (1) {
            int next = -1, w = -1;
            int e1 = (v - 1 + n) % n;
            if (getbit(cur_lo, cur_hi, e1) && e1 != prev) { next = e1; w = e1; }
            if (next < 0 && getbit(cur_lo, cur_hi, v) && v != prev) { next = v; w = (v + 1) % n; }
            if (next < 0) for (int j = 0; j < k; j++) {
                if (((cur_ch >> j) & 1u) && (n + j) != prev && (A[j] == v || B[j] == v)) { next = n + j; w = (A[j] == v) ? B[j] : A[j]; break; }
            }
            if (next < 0) break;
            cnt++; prev = next; v = w;
            if (v == start_v) break;
        }
        if (v == start_v && cnt == ne) { if (ne < 64) lens_lo |= 1ULL << ne; else lens_hi |= 1ULL << (ne - 64); }
    }
    // need = bits 3..n
    u64 need_lo, need_hi;
    if (n + 1 >= 64) { need_lo = ~0ULL; need_hi = (n + 1 > 64) ? ((1ULL << (n + 1 - 64)) - 1ULL) : 0ULL; }
    else { need_lo = (1ULL << (n + 1)) - 1ULL; need_hi = 0ULL; }
    need_lo &= ~7ULL;
    if ((lens_lo & need_lo) == need_lo && (lens_hi & need_hi) == need_hi) {
        int slot = atomicAdd(found_count, 1);
        if (slot < max_found) for (int j = 0; j < k; j++) { found_chords[slot*16 + 2*j] = A[j]; found_chords[slot*16 + 2*j + 1] = B[j]; }
    }
}
'''

# Rows of the unranking table.  The kernel binary-searches binom[c*5+i] for c up to M-1, where M is
# the candidate-chord count n(n-3)/2 (minus the fixed chords), so the table must have at least M rows.
# The original 1024-row table silently capped the usable range at n <= 46 (n=47 has 1034 chords):
# beyond that the kernel read past the table with no diagnostic.  n <= 120 (two-word masks) needs n(n-3)/2 = 7020 rows;
# 8192 covers it, and check_binom_rows() fails loudly instead of letting the next raise of n walk
# off the end again.
BINOM_ROWS = 8192

def binom_table(rows=BINOM_ROWS):
    t = np.zeros((rows, 5), dtype=np.uint64)
    for c in range(rows):
        for i in range(5):
            t[c, i] = math.comb(c, i) if c >= i else 0
    return t

def check_binom_rows(M, binom_d):
    """Fail loudly, host-side and before any launch, if the candidate count M exceeds the table."""
    rows = int(binom_d.size) // 5
    if M > rows:
        raise ValueError(f"candidate chord count M={M} exceeds binom table rows={rows}: the kernel's colex "
                         f"unranking would read binom[] out of bounds; enlarge binom_table(rows=...)")
    return rows

def all_chords(n):
    out = []
    for a in range(n):
        for b in range(a + 2, n):
            if a == 0 and b == n - 1: continue
            sp = b - a; sp = min(sp, n - sp)
            out.append((a, b, sp))
    return out

import json, os
STATE = None
def load_state(n, k):
    global STATE
    fn = f"gpu128-state-{n}-{k}.json"
    STATE = json.load(open(fn)) if os.path.exists(fn) else {"done": [], "cur": None, "start": 0, "witnesses": [], "tested": 0}
    STATE["_fn"] = fn
def save_state():
    d = {kk: v for kk, v in STATE.items() if not kk.startswith("_")}
    json.dump(d, open(STATE["_fn"], "w"))

def run_case(kern, n, k, fixed, cands, chunk, enumerate_all, binom_d, log):
    key = repr(fixed)
    if key in STATE["done"]:
        return [], 0
    r = k - len(fixed)
    M = len(cands)
    check_binom_rows(M, binom_d)
    total = math.comb(M, r)
    fa = cp.asarray([c[0] for c in fixed] or [0], dtype=cp.int32); fb = cp.asarray([c[1] for c in fixed] or [0], dtype=cp.int32)
    ca = cp.asarray([c[0] for c in cands], dtype=cp.int32); cb = cp.asarray([c[1] for c in cands], dtype=cp.int32)
    found_count = cp.zeros(1, dtype=cp.int32); max_found = 64
    found_chords = cp.zeros(max_found * 16, dtype=cp.int32)
    witnesses = []
    start = STATE["start"] if STATE["cur"] == key else 0
    STATE["cur"] = key; STATE["start"] = start; save_state()
    t0 = time.time()
    while start < total:
        cnt = min(chunk, total - start)
        threads = 128; blocks = (cnt + threads - 1) // threads
        kern((int(blocks),), (threads,), (np.int32(n), np.int32(k), np.int32(len(fixed)), np.int32(r), fa, fb, ca, cb, np.int32(M), binom_d,
                                            np.uint64(start), np.uint64(cnt), found_count, found_chords, np.int32(max_found)))
        cp.cuda.Device().synchronize()
        start += cnt
        STATE["start"] = start; STATE["tested"] += int(cnt); save_state()
        fc = int(found_count.get()[0])
        if fc > 0:
            arr = found_chords.get()
            for s in range(min(fc, max_found)):
                w = [(int(arr[s*16 + 2*j]), int(arr[s*16 + 2*j + 1])) for j in range(k)]
                if w not in witnesses: witnesses.append(w)
            if not enumerate_all: break
        if log: print(f"  progress {start}/{total} ({100*start/total:.1f}%) {time.time()-t0:.0f}s found={fc}", flush=True)
    STATE["done"].append(key); STATE["cur"] = None; STATE["start"] = 0
    STATE["witnesses"] += [w for w in witnesses if w not in STATE["witnesses"]]; save_state()
    return witnesses, total

def main():
    n = int(sys.argv[1]); k = int(sys.argv[2])
    enumerate_all = "--all" in sys.argv
    chunk = 1 << 26
    if "--chunk" in sys.argv: chunk = int(sys.argv[sys.argv.index("--chunk") + 1])
    assert 3 <= n <= 120 and 1 <= k <= 8      # two-word masks: 120 vertices, lengths up to 120
    load_state(n, k)
    kern = cp.RawKernel(KERNEL, "search")
    binom_d = cp.asarray(binom_table().reshape(-1))
    chords = all_chords(n)
    nospan2 = [(a, b) for a, b, sp in chords if sp != 2]
    allc = [(a, b) for a, b, sp in chords]
    t0 = time.time(); results = [list(w) for w in STATE["witnesses"]]; tested = 0
    # Case A
    cands = [c for c in allc if c != (0, 2)]
    w, tot = run_case(kern, n, k, [(0, 2)], cands, chunk, enumerate_all, binom_d, log=True); tested += tot; results += w
    if k >= 2 and (enumerate_all or not results):
        for b in range(3, n - 1):
            if not (0, b) in nospan2 or not (1, b) in nospan2: continue
            cands = [c for c in nospan2 if c not in ((0, b), (1, b))]
            w, tot = run_case(kern, n, k, [(0, b), (1, b)], cands, chunk, enumerate_all, binom_d, log=False); tested += tot; results += w
            if results and not enumerate_all: break
    if k >= 3 and (enumerate_all or not results):
        for b in range(3, n - 4):
            for c2 in range(b + 3, n - 2):
                fx = [(0, b), (b, c2), (0, c2)]
                if any(f not in nospan2 for f in fx): continue
                cands = [c for c in nospan2 if c not in fx]
                w, tot = run_case(kern, n, k, fx, cands, chunk, enumerate_all, binom_d, log=False); tested += tot; results += w
                if results and not enumerate_all: break
            if results and not enumerate_all: break
    dt = time.time() - t0
    if results:
        for w in results: print(f"WITNESS n={n} k={k} : " + " ".join(f"({a},{b})" for a, b in w))
        print(f"tested={STATE['tested']} witnesses={len(results)} seconds={dt:.0f}")
    else:
        print(f"NONE n={n} k={k} tested={STATE['tested']} seconds={dt:.0f}")
    STATE["finished"] = True; save_state()

if __name__ == "__main__":
    main()
