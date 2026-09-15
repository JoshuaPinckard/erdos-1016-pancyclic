# k=6 harness and compute lane

Worker 13, 2026-09-15. Scope: the result-integrity harness under `search/shapecsp/`,
the n=68 exact witness hunt, and the planned range-mode descent below n=93.

This file exists because documentation sealing moved to another agent mid-pass.
Everything below is harness and compute; the mathematical write-up lives in
`REPORT-shape-csp.md` and is not edited by this lane after commit `4886eef`.

---

## Costliest finding: the solver binary was replaced under the running hunt, and the run's ledger cannot say which shapes used which build

At 00:31:31 local the laptop's `bb` — the executable `hunt.py` spawns once per
shape — was replaced while the n=68 exact hunt was running and writing its resume
ledger. Measured on the laptop:

| file | bytes | sha256 (first 16) | mtime |
|---|---:|---|---|
| `bb` | 29424 | `8852dfdbb55de6bb` | 00:31:31 |
| `bb-new` | 29424 | `8852dfdbb55de6bb` | 00:24:00 |
| `bb-orig` | 29424 | `8f7e9e463dd9b3d6` | 00:24:04 |
| `bb-prev-lastarc` | 17088 | `535a79f2b410700a` | 00:31:13 |

`bb` is now byte-identical to `bb-new`. `bb-prev-lastarc` is the build the hunt
started against at 00:17. The hunt process (`hunt.py 6 68 5 400000000 1`) resolves
`BB` to a **path**, not to an open handle, and re-spawns it per shape, so shapes
decided before 00:31:31 ran `535a79f2…` and shapes decided after ran `8852dfdb…`.

The ledger records no build identity:

```
$ head -3 hunt-k6-n68-exact.done
0 UNSAT
1 UNSAT
4 UNSAT
```

37 rows at the time of writing, `<eligible-index> <verdict>`, spanning both
builds with nothing marking the boundary. The independent review's handoff asked
for exactly this and it is not yet done: *"Associate each shape result with the
exact source/binary and input identity."*

**Severity, stated precisely rather than inflated.** This does not endanger a
witness: `hunt.py` routes every SAT through `verify.check_record`, which
materialises the graph and tests pancyclicity outside the reformulation, so a hit
is a positive certificate whatever produced it. The exposure is entirely on the
**UNSAT** side — those 37 rows are a partial non-existence certificate whose
provenance is unrecorded, and non-existence is the claim that cannot be
re-checked from the artefact.

**What is and is not known about the two builds.** `bb.c` is unchanged across the
swap; both builds carry `lastarc`. The peer's differential compared `bb-orig`
(pre-`lastarc` source, `bb-orig.c`) against `bb-new` and reported
`DIFFTEST OK -- 1250 record comparisons agree, 973 SAT witness(es) independently
checked on both builds` at k=4 and 78/63 at k=3. That is a real result, and it is
not this one: the pair the hunt actually mixed is `bb-prev-lastarc` against
`bb-new`, and those two were never differentially compared. The 17088-vs-29424
size gap is unexplained — same source, different build flags — and I did not
determine which. "Could not look", not "nothing there".

**Remedy (not applied — see ownership below).** Record the solver's sha256 in the
`.done` ledger header and refuse to resume a ledger written by a different build,
or re-decide the 37 rows under a single pinned binary. Either is cheap next to
53 hours of search; neither should be done while two agents are writing the
directory.

---

## Ownership blocker: two agents are holding this lane

I reported a duplicate lane earlier and the reassignment did not resolve it, so
restating with sharper evidence. A second agent is live on both machines:

- Laptop, 00:23:50: ten files rewritten in one batch, between two of my own reads.
- Laptop, 00:24:00–00:24:04: `bb-new`/`bb-orig` compiled; 00:26:39 `diffrun.sh`.
- Laptop, 00:31:07–00:31:50: `verify.py`, `sweep.py`, `hunt.py` re-pushed;
  `bb` swapped; `ctl5.sh` written; a k=5 control started
  (`control-k5-laptop.log`, running, down to `n=50: eligible=23 sat=0 gaveup=0`).
- Desktop working tree: `search/shapecsp/sweep.py` modified against `4886eef` by
  someone other than me.

`agent_comms.local_roster` from "Worker 13" lists only the manager as reachable,
so I cannot deconflict directly.

**Consequently the descent from n=93 is NOT started, deliberately.** Starting an
11-worker range-mode descent into a directory where another agent is swapping the
solver binary and running controls would produce levels nobody can attribute —
the precise failure this lane was created to remove. The n=68 hunt is left
running rather than restarted to raise the worker count, for the same reason.

I also left `sweep.py` unpatched although it carries the same defect fixed below,
because it is being edited by that agent and was executing at the time.

---

## Repaired this pass

### Unclosed cache handles (flagged by Worker 2)

`pickle.load(open(cache, "rb"))` leaked a file object in three drivers. Replaced
with `with` blocks in `level.py`, `hunt.py` and `capscan.py`.

The check is on stderr content, not exit status: the warning is raised during
garbage collection, so it prints without changing the return code. Measured, same
command, `python -W error::ResourceWarning -B level.py 2 8 1000`:

```
PRE-FIX   exit=0  ResourceWarning lines on stderr: 1
            ResourceWarning: unclosed file <_io.BufferedReader name='...forms-k2.pkl'>
FIXED     exit=0  ResourceWarning lines on stderr: 0
```

1 → 0, so the instrument discriminates. Exit status alone would have reported the
defect as absent both before and after.

`hunt.py`'s resume ledger (`donef = open(DONE, "a", buffering=1)`) is deliberately
held open for the life of the run and closed after the executor drains; it was not
converted to a per-write open, and that is a decision rather than an oversight.

`sweep.py` still has the defect, for the ownership reason above.

### A self-inflicted defect worth recording

My first attempt wrote the three files with `pathlib.write_text`, which applies
platform newline translation and silently converted all three to CRLF — 117, 178
and 66 carriage returns. Nothing in the test suites caught it. The mutation check
did, by refusing:

```
REFUSED level.py rejects a missing terminal record: anchor occurs 0 times in level.py, expected 1
REFUSED level.py rejects a SAT the graph checker refuses: anchor occurs 0 times in level.py, expected 1
```

The two single-line anchors still matched; only the two multi-line ones broke.
Had `mutation-check.py` not asserted its anchor count, both would have written a
no-op mutant, both gates would have reported OK, and the check would have
certified two gates it never touched. Repaired by rewriting the bytes with
`\r\n` → `\n`.

---

## Verification, this pass

All run by me on the desktop tree after the handle fix and the CRLF repair.

```
=== six review contract tests ===         Ran 6 tests in 0.814s / OK
=== mutation check ===                    MUTATION CHECK: 4/4 gates went RED (failures=1)
                                          when disabled and GREEN when restored
=== pre-existing suite (test_shapecsp) === ALL GATES PASS
=== ResourceWarning lines on stderr ===   0
```

The four gates and their RED/GREEN evidence, the vacuity defect found in the
contract tests themselves, and the correction to the `t_6 <= 93` justification are
recorded in `REPORT-shape-csp.md` section 0a, committed in `4886eef` **before**
documentation ownership moved. That section is this lane's work and should survive
the sealing pass; its substance is the withdrawal of the claim that `t_6 <= 93`
was established by level n=94 alone, which a two-line k=2 command refutes.

## Compute status

n=68 exact hunt, observed 00:35:30 local:

```
# 30/6059 elapsed=193s rate=0.031 shapes/s projected_total=53.8h gaveup=0 errors=0
```

37 shapes decided in the ledger, 5 workers at nice 10, `gaveup=0`, `errors=0`.
**No SAT. There is no verified witness at n >= 68 to report.**

Descent below n=93: not started. n=93 and n=92 remain 0-byte holes, so there is no
coverage below 93 at all, and a single UNSAT level at 93 would not tighten the
bound on its own — it has to join the contiguous 94..111 block.

---

# Continued by Worker 7, sole owner of this lane from 00:50

The ownership blocker above is resolved: the manager assigned `search/shapecsp/`
and the laptop to one agent. Everything below is mine. The section above is
Worker 13's and is not edited, including the parts I can now answer — those are
answered here instead.

## The provenance gap is closed by an enforced invariant, not by an intention

Worker 13's finding is correct and its remedy is implemented. The ledger now
carries the solver's sha256 and a resume refuses any other build:

```
# solver sha256=93af338d0c161b897602b3a1d61113e802a7d4faca5184f8e346a2d70271a171 binary=bb.exe k=2 cutoff=9 mode=range nodecap=1000000
0 UNSAT
```

Hand-checked with two genuinely different builds rather than a doctored file —
`bb-orig.exe` put in place of `bb.exe` between two runs of the same command:

```
same build      resume: 1 shape(s) already decided in hunt-k2-n9-range.done, same solver build
different build REFUSING to resume ...: it was written by solver sha256=93af338d..., this run's
                solver is sha256=edff4b13...  Restore that build or move the ledger aside; a
                ledger spanning two builds cannot attribute its UNSAT rows.        exit=1
no header       REFUSING to resume ...: it has 2 row(s) and no solver sha256 header, so the
                build that decided them is unknown.                                exit=1
```

Neither refusal appends a row — asserted, not assumed. Both refusals exit
non-zero, which matters because a gate that exits 0 is the defect the review
already found once in `satcheck.py`.

`hunt.py`'s docstring said a binary change costs nothing. True of resume progress,
false of provenance, and that sentence is precisely what kept the gap invisible;
it now states the opposite and the reason.

Three contracts hold this (`LedgerProvenanceContracts`) and two gates were added
to the mutation check, now **6/6 RED when disabled, GREEN when restored**. The
first attempt at the stamp gate was *REFUSED by the anchor count* rather than
reported as live — `hunt.py` is CRLF and `level.py` is LF, so the multi-line
anchor matched one file and silently missed the other. That is the second time
this pass that the anchor discipline caught a no-op mutation; Worker 13's
`pathlib.write_text` CRLF incident above was the first.

## The pinned build for the descent

The whole 93-downward descent runs on one binary, rebuilt clean from HEAD:

| | |
|---|---|
| source | `bb.c` at HEAD, sha256 `eb59b4f641cadaf3bad2e2d4fb68ba1d7dbc34606b6092ccc84ab3287791a1ac` |
| compiler | gcc 13.3.0 (Ubuntu 13.3.0-6ubuntu2~24.04.1), exit 0, two known `scanf` `-Wunused-result` warnings |
| flags | `-O3 -std=c11 -Wall -Wextra -Wpedantic` |
| **binary sha256** | **`e2fde07b69d7a0d84b67d7954304da50feebd84a3cbd0e192faf706a8a7f562c`** (29432 bytes) |
| reproducible | a second build from the same source gives the identical digest |

Kept as `bb-pinned` alongside `bb`, so the pin can be re-checked at any time, and
every level's ledger header now names it.

A pinned build is a *third* artifact, so it does not inherit the earlier
differential — by the same standard applied to `bb-prev-lastarc`, it gets its own:

| comparison | record comparisons | disagreements | witnesses re-checked |
|---|---|---|---|
| `bb-new` (previously validated) vs **pinned**, k=3, cutoffs 8..20 | 78 | **0** | 63 |

The pre-descent artefacts written by the unpinned binary were archived rather
than appended to: `hunt-k6-n93-range.done.unpinned-archived` (2 rows),
`descend.log.unpinned-archived`, `descend-k6.csv.unpinned-archived`. Two shapes of
work discarded; the alternative was a ledger the new rule exists to forbid.

## Answering the two "could not look" items above

**The 17088-vs-29424 size gap is the optimisation level, not a source
difference.** Compiling the current source at `-O2` gives **17096** bytes against
`bb-prev`'s 17088, while `-O3` gives 29432. So the small build is an `-O2` build.
The residual 8 bytes is a source-revision difference I did not chase further —
that part remains "did not look", and it does not matter now, because nothing
below depends on either of those two builds.

**The `bb-prev-lastarc` vs `bb-new` pair still has no differential, and now never
needs one.** Every result that depended on it — the 39-row n=68 exact ledger — is
discarded with the hunt, and the descent starts from an empty ledger under the
pinned build. The gap is closed by not retaining the results, which is what the
manager directed.

**`sweep.py` is patched.** Worker 13 left it alone because another agent was
executing it; that agent was me. Both leaks are closed, both paths measured with
`-X dev`: read path 2 ResourceWarning lines → 0, cache-rebuild path 0, stderr
empty, `t_2 = 8` unchanged. No `pickle.load(open(...))` remains in the directory.

## HEAD is known-good before the descent starts

Two agents committed to `search/shapecsp/` (`30080d6`, `4886eef`, `6dbe9ee`), so
the tree was re-validated end-to-end at `05176de` rather than trusting either
agent's earlier pass. Desktop:

```
test_shapecsp.py            ALL GATES PASS                                   exit=0
test_review_contracts.py    Ran 9 tests / OK                                 exit=0
mutation-check.py           6/6 gates RED when disabled, GREEN when restored exit=0
sweep.py 2 3                RESULT t_2 = 8   gaveup_records=0                exit=0
sweep.py 3 3                RESULT t_3 = 14  gaveup_records=0                exit=0
sweep.py 4 3                RESULT t_4 = 24  gaveup_records=0                exit=0
```

## The cost curve, computed before paying for it -- and there is no knee

The stop-and-report gate was set at "when the eligible count climbs toward the low
thousands". That trigger can be evaluated **now** rather than discovered level by
level, because eligibility is three cheap tests (cap, lower-bound sum, Hall) while
the levels themselves are hours. `costcurve.py` computes the whole curve in a
second.

The shape count alone understates the wall: a level hands each eligible shape the
whole range `[n, cap]` and every rung has to be refuted, so `rungs`, the sum of
`cap - n + 1` over eligible shapes, is the better proxy.

| n | eligible | rungs | x prev | | n | eligible | rungs | x prev |
|---|---|---|---|---|---|---|---|---|
| 93 | 114 | 373 | | | 83 | 955 | 4976 | 1.24x |
| 92 | 152 | 525 | 1.41x | | 82 | 1090 | 6066 | 1.22x |
| 91 | 181 | 706 | 1.34x | | 81 | 1290 | 7356 | 1.21x |
| 90 | 214 | 920 | 1.30x | | 80 | 1434 | 8790 | 1.19x |
| 89 | 279 | 1199 | 1.30x | | 79 | 1739 | 10529 | 1.20x |
| 88 | 330 | 1529 | 1.28x | | 78 | 1969 | 12498 | 1.19x |
| 87 | 452 | 1981 | 1.30x | | 77 | 2332 | 14830 | 1.19x |
| 86 | 539 | 2520 | 1.27x | | 76 | 2567 | 17397 | 1.17x |
| 85 | 692 | 3212 | 1.27x | | 75 | 3002 | 20399 | 1.17x |
| 84 | 809 | 4021 | 1.25x | | 68 | 6059 | 52629 | |

**There is no knee.** Growth is a smooth 1.13-1.41x per level with no cliff to
stop at, which means the gate cannot be triggered by spotting a discontinuity --
there isn't one. Each further unit of upper bound costs about 20% more than the
one before it, all the way down.

### Calibrating the proxy instead of trusting it

Eight levels have both a rung count and a measured single-core time, so the proxy
can be checked rather than assumed:

| n | rungs | measured s | s/rung |
|---|---:|---:|---:|
| 101 | 5 | 18.1 | 3.6 |
| 100 | 13 | 48.1 | 3.7 |
| 99 | 37 | 521.6 | 14.1 |
| 98 | 65 | 1197.9 | 18.4 |
| 97 | 93 | 2727.1 | 29.3 |
| 96 | 125 | 4682.5 | 37.5 |
| 95 | 178 | 9529.9 | 53.5 |
| 94 | 259 | 4070.6 | **15.7** |

**The proxy is weak and the table says so.** Cost per rung is not constant: it
rises 15-fold across the block and then *falls* by more than half from n=95 to
n=94, so rung count predicts the curve's shape but not its height. n=95 taking
2.3x the wall-clock of n=94 on 31% fewer rungs is the clearest warning: a single
stubborn shape dominates a level, and which level gets one is not predictable
from this table.

### What it projects, stated as the lower bound it is

At the measured mean of 29.4 s/rung over 775 rungs of calibration, five workers,
assuming perfect packing:

| target | block | projected |
|---|---|---|
| `t_6 <= 87` | 93..88 | **~9 h** |
| `t_6 <= 84` | 93..85 | **~21 h** |
| `t_6 <= 74` | 93..75 | **~196 h (8 days)** |

These are **lower bounds**, twice over: the rate rose steadily through the
calibration block, so the deep levels are likely worse per rung, and the five
workers will not pack perfectly against levels that contain one dominant shape.

The operational conclusion is worth stating plainly, because it changes where the
gate should sit. The gate as specified -- eligible counts in the low thousands --
is not reached until n = 82..75, by which point 46 to 196 hours are already spent.
The cheap, decision-relevant stopping points are **n=88 at about 9 hours** and
**n=85 at about 21 hours**. Below 85 the descent stops being an incremental buy
and becomes the weeks-long commitment, on an allocation of five cores.
