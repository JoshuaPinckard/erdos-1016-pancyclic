<#
.SYNOPSIS
  Pull the tiers the laptop owns back into the desktop repository, and verify
  each one against the desktop's own manifest.

.DESCRIPTION
  After the 2026-09-19 rebalance the laptop computes n=69 b=11, whose results
  have to end up in this repository or the exhaustion claim for n=69 has a hole
  in it that nothing on this machine can see.

  A runner state file is machine-independent by construction: the unit plan is
  regenerated from the hashed manifest (gpu_state_runner.py derives `units` from
  `n<N>.jsonl` and binds `source_sha256` into the state), so a state file
  produced on the laptop means exactly the same thing here, provided the
  manifest bytes match.  Copying the file IS the sync; nothing has to be
  merged or replayed.  verify_tier_exhaustion.py is what proves it: it
  re-derives the expected unit key set here and reports `extra_unit_count`,
  which is non-zero if the two sides ever disagreed about the plan.

  Two independent guards stop this from destroying desktop-side work:
    1. an explicit allowlist of the tiers the laptop owns -- pulling
       n70-state-b11.json would clobber the copy this machine is now advancing;
    2. a refusal to replace a local state that already covers MORE units than
       the incoming one, whatever the allowlist says.

.PARAMETER Remote
  ssh destination of the laptop.  Required and not defaulted: the machine name
  belongs in the caller's configuration (the scheduled task registration), not
  baked into this file.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Remote,
    [string]$RemoteDir = '~/erdos-n70',
    # Resolved in the body, not here: under Windows PowerShell 5.1 $PSScriptRoot
    # is not yet bound while param() defaults are evaluated, so a default of
    # (Split-Path -Parent $PSScriptRoot) fails with "empty string".
    [string]$RepoDir,
    # (level, tier) pairs whose results the laptop holds.  70:10 is COMPLETE
    # and was computed entirely on the laptop; until 2026-09-19 its 3040 units
    # (1.04e14 ranks) existed nowhere else, so a laptop disk failure would have
    # destroyed them with nothing on this machine even able to notice.  It is
    # listed here so the pull is idempotent and keeps a second copy current.
    # Under the third (cost-weighted) split the laptop runs 68/11, 70/11 and
    # 70/12, and still holds the completed 70/10.  69:11 and 69:12 are
    # deliberately ABSENT: the desktop runs those and its copies are the live
    # ones, so pulling the laptop's stale copies over them would lose work.
    # The "local is ahead" refusal is a second, independent guard on that, but
    # the allowlist is the one that states the intent.
    [string[]]$Tiers = @('70:10', '68:11', '70:11', '70:12'),
    # Pairwise-plan state files (2026-09-19 cutover): same file name on both
    # machines, under search/shapecsp/pairwise/.  Same two guards as above.
    [string[]]$PairwiseTiers = @('68:11', '70:11', '70:12'),
    [string]$RemotePairwiseDir = '~/erdos-n70/search/shapecsp/pairwise',
    [switch]$WhatIfOnly
)

$ErrorActionPreference = 'Stop'
if (-not $RepoDir) { $RepoDir = Split-Path -Parent $PSScriptRoot }
$blast = Join-Path $RepoDir 'gpu-blast'
$verify = Join-Path $RepoDir 'verify_tier_exhaustion.py'
$python = 'python'

function Read-CompleteCount {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return -1 }
    try {
        return (Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json).complete.Count
    } catch {
        # Not a silent skip: an unreadable local state must not be treated as
        # "behind" and quietly replaced.
        Write-Warning "local state $Path is unreadable ($($_.Exception.Message)); treating as AHEAD and refusing"
        return [int]::MaxValue
    }
}

$stamp = (Get-Date).ToUniversalTime().ToString('o')
Write-Output "[sync] $stamp remote=$Remote repo=$RepoDir"

foreach ($tier in $Tiers) {
    $n, $b = $tier.Split(':')
    $remoteName = "n$n-state-b$b.json"
    $localName = "gpu-state-n$n-b$b.json"
    $localPath = Join-Path $RepoDir $localName
    $tmpPath = Join-Path $RepoDir "$localName.incoming"

    Write-Output "[sync] n=$n b=$b  $remoteName -> $localName"

    # $ErrorActionPreference='Stop' turns anything scp writes to stderr into a
    # TERMINATING error, which aborted the whole run the first time a tier had
    # not started on the laptop yet: no SKIPPED line, no "[sync] done", and
    # every later tier silently never pulled.  A missing remote tier is an
    # ordinary, expected state and must be reported and stepped over, so the
    # native call runs with Continue and its exit code is what decides.
    $scpOut = $null
    try {
        $ErrorActionPreference = 'Continue'
        $scpOut = & scp -o BatchMode=yes "${Remote}:$RemoteDir/$remoteName" $tmpPath 2>&1
        $scpExit = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = 'Stop'
    }
    foreach ($line in $scpOut) { Write-Output "        scp: $line" }
    if ($scpExit -ne 0) {
        Write-Output "[sync] n=$n b=$b SKIPPED: scp exit $scpExit -- the laptop has not started this tier yet, or it is unreachable. Nothing local was touched."
        if (Test-Path $tmpPath) { Remove-Item -LiteralPath $tmpPath -Force }
        continue
    }

    $incoming = Read-CompleteCount $tmpPath
    $existing = Read-CompleteCount $localPath
    Write-Output "        incoming complete_units=$incoming  local complete_units=$existing"

    if ($existing -gt $incoming) {
        Write-Output "[sync] n=$n b=$b REFUSED: local copy is ahead ($existing > $incoming); leaving it alone"
        Move-Item -LiteralPath $tmpPath -Destination "$tmpPath.rejected" -Force
        continue
    }
    if ($existing -eq $incoming) {
        Write-Output "[sync] n=$n b=$b unchanged ($incoming units); nothing to do"
        Remove-Item -LiteralPath $tmpPath -Force
        continue
    }

    if ($WhatIfOnly) {
        Write-Output "[sync] n=$n b=$b WOULD install $incoming units (WhatIfOnly)"
        Remove-Item -LiteralPath $tmpPath -Force
        continue
    }

    Move-Item -LiteralPath $tmpPath -Destination $localPath -Force
    Write-Output "[sync] n=$n b=$b installed $incoming units; verifying against this repo's manifest"
    & $python $verify $blast $localPath --n $n --b $b | ForEach-Object { Write-Output "        $_" }
}

$pairwiseDir = Join-Path $RepoDir 'pairwise'
# The verifier comes from the frozen production snapshot (pairwise-prod, commit
# f63f9f3), never from pairwise/, which is edited in place between commits.
$pverify = Join-Path (Join-Path $RepoDir 'pairwise-prod') 'verify_tier_exhaustion_pairwise.py'
foreach ($tier in $PairwiseTiers) {
    $n, $b = $tier.Split(':')
    $name = "pairwise-state-n$n-b$b.json"
    $localPath = Join-Path $pairwiseDir $name
    $tmpPath = "$localPath.incoming"
    Write-Output "[sync] pairwise n=$n b=$b  $name"
    $scpOut = $null
    try {
        $ErrorActionPreference = 'Continue'
        $scpOut = & scp -o BatchMode=yes "${Remote}:$RemotePairwiseDir/$name" $tmpPath 2>&1
        $scpExit = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = 'Stop'
    }
    foreach ($line in $scpOut) { Write-Output "        scp: $line" }
    if ($scpExit -ne 0) {
        Write-Output "[sync] pairwise n=$n b=$b SKIPPED: scp exit $scpExit -- not started on the laptop yet, or unreachable. Nothing local was touched."
        if (Test-Path $tmpPath) { Remove-Item -LiteralPath $tmpPath -Force }
        continue
    }
    $incoming = Read-CompleteCount $tmpPath
    $existing = Read-CompleteCount $localPath
    Write-Output "        incoming complete_units=$incoming  local complete_units=$existing"
    if ($existing -gt $incoming) {
        Write-Output "[sync] pairwise n=$n b=$b REFUSED: local copy is ahead ($existing > $incoming); leaving it alone"
        Move-Item -LiteralPath $tmpPath -Destination "$tmpPath.rejected" -Force
        continue
    }
    if ($existing -eq $incoming) {
        Write-Output "[sync] pairwise n=$n b=$b unchanged ($incoming units); nothing to do"
        Remove-Item -LiteralPath $tmpPath -Force
        continue
    }
    if ($WhatIfOnly) {
        Write-Output "[sync] pairwise n=$n b=$b WOULD install $incoming units (WhatIfOnly)"
        Remove-Item -LiteralPath $tmpPath -Force
        continue
    }
    Move-Item -LiteralPath $tmpPath -Destination $localPath -Force
    Write-Output "[sync] pairwise n=$n b=$b installed $incoming units; verifying against this repo's tier manifest"
    # The verifier prints a CuPy warning on stderr and exits 1 for a tier that is
    # simply not finished yet; under $ErrorActionPreference='Stop' either one
    # would abort the whole sync (it did, 2026-09-19 17:58), so run it with
    # Continue and report what it printed.
    $vOut = $null
    try {
        $ErrorActionPreference = 'Continue'
        $vOut = & $python $pverify $blast $localPath --n $n --b $b --tables (Join-Path $pairwiseDir 'tables') 2>&1
        $vExit = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = 'Stop'
    }
    $vOut | ForEach-Object { "$_" } |
        Select-String -Pattern '"expected_unit_count"|"covered_unit_count"|"missing_unit_count"|"extra_unit_count"|"composition_totals_match"|"exact_match"|"errors"' |
        ForEach-Object { Write-Output "        $($_.Line.Trim())" }
    Write-Output "        verifier exit $vExit (1 is expected while the tier is still running)"
}

Write-Output "[sync] done $((Get-Date).ToUniversalTime().ToString('o'))"
