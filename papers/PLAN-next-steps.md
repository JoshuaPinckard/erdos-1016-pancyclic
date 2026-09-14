# Erdős #1016 — independent review and next-steps plan

Planner review, 2026-09-14. Scope: read-only assessment of the whole project
(draft, CHANGES/SOURCES, novelty/Griffin/k6/cyclecount/Fibonacci reports,
`notes/01`, the Lean sources, and the `search/` + `papers/construction/`
artifacts) with an adversarial eye on what is publishable, what is strongest,
what has been missed, and what is overclaimed relative to its artifact. No code
was run and no file other than this one was edited. Evidence is given as
path + quoted string, never file:line.

Bottom line up front: the **computational core is real and the write-up is
unusually honest**, but the project's single most load-bearing new claim —
`h(41)=6`, the one genuine threshold crossing in the new range — rests on a
lower bound (no 5-chord graph on 41 vertices) that is **not independently
confirmed the way the draft implies, not formalised, and whose supporting
files are largely not even committed to the repository.** That gap, not any of
the softer overclaims the referee report already caught, is the costliest
thing here.

---

## 1. Costliest finding: the `h(41)=6` lower bound is single-method, and its evidence is untracked

`h(41)=6` is the only place in `n=38..41` where the threshold actually moves
(38, 39, 40 all stay at `h=5`; only 41 forces a sixth chord). Its truth
depends entirely on the negative result "no set of 5 chords makes `C_41`
pancyclic." The draft states this is exhaustive and cross-checked
(`papers/draft/pancyclic-exact-values.md`: "the `k=5` elimination is
exhaustive", and Section 3.4's table row for `n=41`). Tracing the actual
artifacts, the independence is thinner than the prose:

- **The two "exhaustive NONE" runs are the same algorithm.** `search/gpu-41-5d.txt`
  ("`NONE n=41 k=5 tested=17615450195`") and the 128-bit rerun
  `search/k6/gpu128-41-5.txt` ("`NONE n=41 k=5 tested=17615450195`") are the
  original CuPy kernel and a two-word port of *that same kernel*
  (`search/k6/gpu_pancyc128.py` docstring: "128-bit (two-word) port of
  search/gpu_pancyc.py … Nothing else about the algorithm changes"). Identical
  `tested=` totals confirm they walk the identical enumeration. This is a
  strong check against 64-bit overflow, not against a logic error shared by
  both.

- **The genuinely independent exhaustive check does not exist yet.** The
  from-scratch direct-DFS GPU replication is explicit that it did *not* finish:
  `papers/REVIEW-independent-gpu.md` states "the exhaustive b=2 total remains
  UNKNOWN pending continuation from the corrected checkpoint" and that an
  earlier full-looking run "used a mistaken gap expression and rejected every
  candidate; its apparent completion is invalid." It covered a corrected prefix
  of 739,246,080 of 15,147,912,850 mode-A ranks — under 5% of one of the three
  modes.

- **The CPU cross-check for `n=41` aborted.** `search/hn_k5.csv` records
  "`41,5,ABORTED-no-output-processes-died,,8044,0`"; the shard outputs
  `search/sh-41-A0.txt … sh-41-BC.txt` are all zero bytes. So the CPU
  `pancyc3.exe` shard run — the one structurally different exhaustive path — did
  not produce a NONE for 41 at all (this is the process-death pattern the
  throttling record already describes).

- **No lower bound is formalised.** `Axioms.lean` says so directly: "the
  matching LOWER bounds (no k-chord pancyclic graph on n vertices) are NOT
  formalised here; they rest on the exhaustive search programs in search/." The
  Lean layer only certifies the seven *upper-bound* witnesses.

Net: the headline table's one novel threshold crossing is currently
one-algorithm-plus-a-port. The random-sampling and DFS-witness cross-checks in
`papers/REVIEW-gpu-corroboration.md` and `papers/REVIEW-independent.md` confirm
the *witnesses* (existence, `n=38,40,41`) and reproduce Griffin's `n=24→25`
boundary, but none of them independently closes the `n=41,k=5` *non-existence*.
This is not a claim that the result is wrong — the two kernel runs plus the CSP
lane (Section 5) point the same way — but the draft's "exhaustive …
cross-checked by three from-scratch verifiers" reads, for this specific
elimination, as stronger than the artifacts support.

**Reproducibility compounds it.** `.gitignore` excludes `search/*.txt`,
`search/k6/*.txt`, `*.out`, `*.err`, and `search/gpu-state-*.json`. So the files
`papers/draft/SOURCES.md` names as *primary* evidence are not in the repo:
`git ls-files` does not return `search/n38k5-A0.txt` (the `n=38` witness source),
`search/ls-41-6.txt` (the `n=41,k=6` witness source), or the full
`search/gpu-41-5.txt` progress log. Only `search/gpu-40-5-all.txt`,
`search/gpu-41-5d.txt` (a one-line summary), `search/hn_k5.csv`, and
`search/k6/witnesses.csv` are tracked. A referee cloning the repository cannot
reach most of SOURCES.md's cited files. Rank: this is a correctness-of-record
defect one notch below a wrong value — the values look right, but the chain that
proves them is not preserved where the paper points.

---

## 2. What is publishable, ranked

1. **The four-value exact-table extension `h(38..41)=5,5,5,6`, packaged as a
   short note with the Lean-checked upper bounds and an OEIS update.** This is
   the strongest, most defensible unit. It genuinely extends the only prior
   exact table (`papers/1312.0274.txt`, Griffin Table 1, stops at `n=37`), the
   project's own four literature sweeps found nothing that anticipates it
   (`papers/REPORT-novelty-check.md`: GMW13 "does not generalize beyond `v=22`",
   "the cases `v>=23` remain open"), and the seven upper-bound witnesses are
   kernel-checked with a clean axiom set (`ax.log`:
   "`isPancyclic_G38 … depends on axioms: [propext, Classical.choice,
   Quot.sound]`", same for the other six). **Venue:** *Journal of Integer
   Sequences*, *INTEGERS*, or an OEIS A105206 + erdosproblems.com/1016 update
   with the Lean artifact attached. Not a flagship combinatorics journal — see
   the referee's own framing note (`papers/REFEREE-report.md`, Section 7:
   "better framed as a technical note or an OEIS/erdosproblems.com update than
   as a standalone research paper"). Condition: close the Section 1 lower-bound
   gap first.

2. **The shape/CSP exact-value algorithm (`search/shapecsp/`), if it decides
   `t_6`.** This is the most novel *method* in the project and the draft does
   not mention it at all. It reduces `h(n)` to a finite per-shape CP-SAT
   feasibility problem with a rigorous Hall-condition upper bound
   (`search/shapecsp/bound.py`: "Both are pure necessary conditions, so a shape
   failing at n cannot reach n"), and it independently reproduces every known
   threshold: `search/shapecsp/control-k2-k5.log` shows "`t_2 = 8`", "`t_3 = 14`",
   "`t_4 = 24`" each with "`unknown: 0`", and `k=5` reaching "`new best n=40`".
   If a `k=6` sweep terminates with `unknown=0`, it *decides* `t_6` by a method
   entirely independent of the cycle-space search — a real research
   contribution and the natural centerpiece of a stronger paper. **Venue:** a
   combinatorics or experimental-mathematics journal, contingent on the `k=6`
   run actually closing.

3. **The formalisation angle on its own.** `Erdos1016/` proving `IsPancyclic`
   for five graphs via a genuine list-to-`Walk.IsCycle` bridge
   (`Erdos1016/ListCycle.lean`, `exists_cycle_of_list`) is publishable only as a
   small applied-formalisation note, and only honestly if paired with the
   caveat that it is upper-bounds-only. Weak as a standalone; better as a
   subsection of item 1.

4. **The structural lemmas (Section 4) as a survey/expository contribution.**
   The corrected subdivision lemma and the three consequences are correct
   (`papers/REVIEW-notes01.md` re-derives the wall inequality as "a complete,
   checkable proof"), but the referee is right that they are close to
   tautological and non-load-bearing (`papers/REFEREE-report.md`, Section 3.1:
   "the corrected lemma is very close to a tautology"). Not independently
   publishable; fine as context.

**Strongest single result:** item 1, the exact table, specifically the
`h(41)=6` crossing — it is the only value in the project that a knowledgeable
reader could not have produced from Griffin's construction, and it is the one
that changes the sequence. Its strength is entirely gated on repairing the
Section 1 independence/tracking gap.

---

## 3. Missed, understated, or newly-stale — each with its artifact

- **`t_6` is already known to be ≥ 64, not 56 — the draft is stale.** The
  abstract and Section 6.3 of `papers/draft/pancyclic-exact-values.md` say the
  largest confirmed 6-chord witness is `n=56` and bracket `56 ≤ t_6 ≤ 129`. But
  `search/k6/witnesses-v2.csv` records independently re-verified witnesses at
  `n=62,63,64` ("`64,"(0,2) (0,61) (1,12) (3,60) (4,29) (56,61)",…,pancyclic`"),
  and `search/k6/push-61-70.txt` shows for `n=64` "`independent verify.py agrees:
  True`". So the correct current bracket is **`64 ≤ t_6 ≤ 129`**. The
  committed `search/k6/witnesses.csv` still tops out at `n=54`; the newer
  witnesses live only in the untracked `witnesses-v2.csv` and `push-61-70.txt`.
  This is both a missed update and part of the tracking defect in Section 1.

- **The Fibonacci fit is oversold, and worse than the draft's own honest
  caveat: a rival 2-parameter formula fits equally and disagrees at `t_6`.**
  The draft (Section 5) already flags `t_k = 2·Fib(k+3)−2` as "a two-parameter
  family" with only `k=4,5` as genuine coincidences. Recomputed this session
  directly from `t_2..t_5 = 8,14,24,40`: the equally-simple two-parameter form
  **`t_k = 2^(k−2)·(10−k)`** also reproduces `8,14,24,40` exactly at `k=2..5`
  and predicts **`t_6 = 64`**, whereas the Fibonacci form predicts `66`. Two
  distinct two-parameter families nail the same four points and split at six, so
  "the pattern" predicts nothing at `t_6`. And the currently-confirmed lower
  bound (`t_6 ≥ 64`, above) coincidentally equals the *rival's* prediction, not
  the Fibonacci one. The honest framing is stronger than the draft's: `t_6` is
  the discriminator between at least two equally-supported fits, and the data
  so far leans away from `66`. Neither is refuted.

- **The shape/CSP lane is missing from the manuscript entirely.** No mention of
  `search/shapecsp/` appears in `papers/draft/pancyclic-exact-values.md` or
  `papers/draft/SOURCES.md`. It is the project's best independent
  cross-check on the lower bounds (it re-derives `t_2..t_4` with `unknown:0`,
  `search/shapecsp/control-k2-k5.log`) and its only realistic route to a
  *decided* `t_6`. Undersold to the point of omission.

- **The `n=41,k=5` elimination's independence is overstated** — see Section 1.
  Artifact: `papers/REVIEW-independent-gpu.md` ("remains UNKNOWN") vs. the
  draft's "cross-checked by three further from-scratch verifiers." The three
  verifiers confirm *witnesses*, not this *non-existence*.

- **Understated genuine strength: the `n=24→25` boundary was independently
  re-derived from scratch.** `papers/REVIEW-independent.md` reports a direct-DFS
  enumeration ("`26,974,255 tested … 2 classes`" at `n=24`, "`35,303,774 …
  0 witnesses`" at `n=25`) reproducing Griffin's `k=4` boundary with unrelated
  code. This is a real independent replication of a Griffin value and the draft
  mentions it only in passing; it is better evidence of method-soundness than
  the random-sampling controls it sits next to.

- **Griffin's "finite reduction" premise was corrected, and that correction is
  worth stating in the paper.** `papers/REPORT-griffin-method.md` establishes
  that what makes Griffin's `k≤4` search finite is the elementary counting
  ceiling `n ≤ 2^(k+1)+1 = 33`, not the arc-contraction machinery (Props 3–4);
  and that the abstract's "29 vertices" does not appear in the body, which says
  "31". The draft's footnote captures the 29/31 point; the "finiteness comes
  from counting, not from a structural reduction" point is not in the draft and
  sharpens Section 3.4.

- **Not overclaimed (checked, credit where due):** the novelty hedge is correctly
  scoped (`papers/REPORT-novelty-check.md` verdict: "no source anywhere reaches
  `n=38`"); the GKW16 attribution is now properly hedged to Tao's "seems to
  exist" and AK's "an approximation" (`papers/CHANGES.md`, Headline finding 1);
  the counting-cannot-suffice claim was narrowed to the trivial ceiling
  (`papers/CHANGES.md`, Headline finding 3); the abstract now states program
  *capability* not that every run was exhaustive. The referee's seven required
  changes appear all applied per `papers/CHANGES.md`. The remaining exposure is
  the lower-bound independence of Section 1, which the referee did **not** flag
  and which is the real weak point.

---

## 4. The upper-bound / lower-bound asymmetry, stated plainly

Every upper bound in the project is a witness — an explicit graph — and seven of
them are kernel-checked with axioms `[propext, Classical.choice, Quot.sound]`
and no `sorry`/`native_decide` (`ax.log`, `papers/REPORT-lean-witness.md`). A
witness is self-certifying: once the cycle lists check, `h(n) ≤ k` is beyond
doubt. The Lean `n=40` witness `chords40 = [(0,5),(1,5),(2,30),(3,10),(4,11)]`
(`Erdos1016/Witness39_40.lean`) even matches a row of the exhaustive run
(`search/gpu-40-5-all.txt`: "`WITNESS n=40 k=5 : (0,5) (1,5) (2,30) (3,10)
(4,11)`") and `search/hn_k5.csv`.

Every lower bound is a *non-existence over a search space* — `h(n) > k−1`
because "no `(k−1)`-chord graph is pancyclic." That is a claim about
millions-to-billions of graphs, certified only by a program's exhaustion, and
**none of it is formalised.** The two are not symmetric kinds of evidence, and
the paper should say so where it currently blurs them: for `n=38,39,40` the
lower bound `h ≥ 5` is airtight from *pure counting* (`n−2 ≥ 36 > 31 = 2^5−1`,
`papers/REFEREE-report.md` §3.4 — needs no search at all), but for `n=41` the
lower bound `h ≥ 6` is the *only* one requiring an actual exhaustive `k=5`
elimination, and it is exactly the one whose independent confirmation is
incomplete (Section 1). The formalisation asymmetry and the
independence asymmetry point at the same single load-bearing computation.

Formalising a lower bound is possible in principle (a Lean `decide` over the
same case-split enumeration) but is a large effort — the `k=5`, `n=41` space is
~1.5×10^10 mode-A sets; kernel `decide` over that is not feasible without a
verified enumerator and reflection proof. This is a genuine research task, not a
cleanup, and should be named as such rather than implied to already hold.

---

## 5. Prioritised next steps

Each step: rough cost under the one-process / BelowNormal / 20%-CPU throttle,
and a concrete completion test. Steps 1–2 are the ones that gate publication of
the strongest result; 3 is the one that could upgrade the paper's ambition.
Committing/pushing is out of scope for search agents (and for this planner);
step 1's git actions are flagged as operator actions.

**Step 1 — Preserve the evidence the paper cites (operator action, ~15 min).**
Force-add or un-ignore the files `papers/draft/SOURCES.md` names as primary:
at minimum `search/n38k5-A0.txt`, `search/ls-41-6.txt`, `search/gpu-41-5.txt`,
`search/k6/witnesses-v2.csv`, `search/k6/push-61-70.txt`, and the entire
`search/shapecsp/` lane, plus the state JSONs proving exhaustion coverage
(`search/gpu-state-41-5.json`). *Completion test:* for every file path quoted in
`SOURCES.md`, `git ls-files <path>` returns it; a fresh clone into a scratch dir
contains every witness and elimination log the draft points to. Cost: negligible
compute. Highest priority because it is nearly free and the artifact is
currently not reproducible from the repo.

**Step 2 — Get one genuinely independent exhaustive confirmation of
`n=41,k=5` = NONE.** Two routes, either suffices; prefer (b) because it is
structurally furthest from the cycle-space kernel:
  (a) Finish the direct-DFS GPU enumeration to full coverage of all three modes,
  continuing from the corrected checkpoint (`papers/construction/indep_gpu.py`,
  `indep-gpu-state-corrected.json`). *Completion test:* the state file's covered
  ranks equal the full mode-A ∪ B ∪ C count with zero hits, and a tracked log
  records `NONE`.
  (b) Run the shape/CSP solver at `k=5, target=41` (`search/shapecsp/run_shard.py
  5 41 <shard> <nshards>`) across shards to exhaustion. *Completion test:* every
  shape with cap ≥ 41 returns INFEASIBLE with `unknown=0` in the summary lines,
  i.e. no `k=5` shape reaches `n=41`, independently reproducing `t_5=40`. Cost:
  route (b) is minutes-to-hours at `k=5` (the `k=4` full sweep was 8.4s per
  `control-k2-k5.log`; `k=5` is the `n=40`-reaching run already partially in that
  log). This is the cheapest way to convert "one algorithm twice" into "two
  independent methods" for the one load-bearing lower bound.

**Step 3 — Decide `t_6` with the shape/CSP solver (the real prize).** Sweep
`k=6` at ascending targets `65,66,67` (`search/shapecsp/run_shard.py 6 <target>
…`). *Completion test:* either a SAT shape yields a witness at the target
(pushing the confirmed lower bound up, cross-checked by `search/k6/verify.py` /
`search/verify.py`), or all shapes with cap ≥ target return INFEASIBLE with
`unknown=0`, proving `t_6 < target`. The decisive outcome is a target where SAT
at `t` and all-INFEASIBLE at `t+1` bracket `t_6 = t` exactly. Cost: this is the
open compute question — `k=6` has far more shapes than `k=5` (the shape counts
in `control-k2-k5.log` are 3, 14, 103 for `k=2,3,4`), and individual CP-SAT
calls may return `UNKNOWN` under a time limit; expect this to need patient
sharded runs within the throttle, possibly days of wall-clock, not a single
session. If it terminates cleanly it settles the Fibonacci-vs-rival question
outright and is the strongest result the project could produce.

**Step 4 — Update the draft to current evidence (writing, no compute).**
(i) Change the `t_6` bracket everywhere to `64 ≤ t_6 ≤ 129` and cite
`search/k6/witnesses-v2.csv`; (ii) add the rival fit `t_k = 2^(k−2)(10−k)`
(exact at `k=2..5`, predicts `t_6=64`) beside the Fibonacci form and reframe
`t_6` as the discriminator; (iii) add a "shape/CSP exact algorithm" method
subsection citing `search/shapecsp/` and its `t_2..t_4` reproduction with
`unknown:0`; (iv) rewrite the Section 1 / Section 3.4 lower-bound language so the
`n=41,k=5` elimination's evidence status (two runs of one kernel + whichever
independent confirmation Step 2 produced) is stated exactly, and so the
upper/lower formalisation asymmetry is explicit. *Completion test:* no number in
the draft contradicts a tracked artifact (re-run the SOURCES.md cross-index),
and the `56`/`66`-based sentences are gone.

**Step 5 — Optional: Lean-check the new frontier witnesses.** Add
`isPancyclic`-style witnesses for `n=62,63,64` (same `ListCycle.lean` bridge as
`Erdos1016/Witness56.lean`). *Completion test:* `lake build` stays green and
`#print axioms` on the new theorems reports exactly
`[propext, Classical.choice, Quot.sound]`. Low value relative to Steps 1–3
(more upper-bound witnesses do not touch the lower-bound gap), but cheap and it
keeps the formal layer at the true frontier instead of a stale `n=56`.

---

## 6. One-line verdict

Publish the four-value table as a technical note **after** Step 1 (preserve the
evidence) and Step 2 (independently confirm the `h(41)=6` lower bound); treat
Step 3 (decide `t_6` via the shape/CSP solver) as the upgrade that would turn a
solid note into a genuine research contribution and settle the Fibonacci
question the draft currently has to leave open.
