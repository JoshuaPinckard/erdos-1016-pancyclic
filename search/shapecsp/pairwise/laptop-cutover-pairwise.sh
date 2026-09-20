#!/bin/bash
# Cut the laptop chain over from run-chain-laptop-v5.sh (unrestricted plan) to
# run-chain-laptop-v6.sh (pairwise plan).  Run ON THE LAPTOP as user j.
#
#   1. gate: thermal guard active, v6 script and all three tier manifests present;
#   2. stop erdos-laptop-chain (SIGTERM; the runner's lock is left behind, so it
#      is removed here after the process is confirmed gone);
#   3. partition 68/11, 70/11, 70/12 from their now-final unrestricted states;
#   4. rewrite the unit to ExecStart v6 (same fields as rebalance/laptop-cutover.sh),
#      daemon-reload, start;
#   5. verify from disk that pairwise-state-n68-b11.json appears and advances.
set -u
R="$HOME/erdos-n70"
BASE="$R/search/shapecsp"
PW="$BASE/pairwise"
PY="$HOME/erdos-gpu-n70-builder-t92/venv/bin/python"
CHAIN="$R/run-chain-laptop-v6.sh"
UNIT=/etc/systemd/system/erdos-laptop-chain.service
say() { echo "[cutover] $*"; }

say "gate"
systemctl is-active erdos-thermal-guard >/dev/null || { say "REFUSED: thermal guard not active"; exit 2; }
[ -x "$CHAIN" ] || { say "REFUSED: $CHAIN missing or not executable"; exit 2; }
for t in 68:11 70:11 70:12; do
  N=${t%:*}; B=${t#*:}
  m="$PW/tables/n$N-b$B/tier-manifest.json"
  [ -f "$m" ] || { say "REFUSED: missing $m"; exit 2; }
  "$PY" - "$m" <<'EOF' || exit 2
import json, sys
m = json.load(open(sys.argv[1]))
assert not m.get("partial"), "partial manifest"
print("[cutover]  tables", sys.argv[1].split("/")[-2], "shapes", m["shapes_count"], "compositions", m["tier_total_compositions"])
EOF
done
before=$(grep -c '^    \[' "$R/n68-state-b11.json" 2>/dev/null || echo 0)
say "68/11 unrestricted units before stop: $before"

say "stopping the chain"
sudo -n systemctl stop erdos-laptop-chain || { say "STOP FAILED"; exit 3; }
for i in $(seq 1 30); do pgrep -f gpu_state_runner.py >/dev/null || break; sleep 2; done
pgrep -af gpu_state_runner.py && { say "runner still alive after 60 s; refusing to continue"; exit 3; }
for f in "$R"/n*-state-b1*.json.lock; do [ -e "$f" ] && { say "removing dead lock $f (pid $(cat "$f"))"; rm -f "$f"; }; done
after=$(grep -c '^    \[' "$R/n68-state-b11.json" 2>/dev/null || echo 0)
say "chain stopped; 68/11 units $before -> $after (final)"

say "partitioning"
mkdir -p "$PW/partitions"
for t in 68:11 70:11 70:12; do
  N=${t%:*}; B=${t#*:}
  st="$R/n$N-state-b$B.json"
  if [ -f "$st" ]; then
    "$PY" "$PW/partition_tier.py" --source "$BASE/gpu-blast" --n "$N" --b "$B" --state "$st" --out "$PW/partitions" || { say "partition failed for $t"; exit 4; }
  else
    "$PY" "$PW/partition_tier.py" --source "$BASE/gpu-blast" --n "$N" --b "$B" --out "$PW/partitions" || { say "partition failed for $t"; exit 4; }
  fi
done

say "rewriting the unit for v6"
sudo -n tee "$UNIT" >/dev/null <<UNITEOF
[Unit]
Description=Erdos1016 laptop GPU exhaustion chain (pairwise plan: 68/11, 70/11, 70/12)
After=multi-user.target

[Service]
Type=simple
User=j
Group=j
WorkingDirectory=/home/j/erdos-n70/search/shapecsp
ExecStart=/bin/bash $CHAIN
Nice=0
CPUWeight=200
Restart=on-failure
RemainAfterExit=yes
RestartSec=200
StandardOutput=append:/home/j/erdos-n70/chain-laptop.log
StandardError=append:/home/j/erdos-n70/chain-laptop.log

[Install]
WantedBy=multi-user.target
UNITEOF
sudo -n systemctl daemon-reload || { say "daemon-reload FAILED"; exit 5; }
systemctl cat erdos-laptop-chain --no-pager | grep -E 'ExecStart|Requires|After=erdos'
sudo -n systemctl start erdos-laptop-chain || { say "START FAILED"; exit 5; }

say "verifying from disk"
ok=0
for i in $(seq 1 60); do
  u=$(grep -c '^  \[' "$PW/pairwise-state-n68-b11.json" 2>/dev/null || echo 0)
  if pgrep -f gpu_state_runner_pairwise.py >/dev/null && [ "$u" -ge 1 ]; then ok=1; break; fi
  sleep 10
done
if [ "$ok" -eq 1 ]; then say "RESUMED under the pairwise plan: pairwise-state-n68-b11.json units=$u"; else say "NOT VERIFIED after 10 min"; tail -n 5 "$R/chain-laptop.log"; exit 6; fi
systemctl is-active erdos-laptop-chain erdos-thermal-guard
tail -n 3 "$R/chain-laptop.log"
