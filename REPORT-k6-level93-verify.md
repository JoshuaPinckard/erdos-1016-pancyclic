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

## Independent re-verification

Worker 19 (verifier), 2026-09-17 08:20-08:25 PDT. Every number below was read
from the raw files on the laptop over ssh (`josh:~/erdos-shapecsp`) or derived
by re-running the enumeration; nothing was taken from the section above or from
Manager's message. No solver process was launched.

**Result: the level-93 receipt holds. Enumeration diff = 0 differences.**

| check | method | value |
|---|---|---|
| `.done` rows (non-`#` lines) | `grep -v '^#' hunt-k6-n93-range.done \| wc -l` | 114 |
| distinct indices | `awk '{print $1}' \| sort -n \| uniq \| wc -l`; `uniq -d` | 114 distinct, 0 duplicates, range 0..113 |
| verdict column | `awk '{print $2}' \| sort \| uniq -c` | `114 UNSAT`; no other verdict token |
| `gaveup` / `error` / `timeout` in `.done` | `grep -i` | 0 lines |
| `GAVEUP b=` / `ERROR` / `*** SAT` in `descend-k6-n93.log` | `grep -c` | 0; final line `RESULT no eligible shape reaches n >= 93; all 114 decided, gaveup=0 errors=0; 29809.5s` |
| eligible count in `descend-k6-n93.log` | header line | `shapes=21878 eligible=114 caps 101..93` |
| `descend.log` | `cat` | `LEVEL n=93 eligible=114 29814.3s exit=0 :: RESULT no eligible shape reaches n >= 93; all 114 decided, gaveup=0 errors=0` |
| `descend-k6.csv` | `cat` | `93,114,29814.3,UNSAT` |
| `sha256sum bb` on laptop | | `e2fde07b69d7a0d84b67d7954304da50feebd84a3cbd0e192faf706a8a7f562c` = `.done` header `solver sha256=` = `descend-k6-n93.log` `solver bb sha256=` |
| `sha256sum hunt.py` on laptop | | `4aa2d636...582c50` = `driver hunt.py sha256=` in `descend-k6-n93.log`; byte-identical to `search/shapecsp/hunt.py` in this repo |
| `shapes.py`, `bound.py` laptop vs this repo | `sha256sum` both sides | identical (`38215a0d...`, `66323898...`) |
| `forms-k6.pkl` laptop vs this repo | `sha256sum` both sides | identical (`781957f2...`) |
| max `nodes=` over the 101 rows that carry it | `grep -o 'nodes=[0-9]*' \| sort -n \| tail -1` | 820,091,669 (index 21), i.e. 10% of `nodecap=8000000000`; no row near the budget |
| systemd unit at time of check | `systemctl status erdos-descent` | active (running) since 2026-09-16 13:21:33 PDT, `ExecStart descend.py 6 93 88 4 8000000000`, child `hunt.py 6 92 4 8000000000 0` |

### Eligible-shape enumeration re-derived

Neither `hunt.py` nor `level.py` has a dry-run/list mode, so the eligibility
filter and ordering were copied verbatim into `search/shapecsp/enum_eligible.py`
(added in this diff): `d[0] >= cutoff and sum(d[4]) <= cutoff and B.hall_ok(d[5], cutoff)`,
then `sort(key=lambda d: -d[0])`, printing `<idx> cap=<cap> b=<b> nforms=<n>` and never
invoking `bb`. It was run two independent ways:

1. **On the laptop, from the same `forms-k6.pkl` the run used** (`nice -n 19
   taskset -c 0`, `.venv` python): `source=cache shapes=21878 eligible=114 caps 101..93`.
2. **On the desktop, from scratch with `--nocache`** (regenerating every shape
   through `shapes.shapes(6)` / `cycle_forms` / `bound.intervals`, no pickle read;
   77 s): `source=regenerated shapes=21878 eligible=114 caps 101..93`.

Diffs:

| comparison | result |
|---|---|
| index set, enumeration (1) vs `.done` first column | **0 differences** (`diff <(sorted enum idx) <(sorted .done idx)`) |
| `cap=` and `b=` fields, enumeration (1) vs the 101 `.done` rows that carry them | **0 mismatches** (python dict compare) |
| full 114-row listing, enumeration (1) laptop-cache vs enumeration (2) desktop-regenerated | **0 differences** (after stripping CRLF) |

So the 114 indices in the ledger are exactly the 114 shapes that the shipped
`shapes.py`/`bound.py` declare eligible at cutoff 93, the cache the run read is
not stale relative to that code, and every row that records its cap/b agrees
with the shape at that index.

### Observations that do not change the verdict

- **13 rows carry no cost fields** (indices `0 1 2 3 4 5 6 7 9 11 13 14 19`,
  all cap 99..101, b=12): they read `<idx> UNSAT` only, and the `.done` header
  has no `driver=` field although the current `hunt.py` writes one. Those rows
  were written by an earlier revision of `hunt.py` during one of the first three
  `descend.log` launches (`jobs=5`, `jobs=11`, `jobs=12`); the fourth launch
  resumed with `resume: 14 shape(s) already decided ... same solver build`
  (13 bare rows + index 24). The resume check keys on the **solver** sha, which
  is identical across all launches, so every UNSAT row is attributable to
  `bb e2fde07b...`; only the per-shape timing/node counts are missing for those
  13. This is not a mixed-build ledger.
- `descend-k6-n93.log` prints progress only for `n <= 50` and `n % 50 == 0`
  (`hunt.py`), so the jump from `# 50/114` to `# 100/114` in the log is
  expected, not a gap.

### Poll baseline (08:22 PDT 2026-09-17), for the 30-minute watch that follows

| item | value |
|---|---|
| level 92 `hunt-k6-n92-range.done` | 92 rows, 92 distinct idx, 92 UNSAT, 0 SAT, 0 dup; eligible=152; header solver sha `e2fde07b...` driver `4aa2d636...`; `descend-k6-n92.log` gaveup/ERROR/SAT lines = 0 |
| `erdos-descent.service` | active |
| laptop n70 b10 `~/erdos-n70/n70-state-b10.json` | complete=2390, hits=0, `erdos-laptop-chain.service` active |
| desktop n68 b10 `search/shapecsp/gpu-state-n68-b10.json` | complete=1834 of 2302, hits=0 |
