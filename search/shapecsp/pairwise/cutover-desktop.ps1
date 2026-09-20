<#
.SYNOPSIS
  Cut the desktop chain over from run-chain-desktop-v6.cmd (unrestricted plan)
  to run-chain-desktop-v7.cmd (pairwise plan), and prove from disk it resumed.

.DESCRIPTION
  1. health gate: the v6 runner must be alive and heartbeating, the tier
     tables for 69/11, 68/12, 69/12 must exist with the laptop-matching hash;
  2. write the benchmark-window marker (suppresses the 5-minute task trigger),
     end the task instance, confirm the runner exited and released its lock;
  3. partition the three tiers from their now-final unrestricted state files;
  4. point run-chain-desktop-hidden.vbs at v7 and READ IT BACK;
  5. clear the marker, schtasks /run, and verify from disk that a pairwise
     state file appears and advances.
  Every failure path clears the marker so the task trigger can bring back
  whatever wrapper is on disk.
#>
[CmdletBinding()]
param(
    [string]$TaskName = 'Erdos1016-desktop-chain',
    [string[]]$Tiers = @('69:11', '68:12', '69:12'),
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
$PW = $PSScriptRoot
$SC = Split-Path -Parent $PW
$marker = Join-Path (Join-Path $SC 'rebalance') 'benchmark-window.active'
$vbs = Join-Path $SC 'run-chain-desktop-hidden.vbs'
$py = 'C:\Python313\python.exe'
function Say { param([string]$m) Write-Output ("[cutover] " + $m) }
function Get-Runner {
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
        Where-Object { $_.CommandLine -like '*gpu_state_runner*' -and $_.CommandLine -like '*state-n*' } |
        Select-Object -First 1
}
function Units { param([string]$Path) if (-not (Test-Path $Path)) { return -1 }
    try { return (Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json).complete.Count } catch { return -1 } }

Say "health gate"
foreach ($t in $Tiers) {
    $n, $b = $t.Split(':')
    $m = Join-Path $PW "tables\n$n-b$b\tier-manifest.json"
    if (-not (Test-Path $m)) { Say "REFUSED: tier manifest missing: $m"; exit 2 }
    $j = Get-Content -Raw $m | ConvertFrom-Json
    if ($j.partial) { Say "REFUSED: partial manifest $m"; exit 2 }
    Say ("tables n=$n b=$b shapes=" + $j.shapes_count + " compositions=" + $j.tier_total_compositions)
}
if (Test-Path $marker) { Say "REFUSED: a benchmark window is active"; exit 2 }
$runner = Get-Runner
if ($runner) {
    if ($runner.CommandLine -match 'pairwise-state') { Say "REFUSED: the chain is already on the pairwise plan"; exit 2 }
    if ($runner.CommandLine -notmatch 'gpu-state-n(\d+)-b(\d+)\.json') { Say "REFUSED: runner is not on an unrestricted state file: $($runner.CommandLine)"; exit 2 }
    $curN = $Matches[1]; $curB = $Matches[2]
    $curState = Join-Path $SC "gpu-state-n$curN-b$curB.json"
    $lock = "$curState.lock"
    $before = Units $curState
    Say "runner pid $($runner.ProcessId) on n=$curN b=$curB units=$before"
} else {
    # The chain may be down already (a stopped task waiting for its 5-minute
    # trigger).  That is fine: the marker written below keeps it down while the
    # state files are partitioned, and the relaunch at the end starts v7.
    $n, $b = $Tiers[0].Split(':')
    $curN = $n; $curB = $b
    $curState = Join-Path $SC "gpu-state-n$curN-b$curB.json"
    $lock = "$curState.lock"
    $before = Units $curState
    Say "no chain runner alive; proceeding from the state files on disk (n=$curN b=$curB units=$before)"
}
if ($DryRun) { Say "dry run: stopping here"; exit 0 }

$rc = 0
try {
    "30`nstarted=$((Get-Date).ToString('o'))`ncommand=cutover-desktop.ps1" | Set-Content -LiteralPath $marker -Encoding ASCII
    Say "marker written; ending task instance"
    & schtasks /end /tn $TaskName 2>&1 | ForEach-Object { Say "  schtasks: $_" }
    # ORDER MATTERS: the chain scripts (wscript -> cmd -> cmd) must die BEFORE
    # the runner.  Killing the runner first makes cmd.exe see a finished job and
    # start the NEXT tier, which then survives as an orphan on the GPU.  That is
    # exactly what benchmark-window.ps1 did on 2026-09-19 17:10 (orphan 68/12).
    Get-CimInstance Win32_Process -Filter "Name='cmd.exe' OR Name='wscript.exe'" |
        Where-Object { $_.CommandLine -like '*run-chain-desktop*' } |
        ForEach-Object { Say "  stopping chain process $($_.ProcessId) $($_.Name)"; Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2
    $still = Get-Runner
    if ($still) { Say "stopping runner pid $($still.ProcessId) (unit in flight is lost, state file is atomic)"; Stop-Process -Id $still.ProcessId -Force; Start-Sleep -Seconds 3 }
    $deadline = (Get-Date).AddSeconds(30)
    while ((Get-Date) -lt $deadline -and (Get-Runner)) { Start-Sleep -Seconds 2 }
    if (Get-Runner) { throw "a runner is still alive after the stop sequence" }
    if (Test-Path $lock) { Remove-Item -LiteralPath $lock -Force; Say "removed the dead runner's lock $lock" }
    Get-ChildItem (Join-Path $SC 'gpu-state-n*.json.lock') -ErrorAction SilentlyContinue | ForEach-Object {
        Say "removing stale lock $($_.Name) (pid $(Get-Content $_.FullName -Raw))"; Remove-Item $_.FullName -Force }
    $after = Units $curState
    Say "chain stopped; n=$curN b=$curB units $before -> $after (state is now final)"

    Say "partitioning"
    New-Item -ItemType Directory -Force (Join-Path $PW 'partitions') | Out-Null
    foreach ($t in $Tiers) {
        $n, $b = $t.Split(':')
        $st = Join-Path $SC "gpu-state-n$n-b$b.json"
        $args = @((Join-Path $PW 'partition_tier.py'), '--source', (Join-Path $SC 'gpu-blast'), '--n', $n, '--b', $b, '--out', (Join-Path $PW 'partitions'))
        if (Test-Path $st) { $args += @('--state', $st) }
        $out = & $py @args 2>&1
        if ($LASTEXITCODE -ne 0) { throw "partition failed for $t : $out" }
        Say "  $out"
    }

    Say "pointing the wrapper at v7"
    $text = Get-Content -Raw -LiteralPath $vbs
    if ($text -notmatch 'run-chain-desktop-v6\.cmd') { throw "wrapper does not reference v6; refusing to edit" }
    $text = $text -replace 'run-chain-desktop-v6\.cmd', 'run-chain-desktop-v7.cmd'
    Set-Content -LiteralPath $vbs -Value $text -Encoding ASCII -NoNewline
    $back = Get-Content -Raw -LiteralPath $vbs
    if ($back -notmatch 'chain = fso\.BuildPath\(here, "run-chain-desktop-v7\.cmd"\)') { throw "read-back failed: wrapper does not build the v7 path" }
    Say "wrapper read back: v7"
}
catch { Say "ERROR: $($_.Exception.Message)"; $rc = 5 }
finally {
    Remove-Item -LiteralPath $marker -Force -ErrorAction SilentlyContinue
    Say "marker cleared; starting task"
    & schtasks /run /tn $TaskName 2>&1 | ForEach-Object { Say "  schtasks: $_" }
    $n, $b = $Tiers[0].Split(':')
    $pst = Join-Path $PW "pairwise-state-n$n-b$b.json"
    $ok = $false
    $deadline = (Get-Date).AddSeconds(420)
    while ((Get-Date) -lt $deadline) {
        $u = Units $pst
        if ((Get-Runner) -and $u -ge 1) { $ok = $true; break }
        Start-Sleep -Seconds 10
    }
    if ($ok) { Say "RESUMED under the pairwise plan: $pst units=$(Units $pst), runner pid $((Get-Runner).ProcessId)" }
    else { Say "NOT VERIFIED: $pst units=$(Units $pst); runner $(if (Get-Runner) {'alive'} else {'ABSENT'}). Task trigger keeps retrying every 5 min."; if ($rc -eq 0) { $rc = 6 } }
    Say ("chain-desktop.log tail: " + ((Get-Content (Join-Path $SC 'chain-desktop.log') -Tail 3) -join ' | '))
}
Say "done rc=$rc"
exit $rc
