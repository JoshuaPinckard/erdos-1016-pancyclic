#!/bin/bash
# Sequential b>=10 chain for the laptop GPU.
# Each invocation runs one (level, tier) to completion and is fully resumable
# from its own state file, so finished jobs are skipped instantly on restart.
#
# v2 adds the b=12 tier.  It was missing from v1's job list and from the
# desktop's, and nothing else runs them: gpu-blast/n70.jsonl carries a b=12
# block (281 shapes / 4.57e14 ranks) that verify_tier_exhaustion.py counts as
# expected work.  Without it "no 6-chord pancyclic graph on 70 vertices" is not
# an exhaustion claim at all, only a b<=11 claim, and the chain would have run
# to "jobs complete" still owing the largest tier at the level.
#
# v1 is left in place because a live chain may still be executing it: bash
# reads a script incrementally by byte offset, so rewriting the running file
# corrupts the run.
set -u
BASE="$HOME/erdos-n70/search/shapecsp"
PY="$HOME/erdos-gpu-n70-builder-t92/venv/bin/python"
SRC="$BASE/gpu-blast"
MAX_LOCK_RETRIES=12
LOCK_WAIT=200
cd "$BASE" || exit 1
echo "[chain] start $(date -Is)"
rc=0
for job in "70 10" "70 11" "70 12"; do
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
