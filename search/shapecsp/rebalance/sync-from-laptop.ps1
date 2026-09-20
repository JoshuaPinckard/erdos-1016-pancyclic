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
    # Level 71 (whole-tier pairwise states, tables under pairwise/tables-ext,
    # census under pairwise/gpu-blast-ext) is pulled for safekeeping; its claim
    # is finalized on the laptop, which holds the table files.
    [string[]]$PairwiseTiers = @('68:11', '70:11', '70:12', '71:12', '71:11', '71:10', '71:9', '71:8', '71:7', '71:6'),
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
        $psrc = $blast
        $ptab = Join-Path $pairwiseDir 'tables'
        if (-not (Test-Path (Join-Path $blast "n$n.jsonl"))) {
            $psrc = Join-Path $pairwiseDir 'gpu-blast-ext'
            $ptab = Join-Path $pairwiseDir 'tables-ext'
        }
        $vOut = & $python $pverify $psrc $localPath --n $n --b $b --tables $ptab 2>&1
        $vExit = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = 'Stop'
    }
    $vOut | ForEach-Object { "$_" } |
        Select-String -Pattern '"expected_unit_count"|"covered_unit_count"|"missing_unit_count"|"extra_unit_count"|"composition_totals_match"|"exact_match"|"errors"' |
        ForEach-Object { Write-Output "        $($_.Line.Trim())" }
    Write-Output "        verifier exit $vExit (1 is expected while the tier is still running)"
}

# Claim files.  finalize-laptop.sh writes ~/erdos-n70/verification/
# nN-bB-combined.json for every tier the laptop computes (level 71 and the odd
# levels 87..73).  papers/verification in this repository is the record of
# claims, so each one is pulled here.  Never overwrites: a local file with the
# same bytes is left alone, one with different bytes is a conflict (the laptop
# copy is kept beside it as .laptop-conflict and reported).  .part/.err files
# and empty files are not claims and are not pulled.
$claimOut = Join-Path (Split-Path -Parent (Split-Path -Parent $RepoDir)) 'papers\verification'
$RemoteClaimDir = '~/erdos-n70/verification'
$claimList = $null
try {
    $ErrorActionPreference = 'Continue'
    $claimList = & ssh -o BatchMode=yes $Remote "ls -1 $RemoteClaimDir 2>/dev/null | grep -E '^n[0-9]+-b[0-9]+-(combined|unrestricted)[.]json$' || true" 2>&1
    $lsExit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = 'Stop'
}
if ($lsExit -ne 0) {
    Write-Output "[sync] claims SKIPPED: ssh exit $lsExit ($($claimList -join ' '))"
} else {
    $claimNames = @($claimList | ForEach-Object { "$_".Trim() } | Where-Object { $_ -match '^n[0-9]+-b[0-9]+-(combined|unrestricted)\.json$' })
    Write-Output "[sync] claims on the laptop: $($claimNames.Count)"
    foreach ($name in $claimNames) {
        $localClaim = Join-Path $claimOut $name
        $tmpClaim = "$localClaim.incoming"
        $scpOut = $null
        try {
            $ErrorActionPreference = 'Continue'
            $scpOut = & scp -o BatchMode=yes "${Remote}:$RemoteClaimDir/$name" $tmpClaim 2>&1
            $scpExit = $LASTEXITCODE
        } finally {
            $ErrorActionPreference = 'Stop'
        }
        if ($scpExit -ne 0 -or -not (Test-Path $tmpClaim) -or (Get-Item -LiteralPath $tmpClaim).Length -eq 0) {
            Write-Output "[sync] claim $name SKIPPED: scp exit $scpExit $($scpOut -join ' ')"
            if (Test-Path $tmpClaim) { Remove-Item -LiteralPath $tmpClaim -Force }
            continue
        }
        if (Test-Path $localClaim) {
            $same = (Get-FileHash -LiteralPath $localClaim -Algorithm SHA256).Hash -eq (Get-FileHash -LiteralPath $tmpClaim -Algorithm SHA256).Hash
            if ($same) {
                Remove-Item -LiteralPath $tmpClaim -Force
                continue
            }
            Move-Item -LiteralPath $tmpClaim -Destination "$localClaim.laptop-conflict" -Force
            Write-Output "[sync] claim $name CONFLICT: local file differs from the laptop's; laptop copy kept as $name.laptop-conflict, local untouched"
            continue
        }
        if ($WhatIfOnly) {
            Write-Output "[sync] claim $name WOULD be installed (WhatIfOnly)"
            Remove-Item -LiteralPath $tmpClaim -Force
            continue
        }
        Move-Item -LiteralPath $tmpClaim -Destination $localClaim -Force
        $exact = Select-String -LiteralPath $localClaim -Pattern '"exact_match": (true|false)' | Select-Object -First 1
        $hits = Select-String -LiteralPath $localClaim -Pattern '"hits": \[\]' | Select-Object -First 1
        $exactText = if ($exact) { $exact.Matches[0].Value } else { 'exact_match ?' }
        $hitsText = if ($hits) { 'hits none' } else { 'hits PRESENT or unreadable' }
        Write-Output "[sync] claim $name installed: $exactText, $hitsText"
    }
}

Write-Output "[sync] done $((Get-Date).ToUniversalTime().ToString('o'))"
