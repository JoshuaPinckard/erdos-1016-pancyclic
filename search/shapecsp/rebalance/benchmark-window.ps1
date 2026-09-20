<#
.SYNOPSIS
  Take the desktop GPU exclusively for a bounded window, run one command, then
  put the production chain back and prove from disk that it resumed.

.DESCRIPTION
  Decided by the Manager 2026-09-19: benchmarks get an exclusive window and the
  chain does not yield. Worker 21 cannot measure a 1.6-1.9x kernel claim against
  a contended card -- an n69 b11 unit that takes ~43 gpu_s idle was measured at
  74.29, 91.38 and 97.44 gpu_s while a bounded-kernel benchmark ran alongside
  it. This tool is the only sanctioned way to stop the chain.

  It is also the stop/relaunch path for the pairwise cutover: pass the migration
  work as -Command and the same guarantees apply.

  WHAT MAKES THE RELAUNCH SAFE
  The chain's scheduled task repeats every 5 minutes with
  MultipleInstancesPolicy IgnoreNew. This tool therefore NEVER disables it.
  Suppression is a marker file that run-chain-desktop-hidden.vbs honours and
  that EXPIRES on its own:

    * normal path      - the marker is removed and the chain is started at once;
    * script throws    - finally{} removes the marker and starts the chain;
    * script is KILLED - nothing runs, but the marker expires at cap minutes and
                         the next 5-minute trigger starts the chain by itself.

  That last path is the one that matters. The 2026-09-19 12:59 outage happened
  because a chain was run in a tool's foreground and died with it, leaving
  nothing to restart it. Here the worst case is bounded by cap + 5 minutes of
  idle, with no reboot hole, because the task is never disabled.

.PARAMETER Command
  The benchmark to run. Executed DETACHED (its own process, not this script's
  foreground) and hard-capped.

.PARAMETER CapMinutes
  Hard cap on the benchmark, default 10. Also the marker's expiry.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Command,
    [int]$CapMinutes = 10,
    [string]$TaskName = 'Erdos1016-desktop-chain',
    [string]$ShapeDir,
    [switch]$SkipRelaunchForMutationCheck
)

$ErrorActionPreference = 'Stop'
if (-not $ShapeDir) { $ShapeDir = Split-Path -Parent $PSScriptRoot }
$marker = Join-Path $PSScriptRoot 'benchmark-window.active'

function Say { param([string]$m) Write-Output ("[window] " + $m) }

function Get-ChainRunner {
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
        Where-Object { $_.CommandLine -like '*gpu_state_runner.py*' -and $_.CommandLine -like '*gpu-state-n*' } |
        Select-Object -First 1
}

function Get-StateUnits {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return -1 }
    try { return (Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json).complete.Count }
    catch { return -1 }
}

# ---------------------------------------------------------------- health gate
# Refuse on an unhealthy chain. Stopping something already broken and then
# "restoring" it would report success while leaving the GPU idle, which is
# exactly the shape of failure this tool exists to prevent.
Say "health check"
$runner = Get-ChainRunner
if (-not $runner) { Say "REFUSED: no chain runner is alive. Nothing to take the GPU from; fix the chain first."; exit 2 }

if ($runner.CommandLine -notmatch 'gpu-state-n(\d+)-b(\d+)\.json') {
    Say "REFUSED: cannot identify the tier from the runner command line."; exit 2
}
$n = $Matches[1]; $b = $Matches[2]
$statePath = Join-Path $ShapeDir "gpu-state-n$n-b$b.json"
$lockPath = "$statePath.lock"

$before = Get-StateUnits $statePath
if ($before -lt 0) { Say "REFUSED: cannot read $statePath."; exit 2 }
if (-not (Test-Path $lockPath)) { Say "REFUSED: runner alive but its lock $lockPath is missing."; exit 2 }
$lockAge = ((Get-Date) - (Get-Item $lockPath).LastWriteTime).TotalSeconds
if ($lockAge -gt 60) { Say ("REFUSED: lock is {0:N0}s stale; the runner is not heartbeating." -f $lockAge); exit 2 }
if (Test-Path $marker) { Say "REFUSED: a benchmark window is already active ($marker)."; exit 2 }

Say ("healthy: n=$n b=$b, pid $($runner.ProcessId), complete_units=$before, lock age {0:N0}s" -f $lockAge)

$exitCode = 0
try {
    # ------------------------------------------------------------ suppress
    # Marker FIRST, so that if the chain is ended and this script dies a
    # microsecond later, the 5-minute trigger still does not race us back in.
    "$CapMinutes`nstarted=$((Get-Date).ToString('o'))`ncommand=$Command" |
        Set-Content -LiteralPath $marker -Encoding ASCII
    Say "marker written, cap ${CapMinutes}m (wrapper will decline to start the chain until it expires)"

    Say "ending the chain task instance"
    & schtasks /end /tn $TaskName 2>&1 | ForEach-Object { Say "  schtasks: $_" }

    # Confirm the runner really exited AND released its lock. "I asked it to
    # stop" is not the same as "it stopped"; a benchmark started against a
    # still-running chain measures contention, which is the whole problem.
    # ORDER MATTERS (2026-09-19 17:10 incident): the chain scripts (wscript ->
    # cmd -> cmd) must be stopped BEFORE the runner.  schtasks /end only ends
    # the top process, and stopping the runner while cmd.exe is still alive
    # makes cmd see a finished job and launch the NEXT tier, which then runs as
    # an orphan on the GPU right through the benchmark.
    Get-CimInstance Win32_Process -Filter "Name='cmd.exe' OR Name='wscript.exe'" |
        Where-Object { $_.CommandLine -like '*run-chain-desktop*' } |
        ForEach-Object { Say "  stopping chain process $($_.ProcessId) $($_.Name)"; Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2
    $still = Get-ChainRunner
    if ($still) {
        Say "stopping runner $($still.ProcessId) (the unit in flight is lost; the state file is atomic)"
        Stop-Process -Id $still.ProcessId -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
    }
    $deadline = (Get-Date).AddSeconds(30)
    while ((Get-Date) -lt $deadline -and (Get-ChainRunner)) { Start-Sleep -Seconds 2 }
    if (Get-ChainRunner) { throw "a chain runner is still alive after the stop sequence" }

    if (Test-Path $lockPath) {
        # The runner unlinks its lock in a finally:, but SIGKILL-equivalent
        # termination skips that. Report it rather than deleting someone else's
        # lock: the runner's own --lock-stale path clears it after 180s.
        Say "NOTE: $lockPath still present; runner was force-stopped. The chain's own stale-lock path clears it after 180s, so the relaunch may log one LOCKED retry."
    }
    Say "GPU released; runner gone"

    # ------------------------------------------------------------- benchmark
    Say "running benchmark detached, hard cap ${CapMinutes}m"
    Say "  $Command"
    $started = Get-Date
    $proc = Start-Process -FilePath 'powershell.exe' `
        -ArgumentList '-NoProfile', '-NonInteractive', '-WindowStyle', 'Hidden', '-Command', $Command `
        -PassThru -WindowStyle Hidden
    if (-not $proc.WaitForExit($CapMinutes * 60 * 1000)) {
        Say "CAP HIT at ${CapMinutes}m; terminating the benchmark process tree"
        & taskkill /PID $proc.Id /T /F 2>&1 | ForEach-Object { Say "  taskkill: $_" }
        $exitCode = 3
    } else {
        Say ("benchmark exited {0} after {1:N0}s" -f $proc.ExitCode, ((Get-Date) - $started).TotalSeconds)
        if ($proc.ExitCode -ne 0) { $exitCode = 4 }
    }
}
catch {
    Say "ERROR: $($_.Exception.Message)"
    $exitCode = 5
}
finally {
    # --------------------------------------------------------- always relaunch
    if ($SkipRelaunchForMutationCheck) {
        Say "MUTATION CHECK: deliberately skipping marker removal and relaunch"
    } else {
        Remove-Item -LiteralPath $marker -Force -ErrorAction SilentlyContinue
        Say "marker cleared"
        & schtasks /run /tn $TaskName 2>&1 | ForEach-Object { Say "  schtasks: $_" }

        # Verify FROM DISK, not from the fact that we asked. Allow for the
        # chain's LOCKED retry (it waits out the 180s stale window), so give it
        # longer than a single unit takes.
        $ok = $false
        $deadline = (Get-Date).AddSeconds(300)
        while ((Get-Date) -lt $deadline) {
            $after = Get-StateUnits $statePath
            $live = Get-ChainRunner
            if ($live -and $after -ge $before) { $ok = $true; break }
            Start-Sleep -Seconds 10
        }
        $after = Get-StateUnits $statePath
        if ($ok) {
            Say ("RESUMED: n=$n b=$b complete_units $before -> $after (>= recorded), runner pid $((Get-ChainRunner).ProcessId)")
        } else {
            Say ("NOT VERIFIED: complete_units $before -> $after, runner " + $(if (Get-ChainRunner) { 'alive' } else { 'ABSENT' }))
            Say "The marker is cleared, so the 5-minute task trigger will keep retrying on its own."
            $exitCode = 6
        }
    }
}

Say "done rc=$exitCode"
exit $exitCode
