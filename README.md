# Erdős problem 1016: Lean witnesses

This project formalizes explicit upper-bound witnesses for pancyclic graphs. It uses Lean 4.33.1 and Mathlib v4.33.1.

## Installation and build

Install `elan` from the official Lean installer, then select the pinned toolchain:

```text
elan toolchain install leanprover/lean4:v4.33.1
elan default leanprover/lean4:v4.33.1
```

From this directory, install the Mathlib cache and build:

```text
lake exe cache get
lake build
```

The project root imports every development file through `Erdos1016.lean`.

## File map

- `Basic.lean`: defines `IsPancyclic`, requiring a `Walk.IsCycle` of every length 3 through n.
- `Witness.lean`: defines the 38- and 41-vertex Boolean chord graphs and explicit cycle lists.
- `Witness39_40.lean`: proves `isPancyclic_G39` and `isPancyclic_G40` for the 39/40-vertex witnesses.
- `Witness56.lean`: proves `isPancyclic_G56` for the six-chord 56-vertex witness.
- `ListCycle.lean`: proves the general list-to-walk bridge and `isPancyclic_of_candidates`.
- `Pancyclic.lean`: instantiates the bridge for `isPancyclic_G38` and `isPancyclic_G41`.
- `Excess.lean`: defines `baseCycle`, `PancyclicWithChords`, and proves the 38/41 excess statements.
- `Excess2.lean`: proves `pancyclicWithChords_39_5`, `_40_5`, and `_56_6`.

## Definitions to inspect

From `Basic.lean`:

```lean
def IsPancyclic {n : ℕ} (G : SimpleGraph (Fin n)) : Prop :=
  ∀ ℓ, 3 ≤ ℓ → ℓ ≤ n → ∃ (v : Fin n) (w : G.Walk v v), w.IsCycle ∧ w.length = ℓ
```

From `Witness.lean`:

```lean
def adjB (n : Nat) (cs : List (Nat × Nat)) (u v : Nat) : Bool :=
  (v == (u+1) % n) || (u == (v+1) % n) || cs.contains (u,v) || cs.contains (v,u)
```

From `Excess.lean`:

```lean
def baseCycle (n : ℕ) : SimpleGraph (Fin n) :=
  SimpleGraph.fromRel (fun u v => v.val = (u.val + 1) % n)

def PancyclicWithChords (n k : ℕ) : Prop :=
  ∃ cs : Finset (Sym2 (Fin n)), cs.card = k ∧ (∀ e ∈ cs, e ∉ (baseCycle n).edgeSet) ∧
    IsPancyclic (baseCycle n ⊔ SimpleGraph.fromEdgeSet (↑cs : Set (Sym2 (Fin n))))
```

## Axiom checks

Create a temporary file importing `Erdos1016.Excess2`, add `#print axioms` commands, and run `lake env lean`:

```lean
#print axioms Erdos1016.pancyclicWithChords_38_5
#print axioms Erdos1016.pancyclicWithChords_41_6
#print axioms Erdos1016.pancyclicWithChords_39_5
#print axioms Erdos1016.pancyclicWithChords_40_5
#print axioms Erdos1016.pancyclicWithChords_56_6
```

Expected output for each is a dependency set consisting of `propext`, `Classical.choice`, and `Quot.sound` (the exact ordering may vary). These are theorem dependency reports, not unchecked assumptions; the witness predicates and finite checks are proved by kernel reduction with `decide`.

## Scope of the result

These formalizations prove upper bounds only: the existence statements imply `h(n) ≤ k` (equivalently, the stated number of chords suffices). They do not prove matching lower bounds. Lower-bound and exact-threshold claims come from the independent programs under `search/`, with their separate checks and literature evidence recorded under `papers/`.
