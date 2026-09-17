# k=6 level n=92 descent: verification receipt

Read directly over ssh from the laptop (`~/erdos-shapecsp`, host `josh`) on
2026-09-17 13:56 PDT by Worker 19 (verifier), one poll after the level closed
(the 13:25 PDT poll saw 151/152; the 13:55 PDT poll saw 152/152). Every value
below is from the raw files; no solver process was launched.

## Run record

```
descend.log:  LEVEL n=92 eligible=152 57151.9s exit=0 :: RESULT no eligible shape
              reaches n >= 92; all 152 decided, gaveup=0 errors=0; 57146.8s
descend-k6.csv:  92,152,57151.9,UNSAT
service:      erdos-descent  ExecStart descend.py 6 93 88 4 8000000000  (active;
              child now hunt.py 6 91 4 8000000000 0, descend-k6-n91.log eligible=181)
descend-k6-n92.log:  shapes=21878 eligible=152 caps 101..92
```

## `hunt-k6-n92-range.done`

| check | value |
|---|---|
| header | `solver sha256=e2fde07b...7f562c driver=4aa2d636c39ffa5e binary=bb k=6 cutoff=92 mode=range nodecap=8000000000` |
| entries (non-header lines) | 152 |
| distinct shape indices | 152, range 0..151, 0 duplicates, none missing against eligible=152 |
| verdicts | 152 UNSAT, 0 SAT |
| gaveup / error / timeout lines in `.done` | 0 |
| `GAVEUP b=` / `ERROR` / `*** SAT` / `Traceback` in `descend-k6-n92.log` | 0 |
| rows without cost fields | 0 (every row carries `s= nodes= cap= b=`; single driver revision throughout) |
| max `nodes=` | 972,647,190 (12% of `nodecap=8000000000`; no shape near the budget) |
| `sha256sum bb` on the laptop | `e2fde07b69d7a0d84b67d7954304da50feebd84a3cbd0e192faf706a8a7f562c` (matches header and log) |
| `sha256sum hunt.py` on the laptop | `4aa2d636c39ffa5ef04b4fae7ac59443a7ca2a133f886a240b8973f414582c50` (matches `driver=` prefix in header and the log line; identical to `search/shapecsp/hunt.py` here) |
| nodecap / mode vs service unit | 8000000000 / range, match |

## Eligible-shape enumeration re-derived

`search/shapecsp/enum_eligible.py` (same filter and order as `hunt.py`, no `bb`)
run two ways, as for level 93:

1. laptop, from the run's own `forms-k6.pkl` (`nice -n 19 taskset -c 0`):
   `source=cache shapes=21878 eligible=152 caps 101..92`
2. desktop, `--nocache` regeneration through `shapes.shapes(6)` / `bound.intervals`:
   `source=regenerated shapes=21878 eligible=152 caps 101..92`

| comparison | result |
|---|---|
| index set, enumeration (1) vs `.done` first column | **0 differences** (set equality, symmetric difference `[]`) |
| `cap=` / `b=` fields, enumeration (1) vs all 152 `.done` rows | **0 mismatches** |
| full listing, (1) laptop-cache vs (2) desktop-regenerated | **0 differences** |

## Consequence

Level 92 is UNSAT on every eligible shape with gaveup=0 errors=0, decided by
the same `bb` build as levels 93..111. The contiguous refuted block is now
**92..111**, so the upper bound moves from `t_6 <= 92` to **`t_6 <= 91`**.

Level 91 started 2026-09-17 13:54 PDT (`hunt.py 6 91 4 8000000000 0`,
eligible=181, caps 101..91).

## GPU tiers observed during the same watch (for the record, not part of the bound)

| tier | state |
|---|---|
| laptop n=70 b=10 (`~/erdos-n70/n70-state-b10.json`) | complete 3040/3040, `chain-laptop.log` `"exhausted": true`, hits=0; chain moved to b=11 at 12:43:52 PDT |
| desktop n=68 b=10 (`search/shapecsp/gpu-state-n68-b10.json`) | complete 2302/2302, hits=0 |
