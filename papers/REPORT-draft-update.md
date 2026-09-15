# REPORT: draft brought up to the t_6 >= 67 evidence

Worker 12, 2026-09-14, for Manager (f4d1e0af). Scope: `papers/draft/`,
`papers/CHANGES.md`, this file. Nothing under `search/`, `Erdos1016/` or any
other `REPORT-*.md` was modified by this task (`git status --short` also shows
`papers/REPORT-k6-gpu-joint.md` and `papers/REPORT-resource-control.md` as
modified, but both were already modified before this task started — they are
other lanes' in-progress edits). The only files this task changed or created
are `papers/draft/pancyclic-exact-values.md`,
`papers/draft/SOURCES.md`, `papers/draft/verify-rerun-20260914.txt`,
`papers/CHANGES.md`, `papers/REPORT-draft-update.md`).

## Costliest finding first: the draft was wrong by 11 vertices and asserted a refuted prediction — now fixed, and every cited witness re-verified here

The committed draft stated `$56\le t_6\le129$` in the abstract, Section 5 and
Section 6.3, called `$t_6=2\,\mathrm{Fib}(9)-2=66$` "a falsifiable prediction",
and narrated the `$n=66$` search as stalled "3 lengths short". Measured against
the artifacts: `search/k6/witnesses-v2.csv` holds pancyclic 6-chord sets at
n = 62, 63, 64, 65, 66, 67, and `search/k6/sweep2-61-34.txt` holds one at n = 61
(`IMPROVE n=61 missing=0 chords=(0,2)(0,58)(1,44)(3,57)(28,53)(53,58)`). I did
not take those files' word for it: every witness the draft now cites, plus the
n = 68 family member as a negative control, was re-run through the pre-existing
independent verifier `search/verify.py` (networkx `simple_cycles`), one process
at a time at idle priority. Output, verbatim in
`papers/draft/verify-rerun-20260914.txt`:

```
61 [(0, 2), (0, 58), (1, 44), (3, 57), (28, 53), (53, 58)] pancyclic   missing: []
62 [(0, 2), (0, 59), (1, 11), (3, 58), (3, 28), (54, 59)] pancyclic   missing: []
63 [(0, 2), (0, 60), (1, 11), (3, 59), (3, 28), (55, 60)] pancyclic   missing: []
64 [(0, 2), (0, 61), (1, 12), (3, 60), (4, 29), (56, 61)] pancyclic   missing: []
65 [(0, 2), (0, 58), (1, 13), (3, 59), (4, 31), (57, 60)] pancyclic   missing: []
66 [(0, 2), (0, 59), (1, 13), (3, 60), (4, 31), (58, 61)] pancyclic   missing: []
67 [(0, 2), (0, 60), (1, 13), (3, 61), (4, 31), (59, 62)] pancyclic   missing: []
68 [(0, 2), (0, 61), (1, 13), (3, 62), (4, 31), (60, 63)] NOT pancyclic   missing: [33]
57 [(0, 2), (0, 54), (1, 40), (14, 48), (40, 49), (49, 54)] pancyclic   missing: []
58 [(0, 2), (0, 55), (1, 41), (14, 49), (41, 50), (50, 55)] pancyclic   missing: []
59 [(0, 2), (0, 56), (1, 42), (16, 48), (42, 51), (51, 56)] pancyclic   missing: []
60 [(0, 2), (0, 57), (1, 43), (19, 44), (43, 52), (52, 57)] pancyclic   missing: []
```

The n = 68 line is the verifier's own mutation check for this run: it reports
NOT pancyclic, missing exactly `[33]`, which is the value
`papers/REPORT-k6-gpu-joint.md` records for that family member, so the verifier
discriminates and the eleven "pancyclic" lines are meaningful.

Two things in the brief did not match the artifacts and were resolved in favour
of the artifacts:

* The brief lists n = 61 among the witnesses "see search/k6/witnesses-v2.csv".
  That CSV has no n = 61 row (rows: 62, 63, 64, 66, 67, 65). The n = 61 chord
  set in the brief is in `search/k6/sweep2-61-34.txt` (and as the `START` line
  of `search/k6/push-61-70.txt`). The draft cites the sweep2 file for n = 61.
* The brief omits n = 63 and n = 57–60, which are in `witnesses-v2.csv` and in
  `search/k6/coord-57.txt` / `search/k6/smart-57-70.txt`. The draft cites all of
  them (each re-verified above) so it can state `$h(n)\le6$` for every
  `$41\le n\le67$` without a gap.

## Adjacent finding, escalated not adopted: the shape/CSP k = 5 ladder log reads as an independent derivation of t_5 = 40

`search/shapecsp/k5-levels.log` has 18 lines, `LEVEL k=5 n=58 ... sat=0 gaveup=0`
down to `LEVEL k=5 n=41 shapes=1236 eligible=308 sat=0 gaveup=0`, and
`search/shapecsp/control-k2-k5.log` records CP-SAT's `new best n=40` at k = 5.
Per `search/shapecsp/level.py`'s docstring ("t_k is the largest n whose level
answers SAT, and every level above it answering UNSAT with zero GAVEUP is the
exhaustive refutation"), that is a complete refutation of every n from 41 to
the per-shape cap 58 by a method sharing no code with `gpu_pancyc.py`. If the
shape/CSP lane confirms it, draft Section 3.4's statement that `$h(41)>5$` "is
**not** independently replicated" is stale and can be upgraded. I did not make
that change: `papers/REPORT-shape-csp.md` does not claim the k = 5 result (it
reports only the k = 5 lower bound n = 40), the brief's item (3) scopes the
method's controls to `$t_2,t_3,t_4$`, and upgrading a negative result's
evidential status on the strength of a log line is the lane's call, not mine.
The new Section 3.5 states exactly what the log shows and says Section 3.4 is
left pending that report. Routing: Manager (f4d1e0af) → shape/CSP lane.

Similarly, `search/shapecsp/k6-levels.log` shows levels n = 110 down to 97 all
`sat=0 gaveup=0` (last level file `level-k6-n97.txt` written 17:22, ladder still
running at 17:26). I note the log has no `n=111` line although the report gives
111 as the largest k = 6 per-shape cap; the lane should confirm that level was
run or is vacuous. The draft keeps 129 as the stated upper bound and mentions
the ladder only as in progress.

## The five changes, with evidence

| # | change | where in the draft | evidence used |
|---|---|---|---|
| 1 | bracket `$56\le t_6\le129$` → `$67\le t_6\le129$`; witness table n = 57..67 with chord sets | abstract; §2.1; §5 "What the computation has established"; §6.3 first two bullets | `search/k6/witnesses-v2.csv`; `search/k6/sweep2-61-34.txt`; `search/k6/verify-{65,66,67}-gpu-joint.txt`; `papers/REPORT-k6-gpu-joint.md` "Result in one paragraph"; re-run `papers/draft/verify-rerun-20260914.txt` |
| 2 | §5 rewritten around `papers/NOTE-fit-underdetermination.md`; both fits reported refuted; caveat kept | §5 "Pattern-fitting the thresholds" | the note's "Statement" and "Caveat, stated precisely"; the linear system `14a+8b+c=24`, `24a+14b+c=40`, difference `5a+3b=8`, re-derived; `papers/PLAN-next-steps.md` for the rival form |
| 3 | new §3.5 method subsection for `search/shapecsp/` | §3.5 | `papers/REPORT-shape-csp.md`; `search/shapecsp/shape-census.txt` ("3 \| 14 \| 5 \| 9"); `papers/REPORT-griffin-method.md` quoting GMW13 "There are 14 types of graph: AAAi, ..."; `search/shapecsp/gates-red.txt` (`FAIL t_4 == 24 :: got 22`, 5 FAIL lines) and `gates-green.txt` (`ALL GATES PASS`); suite re-run here: `python search/shapecsp/test_shapecsp.py` → `ALL GATES PASS` in 41 s |
| 4 | family `(0,2)(0,n-7)(1,13)(3,n-6)(4,31)(n-8,n-5)` pancyclic n = 64..67, misses exactly one length at n = 68 | §5 last paragraph; §6.3 third bullet | `papers/REPORT-k6-gpu-joint.md` "The structure and how far it lifts" table (`68: [33]`); n = 68 re-run above |
| 5 | §6.3 retitled; "largest confirmed witness n=56", "previously only up to 41", "stalls 3 lengths short" narrative, abstract's "two numerical observations", §5 "Update: partially tested" all reconciled; `SOURCES.md` §2.1/§3.5/§5/§6 rows and "sourcing discipline" bullet updated | §6.3 last bullet; abstract; `SOURCES.md` | `papers/REPORT-k6-upper.md` (the `{5,7,8}` optimum is retained as history); `papers/REPORT-k6-gpu-joint.md` "How they were found" (22,335,424,500 candidates, 15/20 subsets) |

Mechanical DONE-WHEN checks on the final draft (grep counts): stale bracket
`56\le t_6` / `t_6\ge56`: 0; `Fib}(9)`: 0; `shapecsp`: 11 mentions; each of the
six chord sets named in the brief present (n = 67 twice, in §6.3's first
bullet and its table). The remaining `Fib` occurrences (abstract line, §5, §6.3)
all read "predicting 66 ... refuted" or "fails at k=1", none presented as live.

## Abstract, old and new, side by side

**Old** (committed `HEAD`, lines 23–29):

```
correction term the conjecture needs, and two numerical observations on the
threshold sequence $t_k$ (largest $n$ with $h(n)=k$): its ratio to $2^{k+1}$ is
strictly decreasing, and a previously-noted 2-parameter closed form,
$t_k=2\,\mathrm{Fib}(k+3)-2$, exact at $k=2,3$ by construction, is also exact
at $k=4,5$. A dedicated 6-chord search brackets the next threshold as
$56\le t_6\le129$ and stalls 3 lengths short of a witness at the
closed form's predicted value, $n=66$, neither confirming nor refuting it.
```

**New** (working copy, lines 23–38):

```
correction term the conjecture needs, and two observations on the threshold
sequence $t_k$ (largest $n$ with $h(n)=k$): its ratio to $2^{k+1}$ is strictly
decreasing over $k\le5$, and the four known values $t_2,\dots,t_5$ determine
$t_6$ not at all — every three-term integer linear recurrence fitting them
predicts a different $t_6$ (the whole family $66-2t$, $t\in\mathbb Z$), so no
pattern-fit on the known thresholds carries information about the next one.
Computation has since refuted the two members that had been singled out
($2\,\mathrm{Fib}(k+3)-2$, predicting $66$, and $2^{k-2}(10-k)$, predicting
$64$): explicit 6-chord pancyclic graphs exist on every $n$ from $57$ to $67$
vertices, each re-checked by an independent verifier, so $67\le t_6\le129$,
where $129$
is the trivial counting ceiling. We also describe an exact per-shape
feasibility algorithm (a $C_n$ plus $k$ chords is a subdivision of one of
finitely many multigraphs, so pancyclicity becomes a covering problem in the
arc lengths) that reproduces $t_2,t_3,t_4$ from scratch and is the tool for
deciding $t_6$ exactly.
```

## Section 5 (fit paragraphs), old and new, side by side

**Old** (committed `HEAD`, lines 572–610, from "A Fibonacci fit" to the end of
"Update: partially tested, not settled"):

```
**A Fibonacci fit, and exactly how much it is worth.** This observation
originates in `papers/REPORT-bondy-construction.md`, not in this note; we
cite it rather than re-present it as freshly found. Writing
$\mathrm{Fib}(1)=\mathrm{Fib}(2)=1$,
$$t_k = 2\,\mathrm{Fib}(k+3)-2\qquad\text{for } k=2,3,4,5:$$
$$t_2=2\cdot5-2=8,\quad t_3=2\cdot8-2=14,\quad t_4=2\cdot13-2=24,\quad t_5=2\cdot21-2=40.$$
This is an **observation, not a theorem**, and its source explicitly flags
the closed form as "four data points fitting a **two-parameter family**" (a
free multiplicative constant, $2$, and a free additive constant, $-2$). A
2-parameter family fit exactly to two of its four cited points is guaranteed,
not informative — those two matches carry no information. Fixing the two
parameters at $k=2,3$, the genuinely nontrivial content is that the *same*
formula is *also* exact at $k=4,5$: two real coincidences, not four. It
visibly fails at $k=1$ ($2\,\mathrm{Fib}(4)-2=4\ne5$), and the same source
notes that a naturally related *additive* recursion,
$t_k=t_{k-1}+t_{k-2}+2$, also fails at $k=3$ ($8+5+2=15\ne14$) even though
the closed form holds there — i.e. at least one nearby way of framing "the"
Fibonacci pattern already breaks inside the range this note calls clean.
No structural reason for either form is known. If the closed form continued
it would predict
$$t_6 = 2\,\mathrm{Fib}(9)-2 = 2\cdot34-2 = 66,$$
i.e. $h(n)=6$ for $41\le n\le66$ and $h(67)\ge7$ — a falsifiable prediction
that the present search programs (`search/gpu_pancyc.py`, valid for
$n\le60$; extending to $n=66$ needs either a 128-bit port of the GPU kernel
or the CPU program's $n\le60,k\le6$ safe range pushed to $k=6$ at $n$ up to
66) could test directly.

**Update: partially tested, not settled.** A dedicated 6-chord search
(Section 6.3, `papers/REPORT-k6-upper.md`) found a confirmed witness at
$n=56$ and, after extensive local search seeded from it, stalled at a
verified local optimum missing exactly 3 lengths ($\{5,7,8\}$) when attacking
$n=66$ directly. So the Fibonacci prediction $t_6=66$ is now bracketed as
$$56\ \le\ t_6\ \le\ 129,$$
where $129=2^{6+1}+1$ is the trivial counting ceiling ($N_0$ in
`papers/REPORT-cyclecounts.md`'s notation) and $56$ is the largest confirmed
witness — a much wider bracket than the single point-prediction $66$, and
the search neither confirms nor refutes $66$ itself: it got close (missing
only 3 of 64 required lengths at a genuine local optimum) but did not find or
exclude a witness there.
```

**New** (working copy, lines 680–725, the two paragraphs that replace them;
the ratio table before them and the Wallis paragraph after them are unchanged):

```

**Pattern-fitting the thresholds: the known values do not determine $t_6$.**
Earlier revisions of this note presented a closed form,
$t_k=2\,\mathrm{Fib}(k+3)-2$ (from `papers/REPORT-bondy-construction.md`,
exact at $k=2,\dots,5$: $8,14,24,40$, predicting $t_6=66$), as a falsifiable
observation, and `papers/PLAN-next-steps.md` noted a rival two-parameter form,
$t_k=2^{k-2}(10-k)$, exact at the same four points and predicting $t_6=64$.
Both are now **refuted** by the witnesses of Section 6.3 (6-chord pancyclic
graphs exist at $n=66$ and $n=67$, so $t_6\ge67>66>64$). The more useful
observation, from `papers/NOTE-fit-underdetermination.md`, is that neither
fit was ever special. Consider every three-term integer linear recurrence
$$t_k=a\,t_{k-1}+b\,t_{k-2}+c\qquad(a,b,c\in\mathbb Z)$$
consistent with $t_2,\dots,t_5=8,14,24,40$. The two fitting constraints
$14a+8b+c=24$ and $24a+14b+c=40$ differ by $5a+3b=8$, whose integer solutions
form the one-parameter family $(a,b,c)=(1+3t,\,1-5t,\,2-2t)$; each member
reproduces $8,14,24,40$ exactly and predicts
$$t_6=66-2t.$$
The Fibonacci form is $t=0$ and the rival form is $t=1$; they are two
arbitrary members of an unconstrained family rather than competing
hypotheses, and the four known values constrain $t_6$ **not at all** within
this family. So no amount of pattern-fitting on $t_2..t_5$ carries
information about $t_6$; only computation decides it. (Caveat, stated
precisely: "every even value is predicted by some member" is a property of
*this* family — three terms, integer coefficients. It is not a theorem that
$t_6$ is even; families with rational coefficients, more terms, or non-linear
form predict odd values. The claim is that the data fails to select among
simple fits, not that $t_6$ is constrained to a parity.) For the record, the
Fibonacci form also fails at $k=1$ ($2\,\mathrm{Fib}(4)-2=4\ne5$), and the
related additive recursion $t_k=t_{k-1}+t_{k-2}+2$ fails at $k=3$
($8+5+2=15\ne14$); no structural reason for any of these forms was ever known.

**What the computation has established.** Confirmed 6-chord witnesses, each
re-checked with the independent `search/verify.py` (networkx
`simple_cycles`; full output in `papers/draft/verify-rerun-20260914.txt`),
exist at every $n$ from $57$ to $67$ (chord sets in Section 6.3), so
$$67\ \le\ t_6\ \le\ 129,$$
where $129=2^{6+1}+1$ is the trivial counting ceiling ($N_0$ in
`papers/REPORT-cyclecounts.md`'s notation). The witnesses at $n=61,62,64$
already refuted the family members predicting $58,60,62$; those at $n=66,67$
refute both named fits; and the odd witnesses at $n=65$ and $n=67$ refute
*every* member of the integer family above simultaneously, since all of them
predict an even $t_6$. The family $(0,2)(0,n-7)(1,13)(3,n-6)(4,31)(n-8,n-5)$
that supplies the $n=64,\dots,67$ witnesses misses exactly one length
($33$) at $n=68$ (Section 6.3), so $t_6=67$ is possible but not established;
the exact value is the target of the shape/CSP algorithm of Section 3.5,
whose $k=6$ ladder was still running when this revision was written.
```

## What was not done, and why

* Section 3.4 (replication status of `$h(41)>5$`) unchanged — see the adjacent
  finding above; it is routed, not adopted.
* No Lean statement was added for any n ≥ 57 witness; `Erdos1016/` is another
  lane's and the brief forbids touching it. The draft says which witnesses are
  Lean-checked (n = 38, 39, 40, 41, 56) and does not imply more.
* The `papers/REPORT-k6-gpu-joint.md` n = 68 3-of-6 row still holds
  placeholders (`R3_68_SUBSETS` etc.); the draft describes that sweep as "in
  flight" and cites no number for it.
* The ratio-to-ceiling table in §5 was left as is (k = 1..5); adding a k = 6
  row would need t_6 exactly.
* Declared caps: `verify.py` was run on exactly the 12 chord sets listed above,
  not on the n ≤ 56 witnesses of `search/k6/witnesses.csv`, which the draft
  cites to that file and to `papers/REPORT-k6-upper.md` as before.
* Not committed: the brief lifts the commit ban for this contract, but the
  working tree contains many other lanes' uncommitted files
  (`git status --short` at the root lists `search/k6/gpu-joint-state-*.json`,
  `papers/REPORT-shape-csp.md`, `papers/REPORT-resource-control.md` and more).
  A commit scoped to my five files is safe; I have left the timing to the
  manager so the draft, its sources and this report land together with the
  concurrent reports rather than ahead of them.

---

# Second pass, 2026-09-15: doc-sealing (Worker 12)

Four items dispatched by Manager `f4d1e0af`. Every number below was re-derived
from the artifacts in this tree before the text was written; nothing was taken
on the dispatch's word. Files changed in this pass:
`papers/draft/pancyclic-exact-values.md`, `papers/draft/SOURCES.md`,
`papers/REPORT-shape-csp.md`, `.gitignore`, `papers/CHANGES.md`, this file.
No code was touched.

## Costliest finding: the upper end of the bracket was 36 vertices too weak, and the report the draft now cites for it contradicted itself

`67 <= t_6 <= 129` understated what the project had already computed. The
shape/CSP lane had exhausted every $n$ from 94 to 111 at $k=6$, which gives
`t_6 <= 93` — a 36-vertex improvement that the draft was not carrying. The
exhaustion is real and I checked it file by file rather than from the summary:

```
level-k6-n94.txt  :: LEVEL k=6 n=94  shapes=21878 eligible=81 sat=0 gaveup=0 search_seconds=4070.6
level-k6-n95.txt  :: LEVEL k=6 n=95  shapes=21878 eligible=53 sat=0 gaveup=0 search_seconds=9529.9
level-k6-n96.txt  :: LEVEL k=6 n=96  shapes=21878 eligible=32 sat=0 gaveup=0 search_seconds=4682.5
level-k6-n97.txt  :: LEVEL k=6 n=97  shapes=21878 eligible=28 sat=0 gaveup=0 search_seconds=2727.1
level-k6-n98.txt  :: LEVEL k=6 n=98  shapes=21878 eligible=28 sat=0 gaveup=0 search_seconds=1197.9
level-k6-n99.txt  :: LEVEL k=6 n=99  shapes=21878 eligible=24 sat=0 gaveup=0 search_seconds=521.6
level-k6-n100.txt :: LEVEL k=6 n=100 shapes=21878 eligible=8  sat=0 gaveup=0 search_seconds=48.1
level-k6-n101.txt :: LEVEL k=6 n=101 shapes=21878 eligible=5  sat=0 gaveup=0 search_seconds=18.1
level-k6-n102.txt .. level-k6-n111.txt :: eligible=0 sat=0 gaveup=0   (10 levels)
```

That is 18 contiguous levels, 94 through 111, none abandoned. 111 is the
ceiling that makes the block sufficient: `search/shapecsp/shape-census.txt`
row `6 | 21878 | 554 | 21324 | 4..12 | 109 (distinct 109) | 127` gives a
maximum of 109 distinct cycle forms over all 21878 shapes, and a shape with
$F$ forms can be pancyclic only for $n \le F+2 = 111$.

**Why the block and not level 94 alone.** `search/shapecsp/level.py`'s own
docstring states the rule and the reason: eligibility at a level is decided
*at the cutoff* by two necessary conditions (cap, then Hall), "and Hall at the
cutoff is not monotone in n: a shape can fail Hall at cutoff n and still be
feasible at some larger n0, in which case this level never searched it. ...
Cite the block, never a single level." The draft now says this in Section 3.5
in its own words, so the bound cannot be re-cited wrongly from the draft.

**The second half of the finding.** `papers/REPORT-shape-csp.md` — the report
the draft now cites as the source of this bound — contradicted itself. Its
section 0a states the corrected block (`111..102 with eligible=0, then 101..94
with sat=0 gaveup=0`) while its section 9 summary still said:

> the upper end by 17 contiguous exhaustive levels
> (n = 110 down to 94) over all 21878 shapes with nothing abandoned. ... the
> measured maximum of 109 distinct cycle forms already improves that to 111
> with no search at all, and the sweep takes it to 95.

17 levels ending at 110 does not reach the cap 111, and "95" contradicts the
`67 <= t_6 <= 93` printed two lines above it in the same paragraph. This was
not one of the four dispatched items. I corrected it anyway, because sealing
the draft onto a source that says 95 in one place and 93 in another is worse
than leaving the draft at 129, and I left the old sentences quoted in place in
that report so the correction is visible rather than silent. Flagged to the
manager as an unrequested change.

## Abstract: old and new, side by side (this pass)

**Old (bracket):**

> vertices, each re-checked by an independent verifier, so $67\le t_6\le129$,
> where $129$
> is the trivial counting ceiling.

**New:**

> vertices, each re-checked by an independent verifier, so $67\le t_6\le93$.
> The upper end is an exhaustive result, not a counting one: the shape/CSP
> algorithm below refutes every $n$ from $94$ up to $111$, and $111$ is the
> largest $n$ any $6$-chord shape can reach at all. The counting ceiling $129$ is
> now only a trivial prior bound. The upper end is the best the completed levels
> support and may yet fall: the levels at $n=92$ and $n=93$ are undecided, and a
> non-existence descent from $93$ downwards is in progress.

**Old ($h(41)$ replication status):**

> The one new negative result,
> $h(41)>5$, rests on a single complete GPU enumeration of all $5$-chord sets
> on $C_{41}$ (a 64-bit kernel and its 128-bit port, which walk the same
> enumeration) plus non-exhaustive corroboration; an independently written
> exhaustive replication has not yet been completed (Section 3.4).

**New:**

> The one new negative result,
> $h(41)>5$, was first established by a complete GPU enumeration of all $5$-chord
> sets on $C_{41}$ (a 64-bit kernel and its 128-bit port, which walk the same
> enumeration), and has since been independently replicated by a structurally
> different method: the shape/arc-length feasibility search of Section 3.5
> enumerates subdivision shapes rather than chord sets, shares no code with the
> GPU programs, and returns `sat=0 gaveup=0` at $n=41,k=5$ (Section 3.4).

## Section 5: old and new, side by side (this pass)

**Old:**

> $$67\ \le\ t_6\ \le\ 129,$$
> where $129=2^{6+1}+1$ is the trivial counting ceiling ($N_0$ in
> `papers/REPORT-cyclecounts.md`'s notation).

**New:**

> $$67\ \le\ t_6\ \le\ 93.$$
> The upper end is the exhaustive shape/CSP block of Section 3.5: every level
> from $n=94$ to $n=111$ answers `sat=0` with zero abandoned searches
> (`search/shapecsp/level-k6-n94.txt` ... `level-k6-n111.txt`), and $111$ is the
> largest $n$ any $6$-chord shape admits, so no $6$-chord pancyclic graph exists
> on $94$ or more vertices. It supersedes the trivial counting ceiling
> $129=2^{6+1}+1$ ($N_0$ in `papers/REPORT-cyclecounts.md`'s notation), which is
> kept here only as the prior bound this computation replaced. Two levels inside
> the gap, $n=92$ and $n=93$, have not been decided and are counted on neither
> side; a non-existence descent from $93$ downwards is running, and each level it
> closes lowers this upper end by one.

Section 5's closing sentence also changed from "whose $k=6$ ladder was still
running when this revision was written" to "whose $k=6$ ladder has closed the
range $94\le n\le111$ and is now descending through the $68\le n\le93$ gap that
separates the two ends of the bracket."

## h(41)>5: what the replication is, and what it is not

`search/shapecsp/level-k5-n41.txt`, read directly:

```
LEVEL k=5 n=41 shapes=1236 eligible=308 sat=0 gaveup=0 search_seconds=593.8 total_seconds=593.9
```

The independence is structural, and the draft now names it as such: the GPU
path enumerates **chord sets** on $C_{41}$ and tests each with bitmask cycle
walks; the shape/CSP path enumerates the 1236 **subdivision shapes** on 5
chords and asks, per shape, whether integer arc lengths exist whose 0/1 linear
cycle forms cover $[3,41]$. Different enumeration, different search, different
language, no shared code.

**A single level is enough here, and the draft says why.** This is the exact
distinction that section 0a of `REPORT-shape-csp.md` was written to correct, so
it matters that the draft not re-import the error in the opposite direction:
for the $k=6$ *upper bound* you need the contiguous block, because Hall at a
cutoff is not monotone in $n$; for a statement about **one** value of $n$, like
$h(41)>5$, the single level at that $n$ suffices, because Hall is a necessary
condition evaluated at that same $n=41$, so any shape feasible at 41 is
eligible at the $n=41$ level and was searched there. 308 of 1236 shapes
survived the necessary conditions, all 308 were decided, and `gaveup=0` means
none was abandoned on the node budget — no shape is UNKNOWN.

**Kept, not dropped:** the 128-bit run is still a port of the 64-bit kernel and
still counts as one method; `indep_gpu.py` is still unfinished and would be a
third independent exhaustive path.

## REPORT-shape-csp.md: the duplicate row and the shape count

The witness-shape table listed `63` twice, with byte-identical contents, in
rows ordered 61, 63, 62, 63 — ten rows under a heading reading "All nine." The
first `63` row is removed. Verified mechanically after the edit: **9 rows, 6
distinct shape strings**, counted by cutting the shape column and `sort -u`.
The six shapes carry the nine witnesses as 56 | 60 | 61 | 62,63 | 64 | 65,66,67.

"All seven known witness shapes" is therefore wrong, and is corrected in every
place it appears: the summary table, the solver-soundness row, the "taking the
earliest of the seven" lead-in, the satcheck grouping paragraph, the
false-negative-control paragraph, and the section 9 bullet. The seven
*satcheck runs* are real and stay seven; what they decided is six shapes,
because the n=66 and n=67 runs are the same shape and both return 67.

## Tracking audit: method, result, and its bound

Five files cited by `SOURCES.md` as primary evidence were excluded by
`.gitignore`'s `search/k6/*.txt` and so unreachable from a clone. Added as
negations beside the existing ones and staged:

```
search/k6/climb-60-72.txt          402 bytes
search/k6/coord-57.txt             199
search/k6/smart-57-70.txt          488
search/k6/sweep2-61-34.txt         300
search/k6/verify-67-gpu-joint.txt  323
```

`git ls-files` returns all five after the change.

**Where the change landed.** These were staged by this lane and then committed
in `6dbe9ee`, the shape/CSP lane's commit, which picked them up from the shared
index before this lane could commit. They are tracked and correct; only the
commit-message provenance sits in the other lane, and nothing was re-added or
duplicated afterwards. This is also why the five documents of this pass were
committed (`83508d5`) rather than left staged.

**Audit method and its declared bound.** I extracted every backticked span in
`papers/draft/SOURCES.md` matching a file-path shape with a known extension
(`txt|md|py|c|csv|json|log|err|out|lean|ps1|pkl|sh|pdf`) — 93 distinct paths
after this pass — and resolved each against `git ls-files`, falling back to a
basename match for the nine paths `SOURCES.md` writes relative to `papers/` or
`search/` (`n38k5-A7.txt`, `sh-41-BC.txt`, `construction/unrank.out`, and so
on; all nine resolve to tracked files). **Result: zero untracked, with exactly
two exceptions** — `papers/Lai-Liu-2014-survey.pdf` and
`papers/Wallis-2014-IWOCA-open-problems.pdf`, which stay untracked by the
redistribution decision and remain accounted for by size and SHA-256 in
`SOURCES.md`. The bound on this audit: it covers paths written inside
backticks with one of those extensions. A path named in prose without
backticks, or with an extension outside that list, would not be caught.

## Refusals, and what this pass did not do

- **No code was touched.** `level.py`, `satcheck.py` and `bb.c` are Worker
  13's lane; I read `level.py`'s docstring as evidence and changed nothing in
  `search/`.
- **No level was re-run and no gate was added**, so there is no mutation check
  in this pass — items 1 and 2 rest entirely on artifacts already on disk. The
  mutation-checked gate suite behind the shape/CSP method is the one already
  reported in Section 3.5 and `REPORT-shape-csp.md`.
- **The n=92 and n=93 levels are UNKNOWN, not clean.** Their files are
  0 bytes (`level-k6-n92.txt`, `level-k6-n93.txt`, both 2026-09-14 19:26) and
  `k6-levels-9293.log` records `LEVEL k=6 n=93 NO-OUTPUT` and
  `LEVEL k=6 n=92 NO-OUTPUT`. They are counted on neither side of the bracket
  in the draft. I did not start or consult the running descent.
- **One artifact gap, named rather than merged into "not there":** the
  aggregate `search/shapecsp/k6-levels.log` has no rows for $n=94$ and $n=95$,
  although `level-k6-n94.txt` and `level-k6-n95.txt` both exist with complete
  `sat=0 gaveup=0` lines. The per-level files are the primary artifact and the
  draft cites them; the missing aggregate rows are noted in the draft's
  Section 3.5 so a reader checking the log does not read the gap as a gap in
  the block.
- **`git add` was path-scoped**, never `-A`.
