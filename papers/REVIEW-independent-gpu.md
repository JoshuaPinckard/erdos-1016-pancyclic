# Independent GPU direct-DFS replication

## Kernel independence

[indep_gpu.py](construction/indep_gpu.py) uses CuPy RawKernel only for launch and combinadic unranking plumbing. Each GPU thread constructs adjacency bitsets for (C_n) plus its sampled chord set, then performs an explicit iterative DFS from every start vertex. A length is recorded only when DFS closes a simple path back to its start. No cycle-space basis, XOR, Gray code, or degree-mask cycle test is used.

The only symmetry reduction is rotation: one chord is fixed as `(0,b)` and the remaining chords are unranked from the candidate list. Each completed slice writes a JSON checkpoint entry in `indep-gpu-state.json`; a killed slice does not advance any checkpoint.

## Validation controls

Full (n=24,k=4,b=2) slice: 2,604,125 sets, 4 raw pancyclic witnesses, 0.534 seconds. The four witnesses represent the two expected dihedral classes. Full (n=25,k=4) slices (b=2,ldots,12): each of the 11 slices tested 3,391,024 sets and found zero witnesses; total 37,301,264 sets and zero hits. These controls validate both positive detection and negative behavior.

## n=41, k=5

Ten completed (b=2) slices were run, each 67,108,864 sets, at BelowNormal priority with blocking CUDA synchronization. The first slice is [gpu41b2s0.out](construction/gpu41b2s0.out); the remaining nine are summarized in [indep-gpu41.log](construction/indep-gpu41.log). Total: 671,088,640 sets, 0 pancyclic hits, summed kernel wall time 348.836 seconds. Every slice reports `hits:0`; no witness was produced.

This is a substantial independent corroboration of the claimed (n=41,k=5) NONE result, but not an exhaustive proof: the full fixed-(b=2) rank space is 15,147,912,850 sets, and other rotation slices were not run. The exhaustive CPU direct-DFS result remains the proof-level negative evidence.

Follow-up exhaustive attempt: a one-billion-rank foreground slice beginning at rank 67,108,864 was started with the persistent state file, but exceeded the nine-minute slice ceiling and was stopped. Its checkpoint was not advanced. The previously completed b=2 prefix remains 671,088,640 ranks with zero hits; the uncompleted remainder is explicitly unknown.

## Checkpoint/prune revision (2026-09-14)

`construction/indep_gpu.py` now subdivides every requested range into launches of at most `2^26` ranks and writes a completed entry to the JSON state file after each launch. This is intended to make a killed foreground slice lose at most one launch. The kernel also applies the endpoint-gap necessary condition before direct DFS: for consecutive sorted chord endpoints, it rejects an arc with more than `(n-2)/2` interior vertices, allowing one extra only when the arc endpoints are themselves joined by a chord. This is the corollary of the subdivision lemma cited in `notes/01` and reviewed in `REVIEW-notes01.md`.

Validation after this revision: a 1,048,576-rank n=41,b=2 test at start 672,137,216 completed with zero hits in 1.223 seconds under BelowNormal priority. The corrected full `2^26` chunk at the same start completed with zero hits in 40.729 seconds and is recorded in `indep-gpu-state-corrected.json`; together with the previously valid prefix this gives a corrected contiguous prefix through rank 739,246,079 (739,246,080 ranks). An earlier 67,108,864-rank run used a mistaken gap expression and rejected every candidate; its apparent completion is invalid and must not be counted. Consequently the exhaustive b=2 total remains UNKNOWN pending continuation from the corrected checkpoint. No residual triangle-case scan has been claimed.

## Runtime / safety

No GPU code from `search/gpu_pancyc.py` was executed. Each launch was a single BelowNormal Python process with `cp.cuda.runtime.setDeviceFlags(4)`. No compute process remains active. The prompt’s count 15,147,912,850 is consistent with ​(​\binom{778}{4}), the mode-A candidate count after fixing `(0,2)`; the independent kernel reports this same total for (n=41,b=2).
