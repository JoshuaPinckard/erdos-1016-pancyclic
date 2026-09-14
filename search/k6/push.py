"""Chained climb for 6-chord pancyclic witnesses, driving fastcyc.exe.

Per n: single-vertex insertion images of the current witness are the seeds; each of the best seeds
gets an iterated local search (fastcyc search, which is single-chord descent + sampled joint-3 +
exhaustive joint-2); if none closes, the incumbent gets a COMPLETE joint 2-chord sweep split across
processes (fastcyc sweep2, one process per slot pair).  Every witness is re-checked twice: once by
cyclespace.py in this process, and once by the pre-existing, untouched search/verify.py
(networkx.simple_cycles), whose stdout is copied into the log.

Usage: python push.py N0 "(a,b) ..." NMAX [pool] [ils_secs] [sweep_rounds]
"""
import sys, os, subprocess, itertools, time, csv

HERE = os.path.dirname(os.path.abspath(__file__))
FAST = os.path.join(HERE, "fastcyc.exe")
VERIFY = os.path.join(os.path.dirname(HERE), "verify.py")
sys.path.insert(0, HERE)
from cyclespace import missing as cs_missing, parse as cs_parse

K = 6


def fmt(ch):
    return " ".join(f"({a},{b})" for a, b in ch)


def arg(ch):
    return " ".join(f"{a},{b}" for a, b in ch)


def insertion_images(n, chords):
    out = []
    for p in range(n):
        sh = lambda v: v + 1 if v > p else v
        c = [tuple(sorted((sh(a), sh(b)))) for a, b in chords]
        if c not in out:
            out.append(c)
    return out


def run_parallel(cmds, tag):
    procs = []
    for i, c in enumerate(cmds):
        f = open(os.path.join(HERE, f"{tag}-{i}.txt"), "w")
        procs.append((subprocess.Popen(c, stdout=f, stderr=subprocess.STDOUT, cwd=HERE), f))
    outs = []
    for p, f in procs:
        p.wait()
        f.close()
    for i in range(len(cmds)):
        outs.append(open(os.path.join(HERE, f"{tag}-{i}.txt")).read())
    return outs


def best_from(out):
    """last BEST/WITNESS/IMPROVE line -> (missing, chords)"""
    best = None
    for line in out.splitlines():
        if line.startswith(("BEST", "WITNESS", "IMPROVE", "FINAL", "START")):
            parts = line.split()
            m = int(parts[2].split("=")[1])
            ch = cs_parse(parts[3].split("=")[1].replace(")(", ") ("))
            if best is None or m < best[0]:
                best = (m, ch)
    return best


def independent_verify(n, chords):
    r = subprocess.run([sys.executable, VERIFY, str(n), fmt(chords)],
                       capture_output=True, text=True, timeout=1800)
    return r.stdout.strip()


def main():
    n = int(sys.argv[1])
    cur = cs_parse(sys.argv[2])
    nmax = int(sys.argv[3])
    pool = int(sys.argv[4]) if len(sys.argv) > 4 else 7
    ils_secs = int(sys.argv[5]) if len(sys.argv) > 5 else 120
    sweep_rounds = int(sys.argv[6]) if len(sys.argv) > 6 else 3

    assert cs_missing(n, cur) == [], f"start set is not pancyclic at n={n}"
    print(f"START n={n} {fmt(cur)}", flush=True)
    rows = []
    while n < nmax:
        n1 = n + 1
        t0 = time.time()
        seeds = insertion_images(n, cur)
        ranked = sorted(((len(cs_missing(n1, c)), c) for c in seeds), key=lambda t: t[0])
        print(f"n={n1}: {len(seeds)} insertion seeds, best missing={ranked[0][0]}", flush=True)

        # 1. iterated local search from the best seeds, in parallel
        cmds = [[FAST, "search", str(n1), str(ils_secs), str(7000 + n1 * 13 + i), arg(c)]
                for i, (m, c) in enumerate(ranked[:pool])]
        outs = run_parallel(cmds, f"push-ils-{n1}")
        cands = [b for b in (best_from(o) for o in outs) if b]
        cands += [(m, c) for m, c in ranked[:pool]]
        cands.sort(key=lambda t: t[0])
        incumbent = cands[0]
        print(f"n={n1}: after ILS best missing={incumbent[0]} {fmt(incumbent[1])}", flush=True)

        # 2. complete joint-2 sweeps of the incumbent until it closes or stops improving
        for rnd in range(sweep_rounds):
            if incumbent[0] == 0:
                break
            pairs = list(itertools.combinations(range(K), 2))
            cmds = [[FAST, "sweep2", str(n1), arg(incumbent[1]), str(a), str(b)] for a, b in pairs]
            outs = run_parallel(cmds, f"push-sweep2-{n1}-r{rnd}")
            got = [b for b in (best_from(o) for o in outs) if b]
            got.sort(key=lambda t: t[0])
            print(f"n={n1}: joint-2 sweep round {rnd}: {len(pairs)} slot pairs complete, "
                  f"best missing={got[0][0]}", flush=True)
            if got[0][0] >= incumbent[0]:
                print(f"n={n1}: incumbent is an EXHAUSTIVE 2-chord local optimum", flush=True)
                break
            incumbent = got[0]

        if incumbent[0] != 0:
            print(f"n={n1}: STALL missing={incumbent[0]} chords={fmt(incumbent[1])} "
                  f"({time.time()-t0:.0f}s)", flush=True)
            break
        cur = incumbent[1]
        n = n1
        assert cs_missing(n, cur) == []
        vout = independent_verify(n, cur)
        print(f"WITNESS n={n} chords={fmt(cur)}", flush=True)
        print(f"  verify.py: {vout[:120]}...", flush=True)
        ok = "NOT pancyclic" not in vout and "pancyclic" in vout
        print(f"  independent verify.py agrees: {ok}  ({time.time()-t0:.0f}s for this n)", flush=True)
        rows.append({"n": n, "chords": fmt(cur), "method": "insertion + ILS + joint-2 sweep",
                     "verify_py": "pancyclic" if ok else "DISAGREES"})
        with open(os.path.join(HERE, "witnesses-v2.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["n", "chords", "method", "verify_py"])
            w.writeheader()
            w.writerows(rows)
    print(f"FINAL largest n reached: {n}", flush=True)
    print(f"FINAL chords: {fmt(cur)}", flush=True)


if __name__ == "__main__":
    main()
