#!/bin/bash
# Laptop-side unattended claim finalization for the tiers whose table files
# live only on this machine (level 71 now; 72..89 later).  Every POLL seconds,
# for each tier N:B without ~/erdos-n70/verification/nN-bB-combined.json: run
# the fast monitoring verifier from the frozen pairwise-prod snapshot; when it
# exits 0 run the CLAIM tool (verify_tier_combined.py --rebuild -1, every shape
# rebuilt from its census row) at nice 19 and keep its JSON.  Whole-tier states
# (no --only-shapes) need no unrestricted state.  Start detached:
#   setsid nohup bash finalize-laptop.sh > finalize-laptop.log 2>&1 < /dev/null &
set -u
R="$HOME/erdos-n70"; BASE="$R/search/shapecsp"; PW="$BASE/pairwise"; PROD="$BASE/pairwise-prod"
PY="$HOME/erdos-gpu-n70-builder-t92/venv/bin/python"
OUT="$R/verification"; mkdir -p "$OUT"
POLL=${POLL:-600}
TIERS=${TIERS:-"71:12 71:11 71:10 71:9 71:8 71:7 71:6"}
say() { echo "[finalize-laptop] $(date '+%F %T') $*"; }
say "start tiers=$TIERS poll=${POLL}s prod=$PROD pid=$$"
while true; do
  pending=0
  for t in $TIERS; do
    N=${t%%:*}; B=${t##*:}
    final="$OUT/n$N-b$B-combined.json"
    [ -f "$final" ] && continue
    pending=$((pending + 1))
    state="$PW/pairwise-state-n$N-b$B.json"
    [ -f "$state" ] || continue
    if [ -f "$BASE/gpu-blast/n$N.jsonl" ]; then SRC="$BASE/gpu-blast"; TAB="$PW/tables"; else SRC="$PW/gpu-blast-ext"; TAB="$PW/tables-ext"; fi
    if nice -n 19 "$PY" "$PROD/verify_tier_exhaustion_pairwise.py" "$SRC" "$state" --n "$N" --b "$B" --tables "$TAB" > /dev/null 2>&1; then
      say "n=$N b=$B pairwise units complete; running the claim tool with --rebuild -1"
      nice -n 19 "$PY" "$PROD/verify_tier_combined.py" "$SRC" --n "$N" --b "$B" --pairwise-state "$state" --tables "$TAB" --rebuild -1 > "$final.part" 2> "$final.err"
      rc=$?
      mv -f "$final.part" "$final"
      say "n=$N b=$B claim tool exit=$rc $(grep -o '"exact_match": [a-z]*' "$final") $(grep -o '"rebuilt_mismatches": [0-9]*' "$final") -> $final"
    fi
  done
  [ "$pending" -eq 0 ] && { say "all tiers have claim files; exiting"; break; }
  sleep "$POLL"
done
