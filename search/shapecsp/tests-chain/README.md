# Chain control-flow tests

These exercise the *chain drivers*, not the GPU kernel: specifically that a
`gpu_state_runner.py` exit of 2 ("LOCKED" -- a previous instance died without
releasing its lock and the lock is not yet `--lock-stale` old) makes the driver
**retry the same tier** instead of advancing to the next one.

That bug is expensive rather than subtle. The driver used to run each tier once
and move on regardless of exit code, so a single restart inside the 180s stale
window would skip a whole tier and only return to it hours later -- measured at
about 32 GPU-hours for `n70 b10`.

`stub_runner.py` stands in for the real runner: it returns 2 the first time it
sees a given `(n, b)` and 0 thereafter, so a correct driver logs
`exit=2 -> LOCKED (attempt 1) -> exit=0 -> next tier`.

Run against the Windows driver (`run-chain-desktop-v2.cmd`) and the Linux one
(`run-chain-laptop.sh`) by pointing the driver's runner variable at the stub and
shortening its lock wait. Both were verified this way on 2026-09-16: each
retried its locked tier once, then advanced, and the Linux driver exited rc=0
after all tiers.

Both drivers cap the retry (12 attempts x 200s ~= 40min, well past the 180s
stale window) so a permanently locked tier cannot spin forever.


## console-dependency-probe

`timeout.exe` refuses to run when stdin is not a console: it exits immediately
with code 125 instead of waiting. The production launch path is exactly that --
`wscript //B` -> `WshShell.Run(..., 0, True)` -> `cmd /c` -- so a retry built on
`timeout /t 200` returned in 0.09s, every attempt elapsed inside the 180s stale
window, and the retry that was supposed to protect a tier silently did nothing.

Measured through the real launch path:

    timeout /t 5   0.09s   errorlevel=125   DID NOT WAIT
    waitfor /t 5   5.03s   errorlevel=1     waited
    ping    -n 6   5.17s   errorlevel=0     waited

The driver uses `waitfor`, which has no console dependency. Its exit 1 on
timeout is harmless: `ST` is captured further up and the next statement is an
unconditional `goto`.

Run this probe through `console-dependency-probe.vbs` (NOT by invoking the .cmd
directly) whenever a driver gains a new wait, sleep or prompt. Invoking the .cmd
from an ordinary shell gives it a console and hides the entire defect -- that is
precisely how it was missed the first time: the earlier driver test used
`Start-Process cmd.exe -RedirectStandardOutput`, which still had a console
stdin, so `timeout` worked in the test and failed in production.

**The rule this encodes: test the driver through the launcher it actually ships
with, not through a convenient shell.**
