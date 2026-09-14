# Literature sweep: Erdős Problem 1016 (Bondy 1971)

Date checked: 2026-09-14. Scope: the open literature relevant to
`m(n)=n+h(n)`, cycle counts in Hamiltonian graphs with `r` chords, and
uniquely pancyclic graphs. This report records results found, not a proof of
novelty.

## Costliest finding first

Rautenbach–Stella (2005) is the strongest located lower-bound input beyond the
elementary cycle-space count. For `r>=4`, if `M(r)` is the maximum number of
cycles in an n-vertex Hamiltonian graph with `n+r` edges, they prove

`M(r) <= 2^(r+1)-1-r*((sqrt(r)-2)/(log_2(r)+2)-(1/4)log_2(r))`.

Consequently `h(n)` is at least the largest integer `r` for which this right
side is less than `n-2`, strictly improving `2^(r+1)-1` whenever the
parenthesis is positive. It does not prove the proposed `log_* n` additive
term; the all-r extremal problem remains open. Evidence: local
`1312.0274.txt` contains the quoted expression under `Theorem 3 (Rautenbach
and Stella [5])`; the publisher abstract gives the same formula and says exact
values are known only for `5<=r<=10` ([publisher record](https://www.sciencedirect.com/science/article/pii/S0012365X05004826)).

## Results by question

### (1) Lower bounds and the log-star term

**Bondy (1971), “Pancyclic graphs I,” J. Combin. Theory Ser. B 11, 80–84,
DOI 10.1016/0095-8956(71)90016-5.** Bondy stated, without proof in that
paper, `log_2(n-1)-1 <= h(n) <= log_2 n+log_*n+O(1)`. The proved theorem is
a degree-sum criterion: a Hamiltonian graph with degree sum at least `n` for
every nonadjacent pair is pancyclic unless it is `K_(n/2,n/2)`. It is
background, not a stronger sparse lower bound. Evidence: `1312.0274.txt`
contains `Claim 1. (Bondy [3])` and both inequalities; publisher metadata is
at [Bondy](https://www.sciencedirect.com/science/article/pii/0095-8956(71)90016-5).

**Shi (1994), “The number of cycles in a Hamilton graph,” Discrete Math. 133,
249–257, DOI 10.1016/0012-365X(94)90031-0.** For a Hamiltonian graph with
`r` chords, Shi proved `2^r+r(r-1)+1 <= M(r) <= 2^(r+1)-1`, with equality in
the lower bound for `1<=r<=4`. The upper bound gives the usual counting lower
bound on `h`; it does not improve that ceiling. Evidence: the indexed article
record states exactly `2^k+k(k-1)+1 <= M(k) <= 2^(k+1)-1` and identifies the
open extremal question ([article record](https://www.sciencedirect.com/science/article/pii/S0012365X05004826)).

**Rautenbach and Stella (2005), “On the maximum number of cycles in a
Hamiltonian graph,” Discrete Math. 304, 101–107, DOI
10.1016/j.disc.2005.09.007.** They prove the improved upper bound displayed
above, the lower bound `M(r)>=2^r+(5/2)r^2-(21/2)r+14`, and determine `M(r)`
and extremal structures exactly for `5<=r<=10`. This is the only located
improvement to the counting ceiling directly relevant to `h(n)`. Evidence:
`1312.0274.txt` under `Theorem 3`; [RWTH record](https://publications.rwth-aachen.de/record/187389).

**George, Marr and Wallis (2013), “Minimal pancyclic graphs,” J. Combin. Math.
Combin. Comput. 86, 125–133.** Gives chord-pattern analysis and the exact
small values later reproduced by Griffin; no better asymptotic lower bound or
log-star resolution was located. Citation and pages are independently recorded
in [EUDML](https://eudml.org/doc/271240).

**Griffin (2013), “Minimal Pancyclicity,” arXiv:1312.0274.** Exhaustive search
through 29 vertices plus a five-chord construction gives exact `m(n)` for all
`n<=37`. Griffin proves Bondy’s lower bound from the cycle count and records
the Rautenbach–Stella improvement, plus `m(n+1)<=m(n)+2` and partial
monotonicity. No positive log-star correction is proved. Evidence: local
`1312.0274.txt` contains `Exact values are given for m(n) for n <= 37`,
`Claim 1`, and `Proposition 2. m(n + 1) <= m(n) + 2`; [arXiv](https://arxiv.org/abs/1312.0274).

**George, Khodkar and Wallis (2016), *Pancyclic and Bipancyclic Graphs*,
Chapters 4–5, DOI 10.1007/978-3-319-31951-3.** Chapter 4 is the first
located published proof/source for the general `log n+log_*n+O(1)` construction;
the public abstract confirms that it treats minimum excess. It does not close
the lower/upper gap. Chapter 5 treats uniquely pancyclic graphs. Evidence:
[book record](https://portal.mardi4nfdi.de/wiki/Pancyclic_and_Bipancyclic_Graphs)
and [chapter metadata](https://www.researchgate.net/publication/303363776_Minimal_Pancyclicity).

**Alon and Krivelevich (2024 version, arXiv:2308.01564), “Sparse pancyclic
subgraphs of random graphs.”** Not an extremal `m(n)` theorem for complete
graphs. It proves that for `G(n,p)` above `p_*=(1+o(1))log n/n`, with high
probability the minimum pancyclic subgraph has `n+(1+o(1))log_2 n` edges.
Its introduction explicitly says the general exact value in Bondy’s range is
still open. Evidence: local `2308.01564.txt` contains
`Pex(G(n,p)) = (1 + o(1)) · log_2 n` and `What is the exact value ... is still
an open question`; [arXiv](https://arxiv.org/abs/2308.01564).

**Verdict (1):** A stronger finite-r lower bound exists via Rautenbach–Stella,
but no located paper proves or disproves `h(n)>=log_2 n+log_*n-O(1)`. The
asymptotic gap remains open.

### (2) Exact or upper-bound values for `n>=38`

The located primary exact table stops at `n=37`. Griffin has
`m(34),...,m(37)=39,40,41,42`, all with five chords. The manager-supplied new
certificate gives a five-chord family through `n=40`, hence
`h(n)=5 (34<=n<=40)` and `m(38)=43, m(39)=44, m(40)=45`.
This sweep found no prior primary publication of those entries; they should be
called “apparently new relative to located literature,” not unconditionally
new. The independent public report describes the same construction
([Erdős Problem a Day](https://erdosproblemaday.com/report/1016)). For larger
`n`, GKW16 supplies only `h(n)<=log_2 n+log_*n+O(1)`.

**Verdict (2):** `m(38)=43,m(39)=44,m(40)=45` are supported by the new
certificate and absent from the located primary table; no further exact values
were found.

### (3) Maximum cycles / distinct lengths with cyclomatic number `r`

For a connected Hamiltonian graph, cyclomatic number is `r+1` when the graph
has `n+r` edges, while “number of chords” is `r`. Shi’s universal ceiling is
`2^(r+1)-1` cycles. Rautenbach–Stella improve it by the displayed formula and
determine `M(r)` for `5<=r<=10`. Since a pancyclic graph needs `n-2` distinct
lengths, this bounds the number of possible lengths and drives the lower-bound
argument.

Affif Chaouche, Rutherford and Whitty (2012), “Pancyclicity when each cycle
must pass exactly k Hamilton cycle chords,” arXiv:1212.3633, studies a related
but different statistic. It defines `c(n,k)`, proves
`c(n,1)=floor((n-3)/2)`, and for fixed `k`, `c(n,k)=Omega(n^(1/k))`; for
`k=2`, `p>=(1+sqrt(4n-3))/2`. It restates Bondy’s lower bound and the
`2^(p+1)-1` count, but does not improve `h(n)` because every length must use
exactly `k` chords relative to a selected Hamilton cycle. Evidence: downloaded
`1212.3633.pdf`; its indexed text contains `c(n,1)=floor((n-3)/2)` and
`For k >= 1 fixed, c(n,k) is of order Omega(n^(1/k))`; [arXiv](https://arxiv.org/abs/1212.3633).

Entringer–Slater (1981), Volkmann (1996), Teunter–van der Poort (2000),
AlBdaiwi (2018), and Morrison–Roberts–Scott (2021) were checked as citation
trails for cycle maximization. Their settings are respectively general
fixed-edge, estimation, Hamilton-cycle enumeration, regular, or
forbidden-subgraph problems; no sharper universal `M(r)` statement applicable
here was located.

**Verdict (3):** The relevant sharp general facts are Shi’s ceiling,
Rautenbach–Stella’s improved ceiling and exact `r=5..10`, plus the distinct
length/chord statistic of Affif Chaouche–Rutherford–Whitty. No all-r exact
formula was found.

### (4) Uniquely pancyclic graphs

**Shi (1986), “Some theorems of uniquely pancyclic graphs,” Discrete Math. 59,
167–180, DOI 10.1016/0012-365X(86)90078-6.** Defines UPC as exactly one
cycle of each length, classifies outerplanar UPC graphs, and determines all
UPC graphs of size `n+r` for `r<=3`; it conjectures none for `r>=4` and proves
the `r=4` case. Evidence: publisher abstract says
`determine all UPC-graphs each ... contains nu + m edges for m<=3` and
`prove ... m=4` ([ScienceDirect](https://www.sciencedirect.com/science/article/pii/0012365X86900786)).

**Shi, Yap and Teo (1989), “On uniquely r-pancyclic graphs,” Ann. New York
Acad. Sci. 576, 487–499.** Generalizes uniqueness to prescribed cycle ranges;
classification/background only, not a lower bound for ordinary pancyclicity.
Evidence: [Wiley record/PDF](https://nyaspubs.onlinelibrary.wiley.com/doi/pdf/10.1111/j.1749-6632.1989.tb16433.x).

**Markström (2009), “A note on uniquely pancyclic graphs,” Australas. J.
Combin. 44, 105–110.** Gives new edge bounds for UPC graphs and a computer
search finding no new UPC graphs on `n<=59` vertices and no UPC graph with
exactly five chords. Therefore the five-chord graphs used for the
`n=34..40` construction cannot be UPC: some length is repeated. This is
structural evidence, not a lower bound for ordinary pancyclic graphs. Evidence:
downloaded open PDF `Markstrom-2009.pdf`; abstract contains
`no new such graphs on n <= 59` and `no uniquely pancyclic graphs with exactly
5 chords`; [journal PDF](https://ajc.maths.uq.edu.au/pdf/44/ajc_v44_p105.pdf).

**George–Khodkar–Wallis (2016), Chapter 5, “Uniquely Pancyclic Graphs.”**
Book treatment and historical classification context; public chapter metadata
identifies UPC as its subject ([record](https://eurekamag.com/research/100/718/100718928.php)).

**Verdict (4):** UPC results constrain the one-cycle-per-length extreme and
rule out five-chord UPC graphs, but do not imply a stronger lower bound for
`m(n)`. They support using cycle multiplicity as the likely route to improving
the lower bound.

## Search audit and negative-result limits

Independent methods used (queries and caps are explicit):

* **zbMATH Open API:** queried `pancyclic`, `minimum edges pancyclic`,
  `maximum cycles Hamiltonian`, and author/title variants for Bondy, Shi,
  Griffin, Rautenbach, Stella, Markström, and Sridharan. The documents endpoint
  was reachable (HTTP 200), but the attempted `_search` syntax returned HTTP
  422. zbMATH results are therefore **unknown**, not an absence claim.
* **Google Scholar HTML:** exact-title searches for `"Minimal Pancyclicity"`,
  `"On the maximum number of cycles in a Hamiltonian graph"`, `"A note on
  uniquely pancyclic graphs"`, and `"The number of cycles in a Hamilton graph"`
  (HTTP 200). Cited-by links were visible (14 for Rautenbach–Stella and 26 for
  Markström); citation lists were not treated as relevance proof.
* **Semantic Scholar:** Graph API returned HTTP 429 and public search HTML was
  empty. Coverage is **unknown**, not absent.
* **arXiv:** direct records/listing searches for `1312.0274`, `1212.3633`, and
  `2308.01564`; all three PDFs are in this folder. Search terms included
  `m(38)`, `m(40)`, `five chords pancyclic`, `minimum number of edges pancyclic
  graph`, and `post-2024 pancyclic excess`.
* **Erdős Problems #1016, its LaTeX/reference listing, OEIS A105206, and the
  Erdős Problem a Day report:** checked for comments, updates, and exact
  values. OEIS evidence is its text `Number of edges in a pancyclic graph on
  n+2 vertices` and a displayed list ending at 26 ([OEIS](https://oeis.org/A105206)).
* **Cross-checks:** publisher pages, open institutional records, DBLP, EUDML,
  exact-title web search, and citation trails. The targeted searches found no
  primary paper extending Griffin’s exact table past `n=37`. This is a
  literature miss, not proof of nonexistence.

Open-PDF limitation: Bondy, Shi (1986), Shi (1994), Rautenbach–Stella, and the
GKW book chapters were bibliographically verified, but publisher access did
not permit downloading their full PDFs during this run. No paywall bypass was
used. Downloaded open PDFs: `1212.3633.pdf` and `Markstrom-2009.pdf` (alongside
the pre-existing `1312.0274.pdf` and `2308.01564.pdf`).
