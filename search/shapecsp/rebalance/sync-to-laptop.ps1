<#
.SYNOPSIS
  Hand a tier's state file from this repository to the laptop, for a migration
  that moves work desktop -> laptop.

.DESCRIPTION
  The mirror of sync-from-laptop.ps1.  A runner state file is machine-
  independent by construction -- gpu_state_runner.py regenerates the unit plan
  from the hashed manifest and binds source_sha256 into the state -- so copying
  the file IS the migration, in either direction, provided the manifest bytes
  match on both sides.

  This is a ONE-SHOT migration tool, deliberately not scheduled.  The hourly job
  pulls FROM the laptop; a scheduled push in the other direction would race it.

  Two guards, matching the pull:
    1. an explicit list of the tiers being handed over, so a stray argument
       cannot push a tier this machine is actively advancing;
    2. a refusal to overwrite a remote state that already covers MORE units,
       whatever the list says.

  Verification is done ON THE LAPTOP against the laptop's own manifest, because
  verifying against this machine's copy would prove nothing about what the
  laptop will actually read.

.PARAMETER Remote
  ssh destination of the laptop.  Required and not defaulted: the machine name
  belongs in the caller's invocation, not baked into this file.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Remote,
    [Parameter(Mandatory = $true)][string[]]$Tiers,
    [string]$RemoteDir = '~/erdos-n70',
    [string]$RemoteBlast = '~/erdos-n70/search/shapecsp/gpu-blast',
    [string]$RepoDir
)

$ErrorActionPreference = 'Stop'
if (-not $RepoDir) { $RepoDir = Split-Path -Parent $PSScriptRoot }

function Invoke-Native {
    param([scriptblock]$Block)
    # Native stderr must not become a terminating error: a remote file that is
    # simply absent is an ordinary, expected state and has to be reported and
    # stepped over, not allowed to abort the run silently.
    try { $ErrorActionPreference = 'Continue'; $out = & $Block 2>&1; $code = $LASTEXITCODE }
    finally { $ErrorActionPreference = 'Stop' }
    return @{ Output = $out; Exit = $code }
}

Write-Output "[push] $((Get-Date).ToUniversalTime().ToString('o')) remote=$Remote repo=$RepoDir"

foreach ($tier in $Tiers) {
    $n, $b = $tier.Split(':')
    $localName = "gpu-state-n$n-b$b.json"
    $localPath = Join-Path $RepoDir $localName
    $remoteName = "n$n-state-b$b.json"

    Write-Output "[push] n=$n b=$b  $localName -> $remoteName"

    if (-not (Test-Path $localPath)) {
        Write-Output "[push] n=$n b=$b SKIPPED: $localName is not in this repo. Nothing sent."
        continue
    }
    $localUnits = (Get-Content -Raw -LiteralPath $localPath | ConvertFrom-Json).complete.Count

    # What does the laptop already have?
    #
    # "the file is not there" and "I could not find out" are DIFFERENT answers
    # and must not collapse together.  The first version folded both into -1,
    # so a probe that failed for any reason -- quoting, ssh, a corrupt file --
    # looked exactly like an empty slot and the ahead-guard was skipped.  That
    # is the guard silently not firing, which is worse than no guard at all
    # because the log still prints a number.  The remote now names its own
    # state and anything unrecognised refuses.
    $remoteProbe = "if [ ! -f $RemoteDir/$remoteName ]; then echo ABSENT; " +
                   "elif python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1]))[\""complete\""]))' $RemoteDir/$remoteName; then :; " +
                   "else echo PROBE_FAILED; fi"
    $probe = Invoke-Native { ssh -o BatchMode=yes $Remote $remoteProbe }
    $answer = ($probe.Output | Where-Object { "$_".Trim() } | Select-Object -Last 1)
    $answer = "$answer".Trim()

    if ($probe.Exit -ne 0 -or $answer -eq 'PROBE_FAILED' -or
        -not ($answer -eq 'ABSENT' -or $answer -match '^\d+$')) {
        Write-Output "[push] n=$n b=$b REFUSED: could not read the laptop's copy (ssh exit $($probe.Exit), answer '$answer'). Not overwriting something I cannot see."
        continue
    }
    $remoteUnits = if ($answer -eq 'ABSENT') { -1 } else { [int]$answer }
    $shown = if ($answer -eq 'ABSENT') { 'absent' } else { $remoteUnits }
    Write-Output "        local complete_units=$localUnits  remote complete_units=$shown"

    if ($remoteUnits -gt $localUnits) {
        Write-Output "[push] n=$n b=$b REFUSED: the laptop copy is ahead ($remoteUnits > $localUnits); leaving it alone"
        continue
    }
    if ($remoteUnits -eq $localUnits) {
        Write-Output "[push] n=$n b=$b unchanged ($localUnits units); nothing to do"
        continue
    }

    $send = Invoke-Native { scp -o BatchMode=yes $localPath "${Remote}:$RemoteDir/$remoteName" }
    foreach ($line in $send.Output) { Write-Output "        scp: $line" }
    if ($send.Exit -ne 0) {
        Write-Output "[push] n=$n b=$b FAILED: scp exit $($send.Exit). The laptop was not changed."
        continue
    }

    Write-Output "[push] n=$n b=$b sent $localUnits units; verifying on the laptop against ITS manifest"
    $ver = Invoke-Native { ssh -o BatchMode=yes $Remote "cd $RemoteDir && python3 verify_tier_exhaustion.py $RemoteBlast $RemoteDir/$remoteName --n $n --b $b" }
    foreach ($line in $ver.Output) { Write-Output "        $line" }
    if ($ver.Exit -ne 0) {
        Write-Output "[push] n=$n b=$b WARNING: verification could not be run on the laptop (exit $($ver.Exit)). The file was sent; its agreement with the laptop's manifest is UNCONFIRMED."
    }
}

Write-Output "[push] done $((Get-Date).ToUniversalTime().ToString('o'))"
