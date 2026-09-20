#!/bin/bash
# Quiesce the laptop chain so its state files can be copied consistently.
#
# Stops ONLY erdos-laptop-chain.  erdos-thermal-guard is a separate unit that
# the chain Requires=; it is deliberately left running, so the 75 C freeze and
# the 80 C hardware backstop stay in force for the whole cutover.
#
# systemd stops the unit with SIGTERM.  CPython does not raise on SIGTERM, so
# the runner exits without running the finally: that unlinks its .lock file --
# which is why the unit carries RestartSec=200, above the runner's 180 s
# --lock-stale.  This script therefore reports the lock's age so the caller can
# decide whether a restart will be refused with exit 2 (LOCKED) or accepted.
set -u
echo "--- before"
systemctl is-active erdos-laptop-chain erdos-thermal-guard
sudo -n systemctl stop erdos-laptop-chain || { echo "STOP FAILED"; exit 1; }
echo "--- after"
systemctl is-active erdos-laptop-chain || true
echo "thermal guard (must still be active):"
systemctl is-active erdos-thermal-guard
echo "--- runner processes still alive (expect none)"
pgrep -af gpu_state_runner.py || echo "none"
echo "--- stale lock files"
for f in "$HOME"/erdos-n70/*.lock; do
  [ -e "$f" ] || continue
  echo "$f age_seconds=$(( $(date +%s) - $(stat -c %Y "$f") )) pid_in_file=$(cat "$f" 2>/dev/null)"
done
echo "--- final state counts"
"$HOME/erdos-gpu-n70-builder-t92/venv/bin/python" - <<'PYEOF'
import glob, json, os, datetime
for f in sorted(glob.glob(os.path.expanduser("~/erdos-n70/n*-state-b1*.json"))):
    d = json.load(open(f))
    print(os.path.basename(f), "n=%s b=%s-%s" % (d["n"], d["min_b"], d["max_b"]),
          "complete=%d" % len(d["complete"]), "hits=%d" % len(d["hits"]),
          "sha=%s" % d["source_sha256"][:8])
PYEOF
