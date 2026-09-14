import Mathlib
import Erdos1016.Basic

/-!
# From vertex lists to cycles

A vertex list `l` with `l.Nodup`, consecutive vertices adjacent (`List.IsChain G.Adj l`), the last
vertex adjacent to the first, and `3 ≤ l.length` yields a `G.Walk v v` that `IsCycle` with
`length = l.length`.  Hence a graph with such a list for every length `3..n` is pancyclic in the
sense of `Erdos1016.IsPancyclic` (which is stated with `SimpleGraph.Walk.IsCycle`).
-/

open SimpleGraph

namespace Erdos1016

variable {V : Type*} {G : SimpleGraph V}

/-- A nonempty chain of adjacent vertices is the support of some walk. -/
theorem exists_walk_of_isChain :
    ∀ (l : List V), l ≠ [] → l.IsChain G.Adj → ∃ (u v : V) (w : G.Walk u v), w.support = l
  | [], hne, _ => absurd rfl hne
  | [a], _, _ => ⟨a, a, Walk.nil, rfl⟩
  | a :: b :: t, _, h => by
      rw [List.isChain_cons_cons] at h
      obtain ⟨u, v, w, hw⟩ := exists_walk_of_isChain (b :: t) (List.cons_ne_nil b t) h.2
      have hu : u = b := by
        have h1 := w.cons_tail_support
        rw [hw] at h1
        exact (List.cons.inj h1).1
      subst hu
      exact ⟨a, v, Walk.cons h.1 w, by rw [Walk.support_cons, hw]⟩

/-- A closed chain with distinct vertices and at least three of them is a cycle. -/
theorem exists_cycle_of_list (l : List V) (h3 : 3 ≤ l.length) (hnd : l.Nodup)
    (hc : l.IsChain G.Adj) (hne : l ≠ []) (hcl : G.Adj (l.getLast hne) (l.head hne)) :
    ∃ (v : V) (c : G.Walk v v), c.IsCycle ∧ c.length = l.length := by
  obtain ⟨u, v, w, hw⟩ := exists_walk_of_isChain l hne hc
  have hu : l.head hne = u := by
    have h2 : l.head? = some u := by
      rw [← hw, List.head?_eq_some_head w.support_ne_nil, w.head_support]
    rw [List.head?_eq_some_head hne] at h2
    exact Option.some.inj h2
  have hv : l.getLast hne = v := by
    have h2 : l.getLast? = some v := by
      rw [← hw, List.getLast?_eq_some_getLast w.support_ne_nil, w.getLast_support]
    rw [List.getLast?_eq_some_getLast hne] at h2
    exact Option.some.inj h2
  rw [hu, hv] at hcl
  have hlen : w.length + 1 = l.length := by
    have := w.length_support
    rw [hw] at this
    omega
  refine ⟨v, Walk.cons hcl w, ?_, ?_⟩
  · rw [Walk.cons_isCycle_iff]
    have hpath : w.IsPath := Walk.IsPath.mk' (hw ▸ hnd)
    refine ⟨hpath, fun hh => ?_⟩
    -- the closing edge s(v,u) would lie on the path `w : Walk u v`, forcing `u` to be the
    -- penultimate vertex, i.e. support[0] = support[length-1], contradicting injectivity for
    -- a path with at least three vertices (Mathlib's argument in
    -- `isCycle_iff_isPath_tail_and_le_length`).
    have h0 : w.support[0]'(by simp) = w.support[w.length - 1]'(by rw [Walk.length_support]; omega) := by
      simp [← List.head_eq_getElem_zero, hpath.eq_penultimate_of_mem_edges hh]
    have hinj := w.isPath_iff_injective_get_support.mp hpath h0
    have h2 : (0 : ℕ) = w.length - 1 := by simpa using congrArg Fin.val hinj
    omega
  · simp only [Walk.length_cons]
    exact hlen

/-- Sufficient condition for `IsPancyclic` in terms of explicit vertex lists. -/
theorem isPancyclic_of_lists {n : ℕ} (G : SimpleGraph (Fin n))
    (ok : ∀ ℓ, 3 ≤ ℓ → ℓ ≤ n → ∃ l : List (Fin n), l.length = ℓ ∧ l.Nodup ∧ l.IsChain G.Adj ∧
      ∃ hne : l ≠ [], G.Adj (l.getLast hne) (l.head hne)) :
    IsPancyclic G := by
  intro ℓ h3 hn
  obtain ⟨l, hl, hnd, hc, hne, hcl⟩ := ok ℓ h3 hn
  obtain ⟨v, c, hcyc, hlen⟩ := exists_cycle_of_list (G := G) l (hl ▸ h3) hnd hc hne hcl
  exact ⟨v, c, hcyc, hlen.trans hl⟩

/-! ### Boolean helpers so that hypotheses can be discharged by `decide`

The adjacency is supplied as an arbitrary Bool function `adj` together with a proof that
`adj a b = true` implies `G.Adj a b`; this keeps kernel evaluation on plain Bool/Nat terms. -/

section Bool
variable (adj : V → V → Bool)

/-- Consecutive vertices adjacent, as a Bool. -/
def chainB : List V → Bool
  | a :: b :: t => adj a b && chainB (b :: t)
  | _ => true

/-- Last vertex adjacent to first, as a Bool (false on the empty list). -/
def closesB (l : List V) : Bool :=
  match l.head?, l.getLast? with
  | some a, some b => adj b a
  | _, _ => false

variable {adj} (hadj : ∀ a b, adj a b = true → G.Adj a b)
include hadj

theorem chainB_spec : ∀ l : List V, chainB adj l = true → l.IsChain G.Adj
  | [], _ => List.isChain_nil
  | [a], _ => List.isChain_singleton a
  | a :: b :: t, h => by
      simp only [chainB, Bool.and_eq_true] at h
      exact List.isChain_cons_cons.2 ⟨hadj a b h.1, chainB_spec (b :: t) h.2⟩

theorem closesB_spec (l : List V) (h : closesB adj l = true) :
    ∃ hne : l ≠ [], G.Adj (l.getLast hne) (l.head hne) := by
  rcases l with _ | ⟨a, t⟩
  · simp [closesB] at h
  · refine ⟨List.cons_ne_nil a t, ?_⟩
    simp only [closesB, List.head?_cons, List.getLast?_eq_some_getLast (List.cons_ne_nil a t)] at h
    exact hadj _ _ h

end Bool

/-- `IsPancyclic` from a finite list of candidate cycles checked by Bool predicates.
`cands` is a list of vertex lists; the hypothesis says that for every length `ℓ` in `3..n` some
candidate has length `ℓ`, no repeated vertex, consecutive adjacency and a closing edge. -/
theorem isPancyclic_of_candidates {n : ℕ} (G : SimpleGraph (Fin n)) (adj : Fin n → Fin n → Bool)
    (hadj : ∀ a b, adj a b = true → G.Adj a b) (cands : List (List (Fin n)))
    (h : (List.range' 3 (n - 2)).all (fun ℓ => cands.any (fun l =>
        (l.length == ℓ) && decide l.Nodup && chainB adj l && closesB adj l)) = true) :
    IsPancyclic G := by
  apply isPancyclic_of_lists
  intro ℓ h3 hn
  have hmem : ℓ ∈ List.range' 3 (n - 2) := by
    rw [List.mem_range'_1]
    omega
  have h1 := (List.all_eq_true.1 h) ℓ hmem
  obtain ⟨l, hl, hprop⟩ := List.any_eq_true.1 h1
  simp only [Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq] at hprop
  exact ⟨l, hprop.1.1.1, hprop.1.1.2, chainB_spec hadj l hprop.1.2, closesB_spec hadj l hprop.2⟩

end Erdos1016
