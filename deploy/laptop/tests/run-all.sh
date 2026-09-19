#!/bin/bash
# All laptop-thermal tests.  Run before anything here is pointed at the laptop.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
rc=0
for t in test-thermal-guard.sh test-install.sh test-catcher.sh; do
  printf '\n=== %s ===\n' "$t"
  bash "$HERE/$t" || rc=1
done
printf '\n=== overall: %s ===\n' "$([ $rc -eq 0 ] && echo PASS || echo FAIL)"
exit $rc
