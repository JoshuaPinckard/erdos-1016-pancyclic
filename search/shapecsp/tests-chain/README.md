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
