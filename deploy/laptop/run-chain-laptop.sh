#!/bin/bash
# Sequential b>=10 chain for the laptop GPU.
# Each invocation runs one (level, tier) to completion and is fully resumable
# from its own state file, so finished jobs are skipped instantly on restart.
set -u
BASE="$HOME/erdos-n70/search/shapecsp"
PY="$HOME/erdos-gpu-n70-builder-t92/venv/bin/python"
SRC="$BASE/gpu-blast"
cd "$BASE" || exit 1
echo "[chain] start $(date -Is)"
for job in "70 10" "70 11"; do
  set -- $job; N=$1; B=$2
  echo "[chain] n=$N b=$B starting $(date -Is)"
  "$PY" "$BASE/gpu_state_runner.py" "$SRC" "$HOME/erdos-n70/n$N-state-b$B.json" \
        --n "$N" --min-b "$B" --max-b "$B" --wall-budget 0
  echo "[chain] n=$N b=$B exit=$? $(date -Is)"
done
echo "[chain] laptop jobs complete $(date -Is)"
