# Lean witness verification report

## Result

The Lean development kernel-checks explicit pancyclic witnesses on 38, 39, 40, 41, and 56 vertices. The corresponding chord counts are 5, 5, 5, 6, and 6. Thus it formally proves the upper bounds `h(38) ≤ 5`, `h(39) ≤ 5`, `h(40) ≤ 5`, `h(41) ≤ 6`, and `h(56) ≤ 6`.

## Formal layers

`Basic.lean` defines `IsPancyclic` using `SimpleGraph.Walk.IsCycle`. `Witness.lean`, `Witness39_40.lean`, and `Witness56.lean` define Boolean chord adjacency, explicit lists for every length, and finite `decide` checks. `ListCycle.lean` converts list chains into walks and proves `isPancyclic_of_candidates`; `Pancyclic.lean` instantiates it for 38 and 41, while the witness files instantiate it for 39, 40, and 56. `Excess.lean` and `Excess2.lean` express the results as `PancyclicWithChords` statements with finite chord sets and non-cycle-edge proofs.

## Kernel and axiom checks

The candidate coverage checks (`candidates38`, `candidates39`, `candidates40`, `candidates41`, `candidates56`) use `decide` with no `native_decide` or `sorry`. `#print axioms` reports the following expected dependency set for each final excess theorem: `propext`, `Classical.choice`, and `Quot.sound` (ordering can vary). The axioms arise through the general graph/list bridge and finite-set/Sym2 infrastructure; the concrete finite Boolean checks themselves reduce in the kernel.

Relevant final theorem names are `pancyclicWithChords_38_5`, `pancyclicWithChords_41_6`, `pancyclicWithChords_39_5`, `pancyclicWithChords_40_5`, and `pancyclicWithChords_56_6`.

## Build evidence

The project was rebuilt with one BelowNormal process using `lake build`; output ended with `Build completed successfully (8715 jobs)` after the 39/40 and excess wrapper additions. The 56-vertex dedicated check also completed successfully; its `isPancyclic_G56` axiom output was `[propext, Classical.choice, Quot.sound]`.

## Interpretation and limits

These are upper bounds only. They establish existence of chord sets and therefore `h(n) ≤ k`; they do not establish lower bounds or optimality. Lower bounds and exact thresholds rely on the independent search programs under `search/`, together with the independent checks and literature evidence in `papers/`.
