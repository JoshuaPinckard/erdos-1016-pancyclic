#!/bin/bash
# Run ON THE LAPTOP as root (sudo) from the directory holding these files.
# Installs the thermal guard, trims the descent CPU grant from 4 to 3 cores,
# and (re)starts everything in the right order.
set -eu
install -m 0755 erdos-thermal-guard /usr/local/sbin/erdos-thermal-guard
install -m 0644 erdos-thermal-guard.service /etc/systemd/system/erdos-thermal-guard.service
mkdir -p /etc/systemd/system/erdos-descent.service.d
cat > /etc/systemd/system/erdos-descent.service.d/thermal.conf <<'CONF'
[Service]
# 2026-09-18: two thermal shutdowns in one day with 4 cores + GPU. Two cores
# is half the CPU heat; the level ledger resumes shape-by-shape either way.
CPUQuota=200%
CONF
systemctl daemon-reload
systemctl enable --now erdos-thermal-guard.service
systemctl restart erdos-descent.service
systemctl status --no-pager erdos-thermal-guard.service erdos-descent.service erdos-laptop-chain.service | grep -E "Active|Loaded" || true
tail -3 /home/j/erdos-thermal-guard.log
