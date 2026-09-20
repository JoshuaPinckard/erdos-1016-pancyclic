@echo off
REM Sequential chain for the desktop GPU.  Successor to run-chain-desktop-v5.cmd
REM (2026-09-19, third split).  v2..v5 are left on disk untouched: cmd.exe reads
REM a batch file incrementally by byte offset.
REM
REM WHY A THIRD SPLIT
REM -----------------
REM v4 and v5 were both chosen with a model that priced work in RANKS and gave
REM each machine one rate.  That model is wrong.  A rank is not a constant
REM amount of work: measured on the laptop over full 5e10-rank units only,
REM median GPU seconds per unit were
REM     n70 b10  42.05  (1069 units)
REM     n70 b11  48.00  (2253 units)
REM     n69 b11  60.98  (13 units)
REM     n69 b12  77.75  (11 units)
REM so cost rises with the tier AND with the level -- n69 b11 costs 27% more per
REM rank than n70 b11 at the same b.  v5's split put both remaining b=12 tiers
REM on the slower card, which the corrected model prices at about 390 h against
REM roughly 357 h for this one.
REM
REM WHY THIS SPLIT AND NOT THE NOMINAL OPTIMUM
REM ------------------------------------------
REM The b=12 cost multiplier is not pinned down: matched-level desktop probes
REM give 1.28, the laptop's median-of-medians gives 1.43, and the n=69 figures
REM rest on 11-13 units.  Rather than tune to one number, all 64 whole-job
REM splits were ranked at 1.25, 1.28, 1.32, 1.36, 1.40 and 1.43 and scored by
REM worst-case regret against the best split at each point.  Laptop =
REM {68/11, 70/11, 70/12} has a worst-case regret of 2.3 h across that whole
REM range; the next best is 11 h.  It is chosen for being insensitive to the
REM number we are least sure of, not for winning at any single value.
REM See rebalance/enumeration-costweighted-20260919.txt.
REM
REM So this machine takes 69/11 and the two b=12 tiers of levels 68 and 69; the
REM laptop takes the two cheap b=11 remainders and 70/12.  The expensive work
REM belongs on the faster card.
REM
REM ORDER.  69/11 first: it is this machine's only b=11 remainder, and the
REM laptop's two b=11 tiers finish at about hour 150, so running it first closes
REM "b<=11 exhausted at n=68, 69 and 70" as early as the split allows.
REM
REM MIGRATED STATE.  gpu-state-n69-b12.json comes from the laptop; 68/11 and
REM 70/11 go the other way.  A state file is machine-independent by construction
REM -- gpu_state_runner.py regenerates the unit plan from the hashed manifest and
REM binds source_sha256 into the state -- and n68/n69/n70.jsonl are byte-identical
REM on both machines.  Every migrated tier is probed with --wall-budget 1 before
REM this script starts and must advance from the source machine's count by
REM exactly one, NOT from zero.  A silent restart-from-zero on a migrated partial
REM is the one failure here that would look like success.
REM
REM Each gpu_state_runner invocation runs a whole (level, tier) to completion
REM (--wall-budget 0) and is fully resumable from its own state file.
REM
REM CPU: measured at 0.067% of this machine.  /low priority keeps the desktop
REM responsive for other agents' work, per the 5% desktop CPU ceiling.

setlocal
set SC=%~dp0
set PY=C:\Python313\python.exe
set RUNNER=%SC%gpu_state_runner.py
set SRC=%SC%gpu-blast
set RC=0

echo [chain] start %DATE% %TIME% script=v6

call :job 69 11
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
