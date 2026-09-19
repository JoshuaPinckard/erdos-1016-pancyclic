#!/bin/bash
# Run ON THE LAPTOP as root (sudo) from the directory holding these files.
#
# Installs the thermal guard, binds both compute units to it so a boot can
# never start them uncapped, trims the descent CPU grant, and restarts
# everything in the right order.
#
# SYSROOT exists so this can be exercised against a throwaway tree before it is
# pointed at a machine that powers itself off at 80 C; it is empty in real use.
set -eu

cd "$(dirname "$0")"
SYSROOT="${SYSROOT:-}"
SBIN="$SYSROOT/usr/local/sbin"
UNITDIR="$SYSROOT/etc/systemd/system"
GUARD_LOG_PATH="${GUARD_LOG_PATH:-/home/j/erdos-thermal-guard.log}"

# A guard that does not behave is worse than no guard, because everything
# downstream assumes it freezes in time.  Gate the install on its own tests
# when they were shipped alongside it.
if [ -f tests/test-thermal-guard.sh ]; then
  echo "== guard self-test =="
  bash tests/test-thermal-guard.sh
fi

mkdir -p "$SBIN" "$UNITDIR"
install -m 0755 erdos-thermal-guard "$SBIN/erdos-thermal-guard"
install -m 0644 erdos-thermal-guard.service "$UNITDIR/erdos-thermal-guard.service"

# The interlock.  Both compute units are WantedBy=multi-user.target, so before
# this drop-in a boot started them before anything could cap them: that is the
# boot -> 80 C -> power-off loop of 2026-09-18.  Requires= plus After= means a
# job unit cannot reach ExecStart unless the guard is up, and is stopped with
# it if the guard ever goes away.  Failing that way round leaves the laptop
# idle, which is the safe direction: both jobs resume from their ledgers.
for unit in erdos-descent erdos-laptop-chain; do
  mkdir -p "$UNITDIR/${unit}.service.d"
  cat > "$UNITDIR/${unit}.service.d/thermal.conf" <<'CONF'
[Unit]
Requires=erdos-thermal-guard.service
After=erdos-thermal-guard.service
CONF
done

# 2026-09-18: two thermal shutdowns in one day with 4 cores + GPU.  Two cores
# is half the CPU heat; the level ledger resumes shape-by-shape either way.
cat >> "$UNITDIR/erdos-descent.service.d/thermal.conf" <<'CONF'

[Service]
CPUQuota=200%
CONF

systemctl daemon-reload
systemctl enable erdos-thermal-guard.service
# A restart, not `enable --now`: --now leaves an already-running guard on the
# OLD script, which is how a threshold change once installed without taking
# effect.  Restarting the guard restarts the units that Require= it, so the
# descent comes back under the new guard either way.
systemctl restart erdos-thermal-guard.service
systemctl restart erdos-descent.service

echo "== state =="
systemctl status --no-pager erdos-thermal-guard.service erdos-descent.service erdos-laptop-chain.service 2>/dev/null | grep -E "Active|Loaded" || true
tail -3 "$GUARD_LOG_PATH" 2>/dev/null || true
