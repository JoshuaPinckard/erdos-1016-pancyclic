# `search/hn_k5.csv` — provenance and quarantined rows

`hn_k5.csv` is written by `search/run_shards.ps1`, which launches
`pancyc3.exe` shards for each `n` at `k=5`, polls their `sh-{n}-*.txt`
outputs for a `WITNESS` line, and appends one row per `n`. When every shard
process exits without a `WITNESS`, the script appends
`"$n,$k,NONE,,<seconds>,<tested>"` where `<tested>` is the sum of the
`tested=` fields found in the shard outputs — **so a shard run whose processes
died without writing anything is recorded as `NONE` with `tested=0`**. The
script also appends a bare `done` line after each invocation.

## What was changed on 2026-09-14 (see `papers/REPORT-record-integrity.md`)

The file as originally recorded was:

```
n,k,result,witness,seconds,tested
39,5,WITNESS,"(0,2) (0,18) (1,12) (3,19) (17,20)",3201,61561098
40,5,WITNESS,"(0,5) (1,5) (2,30) (3,10) (4,11)",7424,132830426
41,5,ABORTED-no-output-processes-died,,8044,0

41,5,NONE,,66,0
done
41,5,NONE,,187,0
done
```

* The two `41,5,NONE,,66,0` and `41,5,NONE,,187,0` rows are **not evidence of
  anything**: `tested=0` means no shard output contained a `tested=` field,
  i.e. the processes exited (after 66 s and 187 s) without testing a single
  candidate. Their `result` field has been re-labelled
  `INVALID-NONE-tested-zero-processes-died` so that nothing filtering on
  `result == NONE` counts them as a completed elimination. The `seconds`
  and `tested` values are kept verbatim.
* The `41,5,ABORTED-no-output-processes-died,,8044,0` row was already
  hand-labelled and is kept as is. Its shard outputs
  `search/sh-41-A0.txt` … `sh-41-A7.txt`, `sh-41-BC.txt` are all zero bytes
  and are now tracked in git so the abort is checkable.
* The blank line and the two `done` lines, which made the file malformed
  CSV, are removed. (`run_shards.ps1` will append a new `done` line if it is
  run again; the line is a run-completion marker, not data.)

## Consequence for the record

`hn_k5.csv` contains **no** CPU-side elimination of `k=5` at `n=41`. The
only complete `n=41, k=5` eliminations in the project are the GPU runs
`search/gpu-41-5.txt` (64-bit kernel) and `search/k6/gpu128-41-5.txt`
(128-bit port of the same kernel); see Section 3.4 of
`papers/draft/pancyclic-exact-values.md` for what that does and does not
establish.
