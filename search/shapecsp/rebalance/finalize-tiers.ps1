<#
.SYNOPSIS
  Turn each finished tier into a claim file (or a control verdict) without
  anyone watching.

.DESCRIPTION
  Every PollMinutes, for each entry in Tiers that has no result file yet under
  papers/verification/:

    N:B           production tier.  Run the completeness gate
                  (pairwise/check_control.py: unit set re-derived from the tier
                  manifest and the state's own --only-shapes list) on the
                  pairwise state; when it does not exit 2 the tier's pairwise
                  units are all present, so start the CLAIM tool
                  (pairwise-prod/verify_tier_combined.py --rebuild -1: every
                  shape rebuilt from its gpu-blast row, hash compared) as a
                  low-priority background process pinned off the runner's
                  cores; its JSON becomes n{N}-b{B}-combined.json.
    N:B:control   blind positive control (level 67).  pairwise/check_control.py
                  exits 2 while the control state is incomplete, 0 when complete
                  and passed, 1 when complete and failed; the JSON becomes
                  control-n{N}-b{B}.json as soon as it is complete.

  Laptop production tiers (68/11, 70/11, 70/12) arrive through the hourly sync
  task and are finalized here on the desktop copies.  Exits when every entry has
  a result file.  All verification code comes from the frozen pairwise-prod
  snapshot; check_control.py only reads state, manifest and census files.
  Start it through the scheduled task Erdos1016-finalize (schtasks /run): a
  helper launched from an agent shell dies with that shell.
#>
param(
    [int]$PollMinutes = 10,
    [string[]]$Tiers = @('69:11', '68:12', '69:12', '68:11', '70:11', '70:12',
                         '67:12:control', '67:11:control', '67:10:control', '67:9:control',
                         '67:8:control', '67:7:control', '67:6:control',
                         '89:12:ext', '89:11:ext', '89:10:ext', '88:12:ext', '88:11:ext', '88:10:ext',
                         '86:12:ext', '86:11:ext', '86:10:ext',
                         '84:12:ext', '84:11:ext', '84:10:ext', '84:9:ext',
                         '82:12:ext', '82:11:ext', '82:10:ext', '82:9:ext',
                         '80:12:ext', '80:11:ext', '80:10:ext', '80:9:ext',
                         '78:12:ext', '78:11:ext', '78:10:ext', '78:9:ext',
                         '76:12:ext', '76:11:ext', '76:10:ext', '76:9:ext', '76:8:ext',
                         '74:12:ext', '74:11:ext', '74:10:ext', '74:9:ext', '74:8:ext',
                         '72:12:ext', '72:11:ext', '72:10:ext', '72:9:ext', '72:8:ext', '72:7:ext', '72:6:ext')
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
function Field { param([string]$Path, [string]$Name)
    # Quoted string fields ("status": "passed") as well as bare booleans and numbers.
    $m = Select-String -LiteralPath $Path -Pattern ('"' + $Name + '": "?([A-Za-z0-9_-]+)"?') | Select-Object -First 1
    if ($m) { $m.Matches[0].Groups[1].Value } else { '?' } }
$env:PYTHONUTF8 = '1'
$running = @{}
Say "start pid=$PID tiers=$($Tiers -join ',') poll=${PollMinutes}m prod=$PROD"
while ($true) {
    $pending = 0
    foreach ($t in $Tiers) {
        $parts = $t.Split(':')
        $n, $b = $parts[0], $parts[1]
        $kind = if ($parts.Count -ge 3) { $parts[2] } else { 'prod' }
        $final = if ($kind -eq 'control') { Join-Path $OUT "control-n$n-b$b.json" } else { Join-Path $OUT "n$n-b$b-combined.json" }
        if (Test-Path $final) { continue }
        if ($running.ContainsKey($t)) {
            $p = $running[$t]
            if ($p.HasExited) {
                $running.Remove($t)
                $part = "$final.part"
                if (Test-Path $part) { Move-Item -LiteralPath $part -Destination $final -Force }
                Say "n=$n b=$b claim tool exit=$($p.ExitCode) exact_match=$(Field $final 'exact_match') rebuilt_mismatches=$(Field $final 'rebuilt_mismatches') rebuild_covers_every_pairwise_shape=$(Field $final 'rebuild_covers_every_pairwise_shape') -> $final"
            } else { $pending++ }
            continue
        }
        # A claim tool started by an EARLIER finalizer instance (this script is
        # restarted whenever its tier list changes) is adopted by command line,
        # never duplicated: while it runs the entry stays pending; once it is
        # gone its .part output becomes the result file.
        if ($kind -ne 'control') {
            $alive = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
                Where-Object { $_.CommandLine -like '*verify_tier_combined.py*' -and $_.CommandLine -like "*--n $n --b $b *" }
            $part = "$final.part"
            if ($alive) { $pending++; continue }
            if ((Test-Path $part) -and (Get-Item $part).Length -gt 0) {
                Move-Item -LiteralPath $part -Destination $final -Force
                Say "n=$n b=$b claim tool (earlier finalizer) finished: exact_match=$(Field $final 'exact_match') rebuilt_mismatches=$(Field $final 'rebuilt_mismatches') rebuild_covers_every_pairwise_shape=$(Field $final 'rebuild_covers_every_pairwise_shape') -> $final"
                continue
            }
        }
        $pending++
        if ($kind -eq 'control') {
            $state = Join-Path $PW "control-state-n$n-b$b.json"
            if (-not (Test-Path $state)) { continue }
            $part = "$final.part"
            & $PY (Join-Path $PW 'check_control.py') --n $n --b $b --state $state 2>"$final.err" | Set-Content -LiteralPath $part -Encoding ASCII
            $rc = $LASTEXITCODE
            if ($rc -eq 2) { continue }
            Move-Item -LiteralPath $part -Destination $final -Force
            Say "control n=$n b=$b complete: status=$(Field $final 'status') hits=$(Field $final 'hits') failing=$(Field $final 'hits_failing_independent_verifier') family_witness_found=$(Field $final 'family_witness_found') exit=$rc -> $final"
            continue
        }
        $state = Join-Path $PW "pairwise-state-n$n-b$b.json"
        if (-not (Test-Path $state)) { continue }
        # N:B:ext -- a whole-tier state over a census level (pairwise/gpu-blast-ext,
        # tables under pairwise/tables-ext, no unrestricted side).
        $src = Join-Path $SC 'gpu-blast'
        $tab = Join-Path $PW 'tables'
        if ($kind -eq 'ext') { $src = Join-Path $PW 'gpu-blast-ext'; $tab = Join-Path $PW 'tables-ext' }
        # Completeness gate.  A production state is restricted with --only-shapes,
        # which the whole-tier monitoring verifier reports as an error by design
        # (it expects every unit of the tier: 5396 expected vs 3543 covered on the
        # finished 68/11 at 19:37), so the gate is check_control.py, which
        # re-derives the unit set from the manifest and the state's own shape
        # list: exit 2 = not complete, 0 or 1 = complete.  An ext tier is a
        # whole-tier state and takes the same gate.
        & $PY (Join-Path $PW 'check_control.py') --n $n --b $b --state $state --source $src --tables $tab 2>$null | Out-Null
        if ($LASTEXITCODE -eq 2) { continue }
        Say "n=$n b=$b pairwise units complete (gate exit $LASTEXITCODE); starting the claim tool with --rebuild -1"
        $ustate = Join-Path $SC "gpu-state-n$n-b$b.json"
        $vargs = @((Join-Path $PROD 'verify_tier_combined.py'), $src, '--n', $n, '--b', $b,
                   '--pairwise-state', $state, '--tables', $tab, '--rebuild', '-1')
        if ($kind -ne 'ext' -and (Test-Path $ustate)) { $vargs += @('--unrestricted-state', $ustate) }
        $p = Start-Process -FilePath $PY -ArgumentList $vargs -NoNewWindow -PassThru `
            -RedirectStandardOutput "$final.part" -RedirectStandardError "$final.err"
        try { $p.PriorityClass = 'BelowNormal'; $p.ProcessorAffinity = [IntPtr]0xFC } catch { Say "could not pin/deprioritise pid $($p.Id): $($_.Exception.Message)" }
        $running[$t] = $p
        Say "n=$n b=$b claim tool pid $($p.Id)"
    }
    if ($pending -eq 0) { Say 'all entries have result files; exiting'; break }
    Start-Sleep -Seconds (60 * $PollMinutes)
}
