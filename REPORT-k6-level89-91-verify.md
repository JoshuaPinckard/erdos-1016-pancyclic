# k=6 levels n=91, n=90, n=89 descent: verification receipt

Read directly over ssh from the laptop (`~/erdos-shapecsp`, host `josh`) on
2026-09-19 by Worker 22 (verifier). Every value below is from the raw files
or from `search/shapecsp/enum_eligible.py` (unmodified, sha256
`cf1bb536eb19579fc49ea8a75cb99cebef86160bfa1f7db050b5478083bf7bfa` on both
machines, verified by `sha256sum` after `scp`); no solver process was
launched and the live `erdos-descent` service was not touched.

**Result: all three levels (91, 90, 89) are UNSAT on every eligible shape,
contiguous with the previously verified 92..111 block. The refuted block is
now 89..111 and the upper bound moves from `t_6 <= 91` to `t_6 <= 88`.**

Level 88 is running but **not complete** at time of check (`grep -v '^#'
hunt-k6-n88-range.done | wc -l` = 51 of `eligible=330`, `systemctl show
erdos-descent -p ActiveEnterTimestamp` = since 2026-09-18 22:27:33 PDT,
projected_total=19.6h from `descend-k6-n88.log`), so it is out of scope for
this receipt per the task's own condition ("if its .done file is complete by
the time you get there"). No claim is made about level 88.

## Run record

```
descend.log:  LEVEL n=91 eligible=181 1213.9s exit=0 :: RESULT no eligible shape
              reaches n >= 91; all 181 decided, gaveup=0 errors=0; 1213.4s
              LEVEL n=90 eligible=214 20952.0s exit=0 :: RESULT no eligible shape
              reaches n >= 90; all 214 decided, gaveup=0 errors=0; 20951.5s
              LEVEL n=89 eligible=279 38354.7s exit=0 :: RESULT no eligible shape
              reaches n >= 89; all 279 decided, gaveup=0 errors=0; 38354.2s
descend-k6.csv (grep -E '^(91|90|89),' descend-k6.csv):
              91,181,1213.9,UNSAT   (first real run; 5 later 0.5s lines are
                                     resumed re-verifications after service
                                     restarts, all UNSAT, same solver build)
              90,214,20952.0,UNSAT
              89,279,38354.7,UNSAT
descend-k6-n91.log:  shapes=21878 eligible=181 caps 101..91
descend-k6-n90.log:  shapes=21878 eligible=214 caps 101..90
descend-k6-n89.log:  shapes=21878 eligible=279 caps 101..89
service:      erdos-descent  ExecStart descend.py 6 93 88 4 8000000000
              (active; child now hunt.py 6 88 4 8000000000 0, 51/330 decided)
```

`grep -v UNSAT descend-k6.csv` returns exactly one line, the header
(`n,eligible,seconds,verdict`) -- every data row in the whole file is UNSAT;
`grep -c SAT descend-k6.csv` = 24 is entirely substring matches inside the
token "UNSAT", not a SAT verdict.

## `hunt-k6-n{91,90,89}-range.done`

| check | n=91 | n=90 | n=89 |
|---|---|---|---|
| header | `solver sha256=e2fde07b...7f562c driver=4aa2d636c39ffa5e binary=bb k=6 cutoff=91 mode=range nodecap=8000000000` | same, `cutoff=90` | same, `cutoff=89` |
| entries (non-header lines), `grep -vc '^#'` | 181 | 214 | 279 |
| distinct shape indices, `grep -v '^#' \| awk '{print $1}' \| sort -n \| uniq \| wc -l` | 181 (range 0..180) | 214 (range 0..213) | 279 (range 0..278) |
| duplicates, `sort -n \| uniq -d \| wc -l` | 0 | 0 | 0 |
| indices missing vs eligible count | 0 | 0 | 0 |
| verdicts, `grep -v '^#' \| awk '{print $2}' \| sort \| uniq -c` | `181 UNSAT` | `214 UNSAT` | `279 UNSAT` |
| SAT rows | 0 | 0 | 0 |
| gaveup / error / timeout lines in `.done`, `grep -ic` | 0 | 0 | 0 |
| `GAVEUP b=` / `ERROR` / `*** SAT` / `Traceback` in `descend-k6-n{n}.log`, `grep -c` | 0 | 0 | 0 |
| rows without cost fields (`grep -v '^#' \| grep -vc 'nodes='`) | 0 | 0 | 0 |
| max `nodes=`, `grep -o 'nodes=[0-9]*' \| cut -d= -f2 \| sort -n \| tail -1` | 1,328,032,497 (16.6% of `nodecap=8000000000`) | 2,546,391,849 (31.8%) | 3,964,575,865 (49.6%) |
| `sha256sum bb` on laptop | `e2fde07b69d7a0d84b67d7954304da50feebd84a3cbd0e192faf706a8a7f562c` (matches header, all three levels, same build as 92..111) |
| `sha256sum hunt.py` on laptop | `4aa2d636c39ffa5ef04b4fae7ac59443a7ca2a133f886a240b8973f414582c50` (matches `driver=` prefix; byte-identical to `search/shapecsp/hunt.py` here) |
| `sha256sum shapes.py` / `bound.py` / `forms-k6.pkl`, laptop vs this repo | identical: `38215a0d9acfb...`, `66323898e94d4...`, `781957f2fe5e6...` |
| nodecap / mode vs service unit | 8000000000 / range, match, all three |
| resumed rows | n=91: `resume: 181 shape(s) already decided ... same solver build`; n=90: `resume: 46 shape(s) already decided ... same solver build`; n=89: no resume line (single unbroken run) -- all resumed rows still carry full cost fields (unlike level 93's 13 bare legacy rows), so there is no mixed-build or bare-row concern at any of these three levels |

## Eligible-shape enumeration re-derived

`search/shapecsp/enum_eligible.py` (unmodified from the level-92/93 diff) was
copied to `/tmp/enum_eligible.py` on the laptop (not into `~/erdos-shapecsp`,
so the live run directory was never written to) and verified byte-identical
by `sha256sum` (`cf1bb536...` both sides) before running. Run two independent
ways per level, as for levels 92 and 93:

1. **laptop, from the run's own `forms-k6.pkl`** (`nice -n 19 taskset -c 0`,
   the run's own `.venv` python):
   - n=91: `source=cache shapes=21878 eligible=181 caps 101..91`
   - n=90: `source=cache shapes=21878 eligible=214 caps 101..90`
   - n=89: `source=cache shapes=21878 eligible=279 caps 101..89`
2. **desktop, `--nocache` regeneration** through `shapes.shapes(6)` /
   `cycle_forms` / `bound.intervals` (no pickle read), pinned to cores 4,5
   (`ProcessorAffinity=0x30`) at `BelowNormal` priority:
   - n=91: `source=regenerated shapes=21878 eligible=181 caps 101..91` (107s)
   - n=90: `source=regenerated shapes=21878 eligible=214 caps 101..90`
   - n=89: `source=regenerated shapes=21878 eligible=279 caps 101..89`

| comparison | n=91 | n=90 | n=89 |
|---|---|---|---|
| index set, enumeration (1) vs `.done` first column (`Compare-Object`, sorted unique) | **0 differences** | **0 differences** | **0 differences** |
| `cap=` / `b=` fields, enumeration (1) vs every `.done` row that carries them | **0 mismatches** (181/181 checked) | **0 mismatches** (214/214 checked) | **0 mismatches** (279/279 checked) |
| full listing, (1) laptop-cache vs (2) desktop-regenerated (`Compare-Object`, CRLF-normalized) | **0 differences** | **0 differences** | **0 differences** |

So for all three levels the indices in the ledger are exactly the shapes
that the shipped `shapes.py`/`bound.py` declare eligible at that cutoff, the
cache the run read is not stale relative to that code, and every row's
recorded cap/b agrees with the shape at that index.

## Consequence

Levels 91, 90 and 89 are each UNSAT on every eligible shape with gaveup=0
errors=0, decided by the same `bb` build (`e2fde07b...7f562c`) as levels
93..111 and 92. They are contiguous with the previously verified 92..111
block (`REPORT-k6-level92-verify.md`), so the refuted block extends to
**89..111** and the upper bound moves from `t_6 <= 91` to **`t_6 <= 88`**.

Level 88 (`hunt.py 6 88 4 8000000000 0`, eligible=330) is in progress: 51 of
330 decided at time of check, all UNSAT so far, gaveup=0 errors=0,
projected_total=19.6h from the last log checkpoint -- not complete, not
verified, not part of this bound.
