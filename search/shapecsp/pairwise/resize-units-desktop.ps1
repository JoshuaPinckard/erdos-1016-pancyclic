<#
.SYNOPSIS
  Move the desktop's pairwise chain from unit_prefix 2^27 to 2^30 prefix ranks.

.DESCRIPTION
  The first 20 minutes under the pairwise plan measured 0.15 gpu_s per 2^27-
  prefix unit against ~0.27 s of wall per unit: the state write and launch
  overhead cost ~45% of the card.  unit_prefix lives in the tier manifests and
  in every plan hash, so: stop the chain (chain scripts first, then the
  runner), rewrite unit_prefix in the manifests, set the fresh 2^27 state files
  aside (they are refused under the new plan hash anyway), relaunch, verify
  from disk.  The set-aside states held < 20 minutes of work.
#>
[CmdletBinding()]
param([string]$TaskName = 'Erdos1016-desktop-chain', [long]$NewUnit = 1073741824)
$ErrorActionPreference = 'Stop'
$PW = $PSScriptRoot
$SC = Split-Path -Parent $PW
$marker = Join-Path (Join-Path $SC 'rebalance') 'benchmark-window.active'
$py = 'C:\Python313\python.exe'
function Say { param([string]$m) Write-Output ("[resize] " + $m) }
function Get-Runner { Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -like '*gpu_state_runner*' } | Select-Object -First 1 }
function Units { param([string]$Path) if (-not (Test-Path $Path)) { return -1 }
    try { return (Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json).complete.Count } catch { return -1 } }

if (Test-Path $marker) { Say "REFUSED: a benchmark window is active"; exit 2 }
$rc = 0
try {
    "30`nstarted=$((Get-Date).ToString('o'))`ncommand=resize-units-desktop.ps1" | Set-Content -LiteralPath $marker -Encoding ASCII
    & schtasks /end /tn $TaskName 2>&1 | ForEach-Object { Say "  schtasks: $_" }
    Get-CimInstance Win32_Process -Filter "Name='cmd.exe' OR Name='wscript.exe'" |
        Where-Object { $_.CommandLine -like '*run-chain-desktop*' } |
        ForEach-Object { Say "  stopping chain process $($_.ProcessId) $($_.Name)"; Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2
    $r = Get-Runner
    if ($r) { Say "stopping runner $($r.ProcessId)"; Stop-Process -Id $r.ProcessId -Force; Start-Sleep -Seconds 3 }
    if (Get-Runner) { throw "runner still alive" }
    Get-ChildItem (Join-Path $PW 'pairwise-state-n*.json.lock') -ErrorAction SilentlyContinue | ForEach-Object { Remove-Item $_.FullName -Force; Say "removed lock $($_.Name)" }
    $stamp = (Get-Date).ToString('yyyyMMdd-HHmmss')
    Get-ChildItem (Join-Path $PW 'pairwise-state-n*.json') | ForEach-Object {
        $u = Units $_.FullName
        $new = "$($_.FullName).unit27-$stamp.stale"
        Move-Item $_.FullName $new
        Say "set aside $($_.Name) ($u units of 2^27) -> $(Split-Path -Leaf $new)"
    }
    $out = & $py (Join-Path $PW 'set_unit_prefix.py') (Join-Path $PW 'tables') $NewUnit 2>&1
    if ($LASTEXITCODE -ne 0) { throw "set_unit_prefix failed: $out" }
    $out | ForEach-Object { Say "  $_" }
}
catch { Say "ERROR: $($_.Exception.Message)"; $rc = 5 }
finally {
    Remove-Item -LiteralPath $marker -Force -ErrorAction SilentlyContinue
    & schtasks /run /tn $TaskName 2>&1 | ForEach-Object { Say "  schtasks: $_" }
    $pst = Join-Path $PW 'pairwise-state-n69-b11.json'
    $ok = $false
    $deadline = (Get-Date).AddSeconds(420)
    while ((Get-Date) -lt $deadline) {
        if ((Get-Runner) -and (Units $pst) -ge 2) { $ok = $true; break }
        Start-Sleep -Seconds 10
    }
    if ($ok) {
        $j = Get-Content -Raw $pst | ConvertFrom-Json
        Say "RESUMED: unit_prefix=$($j.unit_prefix) units=$($j.complete.Count) runner pid $((Get-Runner).ProcessId)"
    } else { Say "NOT VERIFIED: units=$(Units $pst) runner $(if (Get-Runner) {'alive'} else {'ABSENT'})"; if ($rc -eq 0) { $rc = 6 } }
    Say ("chain-desktop.log tail: " + ((Get-Content (Join-Path $SC 'chain-desktop.log') -Tail 2) -join ' | '))
}
Say "done rc=$rc"
exit $rc
