# Number-to-source index for `pancyclic-exact-values.md`

Every number appearing in the draft, with the exact project file it was taken
from. Paths are relative to `C:\Users\ToolsEnabled-Dev\Desktop\erdos1016\`.

## Section 1 — Introduction

| Number / claim | Source |
|---|---|
| $\log_2(n-1)-1\le h(n)\le\log_2n+\log_*n+O(1)$ (Bondy's claimed bounds) | `papers/1312.0274.txt`, "Claim 1. (Bondy [3])" |
| Jia's Conjecture 1.16 ($g(n)=n+\log_2n+O(1)$) and the Erdős belief ($h(n)-\log_2n\to\infty$) are **incompatible**; the note states the tension, not both as holding | the two are formal negations of each other on the error term. Erdős side: erdosproblems.com/1016, quoted in Section 1. Jia side: Conj. 1.16 as transcribed in `papers/REPORT-oeis-and-jia.md`. The only claimed upper bound, $\log_2n+\log_*n+O(1)$, carries a growing correction and so sits on the Erdős side. Nothing in this note bears on which is right |
| Jia Thm 1.13: $n+\log_2n-1\le g(n)\le n+\frac32\log_2n+1$ | `papers/REPORT-oeis-and-jia.md` (OCR of `papers/Lai-Liu-2014-survey.pdf`, page 3/printed p.53) |
| Jia Cor 1.15: $g(n)=n+\log_2n+O(\log_2\log_2n)$ | `papers/REPORT-oeis-and-jia.md` (OCR, page 4/printed p.54) |
| Jia Conj 1.16: $g(n)=n+\log_2n+O(1)$ | `papers/REPORT-oeis-and-jia.md` (OCR, page 4/printed p.54) |
| GKW16 Ch. 4.5 attribution, **corrected in this revision** to a hedged, secondary-sourced claim rather than flat fact | Tao's exact hedge "that seems to exist" — `papers/REPORT-lit-4.md`, "Costliest finding first" section, quoted in full; GKW16 itself "Not obtained" via two independent methods — `papers/REPORT-bondy-construction.md`, opening bullet list; AK's "we emulate (an approximation of) the construction in [6]" — `papers/REPORT-bondy-construction.md`, quoting `2308.01564.txt` Section 3. (The earlier draft's unhedged claim came from `papers/REPORT-lit-1.md`'s "the public abstract confirms" line, which this revision no longer treats as sufficient given the later, more careful `REPORT-bondy-construction.md` found no chapter content at all — only the title "Minimal Pancyclicity" via the publisher TOC.) |
| Griffin's lower-bound proof and exact table to $n\le37$ | `papers/1312.0274.txt`, abstract and Table 1 |
| Alon–Krivelevich: $\mathrm{Pex}(G)=(1+o(1))\log_2n$ w.h.p. for $p\ge(1+o(1))\ln n/n$ | `papers/REPORT-lit-2.md`, "Alon–Krivelevich, 'Sparse pancyclic subgraphs of random graphs'" section |
| TerenceTao comment, 18 Oct 2025, "consensus... except for very small n where there is some work by George, Marr, and Wallis" | `papers/REPORT-lit-4.md`, "Costliest finding first" section (fetched verbatim from erdosproblems.com/forum/discuss/1016) |

## Section 2 — Exact values table

| $n$ | $h(n)$ | $m(n)$ | Source |
|---:|---:|---:|---|
| 3–37 | — | — | `papers/1312.0274.txt`, Table 1 (all 35 rows transcribed verbatim) |
| 3–22 (cross-check only) | — | — | `papers/oeis/A105206-extension.md`, Section 1 reconciliation table (OEIS A105206 published data matches Griffin term-for-term) |
| 38 | 5 | 43 | `search/n38k5-A0.txt` ("WITNESS n=38 k=5 : (0,2) (0,18) (1,12) (3,19) (17,20)"); cross-checked in `papers/REVIEW-search.md` ("(n=38)... 36 lengths = 3..38") |
| 39 | 5 | 44 | `search/hn_k5.csv`, row `39,5,WITNESS,"(0,2) (0,18) (1,12) (3,19) (17,20)",3201,61561098` |
| 40 | 5 | 45 | `search/hn_k5.csv`, row `40,5,WITNESS,...,7424,132830426`; exhaustively confirmed by `search/gpu-40-5-all.txt` (`tested=14373209608`, 10 witnesses found) |
| 41 | 6 | 47 | `search/gpu-41-5.txt` (full-run log: progress lines to `15147912850/15147912850 (100.0%)`, then "NONE n=41 k=5 tested=17615450195 seconds=845") for the $k=5$ elimination — a single complete enumeration by one program, not independently replicated; see the Section 3.4 rows below; `search/gpu-41-5d.txt` ("NONE n=41 k=5 tested=17615450195 seconds=18") is a re-invocation that reloaded the finished state file. `search/ls-41-6.txt` ("WITNESS n=41 k=6 : (4,13) (28,30) (12,26) (17,31) (12,29) (24,27)") for the witness; witness cross-checked in `papers/REVIEW-search.md` ("(n=41)... 39 lengths = 3..41") |

## Section 2.1 — Thresholds

| Number | Source |
|---|---|
| $t_1,\dots,t_5 = 5,8,14,24,40$ | `notes/01-subdivision-reformulation.md`, "Update 2026-09-14 evening" section |
| **$h(n)=6$ exactly for every $41\le n\le67$; $m(n)=n+6$ there; no monotonicity assumed** | *Lower half* $h(n)\ge6$ for all $n\ge41$: the $k=5$ shape/CSP levels `search/shapecsp/level-k5-n41.txt` … `level-k5-n58.txt`, all 18 reading `sat=0 gaveup=0` (read individually here), together with the $k=5$ ceiling $n\le58$ from `search/shapecsp/shape-census.txt` row `5 | 1236 | … | 56 (distinct 56)` (cap $=F+2$); a contiguous clean block running to the ceiling excludes every $n$ at or above its foot (`search/shapecsp/level.py` docstring). *Upper half* $h(n)\le6$ for $41\le n\le67$: the family $F_n$ below. The two halves meet, so the value is exact |
| The family $F_n=(0,2)(0,n-7)(1,13)(3,n-6)(4,31)(n-8,n-5)$ is pancyclic at every one of the 27 values $n=41..67$, and fails at $n=68$ missing exactly $[33]$ | re-checked here for all 27 plus $n=68$ as a negative control with `search/verify.py` (networkx `simple_cycles`): `papers/draft/verify-family-41-68-20260915.txt`, 27 rows "pancyclic" and the $n=68$ row "NOT pancyclic … [33]" |
| Spectrum of $F_n$ is exactly $[3,32]\cup[n-34,n]$, hence pancyclic iff $n\le67$ | symbolic cycle certificate `family-certificate.md` / `family-cycle-certificate.json` (Builder findings review, 2026-09-15), which lists an explicit cycle in terms of $n$ for every length in both intervals; checked against computed length sets here at $n=41,45,50,55,60,65,66,67,68,69,70$ — equality in every case, with the missing set growing $[33]$, $[33,34]$, $[33,34,35]$ at $n=68,69,70$ |

| $67\le t_6\le93$; $h(n)\le6$ for $41\le n\le67$; $h(n)\ge6$ for $n\ge66$ by counting | lower end and $h(n)\le6$: the Section 6.3 witness table below; upper end: the contiguous exhausted shape/CSP block $94\le n\le111$ — `search/shapecsp/level-k6-n94.txt` … `level-k6-n111.txt`, each `sat=0 gaveup=0`, with $111$ the largest per-shape cap at $k=6$ (`search/shapecsp/shape-census.txt`, row `6 | 21878 | … | 109 (distinct 109)`, cap $=F+2$), analysed in `papers/REPORT-shape-csp.md`. $N_0=2^{k+1}+1=129$ at $k=6$ (`papers/REPORT-cyclecounts.md`) is now only the trivial prior bound. $n=92$ and $n=93$ are undecided ($0$-byte level files) and counted on neither side, so a descent that closes them lowers this end. Counting step: $2^{5+1}-1=63<n-2$ iff $n\ge66$, recomputed here |

## Section 2.2 — Five extremal 5-chord graphs on 40 vertices

| Number / claim | Source |
|---|---|
| All ten raw 5-chord witnesses on $n=40$ | `search/gpu-40-5-all.txt`, the ten `WITNESS n=40 k=5` lines and `tested=14373209608 witnesses=10 seconds=390` |
| Reduction to 5 classes under rotation+reflection, and the gap/cycle/length table | `notes/01-subdivision-reformulation.md`, the five-row chord table and "Every one has exactly one shared endpoint..." paragraph |
| Ten labelled graphs, **five** dihedral classes, but only **four** isomorphism types: rows 4 and 5 are isomorphic, the other nine pairs are not | computed here with `networkx.is_isomorphic` over all ten pairs of the tabulated representatives; the witnessing map sends row 4's chords $(0,4)$ and $(0,5)$ onto cycle edges of row 5's presentation, i.e. it does not preserve the Hamilton cycle, which is why the two presentations differ while the graphs agree. Consistency check: the cycle count is an isomorphism invariant and rows 4 and 5 both show 48 |
| Gap profiles at $n=8,14,24$ | `notes/01-subdivision-reformulation.md`, "Same shape at earlier thresholds:" line |

## Section 3 — Method

| Claim / quote | Source |
|---|---|
| Triangle case split (modes A/B/C), exact quoted text | `search/pancyc.c`, header comment block, lines 6–13 |
| "Same case split as pancyc.c" | `search/gpu_pancyc.py`, module docstring, lines 2–3 |
| Cycle-space basis/XOR/connectivity description, exact quoted text | `search/pancyc.c`, header comment block, lines 15–18 |
| Pruning-bound description | `search/pancyc.c`, header comment lines 20–23, and the `bound` computation in function `rec` |
| `unsigned __int128`, $n+k\le128$ safety note, "in practice... $n\le60,k\le6$" | `search/pancyc.c`, reviewer note comment, lines 25–26 |
| $n=38$ shard files, one per residue class | `search/n38k5-A0.txt` .. `n38k5-A7.txt`, `n38k5-BC.txt` (file listing and contents) |
| GPU kernel: 64-bit masks, $n\le60,k\le8$ | `search/gpu_pancyc.py`, module docstring line 6, and `KERNEL` source using `unsigned long long`/`unsigned int` |
| Colex unranking via binomial table, exact quoted comment | `search/gpu_pancyc.py`, `KERNEL` source, "unrank colex r-combination of {0..M-1}" and `binom_table()` |
| Resumable JSON state file, `gpu-state-{n}-{k}.json` | `search/gpu_pancyc.py`, `load_state`/`save_state` functions |
| `tested=17615450195` is exactly the candidate count of the three-mode case split at $n=41,k=5$ (so the walk was complete, and identical totals across programs mean the same enumeration, nothing more) | recomputed in `papers/REPORT-record-integrity.md` from `search/gpu_pancyc.py`'s `main` (modes A, B, C; $\binom{778}{4}=15{,}147{,}912{,}850$ for mode A) — total $17{,}615{,}450{,}195$, matching `search/gpu-41-5.txt`, `search/gpu-41-5d.txt` and `search/k6/gpu128-41-5.txt`. (An earlier revision of this row described the total as "cumulative across resumed runs" and pointed at `search/hn_k5.csv`'s $n=41$ rows; those rows are produced by the CPU shard runner `search/run_shards.ps1`, not by the GPU program, and are corrected below.) |
| `search/gpu-41-5.txt` is one uninterrupted complete walk (not a resumed stitch-up) | `search/gpu-41-5.txt`, progress lines from `67108864/15147912850 (0.4%) 2s` through `15147912850/15147912850 (100.0%) 719s`, then the `NONE` line |
| The second `NONE` at $n=41,k=5$ is a port of the same algorithm, not an independent implementation | `search/k6/gpu_pancyc128.py`, module docstring: "128-bit (two-word) port of search/gpu_pancyc.py ... Nothing else about the algorithm changes"; its output `search/k6/gpu128-41-5.txt` ends "NONE n=41 k=5 tested=17615450195 seconds=531" |
| The CPU shard run at $n=41,k=5$ aborted with no output | `search/hn_k5.csv`, row `41,5,ABORTED-no-output-processes-died,,8044,0`; `search/sh-41-A0.txt` … `sh-41-A7.txt`, `sh-41-BC.txt` all 0 bytes (tracked); provenance of the file's rows in `search/hn_k5-README.md` |
| Two `NONE` rows with `tested=0` in `search/hn_k5.csv` are not evidence and are quarantined | `search/hn_k5-README.md` (original lines `41,5,NONE,,66,0` and `41,5,NONE,,187,0` quoted verbatim; now `INVALID-NONE-tested-zero-processes-died`); mechanism: `search/run_shards.ps1` appends `NONE` with the summed `tested=` of shard outputs, which is `0` when every shard died without writing |
| The from-scratch direct-DFS GPU replication of the $n=41,k=5$ elimination is unfinished ($739{,}246{,}080$ of $15{,}147{,}912{,}850$ mode-A ranks, $0$ hits) | `papers/REVIEW-independent-gpu.md`, "n=41, k=5" section: "the exhaustive b=2 total remains UNKNOWN pending continuation from the corrected checkpoint"; raw slices `papers/construction/gpu41b2s0.out`, `papers/construction/indep-gpu41.log`, `papers/construction/indep-gpu41b2-corrected.log` (tracked) |
| No lower bound is formalised in Lean | `Axioms.lean` (tracked), comment: "The matching LOWER bounds (no k-chord pancyclic graph on n vertices) are NOT formalised here; they rest on the exhaustive search programs in search/." |
| `search/localsearch.py` method (randomized perturbation, missing-length score) | `search/localsearch.py`, module docstring and `search`/`missing`/`valid` functions |
| `search/verify.py` uses `networkx.simple_cycles` | `search/verify.py`, `cycle_lengths` function |
| `papers/construction/check.py` independent cycle-space implementation | `papers/construction/check.py`, `basis`/`cycle_length`/`spectrum` functions |
| `papers/construction/check.py` reconfirms the three witnesses | `papers/REVIEW-search.md`, "Independent results from check.py" section |
| `papers/construction/indep.c` is "deliberately no cycle-space XOR" (DFS-based) | `papers/construction/indep.c`, header comment line 1 |
| `papers/construction/indep.c` hard-codes the three witnesses in its `witnesses` mode | `papers/construction/indep.c`, `main` function, the `if(!strcmp(av[1],"witnesses"))` branch |
| `isPancyclic_of_lists`/`isPancyclic_of_candidates` general bridge (list → `Walk.IsCycle`) | `Erdos1016/ListCycle.lean`, theorems `exists_cycle_of_list`, `isPancyclic_of_lists`, `isPancyclic_of_candidates` |
| `isPancyclic_G38 : IsPancyclic G38`, `isPancyclic_G41 : IsPancyclic G41` | `Erdos1016/Pancyclic.lean`, full file (chords38/41 match `search/n38k5-A0.txt` and `search/ls-41-6.txt` exactly) |
| `lake build Erdos1016` completes with 0 errors | independently re-run this session: `lake build Erdos1016 > lake-build-verify.log`, tail shows `Build completed successfully (8711 jobs)` (style-linter warnings only, no `sorry`); log deleted after inspection, not committed |
| Axioms `[propext, Classical.choice, Quot.sound]` for both `isPancyclic_G38` and `isPancyclic_G41` | independently re-run this session via a throwaway `lake env lean` invocation (mirroring the project's pre-existing `Axioms.lean`), output: `'Erdos1016.isPancyclic_G38' depends on axioms: [propext, Classical.choice, Quot.sound]` and the same for `_G41`; temp file deleted after inspection, not committed |
| `PancyclicWithChords n k` definition and `pancyclicWithChords_38_5`/`_41_6` | `Erdos1016/Excess.lean`, full file |
| `isPancyclic_G56` for chords `(0,2)(0,53)(1,39)(20,39)(39,48)(48,53)` | `Erdos1016/Witness56.lean`, full file (chords match `search/k6/witnesses.csv` row `56,...` exactly) |
| `isPancyclic_G39`, `isPancyclic_G40` | `Erdos1016/Witness39_40.lean`, full file (chords match `search/n38k5-A0.txt`'s $n=38$ chord shape at $n=39$, and `search/hn_k5.csv`'s $n=40$ row, exactly) |
| `pancyclicWithChords_39_5`, `pancyclicWithChords_40_5`, `pancyclicWithChords_56_6` | `Erdos1016/Excess2.lean`, full file |
| `lake build Erdos1016 Erdos1016.Witness56` completes, 8713 jobs, 0 errors | independently re-run this session; log inspected then deleted, not committed |
| Axioms `[propext, Classical.choice, Quot.sound]` for `pancyclicWithChords_38_5`, `pancyclicWithChords_41_6`, `isPancyclic_G56` | independently re-run this session via a throwaway `lake env lean` invocation; temp file deleted after inspection, not committed |
| `lake build Erdos1016.Excess2` completes, 8713 jobs, 0 errors | independently re-run this session (separate invocation from the row above); log inspected then deleted, not committed |
| Axioms `[propext, Classical.choice, Quot.sound]` for `pancyclicWithChords_39_5`, `pancyclicWithChords_40_5`, `pancyclicWithChords_56_6` | independently re-run this session via a throwaway `lake env lean` invocation; temp file deleted after inspection, not committed |
| $h(n)\ge5$ for $n=38..41$ follows from pure counting alone (no exhaustive-search citation needed) | recomputed directly: Griffin's Corollary 1 ($2^{k+1}-1$ cycle ceiling, `papers/1312.0274.txt`) gives ceiling $31$ at $k=4$; $n-2\ge36>31$ for all of $n=38..41$ |

| Colex-unranking corroboration, `failures=0` across $r\in\{2,3,4\}$, $M\in\{10,50,200,779\}$ | `papers/REVIEW-gpu-corroboration.md`, "1. Colex unranking" section, quoting `construction/unrank.out`'s `SUMMARY seed=20260914 failures=0` |
| Direct-DFS re-confirmation of all three witnesses ($n=38,40,41$) | `papers/REVIEW-independent.md`, "Witness re-verification" section, `CHECK n=38/40/41 ... pancyclic=yes` |
| $n=24$: $26{,}974{,}255$ tested, $15$ raw witnesses, $2$ classes | `papers/REVIEW-independent.md`, "n=24 and n=25 enumeration" section |
| $n=25$: $35{,}303{,}774$ tested, $0$ witnesses | `papers/REVIEW-independent.md`, same section |
| Random sampling: $2{,}000{,}000$ samples at $n=41,k=5$, $0$ hits; positive control $n=24,k=4$, $1$ hit in $2{,}000{,}000$ | `papers/REVIEW-gpu-corroboration.md`, "2. Random direct-DFS corroboration" section |

## Section 3.5 — Shape/CSP exact algorithm

| Number / claim | Source |
|---|---|
| Shape = cycle on the $b\le2k$ chord endpoints plus the $k$ chords, enumerated up to $D_b$ over all $b$ including degenerate families | `search/shapecsp/shapes.py`, `shapes(k)`; `papers/REPORT-shape-csp.md`, "The algorithm" |
| Cycle lengths are $0/1$ linear forms $L_f(a)=\sum_{i\in A_f}a_i+\lvert X_f\rvert$; cycle space of $H$ has dimension $k+1$ | `search/shapecsp/shapes.py`, `cycle_forms(b, chords)`; `papers/REPORT-shape-csp.md`, "The algorithm" |
| Shape counts $3,14,103,1236,21878$ for $k=2..6$; $k=3$ split $5$ non-degenerate $+$ $9$ degenerate; $k=6$ $97.5\%$ degenerate | `search/shapecsp/shape-census.txt`, rows "2 \| 3 \| 2 \| 1", "3 \| 14 \| 5 \| 9", "4 \| 103", "5 \| 1236", "6 \| 21878 \| 554 \| 21324" |
| GMW13's "14 types of graph" at three chords, matching the $k=3$ shape count | `papers/REPORT-griffin-method.md`, quoting GMW13: "There are 14 types of graph: AAAi, AAAii, AABi, AABii, AAC, ABBi, ABBii, ABC, ACC, BBBi, BBBii, BBC, BCC, CCC"; GMW13 arc-length forms "a+b+1, c+d+1" quoted in the same file |
| Max cycles per shape $7,15,29,56,109$ for $k=2..6$ (equal to $M(k)$); largest $k=6$ per-shape cap $111$ | `search/shapecsp/shape-census.txt`, "max cycles" column; `papers/REPORT-shape-csp.md`, "Second finding" ($111$) |
| Two solvers: CP-SAT and C branch-and-bound with exact greedy matching; interval-Hall counterexample at $n=8$ | `search/shapecsp/solve.py`, `search/shapecsp/bb.c`, `search/shapecsp/bound.py:hall_ok`; `papers/REPORT-shape-csp.md`, "A correction worth recording" |
| $t_2=8,t_3=14,t_4=24$ reproduced with `gaveup_records=0`; witnessing shapes and arcs | `papers/REPORT-shape-csp.md`, "Positive control", lines `RESULT t_2 = 8 gaveup_records=0`, `RESULT t_3 = 14 ...`, `RESULT t_4 = 24 ...`; CP-SAT cross-run `search/shapecsp/control-k2-k5.log` (also "new best n=40" at $k=5$) |
| 201 random (shape, arcs) pairs vs `networkx.simple_cycles`, 0 mismatches | `search/shapecsp/gates-green.txt`, "PASS cycle forms reproduce the true cycle-length multiset :: 201 graphs, 0 mismatches" |
| Gate suite mutation: RED with `rng = [2*k]` (`FAIL t_4 == 24 :: got 22`, exit 1), GREEN restored (`ALL GATES PASS`, exit 0) | `search/shapecsp/gates-red.txt`, `search/shapecsp/gates-green.txt`; `papers/REPORT-shape-csp.md`, "Gates and their mutation check"; re-run in this revision: `python search/shapecsp/test_shapecsp.py` → `ALL GATES PASS`, 41 s |
| $n=56$ witness has 7 branch vertices, vertex 39 carries three chords | `papers/REPORT-shape-csp.md`, "Costliest finding" |
| $k=5$ ladder: `sat=0 gaveup=0` at every level $n=58..41$ | `search/shapecsp/k5-levels.log`, all 18 `LEVEL k=5` lines; not yet written up in `papers/REPORT-shape-csp.md`, so Section 3.4's replication status is left unchanged |
| $k=6$ ladder in progress: levels $n=110..97$ `sat=0 gaveup=0` at time of writing | `search/shapecsp/k6-levels.log` as of 2026-09-14 17:26 (last completed level file `search/shapecsp/level-k6-n97.txt`); provisional, not used for the stated bracket |

## Section 4 — Subdivision lemma and cycle-count context

| Claim / quote | Source |
|---|---|
| Subdivision lemma statement, corrected form ($A\cup(B+(n-s))\supseteq[3,n]$) | `notes/01-subdivision-reformulation.md` (post-2026-09-14-correction version); correction driven by `papers/REVIEW-notes01.md`'s Section 1 counterexample, re-verified computationally in the review's Addendum §1 |
| Multigraph/digon caveat (chord-joined arc endpoints give $2\in B$) | `papers/REVIEW-notes01.md`, Addendum §2 (verified against $n=8,(0,2),(0,5)$) |
| Consequence 1 (counting exactly balanced; $s\le2^k+1$), including the $K=\varnothing$ derivation of the $2^k-1$ vs. $2^k$ asymmetry | `notes/01-subdivision-reformulation.md`, "Consequences" bullet 1 (bound), with the $K=\varnothing$ derivation added per the referee report's required change, reconstructing `papers/REVIEW-notes01.md` §2's reasoning directly in the draft text rather than only cross-referencing it |
| "Counting can improve the constant but not the growing correction" ($M(k)=\Theta(2^k)$ under any counting refinement) | derived in this revision from Shi's/Rautenbach–Stella's own stated results (`papers/REPORT-cyclecounts.md`) per the referee report's required change 7, replacing the earlier absolute "counting never helps" claim that was in tension with the Rautenbach–Stella paragraph two subsections later |
| Consequence 2, corrected largest-arc bound ($m\le(n-2)/2$ non-joined, $m\le(n-1)/2$ joined; $n=38$ general floor $s\ge20$, witness value $s=21$) | `papers/REVIEW-notes01.md`, Addendum §3 (supersedes the original flat $m\le(n-3)/2,s\ge21$ claim, refuted by an $n=8$ counterexample in the review's Section 3) |
| Consequence 3, wall inequality $m_j\le2^{k-j+c_j}$ with stretch-multigraph/$c_j$ defined | `notes/01-subdivision-reformulation.md` (corrected version) and `papers/REVIEW-notes01.md`, Addendum §5, confirming the argument is now complete via the standard even-subgraph/cycle-space-dimension fact $2^{E-V+c}$ |
| $M(k)$ table for $k=1..10$: $3,7,15,29,56,109,213,401,783,1484$ | `papers/REPORT-cyclecounts.md`, "Exact M(k)" table |
| Entringer–Slater: $2^{r-1}\le\phi(r)\le2^r$, conjectured $\phi(r)\sim2^{r-1}$ | `papers/REPORT-cyclecount-asymptotics.md`, "What is actually conjectured" section |
| Aldred–Thomassen: $C(G)\le\frac{15}{16}2^r$ | `papers/REPORT-cyclecount-asymptotics.md`, "General simple graphs: later improvements" section |
| "$M(k)/2^k\to1$" inherited-conjecture framing, no proof located | `papers/REPORT-cyclecount-asymptotics.md`, "Conjecture verdict" section |

## Section 5 — Observations and questions

| Number | Source |
|---|---|
| $t_k/2^{k+1}$ ratios $1.25,1.00,0.875,0.75,0.625$ | `notes/01-subdivision-reformulation.md`, "Thresholds t_k..." line; recomputed here directly from $t_k$ and $2^{k+1}$ as a arithmetic check (both match) |
| $N_0=2^{k+1}+1=5,9,17,33,65$ | `papers/REPORT-cyclecounts.md`, "Count-to-order comparison" table, column `N0 trivial` |
| $t_k=2\,\mathrm{Fib}(k+3)-2$ for $k=2..5$, values $8,14,24,40$ | **origin corrected in this revision**: `papers/REPORT-bondy-construction.md`, "An unsourced numerical observation" section — not, as an earlier draft stated, newly derived in this note. Arithmetic independently re-checked here against the $t_k$ values above |
| "Two-parameter family," only $k=4,5$ independent of the fit's own construction | `papers/REPORT-bondy-construction.md`, same section, quoted "four data points fitting a two-parameter family" |
| Additive recursion $t_k=t_{k-1}+t_{k-2}+2$ fails at $k=3$ ($15\ne14$) | `papers/REPORT-bondy-construction.md`, same section, quoted "this does not hold at k=3, t_2+t_1+2=8+5+2=15 != 14, off by one" |
| Fibonacci prediction $t_6=66$ (now refuted) | `papers/REPORT-bondy-construction.md`, extrapolated one step; refuted by the $n=67$ witness below |
| Rival form $t_k=2^{k-2}(10-k)$, exact at $k=2..5$, predicting $t_6=64$ (now refuted) | `papers/PLAN-next-steps.md`, "a rival 2-parameter formula fits equally and disagrees at t_6"; arithmetic re-checked here ($1\cdot8,2\cdot7,4\cdot6,8\cdot5=8,14,24,40$; $16\cdot4=64$); refuted by the $n=65$ witness below |
| Every integer three-term recurrence fitting $8,14,24,40$: $5a+3b=8$, $(a,b,c)=(1+3t,1-5t,2-2t)$, $t_6=66-2t$; "every even value" is a property of this family only | `papers/NOTE-fit-underdetermination.md`, "Statement" and "Caveat, stated precisely"; the two linear constraints and their difference re-derived here |
| Bracket $67\le t_6\le93$ (the prior bound $129=2^7+1$ is superseded) | lower end: the $n=67$ witness of Section 6.3 (`search/k6/witnesses-v2.csv`, `search/k6/verify-67-gpu-joint.txt`, re-run in `papers/draft/verify-rerun-20260914.txt`); upper end: the contiguous shape/CSP levels $n=94$ to $n=111$, all `sat=0 gaveup=0` (`search/shapecsp/level-k6-n94.txt` … `level-k6-n111.txt`; aggregate log `search/shapecsp/k6-levels.log` carries every row except $n=94,95$, which were run separately). The block, not any single level, is what establishes it: eligibility is decided at each cutoff by cap-and-Hall necessary conditions, which are not monotone in $n$, so a shape feasible at $n_0$ is refuted only by the level whose cutoff is exactly $n_0$ (`search/shapecsp/level.py` docstring, "Cite the block, never a single level"; the earlier mis-citation is recorded in `papers/REPORT-shape-csp.md` section 0a). $111$ is the largest cap over all $21878$ shapes, so no level above it is needed. The prior bound was $N_0=2^{k+1}+1$ from `papers/REPORT-cyclecounts.md`'s "Count-to-order comparison" table at $k=6$ |
| Odd witnesses ($n=65,67$) refute every member of the integer family | `papers/NOTE-fit-underdetermination.md`, "A witness at n=65 would be sharper than either named fit anticipates"; witnesses in `search/k6/witnesses-v2.csv` |
| Griffin's Conjecture 1 ($m(n)<m(n+1)$), Proposition 2 ($m(n+1)\le m(n)+2$) | `papers/1312.0274.txt`, "Conjecture 1. m(n) < m(n + 1) for all n >= 3" and "Proposition 2. m(n + 1) <= m(n) + 2" |
| Wallis's Questions 1 and 2, exact wording | `papers/Wallis-2014-IWOCA-open-problems.pdf`, fetched directly from `https://tomasz-radzik.github.io/IWOCA/problems/Wallis2014.pdf` (HTTP 200) and read in full; "1. Is it always true that m(v) <= m(v+1)?... 2. Find a good upper bound for m(v)." |
| Sridharan (1978) claimed exact $m(v)$ for all $v$, shown wrong ($m(13)=17$ claimed vs. $m(13)=16$ actual) | `papers/Wallis-2014-IWOCA-open-problems.pdf`, "The paper [3] claims to give exact values of m(v) for all v, but they have been proven wrong; for example, it is claimed that m(13) = 17, but an example with m(13) = 16 is given in [1]"; cross-checked against this draft's own Section 2 table, which gives $m(13)=16$ from Griffin's Table 1 |

## Section 6 — Extremal structure and near-misses

| Number / claim | Source |
|---|---|
| 6.1 recap of the five $n=40$ extremal graphs | same sources as "Section 2.2" above; not re-derived |
| $n{=}24\to25$ insertion table, all 8 rows (chords, missing lengths) | `papers/PROOF-n25-k4.md`, Section 5's two per-graph tables, computed directly with `search/verify.py`'s `networkx.simple_cycles` method during that task; largest-arc values ($m{=}10$ for both $G_1,G_2$) independently recomputed and corrected in this session (an earlier draft of `PROOF-n25-k4.md` mis-stated one as $m{=}11$; fixed there before this citation) |
| Mirrored missing-length sets $\{4,7,11,23\},\{5,13,21\},\{15\},\{9,19\}$ | same table; cross-checked by direct comparison across the two graphs' rows |
| $n=56$ witness $(0,2)(0,53)(1,39)(20,39)(39,48)(48,53)$ | `papers/REPORT-k6-upper.md`, "Costliest finding first"; raw data `search/k6/witnesses.csv` row `56,...` |
| $n=67$ witness $(0,2)(0,60)(1,13)(3,61)(4,31)(59,62)$, so $t_6\ge67$; its four confirmations | `search/k6/witnesses-v2.csv` row `67,...`; `search/k6/verify-67-gpu-joint.txt` ("pancyclic [3, 4, ..., 67]"); `papers/REPORT-k6-gpu-joint.md`, "Result in one paragraph" (cyclespace.py, GPU r=0 with the near-miss control, manager's separate evaluator); re-run here in `papers/draft/verify-rerun-20260914.txt` |
| Witness table $n=57..67$ (chords and provenance) | $57$: `search/k6/coord-57.txt` ("WITNESS n=57 k=6"); $58,59,60$: `search/k6/smart-57-70.txt` ("n=58: WITNESS", "n=59: WITNESS", "n=60: WITNESS"), $60$ also `search/k6/climb-60-72.txt` ("FINAL n=60 missing=0"); $61$: `search/k6/sweep2-61-34.txt` ("IMPROVE n=61 missing=0 chords=(0,2)(0,58)(1,44)(3,57)(28,53)(53,58)"); $62..67$: `search/k6/witnesses-v2.csv`, all rows; every one re-run with `search/verify.py` in `papers/draft/verify-rerun-20260914.txt` ("pancyclic", missing `[]`) |
| Family $(0,2)(0,n-7)(1,13)(3,n-6)(4,31)(n-8,n-5)$ pancyclic for $n=64..67$, missing $[33]$ at $68$, $[33,34]$ at $69$, ... | `papers/REPORT-k6-gpu-joint.md`, "The structure and how far it lifts" table; $n=68$ member re-run here: `papers/draft/verify-rerun-20260914.txt`, "68 ... NOT pancyclic", missing `[33]` |
| Inner-chord sweep $(1,a)(4,b)$ does not repair $n=68$; 2-of-6 sweep at $n=68$ complete, $36{,}481{,}725$ candidates, no witness; 3-of-6 in flight | `papers/REPORT-k6-gpu-joint.md`, same section and "Neighbourhoods swept" table (row "68 ... 2 ... 36,481,725 ... 0") |
| $n=66$ witness found after $22{,}335{,}424{,}500$ candidates, 15 of 20 slot subsets, seed $(0,2)(0,63)(1,13)(3,62)(4,31)(58,63)$ missing $[57]$ | `papers/REPORT-k6-gpu-joint.md`, "How they were found" and "Seeds" table |
| `gkw-K4.txt`'s "n=36: PANCYCLIC" row is not a six-chord statement | the instantiation uses vertex $36$, which does not exist on $C_{36}$. Both readings recomputed here: literally it adds a $37$th vertex and then misses length $5$; modulo $n$ it collapses to the **five**-chord graph $C_{36}+(0,2)(2,5)(5,10)(10,19)(0,19)$, which is pancyclic and agrees with $h(36)=5$ in Griffin's Table 1. The same out-of-range vertex invalidated the $n=36$ row of `search/k6/witnesses.csv`, removed in this revision; the file now validates with 85 rows and zero out-of-range vertices |
| Binary-shortcut recipe pancyclic at $n=40$ only (**not** also at $n=36$ — see the row above), missing only length 5 on $[37,69]$; recipe's exact chord formulas | `papers/REPORT-k6-upper.md`, "(a) Structured enumeration with geometric gaps" section; raw data `search/k6/gkw-K4.txt`; **attribution corrected in this revision** to Alon–Krivelevich's paraphrase of GKW (`papers/REPORT-bondy-construction.md`, "The explicit recipe" section, quoting AK's Definition 3 and Section 3 verbatim), not to GKW16 directly |
| Recipe undershoots $t_k$ by 50%–12.5% for $k=2..5$ | `papers/REPORT-bondy-construction.md`, "Verdict on the comparison" section, the `u(k)` vs. `t_k` table |
| Earlier $n=66$ direct attempt: missing count driven from 20 to 3 ($\{5,7,8\}$), single-chord local optimum $(0,2)(0,48)(1,40)(11,41)(44,47)(47,52)$ — historical, superseded by the $n=66$ witness | `papers/REPORT-k6-upper.md`, "Additional... direct attack on n=66" section; `search/k6/strict-66.txt`, `search/k6/coord-66.txt` |

## Notes on sourcing discipline

* [Shi94] and [RS05] were also never obtained as full text (per
  `papers/REPORT-lit-1.md`'s search audit) — only publisher abstracts and
  Griffin's own paper quoting their exact theorem statements were seen. This
  is a milder version of the GKW16 problem above (the actual theorem
  statements, not just a paraphrase, were seen), but is recorded here for the
  same reason: [Gr13] and [AK25] are the only two references in this draft
  read in full.
* Every $n\le37$ value is Griffin's, transcribed directly from the local copy of
  his paper, not re-derived. Where OEIS A105206 also publishes a value
  ($n\le22$), the cross-check is reported in `papers/oeis/A105206-extension.md`,
  not treated as a second independent source of the same number (OEIS's data is
  itself presumably downstream of George–Marr–Wallis/Griffin, not an independent
  computation — this project has not established otherwise).
* Every $n\ge38$ *witness* in Section 2's table is backed by a witness file
  plus all three independent verifiers listed in Section 3.3 and the Lean
  proofs, cross-referenced in `papers/REVIEW-search.md` and
  `papers/REVIEW-independent.md`. The one *elimination* ($n=41,k=5$, giving
  $h(41)>5$) was backed by a single complete run of one program and a port of
  that program; it has since been **independently replicated by a structurally
  different method** — the shape/arc-length CSP, which enumerates subdivision
  shapes rather than chord sets and shares no code with `gpu_pancyc.py`:
  `search/shapecsp/level-k5-n41.txt` reads
  `LEVEL k=5 n=41 shapes=1236 eligible=308 sat=0 gaveup=0`. A single level is
  sufficient for a statement about one $n$, because Hall is a necessary
  condition evaluated at that same $n$, so any shape feasible at $41$ is
  eligible at the $n=41$ level. The earlier asymmetry between witnesses and
  this elimination is correspondingly reduced, and the draft's abstract and
  Section 3.4 now state the replication rather than its absence. The
  from-scratch direct-DFS GPU run (`indep_gpu.py`) is still unfinished and
  would be a third independent exhaustive path.
* The Jia (1996) statements are OCR output from a scanned secondary source
  (`papers/Lai-Liu-2014-survey.pdf`), not Jia's original paper, which could not
  be located; `papers/REPORT-oeis-and-jia.md` flags the one place (a coefficient
  in a discarded intermediate theorem, not used in this draft) where the OCR
  itself was ambiguous.
* The Fibonacci fit, the rival fit and the recurrence-family underdetermination
  argument are cited to `papers/REPORT-bondy-construction.md`,
  `papers/PLAN-next-steps.md` and `papers/NOTE-fit-underdetermination.md`
  respectively; the draft's own contribution is only the arithmetic re-check.
  Both named fits are reported as refuted, not as live predictions, since the
  2026-09-14 revision.

## Evidence reachability (2026-09-14 record-integrity pass)

`.gitignore` excludes `search/*.txt`, `search/k6/*.txt`, `*.out`, `*.err`,
`*.log`, `ax*.lean` and `papers/**/*.pdf`, which had left several files this
index names as primary evidence outside the repository. The following files
are now explicitly un-ignored and tracked (see `papers/REPORT-record-integrity.md`
for the `git ls-files` proof and per-file sizes):

* `search/n38k5-A0.txt` … `n38k5-A7.txt`, `n38k5-BC.txt` (the $n=38$ shard outputs, 70–73 bytes each)
* `search/ls-41-6.txt` (the $n=41,k=6$ witness, 67 bytes)
* `search/gpu-41-5.txt` (the complete 64-bit $n=41,k=5$ elimination log, 12,685 bytes)
* `search/k6/gpu128-41-5.txt` (the 128-bit port's log, 12,871 bytes)
* `search/sh-41-A0.txt` … `sh-41-A7.txt`, `sh-41-BC.txt` (the aborted CPU shard outputs, 0 bytes each)
* `search/k6/coord-66.txt`, `search/k6/strict-66.txt`, `search/k6/gkw-K4.txt` (Sections 5–6 raw data)
* `search/k6/climb-60-72.txt` (402 bytes), `search/k6/coord-57.txt` (199), `search/k6/smart-57-70.txt` (488), `search/k6/sweep2-61-34.txt` (300), `search/k6/verify-67-gpu-joint.txt` (323) — the $k=6$ search and verification logs this index cites for the $n=57..67$ witnesses. Un-ignored and tracked in the 2026-09-15 pass; before it they were cited here but excluded by `search/k6/*.txt` and so unreachable from a clone.
* `papers/construction/unrank.out`, `papers/construction/gpu41b2s0.out`, `papers/construction/indep-gpu41.log`, `papers/construction/indep-gpu41b2-corrected.log`, `papers/construction/random41-1.out`, `papers/construction/random41-2.out` (the corroboration artifacts behind `papers/REVIEW-gpu-corroboration.md` and `papers/REVIEW-independent-gpu.md`)
* `Axioms.lean` (the project's axiom-audit file, quoted above)

After the 2026-09-15 pass, exactly two cited files are **not** tracked, and
deliberately so: they are third-party published PDFs, and the repository's
`papers/*.pdf` exclusion is a redistribution decision, not a size one. Every
other path this index cites returns a row from `git ls-files` (audit re-run
2026-09-15 over all 86 file paths named in this document; see
`papers/CHANGES.md`). They are accounted for by size and
SHA-256 instead:

| File | Size (bytes) | SHA-256 |
|---|---:|---|
| `papers/Lai-Liu-2014-survey.pdf` | 589,233 | `fd8361d68030e8805e6960e40ed96a0d31b913e36f2b141f6f1bb4ed1b52ec61` |
| `papers/Wallis-2014-IWOCA-open-problems.pdf` | 177,398 | `d94ab4060e444f3692f7a086e5cefaeb125b7e4b7274edaa9f98742005d98863` |

(`papers/1312.0274.txt` and `papers/2308.01564.txt`, the text extractions
this index actually quotes from, were already tracked.)
