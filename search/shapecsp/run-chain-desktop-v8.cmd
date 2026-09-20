@echo off
REM Sequential chain for the desktop GPU.  Successor to run-chain-desktop-v7.cmd
REM (2026-09-19).  v2..v7 are left on disk untouched: cmd.exe reads a batch
REM file incrementally by byte offset.
REM
REM Same three production tiers as v7 (they resume from their state files and
REM finish instantly once exhausted), then a BLIND POSITIVE CONTROL: the whole
REM of level n=67 (every eligible shape, every b) under the pairwise plan, from
REM the census manifest pairwise\gpu-blast-ext\n67.jsonl and the tables under
REM pairwise\tables-ext.  Level 67 is known to contain 6-chord pancyclic
REM witnesses (the family witness (0,2)(0,60)(1,13)(3,61)(4,31)(59,62) among
REM them), so the run MUST report VERIFIED SAT lines; a level-67 run that ends
REM with zero hits would falsify the pipeline, not the witnesses.  The control
REM state files are named control-state-n67-b%B%.json so nothing can mistake
REM them for production tiers.

setlocal
set SC=%~dp0
set PY=C:\Python313\python.exe
set PW=%SC%pairwise
set RUNNER=%PW%\gpu_state_runner_pairwise.py
set SRC=%SC%gpu-blast
set RC=0

echo [chain] start %DATE% %TIME% script=v8 plan=pairwise

call :job 69 11
call :job 68 12
call :job 69 12

echo [chain] production tiers reported complete %DATE% %TIME% rc=%RC%; starting the n=67 blind control

call :control 67 12
call :control 67 11
call :control 67 10
call :control 67 9
call :control 67 8
call :control 67 7
call :control 67 6

echo [chain] all desktop jobs reported complete %DATE% %TIME% rc=%RC%
exit /b %RC%

:job
set N=%1
set B=%2
set TRIES=0
set ONLY=%PW%\partitions\n%N%-b%B%-remaining.json
if not exist "%ONLY%" (
  echo [chain] n=%N% b=%B% REFUSED: partition file missing %ONLY%
  set RC=9
  exit /b 0
)
:retry
echo [chain] n=%N% b=%B% starting %TIME% plan=pairwise
start /low /b /wait "" "%PY%" "%RUNNER%" "%SRC%" "%PW%\pairwise-state-n%N%-b%B%.json" --tables "%PW%\tables" --n %N% --b %B% --only-shapes "%ONLY%" --wall-budget 0
set ST=%ERRORLEVEL%
echo [chain] n=%N% b=%B% exit=%ST% %TIME%
if not "%ST%"=="2" goto :notlocked
set /a TRIES+=1
if %TRIES% GEQ 12 goto :gaveup
echo [chain] n=%N% b=%B% LOCKED (attempt %TRIES%); waiting out the stale window
waitfor /t 200 ErdosLockWait >nul 2>&1
goto :retry
:gaveup
echo [chain] n=%N% b=%B% STILL LOCKED after %TRIES% attempts; leaving tier undone
set RC=2
exit /b 0
:notlocked
if not "%ST%"=="0" set RC=%ST%
exit /b 0

:control
set N=%1
set B=%2
set TRIES=0
if not exist "%PW%\tables-ext\n%N%-b%B%\tier-manifest.json" (
  echo [chain] control n=%N% b=%B% SKIPPED: no tier manifest under tables-ext
  exit /b 0
)
:cretry
echo [chain] control n=%N% b=%B% starting %TIME% plan=pairwise
start /low /b /wait "" "%PY%" "%RUNNER%" "%PW%\gpu-blast-ext" "%PW%\control-state-n%N%-b%B%.json" --tables "%PW%\tables-ext" --n %N% --b %B% --wall-budget 0
set ST=%ERRORLEVEL%
echo [chain] control n=%N% b=%B% exit=%ST% %TIME%
if not "%ST%"=="2" goto :cnotlocked
set /a TRIES+=1
if %TRIES% GEQ 12 goto :cgaveup
echo [chain] control n=%N% b=%B% LOCKED (attempt %TRIES%); waiting out the stale window
waitfor /t 200 ErdosLockWait >nul 2>&1
goto :cretry
:cgaveup
echo [chain] control n=%N% b=%B% STILL LOCKED after %TRIES% attempts; leaving tier undone
set RC=2
exit /b 0
:cnotlocked
if not "%ST%"=="0" set RC=%ST%
exit /b 0
