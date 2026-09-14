# Bondy's upper-bound construction: what was obtainable, the explicit recipe, and u(k) vs t_k

Date: 2026-09-14. Assignment (Manager, this session): pin down Bondy's construction, obtain
whichever of {Bondy 1971, GKW 2016 ch. 4.5, Sridharan 1978} is accessible and say which, extract
an explicit recipe, derive `u(k)` (largest `n` the construction reaches with `k` chords) for
`k=1..12`, compare against `t_k = 5, 8, 14, 24, 40` (`k=1..5`), and give the recursion.

## What was obtained, and what was not (say which up front, per the assignment)

- **Bondy 1971** ("Pancyclic graphs I", JCTB 11, 80-84): not obtained as full text (ScienceDirect
  paywall, no open mirror located). Its content on this point is already established from prior
  sweeps and confirmed again here: Bondy **states without proof** the bound
  `n + log_2 n + H(n) + O(1)` edges suffice, `H(n)` defined as the smallest integer with
  `(log_2)^{H(n)}(n) < 2` (log_2 iterated `H(n)` times) — this is essentially `log*(n)`. Bondy's
  paper contains no construction recipe recoverable from any source examined; every later source
  that gives a recipe (below) is doing so on Bondy's behalf, not quoting him.
- **George-Khodkar-Wallis (GKW), *Pancyclic and Bipancyclic Graphs* (2016), Chapter 4 "Minimal
  Pancyclicity," pp. 35-47 (per the publisher's own table of contents, checked via Google Books
  this session).** **Not obtained.** Checked two independent routes this session: (a) the Google
  Books preview page for the book (`books.google.de/books/about/Pancyclic_and_Bipancyclic_Graphs`)
  exposes only the cover/reference pages, no Chapter 4 content; (b) a targeted web search for any
  open PDF, ResearchGate full text, or Springer preview of the chapter returned only paywall/
  purchase pages (Springer chapter DOI 10.1007/978-3-319-31951-3, $16.75+ purchase). This matches
  and independently reconfirms the same negative finding already on record in
  `construction/`'s `REPORT-construction.md` from an earlier task on this project (also could not
  obtain it). **Still unknown, not absent** — a library-interlibrary-loan or contacting the
  authors are the remaining routes, both outside this tool's reach.
- **M. R. Sridharan, "On an extremal problem concerning pancyclic graph," J. Math. Phys. Sci. 12
  (1978), 297-306.** **Not obtained.** This is an obscure, apparently print-only Indian journal
  (Madras); no digital record, DOI, abstract, or citation-database entry beyond the bare citation
  string was found by search. Recorded as unknown, not absent — genuinely could not look further
  with the tools available.
- **What was actually obtained and is the primary source for everything below: N. Alon and
  M. Krivelevich, "Sparse pancyclic subgraphs of random graphs," arXiv:2308.01564 (already in
  this folder as `2308.01564.pdf`/`.txt`), Section 3, "The constructed pancyclic subgraph"
  (local text pp. 3-4, immediately following the paper's Definition 3).** Alon-Krivelevich
  explicitly set out to **reproduce GKW's deterministic recipe** before giving their own
  randomized analogue, and state: *"We emulate (an approximation of) the construction in [6]"*
  (`[6]` = GKW). They then give the recipe in enough detail to extract exact formulas, which is
  the best located substitute for the unobtained primary GKW text. Everything numeric below is
  derived from this quoted recipe, not guessed, and every number is shown with its arithmetic so
  it can be checked.

## The explicit recipe (quoted, then unpacked)

**Definition 3 (AK, quoted).** *"Let `G` be a graph and `H ⊆ G` a Hamilton cycle, `2 ≤ ℓ ≤ n-2`.
An edge `e ∈ E(G)` is an `ℓ`-shortcut with respect to `H` if (at least) one of the two intervals on
`H` that connects the two endpoints of `e` has length `ℓ+1`."* Using `H` plus an `ℓ`-shortcut
gives a cycle of length `n - ℓ`.

**The recipe itself (AK, quoted verbatim, Section 3):**

> "In the construction described in [6], one creates a sparse pancyclic graph by taking an
> n-cycle H and K shortcuts `e_0, e_1, ..., e_K`, where K is such that
> `(1/2) n ≤ 2^{K+1} + K - 1 ≤ n` and `e_i` is a `2^i`-shortcut. Additionally, these shortcuts are
> consecutive on the cycle, so that `e_i, e_{i+1}` and their corresponding intervals intersect in
> a vertex `v_i`. By taking intervals from the cycle H and a subset of shortcuts, one can now
> encode a cycle of every length between n and `n - 2^{K+1} + 1`. Next, by adding the edge
> between the first vertex of `e_0` and the second vertex of `e_K`, all cycle lengths between
> `K+2` and `2^{K+1}+K` can be encoded. This leaves out only a subset of cycle lengths contained
> in `[5, K+1]`, and adding these lengths to the set of cycle lengths in the graph can be done by
> inserting `O(log* n)` additional edges. For the full details of the construction, we refer the
> reader to [6] Chapter 4.5."

So the recipe has three stages, in chord-count order:
1. **`K+1` shortcut chords** `e_0,...,e_K` (`e_i` is a `2^i`-shortcut), chosen consecutively so
   their intervals chain through shared vertices `v_i`. Taking any subset `S ⊆ {0,...,K}` and
   using the shortcuts in `S` removes `sum_{i in S} 2^i` from the Hamilton length; since every
   integer in `[0, 2^{K+1}-1]` has a unique binary representation over `{0,...,K}`, this alone
   covers every cycle length in `[n - 2^{K+1} + 1, n]`.
2. **`+1` joining chord** (endpoint of `e_0` to the far endpoint of `e_K`): extends coverage
   downward to cover every length in `[K+2, 2^{K+1}+K]`.
3. **`O(log* n)` more chords** to patch the remaining gap, a *subset* of `[5, K+1]` (not
   necessarily all of it) that stages 1-2 miss. AK explicitly decline to specify which lengths in
   that subset or how the patch is built, deferring to GKW Ch. 4.5 — the exact page this task was
   sent to retrieve, and which could not be retrieved (see above). **This is the one piece of the
   recipe genuinely missing from every source examined**, and it is exactly the piece that would
   pin down an exact integer recursion for `k >= 6`. Flagged here rather than guessed at.

## Deriving `u(k)` for stages 1-2 only (exact, fully sourced arithmetic)

Total chords after stages 1-2: `k = (K+1) + 1 = K+2`. Stage 1-2 coverage is gap-free (no missing
lengths at all, so stage 3 contributes 0 chords) exactly when `[5, K+1]` is empty, i.e. `K <= 3`
— which covers `k = 2,3,4,5`, precisely the range Manager asked to check against `t_k`.

For the two covered ranges `[K+2, 2^{K+1}+K]` and `[n-2^{K+1}+1, n]` to abut with no gap between
them (so together they cover all of `[K+2, n]`, and with stage 1-2 alone `[3,K+1]` empty means the
whole of `[3,n]` is covered), the largest usable `n` is where the ranges just touch:
`2^{K+1}+K >= n - 2^{K+1}` , i.e. `n <= 2^{K+2} + K`. Writing `k = K+2` (so `K = k-2`):

```
u(k) [recipe, stages 1-2 only, valid for k = 2,3,4,5] = 2^k + k - 2
```

| k | K | u(k) recipe | t_k (actual, measured) | ratio u/t |
|---|---|---|---|---|
| 2 | 0 | 4  | 8  | 0.50 |
| 3 | 1 | 9  | 14 | 0.64 |
| 4 | 2 | 18 | 24 | 0.75 |
| 5 | 3 | 35 | 40 | 0.875 |

(`t_1=5` has no recipe counterpart: stages 1-2 need `K>=0`, i.e. `k>=2`; a single-chord minimal
pancyclic graph is a different, ad hoc small construction, not an instance of this recipe.)

**Verdict on the comparison Manager asked for: they do NOT match for `k<=5`, and the direction and
size of the mismatch is informative.** The general GKW/Bondy recipe systematically *undershoots*
the actual best-known thresholds `t_k` by a shrinking margin (50% short at `k=2`, only 12.5% short
at `k=5`). This is exactly what you'd expect from an asymptotically-tight-but-not-optimized
construction: the real `t_k` for `k<=5` come from George-Marr-Wallis's and Griffin's *specific,
individually hand/computer-optimized* 3-, 4- and 5-chord graphs (already on file: Griffin,
arXiv:1312.0274, "A new construction with 5 chords (Figure 1)... extension of [George-Marr-
Wallis]'s construction with 4 chords"), not instances of the generic binary-shortcut recipe. The
generic recipe is built to make the *asymptotic* exponent `log_2 n` correct as `n -> infinity`
(ratio `u/t -> 1` as the table shows), not to be optimal at small `n`. This is the concrete
"where they differ" the assignment asked for: **the construction that actually attains `t_k` for
`k<=5` is not Bondy's / GKW's general recipe at all** — it is the separate small-chord-count
ad hoc family from George-Marr-Wallis/Griffin, already documented in `REPORT-lit-1.md` and
`1312.0274.txt`. Any proof that `h(n) <= u(k)` for the general recipe is a strictly weaker
statement than the known exact small-`n` results.

## The recursion for stages 1-2 (exact, as requested "in the form `t_k >= t_{k-1} + (something)`")

From `u(k) = 2^k + k - 2`: substituting `u(k-1) = 2^{k-1}+k-3`,

```
u(k) = 2*u(k-1) + (4 - k)       [exact, for k = 3,4,5]
```

Check: `u(3) = 2*4 + 1 = 9` ✓. `u(4) = 2*9 + 0 = 18` ✓. `u(5) = 2*18 - 1 = 35` ✓. So in this
regime the construction *doubles the reach per extra chord, minus a small and shrinking
correction* — the `(4-k)` term is exactly the bookkeeping cost of the `K` in `2^{K+1}+K-1`. This
is the honest recipe-recursion; note its growth rate (~2x per chord) is *faster* than the real
data's growth rate (`t_k/t_{k-1}` = 1.6, 1.75, 1.71, 1.67 for `k=2..5` — converging toward roughly
1.6-1.7, not 2), which is only possible because the recipe's absolute values are smaller (see
ratio column above) even though its per-step multiplier is larger; the two effects partly cancel
and the recipe slowly catches up.

## Stage 3 (`k >= 6`): what could and could not be derived

For `k >= 6` (`K >= 4`), the gap `[5, K+1]` is non-empty and needs stage-3 chords, whose exact
rule is the one piece of the recipe that only exists in the unobtained GKW Ch. 4.5. Two honest,
clearly-labelled bounds follow from what *is* in hand, rather than a guessed exact figure:

- **A valid, fully-sourced, but almost certainly non-optimal explicit construction** for `K >= 4`:
  patch every missing length in `[5,K+1]` (worst case, size `K-3`) with one dedicated chord each
  (a single chord creating one specific short cycle length is elementary and does not need GKW's
  unseen log*-recursive trick). This gives `k = (K+2) + (K-3) = 2K-1` chords reaching
  `n = 2^{K+2}+K`, i.e. (substituting `K=(k+1)/2`, valid for odd `k>=7`):
  `u(7)=68` (`K=4`), `u(9)=133` (`K=5`), `u(11)=262` (`K=6`). This is a valid lower bound on what
  the recipe family can do (only odd `k` land on integers this way; even `k` in this crude model
  waste a chord), but it is explicitly **not** the `O(log* n)`-efficient version GKW actually
  proves — it is a strictly weaker fallback built only from the pieces AK's text confirms.
- **What the source claims but does not let me compute exactly:** GKW's actual stage-3 is
  `O(log* n)` chords, not `O(K)` chords, which — combined with Bondy's own definition of `H(n)` as
  "iterate `log_2` until `<2`" — strongly suggests stage 3 is itself a recursive application of
  the *same* stages-1-2 idea to the residual gap (size `~K ~ log_2 n`), then again to that gap's
  own residual (`~ log_2 log_2 n`), etc., terminating after `H(n) = O(log* n)` levels. If so the
  qualitative recursion is `k(n) ≈ (K(n)+2) + k(K(n)+1)`, but I do not have GKW's exact rule for
  *which* lengths survive to the next level (AK's "a subset of `[5,K+1]`," not "all of"), so I
  cannot turn this into verified integers for `k=6,8,10,12` without fabricating the missing
  constant. **Marking `u(6), u(8), u(10), u(12)` as not derivable from sources in hand, rather
  than inventing a number.**

## Numeric summary requested (k=1..12)

| k | u(k), sourced | status |
|---|---|---|
| 1 | — | recipe does not apply (ad hoc small graph, not this construction) |
| 2 | 4 | exact from recipe stages 1-2 |
| 3 | 9 | exact from recipe stages 1-2 |
| 4 | 18 | exact from recipe stages 1-2 |
| 5 | 35 | exact from recipe stages 1-2 |
| 6 | not derivable | stage 3 (patch rule) unsourced; worst-case fallback would need k=7, not 6 |
| 7 | 68 (fallback, non-optimal) | valid but not GKW's efficient version |
| 8 | not derivable | see k=6 |
| 9 | 133 (fallback, non-optimal) | valid but not GKW's efficient version |
| 10 | not derivable | see k=6 |
| 11 | 262 (fallback, non-optimal) | valid but not GKW's efficient version |
| 12 | not derivable | see k=6 |

`t_k` for `k=6..12` were not supplied by Manager this round and are not claimed here.

## An unsourced numerical observation, flagged as speculative (not part of the requested deliverable)

Purely as arithmetic curiosity on the four given real thresholds `t_2,...,t_5 = 8,14,24,40`: they
satisfy `t_k = 2*Fib(k+3) - 2` exactly for `k=2,3,4,5` (Fibonacci `Fib(5)=5, Fib(6)=8, Fib(7)=13,
Fib(8)=21`; `2*5-2=8`, `2*8-2=14`, `2*13-2=24`, `2*21-2=40`), equivalently
`t_k = t_{k-1} + t_{k-2} + 2` for `k=4,5` (`t_4 = 8+14+2=24` ✓, `t_5=14+24+2=40` ✓; this
does **not** hold at `k=3`, `t_2+t_1+2=8+5+2=15 != 14`, off by one). This is four data points
fitting a two-parameter family and is flagged explicitly as **not derived from any source
construction** — no located paper claims minimal-pancyclic thresholds grow like Fibonacci numbers
— and could easily be coincidence that breaks at `k=6`. Recorded only because it is a striking,
checkable pattern a future sweep with more exact `t_6, t_7,...` data could falsify or confirm; it
is not evidence about Bondy's actual construction and should not be cited as such.

## Search log

Web search: `Sridharan 1978 "extremal problem concerning pancyclic" Journal Mathematical Physical
Sciences` (no digital record found); `"Pancyclic and Bipancyclic Graphs" George Khodkar Wallis
chapter 4 "minimal pancyclicity" pdf` (Google Books TOC only, pp. 35-47, no body text);
`"Minimal Pancyclicity" George Khodkar Wallis springer chapter abstract shortcut construction`
(Springer paywall page only). Direct fetch: Google Books "about" page for the GKW book (preview
confirmed empty of Chapter 4 body text — two independent methods, search + direct fetch, per the
"absent" rule). Local files re-read in full: `1312.0274.txt` (Griffin, confirms Bondy's Claim 1
statement and that Griffin/GMW's chord constructions are separate from Bondy/GKW's asymptotic
recipe, and that Griffin explicitly refers the reader to Sridharan [8] for "constructions which
give exact upper bounds on m(n) for general n" — i.e. Griffin also did not reproduce it);
`2308.01564.txt` (Alon-Krivelevich, Section 3, the source of everything quoted above); prior
`construction/REPORT-construction.md` (independent confirmation from an earlier task that GKW
Ch. 4.5 was likewise unobtainable then).

## Conflict/fact note

Manager's message stated GKW give constructions with `(1+o(1)) log_2 n` chords — that description
matches AK's summary of the *leading term* (stage 1-2, `K+2 ≈ log_2 n`), but the accessible text
is explicit that the true count is `log_2 n + O(log* n)` (stage 3 included), not `(1+o(1)) log_2 n`
alone; the `log* n` term is exactly the part this report could not pin down numerically. Recorded
as a clarification, not a contradiction of the assignment.
