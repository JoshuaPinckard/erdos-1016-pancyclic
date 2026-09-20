<#
.SYNOPSIS
  Point run-chain-desktop-hidden.vbs at a new chain version between runs, and
  prove from disk that the new chain started.

.DESCRIPTION
  Generic successor of cutover-desktop.ps1 for the case where the next chain
  version only APPENDS work (v7 -> v8: the same production tiers, resumed from
  their state files, then the n=67 blind control).  Stop order is chain
  scripts first, runner second (see the 2026-09-19 17:10 orphan incident);
  the benchmark-window marker keeps the 5-minute task trigger out while the
  wrapper is edited; every failure path clears the marker and starts the task.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$From,     # e.g. v7
    [Parameter(Mandatory = $true)][string]$To,       # e.g. v8
    [Parameter(Mandatory = $true)][string]$ExpectState,  # state file (under pairwise\) that must exist and advance after the relaunch
    [string]$TaskName = 'Erdos1016-desktop-chain',
    [int]$VerifySeconds = 600
)
$ErrorActionPreference = 'Stop'
$PW = $PSScriptRoot
$SC = Split-Path -Parent $PW
$marker = Join-Path (Join-Path $SC 'rebalance') 'benchmark-window.active'
$vbs = Join-Path $SC 'run-chain-desktop-hidden.vbs'
function Say { param([string]$m) Write-Output ("[repoint] " + $m) }
function Get-Runner { Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -like '*gpu_state_runner*' } | Select-Object -First 1 }
function Units { param([string]$Path) if (-not (Test-Path $Path)) { return -1 }
    try { return (Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json).complete.Count } catch { return -1 } }

if (Test-Path $marker) { Say "REFUSED: a benchmark window is active"; exit 2 }
if (-not (Test-Path (Join-Path $SC "run-chain-desktop-$To.cmd"))) { Say "REFUSED: run-chain-desktop-$To.cmd missing"; exit 2 }
$text = Get-Content -Raw -LiteralPath $vbs
if ($text -notmatch ('run-chain-desktop-' + [regex]::Escape($From) + '\.cmd')) { Say "REFUSED: wrapper does not reference $From"; exit 2 }
$rc = 0
try {
    "30`nstarted=$((Get-Date).ToString('o'))`ncommand=repoint-wrapper.ps1 $From -> $To" | Set-Content -LiteralPath $marker -Encoding ASCII
    & schtasks /end /tn $TaskName 2>&1 | ForEach-Object { Say "  schtasks: $_" }
    Get-CimInstance Win32_Process -Filter "Name='cmd.exe' OR Name='wscript.exe'" |
        Where-Object { $_.CommandLine -like '*run-chain-desktop*' } |
        ForEach-Object { Say "  stopping chain process $($_.ProcessId) $($_.Name)"; Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2
    $r = Get-Runner
    if ($r) { Say "stopping runner $($r.ProcessId) (unit in flight lost; state file atomic)"; Stop-Process -Id $r.ProcessId -Force; Start-Sleep -Seconds 3 }
    if (Get-Runner) { throw "runner still alive" }
    Get-ChildItem (Join-Path $PW '*.json.lock') -ErrorAction SilentlyContinue | ForEach-Object { Remove-Item $_.FullName -Force; Say "removed lock $($_.Name)" }
    $new = $text -replace ('run-chain-desktop-' + [regex]::Escape($From) + '\.cmd'), "run-chain-desktop-$To.cmd"
    Set-Content -LiteralPath $vbs -Value $new -Encoding ASCII -NoNewline
    $back = Get-Content -Raw -LiteralPath $vbs
    if ($back -notmatch ('chain = fso\.BuildPath\(here, "run-chain-desktop-' + [regex]::Escape($To) + '\.cmd"\)')) { throw "read-back failed: wrapper does not build the $To path" }
    Say "wrapper read back: $To"
}
catch { Say "ERROR: $($_.Exception.Message)"; $rc = 5 }
finally {
    Remove-Item -LiteralPath $marker -Force -ErrorAction SilentlyContinue
    & schtasks /run /tn $TaskName 2>&1 | ForEach-Object { Say "  schtasks: $_" }
    $pst = Join-Path $PW $ExpectState
    $ok = $false
    $deadline = (Get-Date).AddSeconds($VerifySeconds)
    while ((Get-Date) -lt $deadline) {
        if ((Get-Runner) -and (Units $pst) -ge 1) { $ok = $true; break }
        Start-Sleep -Seconds 10
    }
    if ($ok) { Say "RESUMED under $To : $ExpectState units=$(Units $pst), runner pid $((Get-Runner).ProcessId)" }
    else { Say "NOT VERIFIED: $ExpectState units=$(Units $pst); runner $(if (Get-Runner) {'alive'} else {'ABSENT'})"; if ($rc -eq 0) { $rc = 6 } }
    Say ("chain-desktop.log tail: " + ((Get-Content (Join-Path $SC 'chain-desktop.log') -Tail 2) -join ' | '))
}
Say "done rc=$rc"
exit $rc
