#!/bin/bash
# Sequential chain for the laptop GPU.  Successor to run-chain-laptop-v4.sh
# (2026-09-19, third split).  v1..v4 are left in place untouched: bash reads a
# script incrementally by byte offset.
#
# WHY A THIRD SPLIT
# -----------------
# v3 and v4 were both chosen with a model that priced work in RANKS and gave
# each machine one rate.  That model is wrong.  A rank is not a constant amount
# of work.  Measured on THIS card from the whole chain log, over full 5e10-rank
# units only, median GPU seconds per unit:
#     n70 b10  42.05  (1069 units)
#     n70 b11  48.00  (2253 units)
#     n69 b11  60.98  (13 units)
#     n69 b12  77.75  (11 units)
# Cost rises with the tier AND with the level: n69 b11 costs 27% more per rank
# than n70 b11 at the same b.  v4 gave this slower card BOTH remaining b=12
# tiers, which the corrected model prices at about 390 h against roughly 357 h
# for this split.
#
# WHY THIS SPLIT AND NOT THE NOMINAL OPTIMUM
# ------------------------------------------
# The b=12 multiplier is not pinned down: matched-level desktop probes give
# 1.28, this card's median-of-medians gives 1.43, and the n=69 numbers rest on
# 11-13 units.  Rather than tune to one value, all 64 whole-job splits were
# ranked at 1.25, 1.28, 1.32, 1.36, 1.40 and 1.43 and scored by worst-case
# regret against the best split at each point.  This assignment --
# {68/11, 70/11, 70/12} here -- has a worst-case regret of 2.3 h across that
# whole range; the next best is 11 h.  It is chosen for being insensitive to
# the number we are least sure of.
#
# So this card takes the two cheap b=11 remainders plus 70/12, and the desktop
# takes 69/11 and the two b=12 tiers of levels 68 and 69.  Expensive work
# belongs on the faster card.
#
# ORDER.  The two b=11 remainders first: together with the desktop's 69/11 they
# close "b<=11 exhausted at n=68, 69 and 70" at about hour 150, as early as this
# split allows.  70/12 is last because nothing depends on it.
#
# n68.jsonl was copied here on 2026-09-19 and its sha256 matches the desktop
# byte for byte (b57e9d74...), as do n69.jsonl and n70.jsonl.  That is what
# makes a state file produced here verifiable there and vice versa.
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
echo "[chain] start $(date -Is) script=v5"
rc=0
for job in "68 11" "70 11" "70 12"; do
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
