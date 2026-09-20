#!/bin/bash
# Sequential chain for the laptop GPU.  Successor to run-chain-laptop-v8.sh
# (2026-09-19).  v1..v8 are left in place untouched: bash reads a script
# incrementally by byte offset.
#
# IDENTICAL to v8 through level 71.  The one addition: interleaved descent of
# the odd levels 87, 85, 83, 81, 79, 77, 75, 73 (the laptop's half of the
# 72..87 gap; the desktop runs the even half in run-chain-desktop-v11.cmd),
# each b=12..6 via run_tier from pairwise/gpu-blast-ext + pairwise/tables-ext,
# whole-tier state pairwise-state-n{N}-b{B}.json, no --only-shapes.  Missing
# manifests are skipped with a log line, same as level 71.  Descending order
# across both machines together means the first hit -- if any -- settles
# t_6 as early in wall-clock time as the two machines can reach it, instead of
# each machine clearing its own block bottom-up first.
set -u
BASE="$HOME/erdos-n70/search/shapecsp"
PW="$BASE/pairwise"
PROD="$BASE/pairwise-prod"
PY="$HOME/erdos-gpu-n70-builder-t92/venv/bin/python"
SRC="$BASE/gpu-blast"
MAX_LOCK_RETRIES=12
LOCK_WAIT=200
cd "$BASE" || exit 1
echo "[chain] start $(date -Is) script=v9 plan=pairwise runner=pairwise-prod"
rc=0
run_tier() {   # N B state source tables [only]
  local N=$1 B=$2 STATE=$3 SOURCE=$4 TABLES=$5 ONLY=${6:-}
  local tries=0 st
  while true; do
    echo "[chain] n=$N b=$B starting $(date -Is) plan=pairwise state=$(basename "$STATE")"
    if [ -n "$ONLY" ]; then
      "$PY" "$PROD/gpu_state_runner_pairwise.py" "$SOURCE" "$STATE" --tables "$TABLES" --n "$N" --b "$B" --only-shapes "$ONLY" --wall-budget 0
    else
      "$PY" "$PROD/gpu_state_runner_pairwise.py" "$SOURCE" "$STATE" --tables "$TABLES" --n "$N" --b "$B" --wall-budget 0
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
echo "[chain] level 71 reported complete $(date -Is) rc=$rc; starting interleaved descent 87..73 (odd)"
for N in 87 85 83 81 79 77 75 73; do
  for B in 12 11 10 9 8 7 6; do
    if [ ! -f "$PW/tables-ext/n$N-b$B/tier-manifest.json" ]; then
      echo "[chain] n=$N b=$B SKIPPED: no tier manifest under tables-ext"; continue
    fi
    run_tier "$N" "$B" "$PW/pairwise-state-n$N-b$B.json" "$PW/gpu-blast-ext" "$PW/tables-ext"
  done
done
echo "[chain] laptop jobs complete $(date -Is) rc=$rc"
exit $rc
