"""GPU joint multi-chord neighbourhood sweep around near-miss 6-chord seeds (GPU only, no CPU search).

Reuses the CuPy RawKernel of search/k6/gpu_pancyc128.py unchanged.  That kernel takes `nfixed` fixed
chords plus an r-combination of a caller-supplied candidate list, unranked in colex order, so a
"replace r of the 6 seed chords" neighbourhood is expressed directly: for each r-subset P of the six
slot positions, fix the other 6-r seed chords and enumerate every r-combination of the legal chords
that are not among the fixed ones.  The union over all P is exactly the set of 6-chord sets that
differ from the seed in at most r chords (the r-sweep contains the (r-1)-sweep, because the removed
chord itself stays in the candidate list).

Two facts about the engine that this harness has to work around, both reported in
papers/REPORT-k6-gpu-joint.md:
  * gpu_pancyc128.binom_table() has 1024 rows, and the kernel indexes binom[c*5+i] for c up to M-1.
    n=56 has 1484 legal chords and n=67 has 2144, so the 1024-row table would be read out of bounds.
    The kernel takes the table as a pointer, so this file passes a table with BINOM_ROWS rows.
  * the kernel's found_chords buffer holds max_found=64 witnesses per launch; the count is reported
    separately so an overflow is visible.

Positive control (run first, always): the kernel must accept the verified n=56 witness
(0,2)(0,53)(1,39)(20,39)(39,48)(48,53) via the r=0 path, reject the n=65/66/67 near-misses via r=0,
and the full 2-of-6 sweep around the n=56 witness must re-find that witness through the colex
unranking with M > 1024.

Usage:
  python gpu_joint_sweep.py control
  python gpu_joint_sweep.py sweep N R "(a,b) (c,d) ..." [--tag NAME] [--all] [--chunk 2^27] [--duty 0.8]
      --all : keep sweeping every slot subset after a witness is found (default: stop at first hit)
      --duty: GPU duty cycle; after each chunk the host sleeps (1/duty-1) x the chunk's measured wall
              time (cap 80 % GPU -> default 0.8).  The idle gap between launches is what lowers
              the nvidia-smi utilisation figure; chunk size alone does not.
State: gpu-joint-state-{tag}.json (resumable per slot subset); witnesses are appended there.
"""
import sys, os, time, json, math, itertools
import numpy as np, cupy as cp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpu_pancyc128 as engine   # KERNEL, all_chords; importing also sets cudaDeviceScheduleBlockingSync

try:  # keep the host side polite: BELOW_NORMAL_PRIORITY_CLASS
    import ctypes
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
except Exception:
    pass

BINOM_ROWS = 4096      # > 2144 legal chords at n=67; C(4095,4) ~ 1.2e13 fits u64
MAX_FOUND = 64
THREADS = 128


def binom_table(rows=BINOM_ROWS):
    t = np.zeros((rows, 5), dtype=np.uint64)
    for c in range(rows):
        for i in range(5):
            t[c, i] = math.comb(c, i)
    return t


def parse(s):
    import re
    return [tuple(int(x) for x in m) for m in re.findall(r"\((\d+),(\d+)\)", s)]


def fmt(ch):
    return "".join(f"({a},{b})" for a, b in ch)


def legal_chords(n):
    return [(a, b) for a, b, sp in engine.all_chords(n)]


class Kernel:
    def __init__(self):
        self.kern = cp.RawKernel(engine.KERNEL, "search")
        self.binom_d = cp.asarray(binom_table().reshape(-1))

    def run(self, n, k, fixed, cands, start, count, found_count, found_chords):
        r = k - len(fixed)
        M = len(cands)
        fa = cp.asarray([c[0] for c in fixed] or [0], dtype=cp.int32)
        fb = cp.asarray([c[1] for c in fixed] or [0], dtype=cp.int32)
        ca = cp.asarray([c[0] for c in cands] or [0], dtype=cp.int32)
        cb = cp.asarray([c[1] for c in cands] or [0], dtype=cp.int32)
        engine.check_binom_rows(M, self.binom_d)   # loud host-side guard: M must fit the unranking table
        blocks = (count + THREADS - 1) // THREADS
        self.kern((int(blocks),), (THREADS,),
                  (np.int32(n), np.int32(k), np.int32(len(fixed)), np.int32(r), fa, fb, ca, cb, np.int32(M),
                   self.binom_d, np.uint64(start), np.uint64(count), found_count, found_chords, np.int32(MAX_FOUND)))
        cp.cuda.Device().synchronize()

    def single(self, n, chords):
        """Kernel verdict on one explicit 6-chord set (nfixed=k, r=0): 1 if pancyclic else 0."""
        fc = cp.zeros(1, dtype=cp.int32); fw = cp.zeros(MAX_FOUND * 16, dtype=cp.int32)
        self.run(n, len(chords), list(chords), [], 0, 1, fc, fw)
        return int(fc.get()[0])

    def neighbourhood(self, n, k, fixed, cands, chunk, log=None, resume_start=0, on_progress=None, duty=1.0):
        """Enumerate every r-combination of cands with the given fixed chords. Returns (witnesses, found_total, tested).

        duty < 1 duty-cycles the GPU: after each chunk the host sleeps (1/duty - 1) times that chunk's
        measured wall time (cap: 80 % GPU utilisation -> duty=0.8 -> sleep a quarter of the chunk time).
        The gap between launches is what moves the nvidia-smi utilisation figure; the chunk size does not."""
        r = k - len(fixed)
        total = math.comb(len(cands), r)
        fc = cp.zeros(1, dtype=cp.int32); fw = cp.zeros(MAX_FOUND * 16, dtype=cp.int32)
        witnesses = []
        start = resume_start
        t0 = time.time()
        while start < total:
            cnt = min(chunk, total - start)
            tc = time.time()
            self.run(n, k, fixed, cands, start, cnt, fc, fw)
            t_chunk = time.time() - tc
            start += cnt
            gap = t_chunk * (1.0 / duty - 1.0) if duty < 1.0 else 0.0
            found = int(fc.get()[0])
            if found > 0:
                arr = fw.get()
                for s in range(min(found, MAX_FOUND)):
                    w = [(int(arr[s*16 + 2*j]), int(arr[s*16 + 2*j + 1])) for j in range(k)]
                    if w not in witnesses:
                        witnesses.append(w)
            if on_progress:
                on_progress(start, total, found)
            if log:
                print(f"  progress {start}/{total} ({100*start/total:.1f}%) {time.time()-t0:.0f}s chunk={t_chunk:.2f}s gap={gap:.2f}s found={found}", file=log, flush=True)
            if gap > 0 and start < total:
                time.sleep(gap)
        return witnesses, int(fc.get()[0]), total - resume_start


# ---------------------------------------------------------------- controls

CONTROL_56 = parse("(0,2)(0,53)(1,39)(20,39)(39,48)(48,53)")
WITNESS_64 = parse("(0,2)(0,61)(1,12)(3,60)(4,29)(56,61)")
NEAR_MISSES = {
    65: [parse("(0,2)(0,62)(1,12)(3,61)(4,29)(57,62)"), parse("(0,2)(0,62)(1,13)(3,61)(4,30)(57,62)")],
    66: [parse("(0,2)(0,63)(1,13)(3,62)(4,31)(58,63)")],
    67: [parse("(0,2)(0,64)(1,13)(3,63)(4,31)(59,64)")],
}


def control(K):
    ok = True
    def check(label, got, want):
        nonlocal ok
        res = "PASS" if got == want else "FAIL"
        if got != want: ok = False
        print(f"[{res}] {label}: got={got} expected={want}", flush=True)

    check("kernel r=0 accepts n=56 witness " + fmt(CONTROL_56), K.single(56, CONTROL_56), 1)
    check("kernel r=0 accepts n=64 witness " + fmt(WITNESS_64), K.single(64, WITNESS_64), 1)
    for n, seeds in NEAR_MISSES.items():
        for s in seeds:
            check(f"kernel r=0 rejects n={n} near-miss {fmt(s)}", K.single(n, s), 0)
    # mutation of the control: break one chord of the n=56 witness -> must be rejected
    broken = list(CONTROL_56); broken[2] = (1, 40)
    check("kernel r=0 rejects mutated n=56 set " + fmt(broken), K.single(56, broken), 0)

    # end-to-end: 2-of-6 sweep around the n=56 witness must re-find it through colex unranking (M=1482 > 1024)
    n, k = 56, 6
    allc = legal_chords(n)
    found_sets, tested, t0 = [], 0, time.time()
    for P in itertools.combinations(range(k), 2):
        fixed = [c for i, c in enumerate(CONTROL_56) if i not in P]
        cands = [c for c in allc if c not in fixed]
        w, fcount, tot = K.neighbourhood(n, k, fixed, cands, 1 << 26)
        tested += tot
        for x in w:
            if sorted(x) not in found_sets: found_sets.append(sorted(x))
    dt = time.time() - t0
    print(f"n=56 2-of-6 sweep: tested={tested} distinct_witnesses={len(found_sets)} seconds={dt:.1f} rate={tested/dt/1e6:.1f}M/s", flush=True)
    for x in found_sets: print("  sweep witness n=56 " + fmt(x), flush=True)
    check("n=56 2-of-6 sweep re-finds the control witness", sorted(CONTROL_56) in found_sets, True)
    print("CONTROL " + ("GREEN" if ok else "RED"), flush=True)
    return ok


# ---------------------------------------------------------------- sweeps

def sweep(K, n, r, seed, tag, enumerate_all, chunk, duty):
    k = len(seed)
    fn = os.path.join(HERE, f"gpu-joint-state-{tag}.json")
    st = json.load(open(fn)) if os.path.exists(fn) else {"n": n, "r": r, "seed": seed, "done": [], "cur": None, "start": 0,
                                                          "tested": 0, "seconds": 0.0, "witnesses": [], "found_counts": {}}
    def save():
        json.dump(st, open(fn, "w"))
    logf = open(os.path.join(HERE, f"gpu-joint-{tag}.txt"), "a")
    print(f"START n={n} r={r} seed={fmt(seed)} tag={tag} chunk={chunk} duty={duty} all={enumerate_all}", file=logf, flush=True)
    allc = legal_chords(n)
    subsets = list(itertools.combinations(range(k), r))
    t_all = time.time()
    for P in subsets:
        key = ",".join(map(str, P))
        if key in st["done"]:
            continue
        fixed = [c for i, c in enumerate(seed) if i not in P]
        cands = [c for c in allc if c not in fixed]
        total = math.comb(len(cands), r)
        resume = st["start"] if st["cur"] == key else 0
        st["cur"] = key; st["start"] = resume; save()
        print(f" slots {P} fixed={fmt(fixed)} M={len(cands)} total={total} resume={resume}", file=logf, flush=True)
        t0 = time.time()
        def on_progress(start, tot, found):
            st["start"] = start; save()
        w, fcount, tested = K.neighbourhood(n, k, fixed, cands, chunk, log=logf, resume_start=resume, on_progress=on_progress, duty=duty)
        dt = time.time() - t0
        st["tested"] += tested; st["seconds"] += dt
        st["found_counts"][key] = fcount
        for x in w:
            if x not in st["witnesses"]:
                st["witnesses"].append(x)
                print(f"WITNESS n={n} slots={P} chords={fmt(x)}", file=logf, flush=True)
                print(f"WITNESS n={n} slots={P} chords={fmt(x)}", flush=True)
        st["done"].append(key); st["cur"] = None; st["start"] = 0; save()
        print(f" slots {P} done tested={tested} seconds={dt:.0f} rate={tested/max(dt,1e-9)/1e6:.1f}M/s found={fcount}", file=logf, flush=True)
        if fcount > 0 and not enumerate_all:
            break
    complete = len(st["done"]) == len(subsets)
    st["complete"] = complete; save()
    msg = (f"{'COMPLETE' if complete else 'STOPPED'} n={n} r={r} seed={fmt(seed)} subsets_done={len(st['done'])}/{len(subsets)} "
           f"tested={st['tested']} seconds={st['seconds']:.0f} witnesses={len(st['witnesses'])}")
    print(msg, file=logf, flush=True); print(msg, flush=True)
    logf.close()


def main():
    K = Kernel()
    if sys.argv[1] == "control":
        sys.exit(0 if control(K) else 1)
    if sys.argv[1] == "sweep":
        n = int(sys.argv[2]); r = int(sys.argv[3]); seed = parse(sys.argv[4])
        assert len(seed) == 6 and 1 <= r <= 4 and n <= 120
        tag = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else f"{n}-r{r}"
        chunk = int(sys.argv[sys.argv.index("--chunk") + 1]) if "--chunk" in sys.argv else (1 << 27)
        duty = float(sys.argv[sys.argv.index("--duty") + 1]) if "--duty" in sys.argv else 0.8
        assert 0.05 <= duty <= 1.0
        sweep(K, n, r, seed, tag, "--all" in sys.argv, chunk, duty)
        return
    print(__doc__)


if __name__ == "__main__":
    main()
