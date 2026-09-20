"""Splice the current render_claims.py output into papers/REPORT-k6-gpu-pairwise-68-70.md
between the '<!-- render_claims.py output' marker and the '## Provenance' heading,
and rewrite the Status section from the per-level verdict lines."""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
report = REPO / "papers" / "REPORT-k6-gpu-pairwise-68-70.md"
out = subprocess.run([sys.executable, str(HERE / "render_claims.py"), "--levels", "68,69,70"],
                     capture_output=True, text=True, check=True).stdout.strip()
text = report.read_text(encoding="utf-8")
start = text.index("<!-- render_claims.py output")
start = text.index("\n", start) + 1
# The generated block ends at its own end marker; anything written by hand
# between that marker and '## Provenance' (the Lean section, 2026-09-20) is
# kept.  Splicing up to '## Provenance' deleted that section once.
END = "<!-- end render_claims.py output -->"
end = text.index(END)
text = text[:start] + "\n" + out + "\n\n" + text[end:]
verdicts = [l for l in out.splitlines() if l.startswith("* n = ")]
complete = [l for l in verdicts if "EXHAUSTED" in l]
status = ("## Status\n\n" + "\n".join(verdicts) + "\n\n"
          + ("All three levels are complete: every tier of the census manifest at n = 68, 69, 70 is exhausted with zero hits, "
             "so h(n) > 6 for n = 68, 69, 70 and t_6 is 67 or lies in 71..88."
             if len(complete) == 3 else
             f"{len(complete)} of 3 levels complete; this file is regenerated as claim files land.")
          + "\nThe T ledger (T543, T573) carries the checkpoints.\n")
text = text[:text.index("## Status")] + status
report.write_text(text, encoding="utf-8")
print("\n".join(verdicts))
print("levels complete:", len(complete))
