import Mathlib
import Erdos1016.Excess
import Erdos1016.Witness39_40
import Erdos1016.Witness56

open SimpleGraph
namespace Erdos1016

def cs39 : Finset (Sym2 (Fin 39)) := {s(0,2), s(0,18), s(1,12), s(3,19), s(17,20)}
def cs40 : Finset (Sym2 (Fin 40)) := {s(0,5), s(1,5), s(2,30), s(3,10), s(4,11)}
def cs56 : Finset (Sym2 (Fin 56)) := {s(0,2), s(0,53), s(1,39), s(20,39), s(39,48), s(48,53)}
theorem cs39_card : cs39.card = 5 := by decide
theorem cs40_card : cs40.card = 5 := by decide
theorem cs56_card : cs56.card = 6 := by decide

theorem adj39_iff (a b : Fin 39) :
    (adj39 a b = true ∨ adj39 b a = true) ↔
      ((b.val = (a.val + 1) % 39 ∨ a.val = (b.val + 1) % 39) ∨ s(a, b) ∈ cs39) := by
  revert a b
  decide

theorem G39_eq : baseCycle 39 ⊔ SimpleGraph.fromEdgeSet (↑cs39 : Set (Sym2 (Fin 39))) = G39 := by
  ext a b
  simp only [SimpleGraph.sup_adj, baseCycle, G39, SimpleGraph.fromRel_adj,
    SimpleGraph.fromEdgeSet_adj, Finset.mem_coe]
  have h := adj39_iff a b
  unfold adj39 at h
  constructor
  · rintro (⟨hne, hc⟩ | ⟨hm, hne⟩)
    · exact ⟨hne, h.2 (Or.inl hc)⟩
    · exact ⟨hne, h.2 (Or.inr hm)⟩
  · rintro ⟨hne, hadj⟩
    rcases h.1 hadj with hc | hm
    · exact Or.inl ⟨hne, hc⟩
    · exact Or.inr ⟨hm, hne⟩

theorem cs39_disjoint : ∀ e ∈ cs39, e ∉ (baseCycle 39).edgeSet := by
  intro e he
  simp only [cs39, Finset.mem_insert, Finset.mem_singleton] at he
  rcases he with rfl | rfl | rfl | rfl | rfl <;>
    simp [SimpleGraph.mem_edgeSet, baseCycle, SimpleGraph.fromRel_adj]

/-- `h(39) ≤ 5`. -/
theorem pancyclicWithChords_39_5 : PancyclicWithChords 39 5 :=
  ⟨cs39, cs39_card, cs39_disjoint, by rw [G39_eq]; exact isPancyclic_G39⟩

theorem adj40_iff (a b : Fin 40) :
    (adj40 a b = true ∨ adj40 b a = true) ↔
      ((b.val = (a.val + 1) % 40 ∨ a.val = (b.val + 1) % 40) ∨ s(a, b) ∈ cs40) := by
  revert a b
  decide

theorem G40_eq : baseCycle 40 ⊔ SimpleGraph.fromEdgeSet (↑cs40 : Set (Sym2 (Fin 40))) = G40 := by
  ext a b
  simp only [SimpleGraph.sup_adj, baseCycle, G40, SimpleGraph.fromRel_adj,
    SimpleGraph.fromEdgeSet_adj, Finset.mem_coe]
  have h := adj40_iff a b
  unfold adj40 at h
  constructor
  · rintro (⟨hne, hc⟩ | ⟨hm, hne⟩)
    · exact ⟨hne, h.2 (Or.inl hc)⟩
    · exact ⟨hne, h.2 (Or.inr hm)⟩
  · rintro ⟨hne, hadj⟩
    rcases h.1 hadj with hc | hm
    · exact Or.inl ⟨hne, hc⟩
    · exact Or.inr ⟨hm, hne⟩

theorem cs40_disjoint : ∀ e ∈ cs40, e ∉ (baseCycle 40).edgeSet := by
  intro e he
  simp only [cs40, Finset.mem_insert, Finset.mem_singleton] at he
  rcases he with rfl | rfl | rfl | rfl | rfl <;>
    simp [SimpleGraph.mem_edgeSet, baseCycle, SimpleGraph.fromRel_adj]

/-- `h(40) ≤ 5`. -/
theorem pancyclicWithChords_40_5 : PancyclicWithChords 40 5 :=
  ⟨cs40, cs40_card, cs40_disjoint, by rw [G40_eq]; exact isPancyclic_G40⟩

theorem adj56_iff (a b : Fin 56) :
    (adj56 a b = true ∨ adj56 b a = true) ↔
      ((b.val = (a.val + 1) % 56 ∨ a.val = (b.val + 1) % 56) ∨ s(a, b) ∈ cs56) := by
  revert a b
  decide

theorem G56_eq : baseCycle 56 ⊔ SimpleGraph.fromEdgeSet (↑cs56 : Set (Sym2 (Fin 56))) = G56 := by
  ext a b
  simp only [SimpleGraph.sup_adj, baseCycle, G56, SimpleGraph.fromRel_adj,
    SimpleGraph.fromEdgeSet_adj, Finset.mem_coe]
  have h := adj56_iff a b
  unfold adj56 at h
  constructor
  · rintro (⟨hne, hc⟩ | ⟨hm, hne⟩)
    · exact ⟨hne, h.2 (Or.inl hc)⟩
    · exact ⟨hne, h.2 (Or.inr hm)⟩
  · rintro ⟨hne, hadj⟩
    rcases h.1 hadj with hc | hm
    · exact Or.inl ⟨hne, hc⟩
    · exact Or.inr ⟨hm, hne⟩

theorem cs56_disjoint : ∀ e ∈ cs56, e ∉ (baseCycle 56).edgeSet := by
  intro e he
  simp only [cs56, Finset.mem_insert, Finset.mem_singleton] at he
  rcases he with rfl | rfl | rfl | rfl | rfl | rfl <;>
    simp [SimpleGraph.mem_edgeSet, baseCycle, SimpleGraph.fromRel_adj]

/-- `h(56) ≤ 6`. -/
theorem pancyclicWithChords_56_6 : PancyclicWithChords 56 6 :=
  ⟨cs56, cs56_card, cs56_disjoint, by rw [G56_eq]; exact isPancyclic_G56⟩

end Erdos1016
