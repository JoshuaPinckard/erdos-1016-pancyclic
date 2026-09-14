Set-Location $PSScriptRoot
foreach ($s in 0..7) {
  Start-Process -FilePath "$PSScriptRoot\pancyc3.exe" -ArgumentList "38","5","A","$s","8" -RedirectStandardOutput "n38k5-A$s.txt" -WindowStyle Hidden
}
Start-Process -FilePath "$PSScriptRoot\pancyc3.exe" -ArgumentList "38","5","BC" -RedirectStandardOutput "n38k5-BC.txt" -WindowStyle Hidden
