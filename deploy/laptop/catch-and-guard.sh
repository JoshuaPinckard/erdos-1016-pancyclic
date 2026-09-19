#!/bin/bash
# Runs on the WINDOWS desktop (git-bash), detached from any agent session.
#
# The laptop's firmware powers the box off at 80 C.  Both compute units are
# WantedBy=multi-user.target, so a boot starts them before anything can cap
# them: boot -> load -> 80 C -> off, with no window to log in.  This watcher
# closes that window from the outside.  The instant ssh answers it SIGSTOPs
# the job processes (no root needed, they run as j), and only then installs
# the thermal guard and lets them run again under its caps.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
LOG="${CATCH_LOG:-$HERE/../../catch-and-guard.log}"
HOST="${CATCH_HOST:-josh}"
POLL="${CATCH_POLL:-5}"
HOURS="${CATCH_HOURS:-24}"
# Seconds to let the box settle after the install before reading temperatures
# back.  Only the tests lower it.
SETTLE="${CATCH_SETTLE:-45}"
SSH=(ssh -o BatchMode=yes -o ConnectTimeout=4 -o StrictHostKeyChecking=yes "$HOST")

log() { printf '%s %s\n' "$(date -Is)" "$*" >> "$LOG"; }
run() { "${SSH[@]}" "$1" >> "$LOG" 2>&1; }

# Match the job processes by their command lines rather than by unit, because
# systemctl kill needs root and pkill as j does not.  The leading character
# classes keep the pattern from matching the login shell that carries it: that
# shell is also owned by j, and stopping it would hang the ssh session with the
# jobs still frozen.
JOBS='[d]escend[.]py|[h]unt[.]py|[r]un-chain-laptop[.]sh|[g]pu_state_runner[.]py'
freeze_jobs() { run "pkill -STOP -u j -f '$JOBS' ; echo \"pkill -STOP rc=\$?\""; }
thaw_jobs()   { run "pkill -CONT -u j -f '$JOBS' ; echo \"pkill -CONT rc=\$?\""; }

log "watcher start pid=$$ host=$HOST poll=${POLL}s window=${HOURS}h"
deadline=$(( $(date +%s) + HOURS * 3600 ))

while [ "$(date +%s)" -lt "$deadline" ]; do
  if "${SSH[@]}" true >/dev/null 2>&1; then
    log "=== SSH UP -- freezing jobs before anything else ==="
    freeze_jobs
    log "--- state at catch ---"
    run 'uptime; nvidia-smi --query-gpu=temperature.gpu,clocks.gr,power.draw --format=csv,noheader 2>/dev/null; systemctl is-active erdos-descent erdos-laptop-chain erdos-thermal-guard 2>&1'
    log "--- why the last boot ended ---"
    run 'journalctl -b -1 --no-pager -n 30 2>/dev/null | tail -30'
    log "--- what owns the 80 C power-off ---"
    run 'systemctl list-unit-files --no-pager 2>/dev/null | grep -iE "therm|backstop" ; for f in /etc/systemd/system/*therm* /usr/local/sbin/*therm* /usr/local/bin/*therm*; do [ -e "$f" ] && { echo "== $f"; cat "$f"; }; done 2>/dev/null'

    log "--- installing guard ---"
    run 'rm -rf /tmp/erdos-guard && mkdir -p /tmp/erdos-guard/tests'
    scp -o BatchMode=yes \
      "$HERE/erdos-thermal-guard" \
      "$HERE/erdos-thermal-guard.service" \
      "$HERE/install-thermal-guard.sh" \
      "$HOST:/tmp/erdos-guard/" >> "$LOG" 2>&1
    scp -o BatchMode=yes "$HERE/tests/test-thermal-guard.sh" "$HOST:/tmp/erdos-guard/tests/" >> "$LOG" 2>&1
    if "${SSH[@]}" 'sudo -n true' >/dev/null 2>&1; then
      run 'cd /tmp/erdos-guard && chmod +x erdos-thermal-guard install-thermal-guard.sh && sudo -n bash install-thermal-guard.sh'
      log "--- guard installed; releasing the freeze ---"
      thaw_jobs
      sleep "$SETTLE"
      run 'tail -8 /home/j/erdos-thermal-guard.log 2>/dev/null; nvidia-smi --query-gpu=temperature.gpu,clocks.gr --format=csv,noheader 2>/dev/null; systemctl is-active erdos-thermal-guard erdos-descent erdos-laptop-chain 2>&1'
      log "=== DONE: guard running, jobs under caps ==="
    else
      # Without root the guard cannot be installed, so the jobs stay stopped.
      # A frozen job loses nothing: both resume from their on-disk ledgers.
      log "!!! no passwordless sudo -- jobs LEFT FROZEN, guard NOT installed"
      run 'systemctl is-enabled erdos-descent erdos-laptop-chain 2>&1'
      log "=== HELD: laptop is safe but idle; needs a root install ==="
    fi
    exit 0
  fi
  sleep "$POLL"
done
log "watcher window expired without ever reaching $HOST"
