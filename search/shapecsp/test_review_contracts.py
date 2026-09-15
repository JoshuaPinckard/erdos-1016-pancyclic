"""Result-integrity contracts for the level driver and the SAT control.

Written by the independent reviewer (Builder c3a46073) against the snapshot that
FAILED four of them; kept here as the regression that holds the fixes in place.
The only change from that original is selecting the Linux `bb` binary when it is
present, so the suite runs on both machines.

The four they reproduce: a child that exits non-zero counted as sat=0; empty
child output counted as sat=0; a SAT accepted although the independent graph
checker rejects it; and the SAT control printing FAILED while exiting 0.
"""
import contextlib
import hashlib
import io
import os
from pathlib import Path
import pickle
import re
import runpy
import subprocess
import sys
import unittest
from unittest.mock import patch

import bound as B
import shapes as S
import verify as V

HERE = Path(__file__).resolve().parent
BB = HERE / "bb"            # Linux build
if not BB.exists():
    BB = HERE / "bb.exe"    # Windows build
DATA = []
for b, ch in S.shapes(2):
    forms = sorted(set(S.cycle_forms(b, ch)))
    iv, lows = B.intervals(b, ch, forms=forms)
    DATA.append((len(forms) + 2, b, ch, forms, lows, iv))
with (HERE / "forms-k2.pkl").open("wb") as fh:
    pickle.dump(DATA, fh)
ELIG = [d for d in DATA if d[0] >= 8 and sum(d[4]) <= 8 and B.hall_ok(d[5], 8)]
assert ELIG


def level_with_result(returncode, stdout):
    result = subprocess.CompletedProcess([], returncode, stdout, "injected failure" if returncode else "")
    output = io.StringIO()
    try:
        with patch.object(sys, "argv", [str(HERE / "level.py"), "2", "8", "1000"]), \
                patch("subprocess.run", return_value=result), contextlib.redirect_stdout(output):
            runpy.run_path(str(HERE / "level.py"), run_name="__main__")
    except SystemExit as e:
        # A clean level ends in sys.exit(0), so treating EVERY SystemExit as a
        # rejection made all three level.py contracts below vacuously true: they
        # passed with the gates deleted.  Only a non-zero status is a rejection.
        return output.getvalue(), bool(e.code)
    except (ValueError, RuntimeError, subprocess.CalledProcessError):
        return output.getvalue(), True
    return output.getvalue(), False


class ReviewContracts(unittest.TestCase):
    def test_nonzero_solver_exit_cannot_certify_zero_sat_zero_gaveup(self):
        out, rejected = level_with_result(23, "".join(f"SHAPE {i} UNSAT nodes=1\n" for i in range(1, len(ELIG) + 1)))
        self.assertTrue(rejected or not re.search(r"LEVEL .*sat=0 gaveup=0", out), out)

    def test_missing_results_cannot_certify_zero_sat_zero_gaveup(self):
        out, rejected = level_with_result(0, "")
        self.assertTrue(rejected or not re.search(r"LEVEL .*sat=0 gaveup=0", out), out)

    def test_invalid_witness_is_not_reported_as_sat(self):
        b = ELIG[0][1]
        arcs = [2, 2, 4]
        self.assertEqual(b, len(arcs))
        self.assertEqual(sum(arcs), 8)
        self.assertTrue(all(a >= low for a, low in zip(arcs, ELIG[0][4])))
        self.assertFalse(V.check(b, ELIG[0][2], arcs)[0])
        invalid = "SHAPE 1 SAT n=8 arcs=" + ",".join(map(str, arcs)) + " nodes=1\n"
        invalid += "".join(f"SHAPE {i} UNSAT nodes=1\n" for i in range(2, len(ELIG) + 1))
        out, rejected = level_with_result(0, invalid)
        self.assertTrue(rejected or not re.search(r"LEVEL .*sat=1", out), out)

    def test_satcheck_budget_failure_has_nonzero_exit(self):
        result = subprocess.run([sys.executable, "-B", str(HERE / "satcheck.py"), "0"],
                                cwd=HERE, text=True, capture_output=True, timeout=30)
        self.assertIn("SATCHECK FAILED", result.stdout)
        self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_native_solver_propagates_gaveup(self):
        _, b, ch, forms, lows, _ = ELIG[0]
        payload = " ".join(map(str, [b, len(forms)] + lows)) + "\n"
        payload += "".join(f"{m} {c}\n" for m, c in forms)
        result = subprocess.run([str(BB), "8", "0", "2"], input=payload,
                                text=True, capture_output=True, check=True, timeout=10)
        self.assertIn(" GAVEUP ", result.stdout)
        self.assertNotIn(" UNSAT ", result.stdout)

    def test_known_native_witness_is_independently_valid(self):
        _, b, ch, forms, lows, _ = ELIG[0]
        payload = " ".join(map(str, [b, len(forms)] + lows)) + "\n"
        payload += "".join(f"{m} {c}\n" for m, c in forms)
        result = subprocess.run([str(BB), "8", "1000000", "2"], input=payload,
                                text=True, capture_output=True, check=True, timeout=10)
        match = re.fullmatch(r"SHAPE 1 SAT n=(\d+) arcs=([\d,]+) nodes=(\d+)\n", result.stdout)
        self.assertIsNotNone(match, result.stdout)
        n = int(match.group(1))
        arcs = list(map(int, match.group(2).split(",")))
        ok, verified_n, _, why = V.check(b, ch, arcs)
        self.assertTrue(ok, why)
        self.assertEqual(n, verified_n)


class LedgerProvenanceContracts(unittest.TestCase):
    """The resume ledger must name the build that wrote it, and refuse any other.

    Added after a solver binary was swapped under a running hunt: the ledger's
    UNSAT rows then span two builds with no boundary, and a non-existence claim is
    exactly a pile of UNSAT rows.  These call hunt.py for real, with k=2 at a
    cutoff above t_2 = 8, so the level is decided instantly and the assertions are
    about the ledger rather than about the search.
    """

    LEDGER = HERE / "hunt-k2-n9-range.done"

    def setUp(self):
        self.LEDGER.unlink(missing_ok=True)

    tearDown = setUp

    def hunt(self):
        return subprocess.run([sys.executable, "-B", str(HERE / "hunt.py"),
                               "2", "9", "1", "1000000", "0"],
                              cwd=HERE, text=True, capture_output=True, timeout=120)

    def test_fresh_ledger_records_the_solver_sha256(self):
        self.assertEqual(self.hunt().returncode, 0)
        head = self.LEDGER.read_text().splitlines()[0]
        digest = hashlib.sha256(BB.read_bytes()).hexdigest()
        self.assertIn(digest, head, head)
        self.assertTrue(any(l.split()[1:2] == ["UNSAT"]
                            for l in self.LEDGER.read_text().splitlines()[1:]))

    def test_resume_refuses_a_ledger_written_by_another_build(self):
        self.assertEqual(self.hunt().returncode, 0)
        rows = self.LEDGER.read_text().splitlines()
        self.LEDGER.write_text("\n".join(["# solver sha256=" + "0" * 64] + rows[1:]) + "\n")
        before = self.LEDGER.read_text()
        r = self.hunt()
        self.assertNotEqual(r.returncode, 0, r.stdout)
        self.assertEqual(self.LEDGER.read_text(), before, "refused run still wrote rows")

    def test_resume_refuses_a_ledger_with_no_build_recorded(self):
        self.LEDGER.write_text("0 UNSAT\n")
        r = self.hunt()
        self.assertNotEqual(r.returncode, 0, r.stdout)
        self.assertEqual(self.LEDGER.read_text(), "0 UNSAT\n", "refused run still wrote rows")


if __name__ == "__main__":
    unittest.main(verbosity=2)
