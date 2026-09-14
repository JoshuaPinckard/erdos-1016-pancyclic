# Referee report: "Exact values of the minimum pancyclic edge count $m(n)$ for $3\le n\le41$"

Reviewed as an anonymous journal referee would: for correctness, novelty, and
overclaiming, against the literature this project itself already collected
(`papers/REPORT-lit-1.md`, `-2.md`, `-4.md`, `REPORT-oeis-and-jia.md`,
`REPORT-bondy-construction.md`, `REPORT-cyclecounts.md`,
`REPORT-cyclecount-asymptotics.md`). I checked every cross-reference against
the actual project files rather than trusting the manuscript's own summary of
them — several of the report's harshest findings come directly from that
cross-check.

## Recommendation: Major revision

The computational core (Section 2's table, its four independent
verifications, and Section 6's supporting data) is correct and well-evidenced
and should be published in some form — it genuinely extends the only prior
exact table (Griffin 2013) and this project's own four separate literature
sweeps found nothing that anticipates it. But the manuscript has a serious,
specific problem running through Sections 1, 4 and 5: **it states several
claims with more confidence than this project's own research supports**, in
one case (GKW 2016) citing a source as settled fact that a *later report in
the same project explicitly says could not be obtained*. None of these are
fatal to the core result, but all must be fixed before this is submittable.

## 1. Summary of claims

The manuscript claims: (a) exact $m(n)=n+h(n)$ for $38\le n\le41$
($h=5,5,5,6$), new relative to the located literature; (b) the extremal
5-chord structure at $n=40$ (five graphs, a common two-scale gap shape); (c) a
corrected subdivision lemma and three consequences bounding what a
counting-only lower-bound argument can achieve; (d) two numerical
observations on the threshold sequence $t_k$ (a strictly decreasing ratio to
$2^{k+1}$, and a Fibonacci closed form for $k=2..5$); (e) supporting
structural evidence (Section 6): near-miss data at the $n=24\to25$ boundary,
and a new $k=6$ upper bound $t_6\ge56$ with a stalled attempt at the
Fibonacci-predicted $n=66$.

## 2. Novelty, checked against the specific sources named

* **Vs. Griffin 2013 [Gr13]:** genuinely new. Griffin's Table 1 stops at
  $n=37$; his own paper's Corollary 1 plus his exhaustive $k\le4$ search
  already rule out $k=4$ for $n\ge25$ (see §3 below on how the manuscript
  states this more awkwardly than necessary), but nothing in Griffin gives
  $k=5$ values past $37$.
* **Vs. Jia 1996:** Jia's results (as recovered, second-hand, in
  `REPORT-oeis-and-jia.md`) are asymptotic upper-bound theorems with no exact
  table; no overlap, correctly noted in the manuscript's Section 1.
* **Vs. GKW 2016:** here the manuscript's novelty claim is fine (GKW's
  asymptotic construction doesn't supply exact $n=38..41$ values either), but
  see §5.1 below — the manuscript's *characterization* of what GKW proves is
  not itself independently verified, which is a citation problem, not a
  novelty problem.
* **Vs. Alon–Krivelevich:** correctly distinguished as a random-graph
  existence result, not a universal extremal one. Fine.
* **Vs. the Tao comment (18 Oct 2025):** this is the strongest novelty
  evidence in the paper, and it is used well — quoting the most current public
  status statement and noting it names nothing past Griffin/GMW's $n\le37$ is
  exactly the right check. No issue here.

**Overall verdict on novelty: solid.** This is the one claim in the paper I
would not ask to be softened.

## 3. Correctness review, theorem by theorem

### 3.1 The corrected subdivision lemma (Section 4)

Mathematically correct as now stated (I re-derived it independently rather
than trusting the correction note: $A\cup(B+m)$ is exactly the reconstructed
cycle spectrum of $G$ under contract-then-subdivide, so it holds for *any*
arc trivially). **But this raises a presentation problem the manuscript does
not address: the corrected lemma is very close to a tautology.** It is true
essentially by definition of what subdivision does to cycle lengths, and nothing
in Consequences 1–3 actually depends on the specific $A\cup(B+m)$ formulation
— Consequence 1 is a direct fact about Shi pairs and a fixed edge, and
Consequence 3 is a direct fact about the stretch multigraph, neither of which
needs the "lemma" as a hypothesis. As written, the section reads as though
the lemma is the load-bearing result and the consequences follow from it;
in fact the consequences could be (and should be) stated as standalone facts
about Shi's dichotomy, and the lemma reduced to a one-line remark that
contraction/subdivision doesn't change which cycles exist. **Required
change:** either demonstrate a place where the corrected lemma's specific
form is actually used (not just "consistent with"), or demote it to a remark
and lead with Consequences 1–3 directly.

### 3.2 Consequence 1 (counting balance)

The stated bounds ($|A|\le2^k-1$, $|B|\le2^k$) are correct, but **the
manuscript does not derive the asymmetry** — why avoiding gets $2^k-1$ and
using gets $2^k$ is asserted, not shown. I can reconstruct why (the
$K=\varnothing$ case can only contribute the full Hamilton cycle, which
always uses $uv$, so it structurally cannot land in $A$), and
`papers/REVIEW-notes01.md` records exactly this reconstruction — but that
reconstruction is not in the manuscript itself. **Required change:** either
include the one-paragraph derivation or cite `REVIEW-notes01.md` explicitly
at this point; as written a careful reader cannot verify the claim from the
manuscript alone.

### 3.3 Consequence 2 (largest-arc bound) and Consequence 3 (wall inequality)

Both correct as stated, and both cite the counterexample/re-verification
trail honestly. No issues. This is the strongest section of the paper
mathematically.

### 3.4 The $M(4)=29$ / $k=4$ elimination argument (Section 3.4)

**This is imprecisely stated and unnecessarily weak.** The manuscript says
$h(n)\ge5$ for $n=38..41$ follows from "Griffin's Corollary 1... so $k=4$
permits at most $31$ cycles; combined with Griffin's exhaustive computer
search of $k\le4$ chords (which the paper states was run without restriction
to small $n$)." This both overstates what Griffin's paper actually says (an
"exhaustive search... without restriction to small $n$" reads as claiming an
unbounded search, which is not literally possible and is not how Griffin's
own text frames it — his search is explicitly bounded, and the *general* $n$
case is closed by counting, not search) and is **more complicated than
necessary for the specific claim being made**: for $n=38,\dots,41$
specifically, $n-2\ge36>31=2^{4+1}-1$, so *pure counting alone*, with no
reference to any exhaustive search at all, already rules out $k=4$. The
manuscript should say this directly — it is both simpler and more airtight
than what is currently written, and doesn't require the reader to trust a
loosely-worded characterization of Griffin's search scope. **Required
change: rewrite this paragraph using the direct counting argument only.**

## 4. Overclaims (as specifically requested)

### 4.1 The Fibonacci fit — the single worst overclaim in the paper

Section 5 presents $t_k=2\,\mathrm{Fib}(k+3)-2$ as matching "for
$k=2,\dots,5$" and calls it "an observation, not a theorem," which is
honest as far as it goes. **But it omits the one caveat that most changes how
surprising this should look to a reader, and that caveat is already on
record in this project's own files:** `papers/REPORT-bondy-construction.md`
(§"An unsourced numerical observation"), which is where this fit actually
originates, explicitly calls it "four data points fitting a **two-parameter
family**" (the closed form has a free multiplicative constant, $2$, and a
free additive constant, $-2$). **A two-parameter family fit to two of its
four cited data points proves nothing — those two matches are guaranteed by
construction.** The only genuine information content is that the *same*
two parameters, fixed by (say) $k=2,3$, also happen to reproduce $k=4,5$
exactly — two real coincidences, not four. The manuscript's phrasing
("matches ... for $k=2,\dots,5$") reads as four independent confirmations to
anyone who hasn't separately worked out the degrees of freedom, which is an
overclaim by omission, not by false statement. **Required change:** state
the degrees-of-freedom explicitly (e.g. "a 2-parameter fit exact at $k=2,3$
by construction, additionally exact at $k=4,5$") and cite
`REPORT-bondy-construction.md` as the origin of the observation — currently
the manuscript's Section 5 does not cite it at all, and a reader would think
this project derived the fit fresh.

Separately, `REPORT-bondy-construction.md` also records an *additive*
Fibonacci-style recursion, $t_k=t_{k-1}+t_{k-2}+2$, and explicitly notes it
**fails at $k=3$** (predicts $15$, actual $14$) even though the closed form
holds there — i.e. the project's own file already found one framing of "the"
Fibonacci pattern that breaks inside the very range the manuscript calls
clean. The manuscript should at least footnote that a naturally-related
recursion form does not hold at $k=3$, since it bears directly on how much
structure to read into the fit.

### 4.2 The ratio table

The $t_k/2^{k+1}$ ratio table (Section 5) is presented as "strictly
decreasing" — true for the five computed points, correctly caveated as
"the only range where $t_k$ is known exactly." This is fine; I would not ask
for a change here beyond noting (as the manuscript itself now does in
Section 5's "Update" paragraph) that Section 6.3's new $k=6$ data does *not*
extend this ratio table with a confirmed sixth point, only a bracket. No
overclaim found in the ratio table itself.

### 4.3 "Counting cannot suffice" (Section 4's title and Consequence 1's boxed claim)

**This is an overclaim, and worse, it is in tension with material the same
section cites two paragraphs later.** Consequence 1 states in bold: "Any
improvement must come from arithmetic..., never from counting alone." But
Section 4's own "Cycle-count context" subsection, immediately following,
credits Rautenbach–Stella with *exactly* a counting-based improvement (a
sharper cycle-count ceiling that does move the bound, per
`papers/REPORT-cyclecounts.md`'s own $N_{RS}>N_0$ comparison for $k\ge4$).
So the manuscript first asserts counting *never* helps, then cites a paper
that used counting to help. The intended meaning is presumably "the specific
trivial $2^{k+1}-1$ ceiling, applied through this particular
subdivision-lemma decomposition, is exactly self-consistent and gives back
nothing new" — a much narrower and defensible claim. **Required change:**
soften the section title (e.g. "why naive counting is self-consistent but
not obviously improvable") and rewrite the bolded sentence in Consequence 1
to scope it explicitly to the trivial ceiling, not to "counting" as a method
in general, given the paper's own citation of a counting-based improvement in
the very next subsection.

## 5. Citation problems

### 5.1 George–Khodkar–Wallis (2016) — the most serious citation issue

The manuscript's Introduction states flatly that GKW16 "give the first
located published proof of Bondy's claimed upper bound." **This project's
own `REPORT-bondy-construction.md` — a later, more careful investigation
specifically tasked with pinning down this exact claim — states GKW's
Chapter 4 was "Not obtained," checked two independent ways (a Google Books
preview exposing no chapter content, and web search returning only paywall
pages), matching an even earlier failed attempt on record in
`construction/REPORT-construction.md`.** Every fact this manuscript
attributes to GKW16 (the Ch. 4.5 proof, and the specific 5-shortcut
construction used in Section 6.3) is therefore sourced *second-hand*, via
Alon–Krivelevich's own paraphrase ("we emulate **an approximation of** the
construction in [GKW]," AK's own words) and via Terence Tao's forum comment,
which itself hedges: "The first literature proof ... **that seems to
exist** is in Chapter 4.5" (quoted in full in `REPORT-lit-4.md`) — note "seems
to exist," which the manuscript's Introduction drops entirely, upgrading a
hedge to a flat assertion. There is also an unreconciled internal
inconsistency: `REPORT-lit-1.md` (an earlier, less careful pass) claims "the
public abstract confirms" GKW's content, which is hard to square with
`REPORT-bondy-construction.md`'s explicit "Not obtained" finding — the
manuscript silently follows the earlier, weaker-sourced report and never
mentions the later one found nothing. **Required changes:** (i) hedge every
GKW16 attribution to match Tao's own "seems to exist," not stronger; (ii)
explicitly note, wherever GKW's construction is used (Section 6.3
particularly), that it is reconstructed from Alon–Krivelevich's approximate
paraphrase, not the primary text; (iii) cite `REPORT-bondy-construction.md`
and flag the unresolved discrepancy with `REPORT-lit-1.md` rather than
silently picking the more convenient of the two.

### 5.2 Shi (1994) and Rautenbach–Stella (2005) — a milder version of the same problem

Per this project's own search logs (`REPORT-lit-1.md`'s audit section), these
were also never obtained as full text — only publisher abstracts and
Griffin's own paper quoting their theorem statements were available. This is
a weaker problem than GKW16 (the actual theorem statements, not just a
paraphrase, were seen), but the manuscript cites them with the same
unqualified confidence as if the papers had been read directly. **Suggested
change:** a single footnote noting that Shi94/RS05/GKW16 are all cited via
secondary access (abstracts, quotations in Griffin, or paraphrase), while
[Gr13] and [AK25] were read in full, would let a reader calibrate confidence
correctly without cluttering the text.

### 5.3 Missing citation: George, Marr and Wallis (2013)

The manuscript's own body text cites "George–Marr–Wallis 2013" **twice** by
name (Section 5, discussing Wallis's Question 1's context and the Sridharan
correction) but this source **never appears in the References list**. This
is a straightforward missing-citation bug, not a judgment call. **Required
change:** add a [GMW13] entry (J. C. George, A. Marr, W. D. Wallis, "Minimal
pancyclic graphs," J. Combin. Math. Combin. Comput. 86 (2013), 125–133, per
`REPORT-lit-1.md`) and replace the inline "[George–Marr–Wallis 2013]" text
with the bracket-key style used everywhere else in the References.

### 5.4 Missing citation: Markström (2009)

Not required (the paper's topic is minimum edges, not uniquely pancyclic
graphs), but Section 4's cycle-count discussion sits close enough to
Markström's UPC edge-count work (already in this project's files,
`papers/REPORT-cyclecounts.md`) that a reader following up on "exact cycle
counts" would expect to see it. **Suggested, not required.**

## 6. Other required changes

1. **Abstract is stale relative to Section 5/6.** The abstract still reads
   "predicting $t_6=66$" with no mention that Section 5 (per the manager's
   own most recent instruction to this draft) now reports the bracket
   $56\le t_6\le129$ and a stalled attempt at $66$ itself. A reader stopping
   at the abstract gets a materially more confident impression than the body
   supports. **Fix the abstract to mention the bracket, not just the
   original point-prediction.**
2. **Section 6.3's "GKW recipe" language should be qualified** per §5.1
   above, in the same sentence it first appears, not just in a
   citation footnote.
3. **The Fibonacci discussion (Section 5) needs the two-parameter caveat and
   the citation to `REPORT-bondy-construction.md`** per §4.1.
4. **Section 3.4's counting argument should be simplified to the direct,
   airtight version** per §3.4, dropping the imprecise characterization of
   Griffin's search scope.
5. **Add the missing [GMW13] reference** per §5.3.
6. **Consequence 1's derivation gap should be closed or cross-referenced**
   per §3.2.
7. **Section 4's title and Consequence 1's bolded claim should be scoped to
   the trivial ceiling specifically**, not "counting" in general, per §4.3.

## 7. Suggested (non-required) changes

* Note in Section 3.3 that "exhaustive" in the abstract's summary sentence
  describes what the programs are *capable of*, not that every run reported
  was carried to full exhaustion (several witnesses were found by
  stop-at-first-hit searches, which is methodologically fine but not what
  "exhaustive" suggests on a first read of the abstract).
* Add the secondary-sourcing footnote suggested in §5.2.
* Consider whether the paper's overall contribution — a four-value table
  extension, a set of correct-but-non-load-bearing structural lemmas, and
  two numerical observations of debatable strength — is better framed as a
  technical note or an OEIS/erdosproblems.com update than as a standalone
  research paper. Nothing here makes theoretical progress on either of
  Wallis's two open questions (monotonicity, a better general upper bound);
  the paper says so honestly in Section 5, which I credit, but the framing
  in the abstract and introduction reads more ambitiously than the content
  underneath it.

## 8. What I checked and did not find fault with

For completeness: Section 2's exact-value table, Section 3's method
description (triangle case split, cycle-space enumeration, the four
independent verifiers including the newly re-verified Lean proofs), and
Section 6's near-miss and $k=6$ data are all consistent with the underlying
project files I cross-checked them against, and I found no numerical errors
in any of them. The problems in this report are about overclaiming,
citation precision and internal consistency, not about the correctness of
the computed values themselves.
