# Frozen production snapshot of search/shapecsp/pairwise at commit f63f9f3 (2026-09-19).
The live chains run the runner from here so that in-place edits under ../pairwise cannot
reach a tier that starts hours later. Tables, partitions and state files stay under ../pairwise.
Do not edit; re-freeze from a commit with freeze_prod.py.

Hotfix 2026-09-19 22:05 on top of f63f9f3, in gpu_state_runner_pairwise.py only: the GPU
engine is constructed with max_n = max(70, n) instead of the default 70. max_n is a
bookkeeping bound (it never reaches the CUDA source; MAX_B, MAX_V, MAX_F are unchanged),
so the compiled kernel is identical; without it every level-71+ tier aborted with
"tables exceed engine capacity". Every other file here is still byte-exact to f63f9f3.
