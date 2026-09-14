# Cycle-count table for Erdős Problem 1016

Checked 2026-09-14. Here `k` is the number of chords beyond a fixed Hamilton
cycle, and `M(k)` is the maximum number of undirected simple cycles in an
n-vertex Hamiltonian graph with `n+k` edges.

## Exact M(k)

Shi, “The number of cycles in a hamilton graph,” *Discrete Mathematics* 133
(1994), 249–257, DOI [10.1016/0012-365X(94)90031-0](https://doi.org/10.1016/0012-365X(94)90031-0),
defines `Gamma_k` and `M(k)` in the introduction and proves
`2^k+k(k-1)+1 <= M(k) <= 2^(k+1)-1`; equality in the lower bound holds for
`1<=k<=4`. The exact values for k=5..10 below are stated by
Rautenbach–Stella, not by Shi.

| k | exact M(k) | reference | extremal configuration |
|---:|---:|---|---|
| 1 | 3 | Shi 1994, intro | equality in Shi lower bound |
| 2 | 7 | Shi 1994, intro | equality in Shi lower bound |
| 3 | 15 | Shi 1994, intro | equality in Shi lower bound |
| 4 | 29 | Shi 1994, intro; R–S Fig. 1 | equality in Shi lower bound |
| 5 | 56 | Rautenbach–Stella 2005, Section 3, Fig. 2 | extremal 3-regular graph on 10 vertices/15 edges; representative shown |
| 6 | 109 | Rautenbach–Stella 2005, Section 3, Fig. 3 | extremal 3-regular graph on 12 vertices/18 edges; representative shown |
| 7 | 213 | Rautenbach–Stella 2005, Section 3, Fig. 4 | extremal 3-regular graph on 14 vertices/21 edges; representative shown |
| 8 | 401 | Rautenbach–Stella 2005, Section 3, Fig. 5 | extremal 3-regular graph on 16 vertices/24 edges; representative shown |
| 9 | 783 | Rautenbach–Stella 2005, Section 3, Fig. 6 | extremal 3-regular graph on 18 vertices/27 edges; representative shown |
| 10 | 1484 | Rautenbach–Stella 2005, Section 3, Fig. 7 | extremal 3-regular graph on 20 vertices/30 edges; representative shown |

Evidence: the indexed publisher record says `Section 3 ... M(k) for 5<=k<=10`
and gives the figure captions `k=5 with 56 cycles`, `k=6 with 109`, `k=7 with
213`, `k=8 with 401`, `k=9 with 783`, and `k=10 with 1484`
([ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0012365X05004826)).
It says extremal graphs were found by enumerating Hamiltonian 3-regular graphs
of order `2k` and size `3k`, then testing isomorphism types, and that the
general exact problem remains open.

## Rautenbach–Stella bound

The parenthesisation needed for the claimed improvement is

`M(k) <= 2^(k+1)-1 - k * ((sqrt(k)-2)/(log_2(k)+2)-(1/4)log_2(k))`, `k>=4`.

Only `log_2(k)+2` is the denominator; the subtraction by `(1/4)log_2(k)` is
outside that fraction but inside the parentheses. This is the expression shown
in the publisher abstract and local `1312.0274.txt`, under `Theorem 3
(Rautenbach and Stella [5])`.

`B_RS` below is the real-valued right side, rounded to six decimals;
`N_RS=floor(B_RS)+2` is the largest integer n allowed by `n-2<=B_RS`.

| k | A(k) | B_RS | N_RS |
|---:|---:|---:|---:|
| 1 | -0.500000 | 3.500000 | 5 |
| 2 | -0.445262 | 7.890524 | 9 |
| 3 | -0.470983 | 16.412949 | 18 |
| 4 | -0.500000 | 33.000000 | 35 |
| 5 | -0.525861 | 65.629305 | 67 |
| 6 | -0.548205 | 130.289230 | 132 |
| 7 | -0.567513 | 258.972591 | 260 |
| 8 | -0.584315 | 515.674517 | 517 |
| 9 | -0.599055 | 1028.391494 | 1030 |
| 10 | -0.612088 | 2053.120879 | 2055 |
| 11 | -0.623693 | 4101.860620 | 4103 |
| 12 | -0.634090 | 8198.609080 | 8200 |
| 13 | -0.643456 | 16391.364928 | 16393 |
| 14 | -0.651933 | 32776.127066 | 32778 |

The k=1..3 evaluations are extrapolations; the theorem is stated for k>=4.

## Count-to-order comparison

A pancyclic n-vertex graph needs at least `n-2` distinct cycles. The trivial
ceiling `U0=2^(k+1)-1` permits `N0=2^(k+1)+1`; any ceiling U permits
`floor(U)+2`.

| k | N0 trivial | N_RS | Shi exact M(k) | N_Shi=M+2 | largest n with h(n)=k known | gaps (N0 / N_RS / N_Shi) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5 | 5* | 3 | 5 | 5 | 0 / 0 / 0 |
| 2 | 9 | 9* | 7 | 9 | 8 | 1 / 1 / 1 |
| 3 | 17 | 17* | 15 | 17 | 14 | 3 / 3 / 3 |
| 4 | 33 | 35 | 29 | 31 | 24 | 9 / 11 / 7 |
| 5 | 65 | 67 | 56 | 58 | 40 | 25 / 27 / 18 |
| 6 | 129 | 132 | 109 | 111 | unknown; h(41)=6 verified | unknown; versus n=41: 88 / 91 / 70 |
| 7 | 257 | 255 | — | — | unknown | unknown |
| 8 | 513 | 511 | — | — | unknown | unknown |
| 9 | 1025 | 1022 | — | — | unknown | unknown |
| 10 | 2049 | 2046 | — | — | unknown | unknown |
| 11 | 4097 | 4093 | — | — | unknown | unknown |
| 12 | 8193 | 8189 | — | — | unknown | unknown |
| 13 | 16385 | 16380 | — | — | unknown | unknown |
| 14 | 32769 | 32763 | — | — | unknown | unknown |

`*` is an extrapolated R–S evaluation below its stated range. The threshold
data are the current verified values: largest known n with h(n)=1,2,3,4,5 is
`5,8,14,24,40`; `h(41)=6` is a separate manager-supplied exhaustive result and
verified witness. The earlier public report contains the evidence string
`h(n)=5 for every 34<=n<=40` ([report](https://erdosproblemaday.com/report/1016)).

## Markström’s known UPC graphs

Markström, “A note on uniquely pancyclic graphs,” *Australasian Journal of
Combinatorics* 44 (2009), 105–110, reports no new UPC graph on `n<=59` and no
UPC graph with exactly five chords. The seven known graphs are:

| n | chord count k | edges n+k |
|---:|---:|---:|
| 3 | 0 | 3 |
| 5 | 1 | 6 |
| 8 | 2 | 10 |
| 8 | 2 | 10 |
| 14 | 3 | 17 |
| 14 | 3 | 17 |
| 14 | 3 | 17 |

Evidence: downloaded `Markstrom-2009.pdf` contains `no new such graphs on n <=
59` and `no uniquely pancyclic graphs with exactly 5 chords`; the indexed
figure summary says `All seven known uniquely pancyclic graphs; they are of
order 3, 5, 8, 8, 14, 14, and 14` ([open PDF](https://ajc.maths.uq.edu.au/pdf/44/ajc_v44_p105.pdf)).

Correction to the assignment premise: these UPC graphs are not all equality
cases of `M(k)<=2^(k+1)-1`. Their cycle count is `n-2`; for example n=8,k=2
has 6 cycles versus bound 7, and n=14,k=3 has 12 versus 15. Equality would
require `n=2^(k+1)+1` (orders 3,5,9,17,...). No UPC graph beyond n=14 is known;
Markström’s bounded search rules out new ones through n=59, not beyond 59.

## Bottom line

Shi supplies the universal ceiling and exact lower-bound equality for k<=4.
Rautenbach–Stella supply the stronger ceiling and exact values 56, 109, 213,
401, 783, 1484 for k=5..10, with extremal representatives in Figures 2–7.
The count argument is exact through k=3, then leaves gaps 7, 18, and 70 for
the exact-cycle values at k=4,5,6 (the k=6 comparison uses only the n=41
point). It does not determine the eventual h(41) threshold or the asymptotic
problem.
