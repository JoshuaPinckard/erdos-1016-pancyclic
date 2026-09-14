param([int]$from = 3, [int]$to = 40, [int]$kmax = 6)
Set-Location $PSScriptRoot
$out = "hn.csv"
if (-not (Test-Path $out)) { "n,h,witness,seconds,k_tried_none" | Set-Content $out }
foreach ($n in $from..$to) {
  # counting lower bound: 2^(h+1)-1 >= n-2
  $k = 0; while (([math]::Pow(2, $k + 1) - 1) -lt ($n - 2)) { $k++ }
  $nones = @()
  while ($k -le $kmax) {
    $sw = [Diagnostics.Stopwatch]::StartNew()
    $r = & .\pancyc.exe $n $k
    $sw.Stop()
    $line = ($r | Where-Object { $_ -match 'WITNESS|NONE' } | Select-Object -First 1)
    if ($line -match 'WITNESS') {
      $w = ($line -replace '^WITNESS n=\d+ k=\d+ :\s*', '')
      "$n,$k,`"$w`",$([int]$sw.Elapsed.TotalSeconds),`"$($nones -join ' ')`"" | Add-Content $out
      break
    } else {
      $nones += "k=$k($([int]$sw.Elapsed.TotalSeconds)s)"
      $k++
    }
  }
}
"done" | Add-Content $out
