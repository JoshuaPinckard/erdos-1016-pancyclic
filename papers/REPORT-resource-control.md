# Resource control for the Erdos #1016 workload (Worker 9)

**Fourth revision.** Supersedes the third version (misallocation check only). Adds
mean+max labeling per Manager's finding that a single instantaneous reading and a
window mean can disagree substantially (load is spiky), a third labeled line for
`SearchIndexer.exe`, and a disk-write measurement to say whether this tree's own
writes are driving it.

## Leading finding: the misallocation flagged in the third revision has resolved — GPU rose from idle to 95–100% once Worker 6's new GPU driver started

Across the 12 samples below (16:11:44–16:16:25), `GPU_ELIGIBLE%` (the `fastcyc.exe`
cycle-search lane) was already at 0% for the whole window — Manager's order to kill
the fastcyc fan-out had already landed before this run started. `GPU%` itself stayed
at 0% for samples 1–7, then jumped to 95–100% for samples 8–12, coinciding exactly with
two new `python.exe gpu_joint_sweep.py` processes appearing and being recapped (pid
20432 at sample 8, pid 17340 at sample 9). `MISALLOCATION` was `no` on every sample in
this window: `no` for samples 1–7 because GPU-eligible CPU was already at 0 (nothing to
misallocate), and `no` for samples 8–12 because GPU stopped being idle. **No further
flag to Manager is needed on this point** — GPU is now well above 10%, exactly as
Controller expected once the fan-out kill and new GPU driver landed.

One self-caught instrumentation bug from this transition, fixed before it could matter:
`gpu_joint_sweep.py` contains the literal substring `sweep.py` and would have been
wrongly folded into the CPU-legitimate CSP-lane exemption (Worker 7's
`shapecsp/sweep.py`) by the plain substring match added in the third revision — it is
actually Worker 6's GPU orchestration driver, unrelated to the CSP lane. The pattern is
now word-boundary-anchored (`(?<!\w)sweep\.py`, requires a non-word character before
the match) so `-u sweep.py` still matches but `gpu_joint_sweep.py` does not. This never
flipped a verdict in the data below (GPU was either at 0 with nothing GPU-eligible
running, or at 95–100% and therefore not idle either way), but is recorded here rather
than silently patched, since precision in this classification is exactly what's been
under scrutiny.

## Mean and max, labeled separately, per Manager's spike-vs-mean finding

Manager's instantaneous two-snapshot reading (SEARCH 11.2%, TOOLING 9.5%, SUM 20.7%)
does not match this report's 12-sample mean below, and that gap is itself the expected
signal, not a discrepancy to resolve: tooling load in particular is bursty (a `grep.exe`
process can appear and disappear within seconds), so a single instant and a multi-sample
mean will diverge. Both are reported from here on.

| Metric | Mean (12 samples) | Max (12 samples) |
|---|---|---|
| SEARCH_COMPUTE% | 9.39 | 9.87 |
| AGENT_TOOLING% | 1.79 | 4.08 |
| SUM% | 11.18 | 13.63 |
| SEARCHINDEXER% | 8.84 | 11.51 |
| GPU% | 40.83 | 100 |

`SUM%` stayed within the 20% cap on every sample this window (mean 11.18%, max
13.63%), well below both Manager's 20.7% instantaneous reading and the 28–41% range
measured in the second revision's window. As stated in the second and third revisions,
tooling load is genuinely time-varying on a live multi-agent tree; this window, the
prior over-cap window, and Manager's instantaneous reading are all real, non-contradictory
measurements of a moving target, not disagreeing reports of a fixed one.

## SearchIndexer.exe — third labeled line, not recapped, disk-write attribution

Added a `SEARCHINDEXER%` line (`Win32_Process` `Name='SearchIndexer.exe'`, same
tick-delta CPU method as the other two categories). It belongs in neither the search-compute
nor agent-tooling category and is **never recapped** by this script — it is a Windows
process, out of scope for this task's recap authority, exactly as instructed. Mean
8.84%, max 11.51% (sample 1) across this window — consistently the second- or
third-largest single consumer after the CSP-lane `solve.py` process, matching the scale
of Manager's 10.61% single-sample reading.

**Disk-write attribution, to say whether this tree's own writes are driving it**: this
run measures both machine-wide disk write throughput
(`\PhysicalDisk(_Total)\Disk Write Bytes/sec`) and this tree's own write throughput
(delta of `Win32_Process.WriteTransferCount` summed across all `SEARCH_COMPUTE` and
`AGENT_TOOLING` processes). Across the 12 samples: mean machine-wide write throughput
was **~5.15 MB/s** (507,919–16,948,312 bytes/sec, highly variable); mean throughput
attributable to this tree's own processes was **~44.3 KB/s** (29,733–94,492
bytes/sec) — **roughly 0.8% of the machine-wide total**. This tree's own writes are a
small fraction of total disk write activity by byte volume; SearchIndexer's CPU cost is
not well explained by this project's write throughput on this measure.

**Caveat, stated plainly rather than overclaiming**: this measures byte volume, not
file-change-event count. `SearchIndexer.exe` is typically triggered by change events
(file creates/modifies/renames), not raw bytes written, and this project does produce
many small log/state files (`.txt`, `.csv`, `.json`, `.log` — visible throughout
`search/`). A high rate of small-file changes could still be feeding the indexer even
at low byte volume; this measurement can rule out "our writes are the dominant *byte*
load" but cannot rule out "our writes are the dominant *event* load." This is handed to
Manager as a decision (possible fix: excluding the project folder from
Windows Search indexing), not acted on here.

## Manager's ruling on the over-cap finding — confirmed, no code change needed

Manager's ruling (relayed via Controller): never throttle/pin/renice agent tooling, and
never kill long-lived `grep`/`rg` processes on sight (usually an agent reading a large
tree; killing one corrupts that agent's work). This script's recap loop has never
touched anything outside `SEARCH_COMPUTE` processes — confirmed unchanged in this
revision, and the persistent `grep.exe` from the second revision's window is
independently confirmed gone in every sample of this run without this script ever
having acted on it (it was never in the recap loop's scope to begin with).

## Monitor script

`C:\Users\ToolsEnabled-Dev\Desktop\erdos1016\search\resource-monitor.ps1`

Unchanged from the third revision except: added `Get-SearchIndexerProcesses` and its
`SEARCHINDEXER%`/`INDEXER_PROCS` log fields (measured, never recapped); added
`DISK_WRITE_BYTES_PER_SEC` (machine-wide, via `Get-Counter`) and
`OUR_WRITE_BYTES_PER_SEC` (this tree's own processes, via `Win32_Process.WriteTransferCount`
deltas); fixed the `sweep.py` substring-collision described above. All prior
corrections (two-figure CPU breakdown, CSP-lane/GPU-eligible split, misallocation
check, `Get-Counter`-based machine total, tick-delta CPU rates, tooling command lines
never logged) remain in place unchanged.

Prior logs, all preserved and not overwritten: `search/resource-monitor-v1-search-only.log`,
`search/resource-monitor-v2-two-figure.log` (over-cap tooling window),
`search/resource-monitor-v3-precoveragefix.log`, `search/resource-monitor-v4-misallocation.log`.
`search/resource-monitor.log` is this revision's live log.

## Sample series (12 of 15 collected before this report was written)

All timestamps local, 2026-09-14, 20-second interval.

| # | Time | SEARCH_COMPUTE% | AGENT_TOOLING% | SUM% | SEARCHINDEXER% | GPU% | MISALLOCATION | Our write B/s | Machine write B/s |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 16:11:44 | 9.35 | 3.95 | 13.30 | 11.51 | 0 | no | 94,492 | 8,794,878 |
| 2 | 16:12:10 | 9.29 | 1.22 | 10.51 | 8.40 | 0 | no | 34,656 | 12,004,163 |
| 3 | 16:12:36 | 9.52 | 0.97 | 10.49 | 8.88 | 0 | no | 31,475 | 2,843,980 |
| 4 | 16:13:01 | 9.21 | 1.75 | 10.97 | 8.65 | 0 | no | 52,804 | 2,120,927 |
| 5 | 16:13:27 | 9.87 | 1.33 | 11.21 | 8.48 | 0 | no | 35,101 | 1,446,009 |
| 6 | 16:13:52 | 9.61 | 1.27 | 10.88 | 8.44 | 0 | no | 34,946 | 4,574,472 |
| 7 | 16:14:18 | 8.97 | 1.71 | 10.68 | 8.77 | 0 | no | 61,525 | 16,948,312 |
| 8 | 16:14:43 | 9.16 | 1.69 | 10.85 | 8.89 | 95 | no | 39,294 | 9,677,324 |
| 9 | 16:15:09 | 8.92 | 1.21 | 10.13 | 8.10 | 100 | no | 36,274 | 2,202,027 |
| 10 | 16:15:34 | 9.55 | 4.08 | 13.63 | 8.86 | 95 | no | 63,448 | 507,919 |
| 11 | 16:16:00 | 9.73 | 1.01 | 10.74 | 8.30 | 100 | no | 29,733 | 557,549 |
| 12 | 16:16:25 | 9.45 | 1.31 | 10.76 | 8.75 | 100 | no | 30,923 | 1,622,032 |

The raw log, including samples beyond #12 collected as the monitor kept running past
this report, is at `C:\Users\ToolsEnabled-Dev\Desktop\erdos1016\search\resource-monitor.log`.

## Recap actions

`RECAPPED=[]` on 10 of 12 samples. Two new `gpu_joint_sweep.py` processes were caught
and re-pinned as soon as they appeared, confirming the recap design (every matched
process checked every cycle, regardless of measured CPU%) still works correctly for
this newly-launched GPU-driver lane:

- Sample 8 (16:14:43): `pid=20432 cmd="C:\Python313\python.exe gpu_joint_sweep.py sweep 66 2 (0,2)(0,63)(1,13)(3,62)(4,31)(58,63) --all"`
- Sample 9 (16:15:09): `pid=17340 cmd="C:\Python313\python.exe gpu_joint_sweep.py sweep 67 3 (0,2)(0,64)(1,13)(3,63)(4,31)(59,64)"`

Both held their pin (`ProcessorAffinity=1`, `PriorityClass=BelowNormal`) for the
remainder of the window without needing re-correction. As before, no agent-tooling or
`SearchIndexer.exe` process is ever recapped by this script.
