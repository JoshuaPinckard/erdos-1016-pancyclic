#!/bin/bash
# Point the laptop chain unit at a given chain script and start it.
#
# Usage: laptop-cutover.sh <chain-script-basename> <unit-description>
# e.g.   laptop-cutover.sh run-chain-laptop-v4.sh "69/12 then 70/12"
#
# Parameterised rather than hardcoded so a re-split does not mean a new copy of
# this file diverging from the last one.
#
# The unit file is rewritten rather than edited in place with sed: systemd reads
# a unit whole at daemon-reload, so there is no byte-offset hazard here (unlike
# the chain script itself, which is why each split gets a new vN file).
# Everything that matters is preserved verbatim:
#   RestartSec=200  -- above the runner's 180 s --lock-stale.  systemd stops the
#                      unit with SIGTERM, which CPython does not turn into an
#                      exception, so the runner exits without running the
#                      finally: that unlinks its .lock.  Restarting inside the
#                      stale window makes the new runner exit 2 (LOCKED).
#   Restart=on-failure -- this is a finite pipeline, not a daemon.
#   CPUWeight/Nice     -- the feeder must stay responsive or the card idles.
# The thermal drop-in at erdos-laptop-chain.service.d/thermal.conf is NOT
# touched, so Requires=/After= erdos-thermal-guard.service still hold.
set -u
SCRIPT="${1:?usage: laptop-cutover.sh <chain-script-basename> <description>}"
DESC="${2:?usage: laptop-cutover.sh <chain-script-basename> <description>}"
UNIT=/etc/systemd/system/erdos-laptop-chain.service
CHAIN="$HOME/erdos-n70/$SCRIPT"

[ -x "$CHAIN" ] || { echo "REFUSING: $CHAIN missing or not executable"; exit 1; }

echo "--- guard must be running before we touch the chain"
systemctl is-active erdos-thermal-guard || { echo "REFUSING: thermal guard not active"; exit 1; }

echo "--- state files present here now"
for f in "$HOME"/erdos-n70/n*-state-b1*.json; do
  [ -e "$f" ] || continue
  python3 -c "
import json,sys
d=json.load(open(sys.argv[1]))
print('   %s n=%s b=%s-%s complete=%d' % (sys.argv[1].split('/')[-1], d['n'], d['min_b'], d['max_b'], len(d['complete'])))
" "$f"
done

sudo -n tee "$UNIT" >/dev/null <<UNITEOF
[Unit]
Description=Erdos1016 laptop GPU exhaustion chain ($DESC)
After=multi-user.target

[Service]
Type=simple
User=j
Group=j
WorkingDirectory=/home/j/erdos-n70/search/shapecsp
ExecStart=/bin/bash $CHAIN
# The GPU feeder needs to stay responsive or the card goes idle between units;
# it costs about 0.002 of a core, so it is not what competes with other agents.
Nice=0
CPUWeight=200
# This is a FINITE pipeline, not a daemon, so it must not relaunch on success.
Restart=on-failure
RemainAfterExit=yes
# MUST stay above gpu_state_runner.py's --lock-stale default of 180s.  systemd
# stops this unit with SIGTERM, which CPython does not turn into an exception,
# so the interpreter exits without running the finally: that unlinks the lock.
# Restarting inside the stale window makes the new runner see a live-looking
# lock and exit 2 immediately.
RestartSec=200
StandardOutput=append:/home/j/erdos-n70/chain-laptop.log
StandardError=append:/home/j/erdos-n70/chain-laptop.log

[Install]
WantedBy=multi-user.target
UNITEOF

sudo -n systemctl daemon-reload || { echo "daemon-reload FAILED"; exit 1; }
echo "--- unit now:"
systemctl cat erdos-laptop-chain --no-pager | grep -E 'ExecStart|Description'
echo "--- thermal drop-in still present:"
systemctl cat erdos-laptop-chain --no-pager | grep -E 'Requires|After=erdos'
sudo -n systemctl start erdos-laptop-chain || { echo "START FAILED"; exit 1; }
sleep 5
echo "--- status"
systemctl is-active erdos-laptop-chain erdos-thermal-guard
pgrep -af gpu_state_runner.py || echo "runner not up yet"
