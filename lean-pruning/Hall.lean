import Bounds
namespace Erdos1016.Pruning

/-- Coverage by the supplied cycle forms. Completeness of the graph-to-form
enumeration must be established separately before applying this to graphs. -/
def Covers (indices : List Nat) (forms : List Form) (n : Nat) (a : Nat → Nat) : Prop :=
  ∀ l, 3 ≤ l → l ≤ n → ∃ f ∈ forms, length indices a f = l

def reaches (indices : List Nat) (n : Nat) (lo : Nat → Nat) (x y : Nat)
    (f : Form) : Bool :=
  decide (lower indices lo f ≤ y ∧ x ≤ upper indices n lo f ∧
    lower indices lo f ≤ upper indices n lo f)

def Hall (indices : List Nat) (forms : List Form) (n : Nat) (lo : Nat → Nat) : Prop :=
  ∀ x y, 3 ≤ x → x ≤ y → y ≤ n →
    y + 1 - x ≤ (forms.filter (reaches indices n lo x y)).length

theorem hall_necessary (indices : List Nat) (forms : List Form) (n : Nat)
    (lo a : Nat → Nat)
    (bounds : ∀ i ∈ indices, lo i ≤ a i)
    (sum_eq : total indices a = n)
    (covers : Covers indices forms n a) :
    Hall indices forms n lo := by
  intro x y hx hxy hyn
  let wanted := List.range' x (y + 1 - x)
  have subset : wanted ⊆
      (forms.filter (reaches indices n lo x y)).map (length indices a) := by
    intro l hl
    have limits := List.mem_range'_1.mp hl
    have hlow : 3 ≤ l := by omega
    have hhigh : l ≤ n := by omega
    obtain ⟨f, hf, heq⟩ := covers l hlow hhigh
    have interval := length_in_interval indices n lo a f bounds sum_eq
      (by omega) (by omega)
    apply List.mem_map.mpr
    refine ⟨f, ?_, heq⟩
    apply List.mem_filter.mpr
    refine ⟨hf, ?_⟩
    simp only [reaches, decide_eq_true_eq]
    omega
  have card := (List.nodup_range' (s := x) (n := y + 1 - x)).length_le_of_subset subset
  simpa [wanted] using card

theorem filter_length_mono {α : Type} (items : List α) (p q : α → Bool)
    (imp : ∀ a ∈ items, p a = true → q a = true) :
    (items.filter p).length ≤ (items.filter q).length := by
  induction items with
  | nil => simp
  | cons a rest ih =>
    have head := imp a (by simp)
    have tail := ih (fun b hb => imp b (by simp [hb]))
    cases hp : p a <;> cases hq : q a <;>
      simp_all [List.filter] <;> omega

/-- Tightening arc lower bounds cannot turn a failing Hall condition into a
passing one. This justifies the downward-closed pairwise staircase. -/
theorem hall_of_raised (indices : List Nat) (forms : List Form) (n : Nat)
    (lo raised : Nat → Nat)
    (bounds : ∀ i ∈ indices, lo i ≤ raised i)
    (h : Hall indices forms n raised) :
    Hall indices forms n lo := by
  intro x y hx hxy hyn
  have counts := filter_length_mono forms
    (reaches indices n raised x y) (reaches indices n lo x y) (by
      intro f hf passed
      have shrink := intervals_shrink indices n lo raised f bounds
      simp only [reaches, decide_eq_true_eq] at passed ⊢
      omega)
  exact Nat.le_trans (h x y hx hxy hyn) counts

theorem pairwise_hall_necessary (indices : List Nat) (forms : List Form) (n : Nat)
    (lo a : Nat → Nat)
    (bounds : ∀ t ∈ indices, lo t ≤ a t)
    (sum_eq : total indices a = n)
    (covers : Covers indices forms n a) :
    ∀ i j, Hall indices forms n (raisePair lo i j (a i) (a j)) := by
  intro i j
  exact hall_necessary indices forms n _ a
    (actual_pair_is_legal indices lo a i j bounds) sum_eq covers

theorem pairwise_rejection_sound (indices : List Nat) (forms : List Form) (n : Nat)
    (lo a : Nat → Nat) (i j : Nat)
    (bounds : ∀ t ∈ indices, lo t ≤ a t)
    (sum_eq : total indices a = n)
    (rejected : ¬ Hall indices forms n (raisePair lo i j (a i) (a j))) :
    ¬ Covers indices forms n a := by
  intro covers
  exact rejected (pairwise_hall_necessary indices forms n lo a bounds sum_eq covers i j)

#print axioms hall_necessary
#print axioms hall_of_raised
#print axioms pairwise_hall_necessary
#print axioms pairwise_rejection_sound
def hallCheck (indices : List Nat) (forms : List Form) (n : Nat)
    (lo : Nat → Nat) : Bool :=
  (List.range' 3 (n - 2)).all fun x =>
    (List.range' x (n + 1 - x)).all fun y =>
      decide (y + 1 - x ≤ (forms.filter (reaches indices n lo x y)).length)

theorem hallCheck_correct (indices : List Nat) (forms : List Form) (n : Nat)
    (lo : Nat → Nat) :
    hallCheck indices forms n lo = true ↔ Hall indices forms n lo := by
  simp only [hallCheck, List.all_eq_true, decide_eq_true_eq]
  constructor
  · intro h x y hx hxy hyn
    apply h x
    · apply List.mem_range'_1.mpr
      omega
    · apply List.mem_range'_1.mpr
      omega
  · intro h x hx y hy
    have xr := List.mem_range'_1.mp hx
    have yr := List.mem_range'_1.mp hy
    exact h x y (by omega) (by omega) (by omega)

theorem failed_check_rejects (indices : List Nat) (forms : List Form) (n : Nat)
    (lo a : Nat → Nat)
    (bounds : ∀ i ∈ indices, lo i ≤ a i)
    (sum_eq : total indices a = n)
    (rejected : hallCheck indices forms n lo = false) :
    ¬ Covers indices forms n a := by
  intro covers
  have passed := (hallCheck_correct indices forms n lo).mpr
    (hall_necessary indices forms n lo a bounds sum_eq covers)
  rw [rejected] at passed
  contradiction

#print axioms hallCheck_correct
#print axioms failed_check_rejects


/-- A failing pair test excludes all larger values of those two arcs. -/
theorem pair_threshold_rejection_sound
    (indices : List Nat) (forms : List Form) (n : Nat)
    (lo a : Nat → Nat) (i j u v : Nat)
    (bounds : ∀ t ∈ indices, lo t ≤ a t)
    (sum_eq : total indices a = n)
    (hu : u ≤ a i) (hv : v ≤ a j)
    (rejected : hallCheck indices forms n (raisePair lo i j u v) = false) :
    ¬ Covers indices forms n a := by
  apply failed_check_rejects indices forms n (raisePair lo i j u v) a ?_ sum_eq rejected
  intro t ht
  unfold raisePair
  split
  · rename_i hi
    subst t
    exact hu
  · split
    · rename_i hj
      subst t
      exact hv
    · exact bounds t ht

#print axioms pair_threshold_rejection_sound

end Erdos1016.Pruning

