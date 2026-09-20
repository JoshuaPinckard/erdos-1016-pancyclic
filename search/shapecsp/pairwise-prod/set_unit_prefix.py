"""Rewrite unit_prefix in every tier manifest under <tables_dir>.

unit_prefix is the runner's unit size in prefix ranks.  It is NOT part of any
tables_sha256 (those cover the header and arrays of one shape only), so it can
be changed without rebuilding; it IS part of every plan hash, so every state
file written under the old size is refused afterwards, by design.

Usage: python set_unit_prefix.py <tables_dir> <new_unit_prefix>
"""
import json
import sys
from pathlib import Path

root, new = Path(sys.argv[1]), int(sys.argv[2])
for mp in sorted(root.glob("n*-b*/tier-manifest.json")):
    m = json.loads(mp.read_text(encoding="utf-8"))
    old = m["unit_prefix"]
    m["unit_prefix"] = new
    with mp.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(m, f, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps({"manifest": str(mp), "unit_prefix": {"old": old, "new": new}}))
