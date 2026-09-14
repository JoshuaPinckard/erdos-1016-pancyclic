# Review of exhaustive search and independent verification

## Scope and execution

Reviewed read-only: [pancyc.c](../search/pancyc.c) and [gpu_pancyc.py](../search/gpu_pancyc.py). The GPU program was not run. Independent cycle-space checks used [check.py](construction/check.py), with basis Hamilton cycle plus each chord and its forward Hamilton path; XOR elements were accepted when every degree was 0 or 2 and the non-isolated edge set was connected.

## (a) Triangle case split

Verdict: **mathematically exhaustive in principle, implementation coverage has a caveat**.

Evidence in [pancyc.c](../search/pancyc.c): quoted strings “Every pancyclic graph contains a triangle” and the three modes “A: chord (0,2)”, “B: no span-2 chord; chords (0,b),(1,b)”, and “C: no span-2 chord, no shape-B pair”. A triangle in (C_n) plus chords uses one, two, or three chords. Rotation sends the one-chord case to (0,2); two chords plus one cycle edge to (0,b),(1,b); three chords to (0,b),(b,c),(0,c). The loop bounds exclude cycle edges and span-2 chords in the relevant no-span cases.

The caveat is that the C implementation’s mode-B search fixes both chords and then calls `rec(2,-1)`, while mode-C similarly fixes three chords and calls `rec(3,-1)`; ordering is still exhaustive because `used[]` removes duplicates. The explanatory claim “up to rotation” is correct, but the implementation does not quotient reflections (only duplication/performance), which is safe. No failed completeness case was found by inspection.

## (b) GPU colex unranking

Verdict: **correct for the stated range (r\le4,M\le1000), subject to one untested runtime caveat**.

Evidence in [gpu_pancyc.py](../search/gpu_pancyc.py): quoted code comment “unrank colex r-combination of {0..M-1}”; for (i=r\) down to 1 it selects the largest (c) with `binom[c,i] <= N`, stores `idx[i-1]=c`, and subtracts `C(c,i)`. This is the standard combinadic/colex representation and produces strictly decreasing selected maxima, hence increasing `idx[0] < ... < idx[r-1]`. `binom_table()` measures `math.comb(c,i)` for `c<1024,i<=4`, so no table entries are guessed.

Independent bounded check: a local Python combinadic comparison over all (r=0,1,2,3,4), (M\le1000), and all ranks would be a large but finite test; it was not run in this review. Therefore the verdict is source-level correctness, not an executed exhaustive GPU-kernel test.

## (c) Cycle-space test and shared endpoints

Verdict: **independent verifier now passes the supplied witnesses; source logic is sound for shared endpoints**.

Evidence in [pancyc.c](../search/pancyc.c): quoted string “an element is a cycle iff all vertex degrees are 0 or 2 and its edges are connected”. The C code increments both endpoints for every selected cycle edge/chord, so chords sharing an endpoint are handled without assuming distinct endpoints. The GPU uses the same degree and walk logic in its quoted sections “basis: element 0 = Hamilton cycle” and “walk”.

Independent results from [check.py](construction/check.py):

- (n=38), chords (0,2),(0,18),(1,12),(3,19),(17,20): 36 lengths = 3..38.
- (n=40), chords (0,5),(1,5),(2,30),(3,10),(4,11): 38 lengths = 3..40.
- (n=41), chords (4,13),(28,30),(12,26),(17,31),(12,29),(24,27): 39 lengths = 3..41.

The independent verifier initially exposed two defects in its own implementation—requiring a cycle to span all vertices, and rejecting degree-0 vertices. Both were corrected; no source code was changed. This correction is important because a simple cycle in the cycle space may omit isolated vertices.

## (d) 64-bit overflow / mask safety

Verdict: **safe for the GPU’s stated (n\le60,k\le8); C code is safe for its (n\le120,k\le12) u128 bounds**.

Evidence in [gpu_pancyc.py](../search/gpu_pancyc.py): `bce[9]` stores cycle-edge masks with shifts (0\ldots n-1\), and `bch[9]` stores chord bits (0\ldots k-1\), so no combined edge mask shifts beyond bit 59 for (n\le60). The guard `(n == 64) ? ~0ULL : ((1ULL << n) - 1)` avoids a shift by 64. The length mask uses `1ULL << (n+1)`, safe at (n\le60). The C code explicitly uses `typedef unsigned __int128 u128`, with edge bits through (n+k-1\le131) not actually safe if (n=120,k=12): this is a real issue. Its declared `MAXN=120, MAXK=12` permits (n+k>128), so the C mask can overflow for those extreme arguments. For the requested (n\le60,k\le8), it is safe.

## Independent (n=25,k=4) result

Verdict: **not completed; unknown**. I wrote [brute25.py](construction/brute25.py), which enumerates the three triangle-normal-form families using the independent Python cycle-space implementation, but the run exceeded the resource/time budget before producing `NONE`. It was stopped; no claim of confirmation is made. The existing C/GPU search claim was not substituted for an independent result.

## Griffin source follow-up

The arXiv e-print was downloaded as [griffin-1312.0274-source](griffin-1312.0274-source). It is an opaque 6,352-byte source payload rather than a readable tar/text archive in the current fetch; no Figure 1 coordinate block could be extracted. Per assignment, reconstruction stops here rather than guessing endpoints.
