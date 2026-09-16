' Self-locating launcher for console-dependency-probe.cmd.
' Self-locating on purpose: an earlier version hard-coded a path that moved, so
' the probe exited 1 with no log and no failure -- a silent skip, in the very
' artifact meant to catch silent skips. It now fails loudly if the target is
' missing, and it echoes the command it ran when the command itself fails.
Option Explicit
Dim fso, here, target, tag, sh, cmd, rc
Set fso = CreateObject("Scripting.FileSystemObject")
here = fso.GetParentFolderName(WScript.ScriptFullName)
target = here & "\console-dependency-probe.cmd"
If Not fso.FileExists(target) Then
    WScript.Echo "PROBE BROKEN: missing " & target
    WScript.Quit 2
End If
tag = "vbs"
If WScript.Arguments.Count > 0 Then tag = WScript.Arguments(0)
Set sh = CreateObject("WScript.Shell")
cmd = "cmd.exe /c " & Chr(34) & target & Chr(34) & " " & tag
rc = sh.Run(cmd, 0, True)
If rc <> 0 Then WScript.Echo "PROBE command returned " & rc & " for: " & cmd
WScript.Quit rc
