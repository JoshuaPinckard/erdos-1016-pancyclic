"""Mutation check for the four result-integrity gates in level.py / satcheck.py.

Per gate: disable it by exact textual substitution, run the contract test that
covers it and require it to go RED *for the predicted reason* -- an assertion
failure, `FAILED (failures=1)` -- then restore the file from a byte copy taken
before the edit and require the same test to report `OK`.

Two disciplines this file exists to enforce, both learned the hard way here:

  * Every substitution asserts its anchor occurs exactly once and refuses to
    write a no-op.  This repository has already shipped a silent `str.replace`
    that matched nothing; a mutation that never lands reports a dead gate as live.
  * A RED that ERRORS is not a RED.  When the mutant crashes, the test stops for
    a reason unrelated to the gate, and the gate's real protection is untested.
    So `errors=1` is reported as BROKEN, not as a pass.

The mutants reproduce the ORIGINAL defects rather than merely deleting an `if`:
that is what the gate has to stop, and a deleted `if` that happens to crash
proves only that crashing is fail-closed.

`python mutation-check.py` -- exits non-zero unless every gate goes RED then GREEN.
"""
from __future__ import annotations
import pathlib, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
SUITE = HERE / "test_review_contracts.py"

ACCEPT_UNCHECKED = """            # MUTANT: take the solver's SAT claim without the independent check
            nv = int(line.split()[3].split("=")[1])
            arcs = [int(x) for x in line.split()[4].split("=")[1].split(",")]
            che, expl = [], "unchecked\""""

GATES = [
    ("level.py rejects a non-zero solver exit", "level.py",
     [("    if p.returncode != 0:", "    if False:  # MUTANT: gate disabled")],
     "test_nonzero_solver_exit_cannot_certify_zero_sat_zero_gaveup"),

    ("level.py rejects a missing terminal record", "level.py",
     [("    if missing:", "    if False:  # MUTANT: gate disabled"),
      # Without this second edit the mutant dies on KeyError, which would be a
      # crash rather than the false certificate the gate actually prevents.
      ("    for i in range(1, len(elig) + 1):\n        line, (cap, b, ch, forms, lows, iv) = recs[i], elig[i - 1]",
       "    for i in sorted(recs):  # MUTANT: report only what came back\n        line, (cap, b, ch, forms, lows, iv) = recs[i], elig[i - 1]")],
     "test_missing_results_cannot_certify_zero_sat_zero_gaveup"),

    ("level.py rejects a SAT the graph checker refuses", "level.py",
     [('            got, why = V.check_record(line, b, ch, lows, cap, n)\n'
       '            if why is not None:\n'
       '                fail(f"shape {i} b={b} chords={ch}: {why}")\n'
       '            nv, arcs, che, expl = got',
       ACCEPT_UNCHECKED)],
     "test_invalid_witness_is_not_reported_as_sat"),

    ("satcheck.py's exit status carries its verdict", "satcheck.py",
     [("sys.exit(0 if not fails else 1)", "sys.exit(0)  # MUTANT: gate disabled")],
     "test_satcheck_budget_failure_has_nonzero_exit"),

    # Added after a solver binary was swapped under a running hunt, leaving UNSAT
    # rows that no longer said which build decided them.
    ("hunt.py stamps the solver build into a fresh ledger", "hunt.py",
     # Single-line anchor deliberately: hunt.py is CRLF and level.py is LF, so a
     # multi-line anchor matches in one file and silently misses in the other.
     # The count assertion caught that rather than reporting a dead gate as live.
     [("if not seen:", "if False:  # MUTANT: gate disabled")],
     "LedgerProvenanceContracts.test_fresh_ledger_records_the_solver_sha256"),

    ("hunt.py refuses to resume a ledger from another build", "hunt.py",
     [("    if recorded != BB_SHA:", "    if False:  # MUTANT: gate disabled")],
     "LedgerProvenanceContracts.test_resume_refuses_a_ledger_written_by_another_build"),
]


def run(test):
    # A bare name is one of the reviewer's original contracts; a dotted one names
    # its class, for the contracts added since.
    test = test if "." in test else f"ReviewContracts.{test}"
    p = subprocess.run([sys.executable, "-B", str(SUITE), test],
                       cwd=HERE, text=True, capture_output=True, timeout=300)
    return p.returncode, (p.stderr.strip().splitlines() or [""])[-1]


def main():
    bad = []
    for label, fname, subs, test in GATES:
        path = HERE / fname
        original = path.read_bytes()
        text = original.decode()
        for anchor, mutant in subs:
            hits = text.count(anchor)
            if hits != 1:
                print(f"REFUSED {label}: anchor occurs {hits} times in {fname}, expected 1")
                bad.append(label)
                text = None
                break
            text = text.replace(anchor, mutant)
        if text is None:
            continue
        with tempfile.TemporaryDirectory() as tmp:
            backup = pathlib.Path(tmp) / fname
            backup.write_bytes(original)
            try:
                path.write_bytes(text.encode())
                assert path.read_bytes() != original, "mutation was a no-op"
                rc_red, why_red = run(test)
            finally:
                path.write_bytes(backup.read_bytes())
            assert path.read_bytes() == original, f"{fname} not restored"
        rc_green, why_green = run(test)
        ok = "FAILED (failures=1)" in why_red and rc_red != 0 and rc_green == 0 and why_green == "OK"
        print(f"{'OK    ' if ok else 'BROKEN'} {label}")
        for anchor, mutant in subs:
            print(f"         mutant  {anchor.splitlines()[0].strip()[:60]!r}"
                  f" -> {mutant.splitlines()[0].strip()[:60]!r}")
        print(f"         RED     {test}  exit={rc_red}  {why_red}")
        print(f"         GREEN   {test}  exit={rc_green}  {why_green}")
        if not ok:
            bad.append(label)
    print()
    print(f"MUTATION CHECK: {len(GATES)}/{len(GATES)} gates went RED (failures=1) when disabled "
          f"and GREEN when restored" if not bad else f"MUTATION CHECK FAILED for {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
