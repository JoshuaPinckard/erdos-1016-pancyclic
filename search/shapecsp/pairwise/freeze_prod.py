"""Export the committed (f63f9f3) pairwise modules byte-exactly into
search/shapecsp/pairwise-prod and report LF-normalised md5s of the committed
blobs, the working tree and the frozen copies."""
import hashlib
import os
import subprocess
import sys

REPO = r"C:\Users\ToolsEnabled-Dev\Desktop\erdos1016"
COMMIT = sys.argv[1] if len(sys.argv) > 1 else "f63f9f3"
FILES = ["gpu_state_runner_pairwise.py", "gpu_search_pairwise.py", "pairwise_tables.py",
         "partition_tier.py", "verify_tier_exhaustion_pairwise.py", "verify_tier_combined.py",
         "check_tables_integrity.py", "status_pairwise.py", "census_level.py", "set_unit_prefix.py"]
PROD = os.path.join(REPO, "search", "shapecsp", "pairwise-prod")
DEV = os.path.join(REPO, "search", "shapecsp", "pairwise")
os.makedirs(PROD, exist_ok=True)


def md5lf(data):
    return hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()


rows = []
for f in FILES:
    blob = subprocess.check_output(["git", "-C", REPO, "show", f"{COMMIT}:search/shapecsp/pairwise/{f}"])
    with open(os.path.join(PROD, f), "wb") as fh:
        fh.write(blob)
    dev = open(os.path.join(DEV, f), "rb").read()
    rows.append((f, md5lf(blob), md5lf(dev), md5lf(open(os.path.join(PROD, f), "rb").read()), len(blob)))

with open(os.path.join(PROD, "README.md"), "w", encoding="ascii", newline="\n") as fh:
    fh.write(f"# Frozen production snapshot of search/shapecsp/pairwise at commit {COMMIT} (2026-09-19).\n"
             "The live chains run the runner from here so that in-place edits under ../pairwise cannot\n"
             "reach a tier that starts hours later. Tables, partitions and state files stay under ../pairwise.\n"
             "Do not edit; re-freeze from a commit with _mgr_freeze_prod.py.\n")

print(f"{'file':38} {'committed':32} {'worktree':32} {'frozen':32} bytes  worktree==committed")
for f, c, d, p, nb in rows:
    print(f"{f:38} {c} {d} {p} {nb:6d}  {c == d}")
assert all(c == p for _, c, _, p, _ in rows), "frozen copy differs from the committed blob"
print("frozen copies are byte-exact to", COMMIT)
