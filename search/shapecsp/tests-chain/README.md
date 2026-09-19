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

**What this probe actually measures: the launcher, not the command.** Whether a
wait primitive waits depends on how the process was started, and getting that
wrong produced two wrong conclusions in a row here -- in both directions.

Same file, two launchers, measured 2026-09-16:

    launcher                       timeout /t 5        waitfor /t 5    ping -n 6
    ---------------------------------------------------------------------------
    from a shell (bash/pwsh)       errorlevel=125      errorlevel=1    errorlevel=0
                                   REFUSED, 0.36s      waited          waited
    from the Task Scheduler        errorlevel=0        errorlevel=1    errorlevel=0
                                   WAITED              waited          waited
    (scheduler confirmed twice)

`timeout.exe` refuses to run when stdin is not a console. A shell hands its
redirected stdin down the entire chain -- `bash`/`pwsh` -> `wscript` -> `cmd` --
so `timeout` refuses there. The Task Scheduler does not, so `timeout` waits.

**Read the exit codes, not the durations.** Under load the nominal 5s intervals
inflated to 40s+; that is the saturated box, not semantics. `errorlevel=125`
versus `errorlevel=0` is the measurement.

### Which launcher is production

For `run-chain-desktop-v2.cmd` it is the **Task Scheduler**
(`Erdos1016-desktop-chain`). Running the driver through `wscript` typed at a
shell is NOT a faithful reproduction: it adds a redirected stdin that production
never has. So `timeout /t 200` would in fact have waited in production, and the
"desktop skips the tier" finding was an artifact of testing through a shell.

The driver nonetheless uses `waitfor`, and should keep using it: it waits under
**both** launchers, so it does not depend on which one starts it. `timeout` only
works where a console exists. Its exit 1 on timeout is harmless -- `ST` is
captured further up and the next statement is an unconditional `goto`.

### Running it

    wscript //B //Nologo console-dependency-probe.vbs <tag>

The `.vbs` self-locates the `.cmd` beside it and fails loudly if it is missing.
An earlier version hard-coded a path that moved, so it exited 1 with no log and
no failure -- a silent skip, in the artifact meant to catch silent skips.

To reproduce the production arm, register a throwaway scheduled task pointing at
the same `.vbs` with tag `scheduler`; both arms append to one log so they can be
compared directly. Remove the throwaway task afterwards.

**The rule this encodes: exercise a driver through the launcher it actually
ships with.** On Windows that means the Task Scheduler, and "through wscript
from my shell" is a different environment that can fail and pass for reasons
production never sees -- in both directions.

## b=12 job list (2026-09-19)

`run-chain-desktop-v3.cmd` (6 tiers: 68/10, 69/10, 68/11, 69/11, 68/12, 69/12)
and `run-chain-laptop-v2.sh` (70/10, 70/11, 70/12) re-ran this stub test with
`LOCK_WAIT` shortened. Both are green: each of the nine tiers logged
`exit=2 -> LOCKED (attempt 1) -> exit=0`, advanced in list order, and the
drivers exited `rc=0`. Test logs are `*.log`, which `.gitignore` excludes.
