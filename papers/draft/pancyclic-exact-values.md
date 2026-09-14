# Exact values of the minimum pancyclic edge count $m(n)$ for $3\le n\le 41$

**Authors:** AUTHORS TBD

## Abstract

A graph on $n$ vertices is *pancyclic* if it contains a cycle of every length
$3,4,\dots,n$. Let $m(n)$ be the minimum number of edges of a pancyclic graph on
$n$ vertices, and write $m(n)=n+h(n)$, where $h(n)$ counts the chords added to a
Hamilton cycle (Erdős Problem #1016, after Bondy 1971). Griffin (2013) determined
$m(n)$ exactly for $n\le 37$ by exhaustive and constructive search. We report
$m(n)$ for $38\le n\le 41$, obtained by two independently implemented exhaustive
GPU/CPU chord searches and cross-checked by two further from-scratch verifiers:
$h(38)=h(39)=h(40)=5$ and $h(41)=6$, so $m(38{:}41)=43,44,45,47$. We record the
extremal $5$-chord graphs at the $n=40$ threshold, a subdivision lemma showing why
counting arguments can improve only the additive constant, never the growing
correction term the conjecture needs, and two numerical observations on the
threshold sequence $t_k$ (largest $n$ with $h(n)=k$): its ratio to $2^{k+1}$ is
strictly decreasing, and a previously-noted 2-parameter closed form,
$t_k=2\,\mathrm{Fib}(k+3)-2$, exact at $k=2,3$ by construction, is also exact
at $k=4,5$. A dedicated 6-chord search brackets the next threshold as
$56\le t_6\le129$ and stalls 3 lengths short of a witness at the
closed form's predicted value, $n=66$, neither confirming nor refuting it.

## 1. Introduction

Bondy [Bo71] proved that a Hamiltonian graph with degree sum at least $n$ for every
nonadjacent pair is pancyclic unless it is $K_{n/2,n/2}$, and stated without proof
that the minimum-edge function $m(n)=n+h(n)$ satisfies
$$\log_2(n-1)-1\ \le\ h(n)\ \le\ \log_2 n+\log_* n+O(1).$$
Erdős believed the upper bound is closer to the truth but could not prove
$h(n)-\log_2 n\to\infty$ (as recorded on the problem's current tracking page,
erdosproblems.com/1016).

**Jia (1996)** [Jia96], the earliest intermediate result located between Bondy's
claim and its eventual proof, defines $g(n)$ (the same function as $m(n)$) and
proves, for $n$ sufficiently large,
$$n+\log_2 n-1\ \le\ g(n)\ \le\ n+\tfrac32\log_2 n+1 \qquad\text{(Thm. 1.13)},$$
and, as a corollary of a further theorem,
$$g(n)=n+\log_2 n+O(\log_2\log_2 n) \qquad\text{(Cor. 1.15)}.$$
Jia also *conjectured*
$$g(n)=n+\log_2 n+O(1),\quad n\to\infty \qquad\text{(Conj. 1.16)},$$
which is, in substance, Erdős Problem #1016 itself. (These statements were
recovered by OCR of a scanned secondary survey, since Jia's original paper could
not be located; see `papers/REPORT-oeis-and-jia.md` for the full transcription and
its caveats, and Section 3 below on why they do not affect the exact values
reported here.)

**George, Khodkar and Wallis (2016)** [GKW16] — what can actually be sourced
here is more limited than earlier drafts of this note stated, and is worth
being precise about. This project never obtained GKW16's Chapter 4 itself:
two independent attempts (`papers/REPORT-bondy-construction.md`) found only
the publisher's table of contents, confirming the chapter's title, "Minimal
Pancyclicity," and nothing of its body text or abstract. What can be cited is
secondary: Terence Tao's comment on the problem's tracking page (18 Oct 2025,
quoted in full in `papers/REPORT-lit-4.md`) says "the first literature proof
of the upper bound $h(n)\le\log_2n+\log_*n+O(1)$ that **seems to exist** is in
Chapter 4.5" of GKW16 — a hedge we preserve rather than upgrade to certainty —
and Alon and Krivelevich [AK25] independently attribute a specific
construction to GKW16 and state they "emulate (an approximation of) the
construction in [GKW]," i.e. even AK's own reproduction is explicitly
approximate. Every construction detail used later in this note (Section 6.3)
is cited to Alon–Krivelevich's paraphrase, not to GKW16 directly.

**Griffin (2013)** [Gr13] proves the lower bound
$m(n)\ge n+\log_2(n-1)-1$ rigorously (from the elementary cycle-count ceiling
$2^{k+1}-1$ on the number of cycles in a Hamiltonian graph with $k$ chords, due to
Shi), and determines $m(n)$ exactly for all $n\le 37$, combining an exhaustive
search on graphs with up to 29 vertices with a 5-chord construction valid through
$n=37$. Griffin's Table 1 is the earliest, and until now the only, exact tabulation
of $m(n)$ beyond the smallest cases.

**Alon and Krivelevich** [AK25] study the analogous question for random graphs:
for $G\sim G(n,p)$ with $p\ge(1+o(1))\ln n/n$, with high probability $G$ contains
a pancyclic subgraph with $n+(1+o(1))\log_2 n$ edges. This is an existence result
in a random host graph, not a universal extremal theorem, but it is evidence for
the field's expectation that the true order of $h(n)$ is close to $\log_2 n$.

**Current status.** The single comment on the problem's erdosproblems.com page
(user TerenceTao, 18 Oct 2025, quoted in full in `papers/REPORT-lit-4.md`) — which
is the most current public accounting located anywhere in this project's
literature sweeps — states that "the consensus seems to be that Bondy's bounds,
which are now proven in the literature, remain the state of the art except for
very small $n$ where there is some work by George, Marr, and Wallis," and names no
exact value of $m(n)$ or $h(n)$ beyond Griffin/George–Marr–Wallis's $n\le 37$. This
paper's Section 2 table is, to the extent of this project's own literature search,
the first published extension of that table.

## 2. Exact values

$h(n)$ is the number of chords added to the $n$-cycle $C_n$, and $m(n)=n+h(n)$.
Values for $n\le 37$ are Griffin's Table 1 [Gr13] (reproduced verbatim in the
project's `papers/1312.0274.txt`; values for $n\le 22$ also agree, term for term,
with the published OEIS sequence A105206 once its indexing is read correctly —
see `papers/oeis/A105206-extension.md`). Values for $38\le n\le 41$ are new,
established in this project (Section 3 gives the method and every witness).

| $n$ | $h(n)$ | $m(n)$ | source |
|---:|---:|---:|---|
| 3 | 0 | 3 | Griffin Table 1 [Gr13] |
| 4 | 1 | 5 | Griffin Table 1 [Gr13] |
| 5 | 1 | 6 | Griffin Table 1 [Gr13] |
| 6 | 2 | 8 | Griffin Table 1 [Gr13] |
| 7 | 2 | 9 | Griffin Table 1 [Gr13] |
| 8 | 2 | 10 | Griffin Table 1 [Gr13] |
| 9 | 3 | 12 | Griffin Table 1 [Gr13] |
| 10 | 3 | 13 | Griffin Table 1 [Gr13] |
| 11 | 3 | 14 | Griffin Table 1 [Gr13] |
| 12 | 3 | 15 | Griffin Table 1 [Gr13] |
| 13 | 3 | 16 | Griffin Table 1 [Gr13] |
| 14 | 3 | 17 | Griffin Table 1 [Gr13] |
| 15 | 4 | 19 | Griffin Table 1 [Gr13] |
| 16 | 4 | 20 | Griffin Table 1 [Gr13] |
| 17 | 4 | 21 | Griffin Table 1 [Gr13] |
| 18 | 4 | 22 | Griffin Table 1 [Gr13] |
| 19 | 4 | 23 | Griffin Table 1 [Gr13] |
| 20 | 4 | 24 | Griffin Table 1 [Gr13] |
| 21 | 4 | 25 | Griffin Table 1 [Gr13] |
| 22 | 4 | 26 | Griffin Table 1 [Gr13] |
| 23 | 4 | 27 | Griffin Table 1 [Gr13] |
| 24 | 4 | 28 | Griffin Table 1 [Gr13] |
| 25 | 5 | 30 | Griffin Table 1 [Gr13] |
| 26 | 5 | 31 | Griffin Table 1 [Gr13] |
| 27 | 5 | 32 | Griffin Table 1 [Gr13] |
| 28 | 5 | 33 | Griffin Table 1 [Gr13] |
| 29 | 5 | 34 | Griffin Table 1 [Gr13] |
| 30 | 5 | 35 | Griffin Table 1 [Gr13] |
| 31 | 5 | 36 | Griffin Table 1 [Gr13] |
| 32 | 5 | 37 | Griffin Table 1 [Gr13] |
| 33 | 5 | 38 | Griffin Table 1 [Gr13] |
| 34 | 5 | 39 | Griffin Table 1 [Gr13] |
| 35 | 5 | 40 | Griffin Table 1 [Gr13] |
| 36 | 5 | 41 | Griffin Table 1 [Gr13] |
| 37 | 5 | 42 | Griffin Table 1 [Gr13] |
| **38** | **5** | **43** | this project (`search/n38k5-A0.txt`, witness) |
| **39** | **5** | **44** | this project (`search/hn_k5.csv`, witness) |
| **40** | **5** | **45** | this project (`search/gpu-40-5-all.txt`, exhaustive; `search/hn_k5.csv`, first witness) |
| **41** | **6** | **47** | this project (`search/gpu-41-5d.txt`, exhaustive elimination of $k=5$; `search/ls-41-6.txt`, $k=6$ witness) |

### 2.1 Thresholds

Let $t_k$ be the largest $n$ with $h(n)=k$. From the table above and Griffin's
Table 1:
$$t_1=5,\quad t_2=8,\quad t_3=14,\quad t_4=24,\quad t_5=40.$$
(Source: `notes/01-subdivision-reformulation.md`, "Update 2026-09-14 evening,"
consistent with Griffin Table 1 for $t_1..t_4$ and with this project's
exhaustive $n=41,k=5$ elimination for $t_5=40$.)

### 2.2 The five extremal 5-chord graphs on 40 vertices

An exhaustive GPU run at $n=40,k=5$ (`search/gpu_pancyc.py`, full enumeration mode
`--all`, `search/gpu-40-5-all.txt`, `tested=14373209608`) finds exactly ten
5-chord pancyclic graphs on 40 vertices, which fall into five classes under the
dihedral symmetry (rotation and reflection) of $C_{40}$ (`notes/01-subdivision-reformulation.md`).
One representative per class, with its gaps listed cyclically around the
Hamilton cycle and its cycle/length counts:

| chords | shared endpoints | gaps (cyclic) | cycles | distinct lengths |
|---|---:|---|---:|---:|
| $(0,2)(1,5)(1,7)(3,34)(24,39)$ | 9 | 1,1,1,5,10,17,2,2,1 | 45 | 38 |
| $(0,2)(0,37)(1,35)(3,18)(8,39)$ | 9 | 1,1,1,5,10,17,2,2,1 | 45 | 38 |
| $(0,2)(0,33)(1,13)(3,34)(32,35)$ | 9 | 1,1,5,1,1,1,19,10,1 | 48 | 38 |
| $(0,4)(0,5)(1,34)(2,35)(3,15)$ | 9 | 1,1,1,1,1,5,1,19,10 | 48 | 38 |
| $(0,7)(1,8)(2,10)(2,11)(9,21)$ | 9 | 1,1,1,1,5,1,1,19,10 | 48 | 38 |

Every extremal graph has exactly one shared endpoint among its five chords (nine
distinct endpoints in total), three "geometric" gaps of size approximately
$n/2,n/4,n/8$ (either $19,10,5$ or $17,10,5$) and the remaining six gaps of size
$1$ or $2$. Only $45$–$48$ of the $2^6-1=63$ cycles allowed by the counting
ceiling actually occur, and exactly $38=n-2$ lengths are distinct — i.e. the
counting bound is slack by $15$–$18$ cycles even though the graph is edge-extremal.
The same two-scale shape (a handful of large "geometric" gaps plus many gaps of
size 1–2) recurs at every earlier threshold (`notes/01-subdivision-reformulation.md`):

| $n$ | $k$ | gap profile |
|---:|---:|---|
| 8 | 2 | 3,3,2 |
| 14 | 3 | 7,3 \| 2,1,1 |
| 24 | 4 | 11,6 \| 2,2,1,1,1 |
| 40 | 5 | 19,10,5 (or 17,10,5) \| six gaps of 1–2 |

## 3. Method

### 3.1 Triangle case split

Both search programs use the same reduction, stated in `search/pancyc.c`:
"Every pancyclic graph contains a triangle, and up to rotation of the cycle a
triangle is one of three shapes, so the search is split: A: chord $(0,2)$ present
[a span-2 chord]; B: no span-2 chord; chords $(0,b),(1,b)$ present [two chords +
one cycle edge]; C: no span-2 chord, no shape-B pair; $(0,b),(b,c),(0,c)$ present
[three chords]." Because only rotation symmetry is used (not reflection), "the
enumeration is exhaustive: if all three modes print NONE, no $k$-chord graph is
pancyclic." `search/gpu_pancyc.py` implements the identical split ("Same case
split as pancyc.c").

### 3.2 Cycle-space enumeration

Cycles are not enumerated by graph search but read off the cycle space: the basis
is the Hamilton cycle plus, for each chord $(a,b)$, the chord together with the
cycle-path from $a$ to $b$; "every cycle of the graph is a XOR of basis elements
($2^{k+1}$ elements); an element is a cycle iff all vertex degrees are 0 or 2 and
its edges are connected" (`search/pancyc.c`). The CPU program walks all $2^{k+1}$
XOR combinations via a Gray code so each step flips exactly one basis element; the
GPU kernel (`search/gpu_pancyc.py`) does the same per-thread, with one CUDA
thread per candidate chord set. A sound pruning rule is used only in the CPU
program: with $j$ chords placed, the graph already has at most $2^{j+1}-1$
cycles, and the remaining $k-j$ chords can add at most $2^{k+1}-2^{j+1}$ further
cycle-space elements, so if (distinct lengths so far) $+\,2^{k+1}-2^{j+1} < n-2$
the partial chord set is abandoned (`search/pancyc.c`, comment block and the
`bound` check in `rec`).

### 3.3 Programs and their roles

* **`search/pancyc.c`** — CPU exhaustive search, edge masks as 128-bit integers
  (`unsigned __int128`), safe for $n+k\le 128$ (the source itself flags, in a
  2026-09-14 reviewer note, that its declared `MAXN=120,MAXK=12` would overflow
  that bound and that "in practice this program is only run with $n\le 60$,
  $k\le 6$"). Used for the $n=38$ shard search (`search/n38k5-A0.txt`
  through `...A7.txt` and `...BC.txt`, one shard per residue class of the first
  free chord) and for small-$n$ regression (`search/hn.csv`, $n\le 37$).
* **`search/gpu_pancyc.py`** — GPU exhaustive search (CuPy `RawKernel`), edge
  masks as 64-bit integers, valid for $n\le 60,k\le 8$; candidate $r$-combinations
  are unranked from a thread index in colex order via the standard combinadic
  construction (binomial-coefficient table `binom[c][i]=\binom{c}{i}` for
  $c<1024,i\le4$, source comment "unrank colex $r$-combination of $\{0..M-1\}$").
  Progress and partial results are checkpointed to a JSON state file
  (`gpu-state-{n}-{k}.json`) so a run can resume after interruption — this is why
  `search/gpu-41-5d.txt`'s cumulative `tested=17615450195` spans several
  restarted invocations (visible as the `ABORTED`/`NONE` sequence in
  `search/hn_k5.csv`'s $n=41$ rows). Used for the full exhaustive $n=40$ run
  (`search/gpu-40-5-all.txt`) and the exhaustive $n=41,k=5$ elimination
  (`search/gpu-41-5d.txt`).
* **`search/localsearch.py`** — randomized local search (simulated-annealing-style
  chord perturbation, scoring by number of missing cycle lengths), used only to
  *find* an upper-bound witness quickly, never to prove a negative. Its output
  `search/ls-41-6.txt` is the source of the $n=41,k=6$ witness.
* **`search/verify.py`** — independent brute-force check using `networkx`'s
  general-purpose `simple_cycles`, not the cycle-space method above; used as a
  first independent cross-check on small cases.
* **`papers/construction/check.py`** — a second, independently written
  cycle-space implementation (own basis/XOR/connectivity code, not shared with
  `pancyc.c`/`gpu_pancyc.py`), used in `papers/REVIEW-search.md` to re-verify the
  three witnesses at $n=38,40,41$ from scratch; it reproduces the exact same
  length sets (e.g. "$n=38$, chords $(0,2),(0,18),(1,12),(3,19),(17,20)$: 36
  lengths = 3..38").
* **`papers/construction/indep.c`** — a *third*, independently written verifier,
  explicitly "deliberately no cycle-space XOR": it enumerates cycles by direct
  DFS over the adjacency matrix from every start vertex. Its `witnesses` mode
  hard-codes the three witnesses for $n=38,40,41$ and reports the popcount of the
  found length-set bitmask against the needed range, giving a third, structurally
  different confirmation that each is pancyclic.
* **Lean 4 formalisation — now a real, kernel-checked fourth verification**
  (superseding the earlier stub, which had empty cycle lists and proved
  nothing; see `papers/REVIEW-notes01.md`'s note on that state if a prior
  draft of this document is consulted). `Erdos1016/ListCycle.lean` proves a
  general bridge lemma, `isPancyclic_of_lists`/`isPancyclic_of_candidates`:
  from an explicit `List (Fin n)` for each required length with no repeated
  vertex, consecutive `Adj`, and a closing edge, it constructs an actual
  `SimpleGraph.Walk` and proves `Walk.IsCycle` of the matching length — a
  genuine list-to-cycle construction, not a restatement of the hypothesis.
  `Erdos1016/Pancyclic.lean` applies this to the two witness graphs, giving
  `isPancyclic_G38 : IsPancyclic G38` and `isPancyclic_G41 : IsPancyclic G41`
  (with `IsPancyclic` defined via `SimpleGraph.Walk.IsCycle` in
  `Erdos1016/Basic.lean`, so these are proofs in the same sense the project's
  other verifiers check, not a weaker Bool-only restatement). Independently
  re-verified in this session: `lake build Erdos1016` completes with 0 errors
  (only Mathlib style-linter warnings — copyright-header length, line length —
  no `sorry`), and `#print axioms Erdos1016.isPancyclic_G38`/`_G41`, run fresh
  via `lake env lean` on a throwaway one-off file (not committed), both report
  exactly `[propext, Classical.choice, Quot.sound]` — the three standard
  Mathlib axioms, with no `sorryAx` and no `native_decide`. This makes Lean a
  genuine fourth independent verification for $n=38,41$ specifically (not yet
  extended to $n=39,40$).

  `Erdos1016/Excess.lean` restates the result in this paper's own language:
  `PancyclicWithChords n k := ∃ cs : Finset (Sym2 (Fin n)), cs.card = k ∧
  (∀ e ∈ cs, e ∉ (baseCycle n).edgeSet) ∧ IsPancyclic (baseCycle n ⊔
  fromEdgeSet ↑cs)` — i.e. literally "$k$ non-cycle edges added to $C_n$ give
  a pancyclic graph," matching $h(n)\le k$ directly — and proves
  `pancyclicWithChords_38_5`/`pancyclicWithChords_41_6` from the same
  underlying witnesses via an explicit graph-equality lemma
  (`G38_eq`/`G41_eq`) rather than restating the hypothesis. `Erdos1016/Witness56.lean`
  gives `isPancyclic_G56` for the Section 6.3 witness
  $(0,2)(0,53)(1,39)(20,39)(39,48)(48,53)$, so $t_6\ge56$ is now also
  kernel-checked (as `IsPancyclic`, not yet restated in `PancyclicWithChords`
  form — that restatement, along with $n=39,40$, is in progress and not yet
  in this file). Independently re-verified in this session exactly as above:
  `lake build Erdos1016 Erdos1016.Witness56` completes with 0 errors
  (`Build completed successfully (8713 jobs)`; style-linter warnings only),
  and a fresh `#print axioms` on `pancyclicWithChords_38_5`,
  `pancyclicWithChords_41_6`, and `isPancyclic_G56` all report exactly
  `[propext, Classical.choice, Quot.sound]`.

### 3.4 Which program established which bound

For every $n$ in $38..41$, the *lower bound* $h(n)\ge5$ is inherited from Griffin's
own published elimination of $k\le4$: Griffin's Corollary 1 gives an absolute
ceiling of $2^{k+1}-1$ cycles for a $k$-chord Hamiltonian graph, so $k=4$ permits
at most $31$ cycles; combined with Griffin's exhaustive computer search of
$k\le4$ chords (which the paper states was run without restriction to small $n$)
this rules out any $4$-chord pancyclic graph on $n\ge25$ vertices outright — no
new search was needed to re-establish $h(n)\ge5$ for $n=38..41$. What this
project newly supplies is:

| $n$ | what was newly established | program / file | exhaustive? |
|---:|---|---|---|
| 38 | a $k=5$ witness (upper bound $h(38)\le5$, hence $=5$) | `search/pancyc.c`, shard search, `search/n38k5-A0.txt` (witness found after `tested=52296703` in that shard) | no — search stopped at first witness |
| 39 | a $k=5$ witness | `search/pancyc.c`, `search/hn_k5.csv` row (`tested=61561098`) | no |
| 40 | a $k=5$ witness, and (separately) the full set of extremal graphs | `search/hn_k5.csv` (first witness, `tested=132830426`); `search/gpu_pancyc.py --all`, `search/gpu-40-5-all.txt` (`tested=14373209608`, all 10 witnesses) | the `--all` run is exhaustive |
| 41 | $h(41)>5$ (elimination of all $k=5$ chord sets) and a $k=6$ witness | `search/gpu_pancyc.py`, `search/gpu-41-5d.txt` (`tested=17615450195`, `NONE`, cumulative across resumed runs); `search/localsearch.py`, `search/ls-41-6.txt` (witness) | the $k=5$ elimination is exhaustive; the $k=6$ witness search is not |

Every witness reported as a table entry in Section 2 was independently
reconfirmed by at least two of the three from-scratch verifiers
(`search/verify.py`, `papers/construction/check.py`,
`papers/construction/indep.c`); see `papers/REVIEW-search.md` for the exact
reconfirmation runs and lengths recovered. For $n=38,41$, the Lean proofs of
Section 3.3 add a fourth, kernel-checked confirmation.

**Independent corroboration of the search machinery itself**
(`papers/REVIEW-gpu-corroboration.md`, `papers/REVIEW-independent.md`, both
separate work re-checking the search code rather than re-deriving specific
witnesses): the GPU kernel's colex-unranking rule was independently
reimplemented and tested against direct binomial-coefficient computation with
`failures=0` across all tested combinations of $r\in\{2,3,4\}$ and
$M\in\{10,50,200,779\}$ (including a full exhaustive check at each size, not
just samples). A from-scratch direct-DFS cycle detector (`indep.c`, "not a
cycle-space basis, XOR, Gray code, or degree-mask test") independently
re-confirmed all three witnesses ($n=38,40,41$) and independently enumerated
$n=24$ (chunked by first-chord endpoint, $26{,}974{,}255$ sets tested,
$15$ raw witnesses reducing to exactly $2$ classes under dihedral symmetry)
and $n=25$ ($35{,}303{,}774$ sets tested, $0$ witnesses) — an independent
reproduction of Griffin's $k=4$ boundary at $n=24{\to}25$ using different code
than any of `pancyc.c`, `gpu_pancyc.py`, or `verify.py`. Two independent
2,000,000-sample random searches at $n=41,k=5$ (uniform random 5-subsets, not
exhaustive) found zero pancyclic graphs, while an identically-structured
positive control at $n=24,k=4$ found one on the first 2,000,000 samples —
demonstrating the random-sampling method can detect a true positive when one
exists, which is why its zero-hit result at $n=41$ is meaningful corroboration
(not proof) rather than a null result from a broken detector.

## 4. The subdivision lemma and why counting cannot suffice

The elementary argument behind every lower bound in this area (Bondy, Griffin,
Shi) is a pure counting bound: a $k$-chord Hamiltonian graph has at most
$2^{k+1}-1$ cycles (Shi's Corollary, via the cycle-space XOR structure in
Section 3.2), and a pancyclic graph on $n$ vertices needs at least $n-2$ of them,
so $2^{k+1}-1\ge n-2$. This alone gives $h(n)\ge\log_2(n-1)-1$ but nothing
stronger — one open question is exactly how much stronger the truth is. The
following reformulation (`notes/01-subdivision-reformulation.md`) shows precisely
where a counting-only argument runs out.

**Subdivision lemma.** Let $G=C_n+k$ chords, and let $e=uv$ be an edge of $C_n$.
Subdividing $e$ with $m$ new vertices adds $m$ to the length of every cycle
through $e$ and leaves cycles avoiding $e$ unchanged. Let $A$ be the set of
lengths of $G'$-cycles avoiding $uv$ and $B$ the set of lengths through $uv$;
subdividing gives $G$ cycle-length set $A\cup(B+m)$. Hence
$$h(n)\le k \iff \exists\, s<n,\ G'=C_s+k\text{ chords, an edge }uv\text{ of }C_s,\text{ such that}\ A\cup(B+(n-s))\supseteq[3,n].$$
(An earlier version of this lemma required $A\supseteq[3,s]$ and $B\supseteq[2s-n,s]$
*separately*; this was refuted by a computed counterexample — a genuinely
pancyclic $n{=}8,k{=}2$ graph none of whose three arcs satisfy that separate
split — and corrected to the single covering condition above, which holds for
*every* arc of a pancyclic $G$, not just a specially-chosen one, since
subdividing $G'$ back at $uv$ with $m=n-s$ vertices exactly reconstructs $G$.
See `papers/REVIEW-notes01.md` for the counterexample and the independent
re-verification of the correction.)

**Multigraph caveat.** If an arc's two endpoints are themselves joined by a
chord, contracting the arc makes that chord parallel to $uv$, and $B$ contains
the "digon" length $2$ — the actual $G$-cycle is the length-$(m{+}2)$ triangle
formed by the arc plus its closing chord.

**Consequence 1 (the counting bound is exactly tight at every recursive level).**
For each chord subset $K$ with both of Shi's two associated cycles present,
exactly one of them uses $uv$ (since $uv$ lies in exactly one of the two
alternating arc classes). So $|A|\le 2^k-1$ and $|B|\le 2^k$ — giving back
$s\le 2^k+1$, $n-s\le 2^k-1$, i.e. the trivial bound again, exactly balanced.
**Any improvement must come from arithmetic (which sums of gaps are
realisable), never from counting alone.** This part of the argument is
unaffected by the correction above.

**Consequence 2 (largest-arc bound, corrected).** Lengths $3,\dots,m+2$ cannot
be through-$uv$ cycles unless the arc's endpoints are chord-joined (a
through-$uv$ cycle needs length $\ge3$ in $G'$, hence $\ge m+3$ in $G$, *unless*
the digon above supplies a length-$(m{+}2)$ shortcut). So an arc whose
endpoints are **not** chord-joined has interior $m\le(n-2)/2$ (lengths
$3,\dots,m+2$ must all be avoiding-cycles, hence $m+2\le s=n-m$); an arc whose
endpoints **are** chord-joined has the looser bound $m\le(n-1)/2$. (The
earlier flat bound $m\le(n-3)/2$, independent of chord-adjacency, was refuted
by an explicit $n{=}8$ witness with a non-joined largest arc at $m=3>2.5$; that
same witness sits exactly at the corrected bound $m=(8-2)/2=3$. See
`papers/REVIEW-notes01.md`.) For the actual $n=38$ witness, the largest arc
($m=17$) is not chord-joined, so the applicable corrected bound is
$m\le(n-2)/2=18$, giving a general floor of $s\ge n-18=20$ — looser than the
$s\ge21$ this section previously (and the specific witness still) reports;
$s=21$ is the value realised by the actual discovered graph, not a value
forced by the general bound.

**Consequence 3 (large-length wall inequality).** Order the gap interior sizes
$m_1\ge m_2\ge\cdots$. The $j$ largest arcs cut $C_n$ into $j$ "stretches";
build the *stretch multigraph* with the stretches as vertices and one edge per
chord whose endpoints lie in different stretches, and let $c_j$ be its number
of connected components. A cycle of length $>n-m_j$ must use all $j$ largest
arcs, forcing its chord subset $K$ to place an even number of endpoints in
every stretch — i.e. $K$'s cross-stretch chords form an even subgraph of the
stretch multigraph. The number of even subgraphs of a multigraph with $E$
edges, $j$ vertices and $c_j$ components is $2^{E-j+c_j}$ (the standard
$\mathrm{GF}(2)$-cycle-space-dimension fact), and within-stretch chords are
free, so the number of qualifying $K$ is $2^{k-j+c_j}$; each qualifying $K$
yields at most one such long cycle (Shi's dichotomy), so $m_j\le2^{k-j+c_j}$
(pancyclicity needs $m_j$ distinct lengths above $n-m_j$, each needing its own
witnessing $K$). This argument is now complete and was independently
re-checked (`papers/REVIEW-notes01.md`, Addendum §5); an earlier pass had
flagged "the multigraph on the $j$ stretches" and $c_j$ as undefined, which the
definitions above resolve. Summing over $j$ recovers the trivial bound;
equality forces geometric gaps $m_j\sim2^{k-j+1}$ (the binary construction),
whose short lengths $3,\dots,2k$ are then missing and must be supplied by
cycles inside single stretches — the same chords have to serve both roles,
which is the tension a genuine improvement has to quantify. This is exactly
the two-scale shape observed empirically in the extremal graphs of Section 2.2
(three "geometric" gaps plus many gaps of size 1–2).

### Cycle-count context ($M(k)$)

Shi [Shi94] proves the universal ceiling $M(k)\le2^{k+1}-1$ (equality in the
matching lower bound for $k\le4$); Rautenbach and Stella [RS05] improve the
ceiling for $k\ge4$ and compute $M(k)$ exactly for $k=5,\dots,10$:

| $k$ | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $M(k)$ | 3 | 7 | 15 | 29 | 56 | 109 | 213 | 401 | 783 | 1484 |

(`papers/REPORT-cyclecounts.md`, transcribing Rautenbach–Stella's Figures 2–7 and
Shi's introduction.) For general (non-Hamiltonian) connected graphs with
cyclomatic number $r$, Entringer and Slater [ES81] conjecture the fixed-cyclomatic
maximum cycle count satisfies $\phi(r)\sim2^{r-1}$, having proved
$2^{r-1}\le\phi(r)\le2^r$; Aldred and Thomassen [AT08] sharpen the universal
ceiling to $C(G)\le\frac{15}{16}2^r$ for connected graphs and to a strictly
smaller planar bound. Substituting $r=k+1$, the Hamiltonian data above is
consistent with — but far too short a range to establish — the inherited
conjecture $M(k)/2^k\to1$ (`papers/REPORT-cyclecount-asymptotics.md`). No located
source proves this limit exists, equals $1$, or exceeds $1$.

## 5. Observations and questions

**Ratio to the trivial ceiling.** The threshold-to-ceiling ratio $t_k/2^{k+1}$ is
strictly decreasing over the only range where $t_k$ is known exactly:

| $k$ | 1 | 2 | 3 | 4 | 5 |
|---:|---:|---:|---:|---:|---:|
| $t_k$ | 5 | 8 | 14 | 24 | 40 |
| $2^{k+1}$ | 4 | 8 | 16 | 32 | 64 |
| $t_k/2^{k+1}$ | 1.25 | 1.00 | 0.875 | 0.75 | 0.625 |

(`notes/01-subdivision-reformulation.md`; $t_1=5>2^2=4$ only because $t_1$ counts
$n\le5$ with a single chord and the $k=0$ base case $n=3$ shifts the small-$n$
indexing, not because the ceiling is violated — $2^{k+1}-1$ bounds *cycles*, not
$n$ directly, and the exact relation $N_0=2^{k+1}+1$ used for this ratio already
accounts for that; see `papers/REPORT-cyclecounts.md`'s $N_0$ column, which gives
$5,9,17,33,65$ for $k=1..5$, matching $t_k$ only up to the counting bound's own
slack.)

**A Fibonacci fit with no known explanation.** Writing $\mathrm{Fib}(1)=\mathrm{Fib}(2)=1$,
$$t_k = 2\,\mathrm{Fib}(k+3)-2\qquad\text{for } k=2,3,4,5:$$
$$t_2=2\cdot5-2=8,\quad t_3=2\cdot8-2=14,\quad t_4=2\cdot13-2=24,\quad t_5=2\cdot21-2=40.$$
This is an **observation, not a theorem** — no structural reason for a Fibonacci
recursion in the threshold sequence is known, and it visibly fails at $k=1$
($2\,\mathrm{Fib}(4)-2=4\ne5$). If it continued it would predict
$$t_6 = 2\,\mathrm{Fib}(9)-2 = 2\cdot34-2 = 66,$$
i.e. $h(n)=6$ for $41\le n\le66$ and $h(67)\ge7$ — a falsifiable prediction that
the present search programs (`search/gpu_pancyc.py`, valid for $n\le60$; extending
to $n=66$ needs either a 128-bit port of the GPU kernel or the CPU program's
$n\le60,k\le6$ safe range pushed to $k=6$ at $n$ up to 66) could test directly.

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

**Wallis's monotonicity question.** W. D. Wallis's open-problem sheet presented
at IWOCA 2014 [Wa14] poses exactly two questions about $m(v)$: "1. Is it always
true that $m(v)\le m(v+1)$? (It is hard to imagine otherwise, but a proof would
be nice.) 2. Find a good upper bound for $m(v)$." The same sheet records a
correction to the literature worth preserving here: Sridharan (1978) had claimed
exact values of $m(v)$ for *all* $v$, but "they have been proven wrong; for
example, it is claimed that $m(13)=17$, but an example with $m(13)=16$ is given
in [George–Marr–Wallis 2013]" — consistent with Griffin's Table 1 value
$m(13)=16$ reproduced in Section 2 above. Wallis's Question 1 is the same
statement as Griffin's Conjecture 1 ($m(n)<m(n+1)$ for all $n\ge3$, non-strict in
Wallis's phrasing, strict in Griffin's), which Griffin proves only in the weaker
form $m(n+1)\le m(n)+2$ plus partial cases via an arc-contraction argument
(Proposition 3–4, Corollaries 2–3, [Gr13]). The data in Section 2 are consistent
with strict monotonicity throughout $3\le n\le41$ (every $m(n+1)>m(n)$ in the
table above), extending Griffin's own $n\le37$ check by four more values, but
four more data points do not constitute progress on the conjecture itself.
Wallis's Question 2, the companion upper-bound question, remains exactly at
George–Khodkar–Wallis's $\log_2n+\log_*n+O(1)$ [GKW16]; nothing in this paper
improves it.

## 6. Extremal structure and near-misses

This section collects, in one place, the concrete evidence this project has
gathered about how *fragile* pancyclicity is at every threshold examined so
far: known extremal/near-extremal graphs, and exactly how small a change
breaks them.

### 6.1 The five extremal 5-chord graphs at $n=40$ (recap)

Restating Section 2.2's data here for completeness: the exhaustive $n=40,k=5$
run (`search/gpu-40-5-all.txt`) finds exactly five classes of extremal graph
(ten raw witnesses under rotation, five under rotation+reflection), every one
with exactly one shared endpoint among its five chords, three "geometric" gaps
near $n/2,n/4,n/8$, and six gaps of size $1$–$2$; only $45$–$48$ of the
counting ceiling's $63$ possible cycles actually occur. See Section 2.2 for
the full per-graph table and the earlier-threshold ($n=8,14,24$) gap-profile
comparison.

### 6.2 From $n=24$ to $n=25$: every single-vertex extension fails

`papers/PROOF-n25-k4.md` (an attempted human-readable proof that no
$C_{25}+4$ chords is pancyclic — not completed, but backed by this concrete
computation) tested both $n=24$, $k=4$ extremal graphs supplied for that task,
$G_1=(0,2)(1,7)(2,5)(3,18)$ and $G_2=(0,2)(0,21)(1,19)(8,23)$, by inserting one
new vertex into *every* gap of each (8 insertions total) and checking
pancyclicity of the resulting $n=25$ graph with `search/verify.py`:

| graph | gap extended (interior size) | resulting $n{=}25$ chords | missing lengths |
|---|---|---|---|
| $G_1$ | $(3,5)$, $m{=}1$ | $(0,2)(1,8)(2,6)(3,19)$ | $4,7,11,23$ |
| $G_1$ | $(5,7)$, $m{=}1$ | $(0,2)(1,8)(2,5)(3,19)$ | $5,13,21$ |
| $G_1$ | $(7,18)$, $m{=}10$ (largest) | $(0,2)(1,7)(2,5)(3,19)$ | $15$ |
| $G_1$ | $(18,0)$, $m{=}5$ | $(0,2)(1,7)(2,5)(3,18)$ | $9,19$ |
| $G_2$ | $(2,8)$, $m{=}5$ | $(0,2)(0,22)(1,20)(9,24)$ | $9,19$ |
| $G_2$ | $(8,19)$, $m{=}10$ (largest) | $(0,2)(0,22)(1,20)(8,24)$ | $15$ |
| $G_2$ | $(19,21)$, $m{=}1$ | $(0,2)(0,22)(1,19)(8,24)$ | $5,13,21$ |
| $G_2$ | $(21,23)$, $m{=}1$ | $(0,2)(0,21)(1,19)(8,24)$ | $4,7,11,23$ |

**All eight fail.** The two graphs' failure patterns mirror each other exactly
(the same four missing-length sets, $\{4,7,11,23\}$, $\{5,13,21\}$, $\{15\}$,
$\{9,19\}$, each appearing once per graph) — evidence $G_1$ and $G_2$ are
related by a symmetry of the construction, not independent data points. The
single closest near-miss (only one length short) comes from extending each
graph's own *largest* gap (interior $10$ in both), missing only length $15$
both times; no clean formula for why $15$ specifically was found. This does
not prove $h(25)>4$ on its own (Griffin's computer search already establishes
that); it is concrete evidence of exactly how tightly these extremal
structures are balanced, and of the kind of "arithmetic of gaps" obstruction
`papers/PROOF-n25-k4.md` and `notes/01` both identify as the open crux of a
general proof.

### 6.3 A 6-chord upper bound: $t_6\ge56$, and a near-miss at the Fibonacci prediction

A dedicated search for 6-chord pancyclic graphs (`papers/REPORT-k6-upper.md`,
raw data in `search/k6/`) established:

* **Largest confirmed witness: $n=56$**, chords
  $(0,2)(0,53)(1,39)(20,39)(39,48)(48,53)$ — double-checked by two
  independent implementations (the constructing script's own check and the
  project's pre-existing `search/verify.py`), agreeing on all lengths
  $3,\dots,56$ (`search/k6/witnesses.csv`). So **$t_6\ge56$**, i.e.
  $h(n)\le6$ is now known for $n$ up to $56$ (previously only up to $41$).
* **The George–Khodkar–Wallis binary-shortcut recipe**, instantiated with
  5 shortcut chords $e_0{=}(0,2),e_1{=}(2,5),e_2{=}(5,10),e_3{=}(10,19),
  e_4{=}(19,36)$ plus one joining edge $(0,36)$ (6 chords total), was
  verified computationally to be pancyclic at **exactly $n=36$ and $n=40$**,
  and to be missing *only and exactly* length $5$ for every other $n$ in
  $[37,69]$ tested — a direct, computed confirmation of the construction
  theory's own claim that this stage needs to patch a small subset of short
  lengths (`papers/REPORT-k6-upper.md`, `search/k6/gkw-K4.txt`).
* **A direct, dedicated attempt at $n=66$** (the Section 5 Fibonacci
  prediction) — seeded from the $n=56$ witness, then 350s of strict-hill-climb
  search followed by exhaustive single-chord coordinate descent (every one of
  the 6 chords tried against every possible replacement, holding the other 5
  fixed, over 12,000 evaluations) — drove the missing-length count from $20$
  down to a confirmed local optimum of **3**, chords
  $(0,2)(0,48)(1,40)(11,41)(44,47)(47,52)$, **missing exactly
  $\{5,7,8\}$**. No single-chord change escapes this optimum; escaping would
  need a joint multi-chord move, a different starting family, or more search
  depth than this pass used.

## 7. References

- [Bo71] J. A. Bondy, "Pancyclic graphs I," *J. Combin. Theory Ser. B* 11 (1971),
  80–84.
- [Jia96] X. Jia, "Some extremal problems on cycle distributed graphs," *Congressus
  Numerantium* 121 (1996), 216–222. MR1431994.
- [Gr13] Sean Griffin, "Minimal Pancyclicity," arXiv:1312.0274 (2013).
- [GKW16] J. C. George, Abdollah Khodkar, W. D. Wallis, *Pancyclic and Bipancyclic
  Graphs*, Springer, 2016.
- [AK25] N. Alon, M. Krivelevich, "Sparse pancyclic subgraphs of random graphs,"
  *SIAM J. Discrete Math.* 39 (2025), 562–574 (arXiv:2308.01564).
- [Shi94] Y. Shi, "The number of cycles in a Hamilton graph," *Discrete Math.* 133
  (1994), 249–257.
- [RS05] D. Rautenbach, I. Stella, "On the maximum number of cycles in a
  Hamiltonian graph," *Discrete Math.* 304 (2005), 101–107.
- [ES81] R. C. Entringer, P. J. Slater, "On the maximum number of cycles in a
  graph," *Discrete Math.* 32 (1981), 305–321.
- [AT08] R. E. L. Aldred, C. Thomassen, "On the maximum number of cycles in a
  planar graph," *J. Graph Theory* 57 (2008), 255–264.
- [Wa14] W. D. Wallis, "Problems on Minimal Pancyclic Graphs," open-problem
  sheet presented at IWOCA 2014 (`papers/Wallis-2014-IWOCA-open-problems.pdf`).
- erdosproblems.com/1016 and its forum thread (comment by TerenceTao, 18 Oct
  2025) — current problem status; see `papers/REPORT-lit-4.md` for the full
  fetch and quotation.

*Every numeric claim in this draft is traceable to a project file; see
`papers/draft/SOURCES.md` for the complete number-to-source index.*
