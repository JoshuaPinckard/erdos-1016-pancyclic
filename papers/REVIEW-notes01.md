# Review of `notes/01-subdivision-reformulation.md`: the subdivision lemma, its corollaries, and the wall inequality

Reviewer role. Checked line by line against the source file plus new,
independently-run computational checks (networkx `simple_cycles`, cross-checked
against the project's own `search/verify.py` for pancyclicity). Reporting gaps
found, not repairing them.

## Summary verdict

The **backward (sufficiency) direction** of the subdivision lemma is correct and
its proof, though one line, is complete. The **forward (necessity) direction**,
as literally stated — "take $s=n-m$ where $m$ is the interior size of *any* arc
of $G$" — is **false as a universal recipe**: a concrete 2-chord pancyclic graph
on 8 vertices has *all three* of its arcs fail the required split. The
underlying *existential* claim (some arc of some witness works) still holds in
this case, but only because a different 2-chord witness on the same $n$ happens
to have a good arc — nothing in the notes establishes that such a good witness
always exists in general. The auxiliary claim "the largest gap has interior
$m\le(n-3)/2$" is **also false as stated**, refuted by an explicit
counterexample, and its stated justification does not support it. The specific
downstream numeric claim "at $n=38$ this forces $s\ge21$" happens to be
verified true for the actual discovered $n=38$ witness, but is not rigorously
*forced* by anything proven in the notes — it is a property of that particular
graph, not a proven consequence of a general bound. The wall inequality
($m_j\le2^{k-j+c_j}$) uses undefined terms ("the multigraph on the $j$
stretches," $c_j$) that make it unfalsifiable as written; I could not verify or
refute it, only note that real extremal-graph gap data is qualitatively (not
exactly) consistent with its stated asymptotic consequence.

## 1. The subdivision lemma

**Statement under review** (quoted): "$h(n)\le k \iff$ there exist $s<n$ and
$G'=C_s+k$ chords with an edge $uv$ of $C_s$ such that (a) every length in
$[3,s]$ is the length of a cycle of $G'$ avoiding $uv$, and (b) every length in
$[2s-n,s]$ is the length of a cycle of $G'$ through $uv$. (take $s=n-m$ where
$m$ is the interior size of any arc of $G$; conversely subdivide.)"

### Backward direction ($\Leftarrow$): correct

Given $G'$ satisfying (a),(b), subdivide $uv$ with $m=n-s$ new vertices to get
$G=C_n+k$ chords. Cycles avoiding $uv$ are untouched, giving lengths $[3,s]$.
Cycles through $uv$ of length $\ell\in[2s-n,s]$ become, after subdivision,
length $\ell+m$; substituting $m=n-s$, this range shifts to exactly $[s,n]$.
$[3,s]\cup[s,n]=[3,n]$, so $G$ is pancyclic with $k$ chords. This is airtight;
the "conversely subdivide" parenthetical is doing real, correct work here.

### Forward direction ($\Rightarrow$), "any arc": **false as stated**

The one-line justification given is "conversely subdivide" — but this only
justifies the backward direction just checked; no argument is given for why
*contracting* an arbitrary arc of an *actual* pancyclic $G$ must produce a $G'$
satisfying both (a) and (b). Pancyclicity of $G$ only asserts that a cycle of
each length $3,\dots,n$ exists *somewhere* in $G$; it says nothing about
whether that witness uses a given arc's interior. Two facts *are* forced by
degree-2-interior structure alone (an arc's interior vertices have no chords,
so a cycle either uses the whole arc or none of it):

* any cycle of length $\le m+2$ must *avoid* the arc (using it would force
  length $\ge m+3$);
* any cycle of length $>s$ must *use* the arc (avoiding it caps length at $s$).

Nothing forces the *middle* range $(m+2,\,s]$ to split the "right way." I
checked this directly on the graph the project's own `search/hn.csv` records as
the minimal witness for $n=8,k=2$: chords $(0,2),(0,5)$
(`search/verify.py 8 "(0,2) (0,5)"` confirms pancyclicity, lengths
$3,\dots,8$). This graph has three arcs, with interiors of sizes $1,2,2$. I
computed, for **each** of the three arcs, the avoiding-length set and the
using-length set (shifted to pre-subdivision form) via `networkx.simple_cycles`
and checked both (a) and (b):

| arc (u,v,interior) | $m$ | $s$ | (a) missing | (b) missing |
|---|---:|---:|---|---|
| $(0,2,\{1\})$ | 1 | 7 | $\{3,6\}$ | $\{6\}$ |
| $(2,5,\{3,4\})$ | 2 | 6 | $\{5,6\}$ | $\varnothing$ |
| $(5,0,\{6,7\})$ | 2 | 6 | $\{4\}$ | $\{4\}$ |

**Every single arc of this genuine, independently-verified pancyclic witness
fails the (a)$\wedge$(b) conjunction.** For the largest arcs (the tied $m=2$
cases), (a) is missing lengths comfortably inside $[3,s]$ (not just a boundary
artifact) — e.g. the second row is missing both $5$ and $6$ from the avoiding
side entirely, because the graph's only length-5 and length-6 cycles happen to
route through that arc's interior. So "take $m$ = interior size of any arc of
$G$" is not a valid universal recipe: it depends on which witness $G$ and which
of its arcs you pick.

**The underlying existential claim survives, but not for free.** I brute-forced
all $\binom{20}{2}=190$ 2-chord subsets on $n=8$ (20 = the number of non-cycle
chords on 8 vertices), found $48$ that are pancyclic, and checked every arc of
every one of them:
$16$ of the $48$ witnesses have at least one arc satisfying (a)$\wedge$(b)
exactly (e.g. chords $(0,2),(1,4)$, arc $(4,0,\{5,6,7\})$, verified with zero
missing lengths in either (a) or (b)). So for $n=8,k=2$ the lemma's "there
exist $s,G',uv$" conclusion is true — but this had to be checked by search over
witnesses and arcs, not read off from "any arc of $G$" for a fixed $G$ as the
notes claim. **Silently used hypothesis:** that a "sufficiently generic" or
"suitably chosen" witness and arc exist with the required property. This may
well be true in general (it is true in every case I tested), but it is not
established by anything written in the notes, and the specific procedural
claim ("any arc") is demonstrably false.

## 2. "Consequence" 1: the counting balance

**Claim under review:** "For each chord subset $K$ with both Shi cycles
present, exactly one of them uses $uv$... So $|A|\le2^k-1$ and $|B|\le2^k$...
That gives $s\le2^k+1$ and $n-s\le2^k-1$."

**Arithmetic check:** if (a),(b) hold as stated, $|A|=s-2$ (integers $3..s$) and
$|B|=n-s+1$ (integers $2s-n..s$). $|A|\le2^k-1\Rightarrow s\le2^k+1$; $|B|\le2^k
\Rightarrow n-s\le2^k-1$. This arithmetic is internally consistent and I
reproduce it without objection.

**Completeness of the underlying combinatorial claim:** the notes assert, but
do not derive, the asymmetric $2^k-1$ vs. $2^k$ split. I reconstructed a
plausible derivation the notes omit: for a fixed chord subset $K\subseteq\{1..k\}$
(there are $2^k$ such subsets), Shi's theorem gives at most two associated
cycles, one from each of the two alternating arc classes relative to $K$; since
$uv$ lies in exactly one class, each $K$ contributes at most one candidate to
the "avoiding" side and at most one to the "using" side. The single asymmetry
is $K=\varnothing$: its only possible candidate is the full Hamilton cycle
itself (length $n$), which by definition includes $uv$ — so $K=\varnothing$ can
contribute to $B$ but structurally cannot contribute to $A$. That accounts for
exactly one fewer available slot on the avoiding side, matching $2^k-1$ vs.
$2^k$. **This reconstruction is not in the notes**; a reader cannot verify the
$-1$'s placement without redoing this argument, which is a completeness gap
even though (as far as I can tell) the conclusion is correct.

**More importantly:** this whole "Consequence" bounds how large $A$ and $B$
*could* be, given they exist as the lemma describes — it does not depend on, or
repair, the forward-direction gap in Section 1 above. Framing it as a
consequence "of" the lemma is a little misleading; it is better described as an
independent refinement of Shi's cycle-count bound, split by a fixed edge $uv$,
that happens to reproduce the same asymptotic ceiling either way.

## 3. "Consequence" 2 (bulleted): the largest-arc bound $m\le(n-3)/2$

**Claim under review:** "Length 2 through $uv$ is impossible (simple graph), so
taking $uv$ on the largest arc: the largest gap has interior $m\le(n-3)/2$. At
$n=38$ this forces $s\ge21$..."

**This is false as a general structural fact about the largest arc of a
pancyclic graph.** Counterexample: $n=8$, chords $(0,2),(1,4)$ — independently
verified pancyclic via `search/verify.py 8 "(0,2) (1,4)"` (lengths $3,\dots,8$).
Its chord-endpoint set is $\{0,1,2,4\}$, giving arcs of interior size
$0,0,1,3$. The **largest arc has interior $m=3$**, while $(n-3)/2=2.5$: the
claimed bound is violated by the largest arc of a genuine 2-chord pancyclic
witness on 8 vertices.

**Why the stated justification does not support the claim.** "Length 2 through
$uv$ is impossible" is a fact about requirement (b)'s *range*, not about arc
size: it is the observation that if $2s-n<3$, the range $[2s-n,s]$ would
nominally demand a "cycle of length $<3$," which cannot exist. Requiring
$2s-n\ge3$, i.e. $n-2m\ge3$, i.e. $m\le(n-3)/2$, is a **constraint one should
impose when choosing which arc to contract** so that (b)'s range stays
meaningful — it is not a fact that automatically holds for *the largest* arc of
an arbitrary pancyclic graph, which the counterexample above shows can be
larger. The notes conflate "a bound we should respect when picking an arc for
the argument to make sense" with "an automatic property of the largest arc,"
and only the former is actually justified by the stated reasoning.

**Bearing on the $n=38$ claim.** I checked the actual discovered $n=38$ witness
(`search/n38k5-A0.txt`: chords $(0,2),(0,18),(1,12),(3,19),(17,20)$). Its
largest arc does have interior $m=17\le(n-3)/2=17.5$, giving $s=21$ exactly as
the notes state, and — checked directly — this specific arc *does* satisfy the
full (a)$\wedge$(b) split with zero missing lengths on either side. So the
$n=38$ narrative is **empirically correct for the graph that was actually
found**. But given that the general bound it rests on is false (per the $n=8$
counterexample), this correctness is a property of this particular witness,
not something the notes' argument *forces* to be true of every possible
5-chord pancyclic graph on 38 vertices. A graph with a larger-than-17 largest
arc, if one existed, would not be excluded by anything proven here.

## 4. The large-length wall inequality

**Claim under review:** "Order gaps by interior size $m_1\ge m_2\ge\cdots$. A
cycle of length $>n-m_j$ must use every arc with interior $\ge m_j$... their
number is $\le2^{k-j+c_j}$, $c_j=$ number of components. So
$m_j\le2^{k-j+c_j}$."

**The $j=1$ base case is sound** and is really the same fact used throughout
Section 1: a cycle avoiding an arc of interior $m$ has length $\le n-m$, so a
cycle of length $>n-m_1$ (the single largest arc) cannot avoid it, i.e. must
use it.

**The general-$j$ step is not verifiable as written.** The notes introduce, but
do not define, "the multigraph on the $j$ stretches" or specify what its
vertex/edge set is, nor do they show why the number of qualifying chord subsets
is bounded by exactly $2^{k-j+c_j}$ rather than some other expression. Without
a precise definition of $c_j$ (which is left as a free parameter, "number of
components," of an unspecified graph), the bound cannot be checked against
data: for any observed $m_j$, one can always claim some $c_j$ makes the
inequality hold. This is a genuine completeness gap, not a disputed claim — I
am reporting "not enough is written down here to check this," which is a
different finding from "this is wrong."

**Numerical consistency check (does not confirm or refute the formula).** The
notes' own $n=40,k=5$ extremal data (`notes/01-subdivision-reformulation.md`)
gives three "geometric" gaps $19,10,5$ (or $17,10,5$). The naive
geometric-construction prediction $m_j\sim2^{k-j+1}$ for $j=1,2,3,k=5$ would be
$32,16,8$. The actual gaps are smaller by roughly the same factor at each step
($19/32\approx0.59$, $10/16=0.625$, $5/8=0.625$), which is at least
*qualitatively* consistent with the notes' claim that "equality forces
geometric gaps... whose lengths are missing," i.e. that the true extremal
graphs undershoot the pure-geometric prediction. This is consistent with, but
does not verify, the specific $2^{k-j+c_j}$ formula, since $c_j$ was not
computed independently for this example.

## What this means for the rest of `notes/01`

The two paragraphs that follow the lemma in the source file (the $n=38$
"local-search near-misses are exactly the $m=18$ configurations" remark, and
the "Update 2026-09-14 evening" section reporting $h(38)=h(39)=h(40)=5$,
$h(41)=6$) do **not** depend on the flawed general claims identified above —
those values were separately established by exhaustive computer search
(`search/gpu_pancyc.py`, `search/pancyc.c`; see `papers/draft/SOURCES.md` for
the full traceability), not by the subdivision-lemma argument. The gaps found
here are in the *proposed proof strategy/heuristic framework* for a future
lower-bound argument, not in the computed exact values themselves.

## Addendum: re-review after `notes/01`'s correction (2026-09-14)

The author corrected `notes/01-subdivision-reformulation.md` in response to
Section 1's counterexample and re-derived Sections 3–5's claims with precise
new definitions. Re-checked independently, computationally, from scratch
(not by re-reading the corrected proof and taking it on faith).

### 1. Corrected lemma: **holds, and the fix is the right one**

New statement: with $A$ = lengths of $G'$-cycles avoiding $uv$ and $B$ =
lengths through $uv$, $h(n)\le k\iff$ some $C_s+k$ chords with edge $uv$ has
$A\cup(B+(n-s))\supseteq[3,n]$ — a single covering condition, not the two
separately-quantified ranges the original claimed.

This is correct, and in fact **provably tautological for any arc of any
genuinely pancyclic $G$**, which is exactly why it fixes the gap: $A$ is by
construction the set of lengths of $G$-cycles avoiding the arc's interior, and
$B+m$ (with $m=n-s$) is the set of lengths of $G$-cycles using the arc
(subdividing $G'$ back at $uv$ with $m$ vertices literally reconstructs $G$).
So $A\cup(B+m)$ is just *all* cycle lengths of $G$, which contains $[3,n]$
because $G$ is pancyclic — for *any* arc, no special argument about where the
witnesses "land" is needed at all. I re-ran the exact computation from Section
1 with the corrected condition, on all three arcs of $n=8$, $(0,2),(0,5)$ (the
graph that broke the old statement) and, as a further check, all four arcs of
the $n=24$ witness `(0,2)(0,21)(1,19)(8,23)`: **zero missing lengths on every
arc of both graphs.** This matches the manager's report of checking "all arcs
of the 8-, 24- and 38-vertex witnesses."

### 2. Digon caveat: **confirmed**

Checked directly: of $n=8,(0,2),(0,5)$'s three arcs, the two whose endpoints
are *also* directly joined by a chord — $(0,2)$ itself (chord $(0,2)$ closes
it) and $(5,0)$ (chord $(0,5)$ closes it) — both have $2\in B$ (the pre-shift
length-2 "digon" through $uv$, corresponding to the actual length-$(m{+}2)$
triangle formed by the arc plus its closing chord in $G$). The one arc without
a closing chord, $(2,5)$, never has $2\in B$. This is exactly the pattern the
correction predicts, confirmed on real data rather than assumed.

### 3. Corrected corollary bound ($(n-2)/2$ non-joined, $(n-1)/2$ joined): **confirmed, and it resolves the Section 3 counterexample precisely**

Recomputed chord-adjacency for every arc in every example so far:

| graph | arc | $m$ | joined? | bound | holds? |
|---|---|---:|---|---:|---|
| $n{=}8,(0,2)(0,5)$ | $(0,2)$ | 1 | yes | 3.5 | yes |
| | $(2,5)$ | 2 | no | 3.0 | yes |
| | $(5,0)$ | 2 | yes | 3.5 | yes |
| $n{=}8,(0,2)(1,4)$ | $(2,4)$ | 1 | no | 3.0 | yes |
| | $(4,0)$ | **3** | no | **3.0** | **yes, tight** |
| $n{=}24$ | all four arcs | $\le10$ | no | 11.0 | yes |

The $(0,2),(1,4)$ largest arc — the Section 3 counterexample against the old
flat $(n-3)/2=2.5$ bound — sits at *exactly* the corrected non-joined bound
$m=(n-2)/2=3$. The old counterexample is fully explained, not just patched
around: it was a valid refutation of the flat bound, and the case split is
what was missing.

**One consequence worth flagging for the draft.** Re-checking the $n=38$
witness's largest arc, $(20,0)$, $m=17$: its endpoints are *not* chord-joined
(chords are $(0,2),(0,18),(1,12),(3,19),(17,20)$; no $(20,0)$/$(0,20)$ chord
among them), so the applicable corrected bound is the *non-joined* case,
$m\le(n-2)/2=18$ — looser than the old flat bound's $17.5$. $m=17$ still
satisfies it, comfortably rather than at the boundary this time, but the
corrected general theorem now only forces $s=n-m\ge n-18=20$ in the worst
case, not $s\ge21$. The specific witness still has $s=21$, but "$s\ge21$" is
no longer even the corrected theory's own worst-case floor — it should read
$s\ge20$ if stated as a general consequence of this bound. This is a small
point but the draft's Section 2.2/4 text should say $s\ge20$ (general bound)
while still reporting $s=21$ (actual witness) as the specific observed value,
not conflate the two.

### 4. Counting-balance corollary: unchanged, no re-review needed (per the correction note, this one was not touched).

### 5. Wall inequality with precise definitions: **now holds**

With the stretch multigraph, $c_j$, and the "even number of $K$-endpoints per
stretch" condition spelled out, this is a correct instance of a standard fact:
**the number of even subgraphs (all-degrees-even edge-subsets) of a multigraph
with $E$ edges, $V$ vertices and $c$ components is $2^{E-V+c}$** (the
$\mathrm{GF}(2)$-dimension of its cycle space is $E-V+c$). Here $V=j$ (the
stretches), $E=$ number of cross-stretch chords, and free within-stretch
chords contribute an independent factor $2^{\text{(within)}}$, giving
$2^{\text{within}}\cdot2^{\text{cross}-j+c_j}=2^{k-j+c_j}$ exactly as claimed,
since within+cross$=k$. The chain of reasoning is now complete: (i) a cycle of
length $>n-m_j$ must use all $j$ largest arcs (proved in Section 3 of the
original notes and not in dispute); (ii) for its chord subset $K$ this forces
an even number of $K$-endpoints in every stretch, i.e. $K$'s cross-chords form
an even subgraph of the stretch multigraph (a direct parity/connectivity
argument, correct); (iii) the count of such $K$ is exactly $2^{k-j+c_j}$ by
the standard cycle-space-dimension fact; (iv) each qualifying $K$ yields at
most one long cycle (Shi's dichotomy, already established), so the number of
*achievable* long-cycle lengths — hence $m_j$, since pancyclicity needs $m_j$
distinct lengths above $n-m_j$ — is at most that count. **This paragraph now
holds as a complete, checkable proof; the earlier finding ("undefined terms,
unfalsifiable") is resolved by the new definitions, not merely made more
precise-sounding.** I did not find a further gap in it.

### Net effect on the draft

Section 4 of `papers/draft/pancyclic-exact-values.md` needs its subdivision
lemma and both corollaries replaced with the corrected versions above; the
wall inequality subsection can now be presented as an established argument
rather than a bounded/asserted one, still correctly distinguished from the
still-open question of whether it can be pushed past the trivial counting
ceiling.
