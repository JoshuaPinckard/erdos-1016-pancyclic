@echo off
REM Probes whether each wait primitive actually waits, under whatever launcher
REM invoked this file. Writes beside itself; %~dp0 works under every launcher.
REM Pass a tag as %1 so two launchers can be compared in one log.
set L=%~dp0console-dependency-probe.log
set TAG=%~1
if "%TAG%"=="" set TAG=untagged
echo ---- %TAG% ---- >> "%L%"
echo timeout START %TIME% >> "%L%"
timeout /t 5 /nobreak >nul 2>&1
echo timeout END   %TIME% errorlevel=%ERRORLEVEL% >> "%L%"
echo waitfor START %TIME% >> "%L%"
waitfor /t 5 ErdosProbeSig >nul 2>&1
echo waitfor END   %TIME% errorlevel=%ERRORLEVEL% >> "%L%"
echo ping    START %TIME% >> "%L%"
ping -n 6 127.0.0.1 >nul 2>&1
echo ping    END   %TIME% errorlevel=%ERRORLEVEL% >> "%L%"
