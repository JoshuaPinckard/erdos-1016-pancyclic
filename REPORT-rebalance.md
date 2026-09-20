# Rebalancing the n=68,69,70 exhaustion chains across the two GPUs

2026-09-19. Worker 22. Both chains are cut over and running. Every number here
is measured on the two machines.

The split was cut three times today. Each re-cut was forced by a measurement
that invalidated the model the previous one rested on, and each is recorded
below rather than quietly replaced, because the sequence is the finding.

---

## 1. Costliest finding: cost per rank is not constant, so a single ranks/hour per machine is the wrong unit of account

Every split proposed today — the original brief's, mine, and the manager's —
priced work in **ranks** and gave each machine **one rate**. That model is
wrong, and it is wrong by enough to have chosen the wrong split three times.

Measured on the laptop from the whole chain log, over full 5e10-rank units only
(so unit size cannot confound it), median GPU seconds per unit:

| tier | units sampled | median gpu_s | mean | p90 |
|---|---|---|---|---|
| n70 b10 | 1069 | 42.05 | 41.96 | 44.83 |
| n70 b11 | 2253 | 48.00 | 51.90 | 65.69 |
| n69 b11 | 13 | 60.98 | 63.52 | 64.13 |
| n69 b12 | 11 | 77.75 | 80.07 | 77.92 |

**One effect is real. A second one I reported is not, and is retracted here.**

* **Tier — real.** A b=12 rank costs about **1.27×** a b=11 rank. A b=12 shape
  carries one more chord and the kernel does more per candidate. Confirmed
  *within a single level* on both cards, which is what makes it a property of
  the kernel rather than of a machine: at n=69, desktop 57.38 / 43.43 = 1.32,
  laptop 77.81 / 60.98 = 1.28.

* **Level — RETRACTED.** I first reported that `n69 b11` costs 27% more per rank
  than `n70 b11`. That is **confounded by clock history**, not a level effect.
  `n70 b11`'s 2253 units span 2026-09-17..19, including time before the fan pin
  and thermal guard settled the laptop at 1395 MHz, so its 48.00 median reflects
  a faster card rather than a cheaper tier. Measured inside one regime the level
  effect is negligible: `n68 b11` 61.88 against `n69 b11` 60.98, **1.5% apart**.
  The same pooling inflated the apparent b=12 multiplier to 1.37;
  `rebalance/tier-cost.sh` now reports only within-level ratios and labels
  cross-level comparison as confounded.

Medians, not means: thermal-guard freezes put a long right tail on whichever
tier was running when the card got hot (n70 b11 mean 51.90 against median
48.00), and a mean would price that as tier cost.

**Consequence.** The manager's split gave the laptop both remaining b=12 tiers,
concentrating the most expensive work on the slowest card. At the corrected
multiplier (1.28) that is **392.9 h against 358.6 h** for what is deployed — the
manager's split costs 34.3 h rather than saving 13.5 h, because the 13.5 h
figure was computed with the single-rate model. My own earlier "swap" was
375.5 h; the original brief's instruction 403.5 h; changing nothing 405.0 h.

The retraction does not reverse any of that — the tier effect alone is what
sinks both-b=12-on-the-slow-card — but it narrows the uncertainty the split had
to tolerate, so the split was re-checked against the narrower range rather than
assumed still valid (§2).

---

## 2. What is deployed, and why it is not the nominal optimum

The b=12 multiplier is **not pinned down**: within-level ratios give 1.32
(desktop, n=69) and 1.28 (laptop, n=69), and both rest on small samples.
Choosing the split that wins at any single value would be tuning to the number
we are least sure of.

So all 64 whole-job assignments were ranked at b12 ∈ {1.24, 1.26, 1.28, 1.30,
1.32} — the range left after the clock-regime confound was removed — and scored
by worst-case regret against the best split at each point:

| laptop takes | worst-case regret (h) |
|---|---|
| 68/12, 69/11, 70/11 | 2.7 |
| **68/11, 70/11, 70/12** (deployed) | **3.2** |
| 68/11, 68/12, 69/11 | 9.1 |
| 68/12, 70/12 | 10.1 |
| 68/12, 69/12 | 12.4 |

The top two are 0.5 h apart, which is inside the measurement noise; switching to
the nominal leader would cost four state migrations to buy a difference that
cannot be resolved. The deployed row stays.

(Over the wider range used before the confound was found — {1.25 … 1.43} — the
deployed row led outright at 2.3 h against 11.0 h. Narrowing the range moved the
two leaders together; it did not promote anything from further down.)

The deployed assignment is the first row — chosen for being insensitive to the
uncertain input, not for winning anywhere in particular.

* **DESKTOP** (`run-chain-desktop-v6.cmd`): 69/11, 68/12, 69/12
* **LAPTOP** (`run-chain-laptop-v5.sh`): 68/11, 70/11, 70/12

Expensive b=12 work on the faster card; the cheap b=11 remainders on the slower
one. It lands within 1.2–4.7 h of the fractional optimum at every multiplier in
the range.

### Finish dates

At the corrected central estimate b12 = 1.28 (regenerate with
`rebalance/forecast.py`; saved at `rebalance/forecast-final-20260919.txt`):

| plan | desktop h | laptop h | makespan h | finish (UTC) |
|---|---|---|---|---|
| baseline (change nothing) | 405.0 | 288.1 | 405.0 | 2026-10-06 17:08 |
| manager's split (69/12+70/12 → laptop) | 324.0 | 392.9 | 392.9 | 2026-10-06 05:00 |
| my earlier swap (v4/v3) | 377.2 | 324.7 | 377.2 | 2026-10-05 12:54 |
| **deployed** | **350.5** | **358.6** | **358.6** | **2026-10-04 18:42** |
| fractional optimum | — | — | 354.0 | 2026-10-04 14:09 |

**Saving against baseline: 46.4 h (1.93 days).** Against the manager's split,
34.3 h. Against my earlier swap, 18.6 h. Idle tail 8.1 h, down from 116.9 h.

Sensitivity of the deployed plan: 358.6 h at 1.28, 372.0 h at 1.36, 383.5 h at
1.43 — within 4.7 h of the optimum at every point tested.

`alt_68_11` in `forecast.py` prints identically to `deployed`: they are the same
assignment. It was recorded this morning as "the alternative I did not take"
under the single-rate model, and the cost-weighted enumeration arrived at it
independently. Kept as a named plan so the coincidence is visible rather than
looking like a duplicate row.

### Remaining work

```
tier        shapes   units    done    left    ranks left   mean unit
n68 b11        1257    6156    1923    4233    1.9829e+14   4.556e+10
n68 b12         298    6871       2    6869    3.3786e+14   4.919e+10
n69 b11        1234    6695      26    6669    3.2296e+14   4.843e+10
n69 b12         296    8140      15    8125    4.0122e+14   4.938e+10
n70 b10        1971    3040    3040       0    0.0000e+00   3.422e+10
n70 b11        1138    7265    2725    4540    2.2043e+14   4.856e+10
n70 b12         281    9263       0    9263    4.5732e+14   4.937e+10
```

All tiers b≤10 at all three levels are complete. **No hits anywhere**: every
state file reports `"hits": 0`.

---

## 3. The other thing that was silently wrong: laptop results had no second copy

`n=70 b=10` was finished on the laptop — 3040 of 3040 units, 1.04e14 ranks — and
**no copy had ever reached this repository.** Before today the repo held only
`gpu-state-n70-b9.json`. A laptop disk failure would have destroyed ~2.4e14
ranks of finished work with nothing on this side able to detect it: the
desktop's own `verify_tier_exhaustion.py` would have reported the tier as never
started.

Now present and verified against this machine's own manifest:

```
[sync] n=70 b=10 installed 3040 units; verifying against this repo's manifest
          "expected_unit_count": 3040,
          "covered_unit_count": 3040,
          "extra_unit_count": 0,
          "rank_totals_match": true,
          "exact_match": true,
```

An hourly scheduled pull keeps it so.

---

## 4. Machine rates and why units/h is not a currency

| | desktop | laptop |
|---|---|---|
| GPU | RTX 5060 Ti | RTX 4070 Laptop |
| clock / power | 2092 MHz, 73 W | 1395 MHz, 39 W (thermal guard) |
| measured on b=11 | **3.6177e12 ranks/h** | **2.7973e12 ranks/h** |
| window | 22.15 h, `gpu-state-n68-b11.json` from empty | 11.61 h, `chain-laptop.log` |

Rates are quoted in **b=11-equivalent ranks/hour**, because both long-window
measurements were taken on b=11 tiers. `forecast.py` converts other tiers with
the measured multiplier.

units/h is not comparable at all. A unit is `min(UNIT, ranks left in the shape)`,
so mean unit size runs 3.42e10 (n70 b10) to 4.94e10 (n69 b12) — a 44% spread —
*and* a rank is itself not constant work. The machines look 1.47× apart in
units/h and are 1.29× apart in b=11 ranks/h. Neither number transfers across
tiers.

---

## 5. Cutover and resumption evidence

No running script was ever edited. `run-chain-desktop-v2..v5.cmd` and
`run-chain-laptop-v1..v4.sh` are untouched on disk; cmd.exe and bash both read a
script incrementally by byte offset.

**Three state migrations**, all verified against the *receiving* machine's
manifest, all resuming rather than restarting:

| tier | direction | source count | after probe | verify |
|---|---|---|---|---|
| 70/11 | laptop → desktop | 2722 | **2723** | `extra_unit_count: 0` |
| 69/11 | laptop → desktop | 16 | **17** | `extra_unit_count: 0` |
| 69/12 | laptop → desktop | 14 | **15** | `extra_unit_count: 0` |
| 68/11 | desktop → laptop | 1923 | 1928 (live) | `extra_unit_count: 0` on laptop |
| 70/11 | desktop → laptop | 2725 | queued | `extra_unit_count: 0` on laptop |

Each migrated partial was probed with `--wall-budget 1`, which runs exactly one
unit (the budget check is guarded by `tested`, so the first iteration always
runs). Every probe advanced the count by one **from the source machine's
number, not from zero**. The unit was real work, so nothing was wasted. This is
the check the manager asked for; a silent restart-from-zero on a migrated
partial is the one failure that would look like success.

Both chains confirmed live afterwards: desktop `run-chain-desktop-v6.cmd`
pid 744 → `gpu-state-n69-b11.json` pid 27120, advancing 17 → 22; laptop
`run-chain-laptop-v5.sh` → `n68-state-b11.json` pid 647019, advancing
1923 → 1928.

**Constraints held.** The thermal guard was never touched — only
`erdos-laptop-chain` was stopped and started, `erdos-thermal-guard` reported
`active` throughout, and the `Requires=`/`After=` drop-in survived every unit
rewrite. Card at 70 °C / 1395 MHz, unchanged. Desktop chain CPU measured at
0.067% of the machine against a 5% ceiling, runner at `Idle` priority. No edit
to `gpu_search.py`, `gpu_state_runner.py`, `verify_tier_exhaustion.py`, or any
`gpu-blast/n*.jsonl`; `n68.jsonl` and `n69.jsonl` were **copied** to the laptop
and all three manifests are byte-identical on both machines
(`b57e9d74…`, `bceb4eee…`, `a7c01425…`).

---

## 6. Sync mechanism, both directions

**Copying the state file is the whole migration.** `gpu_state_runner.py`
regenerates the unit plan from the hashed manifest and binds `source_sha256`
into the state, so a state file means the same thing on either machine provided
the manifest bytes match. Nothing is merged or replayed. `extra_unit_count` is
the check that the two sides never disagreed about the plan; it is 0 on every
transfer above.

* `rebalance/sync-from-laptop.ps1` — hourly, hidden, scheduled task
  `Erdos1016-sync-from-laptop` (`Last Result: 0`). Allowlist now
  `70:10, 68:11, 70:11, 70:12`.
* `rebalance/sync-to-laptop.ps1` — one-shot migration tool, deliberately **not**
  scheduled: a scheduled push would race the hourly pull.

The ssh destination is a required parameter in both, supplied by the scheduled
task registration, so the machine name is configuration rather than repository
content.

### Guards and their mutation checks

*Pull, "local is ahead"* — GREEN/RED/GREEN against a scratch copy in
`rebalance/mutation-check/`, production untouched:

```
GREEN  incoming 2722  local 2723 -> REFUSED: local copy is ahead; scratch after 2723
RED    guard disabled -> installed 2722 units; scratch after 2722   (unit 2723 destroyed)
GREEN  restored       -> REFUSED: local copy is ahead; scratch after 2723
```

*Push* — three cases, using `rebalance/guard-fixture.sh` to stage each:

```
laptop AHEAD       -> REFUSED: the laptop copy is ahead (1924 > 1923); leaving it alone
laptop UNREADABLE  -> REFUSED: could not read the laptop's copy (answer 'PROBE_FAILED').
                      Not overwriting something I cannot see.
normal             -> unchanged (1923 units); nothing to do
```

---

## 7. Two defects found in my own work, both fixed

**A guard that silently did not fire.** The push tool's first version folded
"the remote file is absent" and "I could not read the remote file" into the same
`-1`. The probe was in fact failing on quoting, so it reported `-1` for a file
that held 2722 units and the ahead-guard was skipped entirely. The push happened
to be correct (2725 > 2722), but the guard was not what made it correct. The
remote now names its own state (`ABSENT` / a count / `PROBE_FAILED`) and anything
unrecognised refuses. This is the defect the RED case above now covers.

**A version pointer left behind.** When cutting to v6 I patched the wrapper's
comment but not its `BuildPath` line, so the scheduled task relaunched the
desktop on **v5** — which still listed 68/11 and 70/11, both of which had just
migrated to the laptop. Both machines would have run the same two tiers against
separate state files, duplicating thousands of units with no lock to stop them
(the lock is per state file, and the paths differ by machine). Caught by reading
the file back instead of trusting the patch; the desktop was stopped ~50 s after
launch, before the runner completed a single unit, and all counts were confirmed
unchanged. The wrapper is now verified by reading `BuildPath` after every change.

**A silent skip, found earlier the same day.** `$ErrorActionPreference = 'Stop'`
turned scp's stderr for a not-yet-started tier into a terminating error: no
`SKIPPED` line, no `[sync] done`, and every later tier silently never pulled.
A missing remote tier now names itself and the loop continues.

---

## 8. What I could not determine

*Per-(level, tier) costs.* I have medians for four of the nine cells, and the
n=69 cells rest on 11–13 units taken from the head of their tiers, where shape
ordering may not be representative. A full cost table would let the split be
chosen exactly rather than by worst-case regret. It costs nothing to collect:
`rebalance/tier-cost.sh` reads it out of the chain log, and both machines are
now generating b=11 and b=12 data continuously. **Re-run it in a day and
re-check the split.** This is "could not look yet", not "not there".

*Desktop throughput before 2026-09-19 13:06.* The desktop chain's stdout went
nowhere until today, so the 3.6177e12 ranks/h figure is a 22.15 h average with
no visibility inside the window. **Fixed going forward** (§10): the desktop now
writes `chain-desktop.log` with per-unit `gpu_seconds`, the same record the
laptop has always had. The historical gap cannot be recovered.

*Whether the b=12 multiplier is stable within a tier.* Assumed constant. If it
drifts with shape index the split should be re-checked; the deployed choice was
made to be tolerant of exactly this, which is why it is the recommendation
rather than the nominal optimum.

---

## 9. Desktop per-unit logging, and a contention problem it immediately exposed

The desktop now writes `search/shapecsp/chain-desktop.log` — the per-unit
`gpu_seconds` record the laptop has always had, and what Worker 21 needs to
prove a 1.6–1.9× kernel claim honestly.

The redirect lives in `run-chain-desktop-logged.cmd`, not in the wrapper's
command string and not in a new chain version. `WshShell.Run` does not hand its
argument to a shell: it CreateProcess-es cmd.exe and passes the rest through, and
cmd strips the outer quote pair only under a narrow rule that a command with two
quoted paths does not satisfy. Measured: `cmd.exe /c "A" "B"` through
`WshShell.Run` returns **1 and does nothing**, while the byte-identical text
typed at a prompt works. The wrapper now uses `cmd.exe /s /c ""A" "B""`, which
makes the strip unconditional, and every redirection operator stays inside the
launcher where cmd parses normally. Verified rc=0 with a no-op chain before
going near production. Putting the redirect in the wrapper rather than in a v7
also means future chain versions inherit logging with no further edit.

Rotation: the wrapper rolls the log to one `.1` generation above 64 MiB, giving
a 128 MiB ceiling. At the measured ~85 units/h and ~120 bytes per line a 13-day
run produces only a few MiB, so the cap is a backstop against a pathological
retry loop, not an expected event. A rotation failure is swallowed deliberately —
losing timing data is far cheaper than losing a day of GPU work.

**The contention problem.** Worker 21 benchmarks the bounded kernel on *this*
GPU, and the production chain runs on it too. The first lines of the new log show
what that costs: an `n69 b11` unit that takes ~43 gpu_s on an idle card took
**74.29 gpu_s** while a `gpu_state_runner_bounded.py` benchmark was running
alongside it.

Both measurements are contaminated whenever they overlap — Worker 21's A/B
timing and my per-tier costs alike. A 1.6–1.9× claim cannot be settled on a
shared card. I waited out their 240 s run before launching rather than corrupt
it, but that is a manual courtesy, not a mechanism, and it does not survive the
next 13 days. This needs an arbiter: either the chain yields the GPU on demand,
or benchmark runs get an exclusive window. Flagging rather than adopting it —
it is Worker 21's measurement and the manager's call how to serialise them.

---

## 10. Files

New under `search/shapecsp/rebalance/`: `census.py`, `forecast.py`,
`tier-cost.sh`, `sync-from-laptop.ps1`, `sync-to-laptop.ps1`,
`run-sync-hidden.vbs`, `guard-fixture.sh`, `sample-laptop.sh`, `rate-laptop.sh`,
`laptop-stop.sh`, `laptop-cutover.sh`, `fix-unit-description.sh`, plus the
sampled JSON, `enumeration-20260919.txt`,
`enumeration-costweighted-20260919.txt` and `forecast-final-20260919.txt`.

Chain scripts: `search/shapecsp/run-chain-desktop-v4.cmd`, `-v5.cmd`, `-v6.cmd`
and `deploy/laptop/run-chain-laptop-v3.sh`, `-v4.sh`, `-v5.sh`. v6 and v5 are
live; the rest are superseded and kept because a live chain may have been
executing them.

Modified: `search/shapecsp/run-chain-desktop-hidden.vbs` — launches v6, derives
the chain path from its own location rather than an absolute string, and exits 3
rather than 0 if the chain file is missing.

State now in the repo: `gpu-state-n70-b10.json` (complete, `exact_match: true`),
`gpu-state-n70-b11.json`, `gpu-state-n69-b11.json`, `gpu-state-n69-b12.json`,
`gpu-state-n68-b11.json`, `gpu-state-n68-b12.json`.

Left in place: `gpu-state-n70-b11.json.incoming.rejected` from the pull mutation
check (bounded at one file per tier, reused in place), and stale
`n69-state-b11.json` / `n69-state-b12.json` on the laptop for tiers the desktop
now owns — harmless, nothing there runs them, and both are excluded from the
pull allowlist.
