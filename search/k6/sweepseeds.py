"""Take every known witness at n-1, lift each by single-vertex insertion to n, keep the distinct
images with the smallest missing-count, and give each one a COMPLETE joint 2-chord sweep
(fastcyc sweep2, one process per slot pair).  Reports every set that reaches missing=0 and
re-checks it with the pre-existing search/verify.py.

DECLARED CAP: only the TOPN best distinct insertion images are swept (a full joint-2 sweep is
~15 * NC^2 evaluations, about 10 CPU-minutes at n=65); the rest are listed but not swept.

Usage: python sweepseeds.py N_TARGET witnessfile [TOPN] [POOL]
  witnessfile: one chord set per line, "(a,b)(c,d)..." or "a,b c,d ..."
"""
import sys, os, re, itertools, subprocess, time

HERE = os.path.dirname(os.path.abspath(__file__))
FAST = os.path.join(HERE, "fastcyc.exe")
VERIFY = os.path.join(os.path.dirname(HERE), "verify.py")
sys.path.insert(0, HERE)
from cyclespace import missing as cs_missing


def parse_line(s):
    return [tuple(int(x) for x in m) for m in re.findall(r"\((\d+),(\d+)\)", s)] or \
           [tuple(int(x) for x in t.split(",")) for t in s.split()]


def arg(ch):
    return " ".join(f"{a},{b}" for a, b in ch)


def fmt(ch):
    return " ".join(f"({a},{b})" for a, b in ch)


def run_pool(cmds, names, pool):
    running, out = [], {}
    queue = list(zip(cmds, names))
    while queue or running:
        while queue and len(running) < pool:
            c, nm = queue.pop(0)
            f = open(os.path.join(HERE, nm), "w")
            running.append((subprocess.Popen(c, stdout=f, stderr=subprocess.STDOUT, cwd=HERE), f, nm))
        time.sleep(1)
        for r in running[:]:
            if r[0].poll() is not None:
                r[1].close()
                running.remove(r)
                out[r[2]] = open(os.path.join(HERE, r[2])).read()
    return out


def main():
    n = int(sys.argv[1])
    lines = [l.strip() for l in open(sys.argv[2]) if l.strip()]
    topn = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    pool = int(sys.argv[4]) if len(sys.argv) > 4 else 7
    seeds = {}
    for l in lines:
        base = parse_line(l)
        for p in range(n - 1):
            sh = lambda v: v + 1 if v > p else v
            c = tuple(sorted(tuple(sorted((sh(a), sh(b)))) for a, b in base))
            if c not in seeds:
                seeds[c] = len(cs_missing(n, list(c)))
    ranked = sorted(seeds.items(), key=lambda t: t[1])
    print(f"{len(lines)} source witnesses at n={n-1} -> {len(ranked)} distinct insertion images at "
          f"n={n}; best missing={ranked[0][1]}", flush=True)
    chosen = ranked[:topn]
    print(f"CAP: sweeping the best {len(chosen)} of {len(ranked)} images "
          f"(missing counts {[m for _, m in chosen]})", flush=True)
    pairs = list(itertools.combinations(range(6), 2))
    hits = []
    for si, (ch, m) in enumerate(chosen):
        if m == 0:
            print(f"SEED {si} is ALREADY pancyclic: {fmt(ch)}", flush=True)
            hits.append(list(ch))
            break
        cmds = [[FAST, "sweep2", str(n), arg(ch), str(a), str(b)] for a, b in pairs]
        names = [f"seedsweep-{n}-s{si}-{a}{b}.txt" for a, b in pairs]
        outs = run_pool(cmds, names, pool)
        ncomplete = sum(1 for v in outs.values() if "COMPLETE" in v)
        found = sorted({l.split("chords=")[1] for v in outs.values()
                        for l in v.splitlines() if l.startswith("FOUND")})
        print(f"SEED {si} missing={m} {fmt(ch)}: {ncomplete}/{len(pairs)} slot pairs complete, "
              f"{len(found)} witnesses in its joint-2 neighbourhood", flush=True)
        for f in found:
            print(f"  FOUND n={n} {f}", flush=True)
            hits.append(parse_line(f))
        if found:
            break
    if not hits:
        print(f"NO witness at n={n} from the swept seeds", flush=True)
        return
    w = hits[0]
    assert cs_missing(n, w) == []
    r = subprocess.run([sys.executable, VERIFY, str(n), fmt(w)], capture_output=True, text=True)
    print(f"WITNESS n={n} chords={fmt(w)}", flush=True)
    print(f"verify.py: {r.stdout.strip()}", flush=True)
    with open(os.path.join(HERE, f"witness-{n}.txt"), "w") as f:
        for h in hits:
            f.write(fmt(h) + "\n")


if __name__ == "__main__":
    main()
