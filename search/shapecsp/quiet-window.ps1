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
    [ValidateSet('Suspend', 'Resume', 'Status')]
    [string]$Action
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
            Write-Output "suspended pid $($w.ProcessId)"
        }
        'Resume' {
            $rc = [Erdos.ProcCtl]::NtResumeProcess($proc.Handle)
            if ($rc -ne 0) { throw "NtResumeProcess failed on pid $($w.ProcessId), status 0x$('{0:X}' -f $rc)" }
            Write-Output "resumed pid $($w.ProcessId)"
        }
        'Status' {
            # A fully suspended process has every thread in Wait/Suspended.
            $threads = @($proc.Threads)
            $running = @($threads | Where-Object { $_.ThreadState -ne 'Wait' -or $_.WaitReason -ne 'Suspended' })
            $state = if ($running.Count -eq 0) { 'SUSPENDED' } else { 'RUNNING' }
            Write-Output "pid $($w.ProcessId) $state threads=$($threads.Count) priority=$($proc.PriorityClass)"
        }
    }
}

if ($Action -ne 'Status') {
    Start-Sleep -Seconds 3
    Write-Output "gpu utilisation now $(Get-GpuUtil)%"
}
