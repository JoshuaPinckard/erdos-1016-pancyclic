# Level 88, CPU descent receipt

These files record the CPU refutation of level 88 for k = 6 chords. They were
written on the laptop that ran the descent and were not in the project's
repository until publication.

- `hunt-k6-n88-range.done`: one line per eligible shape, 330 of 330 UNSAT,
  with the solver hash `e2fde07b...7f562c` (the same `bb` build as levels 89..111).
- `descend.log`, `descend-k6-n88.log`, `descend-k6.csv`: the descent over
  levels 93..88. Level 88 ended `all 330 decided, gaveup=0 errors=0` on
  2026-09-20.
- `cpu-n88-ledger-reconciled.json`: a later check that the 330 decided shapes
  are exactly the eligible set, with matching caps, branch counts and hashes.

With levels 89..111 (`REPORT-k6-level89-91-verify.md` and the level 92 and 93
reports at the repository root), this makes the CPU-refuted block 88..111.
`REPORT-k6-level89-91-verify.md` was written while level 88 was still running
and says it was then incomplete. The GPU pipeline also exhausted level 88
(`n88-b10/b11/b12-combined.json`), but it uses the same shape census, so the
two checks are not independent of the census.
