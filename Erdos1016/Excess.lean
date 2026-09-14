import Mathlib
import Erdos1016.Basic
import Erdos1016.Pancyclic

/-!
# The pancyclic excess, stated in the paper's language

`PancyclicWithChords n k` says: there is a set of exactly `k` chords (edges not on the cycle)
whose addition to the `n`-cycle gives a pancyclic graph.  So `h(n) ≤ k` in the notation of
Erdős problem #1016.  We prove `PancyclicWithChords 38 5` and `PancyclicWithChords 41 6`
from the kernel-checked witnesses of `Pancyclic.lean`.
-/

open SimpleGraph

namespace Erdos1016

/-- The `n`-cycle on `Fin n`: `u ~ v` iff they differ by one modulo `n`. -/
def baseCycle (n : ℕ) : SimpleGraph (Fin n) :=
  SimpleGraph.fromRel (fun u v => v.val = (u.val + 1) % n)

/-- `h(n) ≤ k`: some set of `k` non-cycle edges makes the `n`-cycle pancyclic. -/
def PancyclicWithChords (n k : ℕ) : Prop :=
  ∃ cs : Finset (Sym2 (Fin n)), cs.card = k ∧ (∀ e ∈ cs, e ∉ (baseCycle n).edgeSet) ∧
    IsPancyclic (baseCycle n ⊔ SimpleGraph.fromEdgeSet (↑cs : Set (Sym2 (Fin n))))

def cs38 : Finset (Sym2 (Fin 38)) := {s(0,2), s(0,18), s(1,12), s(3,19), s(17,20)}
def cs41 : Finset (Sym2 (Fin 41)) := {s(4,13), s(28,30), s(12,26), s(17,31), s(12,29), s(24,27)}

theorem cs38_card : cs38.card = 5 := by decide
theorem cs41_card : cs41.card = 6 := by decide

/-- The Bool adjacency of `G38` agrees with "cycle edge or chord of `cs38`". -/
theorem adj38_iff (a b : Fin 38) :
    (adj38 a b = true ∨ adj38 b a = true) ↔
      ((b.val = (a.val + 1) % 38 ∨ a.val = (b.val + 1) % 38) ∨ s(a, b) ∈ cs38) := by
  revert a b
  decide

theorem adj41_iff (a b : Fin 41) :
    (adj41 a b = true ∨ adj41 b a = true) ↔
      ((b.val = (a.val + 1) % 41 ∨ a.val = (b.val + 1) % 41) ∨ s(a, b) ∈ cs41) := by
  revert a b
  decide

theorem G38_eq : baseCycle 38 ⊔ SimpleGraph.fromEdgeSet (↑cs38 : Set (Sym2 (Fin 38))) = G38 := by
  ext a b
  simp only [SimpleGraph.sup_adj, baseCycle, G38, SimpleGraph.fromRel_adj,
    SimpleGraph.fromEdgeSet_adj, Finset.mem_coe]
  have h := adj38_iff a b
  unfold adj38 at h
  constructor
  · rintro (⟨hne, hc⟩ | ⟨hm, hne⟩)
    · exact ⟨hne, h.2 (Or.inl hc)⟩
    · exact ⟨hne, h.2 (Or.inr hm)⟩
  · rintro ⟨hne, hadj⟩
    rcases h.1 hadj with hc | hm
    · exact Or.inl ⟨hne, hc⟩
    · exact Or.inr ⟨hm, hne⟩

theorem G41_eq : baseCycle 41 ⊔ SimpleGraph.fromEdgeSet (↑cs41 : Set (Sym2 (Fin 41))) = G41 := by
  ext a b
  simp only [SimpleGraph.sup_adj, baseCycle, G41, SimpleGraph.fromRel_adj,
    SimpleGraph.fromEdgeSet_adj, Finset.mem_coe]
  have h := adj41_iff a b
  unfold adj41 at h
  constructor
  · rintro (⟨hne, hc⟩ | ⟨hm, hne⟩)
    · exact ⟨hne, h.2 (Or.inl hc)⟩
    · exact ⟨hne, h.2 (Or.inr hm)⟩
  · rintro ⟨hne, hadj⟩
    rcases h.1 hadj with hc | hm
    · exact Or.inl ⟨hne, hc⟩
    · exact Or.inr ⟨hm, hne⟩

theorem cs38_disjoint : ∀ e ∈ cs38, e ∉ (baseCycle 38).edgeSet := by
  intro e he
  simp only [cs38, Finset.mem_insert, Finset.mem_singleton] at he
  rcases he with rfl | rfl | rfl | rfl | rfl <;>
    simp [SimpleGraph.mem_edgeSet, baseCycle, SimpleGraph.fromRel_adj]

theorem cs41_disjoint : ∀ e ∈ cs41, e ∉ (baseCycle 41).edgeSet := by
  intro e he
  simp only [cs41, Finset.mem_insert, Finset.mem_singleton] at he
  rcases he with rfl | rfl | rfl | rfl | rfl | rfl <;>
    simp [SimpleGraph.mem_edgeSet, baseCycle, SimpleGraph.fromRel_adj]

/-- `h(38) ≤ 5`. -/
theorem pancyclicWithChords_38_5 : PancyclicWithChords 38 5 :=
  ⟨cs38, cs38_card, cs38_disjoint, by rw [G38_eq]; exact isPancyclic_G38⟩

/-- `h(41) ≤ 6`. -/
theorem pancyclicWithChords_41_6 : PancyclicWithChords 41 6 :=
  ⟨cs41, cs41_card, cs41_disjoint, by rw [G41_eq]; exact isPancyclic_G41⟩

end Erdos1016
