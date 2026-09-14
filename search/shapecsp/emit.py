"""Emit shape records for bb.exe: `python emit.py k [target] [shard nshards]`.

Record format per shape: b m lo_0..lo_{b-1} then m pairs (arcmask chordcount).
Shapes whose cap (#distinct forms + 2) is below `target`, or which already fail
the Hall bound at `target`, are dropped -- both are rigorous necessary
conditions, so dropping them cannot lose a solution.  The kept shapes are listed
on stderr in the same order, so SHAPE i in bb.exe's output maps back.
"""
from __future__ import annotations
import sys
import shapes as S
import bound as B

k = int(sys.argv[1])
target = int(sys.argv[2]) if len(sys.argv) > 2 else 3
shard, nsh = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (0, 1)

kept = 0
cap_drop = hall_drop = 0
for idx, (b, ch) in enumerate(S.shapes(k)):
    forms = sorted(set(S.cycle_forms(b, ch)))
    if len(forms) + 2 < target:
        cap_drop += 1
        continue
    iv, lows = B.intervals(b, ch, forms=forms)
    if target > 3 and not B.hall_ok(iv, target):
        hall_drop += 1
        continue
    if idx % nsh != shard:
        continue
    kept += 1
    print(b, len(forms), *lows)
    for mask, c in forms:
        print(mask, c)
    print(f"{kept} {b} {ch}", file=sys.stderr)
print(f"# kept={kept} cap_dropped={cap_drop} hall_dropped={hall_drop}", file=sys.stderr)
