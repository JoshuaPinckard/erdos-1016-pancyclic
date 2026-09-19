#!/bin/bash
# Behavioural tests for erdos-thermal-guard.  Runs anywhere bash runs -- no GPU,
# no systemd, no root: nvidia-smi and systemctl are replaced by stubs on PATH
# and the hwmon reader is pointed at a fixture tree via HWMON_GLOB.
#
# What is under test is the decision the guard makes, i.e. exactly when it sends
# SIGSTOP and SIGCONT, because that is the whole safety property: the laptop
# powers off at 80 C and the guard is the only thing that keeps the load under
# it.
set -u

GUARD="$(cd "$(dirname "$0")/.." && pwd)/erdos-thermal-guard"
[ -x "$GUARD" ] || { echo "no guard at $GUARD"; exit 1; }

pass=0; fail=0
ok()   { pass=$((pass+1)); printf 'ok   %s\n' "$1"; }
bad()  { fail=$((fail+1)); printf 'FAIL %s\n     %s\n' "$1" "${2:-}"; }

# Each case gets a private sandbox: stub binaries, a fixture sensor tree and a
# guard log.  set_gpu/set_cpu rewrite what the stubs report while it runs.
setup() {
  T=$(mktemp -d); export T
  mkdir -p "$T/bin" "$T/sensors"
  cat > "$T/bin/nvidia-smi" <<'STUB'
#!/bin/bash
case "$*" in
  *-lgc*|*-rgc*) exit 0 ;;
esac
if [ -f "$T/gpu" ]; then cat "$T/gpu"; else exit 1; fi
STUB
  cat > "$T/bin/systemctl" <<'STUB'
#!/bin/bash
printf '%s\n' "$*" >> "$T/actions"
STUB
  # timeout(1) is absent on some minimal images; the guard only uses it to bound
  # nvidia-smi, so a pass-through keeps the test honest about the rest.
  command -v timeout >/dev/null 2>&1 || cat > "$T/bin/timeout" <<'STUB'
#!/bin/bash
shift
exec "$@"
STUB
  chmod +x "$T"/bin/*
  : > "$T/actions"
  PATH="$T/bin:$PATH"; export PATH
}
teardown() { [ -n "${GPID:-}" ] && kill "$GPID" 2>/dev/null; wait "$GPID" 2>/dev/null; rm -rf "$T"; GPID=""; }

set_gpu()   { printf '%s\n' "$1" > "$T/gpu"; }
unset_gpu() { rm -f "$T/gpu"; }
# millidegrees, as sysfs reports them
set_cpu()   { printf '%s\n' "$(( $1 * 1000 ))" > "$T/sensors/temp1_input"; }
unset_cpu() { rm -f "$T/sensors"/*; }
raw_cpu()   { printf '%s\n' "$1" > "$T/sensors/temp1_input"; }

start_guard() {
  HWMON_GLOB="$T/sensors/*" GUARD_LOG="$T/guard.log" POLL=1 \
    GUARD_UNITS="unit-a.service unit-b.service" "$GUARD" &
  GPID=$!
}

# Wait up to 6 s for a predicate rather than sleeping a fixed time.
await() {
  local i=0
  while [ $i -lt 60 ]; do eval "$1" && return 0; sleep 0.1; i=$((i+1)); done
  return 1
}
# grep -c prints 0 AND exits 1 when there is no match, so an `|| echo 0`
# fallback would emit the count twice.  Capture, then default.
count() { local n; n=$(grep -c "$1" "$T/actions" 2>/dev/null); echo "${n:-0}"; }
stops()  { count 'SIGSTOP'; }
conts()  { count 'SIGCONT'; }

# ---------------------------------------------------------------- 1. cool idle
setup; set_gpu 55; set_cpu 50; start_guard
sleep 2
if [ "$(stops)" = "0" ]; then ok "cool box is never frozen"
else bad "cool box is never frozen" "actions: $(cat "$T/actions")"; fi
# the clock ceiling is applied unconditionally at start
if grep -q 'gpu clock ceiling set' "$T/guard.log"; then ok "gpu clock ceiling applied at start"
else bad "gpu clock ceiling applied at start" "$(cat "$T/guard.log")"; fi
teardown

# ------------------------------------------------- 2. freeze / hysteresis/thaw
setup; set_gpu 55; set_cpu 50; start_guard
await '[ "$(stops)" = "0" ]' || true
set_gpu 76
if await '[ "$(stops)" -ge 1 ]'; then ok "freezes when the gpu reaches 76 C"
else bad "freezes when the gpu reaches 76 C" "$(cat "$T/guard.log")"; fi
# 70 is below the 75 freeze point but above the 66 thaw point: must stay frozen
set_gpu 70
sleep 2
if [ "$(conts)" = "0" ]; then ok "hysteresis holds the freeze at 70 C"
else bad "hysteresis holds the freeze at 70 C" "actions: $(cat "$T/actions")"; fi
set_gpu 60
if await '[ "$(conts)" -ge 1 ]'; then ok "thaws once back under 66 C"
else bad "thaws once back under 66 C" "$(cat "$T/guard.log")"; fi
teardown

# ------------------------------------------------------- 3. cpu alone can trip
setup; set_gpu 50; set_cpu 50; start_guard
await '[ "$(stops)" = "0" ]' || true
set_cpu 80
if await '[ "$(stops)" -ge 1 ]'; then ok "cpu alone can trigger the freeze"
else bad "cpu alone can trigger the freeze" "$(cat "$T/guard.log")"; fi
# gpu is cool but the cpu is not: a single cool sensor must not thaw it
set_gpu 40
sleep 2
if [ "$(conts)" = "0" ]; then ok "a cool gpu does not thaw a hot cpu"
else bad "a cool gpu does not thaw a hot cpu" "actions: $(cat "$T/actions")"; fi
teardown

# ------------------------------------- 4. blind sensors must fail CLOSED
setup; set_gpu 55; set_cpu 50; start_guard
await '[ "$(stops)" = "0" ]' || true
unset_gpu; unset_cpu
if await '[ "$(stops)" -ge 1 ]'; then ok "freezes when no sensor can be read"
else bad "freezes when no sensor can be read" "$(cat "$T/guard.log")"; fi
sleep 2
if [ "$(conts)" = "0" ]; then ok "stays frozen while blind"
else bad "stays frozen while blind" "actions: $(cat "$T/actions")"; fi
set_gpu 55; set_cpu 50
if await '[ "$(conts)" -ge 1 ]'; then ok "thaws once a real reading returns cool"
else bad "thaws once a real reading returns cool" "$(cat "$T/guard.log")"; fi
teardown

# ------------------------------------- 5. garbage sensor value is not a reading
setup; set_gpu 55; raw_cpu 3283100; start_guard
sleep 3
if [ "$(stops)" = "0" ]; then ok "an out-of-range hwmon value is ignored, not treated as hot"
else bad "an out-of-range hwmon value is ignored, not treated as hot" "$(cat "$T/guard.log")"; fi
teardown

# --------------------------------- 6. the guard never leaves the jobs frozen
setup; set_gpu 90; set_cpu 50; start_guard
if await '[ "$(stops)" -ge 1 ]'; then :; else bad "setup for exit test" "no freeze"; fi
kill -TERM "$GPID" 2>/dev/null; wait "$GPID" 2>/dev/null; GPID=""
if [ "$(conts)" -ge 1 ]; then ok "a terminating guard thaws the jobs on its way out"
else bad "a terminating guard thaws the jobs on its way out" "actions: $(cat "$T/actions")"; fi
if grep -q 'gpu clock ceiling released' "$T/guard.log"; then ok "a terminating guard releases the clock ceiling"
else bad "a terminating guard releases the clock ceiling" "$(cat "$T/guard.log")"; fi
teardown

printf '\n%d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
