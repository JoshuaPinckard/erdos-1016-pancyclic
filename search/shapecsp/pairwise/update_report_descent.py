"""Regenerate the claim tables and the Status section of
papers/REPORT-k6-gpu-descent-71-88.md from the claim files under
papers/verification.

Levels 71..88 decide t_6 (t_6 = 67 unless one of them holds a 6-chord
pancyclic graph); 89 and 88 are also the GPU replication of two CPU-refuted
levels (T573).  Every tier of these levels ran under the pairwise plan with a
whole-tier state, so the census is pairwise/gpu-blast-ext/n{N}.jsonl, every
claim file is n{N}-b{B}-combined.json, and there are no unrestricted claims
(--exhausted-b-below 0).

Usage: python update_report_descent.py            (rewrite the report, print the verdicts)
       python update_report_descent.py --dry-run  (print only)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
REPORT = REPO / "papers" / "REPORT-k6-gpu-descent-71-88.md"
CLAIMS = REPO / "papers" / "verification"
LEVELS = list(range(89, 70, -1))          # 89, 88, ..., 71
BRACKET = list(range(88, 70, -1))         # the levels that decide t_6
MARKER = "<!-- render_claims.py output"
END_MARKER = "<!-- end render_claims.py output -->"


def render() -> str:
    return subprocess.run(
        [sys.executable, str(HERE / "render_claims.py"), "--source", str(HERE / "gpu-blast-ext"),
         "--levels", ",".join(map(str, LEVELS)), "--exhausted-b-below", "0"],
        capture_output=True, text=True, check=True).stdout.strip()


def hits_by_level() -> dict[int, list]:
    """Every hit recorded in any combined claim file of the descent levels.
    A hit here is a runner-found, verifier-confirmed pancyclic composition; the
    claim tool refuses exact_match on a tier whose hits fail the independent
    verifier, so a hit that reaches a claim file is real."""
    out: dict[int, list] = {}
    for f in sorted(CLAIMS.glob("n*-b*-combined.json")):
        try:
            j = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        n = int(j.get("n", -1))
        if n in LEVELS and j.get("hits"):
            out.setdefault(n, []).extend(j["hits"])
    return out


def status_text(verdicts: list[str], hits: dict[int, list]) -> str:
    exhausted = {int(m.group(1)) for l in verdicts if (m := re.match(r"\* n = (\d+): EXHAUSTED", l))}
    done = [n for n in BRACKET if n in exhausted]
    open_levels = [n for n in BRACKET if n not in exhausted]
    lines = ["## Status", "", *verdicts, ""]
    if hits:
        top = max(hits)
        above_done = all(n in exhausted for n in BRACKET if n > top)
        lines.append(f"A 6-chord pancyclic graph was found at n = {top} ({len(hits[top])} hit(s) in the claim files), "
                     f"so t_6 >= {top}" + (f" and, every level above {top} through 88 being exhausted, t_6 = {top} exactly."
                                            if above_done else f"; levels above {top} still open: "
                                            + ", ".join(str(n) for n in BRACKET if n > top and n not in exhausted) + "."))
        lower = sorted(n for n in hits if n != top)
        if lower:
            lines.append("Further witnesses at n = " + ", ".join(map(str, lower)) + ".")
    elif not open_levels:
        lines.append("Every level 71..88 is exhausted with zero hits. Together with h(68) = h(69) = h(70) >= 7 "
                     "(papers/REPORT-k6-gpu-pairwise-68-70.md) and the CPU refutation of 89..111, this gives "
                     "t_6 = 67 exactly: the family witness at n = 67 is the largest cycle a 6-chord pancyclic graph can have.")
    else:
        lines.append(f"{len(done)} of 18 bracket levels exhausted with zero hits"
                     + (" (" + ", ".join(map(str, done)) + ")" if done else "")
                     + "; t_6 = 67 or lies in {" + ", ".join(map(str, sorted(open_levels))) + "}.")
    if 89 in exhausted:
        lines.append("Level 89 is also exhausted on the GPU, agreeing with the CPU descent (T573 cross-check).")
    lines.append("The T ledger (T3, T543, T573) carries the checkpoints.")
    return "\n".join(lines) + "\n"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    out = render()
    verdicts = [l for l in out.splitlines() if l.startswith("* n = ")]
    hits = hits_by_level()
    status = status_text(verdicts, hits)
    if not args.dry_run:
        text = REPORT.read_text(encoding="utf-8")
        start = text.index(MARKER)
        start = text.index("\n", start) + 1
        end = text.index(END_MARKER)      # hand-written text after the block survives
        text = text[:start] + "\n" + out + "\n\n" + text[end:]
        text = text[:text.index("## Status")] + status
        REPORT.write_text(text, encoding="utf-8", newline="\n")
    print(status)


if __name__ == "__main__":
    main()
