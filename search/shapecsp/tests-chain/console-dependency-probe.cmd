@echo off
set L=%~dp0probe.log
echo timeout START %TIME% > "%L%"
timeout /t 5 /nobreak >nul 2>&1
echo timeout END   %TIME% errorlevel=%ERRORLEVEL% >> "%L%"
echo waitfor START %TIME% >> "%L%"
waitfor /t 5 ErdosProbeSig >nul 2>&1
echo waitfor END   %TIME% errorlevel=%ERRORLEVEL% >> "%L%"
echo ping    START %TIME% >> "%L%"
ping -n 6 127.0.0.1 >nul 2>&1
echo ping    END   %TIME% errorlevel=%ERRORLEVEL% >> "%L%"
