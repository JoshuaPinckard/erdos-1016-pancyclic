' Hidden-window wrapper for scheduled task Erdos1016-desktop-chain.
'
' Rule 2026-09-16: agent programs must not put a window on the
' screen, because a surfacing console steals clicks from other agents driving
' the desktop UI.  Runs the chain with window style 0 and waits, so the
' scheduled task still sees the chain's real exit code.
'
' 2026-09-19 third split: launches v6.  This machine runs 69/11 and the two
' b=12 tiers of levels 68 and 69; the laptop takes 68/11, 70/11 and 70/12.
' v4 and v5 were priced with a single ranks/hour per machine, which is wrong:
' a b=12 rank costs about 1.27x a b=11 rank, measured within a level on both
' cards (n69: desktop 57.38/43.43, laptop 77.81/60.98).  There is NOT a large
' level effect -- an earlier claim of 27% between n69 b11 and n70 b11 was
' confounded by clock history, since n70 b11's units span days before the fan
' pin and thermal guard settled the laptop at 1395 MHz.  Measured inside one
' regime, n68 b11 (61.88) and n69 b11 (60.98) differ by 1.5%.
' v3..v5 are left on disk untouched because cmd.exe reads a batch file
' incrementally by byte offset.
'
' 2026-09-19 LOGGING.  Until now the chain's stdout went nowhere -- this wrapper
' ran cmd /c with no redirect -- so the desktop had no equivalent of the
' laptop's chain-laptop.log and no per-unit timing history at all.  A 22 h
' average plus a spot check cannot settle a 1.6-1.9x kernel claim, so the
' redirect lives HERE rather than in the chain script: the wrapper is not being
' read while the chain runs, every future chain version inherits logging
' without another edit, and turning it on costs one restart instead of a new
' vN file.
'
' The chain path and the log path are both derived from this wrapper's own
' location, so moving or copying the repository cannot leave the scheduled task
' driving -- or logging into -- the old checkout.
Option Explicit

Const MAX_LOG_BYTES = 67108864   ' 64 MiB; one .1 generation kept => 128 MiB ceiling

Dim fso: Set fso = CreateObject("Scripting.FileSystemObject")
Dim here: here = fso.GetParentFolderName(WScript.ScriptFullName)
Dim chain: chain = fso.BuildPath(here, "run-chain-desktop-v12.cmd")
Dim launcher: launcher = fso.BuildPath(here, "run-chain-desktop-logged.cmd")
Dim logPath: logPath = fso.BuildPath(here, "chain-desktop.log")
Dim oldPath: oldPath = logPath & ".1"

' BENCHMARK WINDOW.  rebalance/benchmark-window.ps1 takes the GPU for a bounded
' period by writing a marker here; while it is live this wrapper declines to
' start the chain.  The scheduled task repeats every 5 minutes with
' MultipleInstancesPolicy IgnoreNew, so suppressing HERE is strictly better than
' disabling the task: the task keeps firing, and the moment the marker is gone
' or expired the chain comes back on its own within 5 minutes even if the window
' script was killed.  Disabling the task instead would leave the chain dead
' across a reboot, which is the failure this design exists to avoid.
'
' Expiry is judged from the marker's OWN modification time plus the cap on its
' first line, both read through the same local clock.  No timestamp is parsed
' and no timezone is converted, because a marker that cannot be interpreted
' must not be able to suppress the chain forever.  An unreadable or malformed
' marker is treated as EXPIRED, deliberately: the failure direction is "the
' chain runs when it maybe should not" (costing a contended benchmark) rather
' than "the chain stays down" (costing days).
' The marker lives beside benchmark-window.ps1, in rebalance/, NOT beside this
' wrapper.  The first version of this check looked in the wrapper's own folder
' while the tool wrote it one directory down, so suppression silently never
' fired and a benchmark would have run against a live chain -- the exact
' contention the window exists to prevent, with a green log either side of it.
Dim marker: marker = fso.BuildPath(fso.BuildPath(here, "rebalance"), "benchmark-window.active")
If fso.FileExists(marker) Then
    Dim capMin: capMin = 0
    On Error Resume Next
    Dim ts: Set ts = fso.OpenTextFile(marker, 1)
    If Err.Number = 0 Then
        If Not ts.AtEndOfStream Then capMin = CLng(Trim(ts.ReadLine))
        ts.Close
    End If
    Dim ageMin: ageMin = DateDiff("n", fso.GetFile(marker).DateLastModified, Now)
    If Err.Number <> 0 Then capMin = 0   ' unreadable => treat as expired
    Err.Clear
    On Error GoTo 0
    If capMin > 0 And ageMin < capMin Then
        ' Distinct code so the task's Last Result says "suppressed", not "failed".
        WScript.Quit 7
    End If
End If

If Not fso.FileExists(launcher) Then WScript.Quit 6
If Not fso.FileExists(chain) Then
    ' Fail loudly rather than returning 0: the scheduled task's Last Result is
    ' the only place anyone sees this, and a silent success here would look
    ' exactly like a completed chain.
    WScript.Quit 3
End If

' Roll the log before launching, not during: one chain invocation runs for days,
' so a size check inside the run would need the chain's cooperation.  At the
' desktop's measured ~85 units/h and ~120 bytes per unit line this reaches only
' a few MiB over a 13-day run, so the cap is a backstop against a pathological
' retry loop rather than an expected event.  Exactly one previous generation is
' kept, which bounds total log bytes at 2 x MAX_LOG_BYTES.
On Error Resume Next
If fso.FileExists(logPath) Then
    If fso.GetFile(logPath).Size > MAX_LOG_BYTES Then
        If fso.FileExists(oldPath) Then fso.DeleteFile oldPath, True
        fso.MoveFile logPath, oldPath
    End If
End If
' A rotation failure must not stop the chain: losing timing data is far cheaper
' than losing a day of GPU work, so the error is cleared and the run proceeds.
Err.Clear
On Error GoTo 0

Dim sh: Set sh = CreateObject("WScript.Shell")

' cmd.exe /c "<launcher>" "<chain>"
'
' NO redirection operator crosses this boundary, deliberately.  WshShell.Run
' does not hand its argument to a shell for parsing; it CreateProcess-es cmd.exe
' and passes the remainder through, and cmd's outer-quote-stripping rule then
' mangles a command that mixes quoted paths with a redirect.  Measured: building
' the redirect here returned 1 and created no log file at all, while the byte-
' identical text typed at a prompt wrote the log correctly.  The redirect
' therefore lives inside run-chain-desktop-logged.cmd, where cmd parses
' normally; this line passes only two quoted paths.
'
' The whole command is ALSO wrapped in an outer quote pair with /s.  cmd strips
' the first and last quote of the string after /c only under a narrow rule
' (roughly: exactly two quotes, no special characters, quoted text names an
' executable).  Two quoted paths means four quotes, the rule does not apply, and
' cmd leaves the string alone -- measured, that form returns 1 and does nothing,
' while the byte-identical text typed at a prompt works.  /s with an outer pair
' makes the strip unconditional, which is the documented way to pass a command
' whose arguments are themselves quoted.  Verified: this form rc=0 and the log
' is written; the unwrapped form rc=1 and no file appears.
'
' Chr(34) rather than counted doubled quotes: the escaping is what went wrong,
' so it is named instead of counted.
Dim Q: Q = Chr(34)
Dim cmdLine
cmdLine = "cmd.exe /s /c " & Q & Q & launcher & Q & " " & Q & chain & Q & Q

WScript.Quit sh.Run(cmdLine, 0, True)
