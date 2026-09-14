# Asymptotics of cycle counts with fixed cyclomatic number

Checked 2026-09-14. Let `C(G)` be the number of undirected simple cycles. For
a connected graph with `n` vertices and `m` edges, write `r=m-n+1` for the
cyclomatic number. For a Hamiltonian graph with `n+k` edges, `r=k+1`; the
literature's `M(k)` is therefore a Hamiltonian specialization of the general
fixed-r problem.

## What is actually conjectured

The key historical result is Entringer and Slater, “On the maximum number of
cycles in a graph,” *Discrete Mathematics* 32 (1981), 305–321. Their fixed-r
function (often denoted `phi(r)` or `psi(r)`) satisfies

`2^(r-1) <= phi(r) <= 2^r`.

They give cubic constructions with `C(G)>2^(r-1)` for `r>=3`, and conjecture
that the lower bound is asymptotically correct. In the present notation this
conjecture says `phi(r)/2^(r-1) -> 1`. For Hamiltonian graphs, substituting
`r=k+1` predicts `M(k)/2^k -> 1`, not a limit greater than 1. This is a
conjecture, not a theorem.

Evidence: the open thesis survey `e30d...pdf` (download record indexed by the
University of Manitoba) states `2^(r-1) <= phi(r) <= 2^r`, says Entringer–Slater
“conjecture that their lower bound is asymptotically correct,” and records their
cubic construction. The MathOverflow survey independently describes the
same fixed-cyclomatic parametrization ([MathOverflow](https://mathoverflow.net/questions/203119/how-many-simple-cycles-can-a-graph-with-n-vertices-and-m-edges-have)).

## Hamiltonian fixed-k data and Rautenbach–Stella

Shi (1994) proves, for Hamiltonian graphs with `k` chords,

`2^k+k(k-1)+1 <= M(k) <= 2^(k+1)-1`,

with equality in the lower bound for `k=1,2,3,4`. Rautenbach and Stella,
“On the maximum number of cycles in a Hamiltonian graph,” *Discrete Math.*
304 (2005), 101–107, improve the upper bound for `k>=4` and compute exactly:

`M(5)=56, M(6)=109, M(7)=213, M(8)=401, M(9)=783, M(10)=1484`.

Their abstract gives the asymptotic-strengthened upper bound

`M(k) <= 2^(k+1)-1-k*((sqrt(k)-2)/(log_2(k)+2)-(1/4)log_2(k))`,

where only `log_2(k)+2` is the denominator and the subtraction by
`(1/4)log_2(k)` is outside that fraction but inside the parentheses (the
PDF/OCR layout is easy to misread). They also prove
`M(k)>=2^k+(5/2)k^2-(21/2)k+14`.

The paper explicitly says: `we were unable to find some regularity in these
configurations` and leaves the problem open. No conjecture that the ratio
`M(k)/2^k` converges to a constant greater than 1 is stated there. The data
ratios for k=4..10 are approximately `1.8125, 1.75, 1.7031, 1.6641, 1.5742,
1.5293, 1.4492`; they are consistent with the Entringer–Slater prediction but
far too short a range to establish monotonicity or a limit.

Evidence: publisher text gives the quoted bounds, exact values, and the
statement that exact extremal graphs are determined for `5<=k<=10`
([Rautenbach–Stella](https://www.sciencedirect.com/science/article/pii/S0012365X05004826)).
Local `1312.0274.txt` reproduces the theorem and exact-data context under
`Theorem 3. (Rautenbach and Stella [5])`.

## General simple graphs: later improvements

**Aldred and Thomassen (2008), “On the maximum number of cycles in a planar
graph,” *J. Graph Theory* 57, 255–264, DOI 10.1002/jgt.20290.** They improve
the universal connected-graph cycle-space ceiling to

`C(G) <= (15/16) 2^r`,

and prove a substantially smaller planar bound (of order `2^(r-1)`), with
prism constructions showing the planar order is best possible. This concerns
arbitrary connected graphs/planar graphs, not Hamiltonian `M(k)`, but confirms
that the leading constant in the unrestricted problem is not simply settled by
the binary cycle-space bound. Evidence: the later open paper quotes exactly
`C(G) <= 15/16 2^(m-n+1)` ([EJC 2019 paper](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v26i4p42/pdf/));
the original abstract is at [Wiley](https://doi.org/10.1002/jgt.20290).

**Arman, Gunderson and Tsaturian (2016), “Triangle-free graphs with the
maximum number of cycles,” *Discrete Math.* 339, 699–711, DOI
10.1016/j.disc.2015.10.008.** For `n>=141`, the balanced complete bipartite
graph is the unique triangle-free n-vertex graph with the most cycles; they
also give tight Bessel-function estimates and an upper bound on Hamilton cycles
in triangle-free graphs. This is a dense fixed-n extremal theorem, not a
fixed-r theorem, and gives no direct asymptotic value for `M(k)`. Evidence:
[Monash abstract](https://research.monash.edu/en/publications/triangle-free-graphs-with-the-maximum-number-of-cycles) and open preprint
[arXiv:1501.01088](https://arxiv.org/abs/1501.01088).

**Arman and Tsaturian (2019), “The maximum number of cycles in a graph with
fixed number of edges,” EJC 26(4) #P4.42.** For an m-edge simple graph they
prove an upper bound `(1.443)^m` for sufficiently large m and construct graphs
with `(1.37)^m` cycles. They quote Aldred–Thomassen's `15/16` improvement and
Entringer–Slater's fixed-r problem. This is a different asymptotic regime:
when `m-n+1=r` is fixed or slowly growing, the fixed-edge bound does not settle
the normalized `2^r` constant. Evidence: the paper abstract states
`at most (1.443)^m` and examples `(1.37)^m`
([EJC](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v26i4p42/pdf/)).

**AlBdaiwi (2016/2018), “On the Number of Cycles in a Graph,” arXiv:1603.01807.**
This surveys the fixed-r problem and describes a technique aimed at improving
the Hamiltonian maximum-cycle upper bound, but does not resolve the limit.
Evidence: [arXiv record](https://arxiv.org/abs/1603.01807) says the paper gives
a technique that “could improve an upper bound” rather than claiming a solved
asymptotic.

**Gerbner, Keszegh, Palmer and Patkós (2018), “On the Number of Cycles in a
Graph with Restricted Cycle Lengths,” SIAM J. Discrete Math. 32, 266–279.**
For a fixed allowed length set `L`, they determine polynomial-order maxima in
`n`; this does not address unrestricted cycle lengths at fixed cyclomatic
number. Evidence: [SIAM abstract](https://epubs.siam.org/doi/10.1137/16M109898X).

**Bucić, Gishboliner and Sudakov (2022), “Cycles of many lengths in Hamiltonian
graphs,” Forum Math. Sigma 10, e70.** This is about the number of distinct
cycle lengths under regularity/minimum-degree hypotheses, not the total number
of cycles. It does not imply an asymptotic formula for `M(k)`, but is relevant
to separating “cycle multiplicity” from “cycle spectrum.” Evidence: the public
abstract says the prior bound was only `sqrt(n)` distinct lengths and states
the regular Hamiltonian conjecture ([Cambridge](https://www.cambridge.org/core/journals/forum-of-mathematics-sigma/article/cycles-of-many-lengths-in-hamiltonian-graphs/1B67CCA29A3AD712AE499AF590276522)).

**Kráľ/Kynčl citation check.** Searches for “Kral Kyncl maximum cycles” returned
ordered-Ramsey papers and unrelated cycle results, not a paper improving the
fixed-cyclomatic maximum-cycle function. This is a negative literature result,
not proof that no such citation exists.

## Conjecture verdict

For arbitrary connected simple graphs, the located literature supports only
`2^(r-1) <= phi(r) <= (15/16)2^r` (and the sharper planar result). The
Entringer–Slater conjecture is `phi(r)~2^(r-1)`, i.e. normalized limit 1 under
their natural normalization. For Hamiltonian graphs, Shi/Rautenbach–Stella
give `2^k <= M(k) <=` an approximately `2^(k+1)` ceiling with a lower-order
improvement; the natural inherited conjecture is `M(k)/2^k -> 1`. No located
source proves existence of the limit, proves it equals 1, or proposes a limit
strictly greater than 1.

## Can Rautenbach–Stella Figures 2–7 be converted to chord lists?

No, not from the accessible publication text. The figures are unlabelled
abstract extremal graphs (with representatives up to isomorphism), and the
paper's method first enumerates Hamiltonian 3-regular graphs on `2k` vertices
with `3k` edges. A chord list requires choosing and labelling one particular
Hamilton cycle in each representative; neither the HTML metadata nor the
indexed figure captions supplies that Hamilton cycle or vertex labelling.
Different Hamilton cycles in the same graph can yield different chord lists.
Therefore no canonical explicit lists for k=5..10 can be responsibly reported
without the actual labelled figure data or a machine-readable graph archive.
This is “could not extract,” not “no chord representation exists.”

The only extractable shape statement is the one in the paper: extremal graph
representatives are obtained by isomorphism testing, and the authors say they
found no regularity. Consequently the proposed three-gap comparison with sparse
pancyclic extremals remains open.

## Search/audit notes

Queries used: exact titles and author pairs in Google Scholar; publisher/DOI
pages; arXiv searches for `maximum number cycles cyclomatic`, `Hamiltonian k
chords cycles`, and `Entringer Slater`; Semantic Scholar exact-title searches;
and citation trails from Rautenbach–Stella. Google Scholar exposed the
Rautenbach–Stella cited-by link (7 at the publisher page), but no cited paper
with a fixed-r asymptotic resolution was located. Semantic Scholar API access
was rate-limited (HTTP 429), so that portion is unknown rather than an absence
claim. No additional open PDF of Rautenbach–Stella was found; no paywall bypass
was used.
