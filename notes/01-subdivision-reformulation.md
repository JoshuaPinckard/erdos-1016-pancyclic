# Erdos #1016 working notes -- 2026-09-14

## Data (exact, two independent programs; matches Griffin 2013 for n <= 37)
h(n) = min chords making C_n pancyclic.
h=1: n<=5. h=2: 6..8. h=3: 9..14. h=4: 15..24. h=5: 25..37 (Griffin's construction reaches 37).
Counting bound allows h chords up to n = 2^(h+1)+1 = 5, 9, 17, 33, 65.
Ratios (last n with h chords)/2^(h+1): 1.25, 1.00, 0.875, 0.75, and >= 0.578 for h=5.

n=38, k=5: local search (hours) never finds a witness; best configurations miss exactly one
length, 21 = n/2 + 2. Exhaustive sharded run for n=38, k=5 launched 2026-09-14 (search/n38k5-*.txt).
If it returns NONE for all shards + BC, then t_5 = 37 and h(38) = 6, a new value.

## Subdivision lemma (corrected 2026-09-14 after review REVIEW-notes01.md)
Let G' = C_s + k chords and let e = uv be an edge of C_s.  Let A = set of lengths of cycles of G'
avoiding e, and B = set of lengths of cycles of G' through e (B is a subset of [3, s]).  Subdividing
e with m new vertices gives a graph G on n = s + m vertices whose cycle-length set is exactly
A cup (B + m).  Conversely, if G = C_n + k chords and some arc of C_n between consecutive chord
endpoints has m interior vertices, contracting that arc to a single edge uv gives G' with
L(G) = A cup (B + m).  Hence

  h(n) <= k  <=>  there exist s < n, G' = C_s + k chords and an edge uv of C_s with
                  A cup (B + (n - s))  contains  [3, n].

(The earlier version of this note wrongly demanded A contains [3,s] and B contains [2s-n, s]
separately; lengths below s may come from either side.  Counterexample to the old version: n=8,
chords (0,2)(0,5), any arc.  Found by Worker 4.)

Consequences that survive.
* For each chord subset K with both Shi cycles present, exactly one uses uv and one avoids it
  (uv lies in exactly one of the two alternating arc classes).  So |A| <= 2^k - 1 and |B| <= 2^k,
  and |A| + |B| <= 2^(k+1) - 1: the counting is balanced at every level of the recursion.  Any
  improvement must come from which sums are realisable, never from counting.
* Multigraph caveat: if the arc's two endpoints are also joined by a chord, then after contraction
  that chord is parallel to uv and G' is a multigraph; B then contains 2 (the digon), which is the
  triangle chord+arc of G.  With that convention the lemma holds for every arc (checked numerically
  on all arcs of the witnesses for n = 8, 24, 38 with a multigraph-aware classification).
* Cycles through e have length >= 3 in a simple G', so B + m is contained in [m+3, n] and the lengths
  3, ..., m+2 must lie in A, which is contained in [3, n-m].  Therefore m + 2 <= n - m: every arc
  whose endpoints are NOT joined by a chord has at most (n-2)/2 interior vertices; an arc whose
  endpoints are joined by a chord has at most (n-1)/2.  (The old note said (n-3)/2 for the largest
  arc; that was an off-by-one.  Check: n=8, chords (0,2)(1,4) has an arc with m = 3 = (8-2)/2.)
* At n = 38 the near-miss configurations have m = 18 = (n-2)/2, and then length m + 3 = 21 must be
  a triangle of G' through uv; the local-search near-misses are exactly the graphs lacking it.

## Large-length form of the wall inequality
Order gaps by interior size m_1 >= m_2 >= ... . A cycle of length > n - m_j must use every arc
with interior >= m_j. Cycles using a fixed set of j arcs correspond to chord subsets K for which
those arcs all lie in the same alternating class, i.e. K's cross-chords form an even subgraph of
the multigraph on the j stretches; their number is <= 2^(k - j + c_j), c_j = number of components.
So m_j <= 2^(k - j + c_j). Summing over j recovers the trivial bound; equality forces geometric
gaps m_j ~ 2^(k-j+1), i.e. the binary construction, whose lengths 3..2k are then missing and must
be supplied by cycles inside single stretches (no big arc). The number of such cycles is at most
sum over stretches of (2^(r_i) - 1) with sum r_i <= k, while the number of long cycles is a product
of per-stretch end-to-end path counts. The same chords must serve both; this tension is the
log* recursion and is what a proof has to quantify.

## Generalised problem
P(r) = max m such that some graph with cyclomatic number r has cycles of all lengths 3..m.
h(n) >= (min r with P(r) >= n) - 1. Trivial: P(r) <= 2^r + 1. Conjecture equivalent to Erdos's
weak question: P(r) <= 2^r / omega(1).

## Update 2026-09-14 evening: exact values to 41 and the extremal graphs at the threshold
GPU exhaustive search (search/gpu_pancyc.py): h(38)=h(39)=h(40)=5, h(41)=6 (no 5-chord graph on 41
vertices, 1.76e10 sets; 6-chord witness (4,13)(28,30)(12,26)(17,31)(12,29)(24,27) verified).
Thresholds t_k = largest n with h(n)=k:  5, 8, 14, 24, 40.   t_k / 2^(k+1) = 1.25, 1, .875, .75, .625.

ALL 5-chord pancyclic graphs on 40 vertices (up to rotation and reflection): exactly five.
  chords                              endpoints  gaps (cyclic)                cycles  distinct lengths
  (0,2)(1,5)(1,7)(3,34)(24,39)        9          1,1,1,5,10,17,2,2,1          45      38
  (0,2)(0,37)(1,35)(3,18)(8,39)       9          1,1,1,5,10,17,2,2,1          45      38
  (0,2)(0,33)(1,13)(3,34)(32,35)      9          1,1,5,1,1,1,19,10,1          48      38
  (0,4)(0,5)(1,34)(2,35)(3,15)        9          1,1,1,1,1,5,1,19,10          48      38
  (0,7)(1,8)(2,10)(2,11)(9,21)        9          1,1,1,1,5,1,1,19,10          48      38
Every one has exactly one shared endpoint (9 distinct endpoints for 5 chords), three "geometric" gaps
(19,10,5) or (17,10,5) -- i.e. about n/2, n/4, n/8 -- and the remaining six gaps of size 1 or 2.
Only 45-48 of the 63 possible cycles exist and exactly 38 lengths are distinct: the count bound is slack
by 15-18 cycles, yet the graph is extremal.  Same shape at earlier thresholds:
  n=24 (k=4): gaps 11,6 | 2,2,1,1,1      n=14 (k=3): gaps 7,3 | 2,1,1      n=8 (k=2): gaps 3,3,2.
Reading: the geometric gaps supply the long lengths (each big gap doubles the reachable range), the
tiny gaps plus shared endpoints supply lengths 3..~2k, and the SAME chords must do both.  A proof
should show that with k chords the geometric part can only reach about (1 - c_k) 2^(k+1) with c_k
growing, because chord endpoints spent on the tiny gadget are unavailable as gap boundaries.

## Lean status (2026-09-14, end of day)
Project C:\Users\ToolsEnabled-Dev\Desktop\erdos1016, Lean 4.33.1 / Mathlib v4.33.1, `lake build` passes.
- Basic.lean: IsPancyclic G := ∀ ℓ, 3 ≤ ℓ → ℓ ≤ n → ∃ v (w : G.Walk v v), w.IsCycle ∧ w.length = ℓ.
- Witness.lean (Worker 2): chords38/41, G38/G41 via fromRel over Bool adjacency, explicit cycle lists.
- ListCycle.lean: exists_walk_of_isChain, exists_cycle_of_list, isPancyclic_of_lists, Bool helpers,
  isPancyclic_of_candidates.
- Pancyclic.lean: isPancyclic_G38, isPancyclic_G41 (decide over the lists).
- Excess.lean: baseCycle n; PancyclicWithChords n k := ∃ cs : Finset (Sym2 (Fin n)), cs.card = k ∧
  (∀ e ∈ cs, e ∉ (baseCycle n).edgeSet) ∧ IsPancyclic (baseCycle n ⊔ fromEdgeSet ↑cs);
  theorems pancyclicWithChords_38_5 and pancyclicWithChords_41_6.
All of the above: axioms [propext, Classical.choice, Quot.sound], no sorry, no native_decide.
Independent statement review: papers/REVIEW-lean-statements.md (Worker 3).
