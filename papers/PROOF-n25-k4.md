# Toward a human-readable proof that no $C_{25}+4$ chords is pancyclic

Status up front, honestly: **this is not a complete proof.** It is a rigorous
partial case tree. Sections 1–4 are fully proved. Section 5 (Case A) is pushed
as far as I could get it by hand and stalls at a genuine open point, backed by
concrete computational evidence that the stall is real (not just a failure of
nerve). Sections 6–7 (Cases B, C) are set up but not resolved. Griffin's
non-existence result for $n=25,k=4$ (implicit in Table 1 jumping from
$m(24)=28$ to $m(25)=30$, i.e. $h(24)=4\to h(25)=5$) rests on exhaustive
computer search; nothing here reproduces that search by hand, and I am not
claiming otherwise.

## 1. Setup and tools

$G=C_{25}+4$ chords. Suppose for contradiction $G$ is pancyclic. Write $t$ for
the number of distinct chord endpoints ($4\le t\le8$) and $m_1\ge\cdots\ge m_t$
for the interior sizes of the $t$ arcs; $\sum m_i=25-t$.

Tools used, each already established (either in the literature already
catalogued by this project, or in `notes/01-subdivision-reformulation.md` as
corrected and re-verified in `papers/REVIEW-notes01.md`):

* **Shi's cycle-space dichotomy.** For a fixed chord subset $K$, at most two
  cycles exist (one per "alternating arc class"); if both exist their lengths
  sum to $n+2|K|$, and at most one has length $\le n/2+|K|$
  (`papers/1312.0274.txt`, Theorem 2 (Shi)).
* **Shi's exact $M(4)$.** The maximum number of cycles in *any* Hamiltonian
  graph with 4 chords is exactly $M(4)=2^4+4\cdot3+1=29$ (Shi's lower-bound
  formula holds with equality for $k\le4$; `papers/REPORT-cyclecounts.md`,
  "Exact M(k)" table). This is sharper than the crude $2^{k+1}-1=31$ ceiling.
* **The corrected arc bound** (`papers/REVIEW-notes01.md`, Addendum §3): an
  arc whose endpoints are *not* joined by a chord has interior
  $m\le\lfloor(n-2)/2\rfloor$; if they *are* chord-joined, $m\le\lfloor(n-1)/2\rfloor$.
  For $n=25$: **$m\le11$ (non-joined) or $m\le12$ (joined).**
* **The wall inequality** (`papers/REVIEW-notes01.md`, Addendum §5): ordering
  gaps $m_1\ge m_2\ge\cdots$, cutting by the $j$ largest arcs into $j$
  "stretches," and letting $c_j$ be the number of components of the multigraph
  of cross-stretch chords, $m_j\le2^{k-j+c_j}$.
* **The triangle case split** (Griffin/`search/pancyc.c`, already exhaustive
  and already used as the top level of the project's own computer search): a
  pancyclic graph's length-3 cycle arises, up to rotation, from exactly one of:
  **(A)** a span-2 chord $(0,2)$; **(B)** two chords $(0,b),(1,b)$ sharing an
  endpoint (no span-2 chord present); **(C)** three chords $(0,b),(b,c),(0,c)$
  forming a chord-only triangle (no span-2 chord, no shape-B pair present).
* **A length-4 requirement**, at the level of rigor supplied for this
  assignment (I have not independently re-derived its exhaustiveness the way
  Griffin's paper derives the length-3 split, so I am using it as a supplied
  tool, not a proven lemma of this document): a 4-cycle needs a span-3 chord,
  or two chords sharing a vertex at the right spacing, or a "parallel" chord
  pair $(a,b),(a{+}1,b{+}1)$, or enough chords to form a chord-only 4-cycle.

## 2. The wall inequality specialized to $k=4$, $n=25$

Writing out $m_j\le2^{k-j+c_j}$ for $j=1,2,3$ (as requested):

* **$j=1$:** cutting by the single largest arc leaves one stretch; the
  "multigraph on one vertex" is trivially $1$ component, so $c_1=1$ always.
  $m_1\le2^{4-1+1}=2^4=16$. **This is weaker than the direct arc bound**
  ($m_1\le11$ or $12$), so the arc bound, not the wall inequality, is the
  binding constraint at $j=1$.
* **$j=2$:** $c_2\in\{1,2\}$ (the two stretches are either joined by at least
  one cross-chord, or not). If joined ($c_2=1$): $m_2\le2^{4-2+1}=2^3=8$. If
  not ($c_2=2$): $m_2\le2^{4-2+2}=2^4=16$, but $m_2\le m_1\le12$ regardless by
  ordering plus the arc bound.
* **$j=3$:** $c_3\in\{1,2,3\}$. Fully connected ($c_3=1$, needs $\ge2$ of the
  4 chords as cross-chords to connect 3 stretches): $m_3\le2^{4-3+1}=2^2=4$.
  $c_3=2$: $m_3\le2^{4-3+2}=2^3=8$. $c_3=3$ (no cross-chords at all among the
  3 stretches — all 4 chords within-stretch): $m_3\le2^{4-3+3}=2^4=16$, again
  capped by ordering.

**The only genuinely new constraint from this exercise, beyond the arc bound,
is at $j=3$ with $c_3=1$: if the three largest arcs' stretches are fully
interconnected, the third-largest gap is forced small ($m_3\le4$), and
connecting three stretches costs at least 2 of the 4 available chords,
leaving at most 2 chords for everything else** (the length-3/4 requirements
and all remaining gap structure). I was not able to turn this into a full
contradiction (see Section 5), but it is the sharpest lever this framework
supplies for $k=4$.

## 3. Counting headroom

$G$ needs $23$ distinct lengths ($3,\dots,25$) from at most $M(4)=29$ actual
cycles: **6 units of slack**, tighter than the naive $31-23=8$ the assignment
quotes. No contradiction follows from this alone (6 is not 0), but it bounds
how much redundancy any surviving case can tolerate.

## 4. Top-level case split

Cases A, B, C above (Section 1) are exhaustive up to rotation, per Griffin's
own construction (`search/pancyc.c`). I worked Case A in most depth because
the two $n=24$ extremal graphs supplied for this task,
$(0,2)(1,7)(2,5)(3,18)$ and $(0,2)(0,21)(1,19)(8,23)$, are **both Case A**
(both contain the span-2 chord $(0,2)$) — independently confirmed by reading
off their chord lists directly, not assumed.

## 5. Case A: chord $(0,2)$ present

**What's free.** The subset $K=\{(0,2)\}$ alone, independent of the other 3
chords, always yields exactly the two Shi cycles for that $K$: the triangle
$\{0,1,2\}$ (length 3) and the "bypass vertex 1" cycle (length $n-1=24$),
summing to $n+2=27=3+24$, matching the Shi-pairing sum exactly. The trivial
all-cycle-edges combination gives length $25$. **So $\{3,24,25\}$ are always
present in Case A, regardless of the other 3 chords.** This is a clean, fully
rigorous fact (checked against the pairing-sum identity, not just asserted).

**What's needed.** The remaining $20$ lengths, $\{4,5,\dots,23\}$, must come
from the $2^5-1-3=28$ chord-space combinations involving at least one of the
other 3 chords. By Shi's exact $M(4)=29$ and the 3 already-secured cycles, at
most $29-3=26$ of those 28 combinations can be genuine simple cycles, and we
need 20 of them to hit 20 *distinct* new lengths: **6 units of slack**,
matching Section 3 exactly (as it must, since it's the same global count
re-derived locally).

**Where I stalled.** I could not turn the arc bound or the wall inequality
into a contradiction with only 3 remaining chords and this much slack. At
$n=25$ the arc bound caps the largest arc at $m_1\le11$ (non-joined) or $12$
(joined) — for comparison (recomputed directly from their chord lists, not
assumed), both given $n=24$ extremal graphs sit *below* their own $n=24$
ceiling of $11$, at $m_1=10$ each (see the tables below); a graph with $m_1$
anywhere up to the ceiling is exactly what the counting/arc-bound framework
*permits*, not excludes. The obstruction (if there is one at $n=25$ but not
$n=24$) has to be a genuinely *arithmetic* fact about which combination of
gap sizes can realize all 20 required middle lengths simultaneously, which
is exactly the "log\* recursion" tension `notes/01` describes as the open
crux of the whole problem, not something I resolved here.

### Concrete evidence that the stall is real, not a lack of trying

The task named two $n=24$ Case-A extremal graphs as "the objects any argument
must just barely exclude when $n$ grows by one." I tested this directly and
concretely: for each graph, insert one new vertex into each of its gaps in
turn (shifting later chord endpoints by 1) and check pancyclicity of the
resulting $n=25$, same-4-chords graph with `search/verify.py`'s
`networkx.simple_cycles` method.

**$G_1=(0,2)(1,7)(2,5)(3,18)$, $n=24$**, gaps (arc, interior size)
$(0,1,0),(1,2,0),(2,3,0),(3,5,1),(5,7,1),(7,18,10),(18,0,5)$:

| insert into gap | resulting $n{=}25$ chords | pancyclic? | missing lengths |
|---|---|---|---|
| $(3,5)$ | $(0,2)(1,8)(2,6)(3,19)$ | no | $4,7,11,23$ |
| $(5,7)$ | $(0,2)(1,8)(2,5)(3,19)$ | no | $5,13,21$ |
| $(7,18)$ | $(0,2)(1,7)(2,5)(3,19)$ | no | $15$ |
| $(18,0)$ | $(0,2)(1,7)(2,5)(3,18)$ (relabelled) | no | $9,19$ |

**$G_2=(0,2)(0,21)(1,19)(8,23)$, $n=24$**, gaps
$(0,1,0),(1,2,0),(2,8,5),(8,19,10),(19,21,1),(21,23,1),(23,0,0)$:

| insert into gap | resulting $n{=}25$ chords | pancyclic? | missing lengths |
|---|---|---|---|
| $(2,8)$ | $(0,2)(0,22)(1,20)(9,24)$ | no | $9,19$ |
| $(8,19)$ | $(0,2)(0,22)(1,20)(8,24)$ | no | $15$ |
| $(19,21)$ | $(0,2)(0,22)(1,19)(8,24)$ | no | $5,13,21$ |
| $(21,23)$ | $(0,2)(0,21)(1,19)(8,24)$ | no | $4,7,11,23$ |

**Every single one of the 8 insertions fails**, and the *same four
missing-length sets* ($\{4,7,11,23\}$, $\{5,13,21\}$, $\{15\}$, $\{9,19\}$)
appear across both graphs — strong evidence $G_1$ and $G_2$ are related by a
symmetry of the construction, not independent data points. The single most
robust near-miss (only one length short) is inserting into each graph's
*largest* gap (interior 10, i.e. $(7,18)$ in $G_1$ and $(8,19)$ in $G_2$),
missing only length $15$ both times. I did not find a clean formula
explaining why $15$ specifically; noting it as an observation, not a derived
fact.

**What this does and does not establish.** It is concrete, honest evidence
that the *specific* growth path from these two known $n=24$ extremal graphs
fails at $n=25$, and that it fails by a small, structured margin (never more
than 4 missing lengths, often just 1). It is **not** a proof that *every*
possible Case-A configuration at $n=25$ fails — only these two graphs' eight
single-vertex extensions were checked, out of a much larger space the actual
exhaustive search (Griffin's, or `search/pancyc.c` if pointed at $n=25,k=4$)
would need to cover to close Case A completely.

## 6. Case B: two chords $(0,b),(1,b)$, no span-2 chord

Not worked beyond the setup. This case has one fewer "free" chord identity
than Case A in an important sense: the length-3 triangle here already commits
2 of the 4 chords (both incident to vertex $b$), leaving only 2 free chords
(versus 3 in Case A) for producing $\{4,\dots,23\}$ (the length-24,25
guarantees from Case A's isolated-chord argument do **not** automatically
carry over here — the two triangle chords are not independent of each other
the way $(0,2)$ was alone, so the clean "free lengths" argument of Section 5
would need to be redone from Shi's pairing for $K=\{(0,b),(1,b)\}$
specifically, which I did not do). **Open.**

## 7. Case C: three chords $(0,b),(b,c),(0,c)$, no span-2 chord, no shape-B pair

Not worked beyond the setup. Here the length-3 triangle commits 3 of the 4
chords, leaving exactly 1 free chord. This is the most constrained case and
plausibly the most tractable to close by hand, but I did not find time to
push it: the 1 remaining chord's placement relative to the three gaps of the
$(0,b,c)$ triangle (which itself has 3 free gap-size parameters summing to
$22$) is a real but bounded case space I have not enumerated. **Open.**

## 8. Honest status summary

| piece | status |
|---|---|
| Wall inequality specialized to $k=4$ ($j=1,2,3$) | proved (Section 2) |
| Sharper counting via $M(4)=29$ | proved (Section 3) |
| Case A's free lengths $\{3,24,25\}$ | proved (Section 5) |
| Case A's full exclusion | **open** — stalls at the arithmetic-of-gaps question `notes/01` already flags as unresolved in general |
| Case A near-miss evidence (8 concrete extensions) | computed and verified (Section 5) |
| Case B | **open**, only set up |
| Case C | **open**, only set up |

This case tree does not reprove Griffin's $n=25,k=4$ non-existence result. It
narrows the problem (free lengths in Case A, the $j{=}3$/$c_3{=}1$ chord-budget
observation in Section 2, the near-miss data in Section 5) and identifies
precisely where a human proof would need a genuinely new arithmetic argument
about realizable gap sums — the same gap the project's general theory has not
yet closed either.
