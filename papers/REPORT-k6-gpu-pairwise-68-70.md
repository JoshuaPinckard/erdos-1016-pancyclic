# Levels 68, 69, 70 exhausted on the GPU: no 6-chord pancyclic C_n + chords at n = 68, 69, 70

Manager (f4d1e0af), 2026-09-19. Claim files: `papers/verification/`. Code:
`search/shapecsp/pairwise-prod/` (the frozen production snapshot, byte-exact to
commit f63f9f3 of `search/shapecsp/pairwise/`). Status line at the end of this
file says which levels are complete; the tables are the output of
`search/shapecsp/pairwise/render_claims.py` and are regenerated, not typed.

## Statement

For each level n in {68, 69, 70}, every shape of the k = 6 census manifest
`search/shapecsp/gpu-blast/n{N}.jsonl` (every b from 6 to 12) has been
exhausted with zero pancyclic compositions found:

* tiers b = 6..10 by the unrestricted plan (every composition of the shape's
  arc lengths, GPU kernel `gpu_search.py`, state `search/shapecsp/gpu-state-n{N}-b{9,10}.json`),
  verified by `search/shapecsp/verify_tier_exhaustion.py`, which re-derives the
  unit set from the hashed census manifest and compares rank totals;
* tiers b = 11, 12 by the pairwise plan (the pairwise-admissible set A of
  `search/shapecsp/pairwise/SPEC.md`, a proved superset of every pancyclic
  composition), verified by `pairwise-prod/verify_tier_combined.py --rebuild -1`,
  which re-derives the unrestricted-done shapes from the unrestricted state,
  re-derives the pairwise unit plan from the tier manifest, checks the counted
  compositions against the manifest totals shape by shape, and rebuilds every
  pairwise shape's DP tables from its census row and compares the hashes.

Consequently h(n) > 6 for n = 68, 69, 70 once all three levels show EXHAUSTED
below, and t_6 is not 68, 69 or 70: t_6 = 67 or 71 <= t_6 <= 88 (the upper end
from the CPU descent, `REPORT-k6-level89-91-verify.md`). Level 71 and the
interleaved descent 87..72 are queued on the same pipeline (chains v9 laptop,
v12 desktop; `papers/REPORT-levels-72-89-tables.md`).

## Why the pairwise tiers are exact

`bound.hall_ok` is a necessary condition for pancyclicity and is monotone
non-increasing in the arc lower bounds, so raising two lower bounds to the
values a pancyclic composition takes keeps it true; hence every pancyclic
composition lies in A = { a : sum a = n, lows <= a <= hi, a_j <= T[i][j][a_i]
for every ordered pair }. The DP-state tables enumerate A exactly (prefix rank
over the first b-2 arcs, the last two enumerated in-thread); the kernel counts
every composition it visits and the claim tool requires the counts to equal
the manifest totals for every shape. Independent review (Opus, six findings,
all closed; forged-tier attacks D1-D4 rejected by the claim tool; D3, a shape
forged to claim an empty A, rejected only by the source rebuild, which is why
the claim tool refuses anything but `--rebuild -1`): `papers/REPORT-review-pairwise.md`.
Exact-set evidence: `test_pairwise_tables.py` (2,430,144 compositions equal to
the reference recursion, 524,231 prefix blocks, 0 lost SAT of 175,383 in the
unrestricted scan), `test_pairwise_gpu.py` (kernel visits equal the CPU
sequence, 27 family witnesses found), `test_pairwise_carry.py` (63/64-bit
coverage carry bit-exact against the CPU, carry mutant detected on every case,
carry-critical witness flips).

## Claim files

<!-- render_claims.py output; regenerate with: python search/shapecsp/pairwise/render_claims.py --levels 68,69,70 -->

Unrestricted plan (b below the cutover), unit set re-derived from the census manifest:

| tier | units | ranks covered = manifest | hits | exact_match | claim file |
|---|---|---|---|---|---|
| n=68 b=6 | 1 of 1 | 5,949,147 = manifest | 0 | True | n68-b6-unrestricted.json |
| n=68 b=7 | 17 of 17 | 1,620,406,333 = manifest | 0 | True | n68-b7-unrestricted.json |
| n=68 b=8 | 473 of 473 | 387,641,502,225 = manifest | 0 | True | n68-b8-unrestricted.json |
| n=68 b=9 | 1711 of 1711 | 10,418,519,119,461 = manifest | 0 | True | n68-b9-unrestricted.json |
| n=68 b=10 | 2302 of 2302 | 90,425,326,969,618 = manifest | 0 | True | n68-b10-unrestricted.json |
| n=69 b=6 | 1 of 1 | 6,471,002 = manifest | 0 | True | n69-b6-unrestricted.json |
| n=69 b=7 | 6 of 6 | 574,262,263 = manifest | 0 | True | n69-b7-unrestricted.json |
| n=69 b=8 | 381 of 381 | 349,337,446,776 = manifest | 0 | True | n69-b8-unrestricted.json |
| n=69 b=9 | 1542 of 1542 | 10,698,677,586,699 = manifest | 0 | True | n69-b9-unrestricted.json |
| n=69 b=10 | 2188 of 2188 | 99,523,794,187,552 = manifest | 0 | True | n69-b10-unrestricted.json |
| n=70 b=6 | 1 of 1 | 7,028,847 = manifest | 0 | True | n70-b6-unrestricted.json |
| n=70 b=7 | 6 of 6 | 630,054,289 = manifest | 0 | True | n70-b7-unrestricted.json |
| n=70 b=8 | 272 of 272 | 278,069,214,477 = manifest | 0 | True | n70-b8-unrestricted.json |
| n=70 b=9 | 1312 of 1312 | 10,382,946,734,499 = manifest | 0 | True | n70-b9-unrestricted.json |
| n=70 b=10 | 3040 of 3040 | 104,015,764,237,632 = manifest | 0 | True | n70-b10-unrestricted.json |

Pairwise plan (cutover tiers), claim tool verify_tier_combined.py --rebuild -1:

| tier | shapes | unrestricted-done shapes | pairwise shapes | pairwise units | compositions (manifest = counted) | rebuilt shapes | mismatches | hits | exact_match | claim file |
|---|---|---|---|---|---|---|---|---|---|---|
| n=68 b=11 | 1257 | 474 | 783 | 3543 of 3543 | 18,790,392,772,211 = counted | 783 | 0 | 0 | True | n68-b11-combined.json |
| n=68 b=12 | 298 | 0 | 298 | 1738 of 1738 | 8,073,813,826,147 = counted | 298 | 0 | 0 | True | n68-b12-combined.json |
| n=69 b=11 | 1234 | 73 | 1161 | 5565 of 5565 | 29,700,459,821,233 = counted | 1161 | 0 | 0 | True | n69-b11-combined.json |
| n=69 b=12 | 296 | 0 | 296 | 1909 of 1909 | 9,083,689,300,924 = counted | 296 | 0 | 0 | True | n69-b12-combined.json |
| n=70 b=11 | 1138 | 469 | 669 | 3698 of 3698 | 20,260,638,830,081 = counted | 669 | 0 | 0 | True | n70-b11-combined.json |
| n=70 b=12 | 281 | 0 | 281 | 2011 of 2011 | 9,768,224,097,653 = counted | 281 | 0 | 0 | True | n70-b12-combined.json |

* n = 68: EXHAUSTED. Every tier of the gpu-blast census manifest is covered: b < 11 by the unrestricted plan (unit sets re-derived, rank totals equal), b >= 11 by the pairwise plan (every pairwise shape's tables rebuilt from its gpu-blast row with matching hashes, unrestricted-done shapes re-derived from the unrestricted state). Zero hits in every tier.
* n = 69: EXHAUSTED. Every tier of the gpu-blast census manifest is covered: b < 11 by the unrestricted plan (unit sets re-derived, rank totals equal), b >= 11 by the pairwise plan (every pairwise shape's tables rebuilt from its gpu-blast row with matching hashes, unrestricted-done shapes re-derived from the unrestricted state). Zero hits in every tier.
* n = 70: EXHAUSTED. Every tier of the gpu-blast census manifest is covered: b < 11 by the unrestricted plan (unit sets re-derived, rank totals equal), b >= 11 by the pairwise plan (every pairwise shape's tables rebuilt from its gpu-blast row with matching hashes, unrestricted-done shapes re-derived from the unrestricted state). Zero hits in every tier.

## What is machine-checked in Lean, and what is not

Lean 4 (v4.33.1, Mathlib v4.33.1), project root `lakefile.toml`, library
`Erdos1016`; `lake build` clean on 2026-09-19 23:52 (8743 jobs, no `sorry`),
and `lake env lean Axioms.lean` reports every listed theorem depending only on
`propext`, `Classical.choice`, `Quot.sound`.

* Kernel-checked upper bounds: `pancyclicWithChords_38_5`, `_39_5`, `_40_5`
  (h(38), h(39), h(40) <= 5), `pancyclicWithChords_41_6`, `_56_6`, and, new
  tonight, `family_pancyclic_41_67 : ∀ n, 41 ≤ n → n ≤ 67 → PancyclicWithChords n 6`
  (`Erdos1016/Family.lean`), i.e. h(n) <= 6 for every n in 41..67, from 27
  per-level certificates `Erdos1016/Family/W41.lean` .. `W67.lean` in which the
  family `(0,2)(0,n-7)(1,13)(3,n-6)(4,31)(n-8,n-5)` is given one explicit vertex
  list per cycle length and Lean re-derives, by `decide`, that each list is a
  cycle of the stated length in the stated graph, that the six chords are
  distinct non-cycle edges, and that the Bool adjacency equals `baseCycle n ⊔
  fromEdgeSet cs`. The lists were produced by `search/k6/gen_family_lean.py`
  (networkx simple cycles) and are certificates only; nothing computed by that
  script is trusted.
* NOT in Lean, and not formalisable at this size: every non-existence result.
  h(n) >= 6 for n >= 41 (the k = 5 shape search at levels 41..58), t_6 <= 88
  (the CPU descent 89..111) and tonight's h(n) >= 7 for n = 68, 69, 70 are
  exhaustive computations; their evidence is the claim files above, the
  independent verifiers, the frozen code snapshot, the review's forged-tier
  attacks and the level-67 blind control, not a kernel proof. A Lean proof of
  the reduction itself (a pancyclic C_n + 6 chords is a subdivision of one of
  the census shapes; Hall is necessary and monotone; A is a superset) would
  shrink the trusted computation to "the enumeration of A visited every
  composition", but the enumeration would still be trusted, not checked.

## Provenance

* Chains: desktop `run-chain-desktop-v{8..12}.cmd` (69/11, 68/12, 69/12, then
  the level-67 blind control, levels 89 and 88, then even levels 86..72),
  laptop `deploy/laptop/run-chain-laptop-v{6..9}.sh` (68/11, 70/11, 70/12,
  level 71, then odd levels 87..73). Both run `pairwise-prod/gpu_state_runner_pairwise.py`
  since 18:25 PDT; every unit records its composition count in the state file,
  states are lock-guarded and written atomically.
* Tables: built on both machines from the same census rows; hash-identical
  across machines (cross-machine compare of 609 shapes at levels 88/89; the six
  production tiers were built on both machines with equal hashes at the
  cutover). Manifests are timing-free and byte-reproducible.
* Rates: 3.4 to 4.7e9 compositions per GPU-second per card (RTX-class desktop
  card and the laptop card); a b = 11 tier at n = 69 took about 2.5 GPU-hours.
* Controls: the runner refuses to start unless both real witnesses (n = 67 and
  n = 56) are found at their prefix ranks and 44 sampled ranks unrank
  identically on CPU and GPU with flags equal to `search/verify.py`. A blind
  positive control over the whole of level 67 (every shape, every b, known to
  contain the family witness (0,2)(0,60)(1,13)(3,61)(4,31)(59,62) at shape
  20889, b = 11) runs on the desktop after the production tiers; its verdict
  `papers/verification/control-n67-b{B}.json` is written by
  `pairwise/check_control.py` and must show the witness found and every hit
  re-verified by `search/verify.py`.
* Claim tool provenance: pairwise-prod is byte-exact to f63f9f3 (checked by
  `pairwise/freeze_prod.py` and independently by the reviewer); a rebuild of
  shipped shapes from three tiers reproduces the manifest hashes; the
  worktree's later arc-order commits (917defa, 4b7aa19) are NOT in the
  production snapshot and keep v1 tables loadable and rebuildable in their own
  format (4504 files loaded, 30 rebuilt, 0 mismatches).

## Efficiency work, measured

The arc-order idea (put the two widest arcs last so more compositions are
enumerated in-thread per prefix) was implemented behind a v2 table format and
measured on the full n = 68 tiers (`papers/REPORT-pairwise-order.md`): the
specified widest-pair rule is a net loss (0.970x on b = 11, 0.883x on b = 12,
because completions lie on the line v + w = n - s, so the narrower arc bounds
them, not the product of the ranges); no cheap rule reaches 1.3x; building
every completion pair and keeping the best does reach 1.42x (b = 11) and 1.79x
(b = 12) in prefixes at a cost of about 17 core-hours of table builds for the
two tiers. It is shipped as `--order measured`, not as a default, and not used
for the claims above. A GPU A/B has not been run (the cards are on production).

## Status

* n = 68: EXHAUSTED. Every tier of the gpu-blast census manifest is covered: b < 11 by the unrestricted plan (unit sets re-derived, rank totals equal), b >= 11 by the pairwise plan (every pairwise shape's tables rebuilt from its gpu-blast row with matching hashes, unrestricted-done shapes re-derived from the unrestricted state). Zero hits in every tier.
* n = 69: EXHAUSTED. Every tier of the gpu-blast census manifest is covered: b < 11 by the unrestricted plan (unit sets re-derived, rank totals equal), b >= 11 by the pairwise plan (every pairwise shape's tables rebuilt from its gpu-blast row with matching hashes, unrestricted-done shapes re-derived from the unrestricted state). Zero hits in every tier.
* n = 70: EXHAUSTED. Every tier of the gpu-blast census manifest is covered: b < 11 by the unrestricted plan (unit sets re-derived, rank totals equal), b >= 11 by the pairwise plan (every pairwise shape's tables rebuilt from its gpu-blast row with matching hashes, unrestricted-done shapes re-derived from the unrestricted state). Zero hits in every tier.

All three levels are complete: every tier of the census manifest at n = 68, 69, 70 is exhausted with zero hits, so h(n) > 6 for n = 68, 69, 70 and t_6 is 67 or lies in 71..88.
The T ledger (T543, T573) carries the checkpoints.
