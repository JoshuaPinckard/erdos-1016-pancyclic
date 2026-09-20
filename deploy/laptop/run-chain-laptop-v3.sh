#!/bin/bash
# Sequential b>=11 chain for the laptop GPU, after the 2026-09-19 rebalance.
#
# v2 is left in place untouched because a live chain may still be executing it:
# bash reads a script incrementally by byte offset, so rewriting the running
# file corrupts the run.  That is why v3 is a new file rather than an edit.
#
# WHAT CHANGED FROM v2, AND WHY
# -----------------------------
# v2 ran 70/10, 70/11, 70/12 -- every tier of level 70 and nothing else.  The
# desktop ran both other levels and was the critical path by about four days.
#
# The rebalance is a SWAP, not a one-way move:
#     69/11  desktop -> laptop   (this script gains it)
#     70/11  laptop  -> desktop  (this script loses its remainder)
# Measured rates, not assumed ones, are what force the swap.  The desktop card
# is an RTX 5060 Ti running at 2092 MHz / 72.5 W; this card is an RTX 4070
# Laptop held at 1395 MHz / 39 W by the thermal guard.  The desktop is about
# 1.29x this machine in ranks/hour.  Handing over the whole 69/11 tier
# (3.24e14 ranks) without taking anything back overshoots: it would make THIS
# machine the critical path and finish the proof later than doing nothing at
# all.  Taking 70/11's remainder (2.21e14 ranks) back to the desktop is what
# turns the move into an actual saving.  REPORT-rebalance.md carries the
# measurements and the arithmetic.
#
# 70/10 is gone from the list because it is complete (3040/3040 units); a
# completed tier is skipped in milliseconds anyway, so this is tidiness, not
# behaviour.  70/11 is gone because the desktop now owns it -- do NOT add it
# back as a "safety net": this machine would reach it before the desktop
# finished it and would redo thousands of units that are already done.
#
# 69/12 deliberately stays on the desktop.  Adding it here as well would not
# share it; the two machines keep independent state files and would each run
# the whole tier.  There is no cross-machine claim protocol.
#
# Each invocation runs one (level, tier) to completion and is fully resumable
# from its own state file, so finished jobs are skipped instantly on restart.
# n69.jsonl was copied here on 2026-09-19 and its sha256 matches the desktop's
# byte for byte (bceb4eee...), which is what lets a state file produced here be
# verified against the desktop's manifest.
set -u
BASE="$HOME/erdos-n70/search/shapecsp"
PY="$HOME/erdos-gpu-n70-builder-t92/venv/bin/python"
SRC="$BASE/gpu-blast"
MAX_LOCK_RETRIES=12
LOCK_WAIT=200
cd "$BASE" || exit 1
echo "[chain] start $(date -Is) script=v3"
rc=0
for job in "69 11" "70 12"; do
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
