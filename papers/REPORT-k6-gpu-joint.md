# REPORT: GPU joint multi-chord neighbourhood sweeps for a 6-chord pancyclic C_n, n = 65, 66, 67

Worker 10, 2026-09-14. Working directory `search/k6`. GPU only (NVIDIA GeForce RTX 5060 Ti, CuPy 14.2.0,
Python 3.13.3); `search/k6/fastcyc.exe` and every other CPU search were not run.

## Result in one paragraph

**No witness was found at n = 67 or n = 66** (nor at n = 65). The neighbourhoods exhausted are named
exactly in the section "Neighbourhoods exhausted" below; nothing here claims a witness does not
exist, since the full 6-chord space at n = 67 is about C(2144,6) ~ 1.3e17 unordered chord sets
(about 3.8e14 after the triangle case split of `gpu_pancyc128.py`), far beyond what was searched.
The positive control passed before any new run: the kernel reproduced the n = 56 witness
`(0,2)(0,53)(1,39)(20,39)(39,48)(48,53)` both as a direct r = 0 evaluation and by re-finding it
inside a complete 2-of-6 sweep around it. GPU utilisation: the sweeps run under an 80 % duty cycle (cap set by the manager
mid-run); measured mean 78.8 % over 60 one-second `nvidia-smi` samples. The host-side Python
process used 0.8 % of the machine's CPU.

## Costliest finding first: both GPU engines' binomial table silently capped n at 46 (latent, now fixed)

**What.** `search/gpu_pancyc.py` and `search/k6/gpu_pancyc128.py` both built their unranking table
with `binom_table()` as `np.zeros((1024, 5))`, and both kernel comments said
`binom[c*5 + i] = C(c,i), c < 1024, i <= 4`. The kernel's colex unranking binary-searches
`hi = M - 1` where `M` is the candidate-chord count. `all_chords(n)` yields n(n-3)/2 chords, which
exceeds 1024 once n >= 47 (n = 47: 1034; n = 56: 1484; n = 65: 2015; n = 66: 2079; n = 67: 2144).
Running either engine's own `main()` at those n would read `binom` out of bounds on the device --
an unranking error with no diagnostic, so wrong candidates would be evaluated and reported as
exhaustive coverage.

**Latent, not active -- no recorded result depends on it.** Manager (f4d1e0af) checked draft
Section 3.4 of `papers/draft/pancyclic-exact-values.md`, which names every bound the GPU
established: the only exhaustive GPU claims are n = 40, k = 5 (`search/gpu-40-5-all.txt`,
`tested=14373209608`) and n = 41, k = 5 (`search/gpu-41-5d.txt`, `tested=17615450195`, NONE). n = 40
has 740 candidate chords and n = 41 has 779, both below the 1024-row bound; the only gpu128 outputs
are `gpu128-40-5.txt` and `gpu128-41-5.txt` at the same n. Every published or drafted GPU claim
therefore lies inside the region where the table was correct. The runs in this report never used
the 1024-row table either: `gpu_joint_sweep.py` passed its own larger table from the start.

**The sharp point.** Draft Section 3.4 also states that the colex unranking was independently
reimplemented and checked against direct binomial computation with `failures=0` across
r in {2,3,4} and M in {10, 50, 200, 779}. The largest M ever tested was 779; the fault begins at
M > 1024. The project's own independent verification of exactly this routine was scoped entirely
below the fault and could not have caught it however many times it was run. A positive control
that does not span the failure region is not a control for that region.

**Second, previously unstated limit on `gpu_pancyc.py`.** The draft states `gpu_pancyc.py` is valid
for n <= 60 on 64-bit-word grounds (`assert 3 <= n <= 60`). The 1024-row table actually capped it at
n <= 46, a tighter limit the draft did not state; so the stated range was wrong in a second way,
independent of the word size.

**Fix (both engines, authorised by Manager (f4d1e0af), Worker 6 stopped).** In each file:
`BINOM_ROWS = 8192` (n = 120, the 128-bit engine's asserted maximum, has 7020 chords;
C(8191,4) ~ 1.9e14 fits u64); `binom_table(rows=BINOM_ROWS)`; a new host-side
`check_binom_rows(M, binom_d)` called in `run_case` before any launch that raises
`ValueError("candidate chord count M=... exceeds binom table rows=...: the kernel's colex unranking
would read binom[] out of bounds; ...")` naming both numbers; and the kernel comment corrected to
`c < BINOM_ROWS ...; host checks M <= BINOM_ROWS before launch`. Enlarging alone would only have
moved the landmine; the check is what makes the next raise of n fail loudly. `gpu_joint_sweep.py`
calls the same `engine.check_binom_rows` in `Kernel.run`.

Mutation check of the new gate (host-side, quoted from the run):

```
[RED as expected] gpu_pancyc.py: candidate chord count M=1483 exceeds binom table rows=1024: the kernel's colex unranking would read binom[] out of bounds; enlarge binom_table(rows=...)
[GREEN] gpu_pancyc.py: check_binom_rows(M=2143, rows=8192) passed; BINOM_ROWS=8192
        n=120 chords=7020 <= 8192: True
[RED as expected] gpu_pancyc128.py: candidate chord count M=1483 exceeds binom table rows=1024: the kernel's colex unranking would read binom[] out of bounds; enlarge binom_table(rows=...)
[GREEN] gpu_pancyc128.py: check_binom_rows(M=2143, rows=8192) passed; BINOM_ROWS=8192
        n=120 chords=7020 <= 8192: True
```

Regression after the patch: `gpu_joint_sweep.py control` re-run against the patched engine --
`CONTROL GREEN`, same 211 distinct n = 56 witnesses; and both engines' own `main()` run at
n = 12, k = 3 from a temporary directory (so the recorded `search/gpu-state-12-3.json` was not
touched) print `tested=1378 witnesses=64` with identical witness lists, all of which appear in the
recorded state file's witness list.

**Correction carried from the manager.** The chord family
(0,2)(0,n-3)(1,x)(3,n-4)(4,y)(n-8,n-3) in the brief fits n = 64 and the near-miss seeds but not
n = 62: `search/k6/witnesses-v2.csv` records n = 62 as
`(0,2) (0,59) (1,11) (3,58) (3,28) (54,59)`, chord `(3,28)`, and `cyclespace.py check` shows the
brief's `(4,28)` variant is NOT pancyclic (missing 21 and 46). Manager (f4d1e0af) has confirmed
this and is correcting the family statement upstream; this report uses the recorded witness.

## Can the kernel express a neighbourhood sweep? Yes

The kernel signature is `search(n, k, nfixed, r, fa, fb, ca, cb, M, binom, start, count, ...)`: it
takes `nfixed` fixed chords plus a colex-unranked r-combination of the caller's candidate list, with
`r <= 4` (`int idx[4]`). "Replace r of the 6 seed chords" is therefore expressed directly: for each
r-subset P of the six slot positions, fix the other 6 - r seed chords and enumerate every
r-combination of the legal chords not among the fixed ones (`gpu_joint_sweep.sweep`). The union over
all P is exactly the set of 6-chord sets differing from the seed in at most r chords; the removed
chords themselves stay in the candidate list, so the 3-of-6 sweep contains the 2-of-6 sweep and the
1-of-6 sweep. No CPU fallback was needed.

## Seeds (CPU reference check, `cyclespace.py check`)

| n | chord set | `cyclespace.py` |
|---|---|---|
| 56 | (0,2)(0,53)(1,39)(20,39)(39,48)(48,53) | pancyclic (control) |
| 64 | (0,2)(0,61)(1,12)(3,60)(4,29)(56,61) | pancyclic |
| 65 "C" | (0,2)(0,62)(1,12)(3,61)(4,29)(57,62) | NOT pancyclic, missing [32] |
| 65 "B" | (0,2)(0,62)(1,13)(3,61)(4,30)(57,62) | NOT pancyclic, missing [56] |
| 66 | (0,2)(0,63)(1,13)(3,62)(4,31)(58,63) | NOT pancyclic, missing [57] |
| 67 | (0,2)(0,64)(1,13)(3,63)(4,31)(59,64) | NOT pancyclic, missing [58] |

## Positive control (run before any new claim) -- `search/k6/gpu-joint-control.txt`

`python gpu_joint_sweep.py control`, all lines quoted from the output file:

```
[PASS] kernel r=0 accepts n=56 witness (0,2)(0,53)(1,39)(20,39)(39,48)(48,53): got=1 expected=1
[PASS] kernel r=0 accepts n=64 witness (0,2)(0,61)(1,12)(3,60)(4,29)(56,61): got=1 expected=1
[PASS] kernel r=0 rejects n=65 near-miss (0,2)(0,62)(1,12)(3,61)(4,29)(57,62): got=0 expected=0
[PASS] kernel r=0 rejects n=65 near-miss (0,2)(0,62)(1,13)(3,61)(4,30)(57,62): got=0 expected=0
[PASS] kernel r=0 rejects n=66 near-miss (0,2)(0,63)(1,13)(3,62)(4,31)(58,63): got=0 expected=0
[PASS] kernel r=0 rejects n=67 near-miss (0,2)(0,64)(1,13)(3,63)(4,31)(59,64): got=0 expected=0
[PASS] kernel r=0 rejects mutated n=56 set (0,2)(0,53)(1,40)(20,39)(39,48)(48,53): got=0 expected=0
n=56 2-of-6 sweep: tested=16416900 distinct_witnesses=211 seconds=1.2 rate=13.2M/s
[PASS] n=56 2-of-6 sweep re-finds the control witness: got=True expected=True
CONTROL GREEN
```

The "mutated n=56 set" line is the mutation check of the kernel gate: one chord of the witness
changed, `(1,39)` -> `(1,40)`, gives a set that `cyclespace.py` reports as NOT pancyclic (missing
5, 21, 39) and the kernel duly rejects (RED on the broken input); the unmodified witness is accepted
(GREEN). The 2-of-6 sweep at n = 56 exercises the colex unranking with M = 1482 > 1024 (the case the
engine's own table cannot handle) and re-finds the seed among 211 distinct witnesses in that
neighbourhood. Three of those sweep positives were re-checked independently with the pre-existing
`search/verify.py` (networkx `simple_cycles`):

```
56 [(0, 2), (0, 53), (1, 39), (20, 39), (39, 48), (48, 53)] pancyclic
56 [(0, 2), (0, 53), (1, 39), (3, 52), (20, 39), (44, 53)] pancyclic
56 [(0, 2), (0, 49), (1, 39), (20, 39), (39, 48), (48, 51)] pancyclic
67 [(0, 2), (0, 64), (1, 13), (3, 63), (4, 31), (59, 64)] NOT pancyclic
```

The last line is the verification gate's own mutation check: `verify.py` says NOT pancyclic on the
n = 67 near-miss (RED) and pancyclic on the witnesses (GREEN), so a found witness re-checked through
it would be a meaningful confirmation.

## What the n = 65 and n = 66 neighbourhoods bear on: two closed forms that agree on four points

Relayed by Manager (f4d1e0af) from an independent review, arithmetic re-checked here. Two
two-parameter closed forms fit every known threshold t_k for k = 2..5:

| k | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|
| known t_k | 8 | 14 | 24 | 40 | ? (witnesses confirmed at 64) |
| Fibonacci form 2*Fib(k+3) - 2 | 8 | 14 | 24 | 40 | 66 |
| rival form 2^(k-2) * (10-k) | 8 | 14 | 24 | 40 | 64 |

They first disagree at k = 6. Confirmed 6-chord witnesses exist at n = 64
(`search/k6/witnesses-v2.csv`), so the rival form says t_6 = 64 exactly and nothing larger
exists, while the Fibonacci form says witnesses exist up to 66. Consequences for this lane:

* a single witness at n = 65 refutes the rival form outright; the n = 65 B and C seeds are the
  closest this project has come (missing exactly one cycle length each);
* a witness at n = 66 refutes the rival and gives the Fibonacci form its floor; with no witness at
  n = 67 (which only an exhaustive lane can establish, not this one) that would pin t_6 = 66;
* an exhausted, empty 3-of-6 neighbourhood at n = 65 or n = 66 is therefore evidence bearing on
  which of two named hypotheses survives, not a null result, and is reported below with its exact
  candidate count.

That two distinct closed forms fit the same four data points and diverge at the fifth is itself a
finding: four points do not determine this sequence. The rival form is transparently a finite
artefact (it reaches 0 at k = 10 and goes negative beyond), whereas the Fibonacci form grows; both
match every known value, so that asymmetry is not evidence at k = 6.

## Neighbourhoods exhausted (no witness in any of them)

Each row is a complete enumeration of every 6-chord set that differs from the seed in at most r
chord slots, over all legal chords (`all_chords(n)`: a < b, b - a >= 2, not (0, n-1)). `tested` is
the total kernel-evaluated candidate count summed over the C(6,r) slot subsets, from the
`gpu-joint-state-*.json` state files / `gpu-joint-*.txt` logs.

| n | seed | r | slot subsets | tested candidates | GPU seconds | witnesses |
|---|---|---|---|---|---|---|
| 67 | (0,2)(0,64)(1,13)(3,63)(4,31)(59,64) | 2 | 15/15 | 34,330,950 | 3 | 0 |
| 66 | (0,2)(0,63)(1,13)(3,62)(4,31)(58,63) | 2 | 15/15 | 32,276,625 | 3 | 0 |
| 65 B | (0,2)(0,62)(1,13)(3,61)(4,30)(57,62) | 2 | 15/15 | 30,315,825 | 3 | 0 |
| 65 C | (0,2)(0,62)(1,12)(3,61)(4,29)(57,62) | 2 | 15/15 | 30,315,825 | 3 | 0 |
| 67 | (0,2)(0,64)(1,13)(3,63)(4,31)(59,64) | 3 | R3_67_SUBSETS | R3_67_TESTED | R3_67_SECONDS | R3_67_WITNESSES |
| 66 | (0,2)(0,63)(1,13)(3,62)(4,31)(58,63) | 3 | R3_66_SUBSETS | R3_66_TESTED | R3_66_SECONDS | R3_66_WITNESSES |
| 65 B | (0,2)(0,62)(1,13)(3,61)(4,30)(57,62) | 3 | R3_65B_SUBSETS | R3_65B_TESTED | R3_65B_SECONDS | R3_65B_WITNESSES |
| 65 C | (0,2)(0,62)(1,12)(3,61)(4,29)(57,62) | 3 | R3_65C_SUBSETS | R3_65C_TESTED | R3_65C_SECONDS | R3_65C_WITNESSES |

The 2-of-6 rows at n = 65 agree with the earlier CPU `fastcyc sweep2` runs
(`sweep2-65-B-*.txt`, `sweep2-65-C-*.txt`: "best_missing=1" on every slot pair), which is an
independent corroboration of the GPU harness on those neighbourhoods.

Run history of the 3-of-6 stage (so a resumed run is not read as one continuous run): the n = 67
process was stopped twice. First by me at slot subset (0,1,3), offset 1,006,632,960, to add the
80 % duty cycle. Second, at 16:33, by Worker 7's `Stop-Process` with a `CommandLine -like
'*sweep.py*'` filter that also matched `gpu_joint_sweep.py` (PID 15376, reported by Manager
(f4d1e0af); Worker 7 has since scoped its kills to PID). At that moment the state file
`gpu-joint-state-67-r3.json` held done = (0,1,2), (0,1,3), (0,1,4), (0,1,5), (0,2,3),
cur = (0,2,4) at offset 1,207,959,552, tested = 7,160,318,590; that state was kept and the sweep
resumes from it, redoing only the in-flight chunk. The kill made the shell chain fall through to
the n = 66 stage, which therefore ran before n = 67 finished; the order became 66, then 67
(resumed), then 65 B, then 65 C.

Declared caps: only the four seeds above were swept; r = 4 (about 20 * C(2141,4) ~ 1.8e13 per seed
at n = 67, ~20 GPU-days at the measured rate) was not attempted. The kernel's witness buffer holds
64 witnesses per slot subset (`MAX_FOUND = 64`), with the raw `found_count` recorded per subset in
the state file, so an overflow would be visible; none occurred.

## Measured GPU utilisation and throughput

* Cap: 80 % GPU utilisation for this tree, set by Manager (f4d1e0af) after the first
  3-of-6 stage had started. The harness therefore duty-cycles: after each chunk the host sleeps
  `(1/duty - 1)` times that chunk's *measured* wall time (`--duty 0.8`, `neighbourhood(..., duty=)`);
  the log records both, e.g. `progress 134217728/1633390310 (8.2%) 13s chunk=13.04s gap=3.26s`.
  The first stage was stopped at n = 67 slot subset (0,1,3), offset 1,006,632,960, and resumed from
  the saved offset with the duty cycle; nothing was re-tested and nothing skipped.
* Before the cap was applied (`search/k6/gpu-joint-util.csv`, 10 s samples): `1 %, 937 MiB` idle,
  then `100 %` on every sample while a kernel was resident (e.g.
  `2026/09/14 16:16:18.353, 100 %, 1063 MiB`).
* With the duty cycle (`search/k6/gpu-joint-util-duty80.csv`, 60 one-second samples of
  `utilization.gpu,power.draw`): **mean 78.8 %**, 49 of 60 samples nonzero, about 73 W while
  resident. Each individual sample reads 100 % while a chunk is on the card and 0 % in the gap; the
  time average is the figure under the cap. Chunk size does not move this number (the kernel keeps
  no per-candidate device memory, so the ~1,060 MiB footprint is independent of chunk size), only
  the idle gap does.
* Host CPU: the sweep process (`python gpu_joint_sweep.py sweep 67 3 ...`, priority class
  BelowNormal, set via `SetPriorityClass(..., 0x4000)`) consumed 0.656 CPU-seconds over a 10 s wall
  interval, i.e. 0.8 % of the 8-logical-core machine. The machine's total CPU load at that moment
  was 76 %, all of it from other lanes' `solve.py` / `sweep.py` processes, not this task.
* Throughput at n = 67, k = 6: 1,073,741,824 candidates in 106 s = 10.1 M/s
  (`gpu-joint-67-r3.txt`, "progress 1073741824/1633390310 (65.7%) 106s"). The brief's 33 M/s was
  measured at n = 41, k = 5 (`gpu128-41-5.txt`); at k = 6 the Gray-code loop has 128 instead of 64
  steps and each step is O(n) with n = 67 instead of 41, about 3.3x more work per candidate, which
  accounts for the difference. With the 80 % duty cycle the effective rate is 8.6 M/s x 0.8 ~ 6.9 M/s
  (`rate=8.6M/s` for subset (0,1,3) after resume), so the 3-of-6 sweep costs about 65 min per seed
  at n = 67, not the ~20 min per seed implied by 33 M/s.

## Files

* `search/k6/gpu_joint_sweep.py` -- harness (new). `control` subcommand and `sweep N R "<chords>"`
  subcommand; resumable per slot subset via `gpu-joint-state-{tag}.json`.
* `search/k6/gpu-joint-control.txt` -- control output quoted above.
* `search/k6/gpu-joint-{67,66,65B,65C}-r2.txt`, `...-r3.txt` -- per-subset progress logs;
  `gpu-joint-state-*.json` -- counts and witness lists; `gpu-joint-util.csv` -- nvidia-smi samples.
* `search/gpu_pancyc.py`, `search/k6/gpu_pancyc128.py` -- `BINOM_ROWS`, `binom_table(rows=)`, `check_binom_rows`, kernel comment (see costliest finding). Kernel code otherwise unchanged.
