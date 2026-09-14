import Mathlib
import Erdos1016.Basic
import Erdos1016.Witness
import Erdos1016.ListCycle

/-!
# Kernel-checked pancyclicity of the 38- and 41-vertex witnesses

`G38 = C_38 + {(0,2),(0,18),(1,12),(3,19),(17,20)}` and
`G41 = C_41 + {(4,13),(28,30),(12,26),(17,31),(12,29),(24,27)}` satisfy `IsPancyclic`
(the `Walk.IsCycle` definition of `Erdos1016.Basic`), via the explicit cycle lists of
`Witness.lean` and the bridge `isPancyclic_of_candidates` of `ListCycle.lean`.
Consequently h(38) ≤ 5 and h(41) ≤ 6 for Erdős problem #1016.
-/

open SimpleGraph

namespace Erdos1016

/-- Bool adjacency of `G38` on `Fin 38`. -/
def adj38 (a b : Fin 38) : Bool := adjB 38 chords38 a.val b.val
/-- Bool adjacency of `G41` on `Fin 41`. -/
def adj41 (a b : Fin 41) : Bool := adjB 41 chords41 a.val b.val

theorem adj38_irrefl : ∀ a : Fin 38, adj38 a a = false := by decide
theorem adj41_irrefl : ∀ a : Fin 41, adj41 a a = false := by decide

theorem adj38_spec (a b : Fin 38) (h : adj38 a b = true) : G38.Adj a b := by
  unfold G38
  rw [SimpleGraph.fromRel_adj]
  refine ⟨fun hab => ?_, Or.inl h⟩
  subst hab
  rw [adj38_irrefl] at h
  exact Bool.false_ne_true h

theorem adj41_spec (a b : Fin 41) (h : adj41 a b = true) : G41.Adj a b := by
  unfold G41
  rw [SimpleGraph.fromRel_adj]
  refine ⟨fun hab => ?_, Or.inl h⟩
  subst hab
  rw [adj41_irrefl] at h
  exact Bool.false_ne_true h

/-- The witness cycles of `G38` as lists of `Fin 38`. -/
def cycles38F : List (List (Fin 38)) := cycles38.map (List.map (fun v : ℕ => (⟨v % 38, Nat.mod_lt v (by decide)⟩ : Fin 38)))
/-- The witness cycles of `G41` as lists of `Fin 41`. -/
def cycles41F : List (List (Fin 41)) := cycles41.map (List.map (fun v : ℕ => (⟨v % 41, Nat.mod_lt v (by decide)⟩ : Fin 41)))

set_option maxRecDepth 100000 in
theorem candidates38 : (List.range' 3 (38 - 2)).all (fun ℓ => cycles38F.any (fun l =>
    (l.length == ℓ) && decide l.Nodup && chainB adj38 l && closesB adj38 l)) = true := by decide

set_option maxRecDepth 100000 in
theorem candidates41 : (List.range' 3 (41 - 2)).all (fun ℓ => cycles41F.any (fun l =>
    (l.length == ℓ) && decide l.Nodup && chainB adj41 l && closesB adj41 l)) = true := by decide

/-- `C_38` plus five chords is pancyclic: h(38) ≤ 5. -/
theorem isPancyclic_G38 : IsPancyclic G38 :=
  isPancyclic_of_candidates G38 adj38 adj38_spec cycles38F candidates38

/-- `C_41` plus six chords is pancyclic: h(41) ≤ 6. -/
theorem isPancyclic_G41 : IsPancyclic G41 :=
  isPancyclic_of_candidates G41 adj41 adj41_spec cycles41F candidates41

end Erdos1016
