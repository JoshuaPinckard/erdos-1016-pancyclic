# Exact t_k by the shape/CSP reformulation

Scope: build and validate an exact algorithm for `t_k` = the largest `n` for which
some `C_n` plus `k` chords is pancyclic, via the shape/CSP reformulation; reproduce
`t_2..t_5 = 8, 14, 24, 40` from scratch as a positive control; then report k=6.

Code added under `search/shapecsp/`. Nothing under `search/k6/` was modified.

## Summary

| | result |
|---|---|
| `t_2, t_3, t_4, t_5` | **8, 14, 24, 40** -- exact, from scratch, no lower bound supplied, zero abandoned searches |
| `t_6` | **not resolved.** Improved bracket `56 <= t_6 <= 93` (a-priori upper bound was 129) |
| shapes | 3 / 14 / 103 / 1236 / 21878 for k = 2..6, of which 1 / 9 / 86 / 1157 / **21324** are the degenerate families |
| costliest finding | the perfect-matching-only shape model returns the **wrong** maximum: 22 instead of `t_4 = 24`, 37 instead of `t_5 = 40` |

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
are degenerate** -- only 554 are perfect matchings on 12 points. And the best
verified k=6 witness already in this repository, the 56-vertex one from
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

---

## 6. k=6: what the method establishes, and where it stops

`t_6` is **not** resolved here. What is established:

### Lower bound: t_6 >= 56, and the shape that achieves it is exhausted

The 56-vertex witness already in `search/k6/witnesses.csv` was re-verified from
scratch -- rebuilt as a graph, checked simple, cycles enumerated with `networkx`:
`C_56 + {(0,2),(0,53),(1,39),(20,39),(39,48),(48,53)}` is pancyclic, 6 chords.

Its shape is `b = 7`, canonical form `((0,1),(0,3),(0,6),(2,4),(4,5),(5,6))`, with
57 distinct cycle forms, so its cap is 59. Running that one shape exactly:

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
n=110 .. 102  eligible=0                        (killed by cap + Hall alone)
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

Levels 110 down to 94 are contiguous, so **no C_n plus 6 chords with n >= 94 is
pancyclic**, i.e. `t_6 <= 93`.

The cost is the problem, and it is measured rather than guessed: the level time
goes 18.1 -> 48.1 -> 521.6 -> 1197.9 -> 2727.1 -> 4682.5 -> 9529.9 seconds from
n=101 to n=95, roughly a factor of **2 per level down**. (These are wall times
under varying contention -- up to four levels plus other agents' jobs shared eight
cores -- so they are indicative, not clean single-core measurements; n=94 came in
at 4070.6s because it ran with the machine much less loaded, which is why the
ratio is quoted over the 101..95 stretch rather than fitted to every point.)

The driver of the growth is the coverage slack `cap - n`: at `cap - n = 0` the
cycle forms must biject onto `[3,n]` and the search dies instantly, and every step
down adds one unit of freedom to every shape already in play, while more shapes
become eligible. There are 37 further levels between n=94 and n=57. That is the
reason this run does not reach an exact `t_6`; it is not a timeout that more
patience fixes at this constant factor.

### What the completed work does pin down

So the k=6 status is an **improved bracket, not an exact value**:

    56  <=  t_6  <=  93

with both ends established here: the lower end by re-verifying the existing
witness against the real graph, the upper end by 17 contiguous exhaustive levels
(n = 110 down to 94) over all 21878 shapes with nothing abandoned. For comparison, the a-priori bound
from the brief's `2^(k+1)-1 = 127` cycles is `t_6 <= 129`; the measured maximum of
109 distinct cycle forms already improves that to 111 with no search at all, and
the sweep takes it to 95.

Two further partial results, each with its cap declared:

- **The best known shape is closed.** As above, the shape of the 56-vertex witness
  is UNSAT at 57, 58 and 59 -- its whole range above 56 -- so it is exhausted.
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
| `test_shapecsp.py` | behaviour gates (section 5) |
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
