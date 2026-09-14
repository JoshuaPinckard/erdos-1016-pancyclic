# Literature sweep 3: mathematical techniques for Erdős #1016 (Worker 5)

Date: 2026-09-14. Scope per assignment: (1) theorems bounding how many distinct values a
*structured* family of subset sums can take; (2) any place a `log*(n)` (or iterated-log) term
arises in a covering/recursive construction **with a matching lower bound**, for the technique,
not the result; (3) any recorded attempt at #1016 since 2023. Builds on `REPORT-lit-1.md` and
`REPORT-lit-2.md` (2026-09-14, same day, prior sweeps), which found no paper improving the
counting lower bound `h(n) >= log_2(n-1) - 1` beyond Rautenbach–Stella's finite-`r` refinement.
This report does not repeat findings already logged there except where needed for contrast.

Gap-language reminder used throughout: 2k chord endpoints cut C_n into gaps g_1..g_2k summing to
n; for a subset K of the k chords, the realized cycle length is `|K| + (sum of the gaps lying in
one alternating class determined by K)`. The counting bound `h(n) >= log_2(n-1) - 1` is just
"2^k subsets can't produce n-2 distinct lengths for k too small." We want a technique that shows
the sums also collide/fail to cover **even before** the counting bound is exhausted, by an
additive amount of order `log*(n)`.

## Costliest finding first: Linial's `Theta(log* n)` lower bound is the only located place a
`log*` term is *proved* as a matching lower bound via a recursive combinatorial construction —
but the construction's engine (an adversarial multi-instance compression argument) has no
obvious analogue for a single fixed integer sequence of gaps, and that mismatch is the concrete
obstacle any transfer attempt must resolve first.

**Citation.** N. Linial, "Locality in distributed graph algorithms," *SIAM J. Comput.* 21(1)
(1992), 193–201. Clean modern re-proof: J. Laurinharju and J. Suomela, "Linial's Lower Bound Made
Easy," arXiv:1402.2552 (2014) — downloaded to this folder as
`Linial-Lower-Bound-Made-Easy-1402.2552.pdf`.

**Exact statement (Laurinharju–Suomela's formulation, which is what I verified against the PDF).**
Any deterministic distributed algorithm that properly 3-colors a directed `n`-cycle from unique
node identifiers in `{1,...,n}` needs at least `T >= (1/2) log*(n) - 1` communication rounds,
where `log* x = 0` for `x <= 1` and `log* x = 1 + log*(log_2 x)` otherwise. The upper bound
(matching, up to constant) is Cole–Vishkin's `O(log* n)` coloring algorithm, so the two sides pin
the answer to `Theta(log* n)` exactly. Evidence: PDF quote `"T >= (1/2) log*(n) - 1"` (their
eq. (1)) and the reduction lemma `"k+1 >= log* n for any k-ary 3-colouring function"`.

**The technique, precisely, because this report was asked for the technique not just the
result.** A `T`-round algorithm is recast as a function `A` of `2T+1` consecutive identifiers
(a sliding window over the cycle) that must give different outputs on overlapping windows
(Lemma in their Section 3, `A(x_1,...,x_k) != A(x_2,...,x_{k+1})`). The key move (their Lemma 2)
is a **compression step**: given a `k`-ary `c`-colouring function, define a `(k-1)`-ary
`2^c`-colouring function `B(x_1,...,x_{k-1}) = {A(x_1,...,x_{k-1},x_k) : x_k > x_{k-1}}` — i.e.
replace the *value* of `A` on the last argument by the *set of all values `A` could still take* as
the window's last coordinate ranges over everything larger. This shrinks the arity by 1 but
squares^ish the number of colours (`c -> 2^c`), and the overlap constraint is preserved. Iterating
this `k` times against a tower of exponentials `^i2 = 2^(2^(...2))` (`i` twos) forces the color
count up a power tower while the arity counts down to 1; at arity 1 a one-line pigeonhole
(Lemma 1: a 1-ary `c`-colouring function needs `c >= n`) forces `^{k+1}2 >= n`, i.e.
`k+1 >= log* n`. The `log*` is exactly "how many times can you compress-and-square before the
tower exceeds `n`."

**One-paragraph assessment of transfer.** The surface analogy to #1016 is tempting and worth
recording precisely because it is a trap: both problems are stated on a labelled cycle, and both
want a lower bound on "how many rounds / how many chords are needed," expressed as `Theta` or
`>= x + omega(1)` in `log* n`. But Linial's argument is a **for-all-algorithms, exists-a-hard-ID-
assignment** statement: the compression trick needs the adversary to range over exponentially many
possible continuations of the window (that's what turns `A` into a *set*-valued `B` and creates
the squaring). Erdős #1016's gaps `g_1,...,g_2k` are not a family of possible continuations of a
partial object that a construction must work against; they are one fixed integer vector chosen by
the *constructor*, and the "hardness" we want is a statement that holds for *every* choice of that
vector, not one recursively built by an adversary probing a fixed algorithm. There is no evident
analogue of "the algorithm's behavior on window `x_1..x_{k-1}` compresses to the set of all its
possible extensions," because there is no window/algorithm pair here — only a single sum. Any
transfer attempt has to manufacture that missing multi-instance structure first, e.g. by treating
the *family of all `2^k` chord-subset sums simultaneously* the way Linial treats the *family of
all possible next-identifiers*, and finding a compression operation on gap multisets that squares
some resource while shrinking `k` by one, bottoming out in the same kind of one-line pigeonhole.
I did not find that operation and do not believe it is a small step; it is the single most
promising *shape* of argument located this session, not a transferable lemma.

## (3) Recorded attempts at #1016 since 2023

**GitHub `google-deepmind/formal-conjectures`, issue #1073, "Erdős Problem 1016."** Opened
2025-10-14. Body states the problem exactly as Bondy posed it (`h(n) >= log_2 n + log* n - O(1)`
conjectured, unresolved) and is labelled `Combinatorics (AMS-05)`, `Erdős Problems`,
`New Conjecture`, milestone "All open Erdős problems formalized," **unassigned**, and (per the
issue's own status marker) "up for grabs." No comments, no linked PRs, no partial formalization
found. Evidence: issue body text quoted above; [github.com/google-deepmind/formal-conjectures/issues/1073](https://github.com/google-deepmind/formal-conjectures/issues/1073).
This is an autogenerated tracking issue (one per erdosproblems.com entry), not a human or AI proof
attempt — it records that the problem is *tracked for formalization*, not that anyone has worked
the mathematics.

**erdosproblems.com/1016 itself and its forum.** Direct fetch returned HTTP 403 (site blocks this
tool's fetcher); a search-engine paraphrase of the page (not the primary source) reproduces the
same statement already on file from `REPORT-lit-1.md`/`REPORT-lit-2.md`
(`log_2(n-1)-1 <= h(n) <= log_2 n + log* n + O(1)`, Griffin's lower-bound proof, GKW16's
upper-bound proof) and adds nothing new. A fetch of `erdosproblems.com/forum/thread/30` (the
forum thread numbering nearest #1016 discoverable by search) also returned HTTP 403, so its
content is **unknown**, not confirmed absent — a genuine gap in this sweep, not a negative result.

**Verdict (3):** one autogenerated formalization-tracking issue, zero comments, zero mathematical
progress; nothing else located. The forum itself could not be read (403), so "no attempts posted
there" is an *unknown*, not a checked absence.

## (1) Bounding how many distinct values a structured subset-sum family can take

**D. Conlon, J. Fox, H. T. Pham, "Subset sums, completeness and colorings," 2023 (published
version accessed; downloaded to this folder as
`Conlon-Fox-Pham-Subset-Sums-Completeness-Colorings.pdf`).** This is the strongest and most
recent (post-2023, matching the assignment's recency ask) general toolkit for "does `Sigma(A)`,
the set of subset sums of a structured integer set/sequence `A`, cover a long interval / a given
target / survive an adversarial coloring." Exact statements verified against the PDF:
- Theorem 1.1: the sparsest `r`-Ramsey-complete sequence (subset sums survive **any** `r`-coloring
  of the ground set) satisfies `|A ∩ [n]| = Theta(r log^2 n)` — both bounds proved, closing a
  problem Erdős priced at $350 combined.
- Theorem 1.5/1.6: the minimum number of colors `f(n)` needed so that a *specific* integer `n`
  is **not** a monochromatic subset sum of `[n-1]` is `Theta(n^{1/3}(n/phi(n))/((log n)^{1/3}
  (log log n)^{2/3}))`.
- Theorem 1.9/6.1: any `A subset [n]` with `|A| >= C*sqrt(n)` has a **homogeneous** arithmetic
  progression of length `n` inside `Sigma(A)` — the sharp form of Szemerédi–Vu.
- Theorem 1.7: exact value of `g(n,m)`, the largest subset of `[n]` with **no** subset summing to
  a specific target `m`.

**Proof engine, because the assignment wants the technique.** All of these reduce a `Z`-problem to
a `Z_m`-problem and grow `Sigma_m(A)` by an **iterative process with three phases** ("growth,"
"unsaturated," "saturated" — Lemma 5.6/6.2 in the paper): at each step, add the element of the
remaining set that most expands the current partial-sum set modulo the residual subgroup;
if growth stalls, a structural dichotomy (their Lemma 5.7, built on Deshouillers–Freiman's
inverse theorem for `|A+A| <~ 2|A|`) forces the stalled set into a union of few long arithmetic
progressions, which is then killed by a Selberg-sieve argument because the underlying set (primes,
or integers coprime to a controlled modulus) cannot concentrate on progressions. This is, as far
as this sweep could establish, the sharpest known machine for proving a structured integer family
has a LARGE set of subset sums.

**Assessment.** This machinery answers question (1) in the opposite direction from what #1016
needs: it is built to prove subset sums are **large/cover an interval**, and its lower-bound
constant is `log^2 n` or `n^{1/3}`-type, not `log*`. It does not transfer directly. What is
potentially reusable is the **dichotomy step** itself (a set of increments either expands the sum
set fast, or is forced into an additively structured — few-long-AP — shape): the gap-sum problem
is exactly the reverse question, "can a *small* structured family of subset sums be forced to
**miss** most of `[3,n]`," so the natural adaptation is to ask whether the alternating-class gap
sums, as `K` ranges over `2^k` subsets, are forced into a similarly additively-structured (hence
collision-prone, hence non-covering) shape whenever `k` is close to `log_2 n`. This is a concrete,
checkable next step (does an analogue of Lemma 5.7 apply to the specific sumset structure induced
by chord alternating classes?), not yet attempted here.

**K. G. Milans, F. Pfender, D. Rautenbach, F. Regen, D. B. West (2012), already on file from
`REPORT-lit-2.md`.** Restated here only because it is the closest *existing* answer to question
(1) phrased exactly as "how many distinct values can a structured family of subset sums (path
lengths across `p` chords) take": `s(G) > sqrt(p) - (1/2) ln p - 1`. At `p = Theta(log n)` this
gives only `Theta(sqrt(log n))` forced lengths, nowhere near `log_2 n`, so it under-shoots by an
exponential factor and cannot be the mechanism; it is listed for completeness of the ranked list
below, not as new information.

**Erdős distinct-subset-sums problem (Erdős–Moser).** Multiple 2020s papers were surfaced
(arXiv:2006.12988, arXiv:2510.06032, arXiv:2308.03748) proving lower bounds on `max(a_i)` for an
`n`-element set with all `2^n` subset sums distinct (currently best located general bound
`a_n >= (sqrt(2/pi) - o(1)) n^{-1/2} 2^n`, per arXiv:2006.12988's abstract). This is the same
"family of subset sums" object but the free parameter is the **opposite** one: it fixes that all
`2^n` sums are distinct and asks how large the ground set must be, whereas #1016 fixes the ground
set (gaps summing to `n`) and needs a bound on how many of the `2^k` sums **can** be distinct.
Structurally adjacent, not directly applicable; flagged so it is not re-searched by a later sweep.

## (2) log*/iterated-log terms in other recursive constructions, and whether the lower bound
matches

Besides Linial (the lead finding above), search surfaced only pointers, not verified primary
technique text, to one other classical `log*` **lower** bound:

**Tarjan's union-find "MIN" algorithm, `Theta(m log* n)` worst case (unweighted-union, no
path-compression variant), R. E. Tarjan, "A class of algorithms which require nonlinear time to
maintain disjoint sets," *JCSS* 18 (1979).** Multiple secondary sources (lecture notes, surveys —
none opened as primary text this session) confirm the bound is tight, i.e. there is a matching
`Omega(m log* n)` lower-bound construction, but I did not obtain or read Tarjan's actual
adversarial-sequence construction in this sweep. This is recorded as an **unknown**, not an
absent result: a plausible second data point for "how does a genuine `log*` lower bound get built"
that a follow-up sweep should open directly (search terms used: `"Tarjan log* n lower bound
disjoint set union recursive doubling construction"` — returned only secondary characterizations).

**Distributed LOCAL-model `Omega(log* n)` lower bounds more broadly (Linial's descendants).**
Search confirmed the same `Theta(log* n)` phenomenon recurs for maximal independent set and
maximal matching in bounded-degree graphs (citing Linial's technique directly), and that constant
approximations to maximum independent set on a ring also need `Omega(log* n)` time. All of these
inherit Linial's exact compression argument above; they are not independent techniques, so they do
not add a second transfer candidate, only more evidence that this is the canonical `log*`-lower-
bound machine in combinatorics/distributed computing.

**Negative result:** no search (postage-stamp/h-range extremal bases, complete-sequence minimal
covering, Erdős–Selfridge-style covering systems) turned up a *second*, structurally different
`log*`-with-matching-lower-bound phenomenon. The postage-stamp/h-range literature (Mossige and
successors, e.g. arXiv:2601.21423) has extremal functions governed by explicit polynomial-in-`h`
formulas for fixed `k`, with no iterated-log term located. This is reported as a checked absence
(two independent query families tried, see log below), not an "I didn't look."

## Ranked list of candidate techniques (as required by the task), with concrete application sketch

1. **Linial-style recursive compression forcing a power-tower obstruction (Section "Costliest
   finding" above).** Statement: `Theta(log* n)` matching bound for 3-colouring an `n`-cycle
   under a locality constraint. Sketch for #1016: define, for each `j` from `k` down to `1`, a
   "compressed" object that summarizes — as a *set*, not a single value — all cycle lengths
   still reachable using only the first `j` chords' alternating-class choices, in a way that
   *shrinks* the number of chords considered by one while the *size of the value-set* needed to
   stay injective must grow (squaring-like); iterate until `j=1`, where a one-line pigeonhole
   (analogous to Lemma 1) forces a lower bound on `n` in terms of a power tower of height `k`.
   The open step, honestly stated: nobody has found the "extend by one more chord / take the set
   of consequences" operation that plays the role of Linial's `B(x_1,...,x_{k-1}) = {A(...,x_k) :
   x_k > x_{k-1}}` for chord-gap sums, because #1016 has no adversarial "next identifier" to range
   over. Whoever attempts this must supply that missing ingredient first; it is the crux, not a
   detail.

2. **Conlon–Fox–Pham's growth/unsaturated/saturated dichotomy (Section (1) above), run in
   reverse.** Statement: a structured integer family's subset sums modulo `t` either grow fast at
   every step or the stalled generator set is forced into a small union of long arithmetic
   progressions (their Lemma 5.7, via Deshouillers–Freiman). Sketch for #1016: ask whether the
   `2^k` alternating-class gap sums, when they fail to cover `[3,n]`, are forced (by an analogous
   dichotomy on the *gap multiset* rather than a chosen integer set) into a small union of
   arithmetic-progression-like collision classes whenever `k <= log_2 n + o(log* n)`; if so, the
   size of that union, tracked recursively over `k`, is the natural place a `log*`-type additive
   term could fall out, because the dichotomy itself is inherently "either you win outright or you
   collapse into a small structured family," which is the same qualitative shape Linial's argument
   has. This is speculative and unverified; it is offered because it is the only other located
   machine that produces a genuine structural collapse (rather than a plain counting bound) for
   subset-sum-like families.

3. **Milans–Pfender–Rautenbach–Regen–West's overlap-forcing lemma, refined.** Already on file
   (`REPORT-lit-2.md`); repeated here only to rank it: it gives `Omega(sqrt(p))` forced distinct
   lengths from `p` chords via a pairwise-overlap pigeonhole, which is far weaker than what #1016
   needs (`p = Theta(log n)` chords would need to force `Theta(log n)` lengths, not
   `Theta(sqrt(log n))`), but its overlap/pigeonhole style is the most directly "gap-language"
   compatible of anything located, and a sharper version of the same lemma (exploiting more than
   pairwise overlaps, i.e. `j`-wise overlaps for growing `j`) is a lower-effort next step than
   either technique above, precisely because it needs no adversarial multi-instance apparatus.

## Search log (databases, queries, caps)

- **erdosproblems.com:** direct fetch of `/1016` and `/forum/thread/30` — both HTTP 403
  (blocked for this tool); treated as **unknown**, cross-checked via a search-engine paraphrase
  which added nothing beyond `REPORT-lit-1.md`/`REPORT-lit-2.md`.
- **GitHub (`google-deepmind/formal-conjectures`):** fetched issue #1073 directly; full text
  read, no comments.
- **arXiv / general web search**, queries run (each a distinct method/angle, per the "two
  independent search methods" rule): `Erdos problem 1016 pancyclic chords log star forum`;
  `"distinct subset sums" covering an interval lower bound few summands`; `Tarjan log* n lower
  bound disjoint set union recursive doubling construction`; `"log*" iterated logarithm matching
  lower bound combinatorial construction technique`; `complete sequence minimal number of terms
  cover interval representation function upper bound`; `Linial "locality in distributed graph
  algorithms" log star n lower bound proof technique cycle coloring`; `arxiv "Cycles with almost
  linearly many chords" pancyclic`; `postage stamp problem extremal function h-range complete
  sequence doubling iterated logarithm defect`; `"cycle spectrum" Hamiltonian graph 2024 2025
  sparse chords improved lower bound arxiv`; `Terence Tao blog pancyclic OR "log star" lower bound
  combinatorics recursive construction`; `"erdosproblems.com/1016" OR "problem 1016" Bondy
  pancyclic mathoverflow`.
- **Primary PDFs read in full this session and downloaded to this folder:**
  `Linial-Lower-Bound-Made-Easy-1402.2552.pdf` (3 pages, read completely),
  `Conlon-Fox-Pham-Subset-Sums-Completeness-Colorings.pdf` (75 pages, read completely —
  every theorem statement above is quoted or paraphrased directly from the verified text, not
  from an abstract).
- **Download failure logged, not hidden:** a direct fetch of Linial's original 1992 paper from
  `cs.huji.ac.il/~nati/PAPERS/locality_dist_graph_algs.pdf` returned an HTTP error page
  (`Support ID: B_2262060934065366778`), not a PDF; the file was deleted from this folder rather
  than left as a corrupt artifact, and the Laurinharju–Suomela re-proof was used instead since it
  states and proves the identical theorem.
- **MathOverflow/MathStackExchange:** no direct search interface reachable with the tools
  available in this session (general web search substituted); no #1016-specific thread located by
  that substitute, so coverage there is **unknown**, not confirmed absent.
- **Compute:** reading only, as instructed; no local computation, no scripts run, no processes
  launched.

## Verdict against the assignment's DONE WHEN

Ranked candidate techniques (above) each have citation, exact statement, and a concrete
application sketch. No technique located in this sweep proves or refutes
`h(n) >= log_2 n + log* n - O(1)`; the closest structural match (Linial's compression argument) is
reported with its precise point of non-transfer named, not papered over. The one recorded attempt
at #1016 since 2023 is an unstaffed formalization-tracking issue, not mathematical progress.
