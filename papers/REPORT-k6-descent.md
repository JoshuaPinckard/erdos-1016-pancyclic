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
