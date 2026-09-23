#!/usr/bin/env python3
"""Reproduce the small Lean proofs, Python comparison, and negative controls.

Run inside math_low_impact.py on Linux. No GPU, searches, or table rebuilds.
"""
from pathlib import Path
import ast
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "search" / "shapecsp"
LEAN = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE / "lean-4.33.1-linux/bin/lean"
ART = HERE / "checks"
ART.mkdir(exist_ok=True)
sys.path.insert(0, str(BASE))
import bound as B
import shapes as S

env = dict(os.environ, LEAN_PATH=str(HERE))
allowed_axioms = {"propext", "Classical.choice", "Quot.sound"}


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def lean(file, output=None):
    cmd = [str(LEAN), "-j1", "-s8192", "-M1024"]
    if output:
        cmd += ["-o", str(output)]
    result = subprocess.run(cmd + [str(file)], cwd=HERE, env=env,
                            capture_output=True, text=True, timeout=90)
    return result


for name in ("Bounds", "Hall"):
    r = lean(HERE / (name + ".lean"), HERE / (name + ".olean"))
    (ART / (name + ".log")).write_text(r.stdout + r.stderr)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "sorryAx" not in r.stdout
    matches = list(re.finditer(r"depends on axioms: \[([^]]*)\]", r.stdout))
    assert len(matches) >= {"Bounds": 3, "Hall": 7}[name]
    for match in matches:
        assert set(match[1].split(", ")) <= allowed_axioms

cases = []
# Real positive controls, with small raised-bound variants.
for n, b, chords in [(8, 4, [(0,2),(1,3)]),
                     (14, 5, [(0,2),(0,3),(1,4)])]:
    forms = sorted(set(S.cycle_forms(b, chords)))
    _, lows = B.intervals(b, chords, forms)
    cases.append((n, b, forms, lows, True))
    raised = list(lows)
    raised[0] += n - sum(lows)
    cases.append((n, b, forms, raised, True))

# Arithmetic at actual production sizes and across all branch counts at n=71.
for n in (71, 85, 87, 88, 89):
    source = BASE / "pairwise/gpu-blast-ext" / f"n{n}.jsonl"
    if not source.exists():
        source = BASE / "gpu-blast" / f"n{n}.jsonl"
    rows = [json.loads(x) for x in source.read_text().splitlines()]
    for b in sorted({r["b"] for r in rows}):
        row = next(r for r in rows if r["b"] == b)
        forms = sorted(set(S.cycle_forms(b, [tuple(c) for c in row["chords"]])))
        lows = row["lows"]
        cases.append((n, b, forms, lows, False))
        raised = list(lows)
        slack = n - sum(raised)
        raised[0] += slack // 2
        raised[-1] += slack - slack // 2
        cases.append((n, b, forms, raised, False))

lines = ["import Hall", "open Erdos1016.Pruning",
         "set_option maxRecDepth 10000"]
expected, hall_expected = {}, {}
for index, (n, b, forms, lows, check_hall) in enumerate(cases):
    fs = "[" + ",".join("⟨%d,%d⟩" % f for f in forms) + "]"
    lines += [f"def forms{index} : List Form := {fs}",
              f"def lows{index} (i : Nat) : Nat := ({lows} : List Nat).getD i 0",
              f'#eval IO.println ("bounds{index}:[" ++ String.intercalate "," '
              f'(forms{index}.map (fun f => "(" ++ toString (lower (List.range {b}) lows{index} f) '
              f'++ "," ++ toString (upper (List.range {b}) {n} lows{index} f) ++ ")")) ++ "]")']
    intervals, _ = B.intervals(b, [], forms, lows)
    expected[index] = [(mu, n - nu) for mu, nu in intervals]
    if check_hall:
        lines.append(f'#eval IO.println ("hall{index}:" ++ toString '
                     f'(hallCheck (List.range {b}) forms{index} {n} lows{index}))')
        hall_expected[index] = B.hall_ok(intervals, n)

# Hand-checkable graph controls: a triangle is pancyclic; a bare square misses 3.
lines += [
    "example : hallCheck (List.range 3) [⟨7,0⟩] 3 (fun _ => 1) = true := by decide",
    "example : hallCheck (List.range 4) [⟨15,0⟩] 4 (fun _ => 1) = false := by decide",
]
fixtures = ART / "ProductionComparison.lean"
fixtures.write_text("\n".join(lines) + "\n")
r = lean(fixtures)
(ART / "production-comparison.log").write_text(r.stdout + r.stderr)
assert r.returncode == 0, r.stdout + r.stderr
got, hall_got = {}, {}
for line in r.stdout.splitlines():
    if line.startswith("bounds"):
        label, text = line.split(":", 1)
        got[int(label[6:])] = ast.literal_eval(text)
    elif line.startswith("hall"):
        label, text = line.split(":", 1)
        assert text in ("true", "false")
        hall_got[int(label[4:])] = text == "true"
assert got == expected, "Lean/Python interval mismatch or missing output"
assert hall_got == hall_expected, "Lean/Python Hall mismatch or missing output"
assert True in hall_got.values() and False in hall_got.values()

# Neither mutation changes the genuine source or an existing claim.
mutations = {
    "TooLargeLower": ("max 3 (selectedSum", "max 4 (selectedSum"),
    "TooSmallUpper": ("  n - (selectedSum", "  (n - 1) - (selectedSum"),
}
for name, (old, new) in mutations.items():
    source = (HERE / "Bounds.lean").read_text()
    assert source.count(old) == 1
    mutant = ART / (name + ".lean")
    mutant.write_text(source.replace(old, new))
    r = lean(mutant)
    (ART / (name + ".log")).write_text(r.stdout + r.stderr)
    assert r.returncode != 0 and "error:" in r.stdout, "Invalid bound was accepted"

report = {
    "lean_version": subprocess.check_output([str(LEAN), "--version"], text=True).strip(),
    "proof_modules": ["Bounds.lean", "Hall.lean"],
    "axioms": sorted(allowed_axioms),
    "proof_holes": 0,
    "production_arithmetic_cases": len(cases),
    "cycle_form_intervals_compared": sum(map(len, expected.values())),
    "production_hall_decisions_compared": len(hall_expected),
    "hand_checked_graph_examples": 2,
    "incorrect_bounds_rejected": list(mutations),
    "sha256": {str(p.relative_to(HERE)) if p.is_relative_to(HERE) else str(p): digest(p)
               for p in [HERE/"Bounds.lean", HERE/"Hall.lean", Path(__file__),
                         BASE/"bound.py", BASE/"shapes.py", fixtures]},
    "scope": "Proves the mathematical pruning condition and a Lean checker; comparison tests tie sampled production arithmetic to it.",
    "remaining": ["Graph-to-form census completeness", "Python/CUDA correspondence for every input and historical execution", "Whole-level nonexistence certificates"],
}
(ART / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))

