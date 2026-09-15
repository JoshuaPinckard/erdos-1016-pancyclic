# Exact t_k by the shape/CSP reformulation

Scope: build and validate an exact algorithm for `t_k` = the largest `n` for which
some `C_n` plus `k` chords is pancyclic, via the shape/CSP reformulation; reproduce
`t_2..t_5 = 8, 14, 24, 40` from scratch as a positive control; then report k=6.

Code added under `search/shapecsp/`. Nothing under `search/k6/` was modified.

## Summary

| | result |
|---|---|
| `t_2, t_3, t_4, t_5` | **8, 14, 24, 40** -- exact, from scratch, no lower bound supplied, zero abandoned searches |
| `h(41) > 5` | **independently confirmed.** No 5-chord pancyclic graph on 41 vertices exists: 308 eligible shapes, `sat=0 gaveup=0`, by a method sharing no code with the GPU enumeration (section 4a) |
| `t_6` | **not resolved.** Bracket `67 <= t_6 <= 93` (a-priori upper bound was 129). **All seven** known witness shapes are now closed at their exact maxima, the best being 67 -- any larger k=6 graph needs a shape nobody has looked at |
| k=6 ceiling | independent confirmation of the published `M(6) = 109` (Rautenbach-Stella 2005), hence `n <= 111`; the enumeration reproduces `M(k)` for **all** of k=2..6 by a different route |
| solver soundness | false-negative control passes on all seven witness shapes; red/green gate mutation pair; 201-graph cross-check of the reformulation against `networkx` ground truth |
| k=3 vs GMW13 | 14 shapes vs 14 published types; the refinement structure matches too, but a type-for-type bijection is **not verified** (section 4b) |
| shapes | 3 / 14 / 103 / 1236 / 21878 for k = 2..6, of which 1 / 9 / 86 / 1157 / **21324** are the degenerate families |
| costliest finding | an earlier revision of section 0 claimed `t_6 <= 93` was established by **level n=94 alone**. A two-line k=2 command refutes that reading of a level; the bound is unchanged but rests on the **contiguous block n=94..111**, every level of which is load-bearing (section 0a) |
| costliest modelling finding | the perfect-matching-only shape model returns the **wrong** maximum: 22 instead of `t_4 = 24`, 37 instead of `t_5 = 40` |
| solver optimisation | the review's `lastarc` patch is applied and shown answer-preserving where it counts: **1406 record comparisons across two builds, zero disagreements**, 1099 SAT witnesses re-materialised; `sweep.py` carried the same defect family the review found in the other two drivers (section 5c) |
| result integrity | the four review defects in `level.py`/`satcheck.py` are repaired, the six contract tests pass, and all four gates are mutation-checked RED/GREEN. Three of those tests were **vacuous** after the repair and were strengthened (section 0a) |

---

## 0. A defect in this report's own earlier description, found late and corrected

`bb.exe` does **not** decide a single `n`, which is what sections of this report
previously said it did. Its first argument is a **lower cutoff**: for each shape
it walks `n` from that shape's own cap downward and stops at the first feasible
value. So

    "LEVEL k=6 n=94 ... sat=0"

does not mean "no shape reaches exactly 94". It means **no eligible shape reaches
any n >= 94**.

Cause, stated plainly because it is the failure mode this codebase keeps
re-finding: early on I rewrote `bb.c` from a range loop to a single-`n` form with
a `str.replace` whose anchor no longer matched after an earlier edit. The replace
silently did nothing, and I checked only that the file still compiled. The
patches in this report now assert their anchor and refuse to write a no-op.

**Effect on the conclusions: none, and they are stronger than stated.**

- `t_6 <= 93` holds -- but **on the contiguous block n=94..111, not on level 94
  alone.** An earlier revision of this section claimed the single level at n=94
  established it and that 95..111 were redundant. That claim is false and is
  withdrawn; see section 0a, finding 1, for the measured counterexample.
- `t_5 <= 40` and `h(41) > 5` hold, on the same contiguous-block reading.
- The eligibility argument closes only over a block. Hall's condition at `n0` is a
  *necessary* condition for feasibility at `n0`, so any shape feasible at `n0` is
  eligible **at the level whose cutoff is exactly `n0`** -- but it need not be
  eligible at any lower cutoff, because Hall at the cutoff is not monotone in n.
  So a shape feasible at some `n0 >= 94` is caught by the level at `n0`, and every
  such level from 94 to the largest cap 111 has returned UNSAT with `gaveup=0`.
  Drop any level from that range and the argument no longer closes.
- No reported number is wrong. SAT lines were only ever emitted at k=2,3,4 and at
  k=5 n=40, and every one of those witnesses was independently materialised and
  confirmed to have exactly the stated `n`.

---

## 0a. Result-integrity gates: what they now stop, and the two defects found holding them

This section is the record of the integrity lane (Worker 13, 2026-09-15), taking
the four defects an independent review (Builder `c3a46073`) found in `level.py`
and `satcheck.py`. Its own costliest finding is not one of those four.

### Finding 1 (costliest) -- this report asserted a bound argument that a two-line command refutes

Section 0 above previously read:

> `t_6 <= 93` holds. It is in fact established by the single level at n=94 on its
> own; levels 95..111 are redundant confirmations of it.

**That is false.** `t_6 <= 93` is the only upper bound on `t_6` in this report, so
the sentence overstated the strength of the evidence for the paper's single k=6
conclusion. It is withdrawn above.

The claim rests on reading `sat=0` at cutoff `n` as "no shape reaches any value
`>= n`". Eligibility is decided **at the cutoff** by cap and then Hall, and Hall at
the cutoff is *not monotone in n*: a shape can fail Hall at cutoff `n`, never be
searched at that level, and still be feasible at some larger `n0`. Measured, at
k=2 where the whole space is three shapes:

```
$ python level.py 2 3 1000000
LEVEL k=2 n=3 shapes=3 eligible=0 sat=0 gaveup=0 search_seconds=0.0 total_seconds=0.0

$ python level.py 2 8 1000000
   SAT n=8 (cutoff 8) b=3 chords=((0, 1), (0, 2)) arcs=2,3,3 VERIFIED [(0, 2), (0, 5)] -> pancyclic
   SAT n=8 (cutoff 8) b=4 chords=((0, 1), (2, 3)) arcs=2,1,3,2 VERIFIED [(0, 2), (3, 6)] -> pancyclic
   SAT n=8 (cutoff 8) b=4 chords=((0, 2), (1, 3)) arcs=1,1,2,4 VERIFIED [(0, 2), (1, 4)] -> pancyclic
LEVEL k=2 n=8 shapes=3 eligible=3 sat=3 gaveup=0 search_seconds=0.0 total_seconds=0.0
```

The level at cutoff 3 is a clean `sat=0 gaveup=0` with nothing abandoned, yet
three shapes reach n=8 >= 3, each independently materialised and confirmed
pancyclic. A single clean level therefore does not exclude larger n.

**The bound itself survives, unchanged at `t_6 <= 93`**, because the levels were
actually run as a contiguous block: 111..102 with `eligible=0`, then 101..94 with
`sat=0 gaveup=0` (table in section 7). A shape feasible at any `n0` in 94..111 is
eligible at the level whose cutoff is exactly `n0`, and that level refuted it.
What changes is that **every** level in 94..111 is load-bearing; none is
redundant. The coverage audit later in this report already stated the block
reading correctly -- section 0 contradicted it, and section 0 was the wrong one.

`level.py`'s docstring now carries the rule it has to enforce: *"A single `sat=0`
level therefore does NOT establish 'no shape reaches any value >= n'. ... Cite the
block, never a single level."*

This also bounds a claim nobody has made yet: n=93 and n=92 are 0-byte holes, so
the descent below 93 has no coverage at all, and one UNSAT level at 93 alone would
not tighten the bound to 92 either -- that needs 93 joined onto the block.

### Finding 2 -- the four repaired gates were live, and the tests holding them were vacuous

The six contract tests pass against the repaired code. That was not evidence,
because three of them passed *with the gate deleted*.

`level.py`'s repair ends every path in `sys.exit(...)`, including the clean one
(`sys.exit(1 if gu else 0)`). The reviewer's harness classifies the run by
exception:

```python
    except (ValueError, RuntimeError, subprocess.CalledProcessError, SystemExit):
        return output.getvalue(), True          # "rejected"
```

so after the repair **every** run returned `rejected=True`, and each assertion of
the form `assertTrue(rejected or not re.search(...))` was unconditionally true.
The mutation check caught it: disabling the non-zero-exit gate outright left the
test green.

```
BROKEN level.py rejects a non-zero solver exit
         mutant  'if p.returncode != 0:' -> 'if False:  # MUTANT: gate disabled'
         RED     test_nonzero_solver_exit_cannot_certify_zero_sat_zero_gaveup  exit=0  OK
```

Fixed in the harness, not in the assertions -- the reviewer's six assertions are
unchanged, byte for byte:

```python
    except SystemExit as e:
        # A clean level ends in sys.exit(0), so treating EVERY SystemExit as a
        # rejection made all three level.py contracts below vacuously true: they
        # passed with the gates deleted.  Only a non-zero status is a rejection.
        return output.getvalue(), bool(e.code)
```

Direct probe of the repaired `level.py` behind the harness, confirming the gates
themselves were always correct and only their tests were blind:

```
child exit 23, 3 valid UNSAT : SystemExit(1)  "LEVEL k=2 n=8 FAILED -- solver exited 23 ..."
child exit 0, empty output   : SystemExit(1)  "LEVEL k=2 n=8 FAILED -- 3 of 3 eligible shapes produced no terminal record ..."
invalid SAT witness          : SystemExit(1)  "LEVEL k=2 n=8 FAILED -- shape 1 ...: verify.check REJECTS the materialised graph: n=8 missing [6]"
CLEAN run, all UNSAT         : SystemExit(0)  "LEVEL k=2 n=8 shapes=3 eligible=3 sat=0 gaveup=0 ..."
```

### The six contract tests

`search/shapecsp/test_review_contracts.py`, run by me on the repaired tree:

```
Ran 6 tests in 1.561s

OK
```

Positive control -- the same strengthened harness against the **pre-fix**
`level.py` and `satcheck.py` read out of `HEAD` (no checkout; the blobs were
written in, run, and restored byte-for-byte):

```
FAIL: test_invalid_witness_is_not_reported_as_sat
AssertionError: False is not true :    SAT n=8 (cutoff 8) b=3 chords=((0, 1), (0, 2)) arcs=2,2,4
FAIL: test_missing_results_cannot_certify_zero_sat_zero_gaveup
AssertionError: False is not true : LEVEL k=2 n=8 shapes=3 eligible=3 sat=0 gaveup=0 ...
FAIL: test_nonzero_solver_exit_cannot_certify_zero_sat_zero_gaveup
AssertionError: False is not true : LEVEL k=2 n=8 shapes=3 eligible=3 sat=0 gaveup=0 ...
FAIL: test_satcheck_budget_failure_has_nonzero_exit
AssertionError: 0 == 0 : n=56 b=7 cap=59: INCONCLUSIVE -- node budget hit  [0.8s]
Ran 6 tests in 1.875s
FAILED (failures=4)
restored: OK
```

Four failures, matching the four the review reported, and the same suite is green
on the repaired code. The suite discriminates.

### Mutation check of the four gates

`search/shapecsp/mutation-check.py`. Its log is `*.log` and therefore gitignored, so
the full output is quoted below and is reproduced by running the script.
Each gate is disabled by an exact substitution whose anchor must occur exactly
once, the covering test must go RED **with `failures=1`**, the file is restored
from a byte copy and the test must report `OK`. An `errors=1` RED is reported as
BROKEN, not as a pass: a mutant that crashes stops the test for a reason unrelated
to the gate, so the gate's real protection would go untested. The mutants
reproduce the original defects rather than deleting an `if` -- for the
missing-record gate, deleting the `if` alone dies on `KeyError`, which proves only
that crashing is fail-closed, so that mutant also reverts the reporting loop to
`for i in sorted(recs)`.

```
OK     level.py rejects a non-zero solver exit
         mutant  'if p.returncode != 0:' -> 'if False:  # MUTANT: gate disabled'
         RED     test_nonzero_solver_exit_cannot_certify_zero_sat_zero_gaveup  exit=1  FAILED (failures=1)
         GREEN   test_nonzero_solver_exit_cannot_certify_zero_sat_zero_gaveup  exit=0  OK
OK     level.py rejects a missing terminal record
         mutant  'if missing:' -> 'if False:  # MUTANT: gate disabled'
         mutant  'for i in range(1, len(elig) + 1):' -> 'for i in sorted(recs):  # MUTANT: report only what came back'
         RED     test_missing_results_cannot_certify_zero_sat_zero_gaveup  exit=1  FAILED (failures=1)
         GREEN   test_missing_results_cannot_certify_zero_sat_zero_gaveup  exit=0  OK
OK     level.py rejects a SAT the graph checker refuses
         mutant  'got, why = V.check_record(line, b, ch, lows, cap, n)' -> "# MUTANT: take the solver's SAT claim without the independen"
         RED     test_invalid_witness_is_not_reported_as_sat  exit=1  FAILED (failures=1)
         GREEN   test_invalid_witness_is_not_reported_as_sat  exit=0  OK
OK     satcheck.py's exit status carries its verdict
         mutant  'sys.exit(0 if not fails else 1)' -> 'sys.exit(0)  # MUTANT: gate disabled'
         RED     test_satcheck_budget_failure_has_nonzero_exit  exit=1  FAILED (failures=1)
         GREEN   test_satcheck_budget_failure_has_nonzero_exit  exit=0  OK

MUTATION CHECK: 4/4 gates went RED (failures=1) when disabled and GREEN when restored
```

`level.py` and `satcheck.py` were verified byte-identical to their pre-mutation
copies afterwards (`sha256sum -c`: `level.py: OK`, `satcheck.py: OK`).

### What the four repaired gates now refuse

| review defect | repaired behaviour | symbol |
|---|---|---|
| non-zero-exit child accepted as `sat=0` | `LEVEL ... FAILED -- solver exited N`, exit 1 | `level.py` `fail` |
| empty output accepted as `sat=0` | `... produced no terminal record; an incomplete run is UNKNOWN, not sat=0`, exit 1 | `level.py` `missing` |
| SAT accepted though the graph checker rejects it | `verify.check REJECTS the materialised graph`, exit 1 | `verify.py` `check_record` |
| `satcheck.py` prints FAILED, exits 0 | exit status carries the verdict | `satcheck.py` `sys.exit(0 if not fails else 1)` |

`check_record` re-derives arc count, lower bounds, sum, the `[cutoff, cap]` range
and then materialises the graph through `verify.check`; it returns
`(result, None)` or `(None, why)` so a rejection cannot be unpacked as a witness.
`hunt.py` routes every SAT through the same function and treats a refused SAT as a
solver defect that stops the run.

### Not done, and why -- named rather than left to inference

- **`lastarc.patch` differential: DONE, in the lane that was holding it.** Results
  in section 5c below -- 1406 record comparisons across two builds, zero
  disagreements, 1099 SAT witnesses independently materialised and checked.
- **k=2/3/4 control after the patch: DONE on both machines**, section 5c.
- **Range-mode descent from n=93: not started.** I deliberately left the laptop
  alone. A second agent was mid-build there, and the box was at load average
  22.61 on 16 cores; adding an 11-worker descent would have slowed the hunt, that
  differential and two other trees at once. Changing the hunt's worker count is
  also no longer free: it costs a restart, and only `hunt.py`'s new
  `hunt-k6-n68-exact.done` resume file keeps that from discarding decided shapes.
- **n=68 exact hunt: running and healthy, not finished.** Restarted 00:32 local on
  the patched `bb`, resuming the 24 shapes already decided from
  `hunt-k6-n68-exact.done`; observed 00:35:07 local `# 30/6059 elapsed=193s
  rate=0.031 shapes/s projected_total=53.8h gaveup=0 errors=0`, 5 workers at
  nice 10, every decided record so far UNSAT. **There is no verified witness at
  n >= 68 to report**, and none of the 6059 is decided by anything except a
  completed solver run -- the hunt records only SAT and UNSAT to its `.done` file,
  so a GAVEUP or an execution error is retried rather than counted.


**What was wrong and is now fixed:** `level.py` labelled SAT lines with the
requested cutoff instead of the `n` `bb.exe` returned; `bb.c` did not document its
real contract; and the single-shape timings quoted below are cumulative over
`[n, cap]`, not per-rung, so the marginal cost of each extra rung is the
*difference* between consecutive figures.

---

## 1. Costliest finding: the "perfect matching on 2k points" model returns the wrong number

The brief describes a shape as `H = (2k-cycle plus a perfect matching on those 2k
points)`, with the degenerate families (two chords sharing an endpoint, so fewer
than `2k` branch vertices) called out as something whose omission "makes any
exhaustiveness claim false". That is correct, and it is stronger than a
book-keeping point: on this codebase the perfect-matching-only model produces a
*wrong maximum*, not just a smaller shape count.

Measured, by running the same exact solver over the restricted and the full
enumerations (`search/shapecsp/nondegenerate-maxima.txt`, `gates-green.txt`):

| k | max n over `b = 2k` shapes only | true `t_k` | lost |
|---|---|---|---|
| 3 | 14 | 14 | 0 |
| 4 | **22** | **24** | 2 |
| 5 | **37** | **40** | 3 |

So the perfect-matching-only search reports 22 for k=4 and 37 for k=5, missing
`t_4 = 24` and `t_5 = 40`; the gap grows with k.

The k=4 optimum lives at `b = 7`: shape `((0,2),(1,4),(1,5),(3,6))` -- branch point
1 carries two chords -- with arc lengths `[1,1,1,2,2,11,6]`, i.e. the graph
`C_24 + {(0,2),(1,5),(1,7),(3,18)}`, independently confirmed pancyclic by
`verify.check` (see section 5).

This is not an edge case for k=6 either. Of the 21878 k=6 shapes, **21324 (97.5%)
are degenerate** -- only 554 are perfect matchings on 12 points.

### Every 6-chord witness this project has found is degenerate. All nine.

Each of these was re-verified in this lane -- rebuilt as a graph, checked to have
exactly 6 chords with none duplicating a cycle edge, cycles enumerated with
`networkx` and compared against `[3,n]` -- and then canonicalised to its shape:

| n | branch vertices b | chord degrees | canonical shape |
|---|---|---|---|
| 56 | 7 | 3,2,2,2,1,1,1 | `((0,1),(0,3),(0,6),(2,4),(4,5),(5,6))` |
| 60 | 8 | 2,2,2,2,1,1,1,1 | `((0,1),(0,6),(1,2),(2,4),(3,5),(4,7))` |
| 61 | 9 | 2,2,2,1,1,1,1,1,1 | `((0,1),(0,7),(1,3),(2,6),(3,5),(4,8))` |
| 63 | 9 | 2,2,2,1,1,1,1,1,1 | `((0,1),(0,7),(1,3),(2,5),(4,6),(4,8))` |
| 62 | 9 | 2,2,2,1,1,1,1,1,1 | `((0,1),(0,7),(1,3),(2,5),(4,6),(4,8))` |
| 63 | 9 | 2,2,2,1,1,1,1,1,1 | `((0,1),(0,7),(1,3),(2,5),(4,6),(4,8))` |
| 64 | 10 | 2,2,1,1,1,1,1,1,1,1 | `((0,1),(0,8),(1,3),(2,6),(4,9),(5,7))` |
| 65 | 11 | 2,1,1,1,1,1,1,1,1,1,1 | `((0,2),(0,8),(1,5),(3,9),(4,6),(7,10))` |
| 66 | 11 | 2,1,1,1,1,1,1,1,1,1,1 | `((0,2),(0,8),(1,5),(3,9),(4,6),(7,10))` |
| 67 | 11 | 2,1,1,1,1,1,1,1,1,1,1 | `((0,2),(0,8),(1,5),(3,9),(4,6),(7,10))` |

**Not one of the nine has b = 12.** A search over the 554 perfect-matching shapes
would have enumerated a space containing none of them. Note also how few distinct
shapes there are: the nine witnesses sit on only **six** shapes -- n=62 and 63
share one, and n=65, 66 and 67 all share the b=11 shape. The degenerate families are not an
extra tail of smaller cases to be added for completeness; at k=6 they are 97.5% of
the space and they contain 100% of the known solutions.

A trap worth recording, because it cost me a wrong entry. The repository stores
near-misses and witnesses **in the same files and the same format**, and I first
picked the wrong rows for n=62 and n=65:

```
n=62  (0,2)(0,59)(1,11)(3,58)(3,28)(54,59)    PANCYCLIC        <- the witness
n=62  (0,2)(0,59)(1,45)(3,58)(29,54)(54,59)   missing [29]     <- a "BEST ... missing=1" sweep line
n=65  (0,2)(0,58)(1,13)(3,59)(4,31)(57,60)    PANCYCLIC        <- the witness
n=65  (0,2)(0,62)(1,12)(3,61)(4,29)(57,62)    missing [32]     <- the near-miss seed a sweep was built around
```

All four verified here. Anything reading chord lists out of these logs must check
each one rather than pattern-match the filename or the surrounding `n=`.

Taking the earliest of the seven in detail -- the 56-vertex one from
`search/k6/witnesses.csv`,

```
56,"(0,2) (0,53) (1,39) (20,39) (39,48) (48,53)"
```

has branch points `{0, 1, 2, 20, 39, 48, 53}` -- **7 branch vertices, not 12**;
vertex 39 carries three chords, vertices 0, 48, 53 carry two. It is a degenerate
shape. A k=6 enumeration over perfect matchings alone would not contain the best
graph this repository has already found.

## 2. Second finding: the 2^(k+1)-1 cycle bound is loose, and that is the leverage

The brief's `at most 2^(k+1)-1` cycles is right but not attained for k >= 4.
Measured maxima over all shapes (`search/shapecsp/shape-census.txt`):

| k | shapes | non-degenerate (b=2k) | degenerate (b<2k) | b range | max #cycles | `2^(k+1)-1` |
|---|---|---|---|---|---|---|
| 2 | 3 | 2 | 1 | 3..4 | 7 | 7 |
| 3 | 14 | 5 | 9 | 3..6 | 15 | 15 |
| 4 | 103 | 17 | 86 | 4..8 | 29 | 31 |
| 5 | 1236 | 79 | 1157 | 4..10 | 56 | 63 |
| 6 | 21878 | 554 | 21324 | 4..12 | **109** | 127 |

Shapes per number of branch vertices `b`:

```
k=2  {3:1, 4:2}
k=3  {3:1, 4:4, 5:4, 6:5}
k=4  {4:4, 5:17, 6:38, 7:27, 8:17}
k=5  {4:2, 5:28, 6:153, 7:333, 8:417, 9:224, 10:79}
k=6  {4:1, 5:25, 6:347, 7:1736, 8:4604, 9:6586, 10:5600, 11:2425, 12:554}
```

Every cycle of `G` has length in `[3, n]` and realises exactly one length, so
covering `[3, n]` forces a *surjection* from the cycle forms onto `[3, n]`, hence

    n <= (#distinct cycle forms of that shape) + 2.

For k=6 the largest such cap over all 21878 shapes is **111**, not the a-priori
129. This per-shape cap is also the pruning rule that makes the sweep finite:
a shape with 60 forms is simply irrelevant to any `n > 62`.

> **This is not a new bound -- it is an independent confirmation of a published
> one, and that is worth more here.** `M(k)`, the maximum number of cycles in a
> Hamiltonian graph with `k` chords, is known exactly for `k <= 10`:
> Rautenbach and Stella (2005) give it, and `papers/REPORT-cyclecounts.md` already
> records `6 | 109 | Rautenbach-Stella 2005, Section 3, Fig. 3` with
> `N = M+2 = 111`. The `n <= 111` ceiling was on file before this work. What the
> shape enumeration adds is an **independent computational confirmation by a
> different route**: Rautenbach-Stella enumerate Hamiltonian 3-regular graphs of
> order `2k`; this enumerates all shapes up to `D_b` including the degenerate
> ones, then computes cycle spaces. Both agree on every value:
>
> | k | 2 | 3 | 4 | 5 | 6 |
> |---|---|---|---|---|---|
> | published `M(k)` | 7 | 15 | 29 | 56 | 109 |
> | computed here | 7 | 15 | 29 | 56 | 109 |
> | attained at b = | 4 | 6 | 8 | 10 | 12 |
>
> This is the check on the machinery every other number in this report depends on.
> If the enumeration were missing shapes, the maximum could only come out **too
> low**; it does not, at any k. And the last row is a small result in its own
> right: the cycle-count maximum is always attained at `b = 2k`, the
> *non-degenerate* shapes -- matching Rautenbach-Stella's 3-regular extremal
> graphs exactly -- even though, as section 1 shows, every *pancyclicity* optimum
> lives in the degenerate families. The two extremal problems pull in opposite
> directions, which is precisely why a "most cycles" intuition misleads here.

---

## 3. The algorithm

`search/shapecsp/shapes.py` -- enumeration.

A `C_n + k chords` graph is a subdivision of `H = (cycle on the b chord-endpoints,
in their cyclic order) + (the k chords as a simple graph on those b points)`,
with `b <= 2k` and every point carrying at least one chord. `shapes(k)` enumerates
every such `H` up to the dihedral group `D_b`, over **all** `b` from the smallest
with `C(b,2) >= k` up to `2k` -- the degenerate families included.

`cycle_forms(b, chords)` enumerates the cycle space of `H` (dimension
`(b+k)-b+1 = k+1`) and keeps the elements that are a single cycle. Each cycle
becomes a 0/1 linear form

    L_f(a) = sum_{i in A_f} a_i + |X_f|

in the free arc lengths `a_i >= 1` (`>= 2` when a chord duplicates that arc, or the
graph would not be simple), with `n = sum a_i`. Pancyclicity is exactly: the at
most 109 (k=6) forms cover every value in `[3, n]`.

Two solvers, deliberately independent:

- `solve.py` -- CP-SAT (`ortools`), a ladder of pure-feasibility solves.
- `bb.c` / `bb.exe` -- a C branch-and-bound over the arcs. At each node every form
  is confined to an interval `[lo_f, hi_f]` from the unassigned arcs' lower bounds
  and the remaining slack, on both the `L_f` and the `n - L_f` side; covering
  `[3,n]` then requires a matching saturating the values, which for interval
  neighbourhoods the greedy "give value x the admissible form with the smallest
  hi" decides exactly. Sound prune at internal nodes, exact test at leaves.

`sweep.py` / `level.py` / `runlevels.py` drive it: for `n` descending from the
largest per-shape cap, every shape that can still reach `n` is decided. The first
`n` with a SAT shape is `t_k`; every level above it answering UNSAT with zero
GAVEUP is the exhaustive refutation.

### A correction worth recording

An earlier version of the prune used Hall's condition restricted to *intervals of
values*, which is O(m+n) and looked equivalent to the greedy. It is not. With
`n = 8` and form intervals `(4,5) (3,7) (4,5) (6,8) (5,8) (4,5)`, interval-Hall
passes but no matching exists -- the failing set `{3} together with {6,7,8}` is not an
interval. 4000 randomised comparisons against a brute-force augmenting-path
matcher found 13 such disagreements; the greedy and the brute force agreed on all
4000. `bound.py:hall_ok` therefore remains a *necessary condition only* (it is
used as a cheap pre-filter, where soundness is all that is needed) and the search
itself uses the exact greedy. Node counts before and after the rewrite of the
greedy from heap to bitmask are identical (119676301 both ways at k=5, n=48), at
5.3x the speed.

---

## 4. Positive control: t_2, t_3, t_4, t_5 from scratch

Run with no lower bound supplied -- `n` descends from the per-shape cap, so each
result is "no shape reaches any larger n, and this one reaches this n".

```
$ python sweep.py 2 3
RESULT t_2 = 8      gaveup_records=0 total_seconds=0.0
$ python sweep.py 3 3
RESULT t_3 = 14     gaveup_records=0 total_seconds=0.0
$ python sweep.py 4 3
RESULT t_4 = 24     gaveup_records=0 total_seconds=1.0
```

with the witnessing shapes and arc vectors

```
t_2 = 8   b=3  chords ((0,1),(0,2))          arcs 2,3,3
t_3 = 14  b=5  chords ((0,1),(0,3),(2,4))    arcs 3,2,1,1,7
t_4 = 24  b=7  chords ((0,2),(0,5),(1,4),(3,6))  arcs 1,2,2,11,6,1,1
```

`t_2`, `t_3` and `t_4` were additionally reproduced by the *other* solver, CP-SAT,
from an independent model (`search/shapecsp/control-k2-k5.log`), and CP-SAT
independently found the k=5 lower bound `n = 40`:

```
=== k=5 ===
  new best n=34 b=10 chords=((0, 2), (1, 6), (3, 7), (4, 9), (5, 8)) arcs=[1, 1, 1, 15, 8, 1, 1, 1, 3, 2]
  new best n=36 b=10 chords=((0, 2), (1, 5), (3, 7), (4, 8), (6, 9)) arcs=[1, 1, 9, 15, 5, 1, 1, 1, 1, 1]
  new best n=38 b=9  chords=((0, 2), (1, 5), (1, 6), (3, 7), (4, 8)) arcs=[1, 1, 5, 9, 1, 2, 1, 17, 1]
  new best n=40 b=9  chords=((0, 3), (1, 4), (2, 6), (2, 7), (5, 8)) arcs=[1, 5, 1, 1, 1, 1, 1, 10, 19]
```

---

## 5. Gates and their mutation check

`search/shapecsp/test_shapecsp.py` asserts behaviour by calling the pipeline with
values. It contains no spelling pins -- every gate calls `shapes()`, `t_k()`,
`cycle_forms()` or `verify.check()` and compares the answer.

The load-bearing gate is the one that catches the section 1 defect. Its mutation check:
break the enumeration so it emits only the non-degenerate `b = 2k` shapes, run,
restore, run.

**Mutation** -- in `shapes.py:shapes`, `rng = range(lo, 2*k+1)` replaced by
`rng = [2*k]`:

```
$ python test_shapecsp.py            # RED, exit 1   (search/shapecsp/gates-red.txt)
PASS cycle forms reproduce the true cycle-length multiset :: 147 graphs, 0 mismatches
PASS k=2 cycle count within 2^(k+1)-1 :: max=7 bound=7
...
PASS t_3 == 14 :: got 14 from shape (6, ((0, 1), (2, 4), (3, 5))) arcs [3, 1, 1, 1, 7, 1]
FAIL t_4 == 24 :: got 22 from shape (8, ((0, 2), (1, 4), (3, 6), (5, 7))) arcs [1, 1, 10, 5, 1, 2, 1, 1]
FAIL t_4 witness is a real pancyclic C_n+4 chords :: n=22 chords=[(0, 2), (1, 17), (12, 20), (18, 21)] pancyclic
FAIL k=3 enumeration includes degenerate b<2k :: b values [6]
FAIL k=4 enumeration includes degenerate b<2k :: b values [8]

FAILED: t_4 == 24, t_4 witness is a real pancyclic C_n+4 chords, k=3 enumeration includes degenerate b<2k, k=4 enumeration includes degenerate b<2k
```

**Restored** -- `shapes.py` put back verbatim:

```
$ python test_shapecsp.py            # GREEN, exit 0 (search/shapecsp/gates-green.txt)
PASS cycle forms reproduce the true cycle-length multiset :: 201 graphs, 0 mismatches
PASS k=2 cycle count within 2^(k+1)-1 :: max=7 bound=7
PASS k=3 cycle count within 2^(k+1)-1 :: max=15 bound=15
PASS k=4 cycle count within 2^(k+1)-1 :: max=29 bound=31
PASS k=5 cycle count within 2^(k+1)-1 :: max=56 bound=63
PASS t_2 == 8 :: got 8 from shape (4, ((0, 2), (1, 3))) arcs [4, 2, 1, 1]
PASS t_2 witness is a real pancyclic C_n+2 chords :: n=8 chords=[(0, 6), (4, 7)] pancyclic
PASS t_3 == 14 :: got 14 from shape (5, ((0, 2), (0, 3), (1, 4))) arcs [1, 4, 6, 2, 1]
PASS t_3 witness is a real pancyclic C_n+3 chords :: n=14 chords=[(0, 5), (0, 11), (1, 13)] pancyclic
PASS t_4 == 24 :: got 24 from shape (7, ((0, 2), (1, 4), (1, 5), (3, 6))) arcs [1, 1, 1, 2, 2, 11, 6]
PASS t_4 witness is a real pancyclic C_n+4 chords :: n=24 chords=[(0, 2), (1, 5), (1, 7), (3, 18)] pancyclic
PASS k=3 enumeration includes degenerate b<2k :: b values [3, 4, 5, 6]
PASS k=3 b=2k-only bound is 14 :: b=2k only gives 14, true t_3=14
PASS k=4 enumeration includes degenerate b<2k :: b values [4, 5, 6, 7, 8]
PASS k=4 b=2k-only bound is 22 :: b=2k only gives 22, true t_4=24
PASS dropping the degenerate families loses t_4 :: b=2k only reaches 22, t_4=24
PASS k=2 shape ((0, 2), (1, 3)) infeasible at n>=9 :: status INFEASIBLE n=None

ALL GATES PASS
```

One assumption in the first draft of this gate was wrong and was corrected against
the code rather than the other way round: the gate originally asserted that
dropping the degenerate families loses `t_k` for k=3 as well. It does not -- the
`b=6` family reaches 14 too. The gate now asserts the measured values (14 and 22)
and the loss claim only where it holds, k=4.

### 5c. The `lastarc` optimisation, its differential, and the controls after it

The independent review supplied one optimisation (`lastarc.patch`): when only the
final arc is unassigned, `sum(a) = n` fixes its value, so the loop can start at
`lo[i] + slack` instead of `lo[i]`.

```c
    /* Last arc: sum(a) == nn fixes its value at lo[i] + slack, since every other
     * arc is assigned.  Smaller values reach depth b with slack > 0, where the
     * leaf test rejects them, so skipping them removes no solution. */
    int first = (d == b - 1) ? lo[i] + slack : lo[i];
```

The argument that it removes no solution is short enough to state in full: a
smaller value for the last arc reaches depth `b` with `slack > 0`, and the leaf
test there is `return slack == 0`. So the skipped branches were all going to
return 0.

**That argument is not the evidence.** An answer-preserving claim about a search
is checked by running both searches, which is what `search/shapecsp/difftest.py`
does: every shape of a given `k`, every cutoff in a range, both builds, records
compared with `nodes=` stripped -- the node count is exactly what an optimisation
is meant to change and the verdict is exactly what it must not -- and every SAT
either build returns is materialised and re-checked, so two builds cannot agree
their way past a wrong answer.

| comparison | shapes | record comparisons | disagreements | SAT witnesses re-checked |
|---|---|---|---|---|
| `bb-orig` vs patched, k=3, cutoffs 8..20, desktop | 14 | 78 | **0** | 63 |
| the **running** laptop binary vs patched, k=3, cutoffs 8..20 | 14 | 78 | **0** | 63 |
| `bb-orig` vs patched, k=4, cutoffs 10..26, laptop | 103 | **1250** | **0** | 973 |

The middle row is the one that matters operationally: it compares the patched
build against the exact binary that produced the `.done` records the n=68 hunt had
already banked, so those records did not have to be thrown away when the binary
was swapped.

Both changes to the search since the last control -- the `exact` mode and this
patch -- were followed by re-running the positive control **on both machines**,
against the hardened `sweep.py`, with every witness now verified inline:

```
desktop, MinGW gcc 16.1.0          laptop, gcc 13.3.0 (independent toolchain)
RESULT t_2 = 8   gaveup_records=0  RESULT t_2 = 8   gaveup_records=0   exit=0
RESULT t_3 = 14  gaveup_records=0  RESULT t_3 = 14  gaveup_records=0   exit=0
RESULT t_4 = 24  gaveup_records=0  RESULT t_4 = 24  gaveup_records=0   exit=0
   SAT n=24 b=7 chords=((0, 2), (1, 4), (1, 5), (3, 6)) arcs=1,1,1,2,2,11,6
       VERIFIED [(0, 2), (1, 5), (1, 7), (3, 18)] -> pancyclic
```

`test_shapecsp.py` also still reports `ALL GATES PASS` on the patched build.

I did **not** measure the patch's speedup on the n=68 workload. The review
measured 19.3% fewer nodes and 14.4% less elapsed time on a small benchmark; on
this workload the figure is unknown, and the two runs that would establish it
(same shapes, both builds, at n=68) have not been run because the core-hours are
better spent on the hunt itself.

### `sweep.py` had the same defects, and it is the control driver

The review scoped `level.py` and `satcheck.py`. `sweep.py` -- which is what
produces `RESULT t_k = ...`, the headline positive control -- was not in scope and
had the same three result-handling defects: no child exit check, no completeness
check, and a SAT printed straight from the solver's own claim. It now carries the
identical contract, so the numbers `t_2..t_5` in section 4 are produced under it:

```
SWEEP k={k} FAILED -- solver exited {rc} at n={n}
SWEEP k={k} FAILED -- {missing} of {len(elig)} eligible shapes produced no terminal
                      record at n={n}; that is UNKNOWN, not a refutation
SWEEP k={k} FAILED -- n={n} b={b} chords={ch}: verify.check REJECTS ...
```

`runlevels.py` likewise lost its child exit codes -- it read the last `LEVEL` line
out of the file and ignored the status. It now prints `[child exit N -- NOT a
clean level]` beside any non-clean level and exits non-zero if any level was not
clean, which matters now that `level.py` exits 1 on `gaveup > 0`.

This is the same defect family as the four the review found, in a file the review
did not read, which is the argument for treating the contract as a rule for every
driver in this directory rather than a patch to two of them.

### The reformulation itself is cross-checked against ground truth

The first gate does not trust the cycle-space derivation. For 201 randomly drawn
(shape, arc-length) pairs across k=2..5 it materialises the actual
`C_n + k chords` graph and compares the multiset of lengths predicted by the forms
against `networkx.simple_cycles` on the real graph: **0 mismatches**. Every
reported optimum is additionally re-checked this way in `verify.check`, which
rebuilds the graph, confirms it is simple (no chord duplicating a cycle edge) and
enumerates its cycles directly -- so no reported `t_k` rests on the reformulation
being right.

### t_5 = 40, exhaustively

`runlevels.py 5 41 58 3` decided every level from the largest cap down, then level
40 was run to produce the witnesses. Every level is `sat=0 gaveup=0` -- nothing was
abandoned on a node budget -- so `t_5 <= 40` is a refutation, not a search that gave
up (`search/shapecsp/level-k5-n*.txt`, `k5-levels.log`):

```
LEVEL k=5 n=58 eligible=0   sat=0 gaveup=0   search_seconds=0.0
LEVEL k=5 n=57 eligible=0   sat=0 gaveup=0   search_seconds=0.0
LEVEL k=5 n=56 eligible=0   sat=0 gaveup=0   search_seconds=0.0
LEVEL k=5 n=55 eligible=0   sat=0 gaveup=0   search_seconds=0.0
LEVEL k=5 n=54 eligible=3   sat=0 gaveup=0   search_seconds=0.5
LEVEL k=5 n=53 eligible=5   sat=0 gaveup=0   search_seconds=2.1
LEVEL k=5 n=52 eligible=9   sat=0 gaveup=0   search_seconds=5.9
LEVEL k=5 n=51 eligible=17  sat=0 gaveup=0   search_seconds=13.2
LEVEL k=5 n=50 eligible=23  sat=0 gaveup=0   search_seconds=26.8
LEVEL k=5 n=49 eligible=32  sat=0 gaveup=0   search_seconds=47.1
LEVEL k=5 n=48 eligible=48  sat=0 gaveup=0   search_seconds=77.4
LEVEL k=5 n=47 eligible=74  sat=0 gaveup=0   search_seconds=119.7
LEVEL k=5 n=46 eligible=96  sat=0 gaveup=0   search_seconds=172.2
LEVEL k=5 n=45 eligible=128 sat=0 gaveup=0   search_seconds=238.8
LEVEL k=5 n=44 eligible=159 sat=0 gaveup=0   search_seconds=340.8
LEVEL k=5 n=43 eligible=195 sat=0 gaveup=0   search_seconds=415.9
LEVEL k=5 n=42 eligible=242 sat=0 gaveup=0   search_seconds=522.1
LEVEL k=5 n=41 eligible=308 sat=0 gaveup=0   search_seconds=593.8
LEVEL k=5 n=40 eligible=346 sat=4 gaveup=0   search_seconds=698.2
```

The four optimal shapes at n=40, all with `b=9` (degenerate), each re-verified
pancyclic by rebuilding the graph and enumerating its cycles with `networkx`:

```
b=9 chords ((0,2),(0,6),(1,4),(3,7),(5,8)) arcs 1,1,1,10,19,1,1,1,5
     -> C_40 + {(0,2),(0,33),(1,13),(3,34),(32,35)}   pancyclic
b=9 chords ((0,2),(0,7),(1,5),(3,8),(4,6)) arcs 1,2,2,17,10,5,1,1,1
     -> C_40 + {(0,3),(0,38),(1,32),(5,39),(22,37)}   pancyclic
b=9 chords ((0,2),(1,4),(1,5),(3,7),(6,8)) arcs 1,1,1,2,2,17,10,5,1
     -> C_40 + {(0,2),(1,5),(1,7),(3,34),(24,39)}     pancyclic
b=9 chords ((0,3),(1,4),(2,6),(2,7),(5,8)) arcs 1,1,5,1,1,1,1,10,19
     -> C_40 + {(0,7),(1,8),(2,10),(2,11),(9,21)}     pancyclic
```

**These are, up to dihedral symmetry, the complete list of 5-chord extremal
shapes** -- a statement the hill-climbing programs cannot make. Two of the four,
`(0,2)(1,5)(1,7)(3,34)(24,39)` and `(0,7)(1,8)(2,10)(2,11)(9,21)`, are literally
entries 0 and 4 of the `SHAPES` list that `search/k6/scan_shapes.py` was seeded
with as "5-chord empirical extremal shapes"; the exhaustive sweep confirms those
seeds were extremal and says that the list is complete at four, not five (the
other three entries of that list are not optimal shapes).

So the positive control passes: **t_2, t_3, t_4, t_5 = 8, 14, 24, 40**, each
computed from scratch with no lower bound supplied, and each upper bound a
complete refutation with zero abandoned searches.

### 4a. What the n=41 level says about h(41), and how independent it is

The level at n=41 deserves naming separately, because `h(41) > 5` -- no 5-chord
pancyclic graph on 41 vertices -- is a claim this repository otherwise supports
with a single enumeration:

```
LEVEL k=5 n=41 shapes=1236 eligible=308 sat=0 gaveup=0 search_seconds=593.8
```

`sat=0` with `gaveup=0` means every one of the 308 shapes that could reach n=41
was decided, none abandoned on a node budget. **No C_41 plus 5 chords is
pancyclic.**

Two things a referee will ask, answered plainly:

- **Is 1236 the complete k=5 shape count, including chords that share endpoints?**
  Yes. `shapes(5)` runs `b` from 4 to 10 and the per-`b` breakdown is
  `{4:2, 5:28, 6:153, 7:333, 8:417, 9:224, 10:79}` (`shape-census.txt`). Only the
  79 shapes with `b=10` are perfect matchings; the other **1157 are the degenerate
  families**. The n=41 level drew its 308 eligible shapes from all 1236. This is
  not a formality here: every one of the four shapes that actually attains
  `t_5 = 40` has `b = 9`, so an enumeration without the degenerate families would
  have been wrong about k=5 in both directions.

- **What does this code share with `search/gpu_pancyc.py`?** Nothing. The import
  closure of `search/shapecsp/` is the Python standard library, `networkx`
  (used only in `verify.py` and the gates, never in the search), `ortools` (used
  only by `solve.py`, which is not in the k=5 path) and `psutil` (CPU pinning
  only). No module under `search/` or `search/k6/` is imported, and `bb.c` is
  self-contained C. The algorithms are not merely separate implementations of the
  same idea: the GPU program enumerates **chord sets** at a fixed n and evaluates
  each, while this one enumerates **shapes** (which do not depend on n at all) and
  solves for integer arc lengths. The only thing crossing the boundary anywhere in
  this report is *data*, not code -- the 56-vertex chord list read out of
  `search/k6/witnesses.csv` and the n=66/67 chord lists quoted to me, each of
  which was then re-verified here from scratch. So there is no shared component
  for a common-mode error to hide in.

The evidence that this solver is sound is not only the `t_2`/`t_3`/`t_4`
agreement with CP-SAT. It is the gate suite in section 5, in particular the
cross-check that the cycle forms reproduce the true cycle-length multiset on 201
materialised graphs, and the red/green mutation pair showing the gates actually
fail when the enumeration is broken.

### 4b. Third control: k=3 against GMW13's published hand classification

GMW13 (George, Marr, Wallis 2013) classifies the k=3 case by hand into 14 named
types -- `AAAi, AAAii, AABi, AABii, AAC, ABBi, ABBii, ABC, ACC, BBBi, BBBii, BBC,
BCC, CCC`. This enumeration independently produces **14 shapes at k=3**. The
counts agree, but a coincidence of counts is not a correspondence, so here is
what was actually checked.

GMW13's labels are a multiset of the three pairwise relations between the three
chords, over an alphabet `{A,B,C}`: all 10 multisets appear, and exactly 4 of them
-- `AAA`, `AAB`, `ABB`, `BBB` -- carry a roman-numeral refinement into two
sub-cases. `10 + 4 = 14`.

Computing the same invariant on my 14 shapes (relation = share an endpoint /
cross / neither) gives:

```
AAA x1   AAB x1   AAC x1   ABB x1   ABC x1   ACC x1
BBB x2   BBC x2   BCC x2   CCC x2                     (A = cross, C = shared endpoint)
```

All 10 multisets appear and exactly 4 carry two shapes -- the same
`10 singletons-and-doubletons = 14` structure. Moreover, the four doubled classes
are in both cases *precisely the four multisets drawn from two of the three
letters*: mine are the four over `{B,C}`, GMW13's are the four over `{A,B}`. Those
coincide exactly when GMW13's `C` is the crossing relation. So the agreement is
structural, not just numerical.

**But it is not verified as a bijection, and must not be written as one.** The
repository's copy of GMW13 (`papers/GMW13-George-Marr-Wallis-2013.pdf`) is a
scanned PDF with no text layer -- `pdftotext` yields a 0-byte file and PyMuPDF
reports 0 characters on page 1 -- so I could not read GMW13's own definitions of
`A`, `B`, `C` or of the roman numerals. The label list used above is the quotation
in `papers/REPORT-griffin-method.md`, not the paper. Which letter means "crossing"
is therefore an assumption, and this is a "could not look", not a "checked and it
matches". What is established: the cardinalities agree at 14, and the refinement
structure agrees under one of the two possible readings.

---

## 6. k=6: what the method establishes, and where it stops

`t_6` is **not** resolved here. What is established:

### Lower bound: t_6 >= 67, from witnesses re-verified here

Three 6-chord witnesses were checked from scratch in this lane -- rebuilt as
graphs, confirmed to have exactly 6 chords with none duplicating a cycle edge,
then every cycle enumerated with `networkx` and compared against `[3,n]`:

```
n=56  C_56 + {(0,2),(0,53),(1,39),(20,39),(39,48),(48,53)}   missing=[]  (search/k6/witnesses.csv)
n=66  C_66 + {(0,2),(0,59),(1,13),(3,60),(4,31),(58,61)}     missing=[]  (from the GPU lane)
n=67  C_67 + {(0,2),(0,60),(1,13),(3,61),(4,31),(59,62)}     missing=[]  (from the GPU lane)
```

so **t_6 >= 67**. Only the chord lists crossed from the other lane; the verdicts
above are this lane's own, computed by `verify.py` against the materialised graph
rather than through the shape reformulation.

#### The n=66 and n=67 witnesses are the same shape, and it is degenerate, and it is running down

Both reduce to `b = 11` branch points with canonical chord set
`((0,2),(0,8),(1,5),(3,9),(4,6),(7,10))` -- one shape, not two, with branch point
0 carrying two chords. It is a degenerate shape (11 branch vertices, not 12), it
is present in the 21878-shape enumeration, and it has **85 distinct cycle forms,
so its own cap is 87**. That is a concrete handle the chord-set searches do not
have: whatever the largest n this shape supports is, it is at most 87, and the
whole n=66/67 family is one point in shape space rather than two separate finds.

Running that single shape downward from its own cap is the cheapest live question
in the k=6 range, and it is what the one permitted core was given
(`witness-shape-max.log`, `witness-shape-6872.log`, one process pinned to core 0
at BelowNormal). **It finished:**

```
cutoff 87: UNSAT  nodes=30053700     [65.7s]     -- i.e. nothing in [87, 87]
cutoff 86: UNSAT  nodes=75769444     [132.6s]    -- nothing in [86, 87]
cutoff 72: UNSAT  nodes=842859511    [717.3s]    -- nothing in [72, 87]
cutoff 71: UNSAT  nodes=906297218    [729.4s]
cutoff 70: UNSAT  nodes=969725828    [755.2s]
cutoff 69: UNSAT  nodes=1032827326   [942.1s]
cutoff 68: UNSAT  nodes=1094520191   [963.0s]    -- nothing in [68, 87]
cutoff 67: SAT at n=67, arcs=1,1,1,1,9,18,28,1,1,1,5   [1036.2s]
RESULT shape maximum = 67
```

(Each figure is cumulative over `[cutoff, 87]`, not the cost of one rung -- the
marginal cost of adding a rung is the difference between consecutive lines, 12s,
26s, 187s, 21s, 73s.)

**The shape that carries the n=66 and n=67 witnesses has exact maximum 67.** Every
n from 68 to its cap 87 is refuted with no abandoned search, so that family is
closed and any 6-chord pancyclic graph on 68 or more vertices must use a
*different* shape. (n=85..73 are omitted from the excerpt for length; every rung
from 87 down is in the two logs and every one is UNSAT.)

#### Every witness shape is now maxed out exactly, and none beats 67

Because `bb.exe` takes a lower cutoff and walks down from each shape's own cap
(section 0), asking it for a witness's `n` returns that shape's **exact maximum**.
Run over the shape of each verified witness (`satcheck.py`,
`satcheck.log`, one process pinned to core 0 at BelowNormal):

| witness n | b | shape cap | shape's exact maximum | seconds |
|---|---|---|---|---|
| 56 | 7 | 59 | **56** | 24.0 |
| 60 | 8 | 70 | **62** | 371.0 |
| 61 | 9 | 74 | **61** | 190.6 |
| 63 | 9 | 74 | **63** | 511.2 |
| 64 | 10 | 78 | **64** | 851.8 |
| 66 | 11 | 87 | **67** | 1193.9 |
| 67 | 11 | 87 | **67** | 2100.5 |

```
SATCHECK: all witness shapes returned SAT
```

Grouping the nine verified witnesses by shape, those seven runs cover all of them,
because the nine sit on only six distinct shapes:

| witnesses | shape's exact maximum |
|---|---|
| 56 | 56 |
| 60 | **62** |
| 61 | 61 |
| 62, 63 | 63 |
| 64 | 64 |
| 65, 66, 67 | **67** |

So **every 6-chord shape this project has found is exhausted, and the best of them
tops out at 67.** Improving on `t_6 >= 67` cannot be done by perturbing any known
witness; it requires a shape nobody has looked at. The one small surprise is the
n=60 witness's shape, which reaches 62 -- so the sub-67 witnesses were not at
their own shapes' maxima, even though the best one is.

#### The same run is the false-negative control, and it passed

This doubles as the check that matters most for believing any `sat=0`: a solver
that missed real solutions would report UNSAT on a shape that demonstrably has
one. All seven returned SAT, and each returned arc vector was materialised and
re-verified pancyclic by `verify.check` rather than trusted. Had any single line
come back UNSAT, every `sat=0` level in this report would have been void.

#### The SAT at n=67 is a k=6 positive control, and it passed on the nose

The n=67 line is not just a stopping condition. The solver was given only the
shape and asked for arc lengths; it returned `1,1,1,1,9,18,28,1,1,1,5`, which
materialises to

```
C_67 + {(0,2),(0,60),(1,13),(3,61),(4,31),(59,62)}   -- pancyclic, verify.check
```

-- *character for character the chord set the GPU lane found independently*. A
k=6 solver that returns `sat=0` at n=68 is only worth believing if it returns SAT
where a witness is known to exist, and this is that test, passed at k=6 on the
decisive shape rather than only at k<=4.

### The shape of the 56-vertex witness is exhausted

The 56-vertex witness has shape `b = 7`, canonical form
`((0,1),(0,3),(0,6),(2,4),(4,5),(5,6))`, with 57 distinct cycle forms, so its cap
is 59. Running that one shape exactly:

```
n=59: SHAPE 1 UNSAT nodes=727169
n=58: SHAPE 1 UNSAT nodes=2154411
n=57: SHAPE 1 UNSAT nodes=3963956
```

So **56 is that shape's exact maximum** -- no arc-length assignment on the best
known 6-chord shape does better, at any n. Beating 56 requires a different shape,
which is exactly the question the hill-climbs in `search/k6/` cannot answer and
this method can, given enough compute.

### Upper bound: the descending sweep, and the measured wall it hits

`runlevels.py 6 57 110 4` runs the levels `n = 110 .. 57`, each a complete
decision over every shape that can still reach that `n`. Completed levels
(`search/shapecsp/level-k6-n*.txt`, `k6-levels.log`):

```
n=111 .. 102  eligible=0                        (killed by cap + Hall alone)
n=101         eligible=5   sat=0 gaveup=0     18.1s
n=100         eligible=8   sat=0 gaveup=0     48.1s
n= 99         eligible=24  sat=0 gaveup=0    521.6s
n= 98         eligible=28  sat=0 gaveup=0   1197.9s
n= 97         eligible=28  sat=0 gaveup=0   2727.1s
n= 96         eligible=32  sat=0 gaveup=0   4682.5s
n= 95         eligible=53  sat=0 gaveup=0   9529.9s
n= 94         eligible=81  sat=0 gaveup=0   4070.6s
```

Every one is `sat=0 gaveup=0`, so these levels are refutations over **all 21878
shapes**, degenerate families included. `eligible` is not a sample: it is every
shape that could still reach that n, the rest being excluded by the two rigorous
necessary conditions (cap, then Hall). At n=96, for instance, 146 of the 21878
shapes have a large enough cap and 32 of those survive Hall; the other 21846 are
refuted without search.

Levels 111 down to 94 are contiguous, so **no C_n plus 6 chords with n >= 94 is
pancyclic**, i.e. `t_6 <= 93`.

#### Coverage audit -- which levels are results and which are holes

The aggregate `k6-levels.log` is not the record: parallel workers interleaved
writes into it (the n=110 line is spliced into the middle of the n=107 line) and
it carries a line reading `LEVEL k=6 n=93 NO-OUTPUT` from a level whose process
was stopped. **The per-level files are the record.** Audited:

| n | status |
|---|---|
| 111 .. 102 | UNSAT, `eligible=0` -- decided by the cap and Hall bounds with no search at all |
| 101 .. 94 | UNSAT, `sat=0 gaveup=0`, every eligible shape decided |
| 93, 92 | **HOLES.** Started, stopped for the CPU cap before finishing. `level-k6-n93.txt` and `-n92.txt` are 0 bytes. These are UNKNOWN, not UNSAT, and are not counted as coverage anywhere in this report. |
| 91 and below | not attempted |

The `NO-OUTPUT` line in `k6-levels.log` and the two empty files are exactly the
failure mode this project has had to relabel INVALID elsewhere, so to be explicit:
**nothing in the `t_6 <= 93` claim depends on n=93 or n=92.** The claim uses only
the contiguous block 111..94, all of which have a `LEVEL` line with `gaveup=0`.

### Correcting my own cost model: it is the shape count, not the per-shape cost

An earlier draft of this report attributed the level-cost growth to per-shape
difficulty, quoting "about a factor of 2 per level down". The single-shape run
above is a clean measurement -- one shape, one core, constant conditions -- and it
says otherwise. On a fixed shape the per-rung cost is close to **flat**:

```
n = 72   71   70   69   68   67
s = 717  729  755  942  963  1036
```

That is 1.45x in total across six rungs, not 2x per rung. The level totals
(18.1 -> 48.1 -> 521.6 -> 1197.9 -> 2727.1 -> 4682.5 -> 9529.9 seconds from n=101
to n=95) were measured under varying contention -- up to four levels plus other
agents' jobs sharing eight cores -- and their growth is driven predominantly by
the number of **eligible shapes**, which is what actually explodes:

| n | shapes eligible after cap + Hall |
|---|---|
| 111..102 | 0 |
| 101 | 5 |
| 94 | 81 |
| 93 | 114 |
| 92 | 152 |
| 68 | **6059** |

So the honest feasibility statement for the decisive `n = 68` level is an
extrapolation from a real hard instance rather than from a fitted curve: the
b=11, 85-form shape above cost 963 s at n=68 on one throttled core, and there are
6059 eligible shapes at that n. Depending on how the easier shapes average out
that is of the order of 200 to 800 core-hours as clamped. The clamp itself is
worth a factor -- this lane is confined to one core at BelowNormal -- so on an
unclamped machine the same level plausibly lands in the tens of core-hours.
**The n=68 level is out of reach of this lane's current allocation; it is not
demonstrated to be out of reach of the method.** Those are different claims and
only the first one is measured.

### What the completed work does pin down

So the k=6 status is an **improved bracket, not an exact value**:

    67  <=  t_6  <=  93

with both ends established here: the lower end by re-verifying the existing
witness against the real graph, the upper end by 17 contiguous exhaustive levels
(n = 110 down to 94) over all 21878 shapes with nothing abandoned. For comparison, the a-priori bound
from the brief's `2^(k+1)-1 = 127` cycles is `t_6 <= 129`; the measured maximum of
109 distinct cycle forms already improves that to 111 with no search at all, and
the sweep takes it to 95.

Two further partial results, each with its cap declared:

- **All seven known witness shapes are closed, exactly**: maxima 56, 62, 61, 63,
  64, 67, 67 for the shapes of the n = 56, 60, 61, 63, 64, 66, 67 witnesses, no
  abandoned searches. `t_6 > 67` requires a shape nobody has looked at yet.
- **Low-cap shapes, partially.** `capscan.py 6 56 62` decides shapes whose cap lies
  in `(56, 62]`, at every n from their cap down to 57. It was stopped for CPU
  before finishing: **the first 750 of those 4059 shapes, in enumeration order,
  were fully decided -- `sat=0 gaveup=0`** (`k6-capscan-62.log`). That is a real but
  partial statement about 750 named shapes, not about the 4059.
- **Not obtained.** A bounded-budget hunt for a witness at n = 57, 58, 59 (500000
  nodes per shape, over all cap+Hall-eligible shapes) was started and **did not
  finish**; its processes were stopped and produced no output, so it contributes
  nothing -- neither a witness nor evidence of absence. It is listed here because a
  silent skip would be indistinguishable from a negative result.

---

## 6a. The n=68 question, a second machine, and two more of my own bugs

With every known shape exhausted at 67 (section 6), the live question is whether
*any* shape reaches 68. The work moved to a second machine for this.

### Deployment and its controls

Sources were copied to an Ubuntu 24.04 laptop (16 logical CPUs) and `bb` built
there with the laptop's own `gcc 13.3` -- the Windows binary was deliberately not
shipped, because a fresh toolchain is exactly where a silent difference would
appear. `pip --user` is blocked on that distribution by PEP 668; rather than
`--break-system-packages` on someone else's machine, the dependencies went into a
venv under the project directory.

**The controls were re-run there before any k=6 number was taken from it**, and
both passed on the new toolchain:

```
ALL GATES PASS                       (test_shapecsp.py, incl. the 201-graph
                                      cross-check against networkx)
RESULT t_2 = 8    gaveup_records=0
RESULT t_3 = 14   gaveup_records=0
RESULT t_4 = 24   gaveup_records=0
```

### Two bugs in my own harness, found by the deployment

1. **The node budget was per rung, not per shape.** `bb` reset its node counter
   for each `n` in the range, so a "120M node budget" on a shape with cap 101 and
   cutoff 68 was really 120M x 34. Budgets are now cumulative per shape.
2. **A hit is not cheap after all.** I had reasoned that SAT shapes are answered
   quickly because `bb` stops at the first feasible `n`. That is only true when
   the cap is near the cutoff: a shape with cap 101 must *refute* 101, 100, ... 69
   before it ever tests 68. So the hunt needed a mode that tests one value.
   `bb` now takes `exact=1`, testing only `n = cutoff` -- one search per shape
   instead of `cap - cutoff + 1`.

Both changes touch the search, so the k=2/3/4 control was re-run on **both**
machines afterwards; all three still exact with `gaveup_records=0`.

### What the n=68 run can and cannot deliver

Measured on the laptop, 7 workers at `nice 10`:

```
23/6059 shapes, 592s elapsed, 0.039 shapes/s, gaveup=0
-> ~40 hours wall-clock for all 6059
```

(Likely an over-estimate: shapes are ordered cap-descending and cost rises with
`cap - cutoff`, so the early ones are the worst.)

**That 40 hours buys a hunt, not a proof.** Exact mode answers "is any shape
feasible at exactly 68". A hit is conclusive -- `t_6 >= 68` with arc lengths that
materialise into a chord set. A miss is *not*: it says nothing about a shape
reaching 69..93. The non-existence proof needs range mode over `[68, 93]`, which
is of order 26x the hunt, i.e. weeks. **`t_6 = 67` is not deliverable by this
lane.** As in section 6, that is a statement about the available allocation, not
about the method.

---

## 7. Why this is the right shape of algorithm even though k=6 did not close

The brief's measured motivation holds up. Brute force over chord sets is
`C(8127,6) ~ 4e20` at n=129 and grows like `n^12`; the number of shapes does not
grow with `n` at all -- it is 21878 for k=6, full stop. What this work adds is the
measurement of the *second* cost, the one the shape count hides: per shape the
arc-length CSP is itself a search whose difficulty is governed by the coverage
slack `cap - n`, and that is where k=6 is expensive, not in the shape count.

Concretely, for k=5 the whole exact computation is 18 levels and about 50 minutes
on 3 cores. For k=6 the same scheme is finite and correct but the per-shape cost
at the levels that matter is ~2.2x per step and there are ~40 steps.

Two things would most likely close it, in order of expected value:

1. **A sharper per-shape bound than `#forms + 2`.** Hall's condition restricted to
   value intervals (`bound.py`) is sound but weak -- it removes only 2.2% of the
   cap-eligible shapes at n=57 (13259 -> 12972) and 3.6% at n=65 (8043 -> 7756),
   measured. A bound that uses the arc structure rather than only the form
   intervals would cut the eligible set at each level, which is the multiplier the
   sweep is fighting.
2. **Branching on which form realises each length**, low end and high end
   simultaneously, instead of on arc lengths. Each such choice is a linear
   equation on the arcs, and after about `b` of them the arc vector is determined;
   the current search branches on arc values and only discovers the contradiction
   through the matching test.

CP-SAT was tried first and is the wrong tool here: at k=6 it returned UNKNOWN on
11 of 11 randomly sampled eligible shapes at a 120 s limit with one worker, and
raising `linearization_level` or `symmetry_level` did not decide a single one of
the hard instances in 60 s (`search/shapecsp/solve.py` is kept because it is a
genuinely independent second implementation for k <= 5, where it agrees with the
C search on every value).

---

## 8. Files

Everything new is under `search/shapecsp/`; nothing under `search/k6/` was
touched.

| file | what it is |
|---|---|
| `shapes.py` | shape enumeration up to `D_b`, all `b <= 2k` including degenerate; cycle-space enumeration into 0/1 length forms |
| `bound.py` | interval-Hall necessary condition; cheap per-shape cap |
| `solve.py` | CP-SAT model and ladder driver (second, independent solver) |
| `bb.c` / `bb.exe` | C branch-and-bound with exact greedy interval-matching prune |
| `sweep.py`, `level.py`, `runlevels.py`, `capscan.py` | drivers: descending-n sweep, single level, parallel levels, per-shape scan by cap |
| `verify.py` | independent check: rebuild the real graph, confirm simple, enumerate cycles with `networkx` |
| `hunt.py` | best-first single-cutoff hunt, resumable through `hunt-k<k>-n<n>-<mode>.done` |
| `test_shapecsp.py` | behaviour gates (section 5) |
| `test_review_contracts.py`, `mutation-check.py` | the six result-integrity contracts and the RED/GREEN mutation check of the four gates (section 0a) |
| `difftest.py`, `bb-orig.c` | two-build differential and the pre-`lastarc` C source it compares against (section 5c) |
| `gates-green.txt`, `gates-red.txt` | gate output before/after the mutation |
| `control-k2-k5.log`, `k5-levels.log`, `level-k5-n*.txt` | positive control evidence |
| `k6-levels.log`, `level-k6-n*.txt`, `k6-capscan-62.log`, `hunt-n5*.log` | k=6 evidence |
| `shape-census.txt`, `nondegenerate-maxima.txt` | the tables in sections 1 and 2 |

Reproduce:

```
pip install ortools networkx
cd search/shapecsp
gcc -O2 -o bb.exe bb.c
python test_shapecsp.py          # gates
python test_review_contracts.py  # result-integrity contracts (6)
python mutation-check.py         # each of the 4 gates: RED when disabled, GREEN when restored
python difftest.py bb-orig.exe bb.exe 4 10 26   # the lastarc patch changes no answer
python sweep.py 2 3              # t_2 = 8
python sweep.py 3 3              # t_3 = 14
python sweep.py 4 3              # t_4 = 24
python runlevels.py 5 41 58 3    # t_5 <= 40 (all levels UNSAT, zero gaveup)
python level.py 5 40             # t_5 = 40 with its four extremal shapes
```

`ortools` was not installed in this environment and was added with `pip install
ortools` (9.15.6755). It is needed only for `solve.py` and `test_shapecsp.py`; the
C search and the sweeps need only `networkx`.

---

## 9. Refusals, caps and one operational error

- **Caps declared.** The k=6 sweep is capped, and every cap is stated where it is
  used: levels were run from n=110 down only as far as the times in section 6 show;
  `capscan` covers only shapes whose cap is in the stated range; the `hunt` runs
  use a 500000-node budget per shape and are therefore a *search*, not a
  refutation -- any "nothing found" from them is reported as such and never as
  UNSAT. `bb.exe` reports `GAVEUP` rather than `UNSAT` whenever it hits its node
  budget, and every level line in this report carries its `gaveup` count.
- **Not done.** Exact `t_6`. Also not done: a second independent implementation of
  the k=6 sweep -- the k=6 numbers rest on one search program (`bb.c`), whereas the
  k<=5 numbers are agreed by two. The k<=5 agreement is the evidence that `bb.c`
  is right; it is not a proof about k=6.
- **Operational error, reported.** While stopping my own background runs I used a
  PowerShell filter `CommandLine -like '*sweep.py*'`, which also matched and
  force-stopped a process belonging to another agent on this machine:
  `python gpu_joint_sweep.py sweep 67 3 (0,2)(0,64)(1,13)(3,63)(4,31)(59,64) --duty 0.8`.
  That run was lost and the exact invocation was relayed to the manager so its
  owner could restart it (it has since been seen running again at n=68).
  Subsequent stops were scoped by PID.
