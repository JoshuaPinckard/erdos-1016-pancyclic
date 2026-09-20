<#
.SYNOPSIS
  Turn each finished production tier into a claim file without anyone watching.

.DESCRIPTION
  Every PollMinutes, for each tier in Tiers that has no claim file yet under
  papers/verification/: run the fast monitoring verifier
  (pairwise-prod/verify_tier_exhaustion_pairwise.py) on the pairwise state file;
  when it exits 0 the tier's pairwise units are all present, so start the CLAIM
  tool (pairwise-prod/verify_tier_combined.py --rebuild -1: every shape rebuilt
  from its gpu-blast row, hash compared) as a low-priority background process
  pinned off the runner's cores, and rename its output to
  papers/verification/n{N}-b{B}-combined.json when it exits.  Laptop tiers
  (68/11, 70/11, 70/12) arrive through the hourly sync task, so they are
  finalized here as well, on the desktop copies.  Exits when every tier has a
  claim file.  All code comes from the frozen pairwise-prod snapshot.
#>
param(
    [int]$PollMinutes = 10,
    [string[]]$Tiers = @('69:11', '68:12', '69:12', '68:11', '70:11', '70:12')
)
$ErrorActionPreference = 'Continue'
$SC = Split-Path -Parent $PSScriptRoot
$PROD = Join-Path $SC 'pairwise-prod'
$PW = Join-Path $SC 'pairwise'
$PY = 'C:\Python313\python.exe'
$REPO = Split-Path -Parent (Split-Path -Parent $SC)
$OUT = Join-Path $REPO 'papers\verification'
New-Item -ItemType Directory -Force -Path $OUT | Out-Null
$log = Join-Path $PSScriptRoot 'finalize.log'
function Say { param([string]$m) Add-Content -LiteralPath $log -Value ("[finalize] " + (Get-Date).ToString('yyyy-MM-dd HH:mm:ss') + " " + $m) -Encoding ASCII }
$env:PYTHONUTF8 = '1'
$running = @{}
Say "start tiers=$($Tiers -join ',') poll=${PollMinutes}m prod=$PROD"
while ($true) {
    $pending = 0
    foreach ($t in $Tiers) {
        $n, $b = $t.Split(':')
        $final = Join-Path $OUT "n$n-b$b-combined.json"
        if (Test-Path $final) { continue }
        if ($running.ContainsKey($t)) {
            $p = $running[$t]
            if ($p.HasExited) {
                $running.Remove($t)
                $part = "$final.part"
                if (Test-Path $part) { Move-Item -LiteralPath $part -Destination $final -Force }
                $m = Select-String -LiteralPath $final -Pattern '"exact_match": (true|false)' | Select-Object -First 1
                $grade = if ($m) { $m.Matches[0].Groups[1].Value } else { 'unparsed' }
                $mm = Select-String -LiteralPath $final -Pattern '"rebuilt_mismatches": (\d+)' | Select-Object -First 1
                $bad = if ($mm) { $mm.Matches[0].Groups[1].Value } else { '?' }
                Say "n=$n b=$b combined verifier exit=$($p.ExitCode) exact_match=$grade rebuilt_mismatches=$bad -> $final"
            } else { $pending++ }
            continue
        }
        $pending++
        $state = Join-Path $PW "pairwise-state-n$n-b$b.json"
        if (-not (Test-Path $state)) { continue }
        & $PY (Join-Path $PROD 'verify_tier_exhaustion_pairwise.py') (Join-Path $SC 'gpu-blast') $state --n $n --b $b --tables (Join-Path $PW 'tables') 2>$null | Out-Null
        if ($LASTEXITCODE -ne 0) { continue }
        Say "n=$n b=$b pairwise units complete (fast verifier exit 0); starting the claim tool with --rebuild -1"
        $ustate = Join-Path $SC "gpu-state-n$n-b$b.json"
        $vargs = @((Join-Path $PROD 'verify_tier_combined.py'), (Join-Path $SC 'gpu-blast'), '--n', $n, '--b', $b,
                   '--pairwise-state', $state, '--tables', (Join-Path $PW 'tables'), '--rebuild', '-1')
        if (Test-Path $ustate) { $vargs += @('--unrestricted-state', $ustate) }
        $p = Start-Process -FilePath $PY -ArgumentList $vargs -NoNewWindow -PassThru `
            -RedirectStandardOutput "$final.part" -RedirectStandardError "$final.err"
        try { $p.PriorityClass = 'BelowNormal'; $p.ProcessorAffinity = [IntPtr]0xFC } catch { Say "could not pin/deprioritise pid $($p.Id): $($_.Exception.Message)" }
        $running[$t] = $p
        Say "n=$n b=$b claim tool pid $($p.Id)"
    }
    if ($pending -eq 0) { Say 'all tiers have claim files; exiting'; break }
    Start-Sleep -Seconds (60 * $PollMinutes)
}
