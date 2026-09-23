# ToolsEnabled agent research on Erdős Problem #1016

AI agents in a [ToolsEnabled](https://toolsenabled.ai) agent tree worked on [Erdős Problem #1016](https://www.erdosproblems.com/1016), the fewest edges of a pancyclic graph, and determined it exactly on a new range. This repository holds their proofs, search code, claim files and reports, and a one-page paper.

**Paper:** [`paper/main.pdf`](paper/main.pdf) (source [`paper/main.tex`](paper/main.tex)), a working draft.

## Results

A graph on n vertices is *pancyclic* if it has a cycle of every length 3, ..., n. Let m(n) = n + h(n) be the fewest edges of a pancyclic graph on n vertices, so h(n) is the fewest chords that make the cycle C_n pancyclic. Let t_k be the largest n with h(n) ≤ k.

1. **h(n) = 6 for every 41 ≤ n ≤ 67**, so m(n) = n + 6 there, and t_5 = 40.
   - *Upper bound, checked in Lean 4:* for 41 ≤ n ≤ 67, C_n with the chords {0,2}, {0,n−7}, {1,13}, {3,n−6}, {4,31}, {n−8,n−5} is pancyclic (`Erdos1016.family_pancyclic_41_67`). Its cycle lengths are exactly [3,32] ∪ [n−34,n], so it fails at n = 68, where only length 33 is missing.
   - *Lower bound, exhaustive computation:* no C_n with 5 chords is pancyclic for any n ≥ 41.
2. **t_6 = 67 or t_6 ∈ {72, ..., 79, 81, 83, 84, 85}.** Exhaustive computation shows no 6-chord pancyclic graph on n ∈ {68, 69, 70, 71, 80, 82} or on any n ≥ 86.
   - The CPU descent rules out 88 to 111. Its level-88 receipt is in `papers/verification/cpu-level88/`.
   - The GPU runs rule out 68 to 71, 80, 82 and 86 to 89.
   - The runs stopped on 20 September. Levels 72–79, 81 and 83 were not finished; level 78 was partly run, with no hits. Level 84 lacks its b = 11 tier and level 85 its b = 10 tier.
3. **A second 6-chord pancyclic graph on 67 vertices**, not isomorphic to the family member: {0,27}, {18,30}, {28,37}, {29,37}, {31,38}, {32,39}. A blind control run of the GPU pipeline found it.

### Earlier and parallel work

- Griffin (arXiv:1312.0274, 2013) determined m(n) for n ≤ 37.
- m(38) = 43, m(39) = 44 and m(40) = 45 were first published by P. White and Claude, [Erdős #1016 working report](https://www.erdosproblemaday.com/report/1016), 2026-07-29.
- m(41) = 47 was first published in [Robinfxa/JSP-000846](https://github.com/Robinfxa/JSP-000846): a computer-assisted proof on 2026-09-17, and a Lean proof of the exclusion on 2026-09-22.

The project's literature sweep had found the White and Claude report (`papers/REPORT-lit-1.md`), but the long draft in `papers/draft/` still called m(38..40) new. The project was not aware of the Robinfxa release. Its own n = 41 result, a complete GPU enumeration finished on 2026-09-14, stayed unpublished until 2026-09-23. A note at the top of the draft records these points.

We have found no earlier source for h(n) = 6 on 42 ≤ n ≤ 67 or for the bounds on t_6. The body of the chapter on minimal pancyclicity in George, Khodkar and Wallis (2016) was not obtained.

### What is formal and what is computational

- **Checked by the Lean kernel:** every upper bound (the witnesses and the family), using only the axioms `propext`, `Classical.choice` and `Quot.sound`. Also checked: the arithmetic and Hall inequalities that the GPU prune relies on (`lean-pruning/`), on the condition that the shape census is complete.
- **Exhaustive computation, not formalized:** every non-existence result, including h(n) ≥ 6 for n ≥ 41 and every level ruled out for t_6.
- **The shape census is not checked in Lean.** It reduces a cycle with k chords to a finite list of shapes, and the CPU and GPU searches both rely on it. So the two runs that agree on levels 88 and 89 are not independent of the census.
- **How GPU tiers were claimed:**
  - The pruned tiers were claimed with `search/shapecsp/pairwise/verify_tier_combined.py`, run from the frozen copy in `pairwise-prod/`. It rebuilds every pruning table and matches the composition counts shape by shape.
  - The 15 unpruned tiers (n = 68–70, b = 6–10) were claimed with `search/shapecsp/verify_tier_exhaustion.py`. It re-derives the unit set from the hashed manifest and compares tier-wide totals.

### Quick independent check

`python3 paper/check_witnesses.py` uses only the standard library and none of the search code. It recomputes the cycle lengths of the family for every 41 ≤ n ≤ 67, and of the other witnesses, from the cycle space in under a second.

## How the agents did it

From 13 to 20 September 2026, one ToolsEnabled agent tree did the research. A manager agent split the problem into lanes and merged the results. The worker agents:

- searched the literature (`papers/REPORT-lit-*.md`, `REPORT-novelty-check.md`);
- built the shape reduction (`search/shapecsp/`, `papers/REPORT-shape-csp.md`) and the CUDA kernels (`search/shapecsp/pairwise/`, with the design in `SPEC.md`);
- wrote the Lean certificates (`Erdos1016/`);
- ran the searches on an RTX 5060 Ti desktop and an RTX 4070 laptop.

Other agents reviewed the work:

- a referee-style report (`papers/REFEREE-report.md`);
- independent reviews and re-implementations (`papers/REVIEW-*.md`);
- forged-tier attacks on the claim tool (`papers/REPORT-review-pairwise.md`). Two forgeries passed until the tool was fixed, and a third is caught only with a full table rebuild (`--rebuild -1`).

`papers/CHANGES.md` and the commit history record the sequence. All commits were made by agents. That includes the three on 16 September that carry the author's name.

Joshua Pinckard set the problem, the direction and the compute limits, checked the outputs, and is responsible for the claims. As the founder of ToolsEnabled, Inc., the author has a conflict of interest.

## Layout

| Path | Contents |
|---|---|
| `paper/` | One-page paper and an independent witness checker |
| `Erdos1016/`, `Erdos1016.lean`, `lakefile.toml` | Lean 4 + Mathlib certificates for every upper bound |
| `lean-pruning/` | Lean proofs of the pruning arithmetic and Hall inequalities, with comparison checks |
| `search/` | Chord searches, GPU enumerations and witness files (`search/verify.py` is the original verifier) |
| `search/shapecsp/` | Shape reduction, the CPU descent and the GPU pairwise pipeline (`pairwise/`, frozen copy in `pairwise-prod/`) |
| `papers/verification/` | Claim files: one per exhausted GPU tier, plus the level-88 CPU receipt |
| `papers/` | The agents' reports, reviews, the long draft (`papers/draft/`) and the change log |
| `deploy/laptop/` | The service and chain scripts that ran the laptop searches |
| `erdos617/` | A small side experiment on Erdős #617, not part of the paper |

## Known gaps and errata

- **Paper texts removed.** This is the project's commit history with the full texts of third-party papers removed, for copyright reasons. As a result, the commit hashes cited inside the reports do not resolve here.
- **Some GPU claims can't be re-checked from this repository alone.** The census files for n = 73–89, the pruning tables and the runner state files are not included because of their size; only the table manifests are. `search/shapecsp/pairwise/census_level.py` regenerates the census files.
- **`search/hn.csv`, row 37.** This file is the output of a time-limited heuristic search. Its row n = 37 records 6 because the 5-chord search timed out; the exact value is 5 (Griffin, 2013).
- **`papers/construction/construction.py`, mislabelled chords.** Its chords for 24 ≤ n ≤ 40 are labelled "Griffin, Fig. 1", but they are the construction given by White and Claude (2026).
- **`papers/REPORT-k6-level89-91-verify.md` is out of date on level 88.** It was written while level 88 was still running and calls it incomplete. The finished run is in `papers/verification/cpu-level88/`.

## Building the Lean proofs

Install `elan`, then from the repository root run:

```text
lake exe cache get
lake build
lake env lean Axioms.lean
```

The toolchain is pinned to Lean v4.33.1 with Mathlib v4.33.1. The full build took about 12 minutes on GitHub's CI. `Axioms.lean` prints the axioms of every theorem.

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
