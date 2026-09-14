# Griffin's exhaustive-for-fixed-k method: what actually makes it finite, and how it compares to a suppress-degree-2 / fixed-multigraph reduction

Date: 2026-09-14. Assignment (Manager, this session): Griffin's "exhaustive search
for Hamiltonian graphs with at most 4 chords," with no stated vertex cap, cannot
literally be an enumeration over all `n` (that search space is infinite). Work
through Propositions 3-4 and Corollaries 2-3 (the "arc-contraction argument") to find
Griffin's finite reduction: what object it reduces to, what makes it finite, how many
cases it produces at `k=4`, and whether it is specific to `k<=4` or would extend to
larger `k`. Compare against another lane's own finite reduction for `k=6`
(suppress degree-2 vertices -> fixed multigraph, arc lengths as integer variables),
stating plainly whether they are the same idea.

This report is based on a complete read of `papers/1312.0274.txt` (Griffin's full
paper, all 264 lines / 5 pages of body text, now read in its entirety across this and
the prior novelty-check task — abstract, both theorem sections, Table 1, both
propositions on monotonicity, acknowledgements, and references) and the full text of
`papers/GMW13-George-Marr-Wallis-2013.pdf` (obtained in the prior task).

## Costliest finding: Propositions 3-4 / Corollaries 2-3 are not the reduction that makes the exhaustive search finite — that's a different, simpler mechanism, already in this project's own notation

**Manager's premise needs correcting before the requested write-up can proceed.** The
arc-contraction machinery (Definition 1 "crossing chords," Proposition 3, Definition 2
"arc contraction," Theorem 4, Corollaries 2-3, Proposition 4) is a real finite
reduction, but it solves a different problem: it is Griffin's **partial-progress
argument toward Conjecture 1** (`m(n) < m(n+1)`, strict monotonicity), used to relate
a minimal pancyclic graph on `n` vertices to a smaller pancyclic graph on `n-1` (or
`n/2+2`) vertices by contracting one edge of a sufficiently long arc. It appears in
`1312.0274.txt` *after* Table 1 and the exhaustive-search paragraph, in a section
explicitly introduced as addressing "the behavior of `m(n)` in general" and Conjecture
1 — nothing in its statement, proof, or the surrounding text connects it to bounding
the search space of the `k<=4` exhaustive search. Checked directly: neither
Proposition 3 nor Theorem 4/Corollaries 2-3 nor Proposition 4 is cited anywhere near
the exhaustive-search paragraph (`1312.0274.txt` lines 41-45), and the exhaustive-search
paragraph does not cite them either.

**What actually makes "exhaustive for `k<=4`, no vertex cap" a finite (and therefore
literally exhaustive) claim is Corollary 1 — the same elementary cycle-counting bound
already used three other places in this paper and already used in this project's own
notation.** Corollary 1 states: a Hamiltonian graph with `k` chords has at most
`2^{k+1}-1` cycles. A pancyclic graph on `n` vertices needs at least `n-2` distinct
cycle lengths, hence at least `n-2` cycles. Combining: `2^{k+1}-1 >= n-2`, i.e.
`n <= 2^{k+1}+1`. **This is an absolute, `n`-independent ceiling for any fixed `k`,**
and Griffin uses exactly this inequality twice elsewhere in the same paper for
exactly this purpose — once to derive the general lower bound (`1312.0274.txt`,
Claim 1's proof: `2^{k+1}-1 >= n-2` gives `m(n) >= n+log_2(n-1)-1`), and implicitly a
second time in the exhaustive-search paragraph itself, which invokes "by Corollary 1,
there are at most 31 cycles... and there must be at least `n-2` cycles" immediately
before concluding no `k=4` pancyclic graph exists for `n>=25`. For `k=4`:
`n <= 2^5+1 = 33`. **This `33` is the same quantity this project already tracks as
`N_0=2^{k+1}+1` in `papers/REPORT-cyclecounts.md`'s own notation** (that report's
`N_0` column gives `5,9,17,33,65` for `k=1..5` — the `k=4` entry, `33`, is exactly
this number). So "exhaustive for `k<=4`, no vertex cap" is finite for a mundane
reason that has nothing to do with arc contraction: **beyond `n=33`, no search is
needed at all**, because pure counting already rules out every `n>=34` for `k=4`;
the search Richard Lange's program ran only ever had to cover `n=3` up to `33` (and,
per the paper's own words, apparently did not even need the full range — the
practical negative result it reports, "no graphs on 25 or more vertices with 4 chords
can be pancyclic," was established somewhere inside that already-finite window, not
by extending the search to infinity).

**Consequence for reading the abstract-vs-body discrepancy already reported in
`REPORT-novelty-check.md` (Follow-up 3):** the reason the `k<=4` case needed *no*
explicit vertex cap in Griffin's body text, while the `k=5` case needed an explicit
"31 vertices," is now explained rather than just observed. For `k=5`,
`2^{k+1}+1 = 65` — far beyond what a search can plausibly cover exhaustively with
2013-era tooling, so Griffin's actual `k=5` search was capped well short of the
theoretical `65` ceiling, at a **practical** limit of `31` vertices, and the
remaining range (`n=32..37`) was closed with a specific construction instead (already
established in the prior report). For `k=4`, the theoretical ceiling (`33`) was
apparently itself within reach of the search, so no separate practical cap needed
stating — the paper's "no vertex cap given" for `k<=4` reflects "the counting bound's
own ceiling was small enough to just search the whole thing," not a cleverer
reduction.

## What Griffin's paper does *not* say: the actual search algorithm is not described

Manager's specific questions — "what object he reduces to," "how many cases it
produces at `k=4`" — do not have answers in this source. Griffin's paper credits the
search programs entirely to a collaborator, in the Acknowledgements only: *"I would
also like to thank... Richard Lange who provided me with valuable programs which were
an essential part of the calculation of `m(n)`."* There is no pseudocode, no
description of what is enumerated (graphs directly? chord-interaction patterns with
free gap variables? something else?), and no case count given anywhere for `k=4`
specifically (Table 1 reports only the resulting `m(n)` values, not the search's
internal structure). **This is a genuine gap in the primary source, reported here as
unknown-from-this-text rather than inferred or guessed.** The one adjacent
methodological fact the paper does supply — Proposition 1's proof, which reasons
about "the number of potential cycles eliminated" when a vertex has high degree,
combinatorially via Shi's per-vertex cycle-elimination counts — is a counting
argument about upper-bounding cycle totals, not a description of how graphs/patterns
were enumerated, and does not resolve the question either.

## The one place Griffin's paper *does* show its method concretely: it's the same reduction GMW13 uses by hand, and it matches the k=6 lane's description

Although Griffin's own text is silent on Lange's algorithm, this project now has (per
the prior task) the complete body of **GMW13**, and GMW13 explicitly works exactly the
kind of reduction Manager describes for the `k=6` lane, worked by hand for `k=1,2,3`,
with every step shown:

- For **`k<=2` chords**, GMW13 represents the graph as "a circle with the chords as
  straight lines," with "segments of the outer circle" (i.e. arcs between consecutive
  chord endpoints, exactly "degree-2 vertices suppressed") — the chords' crossing
  pattern is fixed (types A/B/C: non-crossing-no-shared-endpoint, shared-endpoint,
  crossing), and the arc lengths (`a,b,c,d` in GMW13's own notation for the `v=9`
  case) are treated as **free non-negative integer variables** constrained only by
  `a+b+c+d=v` (or the analogous sum for whatever chord count), with cycle lengths
  given as linear functions of the arc-length variables (e.g. GMW13, `v=9` case,
  quoted verbatim: *"The lengths of the seven cycles are 9 (containing neither
  chord), `a+b+1, c+d+1` (horizontal chord), `a+d+1, b+c+1` (vertical chord),
  `a+c+2, b+d+2` (both chords)"*). This is precisely "suppress degree-2 vertices,
  giving a fixed multigraph whose arc lengths are integer variables" — the fixed
  multigraph here is the finite set of `{chord endpoints + their crossing pattern}`,
  and the arc lengths between consecutive endpoints are exactly the integer
  variables.
- For **`k=3` chords**, GMW13 makes the reduction fully explicit and exhaustive:
  *"If a graph has three chords, we classify by looking at the three pairs of
  chords... There are 14 types of graph: AAAi, AAAii, AABi, AABii, AAC, ABBi, ABBii,
  ABC, ACC, BBBi, BBBii, BBC, BCC, CCC"* — **14 is the exact case count at `k=3`**,
  a genuine finite enumeration of chord-interaction patterns (a "fixed multigraph" in
  Manager's phrasing, one per type), each analyzed separately with its own
  cycle-count table (`C(0)..C(3)`, GMW13's Figure 3 / cycle-count table) and its own
  arc-length variables. This is the clearest, most concrete instance of the general
  method in either paper, and it is a genuinely published, worked example — GMW13's
  Figure 3 table is reproduced in the prior report's full-text extraction
  (`REPORT-novelty-check.md`'s costliest-finding section quotes the whole paper).
- **For `k=4` chords, GMW13 itself does *not* do this exhaustively.** Its own words:
  *"There are a large number of possible configurations for four cycles. We have
  examined several of them."* Figure 4 gives **one** specific parametrized
  construction (`x+12` vertices, a fixed chord pattern with one free length variable
  `x`, `1<=x<=10`, reaching `v=15..22`) — this establishes an **upper bound** for
  `15<=v<=22`, not an exhaustive lower-bound elimination of all other `k=4` patterns.
  GMW13 gives no case count for `k=4` and does not claim its `k=4` treatment is
  exhaustive.

**This means Griffin's computer search is a genuine step up in rigor over GMW13
specifically at `k=4`**: where GMW13 explicitly stops at "examined several" patterns
for 4 chords, Griffin's Lange-authored program claims full exhaustiveness at `k=4`
(the "no graphs on 25 or more vertices with 4 chords can be pancyclic" result, which
requires ruling out *every* 4-chord configuration, not just the ones GMW13 happened
to try). Whether Lange's program implements the same chord-pattern/integer-gap-variable
reduction GMW13 used by hand for `k<=3`, done automatically by computer for `k=4`
(the natural way to make an exhaustive-over-all-`n` search tractable at all — you
cannot enumerate graphs one `n` at a time up to `n=33`; you enumerate the finitely
many chord-interaction patterns on `2k=8` labeled cyclic positions instead, then
solve for which non-negative-integer arc-length assignments realize all needed cycle
lengths), is **very likely but not confirmed** — Griffin's text simply does not say.
The circumstantial case for "very likely" is strong: (a) it is the obvious and
essentially forced way to make a `k`-fixed, `n`-unbounded search finite and automatable
at all, since chord-interaction patterns are independent of `n` while arc lengths
scale with `n`; (b) it is exactly the precedent GMW13 (which Griffin cites, extends,
and whose k<=3/k=4 results Griffin's own Table 1 explicitly agrees with — "All of
these values agree with [2]") already established in print for smaller `k`; and (c)
this project's own search programs (`search/pancyc.c`, `search/gpu_pancyc.py`, per
the draft's Section 3.1-3.2) use essentially the same idea in a different guise — a
fixed cycle-space basis (Hamilton cycle plus chords) with cycles read off as XOR
combinations, which is the same "fix the combinatorial pattern, vary the lengths"
strategy at one remove.

## Direct answer to the four questions asked

1. **What object does Griffin's finite reduction reduce to, for the part that
   actually matters (why `k<=4` needs no stated vertex cap)?** Not a graph-structure
   reduction at all — a pure counting inequality, Corollary 1 (`2^{k+1}-1>=n-2`),
   already stated and used elsewhere in the same paper and already in this project's
   own `N_0=2^{k+1}+1` notation (`papers/REPORT-cyclecounts.md`).
2. **What makes it finite?** For `k=4`: `n<=2^5+1=33`, an absolute ceiling from pure
   cycle counting, independent of any graph-structural argument. (Propositions 3-4 /
   Corollaries 2-3, the arc-contraction machinery Manager asked to be worked through,
   do **not** contribute to this — they solve a separate problem, monotonicity of
   `m(n)` across consecutive `n`, not bounding a fixed-`k` search range. They are
   real and correctly summarized above for completeness, but they are not the
   mechanism in question.)
3. **How many cases at `k=4`?** **Not stated anywhere in Griffin's paper** — genuinely
   unknown from this source, not inferred. GMW13, the closest available precedent,
   gives an exact case count only at `k=3` (**14 types**, enumerated by name) and
   explicitly does *not* claim an exhaustive case count at `k=4` ("examined several
   of them"). If a `k=4` case count exists anywhere, it would have to come from
   Lange's unpublished program, which is outside anything this project can access.
4. **Is anything in it specific to `k<=4`, or would it extend to larger `k`?** The
   part that *is* explained (Corollary 1's counting ceiling) is completely general in
   `k` — it gives `n<=2^{k+1}+1` for any `k`, already tabulated in this project's own
   `N_0` column for `k=1..5` (`5,9,17,33,65`) and trivially extensible to `k=6`
   (`N_0=129`, already the ceiling the draft's own Section 5 cites for the `t_6`
   bracket, `56<=t_6<=129`). What is *not* explained (the actual per-`n`, per-`k`
   enumeration algorithm) is, by its nature as an unpublished, uncredited-in-detail
   program, of genuinely unknown generality — but the strong structural inference
   above (chord-interaction-pattern + integer-arc-length-variable reduction) is a
   method that is manifestly general in `k`: the number of chord-interaction patterns
   on `2k` cyclic positions grows combinatorially with `k` (from GMW13's own
   progression: 1 type at `k<=1`, 3 types at `k=2` — A/B/C — 14 types at `k=3`; a
   rough count for `k=4` would be dramatically larger, consistent with GMW13's own
   "large number of possible configurations" remark), but nothing about the
   *reduction itself* — fix the pattern, treat arc lengths as free integers subject
   to a sum-to-`n` constraint and a target set of realizable lengths — is capped at
   `k=4`. It is the same shape of reduction for any `k`.

## Direct comparison to the other lane's `k=6` reduction

**Plainly stated, per Manager's request: this is very likely the same idea under a
different name, with GMW13 — not Griffin's paper — as the actual published precedent
carrying a worked example.** "Suppress degree-2 vertices, giving a fixed multigraph
whose arc lengths are integer variables" describes exactly GMW13's `k<=3` method
(chord endpoints are the multigraph's non-degree-2 vertices; the "fixed multigraph"
is one of GMW13's 14 named types at `k=3`; the arc lengths between consecutive
endpoints are the integer variables) at one level of abstraction, and this project's
own cycle-space/XOR search machinery (`search/pancyc.c`'s Gray-code walk over
`2^{k+1}` XOR combinations of a fixed chord-plus-Hamilton-cycle basis, per the draft's
Section 3.2) at another. Two things follow for the other lane, stated as
recommendations rather than conclusions this report can settle on its own:

- **If validating against a `k<=4` precedent**, GMW13's 14-type enumeration at `k=3`
  (not Griffin's `k=4` result, whose case structure is unpublished) is the actual
  checkable, citable published precedent with a full worked case table — this report
  has the complete case table available (`papers/GMW13-George-Marr-Wallis-2013.pdf`,
  Figure 3 and its `C(0)-C(3)` counts, quoted in full in `REPORT-novelty-check.md`).
  Griffin's `k=4` exhaustive result is real and rigorously established (per the
  counting-bound argument above, it genuinely is exhaustive, not just constructive),
  but its internal case structure cannot be checked against because it was never
  published.
- **If looking for a pruning trick to transplant**, GMW13's method does not appear to
  contain one beyond the basic pattern-then-variables reduction itself — its
  worked cases are small enough (`k<=3`) that no further pruning was needed, and
  Griffin's paper, as established above, documents no pruning strategy at all (the
  work is credited to an unpublished program). If the other lane's `k=6` reduction
  already includes an explicit pruning rule (e.g. this project's own
  `search/pancyc.c`, which does have a documented one — the partial-cycle-count bound
  described in the draft's Section 3.2, "if (distinct lengths so far) +
  `2^{k+1}-2^{j+1} < n-2` the partial chord set is abandoned" — that pruning rule has
  no counterpart in either Griffin's or GMW13's text and would not be "transplanted
  from" either source; if anything it is this project's own contribution, already in
  hand, not something to go looking for externally.

## Caps and scope

This report reflects a complete read of Griffin's paper (all 264 lines / 5 pages,
across this and the prior task) and GMW13's full text (obtained in the prior task);
no further primary source was fetched this round. The claim that Griffin's search
"very likely" uses the same pattern-plus-integer-variable reduction as GMW13 is
explicitly flagged as inference from structural/historical evidence, not a confirmed
reading of Lange's program, which this project has no access to and no route to
obtain (unpublished, uncredited beyond a name in the acknowledgements). GKW16 Chapter
4's own treatment of `k=4` (pp. 38-41, per the TOC obtained in the prior task) was
not re-examined here — it remains unread body text, tracked separately in
`REPORT-novelty-check.md`.
