# Arc order for the pairwise kernel: the specified heuristic is a net loss

Worker 21, 2026-09-19. Code: `search/shapecsp/pairwise/`. Every number below was
produced by the commands in the last section, on this desktop, pinned to cores
4,5 at below-normal priority.

## The costliest finding first

**The completion-pair rule the task specified — "the two arcs with the widest
admissible range, largest product of ranges" — makes the enumeration WORSE, not
better, and adopting it would have slowed the next generation.**

Measured over **every shape** of the two live n=68 tiers, `total_prefixes` with
that rule against the natural order:

| tier | shapes | natural total_prefixes | product-rule total_prefixes | gain |
|---|---|---|---|---|
| n68-b11 | 1257 (all) | 5,036,668,586,479 | 5,194,785,419,611 | **0.970x** |
| n68-b12 | 298 (all) | 1,659,281,442,100 | 1,879,941,506,220 | **0.883x** |

A gain below 1 means more prefixes per composition, i.e. more unrank work per
unit of enumeration — exactly the cost the change was meant to remove. The rule
is worse than natural on 520 of 1257 b=11 shapes and 177 of 298 b=12 shapes.

The reason is a modelling error in the premise, and it is visible in one line:
the two completion arcs are not free to range over their rectangle. A prefix
fixes the sum `s`, so the completions lie on the single line `v + w = n - s`.
The number of them is bounded by the **narrower** arc's range, not by the
**product** of the two ranges. `pairwise_tables.pair_admissible_mass` computes
the true quantity — how many `(v, w)` the pair admits at each total — and its
docstring records this.

I implemented the specified rule anyway (`order_from_derived(rule="product")`),
measured it, and am reporting the disagreement rather than bending either side.

## What no cheap rule achieves

The manager's bar: adopt only if a rule beats natural by >= 1.3x in prefixes.
**No cheap rule clears it.** Full-tier, every shape, every rule:

### n68-b11, all 1257 shapes (tier total_compositions 28,143,344,715,044)

| rule | tier total_prefixes | gain | compositions/prefix | sum(nstates) | shapes worse than natural | shapes >= 1.3x |
|---|---|---|---|---|---|---|
| natural | 5,036,668,586,479 | 1.0000 | 5.5877 | 1,820,340 | — | 0 |
| product | 5,194,785,419,611 | 0.9696 | 5.4176 | 1,225,605 | 520 | 268 |
| min-width | 5,135,789,172,344 | 0.9807 | 5.4798 | 1,223,670 | 522 | 268 |
| pair-mass-total | 4,573,101,593,549 | 1.1014 | 6.1541 | 1,191,794 | 421 | 307 |

### n68-b12, all 298 shapes (tier total_compositions 8,073,813,826,147)

| rule | tier total_prefixes | gain | compositions/prefix | sum(nstates) | shapes worse than natural | shapes >= 1.3x |
|---|---|---|---|---|---|---|
| natural | 1,659,281,442,100 | 1.0000 | 4.8658 | 823,799 | — | 0 |
| product | 1,879,941,506,220 | 0.8826 | 4.2947 | 368,664 | 177 | 52 |
| min-width | 1,877,362,208,579 | 0.8838 | 4.3006 | 368,105 | 178 | 54 |
| pair-mass-total | 1,513,873,693,510 | 1.0961 | 5.3332 | 364,395 | 143 | 68 |

The best cheap rule reaches 1.10x on both tiers. That is below the 1.3x bar.

**Recommendation: do not adopt a cheap order rule.** `DEFAULT_ORDER_RULE` is
therefore `"natural"`, and the reason is recorded in the constant's own comment
so nobody re-adopts a rule the numbers refused.

### A second finding worth keeping

Every cheap rule cuts `sum(nstates)` hard while making prefixes worse — at b=12,
823,799 states down to ~368,000, a 2.2x reduction, for a 0.88x prefix result.
**State count and prefix count are not aligned**, so tuning the order by state
count (the task's suggestion for the remaining arcs) optimises the wrong thing.
That is why the remaining-arc heuristic is reported here as a state-count
measurement only, and is not what selects the order.

## The one rule that does clear the bar, and its price

Building the tables once for **every** candidate completion pair and keeping the
smallest `total_prefixes` is exact, deterministic, and does beat natural.
Sample: 20 shapes per tier (a declared cap, not the tier), every pair built —
55 pairs per shape at b=11, 66 at b=12.

| tier | sample | tier gain | median shape gain | min | max | shapes >= 1.3x | sum(nstates) natural -> best |
|---|---|---|---|---|---|---|---|
| n68-b11 | 20 of 1257 | **1.422x** | 1.631 | 1.017 | 8.887 | 14/20 | 28,581 -> 15,193 |
| n68-b12 | 20 of 298 | **1.789x** | 1.502 | 1.043 | 9.159 | 16/20 | 61,502 -> 24,636 |

Combined: median shape gain 1.513, 30 of 40 shapes at or above 1.3x.

Price: C(b,2) extra builds per shape — measured 73.8 s for one b=11 shape
(shape_index 19380, order `[1,3,0,2,4,8,5,9,6,7,10]`, 2,638,817,226 prefixes
down to 923,516,193 = 2.857x), and about 120 s per b=12 shape. For the two n=68
tiers that is roughly 17 core-hours of table build. It is shipped as
`pairwise_tables.choose_order_measured` and as `--order measured`, not as a
default, because it is a tier-build cost and because prefix count is not yet
known to convert into GPU seconds.

How badly the cheap rules approximate this optimum, on the same 40 shapes:
median rank of the chosen pair among 55 candidates was 16.5 (product and
min-width) and 25.0 (pair-mass-mean) at b=11 — i.e. around the middle of the
field, and `natural` itself ranks 21.0, so the cheap rules are not reliably
better than doing nothing.

## GPU A/B: not measured, and why

The task asked for a 3-shape GPU A/B within 3 minutes of GPU. **I did not run
it.** The manager reserved GPU timing to a benchmark window he will schedule,
because the card is shared with the production chain on both machines. This is a
deferral, not a null result: no GPU A/B timing exists yet.

The contention-free half of that item is measured and is in the tables above:
compositions per prefix, full-tier, for every rule. The GPU *correctness* runs
below did use the card, briefly.

## Correctness of the order machinery

`A` does not depend on the arc order, so `total_compositions` must be invariant
under it and `total_prefixes` must not be. That invariance was checked on
**1555 shapes x 4 orders = 6220 builds** across the two full tiers:
`compositions_invariant_on_every_shape: true` for both.

### test_pairwise_tables.py — format pairwise-tables-v2

```
{"cases": 6, "order_runs": 18, "format": "pairwise-tables-v2",
 "orders": ["chosen", "natural", "reversed"],
 "compositions_compared_against_reference": 2430144,
 "prefix_blocks_checked": 524231, "prefix_blocks_ok": 524231,
 "prefix_ranks_round_tripped": 524231,
 "unrestricted_scanned_for_lost_sat": 2902488, "sat_found": 175383, "sat_lost": 0,
 "duplicates": 0, "missing": 0, "extra": 0,
 "cases_with_non_trivial_chosen_order": 6, "order_comparisons_bad": 0,
 "failing_cases": 0}
```

Every case runs under three orders: natural, a rule-derived one, and a reversed
permutation that is non-trivial for every b so no case can pass by accidentally
being natural. The reference recursion `enumerate_admissible` is computed in
**natural** order from `lows`/`hi`/`Tarr`, which no order touches, and is
compared as a SET; under the natural order the ordered sequence must also match
exactly, and it does. The per-prefix ordered check (`reference_block`) rebuilds
each prefix's completions straight from the definition of `A` — box plus every
pair constraint in both directions, no `C`, no states, no caps — and compares
them in order: 524,231 blocks, 524,231 OK.

### test_pairwise_gpu.py — format pairwise-tables-v2

```
{"cases": 6, "order_runs": 12, "format": "pairwise-tables-v2",
 "orders": ["natural", "reversed"], "compositions_visited": 1620096,
 "sat_compositions": 116922, "verify_py_calls": 989, "verify_py_disagreements": 0,
 "duplicates": 0, "missing": 0, "extra": 0, "control_mismatches": 0,
 "family_witnesses_checked": 27, "family_witnesses_found": 27,
 "order_comparisons_bad": 0, "failing_cases": 0, "seconds": 582.6}
```

The permuted run sends the kernel permuted form masks, permuted `lows` and a
different `Tlast`, and its arc vectors come back in natural order. Both orders
visit the same set and report the same SAT count. `controls` passes under both a
natural build and a rule-derived permuted build (44 sampled prefix ranks each,
0 mismatches).

### test_pairwise_carry.py — format pairwise-tables-v2

```
{"cases": 11, "format": "pairwise-tables-v2", "permuted_order_cases": 2,
 "crossing_prefixes": 66, "compositions_checked": 897, "stock_all_match": true,
 "mutant_differences": 598, "mutation_detected": true,
 "cases_not_separating_mutant": [],
 "carry_witness_sat_on_stock_and_not_on_mutant": true}
```

`crossing_prefixes` now permutes the form masks into assignment order before
looking for a 63/64 crossing, because that is the space the kernel shifts in:
the rising/falling split is decided by positions b-2 and b-1 of the **order**,
not by natural arcs b-2 and b-1. For the natural order `permute_mask` is the
identity, so the existing cases are unchanged — and they still separate the
carry mutant, every one of them.

### Both formats

All three tests also pass built in the legacy v1 header:

```
test_pairwise_tables.py --format pairwise-tables-v1
  {"cases": 6, "order_runs": 6, "format": "pairwise-tables-v1", "orders": ["natural"],
   "compositions_compared_against_reference": 810048, "prefix_blocks_checked": 172829,
   "prefix_blocks_ok": 172829, "sat_lost": 0, "duplicates": 0, "missing": 0, "extra": 0,
   "failing_cases": 0}
test_pairwise_gpu.py --format pairwise-tables-v1
  {"cases": 6, "order_runs": 6, "format": "pairwise-tables-v1", "orders": ["natural"],
   "compositions_visited": 810048, "sat_compositions": 58461, "verify_py_calls": 494,
   "verify_py_disagreements": 0, "control_mismatches": 0,
   "family_witnesses_checked": 27, "family_witnesses_found": 27, "failing_cases": 0}
test_pairwise_carry.py --format pairwise-tables-v1
  {"cases": 9, "format": "pairwise-tables-v1", "permuted_order_cases": 0,
   "crossing_prefixes": 54, "compositions_checked": 795, "stock_all_match": true,
   "mutant_differences": 516, "mutation_detected": true, "cases_not_separating_mutant": []}
```

Under v1 the permuted orders are **refused by name**, not skipped silently:

```
{"refusal": "permuted orders not run",
 "reason": "pairwise-tables-v1 has no order header key, so a permuted build is
            unrepresentable in it; build() refuses rather than writing one",
 "orders": ["natural"]}
```

## Mutation check on the gate this change adds

Every new gate rests on one thing: every arc vector leaving the tables or the
kernel is put back into natural order by `pairwise_tables.natural`. Break it —
return the assignment-order vector unchanged — and the permuted-order gates must
go RED while the natural-order ones stay GREEN, because there the mutation is a
no-op by definition.

```
stock:    ["GREEN", "GREEN"]      (natural, reversed)
mutant:   ["GREEN", "RED"]        <- reversed: 146942 missing, 0 of 60467 prefix blocks OK
restored: ["GREEN", "GREEN"]
passes: true
```

The natural-order column staying GREEN under the mutant is the point: it shows
the old tests could not have caught this, and the new permuted cases can.

## Backward compatibility: production tables are untouched and still rebuildable

The header gains `order` and `shape_index`, both hashed (`shape_index` closes
review finding 1/6: a table file was bound to a shape but not to the index it is
filed under). That is a hash break, so it is gated behind a new format string
and the old one is kept working in two distinct senses:

```
{"existing_npz_loaded": 4504, "load_hash_mismatches": 0,
 "shapes_rebuilt_in_manifest_format": 30, "rebuild_hash_mismatches": 0,
 "v2_hash_equal_to_v1": 0, "v2_totals_or_round_trip_bad": 0,
 "v1_refuses_non_natural_order": true,
 "refusal": "the legacy pairwise-tables-v1 header cannot record an arc order;
             use fmt='pairwise-tables-v2' for order [1, 2, 3, 4, 0]"}
```

- **Loadable**: all 4504 existing `.npz` across the six production tiers load and
  reproduce the `tables_sha256` their manifest recorded. `load()` hashes exactly
  the header it read (`tables_sha256(tab, hdr=hd)`), so a v1 file is hashed over
  the v1 key set whatever this version would write.
- **Rebuildable**: 30 sampled shapes rebuilt from the gpu-blast source in the
  manifest's own format reproduce that same hash. This is what
  `verify_tier_exhaustion_pairwise.py --rebuild -1` and `verify_tier_combined.py`
  need to earn their claim.
- **Distinct**: a v2 build of the same shape never collides with the v1 hash.

### A verifier must rebuild by the RECORDED order, not by the rule name

The reviewer measured a real failure on an honest tier: manifest
`total_prefixes` 38466 from a narrow-first build against a 38784 natural
rebuild, `rebuilt_mismatches` 2, exit 1. The cause is that a rebuild keyed on
the manifest's **rule name** rebuilds in whatever that name means at rebuild
time — and this change moved the default rule to `natural`, so the name no
longer reproduced the tier it named. A rule is a default that can move; the
recorded order is the thing the stored `tables_sha256` actually covers.

`pairwise_tables.rebuild_order(manifest, meta)` is now the single source of that
decision and both verifiers call it: the per-shape recorded `order` for a v2
manifest, `None` (natural) for a v1 manifest, and a raised error — never a
guess — for a v2 manifest that has lost a shape's order. The verifiers catch
that error, count the shape as a mismatch and name it in `errors`, so a damaged
manifest fails loudly instead of quietly rebuilding a different tier.

Reproduced and closed on a scratch v2 tier built with a non-natural rule
(`_w21scratch/check_rebuild.py`, 4 real n68-b11 shapes):

| shape | manifest total_prefixes | rebuilt by rule name | rebuilt by recorded order |
|---|---|---|---|
| 19023 | 1,121,070,054 | 1,970,052,395 (hash differs) | 1,121,070,054 (hash matches) |
| 19026 | 3,061,685,271 | 3,881,282,441 (hash differs) | 3,061,685,271 (hash matches) |
| 19027 | 1,123,841,802 | 803,473,669 (hash differs) | 1,123,841,802 (hash matches) |
| 19029 | 848,363,629 | 1,133,198,608 (hash differs) | 848,363,629 (hash matches) |

```
{"shapes": 4, "RED_rule_name_rebuild_mismatches": 4,
 "GREEN_recorded_order_rebuild_matches": 4, "LOUD_missing_order_raises": true,
 "refusal": "pairwise-tables-v2 tier manifest records no order for this shape,
             so its tables_sha256 cannot be reproduced; rebuild the tier",
 "V1_rebuild_order_is_natural": true, "passes": true}
```

That is the RED/GREEN for this gate: the old rule-name rebuild fails all four
shapes, the recorded-order rebuild reproduces all four, a missing order refuses
by name, and a v1 manifest still rebuilds natural in the legacy header. The
4504-load / 30-legacy-rebuild check above was re-run after this change and is
still 0 mismatches.

`rebuild_order` is reached only from the two verifiers, and no test imports
either verifier, so the GPU and carry tests cannot be affected by it; they were
not re-run for this change. `test_pairwise_tables.py` was re-run and is
unchanged (18 order runs, 524,231 prefix blocks OK, 0 failures).

## What changed, by symbol

`pairwise_tables.py`
- `build(..., order=None, fmt=FORMAT_V2)`. `order` is a permutation, a rule
  name, or None. A rule name is resolved **after** `derive()` via
  `order_from_derived`, so a build pays for the pair staircases once — `derive`
  is not called twice per shape.
- `check_order`, `ordered_view`, `natural`, `permuted`, `ord_lows`, `ord_hi`,
  `permute_mask`: the order algebra. `lows`, `hi`, `Tarr` and `forms` stay in
  NATURAL arc order (they describe the shape); `states`, `trans`, `P`, `C` are in
  ASSIGNMENT order.
- `pair_admissible_mass`, `order_from_derived`, `choose_order`,
  `choose_order_measured`, `ORDER_RULES`, `REST_RULES`, `MEASURED_RULE`,
  `DEFAULT_ORDER_RULE`.
- `FORMAT_V2`, `FORMATS`, `_HEADER_KEYS_V1`, `_HEADER_KEYS_V2`; `header` selects
  the key set by the header's own format string; `tables_sha256(tab, hdr=None)`.
- `unrank_prefix` / `rank_prefix` take and return ASSIGNMENT-order prefixes;
  `completions` returns the two completion arcs' values; `iterate_compositions`
  yields NATURAL-order vectors. `kernel_pack` uploads permuted `lows`, `hi`,
  `Tlast` and permuted form masks.
- `build_tier(..., rule=DEFAULT_ORDER_RULE, fmt=FORMAT_V2)` records `order_rule`
  in the manifest and each shape's `order` per shape.

`gpu_search_pairwise.py`
- **The CUDA source is unchanged.** The kernel works entirely in assignment
  order and knows nothing about the permutation.
- `Engine.run` un-permutes every arc vector — hits and debug rows — back to
  natural order before `materialise`, `search/verify.py` and the return.
- `controls(..., rule=None)` can build the control tables permuted.

`test_pairwise_tables.py`, `test_pairwise_gpu.py`, `test_pairwise_carry.py`: the
order and format cases described above.

`verify_tier_exhaustion_pairwise.py`, `verify_tier_combined.py`: rebuild in the
manifest's format and the shape's recorded order, through
`pairwise_tables.rebuild_order`; a manifest that cannot supply one is counted as
a mismatch and named in `errors`.

`gpu_state_runner_pairwise.py`: `load_manifest` accepts any format in
`PT.FORMATS` instead of only v1 — without this a v2 tier could never be run.
This is a widening; it refuses exactly what it refused before, plus nothing.

Not touched: `pairwise-prod/`, `tables/`, `tables-ext/`, `partitions/`, any
`pairwise-state-*.json`, any chain script. No state file was written. Nothing
was copied to the laptop.

## Commands

```
cd search/shapecsp/pairwise
# all test runs go through a pinner: cores 4,5, below-normal priority
python _w21scratch/pinned.py test_pairwise_tables.py
python _w21scratch/pinned.py test_pairwise_gpu.py
python _w21scratch/pinned.py test_pairwise_carry.py
python _w21scratch/pinned.py test_pairwise_tables.py --format pairwise-tables-v1
python _w21scratch/pinned.py test_pairwise_gpu.py    --format pairwise-tables-v1
python _w21scratch/pinned.py test_pairwise_carry.py  --format pairwise-tables-v1

python _w21scratch/pinned.py _w21scratch/check_formats.py   # 4504 loads + 30 legacy rebuilds
python _w21scratch/pinned.py _w21scratch/check_rebuild.py   # rule-name RED vs recorded-order GREEN
python _w21scratch/mutate_natural.py     # GREEN / RED / GREEN on natural()
python _w21scratch/sweep_pairs2.py       # every completion pair, 20 shapes per tier
python _w21scratch/analyse_sweep.py      # scores each rule against the measured optimum
python _w21scratch/full_tier.py          # natural vs each cheap rule, EVERY shape
```

Raw outputs are in `search/shapecsp/pairwise/_w21scratch/` (scratch, not
committed): `sweep-pairs-2.jsonl`, `full-tier.jsonl`, `sweep-analysis.out`,
`check-formats.out`, `mutation-natural.out`, `f-*.out`, `v1-*.out`.

Full-tier build cost, for scheduling: 3455.4 s for n68-b11 (1257 shapes x 4
orders) and 698.4 s for n68-b12 (298 x 4), on 2 workers pinned to cores 4,5.
