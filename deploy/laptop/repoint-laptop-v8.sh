#!/bin/bash
# Repoint the laptop chain unit from run-chain-laptop-v7.sh to v8 (same jobs;
# the runner now comes from the frozen pairwise-prod/ snapshot).  Runs detached
# on the laptop as user j; log in ~/erdos-n70/_mgr-repoint-v8.log.
set -u
R="$HOME/erdos-n70"; PW="$R/search/shapecsp/pairwise"; CHAIN="$R/run-chain-laptop-v8.sh"
UNIT=/etc/systemd/system/erdos-laptop-chain.service
say() { echo "[repoint-v8] $(date '+%T') $*"; }
bash -n "$CHAIN" || { say "v8 does not parse"; exit 1; }
systemctl is-active erdos-thermal-guard >/dev/null || { say "REFUSED: thermal guard not active"; exit 2; }
before=$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1]))["complete"]))' "$PW/pairwise-state-n68-b11.json")
say "68/11 pairwise units before: $before"
sudo -n systemctl stop erdos-laptop-chain || { say "STOP FAILED"; exit 3; }
for i in $(seq 1 30); do pgrep -f gpu_state_runner_pairwise.py >/dev/null || break; sleep 2; done
pgrep -af gpu_state_runner_pairwise.py && { say "runner still alive; refusing"; exit 3; }
for f in "$PW"/pairwise-state-*.json.lock; do [ -e "$f" ] && { say "removing dead lock $(basename "$f") (pid $(cat "$f"))"; rm -f "$f"; }; done
sudo -n tee "$UNIT" >/dev/null <<UNITEOF
[Unit]
Description=Erdos1016 laptop GPU exhaustion chain (pairwise plan, runner from pairwise-prod: 68/11, 70/11, 70/12, then level 71)
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
ok=0
for i in $(seq 1 36); do
  sleep 10
  u=$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1]))["complete"]))' "$PW/pairwise-state-n68-b11.json" 2>/dev/null || echo 0)
  if pgrep -f gpu_state_runner_pairwise.py >/dev/null && [ "$u" -gt "$before" ]; then ok=1; break; fi
done
if [ "$ok" -eq 1 ]; then say "RESUMED under v8: 68/11 units $before -> $u"; else say "NOT VERIFIED after 6 min (units $before -> $u)"; tail -n 5 "$R/chain-laptop.log"; exit 6; fi
say "runner cmd: $(pgrep -af gpu_state_runner_pairwise.py | head -n 1 | cut -c1-140)"
systemctl is-active erdos-laptop-chain erdos-thermal-guard
tail -n 2 "$R/chain-laptop.log" | cut -c1-160
say "done"
