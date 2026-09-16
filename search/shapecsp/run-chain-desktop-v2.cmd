@echo off
REM Sequential b>=10 chain for the desktop GPU.  Successor to
REM run-chain-desktop.cmd, which could not be edited in place: cmd.exe reads a
REM batch file incrementally by byte offset, so rewriting the running file
REM corrupts the run.  The wrapper VBS points here; the old file is kept only
REM because the currently-live chain is still executing it.
REM
REM Each gpu_state_runner invocation runs a whole (level, tier) to completion
REM (--wall-budget 0) and is fully resumable from its own state file, so a
REM completed job is skipped in milliseconds on a restart.
REM
REM CPU: the GPU kernel needs ~1% of one core. /low priority keeps the desktop
REM responsive for other agents' work, per the 5% desktop CPU ceiling.

setlocal
set SC=%~dp0
set PY=C:\Python313\python.exe
set RUNNER=%SC%gpu_state_runner.py
set SRC=%SC%gpu-blast
set RC=0

echo [chain] start %DATE% %TIME%

call :job 68 10
call :job 69 10
call :job 68 11
call :job 69 11

echo [chain] all desktop jobs reported complete %DATE% %TIME% rc=%RC%
exit /b %RC%

:job
set N=%1
set B=%2
set TRIES=0
:retry
echo [chain] n=%N% b=%B% starting %TIME%
start /low /b /wait "" "%PY%" "%RUNNER%" "%SRC%" "%SC%gpu-state-n%N%-b%B%.json" --n %N% --min-b %B% --max-b %B% --wall-budget 0
set ST=%ERRORLEVEL%
echo [chain] n=%N% b=%B% exit=%ST% %TIME%
REM exit 2 is "LOCKED": a previous instance died without releasing its lock and
REM the lock is not yet older than --lock-stale.  That is NOT a finished tier --
REM advancing here would silently skip a whole level for hours.  Wait out the
REM stale window and retry the SAME tier.  Bounded, so a tier that is somehow
REM permanently locked cannot spin forever: 12 x 200s is ~40min, well past the
REM 180s stale window.  No parenthesised blocks here on purpose -- %TRIES%
REM inside one would expand at parse time rather than per iteration.
if not "%ST%"=="2" goto :notlocked
set /a TRIES+=1
if %TRIES% GEQ 12 goto :gaveup
echo [chain] n=%N% b=%B% LOCKED (attempt %TRIES%); waiting out the stale window
timeout /t 200 /nobreak >nul 2>&1
goto :retry
:gaveup
echo [chain] n=%N% b=%B% STILL LOCKED after %TRIES% attempts; leaving tier undone
set RC=2
exit /b 0
:notlocked
REM Propagate a real failure so the scheduled task can see one.  The previous
REM version always exited 0, which made every failure look like success.
if not "%ST%"=="0" set RC=%ST%
exit /b 0
