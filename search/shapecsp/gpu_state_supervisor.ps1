param(
    [string]$Root = 'C:\Users\ToolsEnabled-Dev\Desktop\erdos1016',
    [int]$N = 68,
    [string]$State = 'search\shapecsp\gpu-state-n68-b9.json'
)
$runner = Join-Path $Root 'search\shapecsp\gpu_state_runner.py'
$source = Join-Path $Root 'search\shapecsp\gpu-blast'
$statePath = Join-Path $Root $State
$needle = [regex]::Escape($statePath)
$live = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -match 'gpu_state_runner\.py' -and $_.CommandLine -match $needle }
if ($live) { exit 0 }
$cmd = '"C:\Python313\python.exe" "' + $runner + '" "' + $source +
    '" "' + $statePath + '" --n ' + $N + ' --min-b 6 --max-b 9 --wall-budget 86400'
[void](Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmd })
