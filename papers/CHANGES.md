# Changes made in response to `papers/REFEREE-report.md`

Each referee item, and exactly how it was resolved in
`papers/draft/pancyclic-exact-values.md` (revised) and
`papers/draft/SOURCES.md` (updated to match). Manager's specific resolution
text is followed where given; independent verification was re-run before
citing any new Lean claim, per standing practice this session.

## Headline finding 1: GKW 2016 attribution (§5.1 of the referee report)

**Resolution applied (Manager's exact instruction):** state only what can be
sourced. Section 1's GKW16 paragraph now says: we did not obtain Chapter 4
(`papers/REPORT-bondy-construction.md`, "Not obtained" via two independent
methods); Tao's comment (18 Oct 2025) says the proof "**seems to exist**" in
Ch. 4.5, and that hedge is preserved verbatim rather than upgraded; and
Alon–Krivelevich attribute the construction to GKW and reproduce "an
approximation" of it. `REPORT-lit-1.md`'s earlier "the public abstract
confirms" line is downgraded in the text to: only the chapter's *title*,
"Minimal Pancyclicity," is confirmed, via the publisher's table of contents —
no abstract or body content was ever seen. Section 6.3's construction is now
explicitly cited to Alon–Krivelevich's paraphrase (with the exact source,
`papers/REPORT-bondy-construction.md`), not to GKW16 directly, and a new
sentence there also reports that this general recipe *undershoots* the
project's actual best-known $t_k$ values by 50%–12.5% for $k\le5$ — context
the original draft omitted entirely. Section 5's Wallis-Question-2 sentence
was also softened from "remains exactly at George–Khodkar–Wallis's ... bound"
to "reportedly proved in [GKW16]," cross-referencing Section 1's caveat.

## Headline finding 2: Fibonacci fit overclaim (§4.1)

**Resolution applied (Manager's exact instruction):** the fit is now
presented as an observation *from* `papers/REPORT-bondy-construction.md`,
cited by name (it was previously presented with no citation, reading as if
freshly derived in this note). The text now states explicitly that the
closed form has two free parameters (a multiplicative constant and an
additive constant), so two of its four cited matches ($k=2,3$) are
guaranteed by construction and carry no information — only the matches at
$k=4,5$ are genuine coincidences. It also now reports, from the same source,
that a natural related additive recursion fails at $k=3$. The $56\le
t_6\le129$ bracket (established in the round before this one) is unchanged
and kept.

## Headline finding 3: "counting cannot suffice" self-contradiction (§4.3)

**Resolution applied (Manager's exact precise statement):** Consequence 1's
bolded claim is replaced with the precise version: nested chords already
realise at least $2^k$ cycles, so any refinement of the counting ceiling
inverts to $h(n)\ge\log_2(n-1)-1+O(1)$ — because $M(k)=\Theta(2^k)$ under any
such refinement, inverting it can adjust the additive constant but can never
produce an unboundedly growing correction. Cycle counting **can** and does
improve the constant (Shi's and Rautenbach–Stella's exact values, cited two
paragraphs later, are real instances of this), but **cannot** by itself
supply the $\log_*n$-type term the full conjecture needs. Section 4's title
was changed from "...and why counting cannot suffice" to "...and what
counting can and cannot give" to match. The Rautenbach–Stella paragraph
itself needed no change — it was already consistent with the corrected
claim; only Consequence 1's overly-absolute framing was in tension with it.

## Required change 1: stale abstract

Rewritten. The abstract no longer states the bare "predicting $t_6=66$"
point-prediction; it now states the fit is a previously-noted 2-parameter
closed form and reports the $56\le t_6\le129$ bracket with the $n=66$ stall,
matching Section 5's body text.

## Required change 2: Section 6.3 GKW qualification

Done as part of Headline finding 1 above.

## Required change 3: Fibonacci two-parameter caveat + citation

Done as part of Headline finding 2 above.

## Required change 4: Section 3.4's counting argument

Simplified per the referee report's own suggested fix: the $h(n)\ge5$
lower bound for $n=38..41$ is now derived directly from pure counting
($n-2\ge36>31=2^{4+1}-1$ for all four values), with no reliance on any
characterization of how far Griffin's exhaustive $k\le4$ search was run. The
old, imprecise "which the paper states was run without restriction to small
$n$" language is removed.

## Required change 5: missing [GMW13] reference

Added to the References list (`J. C. George, A. Marr, W. D. Wallis, "Minimal
pancyclic graphs," J. Combin. Math. Combin. Comput. 86 (2013), 125–133`), and
the inline "[George–Marr–Wallis 2013]" text in Section 5 replaced with the
bracket-key `[GMW13]` to match the citation style used everywhere else.

## Required change 6: Consequence 1's derivation gap

Closed. The draft now includes, in-line, the one-sentence reconstruction of
why $A$ gets $2^k-1$ and $B$ gets $2^k$: the $K=\varnothing$ case can only
ever contribute the full Hamilton cycle (which always uses $uv$), so it can
never land in $A$. This was previously only recorded in
`papers/REVIEW-notes01.md`, not in the manuscript itself.

## Required change 7: Section 4 title / bold claim scope

Done as part of Headline finding 3 above.

## PancyclicWithChords for $n=39,40,56$ (Manager's item 4)

`Erdos1016/Excess2.lean` (new) restates `isPancyclic_G39`/`_G40`
(`Erdos1016/Witness39_40.lean`, new) and `isPancyclic_G56`
(`Erdos1016/Witness56.lean`) in `PancyclicWithChords` form:
`pancyclicWithChords_39_5`, `pancyclicWithChords_40_5`,
`pancyclicWithChords_56_6`. **Independently re-verified in this session
before citing, exactly as for every earlier Lean claim:** `lake build
Erdos1016.Excess2` completes (`Build completed successfully (8713 jobs)`,
style-linter warnings only, no `sorry`) and a fresh `#print axioms` on all
three new theorems reports exactly `[propext, Classical.choice,
Quot.sound]`. (Manager's message reported "build 8715 jobs"; the build
observed independently in this session reports 8713 — recorded as the
number actually measured here, not corrected against or assumed to
contradict Manager's figure, since job counts can differ slightly by which
targets are included in a given invocation. The important, checked fact —
zero errors, matching axiom set — agrees exactly.) Section 3.3 and
`SOURCES.md` updated accordingly; the earlier "in progress, not yet in this
file" note for $n=39,40$ is removed since it is now done.

## Suggested changes also picked up (cheap, directly adjacent to required edits)

* Abstract's "two independently implemented exhaustive GPU/CPU chord
  searches" softened to note that "exhaustive" describes program capability,
  not that every individual run was carried to full exhaustion (some
  witnesses were stop-at-first-hit searches; this is methodologically fine
  but the original phrasing overstated it), and updated to mention the
  Lean verification alongside the other three from-scratch verifiers.
* Added a one-line note in `SOURCES.md` that [Shi94] and [RS05], like
  [GKW16], were never obtained as full text — only publisher abstracts and
  Griffin's own quotations of their theorems were seen — so a reader can
  calibrate confidence the same way as for the GKW16 fix above.

## Griffin exhaustive-search cutoff: abstract vs. body (Manager's narrow authorization, this session)

**Resolution applied (Manager's exact instruction, authorizing this one edit
only):** Section 1's Griffin paragraph previously repeated Griffin's own
*abstract*, "combining an exhaustive search on graphs with up to 29 vertices
with a 5-chord construction valid through $n=37$." `papers/REPORT-novelty-check.md`
(Follow-up 3) found that "29" does not appear anywhere in the paper's body
text, and that the body's own statement is structurally different, not just
numerically: exhaustive "for Hamiltonian graphs with at most 4 chords" with
no stated vertex cap (finite only because Corollary 1's counting ceiling
already forces $n\le33$ for $k=4$), and exhaustive "for Hamiltonian graphs
with 5 chords and at most 31 vertices" — 31, not 29 — for the 5-chord case.
The sentence now quotes the body verbatim instead of the abstract, and a new
footnote (`[^griffin-cutoff]`) records the abstract/body discrepancy
explicitly — quoting both numbers and noting which one the body actually
supports — rather than silently substituting 31 for 29 with no trace, so a
referee who checks Griffin's abstract does not conclude this note misread it.
Nothing else in the draft was touched, per Manager's explicit "this one only"
scope.

## Not changed

The referee report's remaining suggested-only items (reconsidering the
paper's overall framing as a technical note vs. a research paper, and the
Markström citation suggestion) were not acted on — Manager's instruction was
to apply the required list plus the five specific resolutions given; neither
of those two suggestions was named.

## Record-integrity pass (2026-09-14, Worker 11; full detail in `papers/REPORT-record-integrity.md`)

Each change below was driven by a measured mismatch between what the draft
claimed and what the repository actually contained.

1. **`.gitignore` — cited evidence was not in the repository.** `git
   ls-files` reported NOT TRACKED for `search/n38k5-A0.txt`,
   `search/ls-41-6.txt` and `search/gpu-41-5.txt` (and for every other
   `search/*.txt`, `*.out`, `*.log` and `ax*.lean` file `SOURCES.md` names),
   because of blanket ignore patterns. Added explicit `!path` negations for
   the 31 files `SOURCES.md` and Section 3.4 cite (the nine `n38k5-*` shard
   files, `ls-41-6.txt`, `gpu-41-5.txt`, the nine zero-byte `sh-41-*` shard
   files, `k6/gpu128-41-5.txt`, `k6/coord-66.txt`, `k6/strict-66.txt`,
   `k6/gkw-K4.txt`, six `papers/construction/*.out|*.log` corroboration
   artifacts, and `Axioms.lean`) and committed them. The two cited third-party
   PDFs (`Lai-Liu-2014-survey.pdf`, `Wallis-2014-IWOCA-open-problems.pdf`)
   stay untracked on purpose (redistribution) and are accounted for in
   `SOURCES.md` by size and SHA-256. Also tracked `search/k6/gpu_pancyc128.py`,
   the program whose `gpu128-41-5.txt` output is now cited.

2. **Section 3.4 — the $n=41,k=5$ non-existence claim was overstated.** The
   old text called the elimination "exhaustive" and, together with the
   abstract, folded it into "cross-checked by three from-scratch verifiers."
   Measured: the two `NONE` runs (`search/gpu-41-5d.txt`,
   `search/k6/gpu128-41-5.txt`) both print `tested=17615450195`, which is
   exactly the case split's candidate count (recomputed from
   `gpu_pancyc.py`'s `main`), and the second program's docstring says it is a
   "port … Nothing else about the algorithm changes"; the CPU shard run is
   `ABORTED-no-output-processes-died` with nine zero-byte outputs; the
   from-scratch `indep_gpu.py` replication says its exhaustive total "remains
   UNKNOWN". Rewrote the $n=41$ row and replaced the "every witness … at
   least two of the three verifiers" paragraph with a "What is multiply
   confirmed, and what is not" passage that keeps the witnesses (all
   reconfirmed by `verify.py`, `check.py`, `indep.c` and Lean) at full
   strength, keeps $h(n)\ge5$ as pure counting, and states that $h(41)>5$
   rests on one complete enumeration by one algorithm plus a port, with
   corroboration but no finished independent replication. The abstract's
   corresponding sentence and Section 2's $n=41$ row were aligned with it.

3. **Section 3.3 / `SOURCES.md` — "cumulative across resumed runs" was
   wrong.** The draft said `gpu-41-5d.txt`'s total "spans several restarted
   invocations (visible as the ABORTED/NONE sequence in hn_k5.csv)". Measured:
   `search/gpu-41-5.txt` is one uninterrupted walk (progress 0.4% → 100.0%,
   719 s) reaching the same total, and `hn_k5.csv`'s rows are written by the
   CPU runner `run_shards.ps1`, not by the GPU program. Corrected both
   places; `gpu-41-5.txt` (not the 18-second re-invocation `gpu-41-5d.txt`)
   is now the primary citation.

4. **`search/hn_k5.csv` — vacuous rows and malformed lines.** Rows
   `41,5,NONE,,66,0` and `41,5,NONE,,187,0` claimed `NONE` with zero
   candidates tested (the runner sums `tested=` over shard outputs, so dead
   shards yield 0). Re-labelled their `result` to
   `INVALID-NONE-tested-zero-processes-died`, keeping `seconds`/`tested`
   verbatim; removed the blank line and two bare `done` lines so the file
   parses as CSV (checked: 6 rows × 6 fields, zero rows with `result ==
   NONE`). The original file is quoted verbatim, with the mechanism, in the
   new `search/hn_k5-README.md`.

5. **`SOURCES.md`** — added rows sourcing every new Section 3.4 statement
   (port docstring, abort row and zero-byte shards, quarantined rows,
   unfinished replication, `Axioms.lean` quote, candidate-count
   recomputation), corrected the "sourcing discipline" bullet that had
   claimed every $n\ge38$ value was backed by an independent verifier, and
   added an "Evidence reachability" section listing the tracked files and
   the two hashed PDFs.

Not changed: the values themselves ($h(38..41)=5,5,5,6$), every witness
claim, the $n=40$ exhaustive `--all` run (tracked, complete), and every
Lean statement. Nothing was weakened that the artifacts support.

# 2026-09-14 — t_6 update (Worker 12, `papers/REPORT-draft-update.md`)

Five changes to `papers/draft/pancyclic-exact-values.md`, with
`papers/draft/SOURCES.md` updated to match. Every witness cited was re-run
through `search/verify.py` in this revision; the output is
`papers/draft/verify-rerun-20260914.txt`. No file under `search/`,
`Erdos1016/` or any `REPORT-*.md` other than the new
`papers/REPORT-draft-update.md` was touched.

1. **Bracket $56\le t_6\le129$ replaced by $67\le t_6\le129$** in the
   abstract, Section 2.1, Section 5 and Section 6.3. Section 6.3 now tabulates
   a confirmed 6-chord witness at every $n$ from $57$ to $67$ with its chord
   set and provenance ($61$: `search/k6/sweep2-61-34.txt`; $62$–$67$:
   `search/k6/witnesses-v2.csv`; $57$–$60$: `search/k6/coord-57.txt`,
   `search/k6/smart-57-70.txt`), so $h(n)\le6$ is stated for all
   $41\le n\le67$. Section 2.1 also states which lower bounds $h(n)\ge6$ are
   established ($n=41$; $n\ge66$ by counting) and which would need
   monotonicity.

2. **Section 5 rewritten.** The Fibonacci form $2\,\mathrm{Fib}(k+3)-2$
   ($t_6=66$) and the rival $2^{k-2}(10-k)$ ($t_6=64$) are both reported as
   refuted by the $n=65,66,67$ witnesses, and the numerology is replaced by
   the result of `papers/NOTE-fit-underdetermination.md`: every three-term
   integer linear recurrence fitting $t_2..t_5$ has $(a,b,c)=(1+3t,1-5t,2-2t)$
   and predicts $t_6=66-2t$, so the known values determine $t_6$ not at all.
   The note's caveat is kept verbatim in substance: "every even value" is a
   property of that family, not a theorem that $t_6$ is even. The abstract's
   "falsifiable prediction" sentence is gone.

3. **New Section 3.5, "The shape/CSP exact algorithm."** Describes the
   subdivision-of-a-fixed-multigraph reformulation (cycle lengths as $0/1$
   linear forms in the arc lengths; $h(n)$ as a finite per-shape feasibility
   problem), the two independent solvers, the per-shape cap, the controls
   ($t_2=8$, $t_3=14$, $t_4=24$ with `gaveup_records=0`; $k=3$ shape count
   $14$ matching GMW13's "14 types of graph"; 201-graph ground-truth check
   with 0 mismatches), and the mutation-tested gate suite
   (`search/shapecsp/gates-red.txt` / `gates-green.txt`, re-run green here).
   The $k=5$ and $k=6$ ladder logs are reported as logged and flagged as not
   yet written up; Section 3.4's replication statement for $h(41)>5$ is
   deliberately left unchanged pending that lane's report.

4. **Family statement added** (Sections 5 and 6.3): the $n=64,65,66,67$
   witnesses are $(0,2)(0,n-7)(1,13)(3,n-6)(4,31)(n-8,n-5)$, pancyclic for
   exactly $n=64..67$ and missing exactly one length ($33$) at $n=68$
   (`papers/REPORT-k6-gpu-joint.md`; the $n=68$ member re-run here with
   `search/verify.py`: NOT pancyclic, missing `[33]`).

5. **Every other number the above invalidates reconciled.** Section 6.3's
   title, "largest confirmed witness $n=56$", "previously only up to 41", and
   the "stalls 3 lengths short at $n=66$" narrative are rewritten: the
   $\{5,7,8\}$ optimum is now described as a single-chord local optimum of
   one seed family, superseded by the $n=66$ witness found by a joint 3-of-6
   sweep around a different seed. The abstract's "two numerical
   observations" sentence, Section 5's "Update: partially tested, not
   settled" paragraph, and `SOURCES.md`'s Section 5/6 rows and its
   "sourcing discipline" bullet on the Fibonacci fit are replaced
   accordingly. Not changed: every $n\le41$ value, every Lean statement,
   Section 3.4, and the $M(k)$ table (which Section 3.5 now notes the shape
   census reproduces).

## 2026-09-15 -- shape/CSP result integrity (Worker 13)

6. **The `t_6 <= 93` justification corrected** (`REPORT-shape-csp.md` section 0,
   new section 0a). Section 0 claimed the bound was "established by the single
   level at n=94 on its own; levels 95..111 are redundant confirmations of it".
   That is withdrawn. Eligibility is decided *at the cutoff* by cap and Hall, and
   Hall at the cutoff is not monotone in $n$, so a clean `sat=0 gaveup=0` level at
   cutoff $n$ does not exclude larger $n$. Measured counterexample at $k=2$:
   `level.py 2 3` reports `eligible=0 sat=0 gaveup=0` while `level.py 2 8` returns
   three independently verified SAT shapes at $n=8$. **The bound is unchanged at
   $t_6 \le 93$**; what changes is that it rests on the contiguous block
   $n=94..111$ and every level in it is load-bearing. The coverage audit in
   section 7 already said this; section 0 contradicted it.

7. **Four result-integrity defects repaired and their gates mutation-checked.**
   From the independent review by Builder `c3a46073`: a non-zero-exit child
   accepted as `sat=0`; empty child output accepted as `sat=0`; a SAT accepted
   although `verify.check` rejects the materialised graph; and `satcheck.py`
   printing `SATCHECK FAILED` while exiting 0. `level.py` now requires a zero
   exit, exactly one terminal record per eligible shape, and `verify.check_record`
   acceptance for every SAT, failing closed with `LEVEL ... FAILED` and a non-zero
   status; `satcheck.py`'s exit status carries its verdict. The reviewer's six
   contract tests are in `search/shapecsp/test_review_contracts.py` and pass;
   `search/shapecsp/mutation-check.py` disables each gate in turn and records
   `4/4 gates went RED (failures=1) when disabled and GREEN when restored`.

8. **Three of those six contract tests were vacuous and were strengthened.** The
   repair made `level.py` exit through `sys.exit` on every path including the
   clean one, and the reviewer's harness counted *any* `SystemExit` as a
   rejection, so `assertTrue(rejected or ...)` became unconditionally true: the
   tests passed with the gates deleted. Only the harness changed -- the six
   assertions are byte-identical to the reviewer's -- and the strengthened suite
   reproduces exactly the reviewer's four failures against the pre-fix `HEAD`
   blobs while staying green on the repaired code.

9. **Not established here, and stated as such:** the `lastarc.patch` differential
   and the post-patch $k=2/3/4$ control were being run on the laptop by another
   agent and are not reported by this lane; the range-mode descent below $n=93$
   was not started; and the $n=68$ exact hunt was still running
   (`20/6059, gaveup=0, errors=0`) with **no witness at $n \ge 68$ found**.

# 2026-09-15 — doc-sealing pass (Worker 12, `papers/REPORT-draft-update.md`)

Four changes dispatched by Manager `f4d1e0af`, each re-verified against the
artifacts here before being written. Files touched: `papers/draft/pancyclic-exact-values.md`,
`papers/draft/SOURCES.md`, `papers/REPORT-shape-csp.md`, `.gitignore`,
`papers/CHANGES.md`.

1. **The $t_6$ upper bound is now $93$, and it is an exhaustive result rather
   than a counting one.** `67 \le t_6 \le 129` is replaced by
   `67 \le t_6 \le 93` in the draft's abstract, Section 2.1 and Section 5, and
   in the two `SOURCES.md` rows that stated the bracket. The upper end is
   sourced to the **contiguous** block of shape/CSP levels $94 \le n \le 111$,
   every one of them `sat=0 gaveup=0` (`search/shapecsp/level-k6-n94.txt` …
   `level-k6-n111.txt`, all 18 read here), with $111$ the largest per-shape cap
   at $k=6$ (`search/shapecsp/shape-census.txt`, row `6 | 21878 | ... | 109
   (distinct 109)`, cap $= F+2$). The block, not level 94 alone, is what
   carries it: eligibility is decided at each cutoff by cap-and-Hall necessary
   conditions and Hall is not monotone in $n$, so a shape feasible at $n_0$ is
   refuted only by the level whose cutoff is exactly $n_0$
   (`search/shapecsp/level.py` docstring, "Cite the block, never a single
   level"). $129 = 2^{k+1}+1$ is demoted throughout to the trivial prior bound.
   $n=92$ and $n=93$ are preserved as UNKNOWN holes — their level files are
   0 bytes — and are counted on neither side; the wording states the bound as
   what the completed levels support and names the running descent from $93$
   downwards as the thing that would lower it.

2. **$h(41)>5$ is now reported as independently replicated.** Evidence:
   `search/shapecsp/level-k5-n41.txt`, read here, is
   `LEVEL k=5 n=41 shapes=1236 eligible=308 sat=0 gaveup=0`. The draft's
   abstract, its Section 3.4 bullet list and its concluding paragraph, and the
   corresponding `SOURCES.md` bullet, are changed from "one complete
   enumeration plus a same-algorithm 128-bit port, no independent replication"
   to independent replication by a structurally different method, with the
   independence stated explicitly: chord-set enumeration on the GPU versus
   shape/arc-length CSP, no shared code, different search. Two qualifications
   are kept: the 128-bit run is still a port and still counts as one method,
   and `indep_gpu.py` is still unfinished and would be a third path. Section
   3.5 gains a paragraph explaining why a **single** level settles $h(41)>5$
   (Hall is necessary at that same $n$) while the $k=6$ upper bound needs the
   whole block — the two readings that the earlier revision of
   `REPORT-shape-csp.md` had confused.

3. **`papers/REPORT-shape-csp.md`: duplicate row removed, shape count
   corrected.** The witness-shape table listed `63` twice with identical
   contents (rows ordered 61, 63, 62, 63) under a heading that says nine; the
   first `63` row is removed, leaving nine rows in order. "All seven known
   witness shapes" is corrected to **six distinct shapes carrying nine
   witnesses** in the summary table, the solver-soundness row, the
   satcheck-grouping paragraph, the false-negative-control paragraph and the
   section 9 summary: the seven satcheck runs decided six shapes, because the
   n=66 and n=67 runs are the same shape. Counted mechanically from the
   corrected table: 9 rows, 6 distinct shape strings.

   **Sections 0 and 0a of that report are untouched.** They carry the
   block-justification correction — `t_6 \le 93` rests on the contiguous block
   $n=94..111$, not on level 94 alone, because Hall is evaluated at the cutoff
   and is not monotone in $n$ — and this lane preserved them: the hunks of
   commit `83508d5` in that file fall at the summary table, the witness table,
   the satcheck grouping, the false-negative-control paragraph and the section
   9 summary, and `git show 83508d5 --unified=0 -- papers/REPORT-shape-csp.md`
   lists no hunk inside either section. The section 9 correction below aligns
   that summary *with* section 0a rather than against it.

   **One unrequested correction in the same file, flagged rather than folded
   in.** Section 9 said the upper end rested on "17 contiguous exhaustive
   levels (n = 110 down to 94)" and that "the sweep takes it to 95" — both
   contradict section 0a of the same report and the `67 <= t_6 <= 93` stated
   two lines above them. Corrected to 18 levels, $n=111$ down to $94$, and to
   93, with the old text quoted in place so the correction is visible.

4. **Five SOURCES-cited evidence files are now tracked.**
   `search/k6/climb-60-72.txt` (402 bytes), `coord-57.txt` (199),
   `smart-57-70.txt` (488), `sweep2-61-34.txt` (300) and
   `verify-67-gpu-joint.txt` (323) were cited as primary evidence but excluded
   by `.gitignore`'s `search/k6/*.txt`, so they were unreachable from a clone.
   Added as `!` negations next to the existing ones. **Where the change
   landed:** the negations and the five files were staged by this lane and then
   committed in **`6dbe9ee`** ("Close the pickle cache handles; record the
   solver-binary swap under the running hunt"), the shape/CSP lane's commit,
   which picked them up from the shared index. They are tracked and correct;
   only the commit message's provenance sits in the other lane. Nothing was
   re-added or duplicated afterwards. **Audit re-run** (2026-09-15, after
   `6dbe9ee`): every file path named in `papers/draft/SOURCES.md` — 93 paths,
   extracted mechanically from its backticked spans and resolved one at a time
   against `git ls-files` — resolves, 91 of 93, with exactly two exceptions — `papers/Lai-Liu-2014-survey.pdf`
   and `papers/Wallis-2014-IWOCA-open-problems.pdf`, the third-party PDFs,
   which stay untracked by the redistribution decision and remain accounted for
   by size and SHA-256 in `SOURCES.md`. No other file was un-ignored.

**Not done, named rather than left to inference:** no code was touched
(`level.py`, `satcheck.py`, `bb.c` belong to Worker 13's lane and are
untouched here); the running descent below $n=93$ was neither started nor
consulted beyond the 0-byte level files; and no level was re-run — items 1
and 2 rest on reading artifacts already on disk, not on new computation.

# 2026-09-15 — h(n)=6 on 41..67 as the headline, plus four corrections (Worker 12, `papers/REPORT-draft-update.md`)

Dispatched by Manager `f4d1e0af` from Builder's review; every claim re-derived
here before it was written. Files touched:
`papers/draft/pancyclic-exact-values.md`, `papers/draft/SOURCES.md`,
`search/k6/witnesses.csv`, `papers/CHANGES.md`,
`papers/REPORT-draft-update.md`. New artifact:
`papers/draft/verify-family-41-68-20260915.txt`. No code touched.

1. **New headline: $h(n)=6$ exactly for every $41\le n\le67$, hence $m(n)=n+6$
   there, with no monotonicity assumption.** Stated in the abstract, Section
   2.1 and Section 6.3, and sourced in `SOURCES.md`. It replaces a position in
   which $h(n)\ge6$ was known by search only at $n=41$, by counting only for
   $n\ge66$, and for $42\le n\le65$ only through the monotonicity of $h$ —
   which is Wallis's open Question 1 and is now not needed.

   *Lower half*, $h(n)\ge6$ for all $n\ge41$: all 18 files
   `search/shapecsp/level-k5-n41.txt` … `level-k5-n58.txt` read here, every one
   `sat=0 gaveup=0`; the $k=5$ ceiling is $n\le58$ from
   `search/shapecsp/shape-census.txt` row `5 | 1236 | … | 56 (distinct 56)`
   (cap $=F+2$); a contiguous clean block running to the ceiling excludes every
   $n$ at or above its foot. The $n=40$ level, `sat=4`, is the positive control
   in the same series.

   *Upper half*, $h(n)\le6$ for all $41\le n\le67$: the single family
   $F_n=(0,2)(0,n-7)(1,13)(3,n-6)(4,31)(n-8,n-5)$, pancyclic at all 27 values
   $n=41..67$ and failing at $n=68$ by the one length $33$. All 28 checks
   re-run here with `search/verify.py`, each member first asserted to be six
   distinct in-range non-edge pairs:
   `papers/draft/verify-family-41-68-20260915.txt`.

   *Why 67*: the spectrum of $F_n$ is $[3,32]\cup[n-34,n]$ (symbolic cycle
   certificate `family-certificate.md` / `family-cycle-certificate.json`,
   Builder findings review 2026-09-15), which is $[3,n]$ iff $n-34\le33$ iff
   $n\le67$. Checked against computed length sets at
   $n=41,45,50,55,60,65,66,67,68,69,70$ — exact equality at all eleven, missing
   sets $[33]$, $[33,34]$, $[33,34,35]$ at $68,69,70$. **Cap declared:** the
   spectrum formula was machine-checked at 11 values of $n$, not all 27; the 27
   pancyclicity checks are complete.

   *Correction folded in:* the draft said the family "carries the
   $n=64,65,66,67$ witnesses" and is "pancyclic for exactly $n=64,\dots,67$."
   It carries the tabulated witnesses at 65, 66, 67 only — the tabulated $n=64$
   witness $(0,2)(0,61)(1,12)(3,60)(4,29)(56,61)$ is a different graph from
   $F_{64}=(0,2)(0,57)(1,13)(3,58)(4,31)(56,59)$ — and it does not start at 64.

2. **Section 5 sharpened: an odd witness does not refute the even-maxima
   family.** The claim that the $n=65$ and $n=67$ witnesses "refute *every*
   member … since all of them predict an even $t_6$" is a non-sequitur and is
   replaced. Recomputed over the draft's own parametrisation
   $(a,b,c)=(1+3t,1-5t,2-2t)$ with prediction $66-2t$: members are refuted from
   below iff $t\ge0$ (killing 66, 64, … and **both named fits**, which stands)
   and from above iff $t\le-14$, leaving **13 members, $-13\le t\le-1$,
   predicting 68, 70, …, 92**. The member $t=-1$ is $(a,b,c)=(-2,6,4)$ —
   verified: $-2\cdot14+6\cdot8+4=24$, $-2\cdot24+6\cdot14+4=40$ — predicting
   $t_6=68$, consistent with $67\le t_6\le93$ and refuted by nothing computed
   here. Only an odd $t_6$ would fell the family; $t_6$ is unknown. The
   existing parity caveat is kept.

3. **Sections 2.2 and 6.1: five presentations, four graphs.** Checked with
   `networkx.is_isomorphic` over all ten pairs of the tabulated
   representatives: exactly one pair is isomorphic, rows 4 and 5
   ($(0,4)(0,5)(1,34)(2,35)(3,15)$ and $(0,7)(1,8)(2,10)(2,11)(9,21)$); the
   other nine are not. The isomorphism does not preserve the Hamilton cycle —
   two of row 4's chords land on cycle edges of row 5's presentation — so the
   count is **ten labelled graphs, five dihedral classes, four isomorphism
   types**, each answering a different question. Both section titles now say
   "presentations." Consistency check recorded: the cycle count is an
   invariant, and rows 4 and 5 both show 48.

4. **Section 1: Jia's conjecture and the Erdős belief stated as incompatible.**
   The draft called Jia's Conjecture 1.16 ($g(n)=n+\log_2n+O(1)$) "in
   substance, Erdős Problem #1016 itself." It is one of two incompatible
   answers to it, and the one Erdős doubted: Jia asserts $h(n)-\log_2n$ is
   bounded, the Erdős belief recorded earlier in the same section is that it
   tends to infinity. The only claimed upper bound carries a growing $\log_* n$
   correction and sits on the Erdős side. The note now states the tension and
   says nothing here bears on which is right. Wallis's non-strict Question 1
   and Griffin's strict Conjecture 1 remain distinguished; that passage was
   already correct and was not touched.

5. **The obsolete $n=36$ row, and the same defect found live in the draft.**
   All 86 data rows of `search/k6/witnesses.csv` were validated; exactly one
   failed, and the other 85 are the positive control. Removed verbatim:

   ```
   36,"(0,2) (2,5) (5,10) (10,19) (19,36) (0,11)",GKW-shortcut base + scanned 6th chord (scan_join_range.py)
   ```

   Vertex 36 does not exist on $C_{36}$. The file now validates at 85 rows with
   zero out-of-range vertices.

   **Beyond the dispatch:** the same instantiation is the first data line of
   `search/k6/gkw-K4.txt` (`n=36: PANCYCLIC`), and the draft repeated it as
   "pancyclic at **exactly $n=36$ and $n=40$**." Both readings were recomputed:
   literally the chord adds a 37th vertex and the result does *not* cover
   $[3,36]$ (missing 5); modulo $n$ the six chords collapse to the **five**
   chords $C_{36}+(0,2)(2,5)(5,10)(10,19)(0,19)$, which is pancyclic and agrees
   with $h(36)=5$ in Griffin's Table 1 as reproduced in Section 2. Either way
   the row is not a six-chord statement, so the draft now claims $n=40$ only
   and records both readings. `gkw-K4.txt` itself was **not** edited: it is raw
   search output and evidence, so the correction belongs in the prose citing
   it. Nothing in $41\le n\le67$ depends on either instance.

**Repaired in the same pass:** the editing scripts wrote `\text` and `\to`
through non-raw Python strings, so `\t` became a literal TAB in three display
formulas and two inline ones. Found by grepping for tab characters, repaired
with an explicit `chr(9)` replacement; both edited documents now contain zero
tabs.

**Not done, named rather than left to inference:** no code was touched
(`search/shapecsp/` and the laptop are Worker 7's and Worker 13's); the
symbolic spectrum of $F_n$ for general $n$ is Builder's certificate, read but
not re-derived here; and the upper end of the $t_6$ bracket is unchanged at 93,
since the descent below 93 had not reported when this pass was written.

# 2026-09-19 - levels 68..70 exhausted on the GPU; h(n) <= 6 on 41..67 now Lean-checked (Manager (f4d1e0af))

1. **No 6-chord pancyclic `C_n` + chords exists at n = 68, 69, 70.** Every
   shape of the k = 6 census at each level, for every b from 6 to 12, is
   exhausted with zero hits: b <= 10 by the unrestricted GPU plan (15 claim
   files `papers/verification/n{N}-b{B}-unrestricted.json`, unit sets
   re-derived from the census manifest, rank totals equal), b = 11, 12 by the
   pairwise-admissible plan (`search/shapecsp/pairwise/SPEC.md`; 6 claim files
   `n{N}-b{B}-combined.json` from `verify_tier_combined.py --rebuild -1`, every
   one of the 3,388 pairwise shapes' tables rebuilt from its census row with
   matching hashes, counted compositions equal to the manifest totals).
   Report: `papers/REPORT-k6-gpu-pairwise-68-70.md`. Consequence: h(n) >= 7
   for n = 68, 69, 70, and with the CPU descent (`REPORT-k6-level89-91-verify.md`,
   levels 89..111 refuted) the bracket is now **t_6 = 67 or 71 <= t_6 <= 88**.
   The draft's abstract and Sections 2.1 and 5 still print `67 <= t_6 <= 93`;
   they are to be updated together once the descent 87..71 (running on both
   cards under `deploy/laptop/run-chain-laptop-v9.sh` and
   `search/shapecsp/run-chain-desktop-v12.cmd`) either finds the first witness
   above 70 or closes the gap, at which point t_6 is known exactly.
2. **The upper half of `h(n) = 6` on 41..67 is now kernel-checked in Lean.**
   `Erdos1016/Family.lean` proves `family_pancyclic_41_67 : forall n, 41 <= n -> n <= 67
   -> PancyclicWithChords n 6` (ASCII rendering of the Lean statement) from 27 certificates `Erdos1016/Family/W41.lean`
   .. `W67.lean` (the family `(0,2)(0,n-7)(1,13)(3,n-6)(4,31)(n-8,n-5)`, one
   explicit vertex list per cycle length, all facts re-derived by `decide`);
   `lake build` clean, `#print axioms` gives `[propext, Classical.choice,
   Quot.sound]` for every theorem in `Axioms.lean` (35 lines). Generator:
   `search/k6/gen_family_lean.py`. Before tonight only n = 41 (a different
   chord set) and n = 56 were Lean-checked among the k = 6 witnesses; the draft's
   sentence "each reconfirmed by three from-scratch verifiers and by a
   kernel-checked Lean 4 proof" is now true of the whole family, not only of
   the n <= 41 witnesses.
3. **Still computation, not Lean:** h(n) >= 6 for n >= 41, t_6 <= 88, and item 1.
   The independent review of the pairwise plan (`papers/REPORT-review-pairwise.md`,
   addenda 1-5: soundness of A proved and measured, tables and kernel exact,
   forged-tier attacks D1-D4 rejected by the frozen claim tool) and the
   level-67 blind positive control (running; b = 12 passed) are the evidence
   standard for those.

# 2026-09-20 - blind control passed at the decisive tier; draft updated to t_6 = 67 or 71 <= t_6 <= 88 (Manager (f4d1e0af))

1. **The blind positive control found the family witness.** The production
   pipeline, run over the whole of level 67 with no hint (every shape, every
   b; `search/shapecsp/run-chain-desktop-v12.cmd`, `:control`), found
   `(0,2)(0,60)(1,13)(3,61)(4,31)(59,62)` at b = 11, shape 20889, arcs
   1,1,1,1,9,18,28,1,1,1,5, at 00:19 PDT (hit recorded in
   `search/shapecsp/pairwise/control-state-n67-b11.json` with
   `search/verify.py pancyclic=True`; re-run by hand: pancyclic, and the same
   set minus one chord is not). b = 12 had passed earlier (1675 units, 0 hits,
   `papers/verification/control-n67-b12.json`). The b = 11 verdict file is
   written by `pairwise/check_control.py` when the tier completes and must
   show `family_witness_found: true` with zero hits failing the verifier.
   At 00:41 PDT the same tier produced two further hits at shape 21106,
   `(0,27)(18,30)(28,37)(29,37)(31,38)(32,39)` and its mirror image
   (isomorphic to each other, NOT isomorphic to F_67; vertex 37 carries two
   chords): a second 6-chord pancyclic graph on 67 vertices, not among the
   witnesses tabulated in the draft, independently verified pancyclic by
   `search/verify.py`. The control found a witness nobody had pointed it at.
2. **Draft brought to the settled facts** (`papers/draft/pancyclic-exact-values.md`,
   `papers/draft/SOURCES.md`): abstract and Section 2.1 now state
   t_6 = 67 or 71 <= t_6 <= 88; Section 3.3 records `family_pancyclic_41_67`;
   Section 3.5 records the descent levels 93, 92, 91, 90, 89 with their
   receipts (`REPORT-k6-level93-verify.md`, `REPORT-k6-level92-verify.md`,
   `REPORT-k6-level89-91-verify.md`, all at the repository root, and
   `papers/REPORT-k6-descent.md`), so the refuted block is 89..111; a new
   Section 3.6 describes the GPU exhaustion of levels 68..70 (pairwise plan,
   claim files, controls, review); Section 5's recurrence discussion now has
   nine surviving members {72, 74, ..., 88}, the t = -1 and t = -2 members
   (68, 70) having fallen to the level exhaustions; Section 6.3's "t_6 >= 68
   is open" is replaced. SOURCES.md rows updated and a Section 3.6 table
   added. The 0-byte `search/shapecsp/level-k6-n92.txt`/`n93.txt` are named
   as abandoned first attempts, not evidence.
3. **Descent bookkeeping.** Level 71 b = 12 claimed exact on the laptop
   (271 shapes, 2182 units, 1.087e13 compositions counted = manifest, zero
   hits; `papers/verification/n71-b12-combined.json`). The hourly sync
   (`search/shapecsp/rebalance/sync-from-laptop.ps1`) now pulls the laptop
   finalizer's claim files into `papers/verification/`, pulls every laptop
   state file as a backup copy and pushes the desktop's own states to
   `~/erdos-n70/backup-desktop-states/`. `papers/REPORT-k6-gpu-descent-71-88.md`
   is regenerated from the claim files by
   `search/shapecsp/pairwise/update_report_descent.py`; both report updaters
   now splice up to an end marker so hand-written sections after the tables
   survive (the old splice deleted the Lean section once; restored from git).
4. **Correction to item 2 of the 2026-09-19 entry:** the Lean statement was
   written with mis-encoded Unicode; it is now given in ASCII.

