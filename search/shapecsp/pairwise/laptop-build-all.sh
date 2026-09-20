#!/bin/bash
# Build the pairwise tables for every live tier on the laptop, four workers at
# nice 19, sequentially per tier so the CPU grant stays bounded.  Run detached:
#   bash laptop-build-all.sh
set -u
cd "$HOME/erdos-n70/search/shapecsp/pairwise" || exit 1
PY="$HOME/erdos-gpu-n70-builder-t92/venv/bin/python"
mkdir -p tables
sha256sum ../bound.py ../shapes.py ../gpu-blast/n68.jsonl ../gpu-blast/n69.jsonl ../gpu-blast/n70.jsonl \
          ../prune_pairwise.py pairwise_tables.py gpu_search_pairwise.py gpu_state_runner_pairwise.py
"$PY" -c 'import numpy, psutil; print("numpy", numpy.__version__, "psutil", psutil.__version__)'
nproc; cat /proc/loadavg
nohup bash -c '
for t in 69:12 70:12 69:11 70:11 68:11 68:12; do
  N=${t%:*}; B=${t#*:}
  nice -n 19 '"$PY"' pairwise_tables.py build-tier --n $N --b $B --workers 4 --out tables > build-n$N-b$B.log 2>&1
  echo "tier $N $B rc=$? $(date -Is)"
done
echo ALL-BUILDS-DONE' > build-all.log 2>&1 &
sleep 3
pgrep -af pairwise_tables | head -n 3
