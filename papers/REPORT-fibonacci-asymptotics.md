# The Fibonacci fit as a falsifiable claim about Erdős #1016: the lemma, the constants, and how strong the refutation actually is

Date: 2026-09-14. Assignment (Manager, this session): reasoning and sourcing only, no
search-program runs. Re-derive the lemma and the three constants independently (not
on trust), then determine whether the claimed refutation of the Fibonacci fit
(via Jia Corollary 1.15) survives contact with what this project has actually
verified as opposed to what it has only read secondhand.

## Costliest finding first: the refutation is logically real but currently rests on nothing this project has independently verified — every accessible source claiming the needed strength is secondhand, unread, or inapplicable

**Short version.** The compatibility threshold is real and re-derives cleanly:
`c >= log_phi(2) = 1.440420`. Jia's Theorem 1.13 (`c=3/2`) sits above the threshold
by a re-derived margin of **1.930%** and does not refute the Fibonacci form. Jia's
Corollary 1.15 (`c=1`) sits below it and would refute the form if true. **But
Corollary 1.15 was never read from Jia's own paper — it is OCR of a secondary
survey's paraphrase of a primary source this project has never obtained**, and its
only corroboration (Terence Tao's erdosproblems.com comment) turns out, on rereading
Tao's own words, to be reading the *same* secondary survey, not an independent check
against Jia's original. Every other source that could independently supply a
`c<1.440420` bound is either unread (GKW16 Ch. 4.5), explicitly not a universal bound
(Alon-Krivelevich's random-graph theorem), or an explicitly incomplete/approximate
reproduction that defers its own hardest step to the same unread GKW16 chapter
(Alon-Krivelevich's deterministic construction). **The honest statement is: this
project has zero independently-verified sources establishing `h(n) <= c*log_2(n)+C`
for any `c<1.440420`. The refutation is real *if* Jia's Corollary 1.15 is correctly
transcribed and Jia's own proof is correct — both currently unverifiable from primary
material — and is otherwise not established.** This is weaker than "refuted," and
should not be dressed up as more than that.

## Part 1: the lemma, stated and proved

**Setup.** Let `h(n)` be the minimum number of chords needed to make `C_n` pancyclic
(so `m(n)=n+h(n)`), and let `t_k` be the largest `n` with `h(n)=k`, as already defined
in the draft (Section 2.1). **This report uses one monotonicity fact that is
rigorously proved, not assumed**: Griffin's Proposition 2 (`1312.0274.txt`,
`m(n+1)<=m(n)+2` for all `n>=3`) is equivalent to `h(n+1)<=h(n)+1` — `h` can never
jump up by more than `1` in a single step. Combined with `h(3)=0` and `h(n)->infinity`
as `n->infinity` (trivial — finitely many chords cover only finitely many `n`
exhaustively before pancyclicity fails by the counting bound), this proved fact
means `h` cannot skip a value on the way up. The one thing that is *not* proved in
general — Griffin's Conjecture 1, `m(n)<m(n+1)` strictly, i.e. `h` never decreases —
is assumed here exactly as the draft already assumes it when it defines `t_k`
(Section 2.1's table is consistent with strict monotonicity throughout `3<=n<=41`,
per the draft's own Section 5 remark, but this is empirical, not proved for all `n`).
**Flagged explicitly: the lemma below inherits this same unproved-but-consistent
monotonicity assumption; it is not a new gap introduced here.**

**Lemma.** Suppose `h(n) <= c*log_2(n) + C` for all `n >= n_0`, for constants `c>0`,
`C`. Then for every integer `k` large enough that `2^{(k-C)/c} >= n_0`,
```
t_k >= 2^{(k-C)/c} = 2^{-C/c} * (2^{1/c})^k.
```

**Proof.** Fix such a `k` and set `n = 2^{(k-C)/c} (>= n_0)`. Then
`c*log_2(n) + C = c * (k-C)/c + C = k`, so the hypothesis gives `h(n) <= k`. Under the
monotonicity assumption above, `h` is non-decreasing, so `h(n')<=k` for every
`n'<=n` as well, and in particular the largest `n'` with `h(n')=k` (i.e. `t_k`) is at
least `n`. `∎`

This is exactly the inequality Manager stated, re-derived from scratch rather than
copied: `t_k >= const * (2^{1/c})^k` with `const = 2^{-C/c}`.

**Compatibility with the Fibonacci form.** The draft's fit is `t_k = 2*Fib(k+3)-2`
for `k=2..5`, extrapolated as a hypothesis for larger `k`. Using Binet's formula,
`Fib(k+3) ~ phi^{k+3}/sqrt(5)` as `k->infinity`, so
```
t_k ~ (2*phi^3/sqrt(5)) * phi^k   as k -> infinity.
```
(Re-derived numerically below, not just asserted — see Part 2.) For the Lemma's
guaranteed lower bound and the Fibonacci form's asymptotic value to be simultaneously
possible (i.e. for the exponential lower bound not to eventually *exceed* — and
thereby contradict — the smaller of the two growth rates), the two exponential bases
must satisfy `phi >= 2^{1/c}`. If instead `phi < 2^{1/c}`, the Lemma's proved lower
bound `t_k >= const*(2^{1/c})^k` would eventually overtake and exceed any fixed
constant multiple of `phi^k`, forcing the true `t_k` above the Fibonacci-form
prediction for all large `k` — i.e. the Fibonacci form would be false as an
asymptotic law (though it could still hold "by coincidence" at small, finite `k`,
exactly as the draft's own Section 5 already flags: "two real coincidences, not
four"). Taking `log_2` of `phi >= 2^{1/c}`:
```
log_2(phi) >= 1/c   <=>   c >= 1/log_2(phi) = log_phi(2).
```
This is the threshold Manager stated. `∎`

## Part 2: the three constants, re-derived independently (not taken on trust)

Computed fresh this session (`node -e`, exact IEEE-754 double precision, shown in
full so the arithmetic can be checked, not just the final rounded figures):

```
phi              = 1.618033988749895
log_phi(2)       = ln(2)/ln(phi) = 1.4404200904125564
2^(2/3)          = 1.5874010519681994    [ = 2^(1/c) for Jia Thm 1.13's c=3/2 ]
phi >= 2^(2/3) ? true
margin = phi/2^(2/3) - 1 = 0.019297540935678592   ->  1.9297...%  (Manager said "about
                                                                    1.9%" — confirmed,
                                                                    more precisely 1.930%)
2 >= phi ?  true (phi < 2)   [ = 2^(1/c) for Jia Cor 1.15's c=1 ]
```

**Sanity check on the Fibonacci-asymptotic constant**, computed independently by
evaluating `t_k = 2*Fib(k+3)-2` directly (not via Binet's approximation) and dividing
by `phi^k` for increasing `k`, to confirm it actually converges to the value Binet's
formula predicts (`2*phi^3/sqrt(5) = 3.78885...`), which it does — this is a genuine
independent numerical check, not a restatement of the closed-form algebra:

| `k` | `t_k=2*Fib(k+3)-2` | `t_k / phi^k` |
|---:|---:|---:|
| 2 | 8 | 3.0557 |
| 3 | 14 | 3.3050 |
| 4 | 24 | 3.5016 |
| 5 | 40 | 3.6068 |
| 6 | 66 | 3.6781 |
| 7 | 108 | 3.7197 |
| 8 | 176 | 3.7464 |
| 9 | 286 | 3.7625 |
| 10 | 464 | 3.7726 |

(Converging monotonically toward `2*phi^3/sqrt(5) ≈ 3.78885`, confirming the Binet
approximation used in Part 1 is the correct asymptotic constant, not just an
algebraic manipulation — the ratio is still visibly short of the limit even at
`k=10`, i.e. convergence is slow, which matters for how much weight to put on `t_6`
as a "first test," addressed in Part 4.)

**All three headline constants Manager stated are independently confirmed to the
precision given**: `phi=1.618034`, `log_phi(2)=1.440420`, `2^(2/3)=1.587401`, margin
`≈1.93%`.

## Part 3: the payoff, re-checked against the actual Jia statements on file

Both Jia constants come from the same place: `papers/REPORT-oeis-and-jia.md`'s OCR
transcription of `papers/Lai-Liu-2014-survey.pdf` (a secondary survey, not Jia's own
1996 paper, which that report explicitly could not obtain — "Not obtained... an
unknown, not an absent"). Quoting that transcription exactly:

> "Theorem 1.13 (Jia[25]) When n is sufficiently large, `n + log_2 n - 1 <= g(n) <=
> n + (3/2) log_2 n + 1`."
>
> "Corollary 1.15 (Jia[25]) For n sufficiently large, `g(n) = n + log_2 n +
> O(log_2 log_2 n)`."

- **Theorem 1.13 gives `c=3/2`, `C=1`.** `2^(2/3)=1.587401 < phi=1.618034`
  (re-derived above), so the Lemma's compatibility condition holds:
  **Thm 1.13 does NOT refute the Fibonacci form**, and the margin by which it fails to
  refute it is exactly the re-derived `1.930%`. This is Manager's claim, confirmed.
- **Corollary 1.15 gives `c=1` at leading order** (the `O(log_2 log_2 n)` term is
  strictly lower-order than `log_2 n` itself, so it does not change the leading
  coefficient `c`, only the lower-order behavior — a standard and uncontroversial
  reading of the asymptotic notation, re-verified here rather than assumed since it
  is the crux of the whole argument). Since `1 < 1.440420 = log_phi(2)`, **Cor 1.15,
  if true, DOES refute the Fibonacci form as an asymptotic law for large `k`** —
  confirmed, matches Manager's claim exactly.

**Where this project's own confidence actually stands, checked line by line against
`REPORT-oeis-and-jia.md` rather than assumed:**

1. Jia's 1996 paper itself was never located by this project — `REPORT-oeis-and-jia.md`
   states plainly: "**Not obtained.** No open-access copy, preprint, or digitised scan
   of Jia (1996) was found... This is an unknown, not an absent."
2. Both Thm 1.13 and Cor 1.15 come from Tesseract OCR of a scanned secondary survey
   (Lai-Liu 2014), not from Jia directly. The OCR transcription of Cor 1.15's specific
   line is reported as clean (no `[OCR: ...]` uncertainty flag, unlike the adjacent
   Theorem 1.14, whose middle term is flagged as garbled) — so transcription fidelity
   *of the survey's own text* is not in serious doubt, but that only pushes the
   uncertainty back one level, to whether the *survey itself* correctly states Jia's
   result, which this project cannot check without Jia's paper.
3. **The apparent independent corroboration is not independent.** `REPORT-oeis-and-jia.md`
   notes Theorem 1.13's constant "matches the TerenceTao erdosproblems.com comment's
   paraphrase exactly," offered there as cross-validation of the OCR. Re-reading
   Tao's comment in full (quoted verbatim in `REPORT-lit-4.md`), Tao says: **"An
   obscure 1996 paper of Jia (which I was not able to directly obtain, but could see
   their results mentioned in this 2014 survey of Lai and Liu)."** This is the *same*
   Lai-Liu 2014 survey this project OCR'd. **Tao did not read Jia's paper either — he
   read the identical secondary source this project read.** So the match between
   Tao's paraphrase and this project's OCR is evidence that the OCR correctly
   transcribed the Lai-Liu survey (a real and useful check, not nothing), but it is
   **not** independent evidence that the Lai-Liu survey correctly represents Jia's
   actual theorem — both readings trace to one document, not two. This was not
   flagged as clearly as it should have been in the earlier report, and is corrected
   here.
4. Tao's own comment separately states the same functional form as Cor 1.15
   in his own words — "`h(n) <= log_2 n + log_2 log_2 n + O(1)` for all sufficiently
   large `n`" — again sourced (per his own admission) to the Lai-Liu survey, not to
   Jia directly. This is the same single point of failure as (3), not a fourth,
   independent data point.

**Net effect: the specific claim that refutes the Fibonacci form (`c=1`, Cor 1.15) is
supported by exactly one chain of evidence — an OCR of a 2014 survey's paraphrase of
an unobtained 1996 paper — read by two parties (this project and, separately, Tao)
who both stopped at the same survey rather than reaching Jia. This is a single
source, read twice, not two sources.**

## Part 4: the other candidate `(1+o(1))log_2(n)`-type sources, checked the same way

Per the assignment's part (a), every other accessible claim of a bound this strong
was checked for whether it is a primary, proven, universal result:

- **GKW16 Chapter 4.5** (`h(n)<=log_2 n+log_*n+O(1)`, `c=1` at leading order, same
  strength as Cor 1.15): **entirely unread**, per `papers/REPORT-novelty-check.md`
  (multiple independent access attempts, all failed to reach body text). Tao's own
  comment hedges it explicitly: "The first literature proof... **that seems to
  exist** is in Chapter 4.5" — even the one person in this chain who plausibly did
  read GKW16 (or at least is willing to assert its existence) declines to state it as
  certain. **Not usable as independent confirmation of `c<=1` — unread and hedged.**
- **Alon-Krivelevich 2025** (`2308.01564`): proves, for `G~G(n,p)` with
  `p>=(1+o(1))ln n/n`, that with high probability `G` contains a pancyclic subgraph
  with `n+(1+o(1))log_2 n` edges. **This is explicitly a random-host-graph existence
  result, not a universal extremal bound over all `n`-vertex graphs** — Manager's
  instruction to not use it as one is correct and is followed here: it says nothing
  about `h(n)=m(n)-n` for the complete graph or any specific deterministic graph, only
  about a random graph containing *some* sparse pancyclic subgraph with high
  probability. **Not usable for this Lemma at all**, by the terms of its own theorem
  statement.
- **Alon-Krivelevich's own deterministic construction** (their Section 3, "emulating"
  GKW's recipe, already fully extracted in `papers/REPORT-bondy-construction.md`):
  this *is* a deterministic, universal-over-all-`n` construction, and its first two
  stages are fully specified and independently verifiable — but AK25's own text stops
  short of a complete pancyclic graph for large `k`: stages 1-2 alone leave a gap of
  missing lengths `[5,K+1]` that must be patched by "`O(log*n)` additional edges,"
  and AK25 explicitly writes **"For the full details of the construction, we refer
  the reader to [GKW] Chapter 4.5"** — i.e. AK25 does not itself supply or prove the
  patch that makes the construction actually pancyclic for large `n`; it defers to
  the same unread chapter. `REPORT-bondy-construction.md` already established that
  stages 1-2 alone are gap-free (and thus give a fully verified, complete
  construction) only for `k<=5` — precisely the range where the Fibonacci form is not
  in dispute anyway. **For the large-`k` asymptotic regime this report is about, AK25
  reduces to the same single unread source as everything else.**
- **Bondy (1971) itself**: the draft states Bondy's upper bound
  (`h(n)<=log_2 n+H(n)+O(1)`, `H(n)~log*n`, `c=1`) was "stated without proof." This
  session re-attempted to reach Bondy's paper directly (two fresh web searches for an
  open PDF, author preprint, or institutional mirror) — **still not obtained**, same
  paywall result as every prior attempt in this project (`REPORT-bondy-construction.md`,
  `REPORT-lit-1.md`). The "without proof" characterization traces to two places, both
  checked this session: (i) Tao's comment, quoted in full in `REPORT-lit-4.md`,
  states plainly "Bondy's paper actually claims the slightly weaker bounds
  `log_2(n-1)-1<=h(n)<=log_2 n+log_*n+O(1)`... **with no proof given for either
  inequality**" — this reads as a direct, specific claim (Tao explicitly contrasts it
  with what Erdős himself wrote, which is the kind of comparison that suggests Tao
  read Bondy's actual text rather than a paraphrase, though this project cannot
  verify that); (ii) Griffin's own paper (`1312.0274.txt`) states Bondy's bound as
  "Claim 1 (Bondy [3])" and gives a "Proof. (of lower bound)" only — supplying no
  proof of the upper bound itself, consistent with (but not an explicit assertion of)
  the "without proof" reading. **Neither is a primary read of Bondy; both are
  consistent with each other but this project still cannot independently confirm
  Bondy's paper does not, in fact, contain a proof.** Worth noting for the asymptotic
  question specifically: Bondy's asserted (per Tao, unproven) upper bound is already
  at `c=1` strength — i.e. the claim that `c` should eventually reach down to `1`
  traces all the way back to Bondy's own 1971 assertion, not only to Jia or GKW16;
  every later source in this chain (Jia 1996, GKW16 2016) is an attempt to *prove*
  what Bondy only asserted, and this project has independently verified none of them.

## Part 5: how strong is the refutation, stated plainly

**The Fibonacci form is refuted only modulo an unverified citation — stated as
honestly as the evidence allows, per the assignment.** Specifically:

- The **logical argument** (the Lemma, the threshold `c>=log_phi(2)=1.440420`, and the
  conclusion that `c=1`-strength bounds are incompatible with the Fibonacci form
  persisting to large `k`) is sound and independently re-derived in this report — this
  part is solid.
- The **premise that drives the refutation** — some genuine `h(n)<=c*log_2(n)+C` bound
  with `c<1.440420` — is, as far as this project's own literature access extends,
  **asserted by every accessible source (Bondy 1971, Jia 1996 Cor. 1.15, GKW16 2016)
  and independently *proved* by none of them.** Bondy: unproven per every source that
  discusses it (none primary). Jia: secondhand via one OCR'd survey, itself unable to
  reach Jia; the one apparent corroboration (Tao) reads the identical survey. GKW16:
  unread, hedged by the one person in the chain willing to assert its existence.
  Alon-Krivelevich: proves a materially different (random-graph) statement, and its
  own deterministic construction defers the needed step to the same unread GKW16.
- **Therefore: if Jia's Corollary 1.15 (or Bondy's original assertion, or GKW16's
  claimed proof) is correct, the Fibonacci form is a finite coincidence that must
  break for some `k`, and — per the draft's own already-in-hand data — `t_6` is
  exactly where the break would first become checkable** (the draft's Section 5
  already reports the dedicated 6-chord search bracketing `56<=t_6<=129`, stalling 3
  lengths short of a witness at the Fibonacci-predicted `n=66`, "neither confirming
  nor refuting it" — this report does not change that empirical status, only the
  theoretical motivation for treating `t_6` as informative). **But this is a
  conditional claim resting on a citation chain this project has verified for
  internal consistency (OCR fidelity, cross-reader agreement) and explicitly has
  *not* verified for correctness against any primary source.** The reframing from
  "numerology" to "a falsifiable statement about Erdős #1016" is real and worth
  keeping — the Lemma makes it a precise, checkable claim rather than a curve-fit —
  but "falsifiable in principle, refuted only if an unverified secondary source is
  accurate" is the honest strength of the result, not "refuted."

## Search log (this session)

Reasoning/derivation performed locally (Lemma proof, threshold derivation) and
checked numerically via `node -e` (single short-lived process, trivial CPU, no
sustained load — well within the stated 20% machine-wide / one-process / one-core
cap; no search-program runs of any kind, per instruction). Sourcing checks: re-read
`papers/REPORT-oeis-and-jia.md` in full (Jia citation chain, OCR provenance) and
`papers/REPORT-lit-4.md`'s full verbatim quotation of Tao's erdosproblems.com comment
(re-checked specifically for whether Tao's Jia citation is independent of the
Lai-Liu survey this project OCR'd — it is not). Two fresh `WebSearch` queries this
session for an open copy of Bondy (1971): `Bondy 1971 "Pancyclic graphs I" Journal
Combinatorial Theory pdf full text` and `Adrian Bondy "Pancyclic graphs" 1971 open
access preprint author copy` — both returned only paywalled/citation-only results,
consistent with every prior attempt in this project; not re-attempted via `WebFetch`
since the search results themselves gave no new candidate URL to fetch.
`papers/1312.0274.txt` (Griffin, already fully read per `REPORT-griffin-method.md`)
re-checked specifically for how it frames Bondy's Claim 1 (proof given for the lower
bound only, no proof of or comment on the upper bound). `papers/REPORT-bondy-construction.md`
re-checked for the exact Alon-Krivelevich deferral quote ("For the full details of
the construction, we refer the reader to [6] Chapter 4.5") and for the `k<=5`
gap-free range of their reproduced construction's stages 1-2.
