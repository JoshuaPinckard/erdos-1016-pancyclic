# Erdős #1016 — adjacent-literature sweep (lower-bound / cycle spectrum)

## Costliest finding first

No located paper proves (h(n)\ge \log_2 n+\omega(1)). The closest theorem is already known to the project: if a Hamiltonian (n)-vertex graph has (m=n+p) edges, then its cycle spectrum has more than

\[
\sqrt p-\tfrac12\log p-1
\]

distinct lengths (Milans–Pfender–Rautenbach–Regen–West, 2012). This is a lower bound in the number (p) of chords, but it is far below the (\log_2 n) excess needed for pancyclicity when (p=O(\log n)). The paper explicitly says its extremal construction remains a candidate below (m<n^2/4), except ((n,m)=(14,21)) (local evidence: [Milans-Pfender-Rautenbach-Regen-West-2012.pdf](Milans-Pfender-Rautenbach-Regen-West-2012.pdf), quoted symbols “(s(G)>\sqrt p-\frac12\ln p-1)” and “candidate for a graph having the smallest cycle spectrum”).

The sweep did, however, find a promising arithmetic-combinatorics direction: Bucić–Gishboliner–Sudakov’s proof deliberately combines “condensed” path lengths with “spread-out” path lengths, making all pairwise sums distinct; the authors identify this as an additive-combinatorics/subset-sum paradigm. It applies to minimum degree 3 and gives (n^{1-o(1)}) lengths, but it does not currently translate to a graph with only (k=O(\log n)) chords.

## Results directly about (n)-cycles plus chords

### Milans, Pfender, Rautenbach, Regen, West (JCTB 102 (2012), 869–874)

Citation: K. G. Milans, F. Pfender, D. Rautenbach, F. Regen, D. B. West, “Cycle spectra of Hamiltonian graphs,” *Journal of Combinatorial Theory, Series B* 102 (2012), 869–874, DOI [10.1016/j.jctb.2012.04.002](https://doi.org/10.1016/j.jctb.2012.04.002). Open PDF: [Milans-Pfender-Rautenbach-Regen-West-2012.pdf](Milans-Pfender-Rautenbach-Regen-West-2012.pdf).

Precise result: for a Hamiltonian graph with (n) vertices and (m) edges, putting (p=m-n), the number (s(G)) of distinct cycle lengths satisfies (s(G)>\sqrt p-\frac12\ln p-1). For general (m,n), constructions have at most (2\lceil\sqrt p+1\rceil) lengths. Their lower-bound mechanism is a chord/path overlap lemma: (h) pairwise-overlapping chords of equal length force at least (h-1) path lengths, then a partition/counting argument finds a large overlap family. Evidence: PDF quote “A path with endpoints (x) and (y) is an (x,y)-path”; “two chords … overlap if (a<b<c<d)”; and “(s(G)>\sqrt p-\frac12\ln p-1)”.

Assessment: directly relevant to the (C_n+k)-chord formulation, and a useful local lemma for structured chord patterns. It cannot establish (h(n)\ge\log_2n+\omega(1)): at (p=\Theta(\log n)) it forces only (\Theta(\sqrt{\log n})) lengths, and the proof does not exploit the exact subset-sum structure of all chord combinations.

### Affif Chaouche, Rutherford, Whitty (2012/2014), “Pancyclicity when each cycle must pass exactly (k) Hamilton cycle chords”

Citation: F. Affif Chaouche, C. Rutherford, R. Whitty, “Pancyclicity when each cycle must pass exactly (k) Hamilton cycle chords,” arXiv:1212.3633 [math.CO](https://arxiv.org/abs/1212.3633). Open PDF: [Affif-Chaouche-Rutherford-Whitty-2012.pdf](Affif-Chaouche-Rutherford-Whitty-2012.pdf).

Precise result: define (c(n,k)) as the minimum number of chords added to (C_n) so that cycles of every possible length (subject to the exact-(k)-chord requirement) exist. For fixed (k), they prove (c(n,k)=\Omega(n^{1/k})). The abstract states the ordinary pancyclic chord number is (\Theta(\log n)), while exact-(k)-chord pancyclicity has the fixed-(k) lower bound (\Omega(n^{1/k})). Evidence: PDF [Affif-Chaouche-Rutherford-Whitty-2012.pdf](Affif-Chaouche-Rutherford-Whitty-2012.pdf), quoted string “(c(n,k))” and theorem statement “For fixed (k), we establish a lower bound of (\Omega(n^{1/k}))”.

Assessment: the closest located paper to an explicit arithmetic treatment of chord patterns, because it fixes the number of chords used and analyzes which lengths can be represented. It does not imply a stronger lower bound for unrestricted pancyclicity: a cycle may use any number of the available chords, and the theorem’s fixed-(k) quantifier is a different requirement. Its proof/lemmas may be a useful template for bounding unions of (j)-chord realizable lengths and then summing over (j).

### Bucić, Gishboliner, Sudakov (Forum Math. Sigma 10 (2022), e70)

Citation: M. Bucić, L. Gishboliner, B. Sudakov, “Cycles of many lengths in Hamiltonian graphs,” *Forum of Mathematics, Sigma* 10 (2022), e70, DOI [10.1017/fms.2022.42](https://doi.org/10.1017/fms.2022.42). Open PDF: [Bucic-Gishboliner-Sudakov-2022.pdf](Bucic-Gishboliner-Sudakov-2022.pdf).

Precise result: every (n)-vertex Hamiltonian graph with minimum degree at least 3 has (n^{1-o(1)}) distinct cycle lengths. A quantitative theorem in the paper is (\Omega\bigl(n/2^{6\sqrt{\log n\log\log n}}\bigr)). For bounded-degree regular Hamiltonian graphs, the paper states an improved (n/\mathrm{polylog}(n)) bound; it records the Jacobson–Lehel conjecture (linear many lengths for (k\ge3) regular Hamiltonian graphs) and Verstraëte’s minimum-degree-3 strengthening.

Method: partition the Hamilton cycle into sections, find path lengths at multiple scales, and combine (Q_i) and (R_j) so that all sums (|Q_i|+|R_j|) are distinct. The paper explicitly says the idea is used in additive combinatorics and mentions subset-sum work. Evidence: PDF [Bucic-Gishboliner-Sudakov-2022.pdf](Bucic-Gishboliner-Sudakov-2022.pdf), quoted symbols “(n^{1-o(1)})”, “(Q_i+R_j)”, and “fill in the gaps”.

Assessment: conceptually promising for realisable-length arithmetic, but not presently a lower-bound proof for (h(n)). Minimum degree 3 requires linearly many incident edges/chords, whereas Erdős #1016 asks about only (O(\log n)) chords. The multiscale sumset idea is the best candidate to adapt after a structural lemma for sparse chord sets is found.

### Draganić, Munhá Correia, Sudakov (2023), “Pancyclicity of Hamiltonian graphs”

Citation: N. Draganić, D. Munhá Correia, B. Sudakov, “Pancyclicity of Hamiltonian graphs,” arXiv:2209.03325 [math.CO](https://arxiv.org/abs/2209.03325). Open PDF: [Draganic-Munha-Correia-Sudakov-2023.pdf](Draganic-Munha-Correia-Sudakov-2023.pdf).

Precise result: if an n-vertex Hamiltonian graph has independence number at most k and n is at least (2+o(1))k^2, then it is pancyclic; the asymptotic threshold is best possible. Related connectivity and bipartite-hole degree conditions also imply pancyclicity, with the balanced complete bipartite exception. Evidence: [Draganic-Munha-Correia-Sudakov-2023.pdf](Draganic-Munha-Correia-Sudakov-2023.pdf), quoted string “n=(2+o(1))k^2 vertices, it is already pancyclic”.

Assessment: not a sparse-edge theorem. Its hypotheses force substantial global structure and do not hold for C_n plus O(log n) chords in general. The rerouting/path-length techniques may be useful auxiliary tools, but no direct implication for h(n) at least log2(n)+omega(1) was found.

### Jacobson–Lehel (1999 question) and the regular/Hamiltonian spectrum line

The located survey record states their question: minimize the cycle-spectrum size in a (k)-regular Hamiltonian graph, especially (k=3). Their construction joins copies of (K_{k,k}) cyclically and has spectrum size approximately (\frac n2\frac{k-2}{k}+k); for cubic graphs it has (n/6+3) lengths. Evidence: [Cycle Spectrum of Hamiltonian Graphs](https://dwest.web.illinois.edu/regs/specham.html), quoted string “What is the minimum size of the cycle spectrum in a (k)-regular Hamiltonian graph”.

Assessment: important extremal context, but regularity forces (\Theta(n)) chords and therefore does not constrain the (k=O(\log n)) regime. It supplies sparse-spectrum constructions, not the desired lower bound.

## Arithmetic progressions, sparse graphs, and related cycle-length forcing

### Verstraëte, “Arithmetic Progressions of Cycle Lengths in Graphs” (arXiv:math/0204222; 2002)

Precise result: a bipartite graph of average degree at least (4k) and girth (g) contains cycles of ((g/2-1)k) consecutive even lengths; an average-degree-at-least-(8k) graph with even girth has the same conclusion. Evidence: [Verstraete-2002-Arithmetic-Progressions.pdf](Verstraete-2002-Arithmetic-Progressions.pdf), quoted string “cycles of ((g/2-1)k) consecutive even lengths”.

Assessment: genuinely arithmetic (intervals/progressions), but density-driven. With (m=n+O(\log n)), average degree is (2+o(1)), far below the hypothesis. No direct route to (\log_2n+\omega(1)).

### Alon–Krivelevich, “Sparse pancyclic subgraphs of random graphs” (SIAM J. Discrete Math. 39 (2025), 562–574)

Precise result: for (G\sim G(n,p)), if (p\ge(1+o(1))\ln n/n) (with the paper’s stated (p^*) error), then with high probability (G) contains a pancyclic subgraph with (n+(1+o(1))\log_2n) edges. They define pancyclicity excess (\mathrm{Pex}(G)) as the minimum number of chords in a pancyclic subgraph and prove (\mathrm{Pex}(G)=(1+o(1))\log_2n) w.h.p. Evidence: [Alon-Krivelevich-2024-Sparse-Pancyclic-Random.pdf](Alon-Krivelevich-2024-Sparse-Pancyclic-Random.pdf), quoted strings “​(​\mathrm{Pex}(G)=k)” and “​(​\mathrm{Pex}(G)=(1+o(1))\log_2n)”.

Assessment: highly relevant to the scale and to random chord availability, but it is an upper/existence result in random host graphs, not a universal lower bound. Its construction may expose the arithmetic design needed for a near-optimal chord pattern. It does not prove (\log_2n+\omega(1)); indeed it supports the possibility that the true answer is close to ​(log_2n).

### Bondy, “Pancyclic graphs I” (JCTB 11 (1971), 80–84)

Precise result: an (n)-vertex Hamiltonian graph satisfying Bondy’s degree-sum condition (in particular the Dirac threshold (\delta\ge n/2)) is pancyclic except for (K_{n/2,n/2}). Evidence: [Bondy Pancyclic graphs I](https://www.sciencedirect.com/science/article/pii/0095895671900165), quoted string “either pancyclic or else is the complete bipartite graph”. This is a density/degree theorem, not a minimum-edge theorem.

Assessment: foundational and repeatedly cited by the spectrum papers, but no direct sparse lower bound. The adjacent citations checked through the located Erdős #1016 report include George–Marr–Wallis, *Minimal Pancyclic Graphs* (JCMCC 86 (2013), 125–133), and George–Khodkar–Wallis, *Pancyclic and Bipancyclic Graphs* (2016), Chapter 5 “Minimal Pancyclicity”. Their focus is exact small cases/survey material; no located result extends the needed universal asymptotic lower bound beyond Shi’s cycle-count argument.

## Searches, databases, and bounds

Databases/search surfaces used: arXiv math.CO (title/abstract and PDF retrieval); zbMATH Open (title/author/keyword queries); Semantic Scholar-indexed web results; Google Scholar-indexed web results (site-restricted queries; direct result pages were not consistently exposed by the search interface); publisher pages (ScienceDirect/Cambridge/Wiley) and author repositories. Search strings included: “cycle spectrum Hamiltonian graph chords”; “Milans Pfender Rautenbach Regen West”; “Bucic Gishboliner Sudakov cycles many lengths”; “Draganic Munha Correia Sudakov pancyclicity”; “Verstraete conjecture minimum degree 3 Hamiltonian cycle lengths”; “Jacobson Lehel cycle spectrum”; “subset sums chord patterns cycle lengths”; “graphs with cycles of all lengths few edges”; “minimum size pancyclic”; “cycle lengths cyclomatic number”; “Bondy Pancyclic graphs I citations minimum edges”; and “pancyclicity each cycle exactly k Hamilton cycle chords”.

Download bound: six newly retrieved open PDFs were saved under this folder; existing PDFs were preserved. No claim of exhaustive coverage is made: database interfaces and paywalled records were not treated as inspected full text unless an open copy was downloaded.

## Ranked next techniques

1. **Sparse-chord multiscale sumsets (Bucić–Gishboliner–Sudakov adapted).** First seek a structural lemma for a Hamilton cycle plus (k) chords that yields several separated families of path-length increments; use distinct pairwise sums to beat the raw (2^{k+1}-1) cycle count. This is the only located method explicitly controlling arithmetic collisions.

2. **Exact-(j)-chord decomposition (Affif Chaouche–Rutherford–Whitty).** Bound the number/shape of lengths realised by exactly (j) chords, then union over (j=1,\dots,k). Their (\Omega(n^{1/j})) obstruction for fixed (j) is not yet the unrestricted problem, but the decomposition matches the chord-pattern model exactly.

3. **Overlap/interval forcing (Milans–Pfender–Rautenbach–Regen–West plus Verstraëte).** Refine the pairwise-overlapping-chord lemma to exploit many different chord lengths or additive progressions. Current theorem is only (\sqrt{k}), and Verstraëte’s progression theorem needs high average degree; the payoff would require a new sparse analogue.
