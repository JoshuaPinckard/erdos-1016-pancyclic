# Frozen production snapshot of search/shapecsp/pairwise at commit f63f9f3 (2026-09-19).
The live chains run the runner from here so that in-place edits under ../pairwise cannot
reach a tier that starts hours later. Tables, partitions and state files stay under ../pairwise.
Do not edit; re-freeze from a commit with _mgr_freeze_prod.py.
