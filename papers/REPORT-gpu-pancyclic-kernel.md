# GPU pancyclicity search: exhaustive b<=7 exclusions, no new witness

## Result and limits

**No six-chord pancyclic witness was found at n=68, 69, or 70. The bracket
does not improve.** The larger blast evaluated 279,947,297,956 assignments
across every eligible shape, then a short completion exhausted the remaining
b=7 spaces. At each of these three n, every shape with at most seven branch
points is excluded by necessary bounds or complete legal-rank enumeration.

The b>=8 results are **sampled misses**. A bounded/sampled miss proves
nothing about non-existence in the unsearched space. These three levels
cannot establish t_6=67: larger n also require exclusion. No further b>=8
exhaustion was started.

Evidence: `search/shapecsp/gpu-blast/summary.json`, `"hits": []` at every
level; `gpu-b7/summary.json`, `"hits": []`; and
`gpu-b7/census-audit.json`, `"EXHAUSTED; no SAT"`.
Artifact paths abbreviated below are relative to `search/shapecsp/`.
These are computational exclusions using the validated GPU/model pipeline,
not independently checked formal proof certificates.

## Positive control: PASS, before every search

`gpu-run/controls.json`, `"positive_control": "PASS"`, records the same
composition-unranking kernel finding:

| n | Canonical shape | Correct arc lengths | Colex rank |
|---|---|---|---:|
| 67 | `(0,2)(0,8)(1,5)(3,9)(4,6)(7,10)` | `[1,1,1,1,9,18,28,1,1,1,5]` | 107479052940 |
| 56 | `(0,1)(0,3)(0,6)(2,4)(4,5)(5,6)` | `[19,18,1,1,3,5,9]` | 6746008 |

The n=67 graph is exactly `(0,2)(0,60)(1,13)(3,61)(4,31)(59,62)`.
The n=56 canonical graph is
`(0,19)(0,38)(0,47)(37,39)(39,42)(42,47)`, dihedrally equivalent to the
supplied witness. Both passed `search/verify.py`'s `pancyclic` function,
which enumerates NetworkX simple cycles. GPU flags and arc outputs agreed
with that verifier on **44 sampled assignments, zero mismatches**:
first rank, last rank, and 20 seeded ranks per control shape.
These are targeted witness-rank controls, not exhaustive discoveries from
rank zero. The blast and b=7 completion repeated these controls first;
their respective `controls.json` files preserve the results.

Hand-run CLI evidence in `gpu-manual-verification.txt`:

```text
67 [(0, 2), (0, 60), (1, 13), (3, 61), (4, 31), (59, 62)] pancyclic
56 [(0, 2), (0, 53), (1, 39), (20, 39), (39, 48), (48, 53)] pancyclic
68 [(0, 2), (0, 61), (1, 13), (3, 62), (4, 31), (60, 63)] NOT pancyclic
```

The artifact includes full cycle-length lists. The n=68 extension misses
length 33. The verifier CLI exits zero for a checked negative graph too;
the verdict, not exit code alone, determines pancyclicity. The GPU suite
also confirms all 27 supplied family witnesses at n=41..67.

## Measured throughput and resources

Desktop: NVIDIA GeForce RTX 5060 Ti; CuPy 14.2.0. The larger pass used at
most 16,777,216 ranks per eligible shape, exhausting smaller spaces.
Fresh `S.shapes(6)` enumeration produced **21,878 shapes**, largest b=12.
Each n was filtered separately; Hall eligibility was not assumed monotone.

| n | Eligible shapes | Larger-blast assignments | Blocking launch/completion seconds | Level wall seconds | Assignments/s |
|---|---:|---:|---:|---:|---:|
| 68 | 6,059 | 101,642,323,675 | 88.814 | 93.211 | 1.14444 billion |
| 69 | 5,648 | 94,747,409,754 | 96.756 | 113.859 | 0.97924 billion |
| 70 | 4,981 | 83,557,564,527 | 89.989 | 107.571 | 0.92853 billion |

Timing is host monotonic time from launch through blocking CUDA-event
completion, not an isolated device-event benchmark. Source:
`gpu-blast/summary.json`, `"gpu_seconds"` and `"wall_seconds"`.

The resource audit selects samples within each level's timestamps:

| n | Samples | GPU mean / median / max | Search child CPU mean / max |
|---|---:|---|---|
| 68 | 88 | 96.55% / 100% / 100% | 0.192% / 3.975% |
| 69 | 105 | 69.81% / 96% / 100% | 0.143% / 0.550% |
| 70 | 99 | 72.90% / 95% / 100% | 0.135% / 0.550% |

The n=68 blast sustained approximately 1.14e9 assignments/s and near-full
GPU utilisation. Most active-search CPU samples were around 0–0.4%;
the table preserves the higher peaks. GPU utilisation is whole-device
nvidia-smi sampling. Later levels included zero-utilisation samples amid
concurrent desktop load, so were not continuously at 100%.

`gpu_supervise.py` applies a Windows job CPU hard cap of 7% to the search
and descendants. The pilot and larger run's highest sampled child CPU,
including preparation, was respectively 9.2625% and 9.1125%; short sample
windows can exceed the nominal job rate. The Manager clarified that the
10% ceiling concerns our contribution. Unrelated host load was untouched;
concurrent tests used smaller caps. Raw samples: `gpu-resources.jsonl`,
`gpu-blast-resources.jsonl`; reductions: `gpu-blast/audit.json`.
No laptop was used.

## Complete exclusions for b<=7

The final audit freshly re-enumerated all **2,109** shapes with b<=7:
b=4: 1; b=5: 25; b=6: 347; b=7: 1,736. It checked exact equality of the
eligible shape set and combined exhaustive manifests. Every other small
shape fails the cap, lower-bound sum, or Hall necessary condition at that n.

| n | Exhausted b=6 / b=7 shapes | Full b=6 ranks | Full b=7 ranks | Full ranks covered, b<=7 | Other small shapes excluded by bounds |
|---|---:|---:|---:|---:|---:|
| 68 | 1 / 17 | 5,949,147 | 1,620,406,333 | 1,626,355,480 | 2,091 |
| 69 | 1 / 6 | 6,471,002 | 574,262,263 | 580,733,265 | 2,102 |
| 70 | 1 / 6 | 7,028,847 | 630,054,289 | 637,083,136 | 2,102 |

**Computational conclusion:** no pancyclic C_n plus six chords with at most
seven distinct chord endpoints exists for n in `{68,69,70}`.

The b=6 exhaustive row is shape index 361, chords
`(0,1)(0,5)(1,2)(2,3)(3,4)(4,5)`, all lower bounds 2.
Its ranks are in `gpu-blast/n68.jsonl`, `n69.jsonl`, `n70.jsonl`.
All eligible b=7 rows were subsequently exhausted in the matching
`gpu-b7/n*.jsonl` files. These replace their shorter blast prefixes when
calculating combined coverage; repeated ranks are not added twice.
`gpu-b7/census-audit.json`, `"ranks"`, supplies the totals above.

## Sampled b>=8 coverage and remaining work

Each following shape received exactly 16,777,216 distinct legal ranks.
None was exhausted and no hit was found.

| n | b=8 shapes | b=9 | b=10 | b=11 | b=12 | Partial shapes | Tested ranks, b>=8 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 68 | 473 | 1,711 | 2,302 | 1,257 | 298 | 6,041 | 101,351,161,856 |
| 69 | 381 | 1,542 | 2,188 | 1,234 | 296 | 5,641 | 94,640,275,456 |
| 70 | 272 | 1,312 | 1,971 | 1,138 | 281 | 4,974 | 83,449,872,384 |

Exact remaining legal ranks after b<=7 completion:
n=68: **719,580,826,011,211**;
n=69: **836,660,492,971,331**;
n=70: **924,700,063,687,200**.
Largest individual spaces: 1,285,063,345,176; 1,533,058,025,824;
1,823,810,410,032 ranks, respectively. At measured aggregate rates this
is roughly 7.3, 9.9, and 11.5 GPU-days per level. These are extrapolations,
not runtime guarantees. No long exhaustion run was started.

The earlier 262,144-rank pilot is separately preserved in `gpu-run/`:
1,588,330,496 / 1,480,589,312 / 1,305,739,264 evaluations at n=68/69/70.
Pilot and blast overlap; they are not summed as distinct coverage.

## Exact rank mapping and implementation

`gpu_search.py`, symbols `scan`, `Engine.run`, `unrank`, `rank_arcs`
and `main`, implements one thread per legal composition. Forms come from
`S.cycle_forms`; eligibility uses distinct-form count plus two,
`B.intervals`, lower-bound sum, and `B.hall_ok` at the particular n.
Parallel cycle arcs have lower bound 2, others 1, ensuring simplicity.

Put `m = n - sum(lows) + b - 1`. The full legal space has **C(m,b-1)**
ranks, not always C(n-1,b-1). For j=1..b-1, define
`cut_j = sum(a_i-lows_i+1 for i<j)-1`;
rank is `sum(C(cut_j,j) for j=1..b-1)`.
Every JSONL row records canonical chords, b, lows, total, start, step,
and count. Its exact ranks are
`(start + t*step) mod total` for `0 <= t < count`.
The step is coprime to total, so ranks are distinct; count=total covers
every legal arc tuple. `unrank` reconstructs the tuples. No symmetry
quotient of arc assignments is assumed. Affine prefixes are deterministic
samples, not independent uniform random draws.

Kernel arc/cut arrays have size `2*6=12`, the structural maximum,
checked against the measured maximum b. Coverage uses two unsigned
64-bit words. Each SAT rank is materialised into arcs and chords and
independently checked by `search/verify.py` before reporting.
Hit-buffer overflow aborts. CuPy 14.2.0 lacks `runtime.setDeviceFlags`
here; blocking CUDA events provide synchronization instead. The initial
setup failure was not counted as validation.

The larger blast reused complete pilot eligibility manifests, recomputed
forms/bounds, and recorded source SHA-256 hashes in
`gpu-blast/summary.json`, `"replay_sources"`.
`gpu_summarize.py` audits counts and permutation arithmetic;
`gpu_audit_small.py` re-enumerates the complete b<=7 census.

## Tests and deliberate failures

- `gpu-final-tests.txt`: **6 tests, OK**. Exhaustive small-space rank
  inversion; all 84 compositions of a small GPU shape checked against
  NetworkX; batching; b=12 at n=63/64/65/68/69/70; known controls,
  all 27 family witnesses, and rejection of a forged GPU SAT.
- `gpu-review-tests.txt`: existing `test_review_contracts.py`,
  **9 tests, OK**.
- `gpu-shapecsp-tests.txt`: existing `test_shapecsp.py`,
  **ALL GATES PASS**; 201 cycle-multiset checks, zero mismatches,
  and calibrated t_2=8, t_3=14, t_4=24.
- Control mutation: `gpu_search.py --control-only --mutate-control`
  replaces forms by `(0,0)`: exit 1,
  `RuntimeError: POSITIVE CONTROL FAILED`; restored controls passed.
- Upper-word mutation: `test_gpu_search.py --mutate`.
  `gpu-tests-red.txt`: **FAILED (failures=1, errors=1)**.
  Restored `gpu-tests-restored.txt`: **5 tests, OK**;
  expanded final suite: **6 tests, OK**.
- Verifier mutation: `--mutate-verifier GpuTests.test_rejects_false_gpu_sat`
  makes the independent verifier accept everything.
  `gpu-verifier-red.txt`: **FAILED (failures=1)**,
  `AssertionError: RuntimeError not raised`.
  Restored verifier passes that test in `gpu-final-tests.txt`.
- Manifest mutation: `gpu_summarize.py ... --mutate` removes one row:
  exit 1, `ValueError: coverage census missing or duplicated rows`.
  Restored input: exit 0, full `gpu-blast/audit.json` produced.
- Small-census mutation: `gpu_audit_small.py ... --mutate` removes a row;
  `gpu-small-audit-red.txt`: exit 1, `ValueError: small-shape census incomplete`.
  Restoration: `gpu-small-audit-restored.txt`, exit 0, complete census and
  exhaustive legal-rank counts for all three levels.

## Reproduction

Commands from repository root; use new output directories:

```text
python search/shapecsp/gpu_supervise.py --log resources.jsonl -- python search/shapecsp/gpu_search.py --output pilot --count 262144
python search/shapecsp/gpu_supervise.py --log blast-resources.jsonl -- python search/shapecsp/gpu_search.py --output blast --count 16777216 --replay pilot
python search/shapecsp/gpu_supervise.py --log b7-resources.jsonl -- python search/shapecsp/gpu_finish_b7.py blast b7
python search/shapecsp/gpu_audit_small.py blast b7
python search/shapecsp/test_gpu_search.py -v
```

Invocation-time TEMP, TMP and CUPY_CACHE_DIR were explicitly set inside
the permitted Dev temp tree; search scripts hardcode no account-specific
destination. Generated evidence uses UTF-8 and LF.
Base revision measured before work:
`0817c6921439cd27e99b3d0d77bb7eae212a964a`.
Pre-existing reports, states and unrelated changes were preserved.
