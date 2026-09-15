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
