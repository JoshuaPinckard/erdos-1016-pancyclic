@echo off
REM Sequential chain for the desktop GPU.  Successor to run-chain-desktop-v6.cmd
REM (2026-09-19, pairwise cutover).  v2..v6 are left on disk untouched: cmd.exe
REM reads a batch file incrementally by byte offset.
REM
REM WHAT CHANGED
REM ------------
REM Every remaining tier now runs under the PAIRWISE plan (search\shapecsp\
REM pairwise\): the kernel enumerates only compositions that survive the
REM pairwise Hall test, which prune_pairwise.py measured at 42-47x on b=12 and
REM 10-15x on b=11 over the whole manifests.  Shapes that were already
REM exhausted under the unrestricted plan are NOT re-run: partition_tier.py
REM writes pairwise\partitions\n{N}-b{B}-remaining.json from the unrestricted
REM state file, and that list is passed as --only-shapes, so the tier's
REM exhaustion statement is  unrestricted-done shapes + pairwise-done shapes =
REM every manifest shape  (verify_tier_combined.py checks exactly that).
REM
REM The pairwise runner refuses a state file without enumeration="pairwise-v1"
REM and a matching plan hash, so an old unrestricted state can never be
REM mistaken for progress here.
REM
REM ORDER.  69/11 first (largest), then the two b=12 tiers of levels 68, 69.
REM The laptop runs 68/11, 70/11, 70/12 the same way.

setlocal
set SC=%~dp0
set PY=C:\Python313\python.exe
set PW=%SC%pairwise
set RUNNER=%PW%\gpu_state_runner_pairwise.py
set SRC=%SC%gpu-blast
set RC=0

echo [chain] start %DATE% %TIME% script=v7 plan=pairwise

call :job 69 11
call :job 68 12
call :job 69 12

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
REM exit 2 is LOCKED: retry the SAME tier after the stale window, bounded.
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
