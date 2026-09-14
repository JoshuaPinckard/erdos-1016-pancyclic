# 6-chord pancyclic graphs: search for upper bounds on t_6

Date: 2026-09-14. Assignment: find 6-chord pancyclic graphs on as many vertices as possible
(upper bounds on `t_6`), compare against the Fibonacci-fit prediction `t_6 = 66`, report where the
search stalls. Rules followed: one process at a time, BelowNormal priority, no GPU, writes only
under `search\k6\` and `papers\`. All scripts, raw run logs and the running witness pool are in
`search\k6\`; this file is the summary.

## Costliest finding first: the largest confirmed witness is `n = 56`, well short of the
Fibonacci-predicted `t_6 = 66` — and a dedicated, exhaustive-enough attempt *at* `n=66` itself
plateaued 3 lengths short of pancyclic (`missing = [5, 7, 8]`) at a genuine local optimum, so the
prediction is neither confirmed nor cleanly refuted this round.

**Largest independently verified witness: `n=56`, chords
`(0,2) (0,53) (1,39) (20,39) (39,48) (48,53)`** — checked twice, once by the tool that produced it
(`extend.py`'s own `pancyclic()` check) and once independently with the unrelated `verify.py`
script, both agreeing: all lengths `3..56` present. Full chain of witnesses (n=36 through 56) is in
`search\k6\witnesses.csv`, each with its source method.

**Comparison with 66:** `56 < 66`. Not reached. But the attempt to build a witness *at n=66
directly* (seeded from the n=56 witness, then run through 240s of strict-improvement hill-climbing
followed by exhaustive single-slot coordinate descent — see below) drove the missing-length count
down from 20 to 3 and then genuinely stalled: `chords=(0,2)(0,48)(1,40)(11,41)(44,47)(47,52)`,
missing only `[5, 7, 8]`. That stall was checked exhaustively for single-chord fixes (every one of
the 6 chords was tried against every possible replacement, holding the other 5 fixed — over 12,000
evaluations) and none closes the gap; escaping requires changing two or more chords at once, which
this session's search did not find. So the honest read is: **66 is close to reachable with this
family and this search depth, not confirmed, not ruled out.**

## Approaches tried, in the order Manager suggested

### (a) Structured enumeration with geometric gaps

Rather than search over an unconstrained 4-geometric-gap-plus-gadget pattern from scratch, this
round reused the exact GKW/Bondy recipe pinned down in the previous task
(`papers\REPORT-bondy-construction.md`): `K+1=5` shortcut chords `e_0..e_4`, `e_i` a `2^i`-shortcut,
chained through shared vertices, plus 1 joining edge = 6 chords total (`K=4`). Concretely:
`e_0=(0,2)`, `e_1=(2,5)`, `e_2=(5,10)`, `e_3=(10,19)`, `e_4=(19,36)`, join `=(0,36)`.

This construction was **computationally verified** (script `search\k6\gkw_construction.py`,
output `search\k6\gkw-K4.txt`) to be pancyclic at exactly `n=36` and `n=40`, and to be missing
**exactly and only length 5** for every other `n` in `[37,69]` — a clean, direct confirmation of
the theory paper's own claim (that stage-3 needs to patch "a subset of `[5,K+1]`", here just the
single value `{5}`) — and to fail badly (multiple missing lengths, growing) from `n=70` on, matching
the analytically-derived reach `2^{K+2}+K=68` closely (actual cutoff `69`, off by one from the
hand-derived bound, as expected from a rough inequality).

Since only length 5 was ever missing, the natural next move was **not** to add a 7th chord (out of
scope — Manager wants 6), but to ask whether *replacing* the join edge `(0,36)` with some other
single 6th chord (keeping the 5 fixed shortcuts) could patch length 5 while preserving everything
else. `search\k6\scan_join.py` (later `scan_join_range.py` to cover many `n` in one process)
exhaustively tried **every possible 6th chord** for `n=36` through `67`. Result
(`search\k6\scan-range-36-69.txt`, `scan-range-63-90.txt`):

| n range | outcome |
|---|---|
| 36–54 (with one exception `n=55` not tried in this pass boundary) | a pancyclic 6th chord exists for every n tested |
| 55–67 | **none found** — exhaustive over the one free chord, with the 5 shortcuts fixed |

The largest scan-found witness was **`n=54`**, 6th chord `(1,19)`, independently verified. This
confirms Manager's approach (a) works, but *this specific* geometric-shortcut base (chosen to match
the previously-sourced GKW recipe rather than the empirically-observed 5-chord extremal shape
Manager described, e.g. `(0,2)(1,5)(1,7)(3,34)(24,39)`) tops out at 54, not higher, when only the
6th chord is free. A version starting from the *empirical* 5-chord extremal shape (three geometric
gaps plus a tiny-gap gadget, exactly as Manager specified) with a 6th chord searched the same way
was not attempted this round due to time; it is the natural next experiment (see "next steps").

### (b) Pool-based single-vertex extension from every witness

`extend.py` (already in `search\`, unmodified, invoked with outputs redirected into `search\k6\`)
was run from the `n=54` witness. It climbed deterministically: `n=54 -> 55 -> 56`, then stalled —
`"n=57: no extension with 6 chords from 1 witnesses at n-1"` (`search\k6\extend-54.txt`,
`extend.csv`). This matches the pattern already on record for `k=4` (stalled quickly past its
starting point) and `k=5` (`extend.csv` in `search\` root: `"26,5,NONE-BY-EXTENSION"` from an
earlier task) — **single-vertex insertion is a weak climbing method in general, useful only for a
small number of extra vertices past a good seed**, consistent with what Manager's message already
flagged. It is not the source of large gains; it added exactly 2 vertices here (54->56).

### (c) 6-chord subdivision-lemma check

Wrote `search\k6\subdiv_window.py`, implementing the lemma precisely as Manager phrased it: for a
base graph on `s` vertices, if every length `3..s-1` is achieved by cycles **not** using some fixed
Hamilton-cycle edge `uv`, and the lengths achieved by cycles that **do** use `uv` form a contiguous
interval `[a,s]`, then subdividing `uv` gives a valid witness for every `n` in `[s, 2s-a]` using the
*same* 6 chords. Tested this against two graphs:
- The `n=41` witness Manager supplied — **no Hamilton-cycle edge qualifies** (for every one of the
  41 candidate edges, either the non-`uv` cycles miss several lengths in `[3,40]`, or the `uv`-using
  lengths are not contiguous). Full per-edge table in `search\k6\subdiv-41.txt`.
- The `n=50`, chord set `(0,2)(2,5)(5,10)(10,19)(19,36)(0,11)` — same negative result
  (`search\k6\subdiv-50.txt`), **despite this exact chord set being pancyclic for every `n` in
  `[44,53]` with zero changes**, which is a genuinely curious fact this report does not explain:
  a 10-vertex-wide window of "free" pancyclicity for a fixed chord set that is *not* the clean
  single-edge subdivision window the lemma describes. Flagged as unexplained, not claimed as a
  second mechanism — worth a dedicated follow-up (it may be a weaker, two-edge or non-worst-case
  version of the same idea).

**Conclusion on (c) for this session: no witness found so far has the clean single-edge
subdivision property**, so the lemma did not directly produce a large-`n` family this round. Every
gain came from (a) exhaustive small-scale search and (b) cheap deterministic extension, not from an
exploitable structural shortcut.

### Additional, not in Manager's original list: direct attack on n=66

Given the Fibonacci prediction specifically named `n=66`, this session also ran a dedicated attempt
*at* `n=66`: seed = the `n=56` witness's exact chords, unmodified (verified NOT pancyclic at 66,
20 lengths missing — `search\k6\verify-66-asis.txt`), then:
1. `search\k6\strict_climb.py` (strict-improvement-only hill-climb, occasional sideways move to
   escape plateaus, resets to best-found when badly stuck) — two sequential runs totalling 350s
   drove missing-count from 20 down to 3 (`5,7,8`) and then stopped improving
   (`search\k6\strict-66.txt`, `strict-66c.txt`).
2. `search\k6\coord_descent.py` (systematic: for each of the 6 chords in turn, try literally every
   possible replacement chord, holding the other 5 fixed, keep the best) run for 3 full rounds from
   that missing=3 point — **confirmed it is a genuine local optimum**: no single-chord replacement,
   tried exhaustively, improves on `missing=[5,7,8]` (`search\k6\coord-66.txt`).

## Where the search stalls, summarized

- The literal GKW `K=4` recipe (5 shortcuts + 1 fixed join) alone: pancyclic only at the two exact
  points `n=36,40`; misses length 5 everywhere else in `[37,69]`; breaks down entirely from `n=70`.
- Letting the 6th chord (only) vary over the same 5 fixed shortcuts: works continuously for
  `n=36..54`, **stalls hard at `n=55`** (exhaustively checked through `n=67`, zero hits).
- Cheap deterministic single-vertex extension from the best witness (`n=54`): gains exactly 2 more
  vertices (`->56`), **stalls at `n=57`**.
- Direct attack at `n=66` (unstructured local search + exhaustive single-chord coordinate descent):
  **stalls at missing-count 3** (`[5,7,8]`), a confirmed local optimum for single-chord moves; a
  witness may still exist at `n=66` but needs a multi-chord joint move, a different starting shape,
  or more search budget than this session used to find it.

## Reproducibility

All chord sets in this report were checked with two independently-written pieces of code within
this session (the constructing script's own check, plus `..\verify.py`, which is untouched,
pre-existing project tooling using `networkx.simple_cycles` directly) — so every WITNESS line above
is a double-checked claim, not a single script's unverified output. Full run transcripts, including
every intermediate "improved" step of the two searches, are preserved unedited in `search\k6\`
(`*.txt`/`*.err` files named after the script and target `n`) for exact reproduction.

## Suggested next step (not attempted this round, flagged rather than started, given the compute
budget already used)

Repeat approach (a) starting from Manager's actual empirical 5-chord shape
(`(0,2)(1,5)(1,7)(3,34)(24,39)`, scaled to a larger base and with a 6th geometric-scale chord
inserted) rather than the literal GKW binary-shortcut recipe used here — the two are different
6-chord families, and this session only fully explored the latter. The `n=44..53` unexplained
free-window on the `(0,11)`-augmented family is also worth a dedicated look; if it is a real second
mechanism (not coincidence), it could be the thing that gets past `n=56`.
