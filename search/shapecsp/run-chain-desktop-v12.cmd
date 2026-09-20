@echo off
REM v12 (2026-09-19 20:20): byte-identical to v11 except for the version echo and
REM CRLF LINE ENDINGS.  v11 was LF-only and cmd.exe's label search failed on it mid-run
REM (chain-desktop.log 20:13:42: 'The system cannot find the batch label specified - job'),
REM skipping the 68/12 job.  Every chain file must be CRLF.
REM Sequential chain for the desktop GPU.  Successor to run-chain-desktop-v11.cmd
REM (2026-09-19).  v2..v10 are left on disk untouched: cmd.exe reads a batch
REM file incrementally by byte offset.
REM
REM IDENTICAL to v10 through levels 89 and 88.  The one addition: interleaved
REM descent of the even levels 86, 84, 82, 80, 78, 76, 74, 72 (the desktop's
REM half of the 72..87 gap; the laptop runs the odd half in
REM run-chain-laptop-v9.sh), through the existing :ext routine, each b=12..6,
REM tables under pairwise\tables-ext (built locally from pairwise-prod via
REM pairwise\_mgr-build-even-72-86.cmd -- the laptop's npz files are not on
REM this machine).  Missing manifests are skipped with a log line by :ext
REM itself.  Descending order across both machines together means the first
REM hit -- if any -- settles t_6 as early in wall-clock time as the two
REM machines can reach it, instead of each clearing its own block bottom-up.

setlocal
set SC=%~dp0
set PY=C:\Python313\python.exe
set PW=%SC%pairwise
set RUNNER=%SC%pairwise-prod\gpu_state_runner_pairwise.py
set SRC=%SC%gpu-blast
set RC=0

echo [chain] start %DATE% %TIME% script=v12 plan=pairwise runner=pairwise-prod

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

echo [chain] levels 89/88 reported complete %DATE% %TIME% rc=%RC%; starting interleaved descent 86..72 (even)

call :ext 86 12
call :ext 86 11
call :ext 86 10
call :ext 86 9
call :ext 86 8
call :ext 86 7
call :ext 86 6
call :ext 84 12
call :ext 84 11
call :ext 84 10
call :ext 84 9
call :ext 84 8
call :ext 84 7
call :ext 84 6
call :ext 82 12
call :ext 82 11
call :ext 82 10
call :ext 82 9
call :ext 82 8
call :ext 82 7
call :ext 82 6
call :ext 80 12
call :ext 80 11
call :ext 80 10
call :ext 80 9
call :ext 80 8
call :ext 80 7
call :ext 80 6
call :ext 78 12
call :ext 78 11
call :ext 78 10
call :ext 78 9
call :ext 78 8
call :ext 78 7
call :ext 78 6
call :ext 76 12
call :ext 76 11
call :ext 76 10
call :ext 76 9
call :ext 76 8
call :ext 76 7
call :ext 76 6
call :ext 74 12
call :ext 74 11
call :ext 74 10
call :ext 74 9
call :ext 74 8
call :ext 74 7
call :ext 74 6
call :ext 72 12
call :ext 72 11
call :ext 72 10
call :ext 72 9
call :ext 72 8
call :ext 72 7
call :ext 72 6

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
