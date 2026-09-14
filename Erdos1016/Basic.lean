import Mathlib

/-!
# Erdős Problem #1016 (Bondy 1971): minimum excess of a pancyclic graph

`h n` is the least number of chords that must be added to an `n`-cycle to obtain a
pancyclic graph.  Bondy claimed `log₂(n-1) - 1 ≤ h n ≤ log₂ n + log* n + O(1)`.
Only the trivial counting lower bound is known.  Target: `h n - log₂ n → ∞`.
-/

open SimpleGraph

namespace Erdos1016

/-- A graph on `Fin n` is pancyclic if it has a cycle of every length `3 ≤ ℓ ≤ n`. -/
def IsPancyclic {n : ℕ} (G : SimpleGraph (Fin n)) : Prop :=
  ∀ ℓ, 3 ≤ ℓ → ℓ ≤ n → ∃ (v : Fin n) (w : G.Walk v v), w.IsCycle ∧ w.length = ℓ

/-- Sanity check that the toolchain and Mathlib load: the complete graph on 3 vertices
has an edge between distinct vertices. -/
example : (⊤ : SimpleGraph (Fin 3)).Adj 0 1 := by decide

end Erdos1016
