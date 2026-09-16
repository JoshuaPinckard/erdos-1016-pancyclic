<#
.SYNOPSIS
  Suspend or resume the Erdos1016 GPU worker for the release-cut quiet window.

.DESCRIPTION
  The release-cut Controller runs a strict test suite that launches Electron and
  needs a contention-free GPU measurement, so during its window this job must
  release the GPU rather than merely yield it.

  This SUSPENDS the worker in place (NtSuspendProcess). It deliberately does not
  kill it. Both chain drivers treat any non-zero, non-2 runner exit as "tier
  attempted" and advance to the next tier, so killing the worker mid-tier would
  silently abandon the rest of that tier -- about 32 GPU-hours at these sizes.
  A suspended process exits nothing, holds its state file lock, and resumes
  exactly where it stopped, so the cost of a window is its wall-clock length.

  A suspended worker stops refreshing the lock mtime, so its lock looks stale
  after --lock-stale (180s). That is safe only because the scheduled task is
  single-instance: nothing else can start a competing runner and steal it. Do
  not run a second runner by hand against the same state file during a window.

.PARAMETER Action
  Suspend, Resume, or Status.

.EXAMPLE
  .\quiet-window.ps1 -Action Suspend    # on QUIET START
  .\quiet-window.ps1 -Action Resume     # on QUIET END
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Suspend', 'Resume', 'Status', 'Watchdog')]
    [string]$Action,

    # Dead-man's switch. A quiet window is announced as 1.5-3 hours; this is
    # deliberately well past that, so it never fights a real window.
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

function Get-Workers {
    @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
        Where-Object { $_.CommandLine -and $_.CommandLine -match 'gpu_state_runner\.py' })
}

$StateFile = Join-Path $PSScriptRoot 'quiet-window.state'

function Write-State([string]$What) {
    # Appended, never deleted: this doubles as the audit trail of who paused the
    # run and for how long.
    "{0}`t{1}`t{2}" -f (Get-Date).ToUniversalTime().ToString('o'), $What, $env:COMPUTERNAME |
        Add-Content -LiteralPath $StateFile -Encoding UTF8
}

function Get-SuspendedSince {
    if (-not (Test-Path -LiteralPath $StateFile)) { return $null }
    $last = @(Get-Content -LiteralPath $StateFile | Where-Object { $_ -match '\S' }) | Select-Object -Last 1
    if (-not $last) { return $null }
    $parts = $last -split "`t"
    if ($parts.Count -lt 2 -or $parts[1] -ne 'SUSPEND') { return $null }
    try { return [datetime]::Parse($parts[0], $null, [Globalization.DateTimeStyles]::RoundtripKind) } catch { return $null }
}

function Get-GpuUtil {
    try {
        $v = & nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>$null
        if ($LASTEXITCODE -eq 0 -and $v) { return [int]($v | Select-Object -First 1) }
    } catch { }
    return -1
}

$workers = @(Get-Workers)
if ($workers.Count -eq 0) {
    Write-Output 'no gpu_state_runner worker running'
    if ($Action -eq 'Status') { exit 0 }
    exit 1
}

foreach ($w in $workers) {
    $proc = Get-Process -Id $w.ProcessId -ErrorAction Stop
    switch ($Action) {
        'Suspend' {
            $rc = [Erdos.ProcCtl]::NtSuspendProcess($proc.Handle)
            if ($rc -ne 0) { throw "NtSuspendProcess failed on pid $($w.ProcessId), status 0x$('{0:X}' -f $rc)" }
            Write-State "SUSPEND"
            Write-Output "suspended pid $($w.ProcessId)"
            # Freezing the host process does not stop a kernel already on the
            # card; in-flight work drains first. Measured 5.2s / 10.6s / 14.8s
            # over three trials, so a fixed "wait ~3s" is wrong and would
            # contaminate the first seconds of somebody else's measurement.
            # Wait for the card to actually go quiet, so this command only
            # returns once the GPU is genuinely released.
            $t0 = Get-Date
            $drained = $false
            while (((Get-Date) - $t0).TotalSeconds -lt 90) {
                if ((Get-GpuUtil) -le 5) { $drained = $true; break }
                Start-Sleep -Milliseconds 400
            }
            $el = ((Get-Date) - $t0).TotalSeconds
            if ($drained) { Write-Output ("gpu released after {0:N1}s" -f $el) }
            else { Write-Output ("WARNING gpu still busy after {0:N1}s -- do not treat the card as quiet" -f $el) }
        }
        'Resume' {
            $rc = [Erdos.ProcCtl]::NtResumeProcess($proc.Handle)
            if ($rc -ne 0) { throw "NtResumeProcess failed on pid $($w.ProcessId), status 0x$('{0:X}' -f $rc)" }
            Write-State "RESUME"
            Write-Output "resumed pid $($w.ProcessId)"
        }
        'Watchdog' {
            # Resume a worker that has been suspended far longer than any
            # announced window. The hazard this closes: the supervisor is told
            # SUSPENDED is authorised, so if whoever called the window dies
            # before calling QUIET END, the run stalls silently for days.
            $threads = @($proc.Threads)
            $stopped = @($threads | Where-Object { $_.ThreadState -eq 'Wait' -and $_.WaitReason -eq 'Suspended' })
            if ($stopped.Count -ne $threads.Count) { Write-Output "pid $($w.ProcessId) running, nothing to do"; break }
            $since = Get-SuspendedSince
            if (-not $since) { Write-Output "pid $($w.ProcessId) SUSPENDED but no suspend record; leaving alone"; break }
            $hours = ((Get-Date).ToUniversalTime() - $since).TotalHours
            if ($hours -lt $MaxSuspendHours) {
                Write-Output ("pid {0} SUSPENDED {1:N2}h, under the {2}h limit; leaving alone" -f $w.ProcessId, $hours, $MaxSuspendHours)
                break
            }
            $rc = [Erdos.ProcCtl]::NtResumeProcess($proc.Handle)
            if ($rc -ne 0) { throw "watchdog NtResumeProcess failed on pid $($w.ProcessId), status 0x$('{0:X}' -f $rc)" }
            Write-State "WATCHDOG-RESUME"
            Write-Output ("WATCHDOG RESUMED pid {0} after {1:N2}h suspended (limit {2}h)" -f $w.ProcessId, $hours, $MaxSuspendHours)
        }
        'Status' {
            # A fully suspended process has every thread in Wait/Suspended.
            $threads = @($proc.Threads)
            $running = @($threads | Where-Object { $_.ThreadState -ne 'Wait' -or $_.WaitReason -ne 'Suspended' })
            $state = if ($running.Count -eq 0) { 'SUSPENDED' } else { 'RUNNING' }
            $extra = ''
            if ($state -eq 'SUSPENDED') {
                $since = Get-SuspendedSince
                if ($since) { $extra = " since={0:o} ({1:N2}h)" -f $since, ((Get-Date).ToUniversalTime() - $since).TotalHours }
            }
            Write-Output "pid $($w.ProcessId) $state threads=$($threads.Count) priority=$($proc.PriorityClass)$extra"
        }
    }
}

if ($Action -eq 'Resume') {
    Start-Sleep -Seconds 3
    Write-Output "gpu utilisation now $(Get-GpuUtil)%"
}
