# GPU-result corroboration

## 1. Colex unranking

Independent harness: [unrank_test.c](construction/unrank_test.c), compiled with the specified WinLibs GCC and run once at BelowNormal priority. It implements the kernel’s rule directly: for (i=r\) down to 1, choose the largest (c) with (\binom ci\le N), subtract (\binom ci), and check increasing indices and the colex rank sum.

Output is preserved in [unrank.out](construction/unrank.out). Every tested case passed (`failures=0`):

```text
r=2: M=10 all 45; M=50 all 1,225; M=200 all 19,900; M=779 random 1,000,000
r=3: M=10 all 120; M=50 all 19,600; M=200 all 1,313,400; M=779 random 1,000,000
r=4: M=10 all 210; M=50 all 230,300; M=200 all 64,684,950; M=779 random 1,000,000
SUMMARY seed=20260914 failures=0
```

The harness reports `total=15,226,095,626` for \(\binom{779}{4}\). This differs from the task prompt’s `15,147,912,850`; direct integer computation gives 15,226,095,626, so the prompt value is recorded as a discrepancy.

## 2. Random direct-DFS corroboration

The random tests use [indep.c](construction/indep.c), whose cycle detector is direct DFS over adjacency (not cycle-space XOR). Each sample chooses a uniformly random 5-subset (or 4-subset for the control) from the chord list using a seeded xorshift generator. No GPU was run.

For (n=41,k=5), two independent 1,000,000-sample runs found zero pancyclic graphs:

```text
RANDOM n=41 k=5 count=1000000 seed=410051 pancyclic=0 cpu_seconds=102.387
RANDOM n=41 k=5 count=1000000 seed=410052 pancyclic=0 cpu_seconds=125.914
```

Combined: 2,000,000 samples, 0 hits. Output copies are [random41-1.out](construction/random41-1.out) and [random41-2.out](construction/random41-2.out), with aggregate log [random41.log](construction/random41.log).

Positive control (n=24,k=4), 2,000,000 samples, found one pancyclic graph:

```text
RANDOM n=24 k=4 count=2000000 seed=240051 pancyclic=1 cpu_seconds=53.304
```

Output: [random24.out](construction/random24.out). This is consistent with the independently enumerated positive population and demonstrates that the random direct-DFS path can detect a pancyclic sample.

## Verdict

The colex unranking rule passed all requested invariants and all exhaustive small domains tested. The n=41 random corroboration found no 5-chord pancyclic sample, while the n=24 positive control found one. Random sampling does not prove nonexistence; the exhaustive n=25 direct-DFS result remains the stronger negative evidence.
