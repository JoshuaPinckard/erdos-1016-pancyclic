# Explicit chord construction and verification

## Status / leading finding

The executable source recipe is only partially recoverable from the open material. Alon–Krivelevich, arXiv:2308.01564, §3, says the deterministic construction in George–Khodkar–Wallis (2016), Chapter 4.5 uses consecutive binary shortcuts (e_i) with interval sizes (2^i), satisfying (\frac12n\le 2^{K+1}+K-1\le n), then one extra joining edge, and finally (O(\log^*n)) further edges for the short lengths. The chapter itself was not available as an open PDF in this task, so the final completion rules cannot be cited or implemented literally.

`construction.py` therefore exposes the recoverable binary-shortcut skeleton and labels the omitted completion as omitted. For (24\le n\le40), it also exposes the five-chord coordinates transcribed in the local Erdős #1016 report. `check.py` implements the requested cycle-space enumeration: basis = Hamilton cycle plus each chord with its forward Hamilton path, XOR all nonzero subsets, retain connected 2-regular edge sets, and collect lengths.

## Reproduction

From this directory:

```text
python check.py 3 2000 construction_u.csv
```

The CSV columns are exactly `n,k_construction,verified`. The run is intentionally not a proof shortcut: `verified=yes` means the enumerated cycle spectrum contains every length 3 through n. Published patterns are not repaired silently.

## Verification finding

The transcribed five-chord pattern fails the requested checker for every tested value (n=23,24,\ldots,40) in the current run. This is a source-transcription discrepancy, not evidence that Griffin’s Figure 1 fails: the figure’s actual geometry is an image and its chord endpoints were not present in the extracted text. The report must therefore retain the result as “could not verify the figure coordinates,” not claim a failed published construction. The general binary skeleton likewise is not claimed pancyclic without the omitted (O(\log^* n)) completion.

## Exact edge counts / comparison

The source claim is (k(n)=\log_2n+\log^*n+O(1)) chords (Bondy’s asymptotic statement), not an exact integer function. Consequently, exact first-(n) thresholds for (k=5,6,7,8) cannot be derived from that asymptotic claim alone. For the checked implementation, thresholds are to be read mechanically from `construction_u.csv`; failed rows are not counted as pancyclic thresholds.

For comparison, the supplied exact values are (h=0,1,1,2,2,2,3) for (n=3\ldots9), (h=3) for (n=10\ldots14), (h=4) for (n=15\ldots24), and (h=5) for (n=25\ldots40). Griffin (arXiv:1312.0274, Figure 1 and Table 1) states a five-chord construction for 23–37 vertices, but the extracted text does not include the figure’s five endpoint pairs. The local report’s endpoint transcription is therefore marked unverified above.

## Sources and evidence

- Bondy, “Pancyclic graphs I,” JCTB 11 (1971), pp. 80–84: asymptotic bounds are quoted by Alon–Krivelevich as `log2(n−1)−1 ≤ Pex(Kn) ≤ log2 n + log* n + O(1)`; no construction recipe is printed in the open abstract/source inspected.
- George–Khodkar–Wallis, *Pancyclic and Bipancyclic Graphs* (2016), Chapter 4.5: cited by Alon–Krivelevich as the source of the deterministic shortcut construction; full chapter was not obtained, so exact page-level rules remain unknown.
- Griffin, “Minimal Pancyclicity,” arXiv:1312.0274, Figure 1 and Table 1: local evidence [1312.0274.txt](../1312.0274.txt), quoted string “Construction with 23 to 37 vertices” and “A new construction with 5 chords (Figure 1)”.
- Alon–Krivelevich, arXiv:2308.01564, §3: local evidence [2308.01564.txt](../2308.01564.txt), quoted string “one creates a sparse pancyclic graph by taking an n-cycle H and K shortcuts” and “ei is a 2^i-shortcut”.
- Sridharan (1978): not obtained in the accessible search and is not used as authority; this is recorded as “could not look,” not “not there.”

Addendum: the executable output has first chord-count occurrences k=5 at n=18, k=6 at n=41, k=7 at n=66, and k=8 at n=130. These are not verified pancyclic thresholds. The requested 3–2000 run was started and measured through n=801; it was stopped at the next chord-count regime because enumeration became too slow. Thus n=802–2000 are unknown in the current CSV, not silently treated as failures or successes.

Resource-capped rerun: after stopping duplicate Python workers, `check.py` was run once at BelowNormal priority in `sampled` mode. This verifies every n=3..300, then n=350,400,...,2000, and includes every first chord-count increase. The completed CSV is [construction_u.csv](construction/construction_u.csv); all recorded rows currently have `verified=no`.
