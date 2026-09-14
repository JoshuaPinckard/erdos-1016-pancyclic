param([int]$from = 38, [int]$to = 48, [int]$k = 5, [int]$secs = 900)
Set-Location $PSScriptRoot
foreach ($n in $from..$to) {
  $r = python localsearch.py $n $k $secs 2>&1 | Select-Object -Last 1
  "$(Get-Date -Format s) $r" | Add-Content ls.log
}
