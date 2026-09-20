# GPU pairwise pipeline: levels 72..89 census and tables

Worker 22, 2026-09-19, per SPEC.md (`search/shapecsp/pairwise/SPEC.md`).
Manifests for n=72..89 generated on the desktop, scp'd to the laptop
(`josh:~/erdos-n70/search/shapecsp/pairwise/gpu-blast-ext/`), tables built
there with `pairwise_tables.py build-tier`, `workers=4`, alongside the
unmodified `erdos-descent` bb descent. All 18 levels are now built and
integrity-clean.

## Leading finding: 11 tiers were built with an uncommitted worktree module before the frozen module was restored -- fixed, no data was actually wrong

**Corrected mechanism and exact fault window (per Manager, who made the
restore and recorded these mtimes on the laptop at 18:18:58 PDT -- my
original write-up below had the causal direction backwards):** laptop
`search/shapecsp/pairwise/pairwise_tables.py` had mtime `18:14:31.969` and
md5 `4b765c08` -- the desktop worktree version with the 14-key hashed header
and permuted arc order -- most likely Worker 21 testing its patch; not this
task, and as far as the Manager can tell not Worker 20 either.
`gpu_search_pairwise.py`, `gpu_state_runner_pairwise.py` and
`test_pairwise_tables.py` were untouched, mtime `18:12:43` at their committed
md5s. **The fault window is `18:14:31` to `18:22:48` PDT**: the 11 tiers
below were built inside it, with the 14-key worktree module. The write I
measured at `18:22:48.315` was the Manager restoring the committed module
(`cp` from `pairwise-prod`, md5 `92636a0d`) after finding the worktree
copy -- **`18:22:48` is the end of the fault, not its start**; I had misread
it as the corruption landing when it was the fix landing.

Evidence I gathered directly (still accurate as observations, only the
causal reading above is corrected):

- `ssh josh 'sha256sum ~/erdos-n70/.../pairwise_tables.py'` at the start of
  this task: `3094c6c0...` (byte-identical to the desktop copy, confirmed) --
  this was already the uncommitted worktree module on both machines.
- `ssh josh 'ls -la --time-style=full-iso .../pairwise_tables.py'` after the
  build: mtime `2026-09-19 18:22:48.315408290 -0700` -- the Manager's restore.
- `sha256sum` after the build: `c1200645...` (md5 `92636a0d`) -- the
  committed module, confirmed byte-identical to `pairwise-prod/pairwise_tables.py`
  by direct `diff` (see the update below).
- The worktree module hashed `shape_index` and `order` into the table header
  (`_HEADER_KEYS_V2`); the committed module writes `"format":
  "pairwise-tables-v1"` with no such fields (confirmed empty
  `MANIFESTS_WITH_ORDER_FIELDS` sweep below).

`grep '^tier' build-ext-all.log` timestamps the end of the fault window exactly
against the restore: `tier 72 9 rc=0 ...18:22:42`, then the restore at
`18:22:48`, then
`tier 72 8 rc=0 ...18:22:49`. Everything built **before** 18:22:48 -- all of
n=88, n=89, and n=72's b=8..12 -- was built with the uncommitted worktree
module. Everything built **after** -- n=72's b=6,7 and all of n=73..87 -- was
built with the just-restored committed module. Running
`check_tables_integrity.py integrity tables-ext` afterwards uses whatever
code is live *now*, so it recomputes hashes with the committed module's
schema and the pre-18:22:48 tiers fail self-verification: **every** shape in
those 11 tiers came back `bad_count == shapes` (100%), while b=6/7 and
n=73..87 were already clean. This is exactly the set of levels I had
reported to the Manager as "verified clean" minutes earlier for n=88/89 --
that claim held under the module that was live when I checked it, and
stopped holding the moment the committed module was restored under me.

**This was a hash-schema mismatch, not a data defect.** `header()` selects
its key set from the file's own stored `format` field, and `build()`
independently asserts `total_compositions == pair_count_dp(...)` regardless
of header schema -- the DP arrays and composition counts are untouched by the
header change. I confirmed this by rebuilding the 11 affected tiers
(`n=88 b=10,11,12`; `n=89 b=10,11,12`; `n=72 b=8,9,10,11,12`) against the
now-settled code (`c1200645...`, unchanged before/during/after the rebuild,
checked three times) and comparing `tier_total_compositions` before and
after: **identical to the digit** in all 11 tiers (e.g. n=88 total
15,321,886,088,199 both before and after; n=89 total 12,890,258,487,037 both
before and after). Only the persisted `.npz` files and their manifest
`tables_sha256` changed; the substantive numbers never moved.

**Mutation-check, naturally exercised rather than manufactured:** the RED
state is the first `check_tables_integrity.py integrity tables-ext` run
(`all_clean=False`, 11 tiers with `bad_count == shapes`, full mismatch
listing in `/tmp/integrity-final.json` on the laptop). The GREEN state is the
second run after rebuilding those 11 tiers, same command, same code, same
files-on-disk otherwise: `INTEGRITY tiers_checked=90 all_clean=True`, every
tier `bad_count=0 missing=0`. Both outputs are the raw tool output quoted
above and below; nothing was weakened to get GREEN, the actual `.npz` files
were regenerated.

**Consequence:** none for the Manager's chain -- n=88 and n=89's totals,
reported in my earlier message, are confirmed unchanged and now also
hash-verify. No other levels were affected (n=73..87 were never built with the
uncommitted module). `pairwise_tables.py` on the laptop has been the
committed module continuously since the Manager's 18:22:48 restore (checked
stable, unchanged, at three separate points during the rebuild below); the
caution is general, not a live concern here: re-run
`check_tables_integrity.py integrity` before trusting any tier if an
uncommitted worktree copy is ever placed back in `pairwise/`.

**Update after Manager's frozen-snapshot instruction (`pairwise-prod/`,
byte-exact to commit f63f9f3):** I never copied `pairwise_tables.py` to the
laptop myself at any point (only `gpu-blast-ext/n{72..89}.jsonl` manifests
and small one-off trigger/helper scripts unrelated to this module) -- the
file changing under me at 18:22:48 was an external edit, not something this
task did. Checked against the frozen snapshot directly:

```
md5sum ~/erdos-n70/.../pairwise-prod/pairwise_tables.py -> 92636a0daa1b98a7b8fff0cccb06e801
md5sum ~/erdos-n70/.../pairwise/pairwise_tables.py       -> 92636a0daa1b98a7b8fff0cccb06e801  (same)
diff pairwise-prod/pairwise_tables.py pairwise/pairwise_tables.py -> no output (byte-identical)
```

The module that has been live in `pairwise/` since 18:22:48 -- the one that
built n=73..87 in the original loop, and the one I used to rebuild the 11
affected tiers (n=88, n=89, n=72 b8-12) -- **is** the frozen snapshot, md5
`92636a0d`, confirmed by direct diff, not by hash alone. Re-ran the integrity
check by importing `check_tables_integrity` from
`pairwise-prod/` directly (not the `pairwise/` copy) against all 90 tiers:
`ALL_CLEAN True`. Also swept every one of the 90 `tier-manifest.json` files,
top level and per-shape, for `order_heuristic` and a per-shape `order` key:
`MANIFESTS_WITH_ORDER_FIELDS []` -- none present anywhere, including the 11
rebuilt tiers. Every manifest reads `"format": "pairwise-tables-v1"`. The
11-tiers-tainted diagnosis was accurate for the state right after my first
build (18:13:44-18:22:49); it no longer describes the tree, which was already
rebuilt and re-verified clean in the same task before this instruction
arrived. No further rebuild was necessary.

## 1. Census: `census_level.py --n N --out gpu-blast-ext`, desktop, cores 4,5, BelowNormal

Control run first: `python census_level.py --check ../gpu-blast/n68.jsonl` ->
`{"check": "../gpu-blast/n68.jsonl", "n": 68, "rows_existing": 6059,
"rows_census": 6059, "identical": true}` -- the census tool reproduces the
existing n68 manifest exactly.

n=72 was regenerated too (not skipped) as a determinism check: the new
`gpu-blast-ext/n72.jsonl` hashed `448640f7...`, byte-identical to the
pre-existing laptop copy (`sha256sum` on both sides), confirming
`census_level.py` is deterministic across a machine boundary as well as a
time boundary.

| n | eligible | by_b | unrestricted_ranks | sha256 (gpu-blast-ext/nN.jsonl) |
|---|---|---|---|---|
| 72 | 4029 | {6:1, 7:2, 8:137, 9:975, 10:1650, 11:1006, 12:258} | 1,154,764,268,375,770 | `448640f77e0aa96e412f3fb1c5bd2421a8ca1c503bdb42cc112292518fca54b9` |
| 73 | 3691 | {7:1, 8:90, 9:839, 10:1535, 11:973, 12:253} | 1,313,818,199,169,894 | `824bee755794c6031648bed5a120eaa7b4cd6eec9f07ee8a0fee5e0c9f2b9494` |
| 74 | 3263 | {8:43, 9:690, 10:1379, 11:905, 12:246} | 1,460,082,431,363,861 | `f67fff3d38c05d5ac4c54b52d4830606fcbc34501e94a7ad68d672693aee0e61` |
| 75 | 3002 | {8:27, 9:595, 10:1283, 11:860, 12:237} | 1,635,183,080,712,215 | `7bc2b7fbc06376868cf15f75885faa45465f02bf384c9e1f9e022874647b1b78` |
| 76 | 2567 | {8:6, 9:458, 10:1106, 11:777, 12:220} | 1,745,747,697,887,048 | `b16607f80ad99a32a4aae1fb4fdd8a2615b3189df954b3cd1ace38f477485d92` |
| 77 | 2332 | {8:5, 9:355, 10:1014, 11:741, 12:217} | 1,968,393,157,590,000 | `a97285b95de5d8d89505624689aded003adef921f4fe5a8ad7854c5126bba114` |
| 78 | 1969 | {9:262, 10:865, 11:644, 12:198} | 2,053,446,420,876,830 | `d9279aded6e8455e98c39e993ba1c4b9d3e2f177462581ec07ab14ab70952990` |
| 79 | 1739 | {9:174, 10:771, 11:607, 12:187} | 2,246,785,979,170,260 | `ad6a10a6eb016f7e4ace5a0706326c7919c5942b94ddeddf97be321c42ba8b14` |
| 80 | 1434 | {9:98, 10:616, 11:547, 12:173} | 2,366,339,720,238,000 | `65c07803f941d12d019eb393e8dd183ad573c3b1545020f6046d4dc39961487d` |
| 81 | 1290 | {9:37, 10:551, 11:532, 12:170} | 2,662,988,588,528,710 | `394040805316c92c6969d39933827e90766d5d47e71b1c9ab927343774e91005` |
| 82 | 1090 | {9:20, 10:460, 11:466, 12:144} | 2,644,795,244,913,510 | `31e151eadc16b4c3b5075c2564d2995c239791c4a96d5a4ea29ee1cd9e2ab789` |
| 83 | 955 | {9:7, 10:365, 11:442, 12:141} | 2,923,766,359,411,950 | `ac8ce34fc2fc7bf9b2e0828d93b24db0d08b0724af39af1c64a7f78c8636e601` |
| 84 | 809 | {9:2, 10:282, 11:396, 12:129} | 3,039,630,334,779,402 | `62efd0b80fceaff7f23949b92e1fda5afa7e8afc409cd0f727d1b3f1f6194d69` |
| 85 | 692 | {10:205, 11:366, 12:121} | 3,245,033,725,719,786 | `66960f3050f7e8763411bde853491b9a44911dcaf4234d57cff5871f0fb85217` |
| 86 | 539 | {10:134, 11:299, 12:106} | 3,193,968,397,804,002 | `89fc6ff2e8b3916de6e15b794d5cb953e0174e2eaa50bea1a37c9d8b58fc84ae` |
| 87 | 452 | {10:83, 11:269, 12:100} | 3,390,742,919,470,842 | `ac1f12a8eebb2dac40bacc18956f740db36a2b45aab2d97d10d5651f05a07b4c` |
| 88 | 330 | {10:29, 11:212, 12:89} | 3,343,340,275,771,392 | `7cea7d9c08404acae5bc3472e5605b9493393bff44d2b4968d4508fc6dafcc58` |
| 89 | 279 | {10:20, 11:173, 12:86} | 3,531,091,959,443,898 | `291afa53b8f7223aba03c3e592bc32a137d372f841ba48a8e3ec07279f8deca3` |

Sanity cross-check: n=88 `eligible=330` and n=89 `eligible=279` match the
`.done`-file entry counts in `REPORT-k6-level89-91-verify.md` and
`REPORT-k6-level92-verify.md` exactly, as they must -- same eligibility rule
(`len(forms)+2>=n`, `sum(lows)<=n`, `bound.hall_ok`), same shape catalog.

All 18 files scp'd to `josh:~/erdos-n70/search/shapecsp/pairwise/gpu-blast-ext/`;
`sha256sum` on both sides matched for every one of the 18 (verified
individually, not sampled).

## 2. Tables: `pairwise_tables.py build-tier --source gpu-blast-ext --n N --b B --workers 4 --out tables-ext`

Order: 89, 88 (per instruction, and these are the levels the CPU descent has
already decided -- see `REPORT-k6-level89-91-verify.md`), then 72..87
ascending, via `_mgr-laptop-build-ext.sh` with `LEVELS="89 88 72 73 74 75 76
77 78 79 80 81 82 83 84 85 86 87"`, `nohup`, `nice -n 19`. Run in two
launches because the first `export LEVELS="..."` was mangled by shell
quoting through the transport and only picked up `89`; confirmed from
`pgrep -af build-tier` before proceeding, then relaunched the remainder as
`88 72 73 ... 87` -- net effect identical to a single run in the required
order. 73 tier builds total (18 levels x 3-7 b-tiers each), every one
`rc=0`, zero failures. Wall time ~57 minutes (18:16-19:12 PDT) for 72..87
plus the earlier ~2 minutes for 89 and 88.

The `erdos-descent` service (4 bb workers deciding level 88 of the CPU
descent) ran continuously throughout, untouched: `MainPID=85681`,
`ActiveEnterTimestamp=Fri 2026-09-18 22:27:33 PDT` unchanged from before this
task started to after it finished.

### Per-level totals (post-rebuild, `check_tables_integrity.py integrity tables-ext` GREEN on all 90 tiers including the pre-existing n=67, n=71)

`tier_total_compositions` summed across each level's b-tiers; `prune` =
`tier_unrestricted_ranks / tier_total_compositions`; `gpu_hours@4e9` =
`compositions / 4e9 / 3600`, the projection basis SPEC.md names ("gpu_seconds
per unit, compositions per gpu-second... decides the cutover").

| n | b-tiers | compositions | unrestricted | prune | excluded shapes | gpu-hours @ 4e9/s |
|---|---|---|---|---|---|---|
| 72 | 7 | 65,727,181,014,457 | 1,154,764,268,375,770 | 17.6x | 15 | 4.564 |
| 73 | 6 | 70,441,022,501,860 | 1,313,818,199,169,894 | 18.7x | 11 | 4.892 |
| 74 | 5 | 68,327,422,800,432 | 1,460,082,431,363,861 | 21.4x | 2 | 4.745 |
| 75 | 5 | 70,084,953,373,785 | 1,635,183,080,712,215 | 23.3x | 0 | 4.867 |
| 76 | 5 | 65,238,650,617,716 | 1,745,747,697,887,048 | 26.8x | 0 | 4.530 |
| 77 | 5 | 67,049,710,157,175 | 1,968,393,157,590,000 | 29.4x | 0 | 4.656 |
| 78 | 4 | 61,757,648,991,437 | 2,053,446,420,876,830 | 33.3x | 0 | 4.289 |
| 79 | 4 | 61,042,424,770,019 | 2,246,785,979,170,260 | 36.8x | 0 | 4.239 |
| 80 | 4 | 51,433,191,043,035 | 2,366,339,720,238,000 | 46.0x | 0 | 3.572 |
| 81 | 4 | 53,613,097,286,258 | 2,662,988,588,528,710 | 49.7x | 0 | 3.723 |
| 82 | 4 | 48,122,144,589,301 | 2,644,795,244,913,510 | 55.0x | 0 | 3.342 |
| 83 | 4 | 44,750,698,505,101 | 2,923,766,359,411,950 | 65.3x | 0 | 3.108 |
| 84 | 4 | 38,916,433,788,309 | 3,039,630,334,779,402 | 78.1x | 0 | 2.703 |
| 85 | 3 | 40,102,777,004,278 | 3,245,033,725,719,786 | 80.9x | 0 | 2.785 |
| 86 | 3 | 19,643,904,966,689 | 3,193,968,397,804,002 | 162.6x | 0 | 1.364 |
| 87 | 3 | 18,121,842,864,059 | 3,390,742,919,470,842 | 187.1x | 0 | 1.258 |
| 88 | 3 | 15,321,886,088,199 | 3,343,340,275,771,392 | 218.2x | 0 | 1.064 |
| 89 | 3 | 12,890,258,487,037 | 3,531,091,959,443,898 | 273.9x | 0 | 0.895 |
| **72..89 total** | 73 | **872,585,248,849,147** | **43,919,918,761,227,370** | **50.3x** | 28 | **60.6 h** |

`excluded shapes` are manifest shapes with `total_compositions == 0` (the
pairwise-admissible set is structurally empty for that shape at that
cutoff, e.g. lows already forbid every pairwise-consistent completion) --
28 across the whole run, all in n=72..74, none beyond, confirmed via
`tier-manifest.json`'s own `excluded` list, not inferred.

`n=88` and `n=89` totals here are the same figures already sent to the
Manager, now re-verified against the settled code (see leading finding).

Prune ratio rises from 17.6x at n=72 to 273.9x at n=89 -- the closer the
cutoff to the already-refuted 92..111 block, the tighter the pairwise
constraint, matching the trend SPEC.md's own n68/69/70 measurements show
(41.9x-46.7x at b=12, well inside this run's n=88/89 range of 218x-274x for
the same reason: fewer, more constrained eligible shapes at higher cutoffs).

**Projection: ~60.6 GPU-hours at 4e9 compositions/second closes levels
72..89 entirely** (single-stream rate; SPEC.md's own cutover section notes
"same card and tier as the unrestricted kernel" for the real per-tier
`gpu_seconds` measurement once `gpu_search_pairwise.py` runs against these
tables -- 4e9/s is the projection basis given in this task, not yet a
measured rate for these specific tiers).

## 3. Exact commands

```
# desktop, cores 4,5 (affinity 0x30), BelowNormal priority
python census_level.py --check ../gpu-blast/n68.jsonl
for n in 72..89: python census_level.py --n <n> --out gpu-blast-ext

# desktop -> laptop
scp gpu-blast-ext/n{72..89}.jsonl josh:~/erdos-n70/search/shapecsp/pairwise/gpu-blast-ext/
sha256sum (both sides, all 18) -- 18/18 identical

# laptop, nohup, nice -n 19, workers=4, erdos-descent untouched
LEVELS="89 88 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87" \
  bash _mgr-laptop-build-ext.sh
  # -> for N in $LEVELS; for B in 12 11 10 9 8 7 6 (if present):
  #    pairwise_tables.py build-tier --source gpu-blast-ext --n $N --b $B \
  #      --workers 4 --out tables-ext

# after the schema-edit finding, rebuild of the 11 pre-edit tiers:
for (N,B) in (88,10) (88,11) (88,12) (89,10) (89,11) (89,12) \
             (72,8) (72,9) (72,10) (72,11) (72,12):
  pairwise_tables.py build-tier --source gpu-blast-ext --n $N --b $B \
    --workers 4 --out tables-ext

# verification, both times
check_tables_integrity.py integrity tables-ext
  # RED (pre-rebuild): all_clean=False, 11 tiers bad_count==shapes
  # GREEN (post-rebuild): tiers_checked=90 all_clean=True
```
