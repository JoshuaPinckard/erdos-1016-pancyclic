# Erdős Problem #1016: minimal pancyclic graphs with six chords

AI agents worked on [Erdős Problem #1016](https://www.erdosproblems.com/1016) and determined the minimum edge count of pancyclic graphs exactly on a new range. This repository holds their proofs, search code, claim files and reports, plus a one-page paper.

**Paper:** [`paper/main.pdf`](paper/main.pdf) (source [`paper/main.tex`](paper/main.tex)). It is a working draft.

## Results

A graph on n vertices is *pancyclic* if it has a cycle of every length 3, ..., n. Let m(n) = n + h(n) be the fewest edges of a pancyclic graph on n vertices, so h(n) is the fewest chords that make the cycle C_n pancyclic. Let t_k be the largest n with h(n) ≤ k.

1. **h(n) = 6 for every 41 ≤ n ≤ 67**, so m(n) = n + 6 there, and t_5 = 40.
   - *Upper bound, checked in Lean 4:* for 41 ≤ n ≤ 67, C_n plus the chords {0,2}, {0,n−7}, {1,13}, {3,n−6}, {4,31}, {n−8,n−5} is pancyclic (`Erdos1016.family_pancyclic_41_67`). Its cycle lengths are exactly [3,32] ∪ [n−34,n], so it fails at n = 68, where only length 33 is missing.
   - *Lower bound, exhaustive computation:* no C_n plus 5 chords is pancyclic for any n ≥ 41.
2. **t_6 = 67 or t_6 ∈ {72, ..., 79, 81, 83, 84, 85}.** Exhaustive computation shows no 6-chord pancyclic graph on n ∈ {68, 69, 70, 71, 80, 82} or on any n ≥ 86. Levels 72–79, 81 and 83 were not run. Level 84 lacks its b = 11 tier and level 85 its b = 10 tier.
3. **A second 6-chord pancyclic graph on 67 vertices**, not isomorphic to the family member: {0,27}, {18,30}, {28,37}, {29,37}, {31,38}, {32,39}. A blind control run of the GPU pipeline found it.

### Earlier and parallel work

- Griffin (arXiv:1312.0274, 2013) determined m(n) for n ≤ 37.
- m(38) = 43, m(39) = 44 and m(40) = 45 were first published by P. White and Claude, [Erdős #1016 working report](https://www.erdosproblemaday.com/report/1016), 2026-07-29.
- m(41) = 47 was first published in [Robinfxa/JSP-000846](https://github.com/Robinfxa/JSP-000846) on 2026-09-17, with a Lean-checked exclusion.

The project's own literature sweep had found the White and Claude report (`papers/REPORT-lit-1.md`), but the long draft in `papers/draft/` still called m(38..40) new. The Robinfxa release was not known to the project. A note at the top of the draft records both points. We have found no earlier source for h(n) = 6 on 42 ≤ n ≤ 67 or for the bounds on t_6. The body of George, Khodkar and Wallis (2016), Chapter 4.5, was not available to us.

### What is formal and what is computational

- **Checked by the Lean kernel:** every upper bound (the witnesses and the family), using only the axioms `propext`, `Classical.choice` and `Quot.sound`. Also the arithmetic and Hall inequalities that the GPU prune relies on (`lean-pruning/`). Those lemmas are conditional on the shape census being complete.
- **Exhaustive computation, not formalized:** every non-existence result. That includes h(n) ≥ 6 for n ≥ 41 and every level ruled out for t_6. The claim for each level comes with the checks described in `papers/REPORT-k6-gpu-pairwise-68-70.md` and `papers/REPORT-review-pairwise.md`.

### Quick independent check

`python3 paper/check_witnesses.py` uses only the standard library and none of the search code. It recomputes the cycle lengths of the family for every 41 ≤ n ≤ 67 and of the other witnesses from the cycle space, and it finishes in under a second.

## How the agents did it

From 14 to 20 September 2026, LLM agents in a [ToolsEnabled](https://toolsenabled.ai) agent tree did the research. A manager agent assigned work to worker agents and merged their results. The workers:

- surveyed the literature (`papers/REPORT-lit-*.md`, `REPORT-novelty-check.md`);
- built the shape reduction (`search/shapecsp/`, `papers/REPORT-shape-csp.md`) and the CUDA kernels (`search/shapecsp/pairwise/`, with the design in `SPEC.md`);
- wrote the Lean certificates (`Erdos1016/`);
- ran the searches on two consumer GPUs, an RTX 5060 Ti desktop and an RTX 4070 laptop.

Other agents reviewed the work adversarially:

- a referee-style report (`papers/REFEREE-report.md`);
- independent reviews and re-implementations (`papers/REVIEW-*.md`);
- forged-tier attacks on the claim tool (`papers/REPORT-review-pairwise.md`).

`papers/CHANGES.md` and the commit history record the sequence. Commits by "ToolsEnabled research session" are the agents' own commits.

Joshua Pinckard posed the problem, set its direction and compute limits, selected and evaluated the outputs, and is responsible for the claims.

## Layout

| Path | Contents |
|---|---|
| `paper/` | One-page paper and an independent witness checker |
| `Erdos1016/`, `Erdos1016.lean`, `lakefile.toml` | Lean 4 + Mathlib certificates for every upper bound |
| `lean-pruning/` | Lean proofs of the pruning arithmetic and Hall inequalities, with comparison checks |
| `search/` | Chord searches, GPU enumerations, witness files (`search/verify.py` is the original verifier) |
| `search/shapecsp/` | Shape/CSP reduction, the CPU descent and the GPU pairwise pipeline (`pairwise/`) |
| `papers/verification/` | Claim files: one per exhausted tier, with hashes, unit counts and composition counts |
| `papers/` | The agents' reports, reviews, the long draft (`papers/draft/`) and the change log |
| `deploy/laptop/` | The service and chain scripts that ran the laptop searches |
| `erdos617/` | A small side experiment on Erdős #617, not part of the paper |

The full texts of third-party papers that the agents collected are not included, for copyright reasons. Some reports still refer to them by their arXiv numbers.

## Building the Lean proofs

Install `elan`, then from the repository root run:

```text
lake exe cache get
lake build
lake env lean Axioms.lean
```

The toolchain is pinned to Lean v4.33.1 with Mathlib v4.33.1. The per-level certificates for large n use `decide` with `maxHeartbeats 0`, so a full build takes about 50 minutes on 4 cores. `Axioms.lean` prints the axioms of every theorem.

The core definitions are:

```lean
def IsPancyclic {n : ℕ} (G : SimpleGraph (Fin n)) : Prop :=
  ∀ ℓ, 3 ≤ ℓ → ℓ ≤ n → ∃ (v : Fin n) (w : G.Walk v v), w.IsCycle ∧ w.length = ℓ

def PancyclicWithChords (n k : ℕ) : Prop :=
  ∃ cs : Finset (Sym2 (Fin n)), cs.card = k ∧ (∀ e ∈ cs, e ∉ (baseCycle n).edgeSet) ∧
    IsPancyclic (baseCycle n ⊔ SimpleGraph.fromEdgeSet (↑cs : Set (Sym2 (Fin n))))
```

## License and citation

MIT (see `LICENSE` and `NOTICE`). Citation metadata is in `CITATION.cff`. Contact: josh@toolsenabled.ai.
