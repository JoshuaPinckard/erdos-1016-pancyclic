#!/bin/bash
# Per-tier GPU cost of a rank, measured on this one card from the whole chain log.
#
# A rank is not a constant amount of work: a b=12 shape carries one more chord
# than a b=11 shape and the kernel does more per candidate.  The forecast needs
# that as a multiplier, and a multiplier taken from two or three units at the
# head of one tier is not good enough to choose a split with -- the top two
# candidate splits cross over at about b12=1.28.
#
# Method: the log interleaves "[chain] n=N b=B starting" markers with one JSON
# line per completed unit.  Attribute each unit to the most recent marker, keep
# only FULL 5e10-rank units so unit size cannot confound the comparison, and
# report the distribution rather than a mean -- thermal-guard freezes show up
# as a long right tail and must not be allowed to inflate the cost of whichever
# tier happened to be running when the card got hot.  The median is the
# statistic used; it is insensitive to those stalls.
set -u
LOG="${1:-$HOME/erdos-n70/chain-laptop.log}"

python3 - "$LOG" <<'PYEOF'
import json, re, statistics, sys

lines = open(sys.argv[1], encoding="utf-8", errors="replace").read().splitlines()
UNIT = 50_000_000_000
cur = None
per_tier = {}
prev_tested = {}

for ln in lines:
    m = re.match(r"\[chain\] n=(\d+) b=(\d+) starting", ln)
    if m:
        cur = (int(m.group(1)), int(m.group(2)))
        prev_tested[cur] = 0
        continue
    ln = ln.strip()
    if not ln.startswith("{") or cur is None:
        continue
    try:
        rec = json.loads(ln)
    except ValueError:
        continue
    if "gpu_seconds" not in rec or "tested_this_invocation" not in rec:
        continue
    size = rec["tested_this_invocation"] - prev_tested.get(cur, 0)
    prev_tested[cur] = rec["tested_this_invocation"]
    # Only full units: a short tail unit is cheaper for reasons that have
    # nothing to do with the tier.
    if size != UNIT:
        continue
    per_tier.setdefault(cur, []).append(rec["gpu_seconds"])

print(f"{'tier':<10} {'n':>5} {'median':>8} {'mean':>8} {'p10':>8} {'p90':>8} {'min':>8}")
med = {}
for key in sorted(per_tier):
    v = sorted(per_tier[key])
    if not v:
        continue
    n, b = key
    med[key] = statistics.median(v)
    p10 = v[max(0, int(0.10 * len(v)) - 1)]
    p90 = v[min(len(v) - 1, int(0.90 * len(v)))]
    print(f"n{n} b{b:<6} {len(v):>5} {med[key]:>8.2f} "
          f"{statistics.fmean(v):>8.2f} {p10:>8.2f} {p90:>8.2f} {v[0]:>8.2f}")

print()
# Pooling medians across tiers measured in DIFFERENT clock regimes produced a
# wrong answer once already: n70 b11's 2253 units span 2026-09-17..19, which
# includes time before the fan pin and thermal guard settled the card at
# 1395 MHz, so its median (48.00) reflects a faster card rather than a cheaper
# tier.  Pooled against today's b11 tiers that inflated the b12 multiplier to
# 1.37.  Only ratios formed WITHIN one level are reported, because those two
# tiers ran adjacently and share a clock regime; cross-level comparison is
# reported separately and labelled as confounded.
print("b12/b11 ratio, WITHIN a level (tiers ran adjacently, same clock regime):")
any_ratio = False
for n in sorted({k[0] for k in med}):
    if (n, 11) in med and (n, 12) in med:
        any_ratio = True
        print(f"  n{n}: {med[(n, 12)]:.2f} / {med[(n, 11)]:.2f} = "
              f"{med[(n, 12)] / med[(n, 11)]:.4f}")
if not any_ratio:
    print("  none available: this log has no level with BOTH a b=11 and a b=12")
    print("  tier recorded. Have: " + ", ".join(f"n{n} b{b}" for n, b in sorted(med)))

print()
print("b=11 medians across levels (a spread here is NOT necessarily a level")
print("effect -- check whether the samples share a clock regime):")
for n in sorted({k[0] for k in med}):
    if (n, 11) in med:
        print(f"  n{n} b11 {med[(n, 11)]:.2f} gpu_s  ({len(per_tier[(n, 11)])} units)")
PYEOF
