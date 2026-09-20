# Pairwise-admissible GPU enumeration: table format and kernel contract

Manager, 2026-09-19. Binding for Worker 20 (tables), Worker 21 (kernel + runner),
Worker 22 (cutover). Change the spec only through the Manager.

## Why

Measured by prune_pairwise.py on the real manifests (pairwise-n*-b*.jsonl):

| tier | unrestricted ranks | pairwise-admissible | prune |
|---|---|---|---|
| n68 b12 | 3.380e14 | 8.074e12 | 41.9x |
| n69 b12 | 4.020e14 | 9.084e12 | 44.3x |
| n70 b12 (232/281) | 3.680e14 | 7.882e12 | 46.7x |
| n68 b11 | 2.805e14 | 2.814e13 | 10.0x |
| n69 b11 (110/1234) | 2.650e13 | 1.728e12 | 15.3x |

Peak DP states per level <= 5197, no state blow-ups, 1-3 CPU s per shape.
The remaining six tiers are ~1.94e15 unrestricted ranks (372 h on both GPUs);
pairwise-admissible they are ~8e13 compositions. Enumerating exactly the
admissible set is what turns the prune into wall-clock time.

## The set

A(n, shape) = { a in Z^b : sum a = n, lows_i <= a_i <= hi_i, and for every
ordered pair i != j: a_j <= T[i][j][a_i - lows_i] }.

lows from bound.intervals (must equal the manifest row's lows). hi from
prune_pairwise.Shape.per_arc_caps. T from Shape.pair_staircases. Soundness:
bound.hall_ok is monotone non-increasing in lows and holds for every lows <= a
when a is pancyclic, so A contains every pancyclic composition (argument at the
top of prune_pairwise.py). pair_count_dp counts A exactly; its count is the
tier total everything below must reproduce.

Arc order is the natural 0..b-1 for now. Any other order must be recorded as
`order` in the header and hashed.

## Tables: pairwise_tables.py (Worker 20)

build(n, b, chords, lows=None) -> dict with:

- n, b, chords, lows[b], hi[b], forms = sorted(set(S.cycle_forms(b, chords)))
  as (arc_mask, n_chords), exactly as gpu_search.record.
- Tarr: int32 [b][b][VMAX+1], VMAX = max(hi). Tarr[i][j][u] = greatest
  admissible a_j when a_i = u (absolute), for u in [lows_i, hi_i]; a value
  lows_j - 1 means no admissible a_j; entries outside [lows_i, hi_i] are -1.
- Levels k = 0..b-2. states[k] = list of cap tuples (absolute upper bounds
  for arcs k..b-1, length b-k), reachable ones only; states[0] = [tuple(hi)].
  After assigning a_0..a_{k-1}: c_j = min(hi_j, min_{i<k} Tarr[i][j][a_i]).
- trans[k], k = 0..b-3: int32 (len(states[k]), VMAX+1). trans[k][st][v] =
  index into states[k+1] reached by a_k = v, or -1 when v < lows_k, v >
  caps_k(st), or a new cap falls below its lows_j (dead). Dead is monotone:
  once -1 at some v0 >= lows_k it stays -1 for all v > v0 (assert in build).
- P[k], k = 0..b-2: int64 (len(states[k]), n+1). P[k][st][s] = number of
  admissible prefix extensions (a_k..a_{b-3}) from st with partial sum s whose
  end state has at least one valid completion. P[b-2][st][s] = 1 if
  C[st][s] > 0 else 0. P[k][st][s] = sum_v P[k+1][trans[k][st][v]][s+v].
- C: int64 (len(states[b-2]), n+1). C[st][s] = number of valid (v, w):
  v in [lows_{b-2}, caps_0(st)], w = n - s - v in [lows_{b-1}, caps_1(st)],
  w <= Tarr[b-2][b-1][v]. Assert the mirrored condition
  v <= Tarr[b-1][b-2][w] agrees (downward closure) in tests.
- total_prefixes = P[0][0][0]. total_compositions = sum over all prefixes of
  C at their end (state, s). build() asserts total_compositions ==
  pair_count_dp(n, lows, hi, T)[0].

Prefix rank = lexicographic position of (a_0..a_{b-3}) among prefixes with
P > 0:

    unrank_prefix(r): st = 0; s = 0
      for k in 0..b-3:
        for v in lows_k..caps_k(st):
          st2 = trans[k][st][v]; if st2 < 0: break
          c = P[k+1][st2][s+v]
          if r < c: a_k = v; st = st2; s += v; break
          r -= c
      return a[0..b-3], st, s
    rank_prefix inverts it. completions(st, s) -> [(v, w)] by increasing v.

CPU reference enumerate_admissible(n, lows, hi, Tarr) -> every a in A by
plain recursion, no ranks, no tables. Tests, exhaustive on small real manifest
shapes (pick like bounded/test_bounded_exactness.pick_cases), printing counts:

1. [for r in 0..total_prefixes-1, for (v,w) in completions] == enumerate_admissible
   as an ordered sequence; zero duplicates, zero missing, zero extra.
2. rank_prefix(unrank_prefix(r)) == r for every r.
3. total_compositions == pair_count_dp == len(enumerate_admissible).
4. SOUND: prune_pairwise.py verify at an --eval-n where SAT compositions exist:
   sat_not_admitted == 0 (GREEN); --mutate-cap 1 goes RED. Record both outputs.
5. prune_pairwise.py selfcheck GREEN (hall_batch == bound.hall_ok).

save(path, tables) -> .npz with every array plus a JSON header (n, b, chords,
lows, hi, order, sizes, total_prefixes, total_compositions) and tables_sha256
= sha256 over canonical little-endian bytes of (header JSON, Tarr, states[k]
for each k, trans[k] for each k, P[k] for each k, C). load(path) recomputes and
checks the hash. Portable: LF, UTF-8, no absolute paths inside.

build_tier(source, n, b, out_dir) writes one .npz per shape plus
tier-manifest.json {n, b, source_sha256, shapes: {shape_index: {tables_sha256,
total_prefixes, total_compositions, states_per_level}}, tier_total_prefixes,
tier_total_compositions, excluded: [shape_index with total_compositions == 0]}.
Deterministic: two builds of the same tier produce byte-identical files.

## Kernel and runner: pairwise/gpu_search_pairwise.py, gpu_state_runner_pairwise.py (Worker 21)

- One launch = one shape, prefix ranks [offset, offset+count). Thread t:
  r = offset + t; return if r >= total_prefixes. Unrank exactly as above;
  trans and P in global memory (one shape's tables are a few MB); lows, hi,
  caps of the reached state, Tarr[b-2][b-1], forms and per-form deltas in
  shared memory.
- Completion loop: base_f = n_chords_f + sum_{i < b-2, i in f} a_i once per
  thread. delta_f = [b-2 in f] - [b-1 in f]. For v from lows_{b-2} to
  caps_0(st): w = n - s - v; if w < lows_{b-1} break; valid iff w <=
  caps_1(st) and w <= Tarr[b-2][b-1][v]. Maintain len_f incrementally
  (len_f += delta_f per unit step of v); on each valid (v, w) run the
  coverage/SAT test byte-identical to gpu_search.scan (cov0/cov1, need0/need1).
  Every thread atomically adds its number of VALID completions to a per-launch
  uint64 `compositions`; the host records it per unit.
- Guard: any unranked a_k outside [lows_k, caps] or a counted completion
  violating its bounds increments `viol`; the host raises. Hit = (shape,
  prefix rank, v); host materialises a, calls search/verify.py pancyclic,
  raises on rejection. Debug mode records every visited composition.
- Controls before every run: the n=67 and n=56 witnesses lie in A (assert every
  pair constraint), their (prefix rank, v) is SAT from a 1-thread launch, and
  for 22 sampled prefix ranks per control shape the GPU arcs equal the CPU
  unrank and every completion's SAT flag equals verify.py.
- Exact-set test (model: bounded/test_bounded_exactness.py): GPU-visited
  compositions == enumerate_admissible as an ordered sequence; GPU SAT count ==
  CPU SAT count over A; per-launch `compositions` == total_compositions.
- Runner: units over prefix ranks, UNIT_PREFIX = 2**31; state carries
  enumeration = "pairwise-v1", plan_sha256 over (n, tier-manifest sha256, unit
  layout), per-unit compositions; --only-shapes; refuses a state file without
  its enumeration tag. verify_tier_exhaustion_pairwise.py: expected units from
  the tier manifest, zero missing, zero extra, sum of per-unit compositions ==
  tier_total_compositions, hits listed. Same lock/heartbeat/atomic-write
  contract as gpu_state_runner.py.
- Perf, same card and tier as the unrestricted kernel: gpu_seconds per unit,
  compositions per gpu-second, and projected tier hours =
  tier_total_compositions / (compositions per gpu-second). That number decides
  the cutover.

## Cutover (Worker 22)

Shapes already fully exhausted under the unrestricted plan stay exhausted;
every other shape of a tier goes to the pairwise plan via --only-shapes (the
partial unrestricted work on it is abandoned: at 10-47x it is cheaper to redo).
The exhaustion statement for a tier is then: unrestricted-exhausted shapes
(verify_tier_exhaustion.py) + pairwise-exhausted shapes
(verify_tier_exhaustion_pairwise.py) = every manifest shape of the tier.
New chain versions only (v7 desktop, v6 laptop); never edit a live script;
probe every migrated state with --wall-budget 1 before the chain starts.
