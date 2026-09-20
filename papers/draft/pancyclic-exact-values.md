# Exact values of the minimum pancyclic edge count $m(n)$ for $3\le n\le 41$

**Authors:** AUTHORS TBD

## Abstract

A graph on $n$ vertices is *pancyclic* if it contains a cycle of every length
$3,4,\dots,n$. Let $m(n)$ be the minimum number of edges of a pancyclic graph on
$n$ vertices, and write $m(n)=n+h(n)$, where $h(n)$ counts the chords added to a
Hamilton cycle (Erdős Problem #1016, after Bondy 1971). Griffin (2013) determined
$m(n)$ exactly for $n\le 37$ by exhaustive and constructive search. We report
$m(n)$ for $38\le n\le 41$: $h(38)=h(39)=h(40)=5$ and $h(41)=6$, so
$m(38{:}41)=43,44,45,47$, and we then determine $h$ **exactly on a whole
range**: $h(n)=6$ for every $n$ with $41\le n\le67$, so $m(n)=n+6$ there.
Neither half assumes monotonicity of $h$. The lower half, $h(n)\ge6$ for all
$n\ge41$, is exhaustive: the shape/arc-length feasibility search of Section 3.5
refutes $k=5$ at every level from $n=41$ to $n=58$ with nothing abandoned, and
$58$ is the largest $n$ any $5$-chord configuration can reach, so no $n\ge41$
admits five chords. The upper half, $h(n)\le6$ for all $41\le n\le67$, is a
single explicit one-parameter family, $(0,2)(0,n{-}7)(1,13)(3,n{-}6)(4,31)(n{-}8,n{-}5)$,
whose cycle-length spectrum is $[3,32]\cup[n{-}34,n]$ — equal to $[3,n]$ exactly
when $n\le67$, which is why the family works to $67$ and fails at $68$ by the
single missing length $33$. The upper bounds are explicit chord sets found by
GPU/CPU chord search, each reconfirmed by three from-scratch verifiers and
by a kernel-checked Lean 4 proof. The lower bounds $h(n)\ge5$ follow from
Griffin's cycle-counting ceiling alone. The one new negative result,
$h(41)>5$, was first established by a complete GPU enumeration of all $5$-chord
sets on $C_{41}$ (a 64-bit kernel and its 128-bit port, which walk the same
enumeration), and has since been independently replicated by a structurally
different method: the shape/arc-length feasibility search of Section 3.5
enumerates subdivision shapes rather than chord sets, shares no code with the
GPU programs, and returns `sat=0 gaveup=0` at $n=41,k=5$ (Section 3.4). We record the
extremal $5$-chord graphs at the $n=40$ threshold, a subdivision lemma showing why
counting arguments can improve only the additive constant, never the growing
correction term the conjecture needs, and two observations on the threshold
sequence $t_k$ (largest $n$ with $h(n)=k$): its ratio to $2^{k+1}$ is strictly
decreasing over $k\le5$, and the four known values $t_2,\dots,t_5$ determine
$t_6$ not at all — every three-term integer linear recurrence fitting them
predicts a different $t_6$ (the whole family $66-2t$, $t\in\mathbb Z$), so no
pattern-fit on the known thresholds carries information about the next one.
Computation has since refuted the two members that had been singled out
($2\,\mathrm{Fib}(k+3)-2$, predicting $66$, and $2^{k-2}(10-k)$, predicting
$64$): the family above is pancyclic at every $n$ from $41$ to $67$, and
eleven separately found 6-chord graphs cover $n=57,\dots,67$, each re-checked
by an independent verifier, so $t_6\ge67$. The upper end is an exhaustive
result, not a counting one: the shape/CSP algorithm below refutes every $n$
from $89$ up to $111$, and $111$ is the largest $n$ any $6$-chord shape can
reach at all, so $t_6\le88$; the counting ceiling $129$ is now only a trivial
prior bound. A GPU implementation of the same shape reduction, with a pairwise
Hall prune and exhaustion claims re-derived by an independent tool, has since
refuted the three levels just above the family: no $6$-chord pancyclic graph
exists on $68$, $69$ or $70$ vertices. So $t_6=67$, the last value of the
family, unless a $6$-chord pancyclic graph exists at some $n$ with
$71\le n\le88$, a range the same pipeline is now deciding level by level. We
also describe the exact per-shape feasibility algorithm (a $C_n$ plus $k$
chords is a subdivision of one of finitely many multigraphs, so pancyclicity
becomes a covering problem in the arc lengths) that reproduces $t_2,t_3,t_4$
from scratch and is the tool behind both computations.

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
which is **not** Erdős Problem #1016 restated but one of the two
incompatible answers to it, and the one Erdős doubted. Jia's Conjecture 1.16
asserts that the error term $h(n)-\log_2 n$ is *bounded*; the belief recorded
for Erdős above — and the reason the problem is open — is that
$h(n)-\log_2 n\to\infty$, which is exactly the negation. The only upper bound
anyone claims to have proved, $\log_2 n+\log_* n+O(1)$, carries a correction
that grows, however slowly, and is consistent with the Erdős side but not with
Jia's $O(1)$. The two therefore cannot both hold, and this note states them as
a tension to be resolved, not as a pair of known facts: nothing here bears on
which side is right. (These statements were
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
search — stated in the paper's own body text as "for Hamiltonian graphs with at
most 4 chords and for Hamiltonian graphs with 5 chords and at most 31
vertices"[^griffin-cutoff] — with a 5-chord construction valid through $n=37$ for
the range beyond that exhaustive cutoff. Griffin's Table 1 is the earliest, and
until now the only, exact tabulation of $m(n)$ beyond the smallest cases.

[^griffin-cutoff]: Griffin's own abstract instead summarizes this as "an
    exhaustive search on graphs with up to 29 vertices"; the number 29 does not
    appear anywhere in the paper's body text, whose own statement (quoted above,
    `papers/1312.0274.txt`) gives 31, not 29, as the exhaustive cutoff for the
    5-chord case, and states no vertex cap at all for the $\le4$-chord case (that
    part is finite for a different reason: Corollary 1's cycle-count ceiling
    $2^{k+1}-1\ge n-2$ forces $n\le2^{k+1}+1=33$ for $k=4$, so no search beyond
    $n=33$ is needed regardless). This note quotes the body rather than the
    abstract, and records the discrepancy here rather than silently picking one,
    since a reader checking only the abstract would otherwise conclude this
    paper misread it; see `papers/REPORT-novelty-check.md` (Follow-up 3) and
    `papers/REPORT-griffin-method.md` for the full derivation.

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
| **41** | **6** | **47** | this project (`search/gpu-41-5.txt`, complete single-program elimination of $k=5$ - see Section 3.4 for its evidential status; `search/ls-41-6.txt`, $k=6$ witness) |

### 2.1 Thresholds

Let $t_k$ be the largest $n$ with $h(n)=k$. From the table above and Griffin's
Table 1:
$$t_1=5,\quad t_2=8,\quad t_3=14,\quad t_4=24,\quad t_5=40.$$
(Source: `notes/01-subdivision-reformulation.md`, "Update 2026-09-14 evening,"
consistent with Griffin Table 1 for $t_1..t_4$ and with this project's
exhaustive $n=41,k=5$ elimination for $t_5=40$.) The next threshold is not yet
known exactly, but it is pinned to one value or a short range:
$$t_6=67\quad\text{or}\quad 71\le t_6\le88.$$
The lower end comes from explicit 6-chord witnesses on every $n$ from $57$ to
$67$ (Section 6.3); the upper end from the exhaustive shape/CSP refutation of
the contiguous block $89\le n\le111$ (Section 3.5), in which $111$ is the
largest $n$ attainable by any $6$-chord shape; and the three levels just above
the family, $68\le n\le70$, are closed by the GPU exhaustion of Section 3.6,
which finds no $6$-chord pancyclic graph at any of them. The counting ceiling
$2^{k+1}+1=129$ at $k=6$ is superseded by this and is retained only as the
trivial prior bound. The levels $71\le n\le88$ are being decided by the
pipeline of Section 3.6, the even levels from $88$ downwards on one card and
level $71$ then the odd levels from $87$ downwards on the other; the first
witness found, if any, settles $t_6$, and if none is found then $t_6=67$.

**Between the two ends, $h$ is known exactly and unconditionally.**

$$h(n)=6\quad\text{for every }41\le n\le67,\qquad\text{so } m(n)=n+6
\text{ there.}$$

Both halves are established without any appeal to the monotonicity of $h$,
which remains open (Wallis's Question 1, Section 5).

* $h(n)\ge6$ for **all** $n\ge41$. The shape/CSP search of Section 3.5 answers
  `sat=0 gaveup=0` at $k=5$ for every level from $n=41$ to $n=58$
  (`search/shapecsp/level-k5-n41.txt` … `level-k5-n58.txt`, 18 levels,
  nothing abandoned), and $58$ is the largest $n$ any $k=5$ configuration can
  reach — the maximum number of distinct cycle forms over all $1236$ shapes is
  $56$, and a shape with $F$ forms is pancyclic only for $n\le F+2$
  (`search/shapecsp/shape-census.txt`). A contiguous clean block running to
  that ceiling excludes every $n$ at or above its foot, so no $n\ge41$ admits
  five chords. This supersedes the earlier position, in which $h(n)\ge6$ was
  known by exhaustive search only at $n=41$ and by counting only for $n\ge66$
  ($2^6-1=63<n-2$), with $42\le n\le65$ resting on monotonicity.
* $h(n)\le6$ for **all** $41\le n\le67$, from one family rather than from
  scattered witnesses: $(0,2)(0,n-7)(1,13)(3,n-6)(4,31)(n-8,n-5)$ is a valid
  $6$-chord graph and is pancyclic at every one of the $27$ values
  $n=41,\dots,67$ (Section 6.3; all $27$ re-checked here with
  `search/verify.py`, `papers/draft/verify-family-41-68-20260915.txt`).

The two halves meet exactly, so $h(n)=6$ on the whole range. The individual
witnesses of Section 6.3 remain the record of how the range was found, and
several of them are different graphs from the family member at the same $n$,
but they are no longer what carries the upper half.

### 2.2 The five extremal 5-chord presentations on 40 vertices (four graphs)

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

**Five presentations, four graphs.** The five rows are genuinely distinct as
*presentations* — no rotation or reflection of $C_{40}$ carries one to another,
which is what the search enumerates — but two of them are the same abstract
graph. Rows 4 and 5, $(0,4)(0,5)(1,34)(2,35)(3,15)$ and
$(0,7)(1,8)(2,10)(2,11)(9,21)$, are isomorphic; all other nine pairs are not
(checked here with `networkx.is_isomorphic` on all ten pairs). The isomorphism
does **not** carry row 4's Hamilton cycle to row 5's: under it two of row 4's
chords land on cycle edges of row 5's presentation, and two of row 5's cycle
edges become chords. That is the whole content of the coincidence — the graph
has more than one Hamilton cycle, and a different choice of Hamilton cycle
gives a different chord presentation of the same graph. So the count is
**ten labelled graphs, five dihedral classes, four isomorphism types**, and
the three numbers answer three different questions. Rows 1 and 2 realise $45$
cycles and rows 3–5 realise $48$, which is consistent: the cycle count is an
invariant, so rows 4 and 5 necessarily agree.

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
  (`gpu-state-{n}-{k}.json`) so a run can resume after interruption. The
  `tested=` figure it prints is the state file's cumulative candidate count;
  for $n=41,k=5$ that figure, `17615450195`, is exactly the number of
  candidate chord sets the three-mode case split generates
  ($\binom{778}{4}$ for mode A plus the mode-B and mode-C sums, recomputed
  independently in `papers/REPORT-record-integrity.md`), so it identifies a
  complete walk of the enumeration and nothing more. `search/gpu-41-5.txt`
  is the log of one uninterrupted such walk (progress lines from 0.4% to
  100.0%, then `NONE n=41 k=5 tested=17615450195 seconds=845`);
  `search/gpu-41-5d.txt` is an 18-second re-invocation that reloaded the
  finished state file and reprinted the same total. (An earlier draft
  described that total as "cumulative across resumed runs" and pointed to the
  `ABORTED`/`NONE` rows of `search/hn_k5.csv`; those rows belong to the CPU
  shard runner, not to this program — see Section 3.4.) Used for the full
  exhaustive $n=40$ run (`search/gpu-40-5-all.txt`) and the $n=41,k=5$
  elimination (`search/gpu-41-5.txt`).
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
  genuine fourth independent verification for $n=38,41$ specifically.

  `Erdos1016/Excess.lean` restates the result in this paper's own language:
  `PancyclicWithChords n k := ∃ cs : Finset (Sym2 (Fin n)), cs.card = k ∧
  (∀ e ∈ cs, e ∉ (baseCycle n).edgeSet) ∧ IsPancyclic (baseCycle n ⊔
  fromEdgeSet ↑cs)` — i.e. literally "$k$ non-cycle edges added to $C_n$ give
  a pancyclic graph," matching $h(n)\le k$ directly — and proves
  `pancyclicWithChords_38_5`/`pancyclicWithChords_41_6` from the same
  underlying witnesses via an explicit graph-equality lemma
  (`G38_eq`/`G41_eq`) rather than restating the hypothesis.
  `Erdos1016/Witness56.lean` gives `isPancyclic_G56` for the Section 6.3
  witness $(0,2)(0,53)(1,39)(20,39)(39,48)(48,53)$, and
  `Erdos1016/Witness39_40.lean` gives `isPancyclic_G39`/`isPancyclic_G40` for
  the $n=39,40$ witnesses, all by the same `ListCycle.lean` bridge.
  `Erdos1016/Excess2.lean` then restates all three in `PancyclicWithChords`
  form — `pancyclicWithChords_39_5`, `pancyclicWithChords_40_5`,
  `pancyclicWithChords_56_6` — via the same graph-equality technique as
  `Excess.lean`, so $n=38,39,40,41,56$ are now all stated in the paper's own
  $h(n)\le k$ language and kernel-checked, leaving only $n=38,41$ (Section
  3.3 above) additionally checked in the more primitive `IsPancyclic G38/G41`
  form as well. Independently re-verified in this session exactly as before:
  `lake build Erdos1016.Excess2` (which pulls in `Witness39_40.lean` and
  `Witness56.lean` transitively) completes with 0 errors
  (`Build completed successfully (8713 jobs)`; style-linter warnings only),
  and a fresh `#print axioms` on `pancyclicWithChords_38_5`,
  `pancyclicWithChords_39_5`, `pancyclicWithChords_40_5`,
  `pancyclicWithChords_41_6`, and `pancyclicWithChords_56_6` all report
  exactly `[propext, Classical.choice, Quot.sound]`.

  Since 2026-09-20 the whole upper half of the range result is kernel-checked
  as well: `Erdos1016/Family.lean` proves
  `family_pancyclic_41_67 : ∀ n, 41 ≤ n → n ≤ 67 → PancyclicWithChords n 6`
  from 27 per-level certificates `Erdos1016/Family/W41.lean` .. `W67.lean`,
  in which the family $F_n$ of Section 6.3 is given one explicit vertex list
  per cycle length and Lean re-derives by `decide` that each list is a cycle
  of the stated length in the stated graph, that the six chords are distinct
  non-cycle edges, and that the Bool adjacency equals `baseCycle n ⊔
  fromEdgeSet cs`. `lake build` is clean (8743 jobs, no `sorry`) and
  `Axioms.lean` reports `[propext, Classical.choice, Quot.sound]` for the
  range theorem and for every certificate. The lists were generated by
  `search/k6/gen_family_lean.py` and are certificates only; nothing computed
  by that script is trusted. Every non-existence result in this note remains
  computational (Sections 3.4, 3.5 and 3.6).

### 3.4 Which program established which bound

For every $n$ in $38..41$, the *lower bound* $h(n)\ge5$ needs no new search at
all: Griffin's Corollary 1 gives an absolute ceiling of $2^{k+1}-1$ cycles for
a $k$-chord Hamiltonian graph, so $k=4$ permits at most $2^5-1=31$ cycles,
while pancyclicity on $n$ vertices needs $n-2$ distinct lengths. For
$n=38,\dots,41$, $n-2\ge36>31$, so pure counting alone already rules out
$k=4$ (and every $k<4$, since $M(k)$ is increasing) — this is airtight on its
own and does not additionally rely on how far Griffin's own exhaustive $k\le4$
search was run, which the paper does not state was unbounded (nor could it
be). What this project newly supplies is:

| $n$ | what was newly established | program / file | exhaustive? |
|---:|---|---|---|
| 38 | a $k=5$ witness (upper bound $h(38)\le5$, hence $=5$) | `search/pancyc.c`, shard search, `search/n38k5-A0.txt` (witness found after `tested=52296703` in that shard) | no — search stopped at first witness |
| 39 | a $k=5$ witness | `search/pancyc.c`, `search/hn_k5.csv` row (`tested=61561098`) | no |
| 40 | a $k=5$ witness, and (separately) the full set of extremal graphs | `search/hn_k5.csv` (first witness, `tested=132830426`); `search/gpu_pancyc.py --all`, `search/gpu-40-5-all.txt` (`tested=14373209608`, all 10 witnesses) | the `--all` run is exhaustive |
| 41 | $h(41)>5$ (no $5$-chord set on $C_{41}$ is pancyclic) and a $k=6$ witness | elimination: `search/gpu_pancyc.py`, `search/gpu-41-5.txt` (one complete walk, `NONE n=41 k=5 tested=17615450195 seconds=845`; `search/gpu-41-5d.txt` is a re-invocation reprinting the finished state); witness: `search/localsearch.py`, `search/ls-41-6.txt` | the $k=5$ elimination is one complete enumeration by one program — see "What is multiply confirmed" below; the $k=6$ witness search is not exhaustive |

**What is multiply confirmed, and what is not.** The evidence behind the four
new values is of two different kinds and should not be read as one.

*Witnesses (every upper bound; all of $h(38),h(39),h(40)\le5$ and
$h(41)\le6$).* Each witness chord set in Section 2 is an explicit object that
any program can check. Each was independently reconfirmed by the three
from-scratch verifiers of Section 3.3 — `search/verify.py` (networkx
`simple_cycles`), `papers/construction/check.py` (a second cycle-space
implementation) and `papers/construction/indep.c` (direct DFS, no cycle
space) — see `papers/REVIEW-search.md` and `papers/REVIEW-independent.md` for
the runs and the length sets recovered — and, for all of $n=38,39,40,41$ (and
$56$), by a kernel-checked Lean 4 proof (`pancyclicWithChords_38_5` …
`_41_6`, Section 3.3). These claims are multiply and independently confirmed.

*The lower bounds $h(n)\ge5$ for $n=38..41$.* Pure counting, as shown at the
top of this subsection; no search is involved.

*The non-existence result $h(41)>5$.* This is the only new negative claim,
and the only place in $n=38..41$ where the threshold moves. Unlike a
witness, it cannot be checked by inspecting an object; it can only be
re-established by another complete enumeration. Its present evidential
status, read directly from the artifacts, is:

* It **is** established by one complete enumeration: `search/gpu-41-5.txt`
  logs `search/gpu_pancyc.py` walking mode A from 0.4% to 100.0% and then
  printing `NONE n=41 k=5 tested=17615450195`, and `17615450195` is exactly
  the candidate count of the three-mode case split (Section 3.3), so the walk
  was complete, not truncated.
* The second `NONE` run is **not** an independent replication of it.
  `search/k6/gpu128-41-5.txt` (`NONE n=41 k=5 tested=17615450195`) is
  `search/k6/gpu_pancyc128.py`, whose own docstring describes it as a
  "128-bit (two-word) port of `search/gpu_pancyc.py` … Nothing else about the
  algorithm changes." The identical `tested=` total shows the two programs
  walk the identical enumeration; this is a check on 64-bit mask overflow,
  not on a logic error that both would share.
* It **is** independently replicated, by a structurally different method.
  The shape/CSP algorithm of Section 3.5 decides the same question without
  enumerating chord sets at all: it enumerates the $1236$ subdivision shapes
  on $k=5$ chords and asks, per shape, whether integer arc lengths exist whose
  cycle forms cover $[3,41]$. Its answer is
  `LEVEL k=5 n=41 shapes=1236 eligible=308 sat=0 gaveup=0`
  (`search/shapecsp/level-k5-n41.txt`): of the $1236$ shapes, $308$ survive the
  two necessary conditions applied at the cutoff (the per-shape cap
  $n\le F+2$, and the interval-Hall test), all $308$ are decided
  infeasible, and `gaveup=0` means none was abandoned on the node budget, so
  none is UNKNOWN. A single level suffices here, unlike the $k=6$ upper bound
  of Section 3.5, precisely because the question is about one value of $n$:
  Hall is a necessary condition evaluated at that same $n=41$, so any shape
  feasible at $41$ is eligible at the $n=41$ level and was searched there.
  The two programs share no code — different enumeration (shapes versus
  chord sets), different search (arc-length branch-and-bound versus GPU mask
  walk), different language — and every SAT the method reports is
  re-materialised as a graph and re-tested by `verify.check_record` rather
  than trusted, with a false-negative control on known witnesses
  (`papers/REPORT-shape-csp.md`).
* The CPU shard run — the one structurally separate exhaustive path that was
  attempted — did not complete: `search/hn_k5.csv` records
  `41,5,ABORTED-no-output-processes-died,,8044,0`, and its shard outputs
  `search/sh-41-A0.txt` … `sh-41-A7.txt`, `sh-41-BC.txt` are all zero bytes.
  Two later rows in the same file recorded `NONE` with `tested=0` (the shard
  runner's default when every process exits without output); they test no
  candidates, are not evidence, and are re-labelled `INVALID-NONE-…` in the
  file (`search/hn_k5-README.md`).
* The from-scratch direct-DFS GPU replication
  (`papers/construction/indep_gpu.py`, `papers/REVIEW-independent-gpu.md`)
  is unfinished: a corrected contiguous prefix of $739{,}246{,}080$ of the
  $15{,}147{,}912{,}850$ mode-A ranks (under 5% of one of the three modes)
  with $0$ hits, and, in that review's words, "the exhaustive b=2 total
  remains UNKNOWN pending continuation from the corrected checkpoint."
* Non-exhaustive corroboration exists: $2{,}000{,}000$ uniformly random
  $5$-subsets checked by `indep.c` with $0$ hits, against a positive control
  that does find a witness at $n=24,k=4$ (next paragraph).
* Nothing about this negative result is formalised in Lean; the project's
  `Axioms.lean` states that the lower bounds "are NOT formalised here; they
  rest on the exhaustive search programs in `search/`."

So $h(41)=6$ rests on two complete and structurally unrelated exhaustive
arguments for its lower half: the GPU chord-set enumeration, and the
shape/arc-length CSP. That is the footing the witnesses have — two methods
that would have to fail in the same direction for the result to be wrong —
and it is a stronger position than this draft reported before the replication
landed. Two qualifications are kept. First, the 128-bit run remains a port,
not a third method, and is still counted as one. Second, the from-scratch
direct-DFS GPU replication (`indep_gpu.py`) is still unfinished; it would be a
third independent exhaustive run, and completing it remains worthwhile, but
$h(41)>5$ no longer depends on it.

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

### 3.5 The shape/CSP exact algorithm (`search/shapecsp/`)

The searches above enumerate chord *sets* on a fixed $C_n$, one $n$ at a
time, which is why they stop being exhaustive near $n=41$ for $k=5$. A
second, structurally different exact method decides $t_k$ directly and is
the tool intended to settle $t_6$ (`papers/REPORT-shape-csp.md`; code in
`search/shapecsp/`, untouched by the $k=6$ witness searches of Section 6.3).

*Reformulation.* A $C_n$ plus $k$ chords is a subdivision of a fixed
multigraph $H$: a cycle on the $b$ distinct chord endpoints in their cyclic
order, plus the $k$ chords as edges on those $b$ points, with $b\le2k$ and
every point carrying at least one chord (`search/shapecsp/shapes.py`,
`shapes(k)`, enumerated up to the dihedral group $D_b$ over *all* $b$,
including the degenerate families in which chords share endpoints). Call
$H$ the *shape*. Suppressing the degree-2 vertices makes the $b$ arc lengths
$a_1,\dots,a_b\ge1$ free integer variables with $\sum a_i=n$, and every cycle
$f$ of $H$ (there are at most $2^{k+1}-1$; the cycle space of $H$ has
dimension $k+1$) has length that is a $0/1$ linear form
$L_f(a)=\sum_{i\in A_f}a_i+|X_f|$ in the arcs, where $A_f$ is the set of arcs
$f$ uses and $X_f$ its chords (`cycle_forms(b, chords)`). Pancyclicity of the
subdivided graph is then exactly the statement that the forms
$\{L_f\}$ cover every value in $[3,n]$, so $h(n)\le k$ becomes a finite
per-shape feasibility problem in $b$ integer unknowns, and $t_k$ is the
largest $n$ at which any shape is feasible. This is the same reduction
George–Marr–Wallis carry out by hand for $k\le3$ (Section 1; GMW13 write
cycle lengths as linear functions of arc lengths such as "$a+b+1$, $c+d+1$"
and, for three chords, "There are 14 types of graph: AAAi, AAAii, AABi,
AABii, AAC, ABBi, ABBii, ABC, ACC, BBBi, BBBii, BBC, BCC, CCC" — quoted in
`papers/REPORT-griffin-method.md`). The enumeration here reproduces that
count: `shapes(3)` yields exactly **14** shapes (`search/shapecsp/shape-census.txt`,
row "3 | 14 | 5 | 9 | 3..6"), of which 5 are perfect matchings on $2k=6$
points and 9 are degenerate; the counts for $k=2,4,5,6$ are $3,103,1236,21878$
(the $k=6$ shapes being 97.5% degenerate). A per-shape cap falls out of the
reformulation at once: each cycle realises one length, so a shape with $F$
distinct cycle forms can be pancyclic only for $n\le F+2$. The largest cap at
$k=6$ is $111$, already below the counting ceiling $129$, and the largest
number of cycles over all shapes is $7,15,29,56,109$ for $k=2,\dots,6$ —
exactly the Rautenbach–Stella values $M(k)$ of Section 4, recovered here
independently.

*Solvers.* Two deliberately independent decision procedures are used per
shape: a CP-SAT model (`search/shapecsp/solve.py`, ortools) and a C
branch-and-bound over the arcs (`search/shapecsp/bb.c`) whose prune confines
every form to an interval and then decides, by an exact greedy matching,
whether the intervals can still saturate $[3,n]$ (an earlier interval-Hall
prune was found *not* equivalent to the exact test — a counterexample at
$n=8$ is recorded in `papers/REPORT-shape-csp.md` — and is retained only as a
necessary-condition pre-filter). `sweep.py`/`level.py` drive the search with
$n$ descending from the largest per-shape cap; the first $n$ with a feasible
shape is $t_k$, and every level above it that answers infeasible with zero
`gaveup` (no node-cap abandonment) is the exhaustive refutation.

*Controls.* Run with no lower bound supplied, the method reproduces
$t_2=8$, $t_3=14$ and $t_4=24$ from scratch with `gaveup_records=0` at every
level (`papers/REPORT-shape-csp.md`, "Positive control"; witnessing shapes
and arc vectors are listed there, e.g. $t_4=24$ from the degenerate $b=7$
shape $((0,2),(0,5),(1,4),(3,6))$ with arcs $1,2,2,11,6,1,1$, i.e.
$C_{24}+(0,2)(1,5)(1,7)(3,18)$). $t_2,t_3,t_4$ are reproduced by *both*
solvers, and CP-SAT independently finds the $k=5$ lower bound $n=40$. The
reformulation itself is checked against ground truth rather than trusted:
for 201 random (shape, arc-length) pairs across $k=2..5$ the multiset of
lengths predicted by the forms is compared with `networkx.simple_cycles` on
the materialised graph, with 0 mismatches, and every reported optimum is
re-checked the same way (`verify.check`).

*Gate suite.* `search/shapecsp/test_shapecsp.py` asserts behaviour by calling
`shapes()`, `t_k()`, `cycle_forms()` and `verify.check()` with values and
comparing answers, and it is mutation-tested. Restricting the enumeration to
the non-degenerate $b=2k$ shapes (in `shapes.py`, `rng = [2*k]` in place of
`range(lo, 2*k+1)`) turns the suite **red** — `FAIL t_4 == 24 :: got 22`
plus three further failures, exit 1 (`search/shapecsp/gates-red.txt`) —
because the $k=4$ optimum lives at $b=7$ and the perfect-matching-only model
returns the wrong maximum ($22$, not $24$); restoring the file turns it
**green** — `ALL GATES PASS`, exit 0 (`search/shapecsp/gates-green.txt`; the
suite was re-run during this revision and passed, 41 s). The same defect is
not academic at $k=6$: the $n=56$ witness of Section 6.3 has only 7 branch
vertices (vertex 39 carries three chords), so a perfect-matching-only
enumeration would not contain it.

*What a level does and does not establish.* A level at cutoff $n$ hands each
shape to the solver with $n$ as a lower cutoff, so `sat=0` means no shape it
searched admits any value $\ge n$. Eligibility, however, is decided *at* the
cutoff by two necessary conditions — the per-shape cap and the interval-Hall
test — and Hall at cutoff $n$ is not monotone in $n$: a shape can fail it at
$n$ and still be feasible at some larger $n_0$, in which case that level never
searched it. A single clean level therefore does not by itself exclude all
larger $n$. What does is a *contiguous block* of levels
$n,n+1,\dots,N_{\max}$, all returning `sat=0` with `gaveup=0`, where
$N_{\max}$ is the largest cap over all shapes: a shape feasible at any $n_0$
in that range is eligible at the level whose cutoff is exactly $n_0$, because
Hall is necessary at that same $n_0$, and that level refuted it. For a
statement about a single $n$ — such as $h(41)>5$ — the single level at that
$n$ is enough, for the same reason. This distinction is enforced in
`search/shapecsp/level.py`'s own docstring ("Cite the block, never a single
level"), and an earlier misreading of it is recorded and corrected in
`papers/REPORT-shape-csp.md`.

*Status.* The $k=5$ ladder log (`search/shapecsp/k5-levels.log`) records
`sat=0 gaveup=0` at every level from $n=58$ (the largest $k=5$ per-shape cap)
down to $n=41$, with `eligible` shapes at each level from $54$ down. Taken
with the $n=40$ feasibility found by CP-SAT, that is an independent derivation
of $t_5=40$ by a method sharing no code with Section 3.3's programs; its
$n=41$ level is the independent replication of $h(41)>5$ reported in
Section 3.4. At $k=6$ the ladder is complete over the whole range above the
witnesses: every level from $N_{\max}=111$ down to $n=94$ answers `sat=0`
with `gaveup=0` — levels $111$ down to $102$ with `eligible=0`, killed by the
cap and Hall bounds without any search, and levels $101$ down to $94$ with
every eligible shape decided (`search/shapecsp/level-k6-n94.txt` …
`level-k6-n111.txt`; the aggregate `search/shapecsp/k6-levels.log` is missing
the $n=94$ and $n=95$ rows, which were run separately and are recorded in
their own per-level files). The descent has since
closed the five levels below it the same way: $n=93$ (114 eligible shapes, all
UNSAT, `REPORT-k6-level93-verify.md`), $n=92$ (152 of 152 UNSAT, with an
independent re-enumeration differing in nothing, `REPORT-k6-level92-verify.md`)
and $n=91,90,89$ (all UNSAT, enumeration diff $0$, the same `bb` build as the
block above, `REPORT-k6-level89-91-verify.md`; the run itself is documented in
`papers/REPORT-k6-descent.md`). The $0$-byte `level-k6-n92.txt` and
`level-k6-n93.txt` in `search/shapecsp/` are the abandoned first attempts at
those two levels and are not the evidence. The contiguous block is therefore
$89\le n\le111$ and is what gives $t_6\le88$; no single level in it is
redundant. Below $89$ the per-level branch-and-bound grows too expensive for
one CPU, and the levels $68$ to $88$ are handled by the GPU pipeline of the
next subsection.

### 3.6 GPU exhaustion of the levels between the family and the block (`search/shapecsp/pairwise/`)

Between the witnesses at $n\le67$ and the CPU block at $n\ge89$ the same shape
reduction is run on GPUs, one level at a time, with the per-shape question
decided by enumeration rather than branch-and-bound. The census of a level
(`census_level.py`: the enumeration of the $21{,}878$ shapes of Section 3.5,
restricted to the shapes whose cap and interval-Hall test admit that $n$, and
reproducing the earlier $n=68,69,70$ manifests byte for byte) lists, per
shape, the arc lower bounds and the cycle forms; every composition of the arc
lengths summing to $n$ is then tested on the GPU against the forms, one thread
per prefix of the composition, the last two arcs enumerated in-thread with two
64-bit coverage words. Two facts make the count feasible. Shapes with at most
$10$ branch vertices are enumerated unrestrictedly. For $b=11,12$ the
enumeration is restricted to the *pairwise-admissible* set $A$: the
interval-Hall test is necessary for pancyclicity and monotone in the arc lower
bounds, so raising any two lower bounds to the values a pancyclic composition
takes keeps it true, and every pancyclic composition therefore lies in
$A=\{a:\ \sum_i a_i=n,\ \text{low}\le a\le\text{high},\ a_j\le T[i][j][a_i]\ \text{for every ordered pair }(i,j)\}$,
which per-shape tables enumerate exactly and which admits one composition in
roughly $42$ to $47$ at $b=12$ and one in $10$ to $15$ at $b=11$
(`search/shapecsp/pairwise/SPEC.md`). Every unit of work records the number of
compositions it visited; a level is claimed exhausted only when an independent
tool, run from a frozen snapshot of the code, re-derives the unit set of every
tier from the hashed census manifest and finds every unit present and none
extra, and, for the pairwise tiers, rebuilds every shape's tables from its
census row with matching hashes and finds the visited counts equal to the
manifest totals shape by shape. Controls: the runner refuses to start unless
the known witnesses at $n=56$ and $n=67$ are found at their ranks and sampled
ranks unrank identically on CPU and GPU; and a blind run of the whole pipeline
over the whole of level $67$, every shape and every $b$, found the family
member $F_{67}$ at its shape ($b=11$, shape $20889$) and nothing else
(`papers/verification/control-n67-b*.json`).

*Result.* Levels $68$, $69$ and $70$ are exhausted with zero hits in every
tier: $21$ claim files under `papers/verification/`, rendered and totalled in
`papers/REPORT-k6-gpu-pairwise-68-70.md`, with the independent review of the
prune, the tables, the kernel and the claim tool in
`papers/REPORT-review-pairwise.md`. Hence $h(68)=h(69)=h(70)\ge7$, the first
three levels above the family, and $t_6\notin\{68,69,70\}$. The levels
$71\le n\le88$ are being run by the same pipeline
(`papers/REPORT-k6-gpu-descent-71-88.md`, regenerated from the claim files as
they land), each card working downwards so that the first witness found, if
any, is $t_6$ itself; if none is found, $t_6=67$.

## 4. The subdivision lemma, and what counting can and cannot give

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
alternating arc classes); the one exception is $K=\varnothing$, whose only
possible cycle is the full Hamilton cycle itself, which always uses $uv$ and
so can only ever land in $B$, never $A$. Summing over the $2^k$ subsets with
this one adjustment gives $|A|\le 2^k-1$ and $|B|\le 2^k$ — hence
$s\le 2^k+1$, $n-s\le 2^k-1$, i.e. the trivial bound again, exactly balanced.
This part of the argument is unaffected by the correction above.

**What this does and does not say about counting.** Since nested chords
already realise at least $2^k$ cycles, any refinement of the form
$n-2\le M(k)$ for the true maximum cycle count $M(k)$ inverts to
$h(n)\ge\log_2(n-1)-1+O(1)$: because $M(k)=\Theta(2^k)$ under *any* such
refinement (only the lower-order terms change), inverting it can only ever
adjust the additive constant, never produce a term that grows without bound
in $n$. So **cycle counting can, and does, improve the constant** — Shi's and
Rautenbach–Stella's sharper exact values for $M(k)$ (below) are real
improvements of exactly this kind — **but it can never by itself supply the
$\log_* n$-type growing correction** the full conjecture asks for. This is a
narrower and more defensible claim than "counting never helps," and it is
consistent with, rather than contradicted by, the Rautenbach–Stella result
cited next.

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
exist at every $n$ from $57$ to $67$ (chord sets in Section 6.3), and the
family $F_n$ of Section 6.3 is pancyclic at every $n$ from $41$ to $67$, so
$$t_6=67\quad\text{or}\quad 71\le t_6\le88.$$
The upper end is the exhaustive shape/CSP block of Section 3.5: every level
from $n=89$ to $n=111$ answers `sat=0` with zero abandoned searches
(`search/shapecsp/level-k6-n94.txt` ... `level-k6-n111.txt` for the block
closed first; `REPORT-k6-level93-verify.md`, `REPORT-k6-level92-verify.md` and
`REPORT-k6-level89-91-verify.md` for the descent that extended it down to
$89$), and $111$ is the largest $n$ any $6$-chord shape admits, so no
$6$-chord pancyclic graph exists on $89$ or more vertices. It supersedes the
trivial counting ceiling $129=2^{6+1}+1$ ($N_0$ in
`papers/REPORT-cyclecounts.md`'s notation), which is kept here only as the
prior bound this computation replaced. The three levels just above the family,
$n=68,69,70$, are exhausted by the GPU pipeline of Section 3.6 with no witness.
What the computation does to the family is sharper than "refutes it," and an
earlier revision of this note over-claimed here. The bracket removes the
members at both ends and leaves a middle band. A member predicting $66-2t$ is
refuted from below whenever $66-2t<67$, i.e. for every $t\ge0$: that kills the
predictions $66,64,62,\dots$, and with them **both named fits** (Fibonacci at
$66$, the rival at $64$). It is refuted from above whenever $66-2t>88$, i.e.
for every $t\le-12$, and the members $t=-1$ and $t=-2$, predicting $68$ and
$70$, fall to the level exhaustions of Section 3.6. What survives is the nine
members with $-11\le t\le-3$, predicting $t_6\in\{72,74,\dots,88\}$. An odd
witness does not by itself refute the family: a witness at $n=67$ shows
$t_6\ge67$, which is consistent with a prediction of $72$. Every surviving
member falls at once if $t_6$ turns out to be *odd*, and in particular if
$t_6=67$. The family $(0,2)(0,n-7)(1,13)(3,n-6)(4,31)(n-8,n-5)$ that
establishes $h(n)\le6$ on all of $41\le n\le67$ has spectrum
$[3,32]\cup[n-34,n]$, so it covers $[3,n]$ exactly while $n\le67$ and misses
exactly the single length $33$ at $n=68$ (Section 6.3), and Section 3.6 shows
that nothing else works at $68$, $69$ or $70$ either. $t_6=67$ is therefore
the value unless a $6$-chord pancyclic graph exists at some $n$ in $71..88$;
the GPU pipeline of Section 3.6 is deciding those eighteen levels now, and the
first witness it finds, if any, is $t_6$.

**Wallis's monotonicity question.** W. D. Wallis's open-problem sheet presented
at IWOCA 2014 [Wa14] poses exactly two questions about $m(v)$: "1. Is it always
true that $m(v)\le m(v+1)$? (It is hard to imagine otherwise, but a proof would
be nice.) 2. Find a good upper bound for $m(v)$." The same sheet records a
correction to the literature worth preserving here: Sridharan (1978) had claimed
exact values of $m(v)$ for *all* $v$, but "they have been proven wrong; for
example, it is claimed that $m(13)=17$, but an example with $m(13)=16$ is given
in [GMW13]" — consistent with Griffin's Table 1 value
$m(13)=16$ reproduced in Section 2 above. Wallis's Question 1 is the same
statement as Griffin's Conjecture 1 ($m(n)<m(n+1)$ for all $n\ge3$, non-strict in
Wallis's phrasing, strict in Griffin's), which Griffin proves only in the weaker
form $m(n+1)\le m(n)+2$ plus partial cases via an arc-contraction argument
(Proposition 3–4, Corollaries 2–3, [Gr13]). The data in Section 2 are consistent
with strict monotonicity throughout $3\le n\le41$ (every $m(n+1)>m(n)$ in the
table above), extending Griffin's own $n\le37$ check by four more values, but
four more data points do not constitute progress on the conjecture itself.
Wallis's Question 2, the companion upper-bound question, remains at the
$\log_2n+\log_*n+O(1)$ bound reportedly proved in [GKW16] (see Section 1's
caveat on how that attribution is sourced); nothing in this paper improves it.

## 6. Extremal structure and near-misses

This section collects, in one place, the concrete evidence this project has
gathered about how *fragile* pancyclicity is at every threshold examined so
far: known extremal/near-extremal graphs, and exactly how small a change
breaks them.

### 6.1 The five extremal 5-chord presentations at $n=40$ (recap)

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

### 6.3 One family gives $h(n)\le6$ on all of $41\le n\le67$; $t_6\ge67$

A dedicated search for 6-chord pancyclic graphs (`papers/REPORT-k6-upper.md`
for the first phase, `papers/REPORT-k6-gpu-joint.md` for the GPU
joint-neighbourhood sweeps, raw data in `search/k6/`) established:

* **Largest confirmed witness: $n=67$**, chords
  $(0,2)(0,60)(1,13)(3,61)(4,31)(59,62)$ — confirmed by `search/verify.py`
  (`search/k6/verify-67-gpu-joint.txt`, "pancyclic [3, 4, ..., 67]"), by the
  reference cycle-space evaluator `search/k6/cyclespace.py check`
  ("pancyclic missing=[]"), by the GPU kernel's direct evaluation with the
  $n=67$ near-miss $(0,2)(0,64)(1,13)(3,63)(4,31)(59,64)$ as a same-session
  negative control, and by a separately written cycle-space evaluator run
  with a known witness and a known near-miss as controls. So **$t_6\ge67$**,
  i.e. $h(n)\le6$ is now known for $n$ up to $67$ (previously $56$ in this
  note's earlier revisions, and $41$ before that).
* **Witnesses at every $n$ from $57$ to $67$**, all re-checked with
  `search/verify.py` in this revision (`papers/draft/verify-rerun-20260914.txt`,
  every row "pancyclic", missing $[\,]$):

  | $n$ | chords | found by |
  |---:|---|---|
  | 57 | $(0,2)(0,54)(1,40)(14,48)(40,49)(49,54)$ | coordinate descent, `search/k6/coord-57.txt` |
  | 58 | $(0,2)(0,55)(1,41)(14,49)(41,50)(50,55)$ | `search/k6/smart-57-70.txt` |
  | 59 | $(0,2)(0,56)(1,42)(16,48)(42,51)(51,56)$ | `search/k6/smart-57-70.txt` |
  | 60 | $(0,2)(0,57)(1,43)(19,44)(43,52)(52,57)$ | `search/k6/smart-57-70.txt`, `search/k6/climb-60-72.txt` |
  | 61 | $(0,2)(0,58)(1,44)(3,57)(28,53)(53,58)$ | CPU 2-of-6 slot sweep, `search/k6/sweep2-61-34.txt` ("IMPROVE n=61 missing=0") |
  | 62 | $(0,2)(0,59)(1,11)(3,58)(3,28)(54,59)$ | insertion + ILS + joint-2 sweep, `search/k6/witnesses-v2.csv` |
  | 63 | $(0,2)(0,60)(1,11)(3,59)(3,28)(55,60)$ | insertion + ILS + joint-2 sweep, `search/k6/witnesses-v2.csv` |
  | 64 | $(0,2)(0,61)(1,12)(3,60)(4,29)(56,61)$ | insertion + ILS + joint-2 sweep, `search/k6/witnesses-v2.csv` |
  | 65 | $(0,2)(0,58)(1,13)(3,59)(4,31)(57,60)$ | member of the family below, `search/k6/witnesses-v2.csv` |
  | 66 | $(0,2)(0,59)(1,13)(3,60)(4,31)(58,61)$ | GPU 3-of-6 sweep around the near-miss $(0,2)(0,63)(1,13)(3,62)(4,31)(58,63)$, `search/k6/witnesses-v2.csv` |
  | 67 | $(0,2)(0,60)(1,13)(3,61)(4,31)(59,62)$ | lift of the $n=66$ structure by one vertex, `search/k6/witnesses-v2.csv` |

  These eleven are the record of how the range was found, one $n$ at a time,
  and the earlier witnesses at $n\le56$ (`search/k6/witnesses.csv`, including
  the $n=56$ graph $(0,2)(0,53)(1,39)(20,39)(39,48)(48,53)$ that is also
  kernel-checked in Lean, Section 3.3) fill the rest. They are no longer what
  carries $h(n)\le6$: the single family in the next bullet does that for the
  whole range at once.
* **One family covers the entire range $41\le n\le67$.** Write
  $$F_n=(0,2)\,(0,n-7)\,(1,13)\,(3,n-6)\,(4,31)\,(n-8,n-5),$$
  with the two "inner" chords $(1,13)$ and $(4,31)$ fixed and the other four
  sliding with $n$. $F_n$ is a legitimate $C_n$ plus six chords for every
  $n\ge41$ (six distinct pairs, none of them a cycle edge), and it is
  **pancyclic at every one of the $27$ values $n=41,\dots,67$**. All 27 were
  re-checked here with `search/verify.py`, together with $F_{68}$ as a
  negative control, in a single run recorded at
  `papers/draft/verify-family-41-68-20260915.txt` (27 rows "pancyclic",
  missing $[\,]$; the $n=68$ row "NOT pancyclic", missing exactly $[33]$).
  This one construction therefore establishes $h(n)\le6$ for all
  $41\le n\le67$ on its own, with no monotonicity assumption and no appeal to
  the eleven individual witnesses above.

  *Why it stops at $67$, exactly.* The cycle-length spectrum of $F_n$ is
  $$\{\,\ell:\ell\text{ is a cycle length of }F_n\,\}=[3,32]\ \cup\ [n-34,\,n],$$
  a symbolic statement in $n$: a fixed core of short cycles realises
  $3,\dots,32$ and never more, and a second family realises $n-34,\dots,n$,
  only the arc from $31$ to $n-8$ changing length between them. Explicit cycles
  for every length in both intervals, written in terms of $n$, are listed in
  the review certificate `family-certificate.md` /
  `family-cycle-certificate.json` (Builder's findings review,
  2026-09-15). The union is all of $[3,n]$ precisely when the intervals
  meet, $n-34\le33$, i.e. **iff $n\le67$**. So $F_{67}$ is pancyclic and
  $F_{68}$ misses exactly $33$ — not an accident of the search, but the first
  value the two intervals fail to cover. Checked against ground truth here:
  the computed length set equals $[3,32]\cup[n-34,n]$ exactly at
  $n=41,45,50,55,60,65,66,67,68,69,70$, and the missing set grows as
  predicted, $[33]$ at $68$, $[33,34]$ at $69$, $[33,34,35]$ at $70$.

  *One correction to an earlier revision of this note.* It said the family
  "carries the $n=64,65,66,67$ witnesses" and is "pancyclic for exactly
  $n=64,\dots,67$". Both are wrong. It carries the witnesses tabulated above
  at $n=65,66,67$ only — the tabulated $n=64$ witness is
  $(0,2)(0,61)(1,12)(3,60)(4,29)(56,61)$, a different graph from
  $F_{64}=(0,2)(0,57)(1,13)(3,58)(4,31)(56,59)$, though both are pancyclic —
  and the family does not start at $64$: it reaches down to $41$ and below.
  The earlier claim recorded where the search had looked, not where the family
  works. The $n=68$ member $(0,2)(0,61)(1,13)(3,62)(4,31)(60,63)$ was
  re-checked with `search/verify.py` in this revision: "NOT pancyclic",
  missing exactly $[33]$ (`papers/draft/verify-rerun-20260914.txt`). Varying
  the two inner chords over $(1,a)(4,b)$, $a\in[5,44]$, $b\in[a+1,\min(n-9,59)]$,
  does not repair $n=68$ (best is still missing one length), and a complete
  2-of-6 slot sweep around the $n=68$ member finds no witness
  ($36{,}481{,}725$ candidates); the 3-of-6 sweep at $n=68$ was in flight when
  `papers/REPORT-k6-gpu-joint.md` was written. So $n=68$ was a
  missing-one near-miss of exactly the kind the 3-of-6 sweep resolved at
  $n=66$; the exhaustion of Section 3.6 has since shown that no $6$-chord
  pancyclic graph exists on $68$, $69$ or $70$ vertices at all, so
  $t_6\ge68$ is excluded and $t_6=67$ unless a witness exists in $71..88$.
* **Both closed forms of Section 5 are refuted at their first genuine test.**
  The rival form $2^{k-2}(10-k)$ predicted $t_6=64$; the $n=65$ witness
  refutes it. The Fibonacci form $2\,\mathrm{Fib}(k+3)-2$ predicted
  $t_6=66$; the $n=67$ witness refutes it. Neither witness lies in the chord
  family the earlier search phases were extending.
* **The binary-shortcut recipe Alon and Krivelevich [AK25] attribute to
  GKW16 and reproduce approximately** (Section 1 explains why the
  attribution to GKW16 itself is secondary and hedged; every numeric detail
  here is taken from AK's own paraphrase, transcribed with its exact
  arithmetic in `papers/REPORT-bondy-construction.md`, not from GKW16
  directly), instantiated with 5 shortcut chords
  $e_0{=}(0,2),e_1{=}(2,5),e_2{=}(5,10),e_3{=}(10,19),e_4{=}(19,36)$ plus one
  joining edge $(0,36)$ (6 chords total), was verified computationally to be
  pancyclic at **$n=40$**, and to be missing *only and
  exactly* length $5$ for every other $n$ in $[37,69]$ tested — a direct,
  computed confirmation of AK's paraphrased claim that this stage needs to
  patch a small subset of short lengths (`papers/REPORT-k6-upper.md`,
  `search/k6/gkw-K4.txt`).

  *The $n=36$ row of that log is not a six-chord result.* The log also
  carries a row "n=36: PANCYCLIC", and an earlier revision of this note
  repeated it as "pancyclic at exactly $n=36$ and $n=40$." The
  instantiation uses vertex $36$, which does not exist on $C_{36}$. Read
  literally it adds a $37$th vertex, and the resulting graph does *not*
  cover $[3,36]$ — it misses $5$, like its neighbours. Read modulo $n$ it
  collapses $(19,36)$ to $(19,0)$ and $(0,36)$ to a self-loop, leaving the
  **five**-chord graph $C_{36}+(0,2)(2,5)(5,10)(10,19)(0,19)$, which is
  pancyclic and agrees with $h(36)=5$ in Section 2's table, but says
  nothing about six chords. Both readings were recomputed here. Only the
  $n=40$ row is a six-chord statement. The same out-of-range vertex
  invalidated one row of `search/k6/witnesses.csv`, removed in this
  revision; nothing in $41\le n\le67$ depends on either.

  Note also that `papers/REPORT-bondy-construction.md`
  finds this general recipe *undershoots* the actual best-known thresholds
  $t_k$ substantially for $k\le5$ (by 50% at $k=2$, still 12.5% at $k=5$); it
  is an asymptotically-motivated construction, not the source of this
  project's small-$k$ exact values, which come from the separate
  hand/computer-optimized graphs of Griffin and George–Marr–Wallis.
* **How the earlier $n=66$ attempt stalled, and why it no longer bears on
  $t_6$.** The first phase's direct attack on $n=66$ (seeded from the $n=56$
  witness, 350 s of strict hill-climb followed by exhaustive single-chord
  coordinate descent over 12,000 evaluations, `papers/REPORT-k6-upper.md`)
  reached a confirmed *single-chord* local optimum
  $(0,2)(0,48)(1,40)(11,41)(44,47)(47,52)$ missing exactly $\{5,7,8\}$, and
  an earlier revision of this note reported $n=66$ as "stalled 3 lengths
  short." That optimum was local to single-chord moves and to that seed
  family; the witness at $n=66$ was subsequently found by a joint 3-of-6
  chord replacement around a different seed (the near-miss
  $(0,2)(0,63)(1,13)(3,62)(4,31)(58,63)$, missing only $[57]$), after
  $22{,}335{,}424{,}500$ GPU-evaluated candidates over 15 of the 20 slot
  subsets. The stall is therefore a statement about that search's
  neighbourhood, not about $n=66$.

## 7. References

- [Bo71] J. A. Bondy, "Pancyclic graphs I," *J. Combin. Theory Ser. B* 11 (1971),
  80–84.
- [Jia96] X. Jia, "Some extremal problems on cycle distributed graphs," *Congressus
  Numerantium* 121 (1996), 216–222. MR1431994.
- [Gr13] Sean Griffin, "Minimal Pancyclicity," arXiv:1312.0274 (2013).
- [GMW13] J. C. George, A. Marr, W. D. Wallis, "Minimal pancyclic graphs,"
  *J. Combin. Math. Combin. Comput.* 86 (2013), 125–133.
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
