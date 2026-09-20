# Independent review: pairwise-admissible GPU enumeration (Erdos #1016, k=6)

Reviewer: Worker 20 (VERIFIER). Date 2026-09-19. Repository root
`C:\Users\ToolsEnabled-Dev\Desktop\erdos1016`. No existing file under
`search/shapecsp` was edited; the eight probe scripts written for this review are
new files under `search/shapecsp/review/`, and their raw output is beside them.

Addendum 2 (end of file) re-reviews the fixes that landed for findings 1, 2 and
5 while this review was open, and records what is still outstanding.

Short verdicts:

| question | verdict |
|---|---|
| (1) Is `A` a superset of every pancyclic composition? | **YES**, with the premises named. No counterexample found; 29 real pancyclic witnesses and 58,461 exhaustively-found SAT compositions all lie in `A`. |
| (2) Do the tables and the kernel enumerate exactly `A`? | **YES on everything that can be tested.** The cross-word half of the coverage predicate was untested (finding 2); since fixed and re-verified — addendum 2. |
| (3) Is an incomplete or wrongly-planned tier impossible to report as exhausted? | **NO at the time of review.** Two state files that pass `verify_tier_exhaustion_pairwise.py` with `exact_match: true` and exit 0 while `A` is not covered are in `search/shapecsp/review/vattack/`. Both now exit 1 against commit 8bf6087 — addendum 2. |

---

## Finding 1 (costliest) — a tier can be reported exhausted without covering `A`; the tier manifest is believed, not re-derived

`verify_tier_exhaustion_pairwise.main` derives the expected unit set *from the
tier manifest* (`for offset in range(0, total, UNIT)` over
`meta["total_prefixes"]`), checks the per-shape composition sums *against the
same manifest* (`comp_mismatch`), and recomputes `plan_sha256` by calling
`gpu_state_runner_pairwise.plan_hash` *on the same manifest*. Every one of those
checks is internally consistent with a manifest that understates `A`. The only
code that re-derives the manifest from mathematics is the `--rebuild` branch,
and `p.add_argument("--rebuild", type=int, default=0)` — so the default
verification answers "does the state cover the manifest", not "does the state
cover `A`".

Demonstrated with `search/shapecsp/review/w20_probe_verifier.py`, on a synthetic
two-shape tier built from real n68 manifest chord sets (`shape_index` 2082 and
2083, both `b=7`, both `lows=[1,1,1,1,1,1,1]`) at `n=26`. Raw output:
`search/shapecsp/review/w20-vattack.out`. True sizes: `A(2082)` = 165,418 and
`A(2083)` = 165,263 compositions.

**Control (honest manifest, honest state):** exit 0, `exact_match: true`,
`expected_unit_count` 2, `tier_total_compositions_manifest` 330,681,
`compositions_counted_by_kernel` 330,681.

**D1 — understated manifest.** Halve shape 2083's `total_prefixes` and
`total_compositions` in `tier-manifest.json`, leave `shape-2083.npz` untouched,
write the state that matches the smaller plan:

```
exit_code 0, exact_match true, errors []
manifest_claims_compositions 248049   true_total_compositions 330681
compositions_never_enumerated 82632
```

`gpu_state_runner_pairwise.main` *would* catch this one — my reproduction of its
three per-shape checks reports `total_prefixes_ok: false` for shape 2083,
because it compares the loaded tables' `total_prefixes` with the manifest. The
verifier, which is the artifact whose whole job is to not trust the runner, does
not.

**D2 — shape swap, self-consistent.** Give shape 2083's manifest entry shape
2082's `tables_sha256` / `total_prefixes` / `total_compositions` / `nstates`, and
put a byte copy of `shape-2082.npz` at `shape-2083.npz`:

```
exit_code 0, exact_match true, errors []
shape_whose_A_was_never_enumerated 2083
its_true_total_compositions 165263
runner_checks_on_the_swapped_tier:
  2082: load_hash_ok true, total_prefixes_ok true, unrestricted_total_ok true, chords_match true
  2083: load_hash_ok true, total_prefixes_ok true, unrestricted_total_ok true, chords_match FALSE
```

Every check the runner and the verifier actually perform passes. Shape 2083's
165,263 admissible compositions are never enumerated; shape 2082's are
enumerated twice. Two root causes, both nameable:

* `pairwise_tables._HEADER_KEYS` is
  `("format","n","b","chords","lows","hi","vmax","forms","nstates","total_prefixes","total_compositions","empty")`
  — **no `shape_index`**. `tables_sha256` therefore binds a table file to a
  *shape*, but not to the *index it is filed under*. `build()` does put
  `shape_index=shape_index` in `tab`, and `header()` drops it.
* Neither `gpu_state_runner_pairwise.main` nor
  `verify_tier_exhaustion_pairwise.main` ever compares the loaded tables'
  `chords` with the gpu-blast row's `chords`. The only field that is compared,
  `unrestricted_total`, is `math.comb(n - sum(lows) + b - 1, b - 1)` — a function
  of `(n, b, sum(lows))` alone. In `gpu-blast/n68.jsonl` there are 15 shapes
  with `b=7` and `sum(lows)=7`; any two of them are interchangeable under this
  check.

**The defence that works, and its mutation pair.** The same D2 tier, verified
with `--rebuild 2`:

```
exit_code 1, exact_match false
errors ["rebuilt tables for shape 2083 disagree with the manifest"]
rebuilt [{"shape_index": 2082, "hash_and_totals_match": true},
         {"shape_index": 2083, "hash_and_totals_match": false}]
```

RED with `--rebuild 2`, GREEN with the default `--rebuild 0`, same state file,
same tier — that is the gate, and it is off by default and samples K of
thousands of shapes.

This is not only an adversarial story. A manifest and its `.npz` files built by
the *same* stale or buggy `pairwise_tables` agree with each other, so the
runner's `total_prefixes` check passes too and `--rebuild` (which rebuilds with
the *current* code) is the only thing left. On a claim covering ~1.9e15
unrestricted ranks, the honest statement today is: **the exhaustion rests on
`pairwise_tables.build` having been correct at manifest-build time, and nothing
in the default verification re-establishes that.**

Suggested repairs, in order of cost: add `shape_index` to `_HEADER_KEYS`;
compare `tab["chords"]` against the gpu-blast row in both
`gpu_state_runner_pairwise.main` and `verify_tier_exhaustion_pairwise.main`;
make `--rebuild` default to a nonzero sample, or require it for `exact_match`.

---

## Finding 2 — the 63/64 cross-word carry in the kernel is executed constantly and tested by nothing

`gpu_search_pairwise.CUDA` (kernel `scan`) advances its three 128-bit coverage
masks once per unit step of `a_{b-2}`:

```c
p1 = (p1 << 1) | (p0 >> 63); p0 <<= 1;      /* rising forms  */
m0 = (m0 >> 1) | (m1 << 63); m1 >>= 1;      /* falling forms */
```

`(p0 >> 63)` and `(m1 << 63)` are the only code that moves a form's length
between length 63 (word 0, bit 63) and length 64 (word 1, bit 0). I read both
and believe them correct. They are also, measurably, covered by nothing.

`search/shapecsp/review/w20_probe_carry_mutation.py` rebinds
`gpu_search_pairwise.CUDA` **in its own process only** with those two terms
deleted, builds a second `cp.RawKernel`, and re-runs the suite's own checks
against both engines (`search/shapecsp/review/w20-carrymut.out`):

```
stock : positive_control PASS, sample 44, mismatches 0, family 27/27,
        810048 compositions, 58461 SAT
mutant: controls   PASSED (mutation not detected)  sample 44, mismatches 0
        family     PASSED (mutation not detected)  27/27
        exact-set  6 cases, 810048 compositions, total_flag_differences 0
verdict: GREEN MUTANT: no existing check detects the carry mutation
```

Why, precisely (`w20_probe_carry2.py`, output `w20-carry2.out`): the only SAT
compositions the suite has at `n >= 64` are the production witness at `n=67` and
the family members `n=64,65,66,67`. At every one of those five,
`witness_v == vlo == 1` — the witness's completion arc is the *first* value the
kernel scans, so `forms_carried_across_63_64` is **0** and the incremental shift
has not run at all when the verdict is taken. `carry_critical_lengths` is empty
for all five. The `--mutate-forms` control is orthogonal: it replaces `forms`
with `[[0,0]]`, which breaks the initial mask construction, not the shift.

The within-word shifts (`p0 <<= 1`, `m0 >>= 1`) *are* covered heavily: the six
exact-set cases run at `n = 8, 14, 24, 25, 32, 42` and compare flags on 810,048
compositions with 58,461 SATs, most at `v > vlo`. But every one of those `n` is
below 63, so word 1 is empty there and the carries are unreachable. The carry
path does execute at the production `n` — `w20_probe_carry.py` measured 23,204
of 52,282 compositions in one `n=67` window crossing the boundary — it simply
never decides a verdict.

A positive control at `n = 68, 69, 70` is impossible by construction: the claim
being proved is that no SAT exists there. The buildable substitute is a case at
`n = 64..67` whose SAT sits at `v > vlo` with a required length in `[64, n]`
realised only by a carried form. **That case exists and needs no new
mathematics** — see the addendum below.

### Addendum, 2026-09-19: the missing case, built

`gpu_search_pairwise.canonical_witness` picks the one dihedral image of a
witness graph that matches `shapes.canon`. Every other image of
`shapes._dihedral` is the same graph with the arcs permuted, and
`pairwise_tables.build` needs only `(n, b, chords)` — it does not require a
canonical labelling, exactly as `test_pairwise_tables.pick_cases` already
appends non-manifest witness shapes. `search/shapecsp/review/w20_probe_carry_case.py`
scans all 110 dihedral images of the five `n >= 64` witnesses
(`w20-carrycase.out`):

```
dihedral_images_scanned 110, usable (pancyclic and in A) 110,
carry_critical_candidates 4   (n=64: 0, n=65: 0, n=66: 0, n=67: 2 per entry)
```

and the first candidate, run on the stock kernel and on the carry-deleted
mutant:

```
n 67, b 11
chords [[0,3],[1,6],[2,10],[3,5],[4,8],[7,9]]
arcs   [1,1,5,1,1,1,1,9,18,28,1]
prefix_rank 2435156, vlo 1, v 28   (27 steps of the sweep before the verdict)
carry_critical_lengths [64]
stock_reports_sat  true
mutant_sat_count   0
verdict "RED on the mutant: this case tests the carry"
```

Length 64 is realised at this composition only by forms that crossed the word
boundary during the sweep, so deleting `(p0 >> 63)` / `(m1 << 63)` loses it and
the witness stops being SAT. Adding this `(n, chords, arcs)` to
`test_pairwise_gpu.family` — or to `test_pairwise_tables.pick_cases`' `want_sat`
list, where it also gives the CPU suite its first `n >= 64` SAT — closes the
hole. It is a relabelling of the production `n=67` witness, so it introduces no
new claim: `search/verify.py` confirms the materialised graph is pancyclic and
`pairwise_tables.admitted` confirms it lies in `A`.

Only `n = 67` yields a carry-critical image; at `n = 64, 65, 66` all 22 images
are usable and none is carry-critical, so the case must be the `n=67` one.

---

## Finding 3 — `state_tier_manifest_sha256` is reported but never compared, and `tier-manifest.json` is not reproducible

`verify_tier_exhaustion_pairwise.main` emits both
`"tier_manifest_sha256": hashlib.sha256(mpath.read_bytes()).hexdigest()` and
`"state_tier_manifest_sha256": state.get("tier_manifest_sha256")`, and
`out["exact_match"]` never consults either. A field that looks like a binding is
not one.

It also could not be one as things stand. `pairwise_tables.build_tier` writes
`build_wall_seconds` into the manifest and `_build_one` writes per-shape
`build_seconds`; both are wall-clock timings. Measured — two builds of the same
synthetic tier, back to back:

```
shape-2082.npz       bytes_identical true   (6838 / 6838)
shape-2083.npz       bytes_identical true   (6606 / 6606)
tier-manifest.json   bytes_identical FALSE  (992 / 993)
tables_sha256        identical for both shapes
total_compositions   identical for both shapes
```

So `SPEC.md`'s "Deterministic: two builds of the same tier produce byte-identical
files" is true of the `.npz` arrays and of `tables_sha256`, and false of
`tier-manifest.json`. Dropping the two timing fields would make the manifest
reproducible and `state_tier_manifest_sha256` usable as the check it is dressed
up as.

---

## Finding 4 — the SOUND check in `test_pairwise_tables.py` can skip silently

`run_case` computes `sat_lost_by_A` only inside `if unrestricted_size <= LIMIT_U:`
(`LIMIT_U = 400_000`), and the pass criterion in `__main__` is
`r.get("sat_lost_by_A", 0) == 0`. A case for which the block never ran carries no
`sat_lost_by_A` key at all and is scored green by the default. Today's run did
evaluate SOUND on all six cases (`unrestricted_scanned_for_lost_sat` 967,496,
`sat_found` 58,461), so the printed 0 is real — but the `want_sat` witness cases
appended at the end of `pick_cases` are not filtered by `LIMIT_U`, so a future
larger witness case would be admitted and silently scored without the check. A
`sound_evaluated` flag that the pass criterion requires would close it.

---

## Finding 5 — the runner never checks that the loaded tables are this tier's `n` and `b`

`gpu_state_runner_pairwise.main` does
`current = PT.load(path, expected_sha256=unit["tables_sha256"])`, then checks
only `current["total_prefixes"] != unit["total_prefixes"]`, then calls
`engine.run(current, ...)` — and `Engine.run` takes `n, b = tab["n"], tab["b"]`
*from the file*. Nothing asserts `current["n"] == args.n` or
`current["b"] == args.b`, and the tier manifest records no per-shape `n`/`b`. A
table file built at the wrong level and dropped into `n{N}-b{B}/` would search a
different `n` and be recorded as this tier's work. Same class as finding 1 and
fixed by the same two lines.

---

## Finding 6 — smaller notes

* `build()`'s cross-check calls `PP.pair_count_dp(n, lows, hi, T)` with the same
  forward-only `T` that `build()` itself used. That validates the counting
  machinery, not the definition of the set; `pairwise_tables.enumerate_admissible`
  is the genuinely independent definition and it runs only in
  `test_pairwise_tables.py` on six small cases. The docstring's "independently
  written counter" is true of the algorithm and not of the set.
* `SPEC.md` requires the arc order to be "recorded as `order` in the header and
  hashed". `_HEADER_KEYS` has no `order`. Harmless while `build()` never passes
  an order to `pair_count_dp` (which defaults to `range(b)`), but the spec and
  the code disagree and the code is the fact.
* `gpu_search_pairwise.MAXC = 80` bounds the debug record to 80 completions per
  prefix and `Engine.run` raises `"debug record overflow"` above it. Debug mode
  is the only path the exact-set test uses, so the exact-set test is
  structurally capped at shapes whose prefixes are narrow. Measured on the first
  400 prefixes of the real `n=68/69/70` shape 361 (`b=6`): max 32 completions,
  so this is not currently binding — but it is why a wide `b=12` shape could not
  be exact-set tested without raising `MAXC`.
* `Engine.run`'s `viol` guard is structural, not independent: the unrank loop
  only picks `v` with `tr[v] >= 0` and the completion loop only counts `v` inside
  `[vlo, vhi]` with `w <= Tlast[v]`, so `viol` catches an *inconsistent* table
  (an unrankable rank, a prefix with no completion) but cannot catch a table that
  is wrong and self-consistent. The real backstop for a reported SAT is
  `V.pancyclic` in `Engine.run`, which is unconditional and correct.

---

## Question (1) — is `A` a provable superset of every pancyclic composition?

**Yes.** Three links, each checked.

**Monotonicity of the Hall test in the arc lower bounds.** `bound.hall_ok(iv, n)`
tests, over forms `f` with `mu_f <= y` and `n - max(nu_f,0) >= x`, that
`#{f} >= y-x+1` for all `3 <= x <= y <= n`. `prune_pairwise.Shape.hall_raises`
evaluates it at raised lows via `dlo = D @ self.memb` and
`dup = D @ (1 - self.memb)`, then
`lo = maximum(3, base_lo + dlo)` and `up = minimum(n, n - maximum(0, base_up + dup))`.
Both are monotone in `D`: `memb` and `1 - memb` are non-negative, so `lo` is
non-decreasing and `up` non-increasing; `hall_batch` counts forms whose interval
meets `[x, y]`, and narrowing an interval can only decrease that count (a form
that empties is folded to `n+1` by `dead = lo > hi` and drops out of both
cumulative counts); and the final `ok &= int(self.low.sum()) + D.sum(axis=1) <= n`
is monotone too. So `hall_raises` is monotone non-increasing in `D`, exactly as
the soundness comment at the top of `prune_pairwise.py` argues.

Measured: `w20_probe_soundness.check_monotone` drew 400 random comparable pairs
`D <= D'` per shape on 39 real manifest shapes (2 per `(n, b)` for
`n in 68,69,70` and `b in 6..12`) — **15,600 trials, 0 violations** of
`ok(D') => ok(D)`.

**The Hall argument itself.** If `a` is pancyclic at `n` then each of the `n-2`
lengths in `[3, n]` is realised by a cycle, a given form realises exactly one
length under a given `a`, so the map length -> form is injective: a matching
saturating `[3, n]` exists and `hall_ok` holds for **any** `lows <= a`. Taking
`lows'` equal to `lows` except `lows'_i = a_i` and `lows'_j = a_j` is legal, so
`(a_i, a_j)` lies in the feasible region `S_ij` and hence `a_j <= T[i][j][a_i]`.
Failure of `hall_ok` at `(u, v)` therefore excludes only non-pancyclic points.
This is correct as written.

**Forward staircase only.** `build()` updates caps with
`sub = Tarr[k, k + 1:, :][:, vs]` — only `T[k][j]` for `j > k`; the same is true
of `pair_count_dp`'s `lim = min(caps[q], T[(i, j)][v - lows[i]])`. The definition
of `A`, and `pairwise_tables.admitted` / `enumerate_admissible`, use **both**
directions. These coincide exactly when `S_ij` is downward closed, which
monotonicity gives: then `{v : ok(u,v)} = [lows_j, T[i][j][u]]` and
`{u : ok(u,v)} = [lows_i, T[j][i][v]]`, so `v <= T[i][j][u]` and
`u <= T[j][i][v]` are the same condition. `tarr_from`'s assertion
(`"staircase T[{i}][{j}] increases at u=..."`) is the necessary consequence and
it is live on the production build path.

Measured, over the same 39 shapes:

```
symmetry_box_points     2172074   symmetry_disagreements     0
closure_violations      0         staircase_not_max          0
staircase_non_monotone  0
```

`symmetry` compares `(v <= T[i][j][u])` against `(u <= T[j][i][v])` at every
`(u, v)` of every ordered pair's box; `closure`/`not_max` recompute the raw Hall
grid with `Shape.hall_raises` for 6 pairs per shape and check the grid is
downward closed, that each row's admissible set is the full prefix
`[lows_j, T[i][j][u]]` with no holes, and that `T` is the true row maximum.

**`per_arc_caps` needs monotonicity beyond the box.** It scans
`span = arange(lows[i], n+1)` and takes the value below the **first** failure. A
non-monotone scan there would make `hi` too *small* and could cut a pancyclic
point — a soundness hole, not a mere weakening. `w20_probe_kernel.check_perarc`
scans the full range for every arc of the real `n=68/69/70` shapes and confirms
the pass set is a prefix and the recomputed cap equals the reported `hi`:
`per_arc_violations 0`.

**Counterexample attempt — failed.** Two independent searches:

* Every real pancyclic witness available: the two in
  `gpu_search_pairwise.WITNESSES` (`n=67`, `n=56`) plus the 27-member family
  `n=41..67` used by `test_pairwise_gpu.family`. `w20_probe_soundness` reports
  `checked 29, pancyclic 29 (by search/verify.py), admitted_by_A 29,
  pancyclic_but_not_admitted 0`.
* Exhaustive: `test_pairwise_tables.py` enumerated 967,496 unrestricted
  compositions across six cases, found 58,461 that pass the full coverage test,
  and lost **0** to `A` (`sat_lost 0`, `sat_examples_lost []` on every case).

**Premises I did not verify**, and which the pairwise prune leans on harder than
the unrestricted plan did: `shapes.cycle_forms(b, chords)` must enumerate every
cycle form — an omitted form makes `hall_ok` *strictly harder*, so it would now
shrink the per-shape composition space rather than merely mis-gate eligibility —
and `bound.intervals`' rule `lows = [2 if i in par else 1 ...]` from
`shapes.parallel_arcs`. Both are inherited from the unrestricted search and
outside this review's scope; the 29 witnesses found through those same forms are
the evidence that exists.

---

## Question (2) — do the tables and the kernel enumerate exactly `A`?

**Yes on everything testable.** Audit and measurement:

**`build()`.** `state_lists[0] = [tuple(hi)]`; level `k` produces caps
`newc = minimum(caps[1:], Tarr[k, k+1:, vs])` for `vs = arange(lows[k], cap0+1)`,
deduplicated through `nxt_index`. The dead-transition monotonicity the unrank
loop depends on is asserted, not assumed:
`"dead transitions are not monotone at level {k}, state {caps}"`. That assertion
is what makes the kernel's `if (st2 < 0 || s + v > n) break;` equivalent to the
DP's per-`v` mask `m = col >= 0`, which does *not* break. `C[si]` counts
`(w >= lows[b-1]) & (w <= cB) & (w <= Tlast[vs])`; `cB <= hi[b-1]` holds because
caps only ever shrink from `hi`. `P[b-2] = (C > 0)` and
`Pk[m, :n+1-v] += P[k+1][col[m], v:]` implement the specified recursion. `F` is
computed forward and `"forward/backward prefix counts disagree"` is asserted.
`total_compositions` is checked against `PP.pair_count_dp` in `build()` itself.
The `empty` branch pads `states`, `trans`, `P`, `F`, `C` to the shapes
`_array_items` expects.

**`unrank_prefix` / `rank_prefix` / `completions`.** `rank_prefix`'s inner loop
breaks on the same two conditions as `unrank_prefix`, so the two agree given the
monotonicity assertion. `completions`' `vlo = max(lows[b-2], n - s - cB)` and
`vhi = min(cA, n - s - lows[b-1])` are character-for-character the kernel's
`if (n - s - cB > vlo) vlo = ...; if (n - s - lows[b-1] < vhi) vhi = ...;`.
Measured: **172,829 prefix ranks round-tripped, 0 failures**; ordered sequence
identical to `enumerate_admissible` (the both-directions reference recursion) on
**810,048 compositions**, `duplicates 0, missing 0, extra 0` on every case.

**Kernel `unrank` and completion loop.** `kernel_pack` lays `trans` and `P[1..b-2]`
flat with `trans_off` / `P_off`; the kernel indexes
`trans_flat + trans_off[k] + st*(vmax+1)` and `P_flat + P_off[k+1]`, which
matches. `P[0]` is never uploaded and never needed. The completion loop shifts
the masks on *every* `v`, including the ones skipped by `w <= Tlast[v]` — correct,
because the masks track `v`, not valid `v`. `if (mycomp == 0) atomicAdd(viol, 1);`
is a genuine guard: `total_prefixes` counts only prefixes with `C > 0`, so a
prefix with no completion is a real inconsistency.

**Shifted-mask coverage vs `gpu_search.scan`.** The two `need0` / `need1`
expressions are identical text in both kernels. The pairwise kernel differs in
one way: `gpu_search` clamps with `if(len>=3 && len<=n)`, the pairwise kernel
only drops `len < 0 || len > 127` and buckets with `1ULL << (len & 63)`, so it
*sets* bits outside `[3, n]`. `w20_probe_kernel.check_masks` transcribes both
expressions into Python and verifies for **every `n` from 3 to 70** that the
required bit set is exactly `{3..n}` and that no bit the kernel can set outside
that range is required (`spurious_required_bits 0` throughout), so the extra bits
are all masked away. At the word boundary:

```
n=62  need0 0x7ffffffffffffff8  need1 0x0    word0 3..62  word1 none
n=63  need0 0xfffffffffffffff8  need1 0x0    word0 3..63  word1 none
n=64  need0 0xfffffffffffffff8  need1 0x1    word0 3..63  word1 64..64
n=67  need0 0xfffffffffffffff8  need1 0xf    word0 3..63  word1 64..67
n=68  need0 0xfffffffffffffff8  need1 0x1f   word0 3..63  word1 64..68
n=69  need0 0xfffffffffffffff8  need1 0x3f   word0 3..63  word1 64..69
n=70  need0 0xfffffffffffffff8  need1 0x7f   word0 3..63  word1 64..70
```

`n = 63` takes the `n >= 63` branch, so `1ULL << (n + 1)` is never evaluated with
a shift count of 64; `n - 63 <= 57` for the engine's `max_n <= 120`, so
`1ULL << (n - 63)` is never undefined either. No `SHIFT_UNDEFINED_IN_C` was
raised for any `n` in 3..70.

**The `len > 127` drop.** For a *falling* form (`hasB` only) `v = vlo` is its
maximum length, so a drop there would be permanent and would lose coverage.
`w20_probe_soundness.max_form_length` bounds the largest realisable form length
over the whole box with `sum a = n` for all 39 shapes: **max 70, shapes over
127: 0**. The comment "cannot happen for a real composition" holds with wide
margin for these tiers.

**The production `n` is exercised nowhere in the suite; I closed that.**
`test_pairwise_gpu.py`'s exact-set cases run at `n = 42, 32, 25, 8, 14, 24`;
`controls` reaches 67 and `family` 41..67. `w20_probe_kernel.py` runs the real
kernel on real `n = 68, 69, 70` manifest shapes (shape 361, `b=6`, 70 forms),
1,500 prefixes each:

```
n=68  total_prefixes 288132  gpu_visited 17004 = cpu_expected  ordered identical  counter matches  flags identical
n=69  total_prefixes 293640  gpu_visited 16171 = cpu_expected  ordered identical  counter matches  flags identical
n=70  total_prefixes 308538  gpu_visited 15980 = cpu_expected  ordered identical  counter matches  flags identical
```

`gpu_sat = cpu_sat = 0` at all three, so the flag agreement there is negative
only — unavoidably, since the claim is that no SAT exists at those `n`. That is
the residue behind finding 2.

**Cap declared:** 2 shapes per `(n, b)` (39 shapes), 6 randomly chosen pairs per
shape for the grid recomputation, 400 monotonicity trials per shape, 1,500 of
~290,000 prefixes per production-`n` live launch. These are samples, not totals.

---

## Question (3) — can an incomplete or wrongly-planned tier be reported as exhausted?

**Yes** — see finding 1 for the two state files and their exact verifier output.

What *does* hold, and should not be lost in the finding: the `enumeration`
tag (`"pairwise-v1"`) is required by both the runner (`"state file enumeration
is ..., not ...; its completed units mean different work here"`) and the
verifier, so unrestricted work cannot be passed off as pairwise work;
`plan_sha256` covers `ENUMERATION`, `n`, `b`, `UNIT`, `source_sha256` and every
unit's `(shape_index, offset, count, total_prefixes, tables_sha256)`, so a
re-unitised or re-tabled plan is refused; `--only-shapes` states are rejected by
the verifier (`"state was restricted with --only-shapes"`); `partial` manifests
are rejected by both; duplicate, missing and extra units are counted; per-shape
composition sums are compared. The hole is precisely and only that all of those
are computed **from the manifest**, and the manifest is not re-derived by
default.

---

## Commands run, with their printed counts

All CPU work pinned to logical cores 4,5 (`ProcessorAffinity = 0x30`) at
`BelowNormal`. The production chain (`gpu_state_runner.py ... gpu-state-n68-b12.json
--n 68 --min-b 12 --max-b 12`) was running throughout and was not touched;
`gpu-state-n69-b11.json` and its lock were not read or written; no
`rebalance/benchmark-window.active` existed at any point (checked by recursive
search over the repository, no match).

**1. `python test_pairwise_tables.py`** (cwd `search/shapecsp/pairwise`) —
**exit code 0**, log `search/shapecsp/review/w20-tables.out`

```
{"cases": 6, "compositions_compared_against_reference": 810048,
 "prefix_ranks_round_tripped": 172829, "unrestricted_scanned_for_lost_sat": 967496,
 "sat_found": 58461, "sat_lost": 0, "failing_cases": 0}
```

Per case, every one: `ordered_sequence_identical true, duplicates 0, missing 0,
extra 0, rank_round_trip_ok true, counts_agree true, sat_lost_by_A 0,
io_round_trip_hash true, io_round_trip_arrays true`. Cases and their
`sat_in_unrestricted`: shape 361 b=6 n=42 (15,480), shape 1946 b=7 n=32 (18,924),
shape 2199 b=8 n=25 (24,041), b=4 n=8 (8), b=5 n=14 (6), b=7 n=24 (2).

**2. `python test_pairwise_gpu.py`** (cwd `search/shapecsp/pairwise`) —
**exit code 0**, log `search/shapecsp/review/w20-gpu.out`

```
{"controls": {"positive_control": "PASS", "soundness_control_on_witnesses": "PASS",
              "sample": 44, "mismatches": 0}}
{"cases": 6, "compositions_visited": 810048, "sat_compositions": 58461,
 "family_witnesses_checked": 27, "family_witnesses_found": 27,
 "failing_cases": 0, "seconds": 274.1}
```

Per case: `ordered_sequence_identical true, duplicates 0, missing 0, extra 0,
counter_matches true, flags_identical true`, `gpu_sat == cpu_sat` throughout.

**3. `python test_pairwise_gpu.py --mutate-forms`** — **exit code 1**, log
`search/shapecsp/review/w20-gpu-mutate.err`

```
RuntimeError: POSITIVE CONTROL FAILED
  raised from gpu_search_pairwise.controls
```

(An earlier capture of these three printed `EXIT=0` for the mutate run; that was
my harness, not the test — `%ERRORLEVEL%` in a `cmd /c "a & echo %ERRORLEVEL%"`
chain expands before the chain runs. All three exit codes above were re-taken
with `cmd /v:on` and `!ERRORLEVEL!`, or synchronously via `$LASTEXITCODE`.)

**4. `python w20_probe_soundness.py 2`** (new, `search/shapecsp/review/`) —
exit 0, GREEN, 63.0 s, log `w20-probe.out`

```
{"witness_check": "pancyclic => in A", "checked": 29, "pancyclic": 29,
 "admitted_by_A": 29, "pancyclic_but_not_admitted": 0}
{"summary": true, "shapes": 39, "monotone_trials": 15600, "monotone_violations": 0,
 "closure_violations": 0, "staircase_not_max": 0, "staircase_non_monotone": 0,
 "symmetry_box_points": 2172074, "symmetry_disagreements": 0,
 "max_form_length": 70, "shapes_over_127": 0, "violations": 0, "verdict": "GREEN"}
```

**5. `python w20_probe_kernel.py 1500`** — exit 0, GREEN, 8.7 s, log
`w20-kernel.out`; `need0`/`need1` table above, `per_arc_violations 0`, live
`n=68/69/70` rows above.

**6. `python w20_probe_verifier.py`** — exit 0, log `w20-vattack.out`; CONTROL /
D1 / D2 / D2+`--rebuild 2` results above.

**7. `python w20_probe_carry.py 3000`** — exit 0, log `w20-carry.out`

```
n=67 b=11 window 3000 prefixes, 52282 compositions, ordered identical,
counter matches, flags identical, gpu_sat 0,
compositions_whose_mask_crossed_63_64 23204,
SAT_compositions_whose_mask_crossed_63_64 0, carry_is_load_bearing_here false
```

**8. `python w20_probe_carry2.py`** — exit 0, log `w20-carry2.out`; five
witnesses `n = 67, 64, 65, 66, 67`, every one
`gpu_reports_sat_at_this_rank true`, `forms_carried_across_63_64 0`,
`carry_critical_lengths []`; summary
`"carry NOT covered by any failing test"`.

**9. `python w20_probe_carry_mutation.py`** — exit 0, 67.0 s, log
`w20-carrymut.out`; stock and mutant results above; verdict
`"GREEN MUTANT: no existing check detects the carry mutation"`.

**9b. `python w20_probe_carry_case.py`** — exit 0, 325.8 s, log
`w20-carrycase.out`; 110 dihedral images scanned, 4 carry-critical, proposed
case `stock_reports_sat true` / `mutant_sat_count 0`, verdict
`"RED on the mutant: this case tests the carry"`.

**10. Determinism**, two consecutive `PT.build_tier` calls on the same synthetic
tier: `.npz` byte-identical, `tables_sha256` identical, totals identical,
`tier-manifest.json` differs (992 vs 993 bytes).

## Addendum 2, 2026-09-19 evening: re-review of the fixes

Findings 1, 2 and 5 were fixed by others while this review was open. I re-ran
the attacks against the fixed code rather than take the fix reports on trust.
All three fixes hold.

### Findings 1 and 5 - fixed, and by default (commit 8bf6087)

`gpu_state_runner_pairwise.main` now resolves `row = by_shape[unit["shape_index"]]`
and refuses when `current["n"] != args.n`, `current["b"] != row["b"]`, or the
loaded `chords` or `lows` differ from the gpu-blast row. That closes finding 5
(`n`/`b` unchecked) as well as D2.

`verify_tier_exhaustion_pairwise.main` gained an **unconditional** per-shape
header check over every gpu-blast row - it loads each `shape-{idx}.npz` with the
manifest hash and compares `n`, `b`, `chords`, `lows`, `total_prefixes` and
`total_compositions` - plus `--rebuild -1` for a full rebuild. Re-running
`w20_probe_verifier.py` unchanged against it (`w20-vattack2.out`):

| case | before | after |
|---|---|---|
| CONTROL (honest manifest and state) | exit 0, `exact_match true` | exit 0, `exact_match true` |
| D1 understated manifest | exit 0, `exact_match true` | **exit 1**, `"1 shape table files do not describe their gpu-blast shape: ['2083']"` |
| D2 shape swap | exit 0, `exact_match true` | **exit 1**, same error |
| D2 with `--rebuild 2` | exit 1 | exit 1, both the header error and the rebuild error |

D1 is now caught without any `--rebuild`, because the header check compares the
npz's own `total_prefixes` against the manifest's and that is exactly what D1
falsified. The honest tier still passes, so the new check is not a blanket
refusal.

### Finding 2 - fixed, and the new gate is a real gate

`gpu_search_pairwise.scan` now takes a `U* cov_out` and, inside the existing
`if (debug && j < MAXC)` block, stores `cov0` and `cov1` - **the same two locals
that produced `sat` on the line above**, not a recomputation - so `Engine.run`'s
debug tuple is now `(rows, flags, cn, coverage)`. The non-debug path is
untouched: the diff adds nothing outside the `debug` guard.

`test_pairwise_carry.py` finds prefixes whose completion loop carries a form
length across 63/64 in both directions and compares the coverage words
bit-exactly rather than the verdict. That is the right shape for this problem:
all nine of its cases report `sat_in_window 0`, so a verdict-only test would
have been blind there - which is exactly why the old suite was.

Stock run (`w20-newcarry-stock.out`), **exit code 0**:

```
9 cases, crossing_prefixes 54, compositions_checked 795,
stock_all_match true, mutant_differences 516, mutation_detected true
```

The test builds its own carry-deleted mutant and requires
`mutant_differences > 0`, which proves it can tell two kernels apart. That does
not by itself prove it would go red if the **shipped** kernel were the broken
one. `search/shapecsp/review/w20_probe_newcarry_mutation.py` imports the test
unmodified, rebinds `gpu_search_pairwise.CUDA` in-process to the carry-deleted
version and calls `test_pairwise_carry.main()` (`w20-newcarry-mut.out`):

```
all 9 cases: stock_matches_cpu false, coverage_words_identical false
summary:     stock_all_match false, mutant_differences 0, mutation_detected false
test_pairwise_carry return code with broken kernel: 1
"RED as required: the gate catches a broken shipped carry"
```

RED with the carry deleted, GREEN with it present. The green mutant recorded in
finding 2 is closed. My `w20_probe_carry_case.py` fixture is now redundant for
coverage: the new test reaches the same fault by a better route, because it does
not depend on finding a pancyclic witness at all.

### No regression from the debug change

`w20_probe_kernel.py` re-run against the new kernel (`w20-kernel2.out`, exit 0)
reproduces the pre-change numbers exactly at the production levels: `n=68`
17,004 compositions, `n=69` 16,171, `n=70` 15,980, each with
`ordered_sequence_identical true`, `counter_matches true`, `flags_identical
true`, and `per_arc_violations 0`.

### Still open after the fixes

* **`exact_match` does not require `rebuild_covers_every_shape`.** The verifier
  computes `out["rebuild_covers_every_shape"] = len(picked) == len(mshapes)` and
  then `out["exact_match"] = (not out["errors"] and not missing and not extra
  and out["composition_totals_match"])`. A run with the default `--rebuild 0`
  still prints `exact_match: true` and exits 0, so "the final tier claim uses
  `--rebuild -1`" is a procedure, not a gate - the same shape of defect as
  `state_tier_manifest_sha256` in finding 3. This matters most for shapes with
  `total_prefixes == 0`: the header check binds their tables to their chords,
  but nothing re-derives that their admissible set really is empty except a
  rebuild. `--rebuild -1` does cover them, since `picked = sorted(mshapes)`.
* **`test_pairwise_carry.cpu_coverage` masks lengths to `[3, n]` while the
  kernel masks only to `[0, 127]`.** They agree, and provably rather than by
  luck: a cycle in an `n`-vertex graph visits each vertex at most once, so every
  form length is at most `n`, and a cycle has length at least 3. That also makes
  the kernel's `if (len < 0 || len > 127) continue` vacuous for every tier here,
  which upgrades the measured bound of 70 I reported under question (2) to a
  proof. Worth stating so the mask is not later "fixed" into disagreement.
* `mutant_differences > 0` is required in aggregate, not per case, so eight of
  the nine cases could stop separating stock from mutant unnoticed.

Findings 3, 4 and 6 are unchanged and still open.

## Files added by this review

All under `search/shapecsp/review/` (no existing file under `search/shapecsp`
was edited):

```
w20_probe_soundness.py        Q1: monotonicity, downward closure, forward/reverse
                              symmetry, form-length bound, pancyclic witnesses in A
w20_probe_kernel.py           Q2: need0/need1 for n=3..70, per-arc scan monotonicity,
                              live kernel at n=68/69/70
w20_probe_verifier.py         Q3: honest control + two state files that pass the
                              verifier without covering A, and the --rebuild RED
w20_probe_carry.py            the 63/64 carry: how often it runs, whether it decides
w20_probe_carry2.py           whether any witness's verdict depends on it
w20_probe_carry_mutation.py   delete both carries in-process and re-run the suite
w20_probe_carry_case.py       find the dihedral image that DOES depend on it, and
                              separate stock from mutant on it
w20_probe_newcarry_mutation.py  break the SHIPPED carry and check the new
                              test_pairwise_carry.py gate goes red (addendum 2)
w20_probe_verifier2.py        addendum 3: D1/D2 re-run, D3 empty-A forgery, D4
                              stale state hash, manifest reproducibility
w20_probe_rebuild_determinism.py  addendum 3: why --rebuild -1 rejects an honest
                              tier, on a real production tier
w20-*.out / w20-*.err         raw output of every run above
vattack/, vattack2/, det-*/   the synthetic tiers the verifier probes built
```

---

# Addendum 3, 2026-09-19 late: --rebuild -1 currently rejects honest tiers

Measured against the working tree at the time of writing, which is **not** a
clean checkout: `git status` reports `pairwise_tables.py`, `gpu_search_pairwise.py`
and `test_pairwise_tables.py` modified and uncommitted, with scratch patch
scripts under `pairwise/_w21scratch/`. An arc-order heuristic (`choose_order`,
`ORDER_HEURISTICS = ("narrow-first", "wide-first", "natural")`,
`build(..., order=None)`, `build_tier(..., heuristic="narrow-first")`) is in the
working tree and in no commit. The two faults below are consequences of that
in-flight work plus the header change that did land, and both are **false
negatives on the honest path**, never false passes.

`--rebuild -1` is now declared the sole gate for the final exhaustion claim
(`verify_tier_combined.py` appends an error unless `args.rebuild == -1`). It
currently fails on honest input, which is the condition under which a gate gets
weakened rather than fixed.

### Fault A — no tier built before the header change can ever match a rebuild

`_HEADER_KEYS` is now
`("format","n","b","shape_index","chords","order","lows","hi","vmax","forms","nstates","total_prefixes","total_compositions","empty")`
— it gained `shape_index` (the repair I suggested for finding 1) and `order`.
`FORMAT` was **not** bumped: it is still `"pairwise-tables-v1"`. The shipped
production tables predate the change; `pairwise/tables/n68-b11/shape-19023.npz`
has header keys `['b','chords','empty','format','forms','hi','lows','n','nstates','total_compositions','total_prefixes','vmax']`
and declares the same format string.

`PT.load` on those files still works and rehashes to the manifest's value
(`9d8ab40070a81e21` both ways), so the runner and the verifier's header check are
unaffected. `--rebuild` is not, because it compares against a *fresh* build whose
header now carries the two new keys. Rebuilding three real shapes of the live
`n68-b11` tier (`w20-rebuilddet.out`):

```
19023  hash_matches false  prefixes_match true  compositions_match true
19026  hash_matches false  prefixes_match true  compositions_match true
19027  hash_matches false  prefixes_match true  compositions_match true
```

Totals reproduce exactly; only the hash disagrees, and only because the hashed
header changed shape under an unchanged format tag.

### Fault B — the verifiers rebuild in natural order; build_tier no longer builds in natural order

`_build_one` now computes
`order = None if heuristic == "natural-order" else choose_order(n, row["b"], row["chords"], row["lows"], heuristic=heuristic)`
and passes it to `build`. Both `verify_tier_exhaustion_pairwise.main` and
`verify_tier_combined.main` rebuild with
`PT.build(args.n, r["b"], r["chords"], r["lows"], shape_index=idx)` — **no
`order` argument**, so `order=None`, so the natural order. On a tier I built
with the current code minutes earlier (`w20-vattack3.out`, `w20-rebuilddet.out`):

```
manifest (narrow-first)  total_prefixes 38466   total_compositions 165418
fresh build (natural)    total_prefixes 38784   total_compositions 165418
verify_tier_combined --rebuild -1 on the HONEST tier:
  exit 1, rebuilt_count 2, rebuilt_mismatches 2,
  errors ["rebuilt tables disagree for shape 2082", "rebuilt tables disagree for shape 2083"]
```

`total_compositions` is invariant under the order — the module docstring says so
and the measurement confirms it — so the number the exhaustion claim rests on is
untouched. Only `total_prefixes`, and therefore the hash, move. `_build_one`
already records `order=tab["order"]` in the manifest meta, so the repair is to
pass it back: `PT.build(..., order=mshapes[idx]["order"])` in both verifiers.

### D3 (new) — a manifest that claims a shape's `A` is empty passes by default

The case the first pass did not cover. Forge `shape-2083.npz` to claim emptiness
while describing the real shape: right `n`, `b`, `chords`, `lows`,
`total_prefixes 0`, `total_compositions 0`, the array shapes `build()` produces
on its `empty` branch, and a `tables_sha256` recomputed over that header. Put
that hash and those zeros in the manifest and add the shape to `excluded`.
Nothing contradicts it: the header check compares npz against manifest and both
say zero, the shape contributes no units, and the per-shape composition check is
guarded by `int(meta["total_prefixes"]) > 0`.

```
default (--rebuild 0):  exit 0, exact_match TRUE, errors []
                        shapes_with_empty_admissible_set 1
                        tier_total_compositions_manifest 165418  (true tier total 330681)
                        165263 compositions of shape 2083 never enumerated
--rebuild -1:           exit 1
verify_tier_combined --rebuild -1: exit 1
```

So the default verifier still accepts a tier that silently drops a whole shape by
declaring its admissible set empty, and only a rebuild catches it. That is the
intended design — but it makes faults A and B blocking rather than cosmetic,
because today `--rebuild -1` rejects honest tiers too, so its rejection of D3
carries no information. **D3 must be re-run once A and B are fixed**; until then
the empty-`A` case is not demonstrably caught by anything.

### Closed by 83e8915

* D1 and D2 remain closed: both exit 1 with
  `"1 shape table files do not describe their gpu-blast shape: ['2083']"`, and
  the honest control still exits 0 with `exact_match true`.
* **D4 (new)** — a state whose `tier_manifest_sha256` does not match the file on
  disk is now rejected: exit 1,
  `"state tier_manifest_sha256 != hash of the tier manifest on disk (review finding 3)"`.
* `tier-manifest.json` is now byte-reproducible across two builds of the same
  tier (timings moved to a `tier-build.json` sidecar, which is present). With D4
  that closes **finding 3** completely.
* `order` is now in the hashed header, which closes the `SPEC.md` divergence
  noted under finding 6.
* `test_pairwise_tables.py` now requires `sound_evaluated`, closing **finding 4**
  (not re-measured here; the change is in the working tree).

### Caveat on this addendum

`pairwise_tables.py` was being edited while these measurements ran. Faults A and
B are reproducible from the recorded outputs, but the file may differ by the
time they are read; the totals and hashes above name the exact tier and shapes
so they can be re-taken.

### Correction to this addendum

Above I recorded finding 4 as closed "in the working tree". That was wrong about
provenance: it is committed in 83e8915, which changes
`test_pairwise_tables.run_case` to set `rec["sound_evaluated"] = unrestricted_size <= LIMIT_U`
and adds `r["sound_evaluated"]` to the pass criterion in `__main__`, so a case
above `LIMIT_U` now fails instead of scoring green on a missing key. The finding
is closed; my citation was not.

---

# Addendum 4, 2026-09-19: closing verdict

Commit references, each checked against the repository rather than taken from
the change report:

| item | commit | checked by |
|---|---|---|
| Runner compares every loaded table's `n`/`b`/`chords`/`lows` with the gpu-blast row (findings 1, 5 / D2) | 8bf6087 | diff read; D2 exits 1 |
| Verifier per-shape header check, unconditional; `--rebuild -1` | 8bf6087 | diff read; D1 and D2 exit 1 |
| `build_tier` writes no timing into `tier-manifest.json` (timings to `tier-build.json`); both verifiers compare the state's `tier_manifest_sha256` with the file on disk (finding 3) | 83e8915 | commit message and diff; D4 exits 1; two builds byte-identical |
| `test_pairwise_tables.py` scores `sound_evaluated` as a hard requirement (finding 4) | 83e8915 | diff hunks `rec["sound_evaluated"] = unrestricted_size <= LIMIT_U` and the `__main__` criterion |
| Kernel debug mode exports the coverage words; `test_pairwise_carry.py` (finding 2) | e852461 | diff read; stock exit 0, broken-shipped-carry exit 1 |
| Verifier reports `exact_match_full_rebuild` and `claim_grade`; carry test requires **every** case to separate the mutant; `[3,n]` vs `[0,127]` mask agreement documented | f63f9f3 | `claim_grade` at line 181 of the verifier, `cases_not_separating` at line 189 of the carry test |
| `shape_index` in the hashed header (finding 6) scheduled with Worker 21's arc-order change, so the tables hash breaks once | not yet committed | `pairwise_tables.py` still shows as modified |

## Closing verdict

**(1) Is `A` a provable superset of every pancyclic composition? YES.** The
monotonicity of `Shape.hall_raises` in the arc lower bounds is provable and was
measured at 15,600 comparable pairs with 0 violations; downward closure follows,
which is what makes the forward-only staircase in `build()` and `pair_count_dp`
equal to the both-direction set (2,172,074 box points, 0 disagreements);
`per_arc_caps`' first-failure scan is monotone over its whole range (0
violations). Every counterexample attempt failed: 29 real pancyclic witnesses
all lie in `A`, and 58,461 exhaustively-found SAT compositions lost 0. The
premises I did not verify are named under question (1) and are inherited from
the unrestricted search: `shapes.cycle_forms` must be complete, and
`bound.intervals`' `lows` rule.

**(2) Do the tables and the kernel enumerate exactly `A`? YES**, on everything
testable, and the one hole is now closed. 810,048 compositions matched the
independent reference recursion in order with zero duplicates, missing or extra;
172,829 prefix ranks round-tripped; `need0`/`need1` are exact for every `n` in
3..70 including the 63/64 boundary; the live kernel matches the CPU tables at
`n=68, 69, 70`. The cross-word carry was executed constantly and tested by
nothing (a green mutant); it is now covered bit-exactly, and I confirmed the new
gate goes red when the *shipped* carry is broken, not only when the test breaks
its own copy.

**(3) Is an incomplete or wrongly-planned tier impossible to report as
exhausted? NOT YET, but for one remaining reason only.** D1, D2 and D4 are
closed and re-measured. D3 — a manifest that declares a shape's admissible set
empty, with a self-consistent forged table — still passes the default verifier
with `exit 0, exact_match true`, and is caught only by a rebuild. That is the
intended design, and `verify_tier_combined.py` refuses anything but
`--rebuild -1`, so the claim path covers it. **The blocker is that `--rebuild -1`
currently rejects honest tiers**, for the two faults in addendum 3. Fault A is
scheduled (one coordinated hash break with the order change). Fault B is not:
`verify_tier_exhaustion_pairwise.py` line 147 and `verify_tier_combined.py`
line 155 both still call
`PT.build(args.n, r["b"], r["chords"], r["lows"], shape_index=idx)` with no
`order`, while `_build_one` builds with `choose_order(...)`. Until that one
argument is passed, a full rebuild cannot succeed on a tier built by the current
`build_tier`, and D3's rejection carries no information. Tracked as T563.

Nothing in faults A or B can turn an unexhausted tier into a reported-exhausted
one: both are false negatives on the honest path, and `total_compositions` — the
quantity the exhaustion claim rests on — is invariant under the arc order
(165,418 either way, measured). The soundness of `A` and the exactness of the
enumeration are not affected by them.

### Addendum 5 — D3 against the frozen claim path, and the scope of faults A and B

Faults A and B are confined to the working tree. Since 18:25 the chains, the
hourly sync and the unattended finalizers run from
`search/shapecsp/pairwise-prod`, a snapshot of commit `f63f9f3`. I verified the
snapshot rather than accepting it: every one of the ten `.py` files there is
**byte-identical** to `git show f63f9f3:search/shapecsp/pairwise/<name>`
(compared as bytes, not text). The frozen module reports

```
pairwise-prod/pairwise_tables.py
_HEADER_KEYS ("format","n","b","chords","lows","hi","vmax","forms","nstates",
              "total_prefixes","total_compositions","empty")     -- the v1 12-key tuple
build(n, b, chords, lows=None, shape_index=None, check=True)     -- no order parameter
FORMAT "pairwise-tables-v1"
```

so neither the `_HEADER_KEYS` growth nor `build_tier`'s `choose_order` is in the
code any claim is made with. `search/shapecsp/review/w20_probe_d3_prod.py` puts
that directory first on `sys.path` and invokes
`pairwise-prod/verify_tier_combined.py` by path
(`w20-d3prod.out`):

**Honest scratch tier, claim tool, `--rebuild -1`:**

```
exit 0, exact_match true, errors []
rebuilt_count 2, rebuilt_mismatches 0, rebuild_covers_every_pairwise_shape true
pairwise_compositions_manifest 330681 == pairwise_compositions_counted 330681
union_covers_tier true
```

A full rebuild of every shape succeeds on the frozen path. Faults A and B do not
reach it.

**D3 (one shape's tables forged to claim an empty admissible set, manifest
agreeing), claim tool, `--rebuild -1`:**

```
exit 1, exact_match false
errors ["rebuilt tables disagree for shape 2083"]
rebuilt_count 2, rebuilt_mismatches 1, rebuild_covers_every_pairwise_shape true
```

D3 is rejected, and rejected for the right reason — the rebuild from the
gpu-blast row, not an incidental mismatch. 165,263 compositions would otherwise
have gone unenumerated.

**D3 through the exhaustion verifier with the default `--rebuild 0`:**

```
exit 0, exact_match true, errors []
claim_grade "manifest-consistent-only", exact_match_full_rebuild false
shapes_with_empty_admissible_set 1, tier_total_compositions_manifest 165418
```

The default run still accepts it, as designed — but `f63f9f3` now makes that
result label itself: `claim_grade "manifest-consistent-only"` and
`exact_match_full_rebuild false` say on the face of the output that this is not
a claim. That is the difference between a gap and a trap, and it closes my last
open point from addendum 2.

So, for the tiers being claimed tonight: the claim tool accepts an honest tier
under a full rebuild and rejects the empty-`A` forgery, and a run that did not
do a full rebuild cannot be mistaken for one. Faults A and B remain open against
the working tree and are tracked for Worker 21's arc-order adoption (v2 format
string, a legacy path that rebuilds v1 tiers hash-identically, the verifiers
passing `order=mshapes[idx]["order"]`, and permuted-order GPU and carry tests);
T563 covers re-running D3 against that code when it lands.

End of review.
