@echo off
REM Sequential chain for the desktop GPU.  Successor to run-chain-desktop-v4.cmd
REM (2026-09-19, second rebalance).  v2/v3/v4 are left on disk untouched: cmd.exe
REM reads a batch file incrementally by byte offset, so rewriting a file that a
REM live chain may still be executing corrupts the run.
REM
REM WHAT CHANGED FROM v4, AND WHY
REM -----------------------------
REM v4 ran 68/11, 70/11, 68/12, 69/12 and gave 69/11 to the laptop.  That was a
REM correction to v3 but not the best correction.  Enumerating all 64 whole-job
REM assignments of the six outstanding tiers across the two measured rates
REM (desktop 3.6177e12 ranks/h, laptop 2.7973e12) puts v4's split at 320.5 h and
REM this one at 307.2 h -- 13.3 h better, and within 4.7 h of the 302.5 h
REM fractional bound.  See rebalance/enumeration-20260919.txt.
REM
REM The rule that falls out of the enumeration: every b=11 REMAINDER belongs on
REM the faster card and the laptop takes whole b=12 tiers.  So this machine now
REM owns all three b=11 tiers and the laptop owns 69/12 + 70/12.  The single
REM tier that changed sides versus v4 is 69/11 (laptop -> here); 69/12 went the
REM other way.  4.02e14 > 3.24e14 is what makes that the balancing swap.
REM
REM ORDER.  The three b=11 tiers run first, so "no 6-chord pancyclic graph with
REM b<=11" is established at n=68, 69 AND 70 together at about hour 206 rather
REM than being gated behind this machine's b=12 work.  68/12 is last because
REM nothing else depends on it.
REM
REM MIGRATED STATE.  gpu-state-n69-b11.json and gpu-state-n70-b11.json were both
REM produced on the laptop and copied here.  A state file is machine-independent
REM by construction -- gpu_state_runner.py regenerates the unit plan from the
REM hashed manifest and binds source_sha256 into the state -- and n69.jsonl and
REM n70.jsonl are byte-identical on both machines.  Both were probed with
REM --wall-budget 1 before this script was started and each advanced from the
REM laptop's count by exactly one, NOT from zero.  A silent restart-from-zero on
REM a migrated partial is the one failure here that would look like success, and
REM it would cost about 80 hours.
REM
REM Each gpu_state_runner invocation runs a whole (level, tier) to completion
REM (--wall-budget 0) and is fully resumable from its own state file, so a
REM completed job is skipped in milliseconds on a restart.
REM
REM CPU: the GPU kernel needs ~1% of one core; measured at 0.067% of this
REM machine.  /low priority keeps the desktop responsive for other agents' work,
REM per the 5% desktop CPU ceiling.

setlocal
set SC=%~dp0
set PY=C:\Python313\python.exe
set RUNNER=%SC%gpu_state_runner.py
set SRC=%SC%gpu-blast
set RC=0

echo [chain] start %DATE% %TIME% script=v5

call :job 68 11
call :job 69 11
call :job 70 11
call :job 68 12

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
