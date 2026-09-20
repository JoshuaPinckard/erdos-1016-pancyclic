@echo off
REM Sequential chain for the desktop GPU.  Successor to run-chain-desktop-v9.cmd
REM (2026-09-19).  v2..v9 are left on disk untouched: cmd.exe reads a batch
REM file incrementally by byte offset.
REM
REM Same jobs as v9 (production tiers resumed from their state files, then the
REM n=67 blind control), then LEVELS 89 AND 88 under the pairwise plan from the
REM census manifests pairwise\gpu-blast-ext\n{89,88}.jsonl and tables under
REM pairwise\tables-ext (built here from the frozen module).  The CPU descent
REM already verified both levels UNSAT (REPORT-k6-level89-91-verify.md), so a
REM zero-hit exhaustion here is an independent GPU-pipeline cross-check of that
REM result, and a hit would falsify one of the two.  Whole-tier state files
REM pairwise-state-n{N}-b{B}.json, no --only-shapes.  Runner and modules come
REM from pairwise-prod\ (frozen snapshot of pairwise\ at commit f63f9f3).

setlocal
set SC=%~dp0
set PY=C:\Python313\python.exe
set PW=%SC%pairwise
set RUNNER=%SC%pairwise-prod\gpu_state_runner_pairwise.py
set SRC=%SC%gpu-blast
set RC=0

echo [chain] start %DATE% %TIME% script=v10 plan=pairwise runner=pairwise-prod

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

echo [chain] control reported complete %DATE% %TIME% rc=%RC%; starting levels 89 and 88

call :ext 89 12
call :ext 89 11
call :ext 89 10
call :ext 89 9
call :ext 88 12
call :ext 88 11
call :ext 88 10
call :ext 88 9

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

:ext
set N=%1
set B=%2
set TRIES=0
if not exist "%PW%\tables-ext\n%N%-b%B%\tier-manifest.json" (
  echo [chain] n=%N% b=%B% SKIPPED: no tier manifest under tables-ext
  exit /b 0
)
:eretry
echo [chain] n=%N% b=%B% starting %TIME% plan=pairwise source=gpu-blast-ext
start /low /b /wait "" "%PY%" "%RUNNER%" "%PW%\gpu-blast-ext" "%PW%\pairwise-state-n%N%-b%B%.json" --tables "%PW%\tables-ext" --n %N% --b %B% --wall-budget 0
set ST=%ERRORLEVEL%
echo [chain] n=%N% b=%B% exit=%ST% %TIME%
if not "%ST%"=="2" goto :enotlocked
set /a TRIES+=1
if %TRIES% GEQ 12 goto :egaveup
echo [chain] n=%N% b=%B% LOCKED (attempt %TRIES%); waiting out the stale window
waitfor /t 200 ErdosLockWait >nul 2>&1
goto :eretry
:egaveup
echo [chain] n=%N% b=%B% STILL LOCKED after %TRIES% attempts; leaving tier undone
set RC=2
exit /b 0
:enotlocked
if not "%ST%"=="0" set RC=%ST%
exit /b 0
