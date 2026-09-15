"""Contiguous descending block of range-mode levels.

    python3 descend.py <k> <nhi> <nlo> <jobs> [nodecap]

Runs one range-mode level per value of n, from nhi DOWN to nlo, and stops early
on anything that is not a clean refutation.  This is the shape the upper-bound
argument actually needs, and the reason is worth stating because a single level
does not give it:

Eligibility is decided AT the cutoff by cap, the sum of the arc lower bounds and
Hall, and Hall at the cutoff is NOT monotone in n -- a shape can fail it at 94
and still be feasible at 100.  So one clean level at n says only "no shape
eligible AT n reaches any value >= n".  What rules out every n >= N is the
CONTIGUOUS BLOCK of clean levels N, N+1, ..., max_cap: a shape feasible at n0 in
that range is eligible at the level whose cutoff is exactly n0, because Hall is
evaluated at that same n0, and that level refuted it.  Each level this driver
completes cleanly therefore extends the block down by exactly one and tightens
the upper bound by one.  A gap in the middle voids everything below it, which is
why this descends contiguously and halts rather than skipping a level.

Two outcomes, both worth having:
  * a SAT anywhere in the block is a witness -- it raises the LOWER bound, and it
    is materialised and checked as a real graph before it is believed;
  * a clean UNSAT level lowers the UPPER bound by one.

A level with any GAVEUP or execution error is UNKNOWN, not UNSAT: it stops the
descent, because continuing past it would silently rest the block on a level that
was never decided.

Each level is delegated to hunt.py in range mode, which supplies the parallelism,
the per-shape resumable .done file, and the inline verification of every SAT.
Re-running this driver after an interruption re-runs only the undecided shapes of
the level it stopped in.  Per-level cost goes to descend-k<k>.csv, so the shape of
the cost curve is a measurement rather than an impression.
"""
from __future__ import annotations
import os, subprocess, sys, time

k, nhi, nlo, jobs = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
nodecap = sys.argv[5] if len(sys.argv) > 5 else "8000000000"
HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, f"descend-k{k}.csv")

if not os.path.exists(CSV):
    with open(CSV, "w") as fh:
        fh.write("n,eligible,seconds,verdict\n")

print(f"descend k={k} levels {nhi}..{nlo} jobs={jobs} nodecap={nodecap}/shape", flush=True)
for n in range(nhi, nlo - 1, -1):
    log = os.path.join(HERE, f"descend-k{k}-n{n}.log")
    t0 = time.time()
    with open(log, "w") as fh:
        rc = subprocess.run([sys.executable, "-u", os.path.join(HERE, "hunt.py"),
                             str(k), str(n), str(jobs), nodecap, "0"],
                            stdout=fh, stderr=subprocess.STDOUT, cwd=HERE).returncode
    dt = round(time.time() - t0, 1)
    text = open(log).read()
    result = ([l for l in text.splitlines() if l.startswith("RESULT")] or ["RESULT (none)"])[-1]
    elig = ([l.split("eligible=")[1].split()[0] for l in text.splitlines()
             if l.startswith("shapes=")] or ["?"])[0]
    verdict = ("SAT" if "RESULT SAT" in result else
               "UNSAT" if "no eligible shape reaches" in result else "UNKNOWN")
    with open(CSV, "a") as fh:
        fh.write(f"{n},{elig},{dt},{verdict}\n")
    print(f"LEVEL n={n} eligible={elig} {dt}s exit={rc} :: {result}", flush=True)
    if verdict == "SAT":
        for l in text.splitlines():
            if l.startswith("*** SAT"):
                print(l, flush=True)
        print(f"DESCEND STOPPED at n={n}: a witness raises the lower bound; "
              f"t_{k} >= the n on that line.  Nothing below is run.", flush=True)
        sys.exit(0)
    if verdict != "UNSAT":
        print(f"DESCEND STOPPED at n={n}: the level is UNKNOWN, not a refutation "
              f"(exit {rc}).  The block ends at n={n+1} and everything below it is "
              f"unproven.", flush=True)
        sys.exit(1)

print(f"DESCEND COMPLETE -- levels {nhi}..{nlo} all clean UNSAT with gaveup=0; "
      f"the block now runs {nlo}..max_cap, so t_{k} <= {nlo - 1}", flush=True)
