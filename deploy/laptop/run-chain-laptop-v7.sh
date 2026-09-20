#!/bin/bash
# Sequential chain for the laptop GPU.  Successor to run-chain-laptop-v6.sh
# (2026-09-19).  v1..v6 are left in place untouched: bash reads a script
# incrementally by byte offset.
#
# Same three production tiers as v6 (resumed from their state files; finished
# tiers are skipped instantly), then LEVEL 71 under the pairwise plan, every
# eligible shape of every b, from the census manifest pairwise/gpu-blast-ext/
# n71.jsonl and the tables under pairwise/tables-ext (built on this machine).
# Level 71 state files are pairwise-state-n71-b{B}.json, no --only-shapes, so
# each one is a whole-tier exhaustion by itself.  A tier whose tables are not
# built yet is SKIPPED and reported, never silently passed.
set -u
BASE="$HOME/erdos-n70/search/shapecsp"
PW="$BASE/pairwise"
PY="$HOME/erdos-gpu-n70-builder-t92/venv/bin/python"
SRC="$BASE/gpu-blast"
MAX_LOCK_RETRIES=12
LOCK_WAIT=200
cd "$BASE" || exit 1
echo "[chain] start $(date -Is) script=v7 plan=pairwise"
rc=0
run_tier() {   # N B state source tables [only]
  local N=$1 B=$2 STATE=$3 SOURCE=$4 TABLES=$5 ONLY=${6:-}
  local tries=0 st
  while true; do
    echo "[chain] n=$N b=$B starting $(date -Is) plan=pairwise state=$(basename "$STATE")"
    if [ -n "$ONLY" ]; then
      "$PY" "$PW/gpu_state_runner_pairwise.py" "$SOURCE" "$STATE" --tables "$TABLES" --n "$N" --b "$B" --only-shapes "$ONLY" --wall-budget 0
    else
      "$PY" "$PW/gpu_state_runner_pairwise.py" "$SOURCE" "$STATE" --tables "$TABLES" --n "$N" --b "$B" --wall-budget 0
    fi
    st=$?
    echo "[chain] n=$N b=$B exit=$st $(date -Is)"
    if [ "$st" -eq 2 ]; then
      tries=$((tries + 1))
      if [ "$tries" -ge "$MAX_LOCK_RETRIES" ]; then
        echo "[chain] n=$N b=$B STILL LOCKED after $tries attempts; leaving tier undone"
        rc=2
        return
      fi
      echo "[chain] n=$N b=$B LOCKED (attempt $tries); waiting out the stale window"
      sleep "$LOCK_WAIT"
      continue
    fi
    [ "$st" -ne 0 ] && rc=$st
    return
  done
}
for job in "68 11" "70 11" "70 12"; do
  set -- $job; N=$1; B=$2
  ONLY="$PW/partitions/n$N-b$B-remaining.json"
  if [ ! -f "$ONLY" ]; then
    echo "[chain] n=$N b=$B REFUSED: partition file missing $ONLY"; rc=9; continue
  fi
  run_tier "$N" "$B" "$PW/pairwise-state-n$N-b$B.json" "$SRC" "$PW/tables" "$ONLY"
done
echo "[chain] production tiers reported complete $(date -Is) rc=$rc; starting level 71"
for B in 12 11 10 9 8 7 6; do
  if [ ! -f "$PW/tables-ext/n71-b$B/tier-manifest.json" ]; then
    echo "[chain] n=71 b=$B SKIPPED: no tier manifest under tables-ext"; continue
  fi
  run_tier 71 "$B" "$PW/pairwise-state-n71-b$B.json" "$PW/gpu-blast-ext" "$PW/tables-ext"
done
echo "[chain] laptop jobs complete $(date -Is) rc=$rc"
exit $rc
