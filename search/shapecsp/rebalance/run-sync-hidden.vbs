' Hidden-window wrapper for scheduled task Erdos1016-sync-from-laptop.
'
' Same rule as the chain's wrapper: an agent program must not put a window on
' the screen, because a surfacing console steals clicks from other agents
' driving the desktop UI.  Window style 0, and bWaitOnReturn True so the
' scheduled task's Last Result is the sync's real exit code rather than 0.
'
' The ssh destination is NOT written here.  It is configuration and belongs in
' the scheduled task registration, which passes it as the first argument.
' Usage: wscript //B run-sync-hidden.vbs <ssh-destination>
If WScript.Arguments.Count < 1 Then
    ' Fail loudly.  Last Result is the only place anyone sees this, and exiting
    ' 0 with nothing done would look exactly like a successful sync.
    WScript.Quit 2
End If

Dim fso: Set fso = CreateObject("Scripting.FileSystemObject")
Dim here: here = fso.GetParentFolderName(WScript.ScriptFullName)
Dim ps1: ps1 = fso.BuildPath(here, "sync-from-laptop.ps1")
Dim log: log = fso.BuildPath(here, "sync-from-laptop.log")
If Not fso.FileExists(ps1) Then WScript.Quit 3

Dim cmd
cmd = "cmd.exe /c powershell -NoProfile -ExecutionPolicy Bypass -File """ & ps1 & _
      """ -Remote " & WScript.Arguments(0) & " >>""" & log & """ 2>&1"

Dim sh: Set sh = CreateObject("WScript.Shell")
WScript.Quit sh.Run(cmd, 0, True)
