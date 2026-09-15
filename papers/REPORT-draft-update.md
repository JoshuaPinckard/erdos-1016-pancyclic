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
