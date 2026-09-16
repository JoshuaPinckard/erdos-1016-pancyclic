' Hidden-window wrapper for scheduled task Erdos1016-quiet-watchdog.
' Rule: agent programs must not put a window on the screen, because a
' surfacing console steals clicks from other agents driving the desktop UI.
' Runs the watchdog with window style 0 and waits, so the task sees its real
' exit code.
Dim sh: Set sh = CreateObject("WScript.Shell")
Dim cmd: cmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""C:\Users\ToolsEnabled-Dev\Desktop\erdos1016\search\shapecsp\quiet-window.ps1"" -Action Watchdog"
WScript.Quit sh.Run(cmd, 0, True)
