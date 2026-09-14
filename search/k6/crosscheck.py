"""Differential gate: fastcyc.exe (C, two-word masks) must agree with cyclespace.py (Python,
arbitrary-width ints) on the FULL set of cycle lengths, for random chord sets over a range of n
that includes n > 64 (where the C code's masks cross the 64-bit word boundary).

cyclespace.py is itself gated against networkx.simple_cycles by "python cyclespace.py control", so
a pass here chains fastcyc -> cyclespace -> networkx.  This asserts behaviour (the length set for
given inputs), not an implementation spelling.

Usage: python crosscheck.py [trials] [seed]
"""
import sys, os, random, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
FAST = os.path.join(HERE, "fastcyc.exe")
sys.path.insert(0, HERE)
from cyclespace import cycle_lengths

EXE = sys.argv[3] if len(sys.argv) > 3 else FAST


def fast_lengths(n, chords):
    arg = " ".join(f"{a},{b}" for a, b in chords)
    r = subprocess.run([EXE, "verify", str(n), arg], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if line.startswith("n="):
            body = line.split("lengths=")[1].strip()
            return {int(x) for x in body.split()} if body else set()
    raise RuntimeError(r.stdout + r.stderr)


def main():
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 20260914)
    bad = 0
    for t in range(trials):
        n = rng.choice([rng.randint(7, 20), rng.randint(55, 75), rng.randint(76, 110)])
        k = rng.randint(1, 6)
        pool = [(a, b) for a in range(n) for b in range(a + 2, n) if not (a == 0 and b == n - 1)]
        chords = rng.sample(pool, min(k, len(pool)))
        ref = cycle_lengths(n, chords)
        got = fast_lengths(n, chords)
        if ref != got:
            bad += 1
            if bad <= 3:
                print(f"    MISMATCH n={n} chords={chords}")
                print(f"      cyclespace only: {sorted(ref - got)}   fastcyc only: {sorted(got - ref)}")
    print(f"[{'PASS' if bad == 0 else 'FAIL'}] fastcyc agrees with cyclespace on {trials} random "
          f"graphs (n from 7 to 110): {bad} mismatches")
    print("CROSSCHECK " + ("GREEN" if bad == 0 else "RED"))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
