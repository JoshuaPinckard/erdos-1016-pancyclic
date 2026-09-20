#!/bin/bash
# Sequential chain for the laptop GPU.  Successor to run-chain-laptop-v5.sh
# (2026-09-19, pairwise cutover).  v1..v5 are left in place untouched: bash
# reads a script incrementally by byte offset.
#
# Every remaining tier runs under the PAIRWISE plan (search/shapecsp/pairwise):
# only compositions surviving the pairwise Hall test are enumerated (measured
# 42-47x fewer on b=12, 10-15x on b=11).  Shapes already exhausted under the
# unrestricted plan are not re-run: partition_tier.py derives the remaining
# shape list from the unrestricted state file and it is passed as
# --only-shapes.  The runner refuses any state file without
# enumeration="pairwise-v1" and a matching plan hash.
#
# Tables under pairwise/tables/n{N}-b{B}/ were built on this machine; their
# tier-manifest hashes are compared with the desktop's before cutover.
set -u
BASE="$HOME/erdos-n70/search/shapecsp"
PW="$BASE/pairwise"
PY="$HOME/erdos-gpu-n70-builder-t92/venv/bin/python"
SRC="$BASE/gpu-blast"
MAX_LOCK_RETRIES=12
LOCK_WAIT=200
cd "$BASE" || exit 1
echo "[chain] start $(date -Is) script=v6 plan=pairwise"
rc=0
for job in "68 11" "70 11" "70 12"; do
  set -- $job; N=$1; B=$2
  ONLY="$PW/partitions/n$N-b$B-remaining.json"
  if [ ! -f "$ONLY" ]; then
    echo "[chain] n=$N b=$B REFUSED: partition file missing $ONLY"
    rc=9
    continue
  fi
  tries=0
  while true; do
    echo "[chain] n=$N b=$B starting $(date -Is) plan=pairwise"
    "$PY" "$PW/gpu_state_runner_pairwise.py" "$SRC" "$PW/pairwise-state-n$N-b$B.json" \
          --tables "$PW/tables" --n "$N" --b "$B" --only-shapes "$ONLY" --wall-budget 0
    st=$?
    echo "[chain] n=$N b=$B exit=$st $(date -Is)"
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
