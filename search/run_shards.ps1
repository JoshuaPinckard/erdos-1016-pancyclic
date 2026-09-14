param([int]$from = 39, [int]$to = 70, [int]$k = 5, [int]$shards = 8)
Set-Location $PSScriptRoot
$out = "hn_k$k.csv"
if (-not (Test-Path $out)) { "n,k,result,witness,seconds,tested" | Set-Content $out }
foreach ($n in $from..$to) {
  $sw = [Diagnostics.Stopwatch]::StartNew()
  $procs = @()
  Remove-Item "sh-$n-*.txt" -ErrorAction SilentlyContinue
  foreach ($s in 0..($shards-1)) {
    $procs += Start-Process -FilePath "$PSScriptRoot\pancyc3.exe" -ArgumentList "$n","$k","A","$s","$shards" -RedirectStandardOutput "sh-$n-A$s.txt" -WindowStyle Hidden -PassThru
  }
  $procs += Start-Process -FilePath "$PSScriptRoot\pancyc3.exe" -ArgumentList "$n","$k","BC" -RedirectStandardOutput "sh-$n-BC.txt" -WindowStyle Hidden -PassThru
  $witness = $null
  while ($true) {
    Start-Sleep -Seconds 5
    foreach ($f in Get-ChildItem "sh-$n-*.txt") {
      $c = Get-Content $f.FullName -ErrorAction SilentlyContinue
      $w = $c | Where-Object { $_ -match '^WITNESS' } | Select-Object -First 1
      if ($w) { $witness = $w; break }
    }
    if ($witness) { break }
    $alive = ($procs | Where-Object { -not $_.HasExited }).Count
    if ($alive -eq 0) { break }
  }
  foreach ($p in $procs) { if (-not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue } }
  $sw.Stop()
  $tested = 0; foreach ($f in Get-ChildItem "sh-$n-*.txt") { $c = Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue; if ($c -match 'tested=(\d+)') { $tested += [int64]$Matches[1] } }
  if ($witness) {
    $wtxt = $witness -replace '^WITNESS n=\d+ k=\d+ :\s*',''
    "$n,$k,WITNESS,`"$wtxt`",$([int]$sw.Elapsed.TotalSeconds),$tested" | Add-Content $out
  } else {
    "$n,$k,NONE,,$([int]$sw.Elapsed.TotalSeconds),$tested" | Add-Content $out
    break
  }
}
"done" | Add-Content $out
