@echo off
REM Sequential b>=10 chain for the desktop GPU.
REM Each gpu_state_runner invocation runs a whole (level, tier) to completion
REM (--wall-budget 0) and is fully resumable from its own state file, so a
REM completed job is skipped in milliseconds on a restart. The scheduled task
REM that calls this re-runs it if it dies; the chain then resumes where it was.
REM
REM CPU: the GPU kernel needs ~1% of one core. /low priority keeps the desktop
REM responsive for other agents' work, per the 5% desktop CPU ceiling.

setlocal
set SC=%~dp0
set PY=C:\Python313\python.exe
set RUNNER=%SC%gpu_state_runner.py
set SRC=%SC%gpu-blast

echo [chain] start %DATE% %TIME%

call :job 68 10
call :job 69 10
call :job 68 11
call :job 69 11

echo [chain] all desktop jobs reported complete %DATE% %TIME%
exit /b 0

:job
set N=%1
set B=%2
echo [chain] n=%N% b=%B% starting %TIME%
start /low /b /wait "" "%PY%" "%RUNNER%" "%SRC%" "%SC%gpu-state-n%N%-b%B%.json" --n %N% --min-b %B% --max-b %B% --wall-budget 0
echo [chain] n=%N% b=%B% exit=%ERRORLEVEL% %TIME%
exit /b 0
