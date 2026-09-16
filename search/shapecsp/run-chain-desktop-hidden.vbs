' Hidden-window wrapper for scheduled task Erdos1016-desktop-chain.
' Rule 2026-09-16: agent programs must not put a window on the
' screen, because a surfacing console steals clicks from other agents driving
' the desktop UI.  Runs the identical chain with window style 0 and waits, so
' the scheduled task still sees the chain's real exit code.
Dim sh: Set sh = CreateObject("WScript.Shell")
Dim cmd: cmd = "cmd.exe /c """"C:\Users\ToolsEnabled-Dev\Desktop\erdos1016\search\shapecsp\run-chain-desktop-v2.cmd"""""
WScript.Quit sh.Run(cmd, 0, True)
