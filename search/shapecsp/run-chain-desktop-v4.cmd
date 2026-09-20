@echo off
REM Sequential b>=11 chain for the desktop GPU, after the 2026-09-19 rebalance.
REM
REM Successor to run-chain-desktop-v3.cmd, which could not be edited in place:
REM cmd.exe reads a batch file incrementally by byte offset, so rewriting the
REM running file corrupts the run.  v2 and v3 are kept only because a live
REM chain may still be executing one of them.
REM
REM WHAT CHANGED FROM v3, AND WHY
REM -----------------------------
REM v3 ran 68/10, 69/10, 68/11, 69/11, 68/12, 69/12 -- both of levels 68 and 69
REM entirely -- while the laptop ran level 70 alone.  By manifest totals that
REM left this machine about 1.26e15 ranks against the laptop's 6.8e14, so this
REM machine was the critical path by about four days while the laptop would
REM have idled.
REM
REM The rebalance is a SWAP, not a one-way move:
REM     69/11  desktop -> laptop   (this script loses it)
REM     70/11  laptop  -> desktop  (this script gains its remainder)
REM Measured rates, not assumed ones, are what force the swap.  This card is an
REM RTX 5060 Ti at 2092 MHz / 72.5 W; the laptop is an RTX 4070 Laptop held at
REM 1395 MHz / 39 W by its thermal guard.  This machine is about 1.29x the
REM laptop in ranks/hour.  Handing 69/11 (3.24e14 ranks) over without taking
REM anything back overshoots: it makes the LAPTOP the critical path and lands
REM the proof later than changing nothing.  Taking 70/11's remainder (2.21e14
REM ranks) back is what turns the move into a real saving.  The measurements
REM and the arithmetic are in REPORT-rebalance.md.
REM
REM 68/10 and 69/10 are gone from the list because they are complete
REM (2302/2302 and 2188/2188 units).  A completed tier is skipped in
REM milliseconds anyway, so this is tidiness, not behaviour.
REM
REM 70/11 runs here against gpu-blast\n70.jsonl, which is already present and
REM whose sha256 (a7c01425...) matches the laptop's byte for byte.  Its state
REM file gpu-state-n70-b11.json was produced on the laptop and copied here; the
REM unit plan is derived from the hashed manifest, not from the machine, so the
REM transplanted progress is resumed rather than repeated.
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

echo [chain] start %DATE% %TIME% script=v4

call :job 68 11
call :job 70 11
call :job 68 12
call :job 69 12

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
REM NOT timeout.exe: it refuses to run when stdin is not a console and exits
REM immediately with 125.  The production launch path is exactly that --
REM wscript //B -> WshShell.Run(window style 0) -> cmd /c -- so `timeout /t
REM 200` returned in 0.09s and every retry elapsed inside the 180s stale
REM window, silently defeating the whole retry.  waitfor has no console
REM dependency; it exits 1 on timeout, harmless because ST was captured
REM above and the next statement is an unconditional goto.
waitfor /t 200 ErdosLockWait >nul 2>&1
goto :retry
:gaveup
echo [chain] n=%N% b=%B% STILL LOCKED after %TRIES% attempts; leaving tier undone
set RC=2
exit /b 0
:notlocked
REM Propagate a real failure so the scheduled task can see one.  The original
REM version always exited 0, which made every failure look like success.
if not "%ST%"=="0" set RC=%ST%
exit /b 0
