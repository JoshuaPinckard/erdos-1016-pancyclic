# k=6 level n=93 descent: verification receipt

Read directly over ssh from the laptop (`~/erdos-shapecsp`, host `josh`) on
2026-09-17 08:16 PDT by Manager, before any other agent touched the result.

## Run record

```
descend.log:  LEVEL n=93 eligible=114 29814.3s exit=0 :: RESULT no eligible shape
              reaches n >= 93; all 114 decided, gaveup=0 errors=0; 29809.5s
service:      erdos-descent  ExecStart descend.py 6 93 88 4 8000000000  (active)
descend-k6-n93.log:  shapes=21878 eligible=114 caps 101..93
```

## `hunt-k6-n93-range.done`

| check | value |
|---|---|
| header | `solver sha256=e2fde07b...7f562c binary=bb k=6 cutoff=93 mode=range nodecap=8000000000` |
| entries (non-header lines) | 114 |
| distinct shape indices | 114 (no duplicates, none missing against eligible=114) |
| verdicts | 114 UNSAT, 0 SAT |
| gaveup / error / timeout lines | 0 |
| `sha256sum bb` on the laptop | `e2fde07b69d7a0d84b67d7954304da50feebd84a3cbd0e192faf706a8a7f562c` (matches header) |
| nodecap / mode vs service unit | 8000000000 / range, match |

## Consequence

Level 93 is UNSAT on every eligible shape and joins the contiguous refuted block
94..111 recorded in `papers/REPORT-k6-descent.md`. The block is now 93..111, so
the upper bound moves from `t_6 <= 93` to **`t_6 <= 92`**.

Level 92 is running (`hunt.py 6 92 4 8000000000 0`): 91 of 152 eligible shapes
decided at the time of this receipt, all UNSAT, gaveup=0 errors=0.
