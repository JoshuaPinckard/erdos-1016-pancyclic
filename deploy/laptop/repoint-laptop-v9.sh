#!/bin/bash
# Repoint the laptop chain unit from run-chain-laptop-v8.sh to v9 (same jobs,
# then the odd-level interleaved descent 87..73), and restart the laptop
# finalizer so it reads the extended TIERS list.  Runs detached on the laptop
# as user j; log in ~/erdos-n70/_mgr-repoint-v9.log.
set -u
R="$HOME/erdos-n70"; PW="$R/search/shapecsp/pairwise"; CHAIN="$R/run-chain-laptop-v9.sh"
UNIT=/etc/systemd/system/erdos-laptop-chain.service
say() { echo "[repoint-v9] $(date '+%T') $*"; }
sed -i 's/\r$//' "$CHAIN" "$R/finalize-laptop.sh"; chmod +x "$CHAIN" "$R/finalize-laptop.sh"
bash -n "$CHAIN" || { say "v9 does not parse"; exit 1; }
bash -n "$R/finalize-laptop.sh" || { say "finalize-laptop.sh does not parse"; exit 1; }
grep -q 'PROD="$BASE/pairwise-prod"' "$CHAIN" && grep -q '"$PROD/gpu_state_runner_pairwise.py"' "$CHAIN" || { say "v9 does not run the frozen runner"; exit 1; }
systemctl is-active erdos-thermal-guard >/dev/null || { say "REFUSED: thermal guard not active"; exit 2; }
STATE="$PW/pairwise-state-n70-b11.json"
before=$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1]))["complete"]))' "$STATE")
say "70/11 pairwise units before: $before"
sudo -n systemctl stop erdos-laptop-chain || { say "STOP FAILED"; exit 3; }
for i in $(seq 1 30); do pgrep -f gpu_state_runner_pairwise.py >/dev/null || break; sleep 2; done
pgrep -af gpu_state_runner_pairwise.py && { say "runner still alive; refusing"; exit 3; }
for f in "$PW"/pairwise-state-*.json.lock; do [ -e "$f" ] && { say "removing dead lock $(basename "$f") (pid $(cat "$f"))"; rm -f "$f"; }; done
sudo -n tee "$UNIT" >/dev/null <<UNITEOF
[Unit]
Description=Erdos1016 laptop GPU exhaustion chain (pairwise plan, runner from pairwise-prod: 70/11, 70/12, level 71, then odd levels 87..73)
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
  u=$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1]))["complete"]))' "$STATE" 2>/dev/null || echo 0)
  if pgrep -f gpu_state_runner_pairwise.py >/dev/null && [ "$u" -gt "$before" ]; then ok=1; break; fi
done
if [ "$ok" -eq 1 ]; then say "RESUMED under v9: 70/11 units $before -> $u"; else say "NOT VERIFIED after 6 min (units $before -> $u)"; tail -n 5 "$R/chain-laptop.log"; exit 6; fi
say "runner cmd: $(pgrep -af gpu_state_runner_pairwise.py | head -n 1 | cut -c1-140)"
# finalizer: restart only if no claim tool is running (none can be: level 71 has not started)
if pgrep -f verify_tier_combined.py >/dev/null; then
  say "claim tool running; leaving the old finalizer in place (restart it later)"
else
  pkill -f 'bash finalize-laptop.sh' && say "old finalizer stopped"
  sleep 1
  (cd "$R" && setsid nohup bash "$R/finalize-laptop.sh" >> "$R/finalize-laptop.log" 2>&1 < /dev/null &)
  sleep 2; say "finalizer restarted: $(pgrep -af 'bash finalize-laptop.sh' | grep -v pgrep | wc -l) process(es)"; tail -n 1 "$R/finalize-laptop.log" | cut -c1-200
fi
systemctl is-active erdos-laptop-chain erdos-thermal-guard
say "done"
