import Std

/-!
Bounds for the pairwise Hall pruning used by the Erdos1016 search.
Only Lean's core/Std library is needed. No sorry, native_decide, or extra axioms.
The graph-to-cycle-form reduction and the executable GPU enumeration are separate
obligations: these theorems concern the arithmetic on an already supplied form.
-/
namespace Erdos1016.Pruning

def selectedSum (indices : List Nat) (mask : Nat → Bool) (a : Nat → Nat) : Nat :=
  match indices with
  | [] => 0
  | i :: rest => (if mask i then a i else 0) + selectedSum rest mask a

def total (indices : List Nat) (a : Nat → Nat) : Nat :=
  selectedSum indices (fun _ => true) a

theorem selectedSum_mono (indices : List Nat) (mask : Nat → Bool)
    (lo hi : Nat → Nat) (h : ∀ i ∈ indices, lo i ≤ hi i) :
    selectedSum indices mask lo ≤ selectedSum indices mask hi := by
  induction indices with
  | nil => simp [selectedSum]
  | cons i rest ih =>
    have hhead := h i (by simp)
    have htail := ih (fun j hj => h j (by simp [hj]))
    cases hm : mask i <;> simp [selectedSum, hm] <;> omega

theorem selectedSum_complement (indices : List Nat) (mask : Nat → Bool)
    (a : Nat → Nat) :
    selectedSum indices mask a + selectedSum indices (fun i => !(mask i)) a =
      total indices a := by
  induction indices with
  | nil => simp [selectedSum, total]
  | cons i rest ih =>
    cases hm : mask i <;> simp [selectedSum, total, hm] at * <;> omega

structure Form where
  mask : Nat
  chords : Nat
deriving DecidableEq, Repr

def length (indices : List Nat) (a : Nat → Nat) (f : Form) : Nat :=
  selectedSum indices (fun i => f.mask.testBit i) a + f.chords

def lower (indices : List Nat) (lo : Nat → Nat) (f : Form) : Nat :=
  max 4 (selectedSum indices (fun i => f.mask.testBit i) lo + f.chords)

def upper (indices : List Nat) (n : Nat) (lo : Nat → Nat) (f : Form) : Nat :=
  n - (selectedSum indices (fun i => !(f.mask.testBit i)) lo - f.chords)

theorem length_in_interval (indices : List Nat) (n : Nat)
    (lo a : Nat → Nat) (f : Form)
    (bounds : ∀ i ∈ indices, lo i ≤ a i)
    (sum_eq : total indices a = n)
    (short : 3 ≤ length indices a f)
    (long : length indices a f ≤ n) :
    lower indices lo f ≤ length indices a f ∧
      length indices a f ≤ upper indices n lo f := by
  have hin := selectedSum_mono indices (fun i => f.mask.testBit i) lo a bounds
  have hout := selectedSum_mono indices (fun i => !(f.mask.testBit i)) lo a bounds
  have hsplit := selectedSum_complement indices (fun i => f.mask.testBit i) a
  unfold lower upper length at *
  omega

theorem intervals_shrink (indices : List Nat) (n : Nat)
    (lo raised : Nat → Nat) (f : Form)
    (bounds : ∀ i ∈ indices, lo i ≤ raised i) :
    lower indices lo f ≤ lower indices raised f ∧
      upper indices n raised f ≤ upper indices n lo f := by
  have hin := selectedSum_mono indices (fun i => f.mask.testBit i) lo raised bounds
  have hout := selectedSum_mono indices (fun i => !(f.mask.testBit i)) lo raised bounds
  unfold lower upper
  omega

def raisePair (lo : Nat → Nat) (i j u v : Nat) : Nat → Nat :=
  fun t => if t = i then u else if t = j then v else lo t

theorem actual_pair_is_legal (indices : List Nat) (lo a : Nat → Nat)
    (i j : Nat) (bounds : ∀ t ∈ indices, lo t ≤ a t) :
    ∀ t ∈ indices, raisePair lo i j (a i) (a j) t ≤ a t := by
  intro t ht
  unfold raisePair
  split <;> rename_i h
  · subst t
    exact Nat.le_refl _
  · split
    · rename_i hj
      subst t
      exact Nat.le_refl _
    · exact bounds t ht

theorem pair_interval_contains_solution (indices : List Nat) (n : Nat)
    (lo a : Nat → Nat) (f : Form) (i j : Nat)
    (bounds : ∀ t ∈ indices, lo t ≤ a t)
    (sum_eq : total indices a = n)
    (short : 3 ≤ length indices a f)
    (long : length indices a f ≤ n) :
    lower indices (raisePair lo i j (a i) (a j)) f ≤ length indices a f ∧
      length indices a f ≤ upper indices n (raisePair lo i j (a i) (a j)) f :=
  length_in_interval indices n _ a f
    (actual_pair_is_legal indices lo a i j bounds) sum_eq short long

#print axioms length_in_interval
#print axioms intervals_shrink
#print axioms pair_interval_contains_solution
end Erdos1016.Pruning

