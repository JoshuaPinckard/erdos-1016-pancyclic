# REPORT — record integrity of the `n=38..41` evidence (2026-09-14, Worker 11)

Project root: `C:\Users\ToolsEnabled-Dev\Desktop\erdos1016` (git, branch
`master`, HEAD before this pass `d7a649c`). All paths below are relative to
it. Every measurement quoted here was taken in this pass, on this tree.

## Costliest finding first: `h(41)=6`'s lower half was described as "exhaustive and cross-checked" but is a single algorithm plus a port, and its cited evidence was not in the repository

`h(41)=6` is the only value in `n=38..41` where the threshold moves, and its
lower half — "no 5-chord set on `C_41` is pancyclic" — is the only new
*negative* claim in the paper. The draft (`papers/draft/pancyclic-exact-values.md`,
Section 3.4 and the abstract) presented it as exhaustive and folded it into
"cross-checked by three further from-scratch verifiers." The artifacts say:

| What the draft implied | What the artifacts show |
|---|---|
| Two independent exhaustive `NONE` results | `search/gpu-41-5d.txt` and `search/k6/gpu128-41-5.txt` both print `NONE n=41 k=5 tested=17615450195`. `17615450195` is **exactly** the candidate count of the three-mode case split (recomputed below from `search/gpu_pancyc.py`'s `main`), so identical totals mean "same enumeration walked to the end", nothing more. `search/k6/gpu_pancyc128.py`'s docstring: "128-bit (two-word) port of search/gpu_pancyc.py … Nothing else about the algorithm changes." |
| A CPU cross-check | `search/hn_k5.csv` row `41,5,ABORTED-no-output-processes-died,,8044,0`; `search/sh-41-A0.txt` … `sh-41-A7.txt`, `sh-41-BC.txt` are all 0 bytes. |
| A from-scratch replication | `papers/REVIEW-independent-gpu.md`: corrected prefix of 739,246,080 of 15,147,912,850 mode-A ranks (4.9% of one of three modes), "the exhaustive b=2 total remains UNKNOWN pending continuation from the corrected checkpoint." |
| Evidence in the repo | `git ls-files` returned nothing for `search/n38k5-A0.txt`, `search/ls-41-6.txt`, `search/gpu-41-5.txt` and 28 other cited files: all matched by blanket `.gitignore` patterns. `search/gpu-41-5d.txt` (the tracked one) is a **18-second re-invocation** that reloaded a finished state file; the actual complete run log, `search/gpu-41-5.txt` (719 s of progress lines to 100.0%), was untracked. |

What *is* fully supported and was left at full strength: every witness
(`h(38),h(39),h(40)≤5`, `h(41)≤6`) is an explicit object reconfirmed by
`search/verify.py`, `papers/construction/check.py`, `papers/construction/indep.c`
and kernel-checked Lean (`pancyclicWithChords_38_5` … `_41_6`,
`pancyclicWithChords_56_6`); `h(n)≥5` for `n=38..41` is pure counting; the
`n=40` `--all` run is a tracked, complete enumeration; and `h(41)>5` *is*
established by one complete enumeration — that sentence stays, with its
replication status stated next to it.

Candidate-count recomputation (Python, from the case split in
`search/gpu_pancyc.py` `main`: mode A fixes `(0,2)` and chooses 4 of the
remaining 778 chords; mode B fixes `(0,b),(1,b)` over `b`, choosing 3 of the
remaining span≠2 chords; mode C fixes the chord triangle `(0,b),(b,c),(0,c)`,
choosing 2):

```
M 779 modeA C(778,4)= 15147912850
expected total tested for n=41,k=5 case split: 17615450195
```

`15147912850` is also the denominator of every `progress` line in
`search/gpu-41-5.txt` and `search/k6/gpu128-41-5.txt`.

---

## Job 1 — evidence reachability

### `.gitignore` change (committed)

Appended after the existing patterns, which are unchanged:

```
# Evidence files cited as primary sources by papers/draft/SOURCES.md and
# papers/draft/pancyclic-exact-values.md Section 3.4. Kept tracked so the
# draft's claims are checkable from the repository alone; see
# papers/REPORT-record-integrity.md for the list and rationale.
!search/n38k5-A0.txt
!search/n38k5-A1.txt
!search/n38k5-A2.txt
!search/n38k5-A3.txt
!search/n38k5-A4.txt
!search/n38k5-A5.txt
!search/n38k5-A6.txt
!search/n38k5-A7.txt
!search/n38k5-BC.txt
!search/ls-41-6.txt
!search/gpu-41-5.txt
!search/sh-41-A0.txt
!search/sh-41-A1.txt
!search/sh-41-A2.txt
!search/sh-41-A3.txt
!search/sh-41-A4.txt
!search/sh-41-A5.txt
!search/sh-41-A6.txt
!search/sh-41-A7.txt
!search/sh-41-BC.txt
!search/k6/gpu128-41-5.txt
!search/k6/coord-66.txt
!search/k6/strict-66.txt
!search/k6/gkw-K4.txt
!papers/construction/unrank.out
!papers/construction/gpu41b2s0.out
!papers/construction/indep-gpu41.log
!papers/construction/indep-gpu41b2-corrected.log
!papers/construction/random41-1.out
!papers/construction/random41-2.out
!Axioms.lean
```

Why each group: the nine `n38k5-*` files, `ls-41-6.txt`, `k6/coord-66.txt`,
`k6/strict-66.txt`, `k6/gkw-K4.txt`, `papers/construction/unrank.out` and
`Axioms.lean` are named directly in `papers/draft/SOURCES.md`. `gpu-41-5.txt`
was named by the assignment and is the only complete-run log of the
elimination. `k6/gpu128-41-5.txt`, the nine zero-byte `sh-41-*` files and the
five `papers/construction` corroboration artifacts are what the corrected
Section 3.4 and the new `SOURCES.md` rows cite for the elimination's status;
they are tiny (largest 12,871 bytes) and are the artifacts a reader would have
to see to check the corrected claims. `search/k6/gpu_pancyc128.py` (the port
program itself, untracked but not ignored) was added alongside its output.

### Mutation check on the ignore rules

`git check-ignore` over the 31 paths, before and after the edit (a printed
path = still ignored):

```
BEFORE (git check-ignore; a printed path = ignored):
31
AFTER:
0
```

### `git ls-files` proof (staged, then committed — see commit hash at the end)

```
TRACKED 72B search/n38k5-A0.txt
TRACKED 70B search/n38k5-A1.txt
TRACKED 73B search/n38k5-A2.txt
TRACKED 73B search/n38k5-A3.txt
TRACKED 71B search/n38k5-A4.txt
TRACKED 73B search/n38k5-A5.txt
TRACKED 70B search/n38k5-A6.txt
TRACKED 73B search/n38k5-A7.txt
TRACKED 70B search/n38k5-BC.txt
TRACKED 67B search/ls-41-6.txt
TRACKED 12685B search/gpu-41-5.txt
TRACKED 0B search/sh-41-A0.txt
TRACKED 0B search/sh-41-A1.txt
TRACKED 0B search/sh-41-A2.txt
TRACKED 0B search/sh-41-A3.txt
TRACKED 0B search/sh-41-A4.txt
TRACKED 0B search/sh-41-A5.txt
TRACKED 0B search/sh-41-A6.txt
TRACKED 0B search/sh-41-A7.txt
TRACKED 0B search/sh-41-BC.txt
TRACKED 12871B search/k6/gpu128-41-5.txt
TRACKED 148B search/k6/coord-66.txt
TRACKED 1367B search/k6/strict-66.txt
TRACKED 930B search/k6/gkw-K4.txt
TRACKED 532B papers/construction/unrank.out
TRACKED 122B papers/construction/gpu41b2s0.out
TRACKED 1160B papers/construction/indep-gpu41.log
TRACKED 1526B papers/construction/indep-gpu41b2-corrected.log
TRACKED 75B papers/construction/random41-1.out
TRACKED 75B papers/construction/random41-2.out
TRACKED 657B Axioms.lean
```

Before the change the same loop printed `NOT-TRACKED` for all 31 (the three
the assignment measured — `search/n38k5-A0.txt`, `search/ls-41-6.txt`,
`search/gpu-41-5.txt` — plus the 28 others; `search/gpu-40-5-all.txt`,
`search/gpu-41-5d.txt` and `search/hn_k5.csv` were already tracked, as the
assignment also measured).

### Cited files deliberately *not* tracked (accounted for instead)

| File | Size (bytes) | SHA-256 | Reason |
|---|---:|---|---|
| `papers/Lai-Liu-2014-survey.pdf` | 589,233 | `fd8361d68030e8805e6960e40ed96a0d31b913e36f2b141f6f1bb4ed1b52ec61` | third-party published PDF; `papers/*.pdf` exclusion is a redistribution choice, not a size one |
| `papers/Wallis-2014-IWOCA-open-problems.pdf` | 177,398 | `d94ab4060e444f3692f7a086e5cefaeb125b7e4b7274edaa9f98742005d98863` | same |

Both are recorded with size and hash in `SOURCES.md`'s new "Evidence
reachability" section. This is a judgment call (the assignment's stated
exception was size); if the operator prefers them tracked, adding
`!papers/Lai-Liu-2014-survey.pdf` and `!papers/Wallis-2014-IWOCA-open-problems.pdf`
to `.gitignore` is the whole change.

### Post-pass sweep

Every backticked file path in `SOURCES.md` was re-resolved after the edits.
All resolve to tracked files except: `papers/REPORT-record-integrity.md` and
`search/hn_k5-README.md` (both created in this pass and committed with it).

---

## Job 2 — Section 3.4 (and the sentences that echo it), old vs. new

### Section 3.4, `n=41` table row

**Old:**

```
| 41 | $h(41)>5$ (elimination of all $k=5$ chord sets) and a $k=6$ witness | `search/gpu_pancyc.py`, `search/gpu-41-5d.txt` (`tested=17615450195`, `NONE`, cumulative across resumed runs); `search/localsearch.py`, `search/ls-41-6.txt` (witness) | the $k=5$ elimination is exhaustive; the $k=6$ witness search is not |
```

**New:**

```
| 41 | $h(41)>5$ (no $5$-chord set on $C_{41}$ is pancyclic) and a $k=6$ witness | elimination: `search/gpu_pancyc.py`, `search/gpu-41-5.txt` (one complete walk, `NONE n=41 k=5 tested=17615450195 seconds=845`; `search/gpu-41-5d.txt` is a re-invocation reprinting the finished state); witness: `search/localsearch.py`, `search/ls-41-6.txt` | the $k=5$ elimination is one complete enumeration by one program — see "What is multiply confirmed" below; the $k=6$ witness search is not exhaustive |
```

### Section 3.4, paragraph after the table

**Old:**

```
Every witness reported as a table entry in Section 2 was independently
reconfirmed by at least two of the three from-scratch verifiers
(`search/verify.py`, `papers/construction/check.py`,
`papers/construction/indep.c`); see `papers/REVIEW-search.md` for the exact
reconfirmation runs and lengths recovered. For $n=38,41$, the Lean proofs of
Section 3.3 add a fourth, kernel-checked confirmation.
```

**New:**

```
**What is multiply confirmed, and what is not.** The evidence behind the four
new values is of two different kinds and should not be read as one.

*Witnesses (every upper bound; all of $h(38),h(39),h(40)\le5$ and
$h(41)\le6$).* Each witness chord set in Section 2 is an explicit object that
any program can check. Each was independently reconfirmed by the three
from-scratch verifiers of Section 3.3 — `search/verify.py` (networkx
`simple_cycles`), `papers/construction/check.py` (a second cycle-space
implementation) and `papers/construction/indep.c` (direct DFS, no cycle
space) — see `papers/REVIEW-search.md` and `papers/REVIEW-independent.md` for
the runs and the length sets recovered — and, for all of $n=38,39,40,41$ (and
$56$), by a kernel-checked Lean 4 proof (`pancyclicWithChords_38_5` …
`_41_6`, Section 3.3). These claims are multiply and independently confirmed.

*The lower bounds $h(n)\ge5$ for $n=38..41$.* Pure counting, as shown at the
top of this subsection; no search is involved.

*The non-existence result $h(41)>5$.* This is the only new negative claim,
and the only place in $n=38..41$ where the threshold moves. Unlike a
witness, it cannot be checked by inspecting an object; it can only be
re-established by another complete enumeration. Its present evidential
status, read directly from the artifacts, is:

* It **is** established by one complete enumeration: `search/gpu-41-5.txt`
  logs `search/gpu_pancyc.py` walking mode A from 0.4% to 100.0% and then
  printing `NONE n=41 k=5 tested=17615450195`, and `17615450195` is exactly
  the candidate count of the three-mode case split (Section 3.3), so the walk
  was complete, not truncated.
* It is **not** independently replicated. The second `NONE` run,
  `search/k6/gpu128-41-5.txt` (`NONE n=41 k=5 tested=17615450195`), is
  `search/k6/gpu_pancyc128.py`, whose own docstring describes it as a
  "128-bit (two-word) port of `search/gpu_pancyc.py` … Nothing else about the
  algorithm changes." The identical `tested=` total shows the two programs
  walk the identical enumeration; this is a check on 64-bit mask overflow,
  not on a logic error that both would share.
* The CPU shard run — the one structurally separate exhaustive path that was
  attempted — did not complete: `search/hn_k5.csv` records
  `41,5,ABORTED-no-output-processes-died,,8044,0`, and its shard outputs
  `search/sh-41-A0.txt` … `sh-41-A7.txt`, `sh-41-BC.txt` are all zero bytes.
  Two later rows in the same file recorded `NONE` with `tested=0` (the shard
  runner's default when every process exits without output); they test no
  candidates, are not evidence, and are re-labelled `INVALID-NONE-…` in the
  file (`search/hn_k5-README.md`).
* The from-scratch direct-DFS GPU replication
  (`papers/construction/indep_gpu.py`, `papers/REVIEW-independent-gpu.md`)
  is unfinished: a corrected contiguous prefix of $739{,}246{,}080$ of the
  $15{,}147{,}912{,}850$ mode-A ranks (under 5% of one of the three modes)
  with $0$ hits, and, in that review's words, "the exhaustive b=2 total
  remains UNKNOWN pending continuation from the corrected checkpoint."
* Non-exhaustive corroboration exists: $2{,}000{,}000$ uniformly random
  $5$-subsets checked by `indep.c` with $0$ hits, against a positive control
  that does find a witness at $n=24,k=4$ (next paragraph).
* Nothing about this negative result is formalised in Lean; the project's
  `Axioms.lean` states that the lower bounds "are NOT formalised here; they
  rest on the exhaustive search programs in `search/`."

So $h(41)=6$ currently rests on one algorithm (plus a port of it) for its
lower half. We report it as established by that enumeration, and we report
the enumeration's replication status as above rather than as
"cross-checked." Completing an independently written exhaustive run
(`indep_gpu.py` or a CPU direct-DFS enumeration) is the outstanding step
that would raise this claim to the same footing as the witnesses.
```

The unchanged "Independent corroboration of the search machinery itself"
paragraph (colex unranking `failures=0`, `n=24/25` reproduction, the
2,000,000-sample random search with positive control) follows; it already
described the random search as "corroboration (not proof)".

### Sentences elsewhere that echoed the old claim (aligned so the draft does not contradict itself)

*Abstract* — old: "obtained by two independently implemented GPU/CPU
chord-search programs (each capable of exhaustive search; … the matching
lower bounds and one upper-bound elimination were run to full exhaustion) and
cross-checked by three further from-scratch verifiers, including a
kernel-checked Lean 4 proof for $n=38,41$". New: "The upper bounds are explicit
chord sets found by GPU/CPU chord search, each reconfirmed by three
from-scratch verifiers and by a kernel-checked Lean 4 proof. The lower bounds
$h(n)\ge5$ follow from Griffin's cycle-counting ceiling alone. The one new
negative result, $h(41)>5$, rests on a single complete GPU enumeration of all
$5$-chord sets on $C_{41}$ (a 64-bit kernel and its 128-bit port, which walk
the same enumeration) plus non-exhaustive corroboration; an independently
written exhaustive replication has not yet been completed (Section 3.4)."

*Section 2 table, `n=41` row* — old: "`search/gpu-41-5d.txt`, exhaustive
elimination of $k=5$". New: "`search/gpu-41-5.txt`, complete single-program
elimination of $k=5$ - see Section 3.4 for its evidential status".

*Section 3.3, `gpu_pancyc.py` bullet* — old: "this is why
`search/gpu-41-5d.txt`'s cumulative `tested=17615450195` spans several
restarted invocations (visible as the `ABORTED`/`NONE` sequence in
`search/hn_k5.csv`'s $n=41$ rows)". This was factually wrong on two counts:
`gpu-41-5.txt` is one uninterrupted walk to 100.0% reaching that total, and
`hn_k5.csv` is written by the CPU runner `search/run_shards.ps1`, not by the
GPU program. New text explains that `tested=` equals the case split's
candidate count, names `gpu-41-5.txt` as the complete-run log and
`gpu-41-5d.txt` as the 18-second re-invocation, and records the earlier
misdescription in a parenthesis.

### Claims deliberately not weakened

The values `h(38..41)=5,5,5,6`; every witness; "the `--all` run is
exhaustive" for `n=40` (`search/gpu-40-5-all.txt`, tracked,
`tested=14373209608 witnesses=10`); every Lean statement; the `n=24/25`
independent reproduction. The `n=41,k=5` elimination is still stated as a
complete enumeration — the artifact supports that — only its "cross-checked
/ independently replicated" status was corrected.

---

## Job 3 — `search/hn_k5.csv`

**Old (verbatim, including the blank line and the two `done` lines):**

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

**New:**

```
n,k,result,witness,seconds,tested
39,5,WITNESS,"(0,2) (0,18) (1,12) (3,19) (17,20)",3201,61561098
40,5,WITNESS,"(0,5) (1,5) (2,30) (3,10) (4,11)",7424,132830426
41,5,ABORTED-no-output-processes-died,,8044,0
41,5,INVALID-NONE-tested-zero-processes-died,,66,0
41,5,INVALID-NONE-tested-zero-processes-died,,187,0
```

Mechanism (from `search/run_shards.ps1`): when every `pancyc3.exe` shard
exits without a `WITNESS` line the script appends
`"$n,$k,NONE,,<seconds>,<tested>"` with `<tested>` = sum of `tested=` over
the `sh-{n}-*.txt` outputs — which is `0` when the shards died without
writing — and then appends a bare `done`. So both `NONE` rows record runs
that tested zero candidates in 66 s and 187 s; they are not evidence. The
`result` field is re-labelled so that any filter on `result == NONE` no
longer matches them; `seconds` and `tested` are kept verbatim; the
already-hand-labelled `ABORTED` row is unchanged. The original file and this
mechanism are recorded in the new `search/hn_k5-README.md`.

Well-formedness check after the rewrite (Python `csv`):

```
well-formed rows: 6 NONE rows: 0
```

(6 rows × 6 fields including the header; zero rows whose `result` is `NONE`.)

---

## Other files touched

* `papers/draft/SOURCES.md` — `n=41` row now cites `gpu-41-5.txt` with
  status; the "Cumulative `tested=17615450195` across resumed runs" row
  replaced by seven rows sourcing each new Section 3.4 statement; the
  "sourcing discipline" bullet no longer claims every `n≥38` value has an
  independent verifier (only the witnesses do); new "Evidence reachability"
  section.
* `papers/CHANGES.md` — one entry per change (items 1–5 under
  "Record-integrity pass").
* `search/hn_k5-README.md` — new.

## What was committed and what was left in the working tree, and why

Committed (one commit, this pass): `.gitignore`, the 31 newly tracked
evidence files, `search/k6/gpu_pancyc128.py`, `search/hn_k5.csv`,
`search/hn_k5-README.md`, and this report.

**Left uncommitted, deliberately:** `papers/draft/pancyclic-exact-values.md`,
`papers/draft/SOURCES.md` and `papers/CHANGES.md`. All three already carried
substantial uncommitted edits from another lane (the referee-response
revision: `git diff --stat` showed `+167/−…` on the draft and `+27` on
`SOURCES.md` before this pass began, and `CHANGES.md` was untracked). My
edits sit on top of those; committing the files would sweep that other
lane's work into a commit under this task's name. Committing the draft
revision as a whole is the manager's/operator's call. `git diff` on those
three files shows both sets of hunks; the hunks from this pass are the ones
described in this report.

## Caps and limits declared

* No search program was run. The candidate-count recomputation is arithmetic
  over the case split, not a re-enumeration.
* I did not verify the *contents* of the 31 tracked files beyond what is
  quoted here (the `n=38` witness line, the `n=41,k=6` witness line, the two
  `NONE` lines with their `tested=` totals, the 100.0% progress lines, and
  the zero-byte sizes). Whether `gpu_pancyc.py`'s kernel is *correct* is
  exactly the open question the corrected Section 3.4 now states; it is
  outside this task.
* `git check-ignore` and `git ls-files` were the two independent methods used
  for "tracked / not tracked"; both agree before and after.

## Outstanding (not this task's scope, routed to the manager)

The step that would let Section 3.4 say "independently replicated" for
`h(41)>5` is finishing an independently written exhaustive run:
`papers/construction/indep_gpu.py` from its corrected checkpoint (mode A
remainder plus modes B and C), or a CPU direct-DFS enumeration. Under the
standing 20% compute cap that is a long, single-process job, not a fleet.

## Commit

The changes listed under "What was committed" are commit `e59dd10` on
`master` ("Record integrity: track cited evidence files, quarantine vacuous
hn_k5.csv rows"), 36 files. `git ls-files` at that commit returns all 31
evidence paths plus `search/k6/gpu_pancyc128.py`, `search/hn_k5.csv`,
`search/hn_k5-README.md`, `.gitignore` and this report.
