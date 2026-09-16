<#
.SYNOPSIS
  Suspend or resume the Erdos1016 GPU worker for the release-cut quiet window.

.DESCRIPTION
  The release-cut Controller runs a strict test suite that launches Electron and
  needs a contention-free GPU measurement, so during its window this job must
  release the GPU rather than merely yield it.

  It SUSPENDS the worker in place (NtSuspendProcess) and deliberately does not
  kill it. Both chain drivers treat any non-zero, non-2 runner exit as "tier
  attempted" and advance, so killing the worker mid-tier would silently abandon
  the rest of that tier -- about 32 GPU-hours at these sizes.

  Watchdog is a dead-man's switch: the supervisor is told SUSPENDED is
  authorised, so a session that dies mid-window would otherwise stall the run
  silently for days.

.NOTES
  The suspend record is BOUND to a specific process (pid + process start time).
  An unbound "something was suspended at T" record is unsafe in both
  directions: it let the watchdog resume a legitimately-suspended worker on a
  stale timestamp, and let it refuse to resume an abandoned one. Start time is
  carried because a pid alone can be recycled.

  State lives OUTSIDE the git worktree on purpose: as an untracked file inside
  it, git clean -xfd erased the watchdog's memory.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Suspend', 'Resume', 'Status', 'Watchdog')]
    [string]$Action,
    [double]$MaxSuspendHours = 6.0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not ('Erdos.ProcCtl' -as [type])) {
    Add-Type -Namespace Erdos -Name ProcCtl -MemberDefinition @'
[DllImport("ntdll.dll", SetLastError = true)] public static extern uint NtSuspendProcess(IntPtr h);
[DllImport("ntdll.dll", SetLastError = true)] public static extern uint NtResumeProcess(IntPtr h);
'@
}

$StateDir  = Join-Path $env:LOCALAPPDATA 'Erdos1016'
$StateFile = Join-Path $StateDir 'quiet-window.state'
$LogFile   = Join-Path $StateDir 'quiet-window.log'
if (-not (Test-Path -LiteralPath $StateDir)) { New-Item -ItemType Directory -Path $StateDir -Force | Out-Null }

function Write-Line([string]$Text) {
    # The watchdog runs under hidden wscript, which discards stdout entirely, so
    # every outcome is logged. Previously only WATCHDOG-RESUME left any trace:
    # "leaving alone" and "no worker" vanished without record.
    Write-Output $Text
    try {
        "{0}`t{1}" -f (Get-Date).ToUniversalTime().ToString('o'), $Text | Add-Content -LiteralPath $LogFile -Encoding UTF8
    } catch { }
}

function Write-State([string]$What, $Proc) {
    $pidv = 0
    $startv = ''
    if ($Proc) { $pidv = $Proc.Id; $startv = $Proc.StartTime.ToUniversalTime().ToString('o') }
    "{0}`t{1}`t{2}`t{3}`t{4}" -f (Get-Date).ToUniversalTime().ToString('o'), $What, $env:COMPUTERNAME, $pidv, $startv | Add-Content -LiteralPath $StateFile -Encoding UTF8
}

function Get-SuspendRecord {
    # Returns $null unless the last record is a SUSPEND carrying a parseable
    # timestamp, pid and process start time. Every other shape fails safe.
    if (-not (Test-Path -LiteralPath $StateFile)) { return $null }
    $lines = @(Get-Content -LiteralPath $StateFile -ErrorAction SilentlyContinue | Where-Object { $_ -match '\S' })
    if ($lines.Count -eq 0) { return $null }
    $parts = ($lines | Select-Object -Last 1) -split "`t"
    if ($parts.Count -lt 5 -or $parts[1] -ne 'SUSPEND') { return $null }
    try {
        $when  = [datetime]::Parse($parts[0], $null, [Globalization.DateTimeStyles]::RoundtripKind)
        $start = [datetime]::Parse($parts[4], $null, [Globalization.DateTimeStyles]::RoundtripKind)
        return [pscustomobject]@{ When = $when; WPid = [int]$parts[3]; Start = $start }
    } catch { return $null }
}

function Get-GpuUtil {
    # Returns $null when the card could not be measured, NEVER a sentinel
    # number. The drain guard was `-le 5` against a -1 sentinel, and -1 -le 5 is
    # true, so an unmeasurable card read as "quiet" and the command announced
    # the GPU released on a reading that never happened.
    $out = Join-Path $env:TEMP ('erdos-gpu-' + [guid]::NewGuid().ToString('N') + '.txt')
    try {
        $p = Start-Process -FilePath 'nvidia-smi' -ArgumentList '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits' -NoNewWindow -PassThru -RedirectStandardOutput $out -ErrorAction Stop
        if (-not $p.WaitForExit(8000)) { try { $p.Kill() } catch { }; return $null }
        # Settle the object: with -PassThru and the timed WaitForExit(ms)
        # overload, ExitCode comes back EMPTY, so a naive `-ne 0` test rejects
        # every successful reading. That made the drain wait warn on all 90s of
        # a perfectly measurable card.
        try { $p.WaitForExit() } catch { }
        $code = $null
        try { $code = $p.ExitCode } catch { }
        if ($null -ne $code -and $code -ne 0) { return $null }
        # Require a bare integer. An error message can contain digits, so
        # "matches \d" is not evidence of a measurement.
        $v = @(Get-Content -LiteralPath $out -ErrorAction SilentlyContinue | Where-Object { $_ -match '^\s*\d+\s*$' })
        if ($v.Count -eq 0) { return $null }
        return [int]($v[0].Trim())
    } catch { return $null }
    finally { Remove-Item -LiteralPath $out -ErrorAction SilentlyContinue }
}

function Get-Workers {
    # Win32_Process.CommandLine is unreadable for processes started in another
    # context, so a scheduler-launched caller cannot inspect a shell-launched
    # worker. Treating unreadable as "no worker" made an uninspectable worker
    # indistinguishable from none -- silently inert exactly when someone has
    # intervened by hand. Report that case instead of hiding it.
    $py = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue)
    $match  = @($py | Where-Object { $_.CommandLine -and $_.CommandLine -match 'gpu_state_runner\.py' })
    $opaque = @($py | Where-Object { -not $_.CommandLine })
    return [pscustomobject]@{ Matched = $match; Opaque = $opaque.Count; TotalPython = $py.Count }
}

function Test-FullySuspended($Proc) {
    $threads = @($Proc.Threads)
    if ($threads.Count -eq 0) { return $false }
    $awake = @($threads | Where-Object { $_.ThreadState -ne 'Wait' -or $_.WaitReason -ne 'Suspended' })
    return ($awake.Count -eq 0)
}

$scan = Get-Workers
$workers = @($scan.Matched)
if ($workers.Count -eq 0) {
    if ($scan.Opaque -gt 0) {
        Write-Line "CANNOT INSPECT: $($scan.Opaque) of $($scan.TotalPython) python processes have unreadable CommandLine from this context; a worker may exist and be invisible here"
        exit 3
    }
    Write-Line 'no gpu_state_runner worker running'
    if ($Action -eq 'Status') { exit 0 }
    exit 1
}

foreach ($w in $workers) {
    $proc = Get-Process -Id $w.ProcessId -ErrorAction Stop
    switch ($Action) {
        'Suspend' {
            $rc = [Erdos.ProcCtl]::NtSuspendProcess($proc.Handle)
            if ($rc -ne 0) { throw "NtSuspendProcess failed on pid $($w.ProcessId), status 0x$('{0:X}' -f $rc)" }
            # Record BEFORE announcing success. If recording throws, resume
            # rather than leave a suspended worker with no record -- that is
            # precisely the state the watchdog cannot reason about.
            try { Write-State 'SUSPEND' $proc }
            catch {
                [void][Erdos.ProcCtl]::NtResumeProcess($proc.Handle)
                throw "suspend recorded nothing and was rolled back on pid $($w.ProcessId): $($_.Exception.Message)"
            }
            Write-Line "suspended pid $($w.ProcessId)"
            # Freezing the host process does not stop a kernel already on the
            # card; in-flight work drains first. Measured 5-30s, so a fixed
            # short wait would hand out a card that is still busy.
            $t0 = Get-Date
            $drained = $false
            $unmeasurable = $false
            while (((Get-Date) - $t0).TotalSeconds -lt 90) {
                $u = Get-GpuUtil
                if ($null -eq $u) { $unmeasurable = $true }
                elseif ($u -le 5) { $drained = $true; break }
                Start-Sleep -Milliseconds 400
            }
            $el = ((Get-Date) - $t0).TotalSeconds
            if ($drained) { Write-Line ("gpu released after {0:N1}s" -f $el) }
            elseif ($unmeasurable) { Write-Line ("WARNING gpu utilisation could not be measured after {0:N1}s -- do NOT treat the card as quiet" -f $el) }
            else { Write-Line ("WARNING gpu still busy after {0:N1}s -- do not treat the card as quiet" -f $el) }
        }
        'Resume' {
            $rc = [Erdos.ProcCtl]::NtResumeProcess($proc.Handle)
            if ($rc -ne 0) { throw "NtResumeProcess failed on pid $($w.ProcessId), status 0x$('{0:X}' -f $rc)" }
            Write-State 'RESUME' $proc
            Write-Line "resumed pid $($w.ProcessId)"
            Start-Sleep -Seconds 3
            $u = Get-GpuUtil
            if ($null -eq $u) { Write-Line 'gpu utilisation now UNMEASURABLE' } else { Write-Line "gpu utilisation now $u%" }
        }
        'Watchdog' {
            if (-not (Test-FullySuspended $proc)) { Write-Line "pid $($w.ProcessId) running, nothing to do"; break }
            $rec = Get-SuspendRecord
            if (-not $rec) { Write-Line "pid $($w.ProcessId) SUSPENDED but no usable suspend record; leaving alone"; break }
            # The record must belong to THIS process. An unbound timestamp let
            # the watchdog resume a legitimately-suspended worker.
            if ($rec.WPid -ne $proc.Id) { Write-Line "pid $($w.ProcessId) SUSPENDED but record names pid $($rec.WPid); leaving alone"; break }
            if ([math]::Abs(($rec.Start - $proc.StartTime.ToUniversalTime()).TotalSeconds) -gt 2) {
                Write-Line "pid $($w.ProcessId) SUSPENDED but record start time does not match (likely pid reuse); leaving alone"
                break
            }
            $hours = ((Get-Date).ToUniversalTime() - $rec.When).TotalHours
            if ($hours -lt $MaxSuspendHours) {
                Write-Line ("pid {0} SUSPENDED {1:N2}h, under the {2}h limit; leaving alone" -f $w.ProcessId, $hours, $MaxSuspendHours)
                break
            }
            $rc = [Erdos.ProcCtl]::NtResumeProcess($proc.Handle)
            if ($rc -ne 0) { throw "watchdog NtResumeProcess failed on pid $($w.ProcessId), status 0x$('{0:X}' -f $rc)" }
            Write-State 'WATCHDOG-RESUME' $proc
            Write-Line ("WATCHDOG RESUMED pid {0} after {1:N2}h suspended (limit {2}h)" -f $w.ProcessId, $hours, $MaxSuspendHours)
        }
        'Status' {
            $state = 'RUNNING'
            if (Test-FullySuspended $proc) { $state = 'SUSPENDED' }
            $extra = ''
            if ($state -eq 'SUSPENDED') {
                $rec = Get-SuspendRecord
                if ($rec -and $rec.WPid -eq $proc.Id) { $extra = " since={0:o} ({1:N2}h)" -f $rec.When, ((Get-Date).ToUniversalTime() - $rec.When).TotalHours }
                else { $extra = ' (no matching suspend record)' }
            }
            Write-Line "pid $($w.ProcessId) $state threads=$(@($proc.Threads).Count) priority=$($proc.PriorityClass)$extra"
        }
    }
}
