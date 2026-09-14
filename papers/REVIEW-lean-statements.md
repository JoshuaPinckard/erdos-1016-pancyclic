# Lean statement-faithfulness review

Reviewed read-only: `Erdos1016/Basic.lean`, `Witness.lean`, `ListCycle.lean`, and `Pancyclic.lean`. The source files were not edited. The requested axiom query was run with one BelowNormal Lean process; raw output is [lean-axioms.out](lean-axioms.out).

## (a) `IsPancyclic`

Verdict: **faithful to the intended standard notion, with one scope qualification**.

Evidence: [Basic.lean](../Erdos1016/Basic.lean) defines `IsPancyclic` as `∀ ℓ, 3 ≤ ℓ → ℓ ≤ n → ∃ (v : Fin n) (w : G.Walk v v), w.IsCycle ∧ w.length = ℓ`. Thus the graph has exactly the vertex type `Fin n`, and every length 3 through n is required. `Walk.IsCycle` is Mathlib’s simple-cycle predicate on a closed walk, so repeated vertices are excluded in the usual way.

Qualification: the definition does not explicitly require `n ≥ 3`; for `n<3` the quantified interval is empty, so pancyclicity is vacuous. That is harmless for G38/G41 and standard formulations usually state the order assumption separately. It should not be described as an unconditional non-vacuous notion for all natural n.

## (b) Exactness of `G38`, `G41`, and `adjB`

Verdict: **faithful for the concrete n=38 and n=41 witnesses; generic `adjB` has an n=1 edge-case**.

Evidence: [Witness.lean](../Erdos1016/Witness.lean) defines the exact lists `chords38 := [(0,2),(0,18),(1,12),(3,19),(17,20)]` and `chords41 := [(4,13),(28,30),(12,26),(17,31),(12,29),(24,27)]`. `adjB` is exactly the disjunction of the two modular successor relations and `cs.contains (u,v) || cs.contains (v,u)`. Therefore for `Fin 38`/`Fin 41`, every Hamilton-cycle edge including wraparound `(n-1,0)` is present; listed chords are present in either orientation; no other edge can appear because the disjunction has no other branch.

For concrete n=38/41 there are no loops: `u+1 mod n = u` is impossible, and none of the listed chord pairs is a loop. The source separately proves `adj38_irrefl` and `adj41_irrefl` by `decide`, then uses `SimpleGraph.fromRel` via `adj38_spec`/`adj41_spec`. There is no drop/add behavior from symmetry: the OR of both pair orientations makes the relation symmetric.

Mismatch/qualification: generic `adjB 1 cs u v` can regard the sole modular successor as itself, so it is not generically irreflexive at n=1. This does not affect G38/G41, whose explicit irrefl theorems pass.

## (c) `isPancyclic_of_lists` and `isPancyclic_of_candidates`

Verdict: **the list bridge proves its docstring claim; candidate bridge has no vacuous hypothesis for the concrete uses**.

Evidence: [ListCycle.lean](../Erdos1016/ListCycle.lean) states `isPancyclic_of_lists` with, for every `ℓ` in the required interval, a list of exact length `ℓ`, `Nodup`, adjacent-chain membership, and a closing edge. It invokes `exists_cycle_of_list`, which constructs a closed `G.Walk` and proves `IsCycle` and equal length. `isPancyclic_of_candidates` requires `hadj : adj a b = true → G.Adj a b` and requires `(List.range' 3 (n - 2)).all ... = true`; its local `hmem` proof shows every `3 ≤ ℓ ≤ n` belongs to that range, so the range has exactly the intended lengths.

There is no vacuity in G38/G41: `candidates38` and `candidates41` are separately discharged by `decide`, and their ranges have 36 and 39 lengths respectively. The Bool chain helper checks every consecutive pair; `closesB` checks the final-to-first edge; `decide l.Nodup` checks simplicity of each listed vertex sequence.

## (d) Main witness theorems

Verdict: **not weakened by hidden assumptions**.

Evidence: [Pancyclic.lean](../Erdos1016/Pancyclic.lean) defines `adj38`/`adj41` directly from `adjB`, proves their irreflexivity and adjacency specifications, and then applies `isPancyclic_of_candidates G38 adj38 adj38_spec cycles38F candidates38` and the corresponding G41 term. The candidate lists are concrete closed lists; no axiom, `sorry`, assumption parameter, or unproved external hypothesis appears in either theorem. `cycles38F`/`cycles41F` map each Nat vertex through `% 38`/`% 41`; all literal values are already in range, so this does not alter the intended witness vertices.

The theorem statements prove exactly `IsPancyclic G38` and `IsPancyclic G41`, hence upper-bound witness claims only. They do not prove minimality or h(38)=5/h(41)=6; the file comments correctly say `h(38) ≤ 5` and `h(41) ≤ 6`.

## (e) `#print axioms` output

Command file: [LeanAxioms.lean](LeanAxioms.lean). `lake env lean papers/LeanAxioms.lean` completed successfully. Exact output:

```text
'Erdos1016.isPancyclic_G38' depends on axioms: [propext, Classical.choice, Quot.sound]
'Erdos1016.isPancyclic_G41' depends on axioms: [propext, Classical.choice, Quot.sound]
'Erdos1016.isPancyclic_of_lists' depends on axioms: [propext, Classical.choice, Quot.sound]
'Erdos1016.isPancyclic_of_candidates' depends on axioms: [propext, Classical.choice, Quot.sound]
```

These are standard Mathlib foundational/classical axioms, not project-local admitted theorems. The output does not list `sorryAx`.

## Bottom line

For n=38 and n=41, the Lean statements mean what the project says: exact finite graphs consisting of the n-cycle plus the listed chords are pancyclic in the standard simple-cycle sense. The only identified semantic caveat is that `IsPancyclic` is vacuous for orders below 3 and generic `adjB` is not loop-free at n=1; neither affects the concrete witnesses.
