#!/bin/bash
# Tests for catch-and-guard.sh with ssh/scp stubbed.
#
# The safety property is an ORDER, not a result: the very first thing the
# watcher does on a successful connection must be to stop the jobs, because the
# laptop is already heating toward its 80 C power-off while we are talking to
# it. Everything else -- diagnostics, copying files, installing -- has to come
# after that. These tests assert that order, and assert that a box without
# passwordless sudo is left idle rather than running uncapped.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$(cd "$HERE/.." && pwd)"

pass=0; fail=0
ok()  { pass=$((pass+1)); printf 'ok   %s\n' "$1"; }
bad() { fail=$((fail+1)); printf 'FAIL %s\n     %s\n' "$1" "${2:-}"; }

# SUDO=yes/no decides whether the stubbed host has passwordless sudo.
# UP_AFTER is how many probes must fail before the host "comes up".
run_case() {
  CASE_HOURS="${CASE_HOURS:-1}"
  T=$(mktemp -d)
  mkdir -p "$T/bin"
  cat > "$T/bin/ssh" <<'STUB'
#!/bin/bash
# drop the -o flags and the host, keep the remote command
cmd=""
while [ $# -gt 0 ]; do
  case "$1" in
    -o) shift 2 ;;
    -*) shift ;;
    *) shift; cmd="$*"; break ;;
  esac
done
if [ -z "$cmd" ] || [ "$cmd" = "true" ]; then
  n=$(cat "$T/probes" 2>/dev/null || echo 0); n=$((n+1)); echo "$n" > "$T/probes"
  [ "$n" -gt "$UP_AFTER" ] || exit 255
  printf 'PROBE-OK\n' >> "$T/trace"
  exit 0
fi
printf '%s\n' "$cmd" >> "$T/trace"
case "$cmd" in
  *"sudo -n true"*) [ "$SUDO" = yes ] || exit 1 ;;
esac
exit 0
STUB
  cat > "$T/bin/scp" <<'STUB'
#!/bin/bash
printf 'SCP\n' >> "$T/trace"
exit 0
STUB
  chmod +x "$T/bin"/*
  : > "$T/trace"
  PATH="$T/bin:$PATH" T="$T" SUDO="$SUDO" UP_AFTER="$UP_AFTER" \
    CATCH_LOG="$T/catch.log" CATCH_POLL=1 CATCH_HOURS="${CASE_HOURS:-1}" CATCH_SETTLE=0 \
    bash "$SRC/catch-and-guard.sh" >/dev/null 2>&1
}

line_of() { grep -n -- "$1" "$T/trace" | head -1 | cut -d: -f1; }

# ------------------------------------------------ 1. host up, sudo available
SUDO=yes UP_AFTER=2 run_case
first=$(head -1 "$T/trace")
if [ "$first" = "PROBE-OK" ]; then ok "the connection probe itself is the first contact"
else bad "the connection probe itself is the first contact" "$(head -3 "$T/trace")"; fi

stop_at=$(line_of 'pkill -STOP')
scp_at=$(line_of 'SCP')
inst_at=$(line_of 'install-thermal-guard.sh')
cont_at=$(line_of 'pkill -CONT')
if [ -n "$stop_at" ] && [ -n "$scp_at" ] && [ "$stop_at" -lt "$scp_at" ]; then
  ok "jobs are stopped before anything is copied to the box"
else bad "jobs are stopped before anything is copied" "STOP@$stop_at SCP@$scp_at
$(cat "$T/trace")"; fi

if [ -n "$inst_at" ] && [ "$stop_at" -lt "$inst_at" ]; then
  ok "jobs are stopped before the installer runs"
else bad "jobs are stopped before the installer runs" "STOP@$stop_at INSTALL@$inst_at"; fi

if [ -n "$cont_at" ] && [ "$inst_at" -lt "$cont_at" ]; then
  ok "jobs are released only after the guard is installed"
else bad "jobs are released only after the guard is installed" "INSTALL@$inst_at CONT@$cont_at
$(cat "$T/trace")"; fi

# The pattern must not be able to stop the shell carrying it.
if grep -q 'pkill -STOP -u j -f .\[d\]escend' "$T/trace"; then
  ok "the pkill pattern is written so it cannot match its own shell"
else bad "the pkill pattern is written so it cannot match its own shell" "$(grep pkill "$T/trace")"; fi

grep -q 'journalctl -b -1' "$T/trace" \
  && ok "the previous boot's journal is captured" || bad "previous boot journal captured" ""
rm -rf "$T"

# ---------------------------------------------- 2. host up, no passwordless sudo
SUDO=no UP_AFTER=1 run_case
if grep -q 'pkill -STOP' "$T/trace"; then ok "jobs are stopped even when the install cannot proceed"
else bad "jobs are stopped even when the install cannot proceed" "$(cat "$T/trace")"; fi
if grep -q 'pkill -CONT' "$T/trace"; then
  bad "jobs are LEFT stopped without sudo" "found a CONT: $(cat "$T/trace")"
else ok "jobs are left stopped rather than running uncapped without sudo"; fi
if grep -q 'no passwordless sudo' "$T/catch.log"; then ok "the blocker is recorded in the log"
else bad "the blocker is recorded in the log" "$(cat "$T/catch.log")"; fi
rm -rf "$T"

# ------------------------------------------------------ 3. host never answers
SUDO=yes UP_AFTER=99999 CASE_HOURS=0 run_case
if grep -q 'pkill' "$T/trace" 2>/dev/null; then
  bad "an unreachable host is never touched" "$(cat "$T/trace")"
else ok "an unreachable host is never touched"; fi
rm -rf "$T"

printf '\n%d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
