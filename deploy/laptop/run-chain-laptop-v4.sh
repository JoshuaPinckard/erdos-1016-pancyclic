#!/bin/bash
# Sequential chain for the laptop GPU.  Successor to run-chain-laptop-v3.sh
# (2026-09-19, second rebalance).  v1/v2/v3 are left in place untouched: bash
# reads a script incrementally by byte offset, so rewriting a file a live chain
# may still be executing corrupts the run.
#
# WHAT CHANGED FROM v3, AND WHY
# -----------------------------
# v3 ran 69/11 then 70/12.  Enumerating all 64 whole-job assignments of the six
# outstanding tiers at the two MEASURED rates (desktop 3.6177e12 ranks/h,
# laptop 2.7973e12) puts v3's split at 320.5 h and this one at 307.2 h --
# 13.3 h better, and within 4.7 h of the 302.5 h fractional bound.  The idle
# tail on this machine drops from 41.4 h to 8.4 h.  Full ranking in
# rebalance/enumeration-20260919.txt.
#
# The rule the enumeration produces: every b=11 REMAINDER runs on the faster
# card and this machine takes whole b=12 tiers.  So 69/11 goes back to the
# desktop -- its 14 completed units travel with it as a state file -- and 69/12
# comes here instead.  4.02e14 > 3.24e14 is exactly what makes that the
# balancing exchange; sending the smaller tier undershot.
#
# ORDER.  69/12 first.  The desktop finishes 69/11 at about hour 145 and this
# tier lands at about hour 144, so level 69 closes out completely near hour 145
# -- the earliest any whole level can be finished under this split.  Running
# 70/12 first would instead close level 70 at hour 206 and push level 69 to
# hour 307.
#
# n69.jsonl is resident here and its sha256 matches the desktop byte for byte
# (bceb4eee...), which is what makes 69/12's state file verifiable there.
#
# Each invocation runs one (level, tier) to completion and is fully resumable
# from its own state file, so finished jobs are skipped instantly on restart.
set -u
BASE="$HOME/erdos-n70/search/shapecsp"
PY="$HOME/erdos-gpu-n70-builder-t92/venv/bin/python"
SRC="$BASE/gpu-blast"
MAX_LOCK_RETRIES=12
LOCK_WAIT=200
cd "$BASE" || exit 1
echo "[chain] start $(date -Is) script=v4"
rc=0
for job in "69 12" "70 12"; do
  set -- $job; N=$1; B=$2
  tries=0
  while true; do
    echo "[chain] n=$N b=$B starting $(date -Is)"
    "$PY" "$BASE/gpu_state_runner.py" "$SRC" "$HOME/erdos-n70/n$N-state-b$B.json" \
          --n "$N" --min-b "$B" --max-b "$B" --wall-budget 0
    st=$?
    echo "[chain] n=$N b=$B exit=$st $(date -Is)"
    # exit 2 is "LOCKED": a previous instance died without releasing its lock
    # and the lock is not yet older than --lock-stale.  That is NOT a finished
    # tier -- advancing here would silently skip a whole level for hours.  Wait
    # out the stale window and retry the SAME tier, bounded so a permanently
    # locked tier cannot spin forever (12 x 200s is ~40min, well past the 180s
    # stale window).
    if [ "$st" -eq 2 ]; then
      tries=$((tries + 1))
      if [ "$tries" -ge "$MAX_LOCK_RETRIES" ]; then
        echo "[chain] n=$N b=$B STILL LOCKED after $tries attempts; leaving tier undone"
        rc=2
        break
      fi
      echo "[chain] n=$N b=$B LOCKED (attempt $tries); waiting out the stale window"
      sleep "$LOCK_WAIT"
      continue
    fi
    [ "$st" -ne 0 ] && rc=$st
    break
  done
done
echo "[chain] laptop jobs complete $(date -Is) rc=$rc"
exit $rc
