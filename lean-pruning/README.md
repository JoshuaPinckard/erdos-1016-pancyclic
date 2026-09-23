Lean 4.33.1 verification of the arithmetic and Hall pruning used by Erdos1016.

Bounds.lean proves that a represented cycle's length lies in the computed
interval, that raising arc lower bounds shrinks intervals, and that raising
two bounds to the values in a solution preserves that solution.

Hall.lean proves the necessary Hall counting inequalities from coverage by
the supplied cycle forms, their monotonicity under raising lower bounds,
soundness of pairwise rejection, correctness of the executable hallCheck,
and rejection of all arc values beyond a failing pairwise threshold.

The theorems are general in the number of arcs, cycle masks, chord counts,
and target size. Their dependencies are only propext, Classical.choice,
and Quot.sound. No proof holes or native_decide are used.

These are conditional on the supplied cycle forms covering the graph's
cycles. They do not establish the completeness of shapes.py, equivalence of
the Python/CUDA implementation on every input, or certify historical GPU
execution. Existing graph witnesses checked in the original Lean project
are separate results and have not been rebuilt here.

Reproduce on this laptop from this directory:

    python3 check.py

(On the original laptop this ran inside a resource limiter, `math_low_impact.py`, which is not part of this repository.)

A different Lean 4.33.1 executable may be supplied as the first argument to
check.py. The Lean files themselves use only the bundled standard library.
The Python comparisons expect ../search/shapecsp/bound.py, shapes.py and the
existing census manifests. They perform no searches or GPU work.

checks/verification.json binds the source hashes and verification results.
The current run checks 42 production arithmetic cases (3,082 form intervals),
four full small Hall decisions, two hand-checkable graph examples, and two
deliberately incorrect bounds. It compiles both proof modules and refuses
unexpected axioms or missing proof output. Tests tie sampled executable
arithmetic to the proved definitions; they are not a formal translation
proof for the Python/CUDA programs.

The local Linux compiler archive is pinned by toolchain-source.json to the
official release and its SHA-256. The original production search, result
claims, and search checkpoints have not been edited.

