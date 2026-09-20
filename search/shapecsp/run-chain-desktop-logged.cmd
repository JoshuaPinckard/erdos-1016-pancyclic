@echo off
REM Thin logging launcher for the desktop chain.
REM
REM WHY THIS FILE EXISTS
REM The redirect cannot live in the VBS wrapper's command string.  WshShell.Run
REM does not hand its argument to a shell for parsing -- it CreateProcess-es
REM cmd.exe and passes the rest through -- and cmd's rule for stripping the
REM outer quote pair then mangles a command that contains BOTH quoted paths and
REM a redirection operator.  Measured: the identical text works typed at a
REM prompt and writes the log, but through WshShell.Run it returns 1 and creates
REM no file at all (test E, rebalance/ bisect).  Keeping every redirection
REM operator on this side of that boundary is what makes it reliable: the VBS
REM now passes only two quoted paths and no operators.
REM
REM The chain script is %1 so a version bump touches the VBS and nothing here --
REM this file is itself read incrementally by cmd.exe while it runs, so it must
REM not need editing mid-run.
REM
REM The log is written beside this script, and %~dp0 already ends in a
REM backslash, so there is no separator between it and the file name.
setlocal
if "%~1"=="" (
  REM Fail loudly: an empty target would otherwise redirect nothing into the log
  REM and exit 0, which reads as a completed chain.
  echo [logged] no chain script given
  exit /b 4
)
if not exist "%~1" (
  echo [logged] chain script not found: %~1
  exit /b 5
)
call "%~1" >> "%~dp0chain-desktop.log" 2>&1
exit /b %ERRORLEVEL%
