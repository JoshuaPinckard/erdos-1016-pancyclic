' Detached hidden launcher for the bounded-unrank scratch build.
' Same pattern as run-hidden-gpu-state-runner.vbs: WshShell.Run with window
' style 0.  bWaitOnReturn is False here on purpose -- the caller's shell can be
' torn down without taking the measurement or the scratch GPU run with it.
' Usage: wscript //B detach.vbs "<full command line with its own redirections>"
Dim sh: Set sh = CreateObject("WScript.Shell")
sh.Run "cmd /c " & WScript.Arguments(0), 0, False
