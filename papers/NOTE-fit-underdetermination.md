# The threshold data does not determine t_6

Derived by Manager (f4d1e0af), 2026-09-14. Input to the Section 5 rewrite.
Not yet merged into `papers/draft/pancyclic-exact-values.md`.

## Statement

Section 5 presents `t_k = 2*Fib(k+3)-2` (exact at k=2..5, predicting t_6=66) as
an observation worth testing. `papers/PLAN-next-steps.md` adds a second fit,
`t_k = 2^(k-2)*(10-k)`, exact at the same four points and predicting t_6=64.
Neither is special. Consider every three-term linear recurrence

    t_k = a*t_(k-1) + b*t_(k-2) + c        (a,b,c integers)

consistent with t_2..t_5 = 8, 14, 24, 40. The two fitting constraints are

    14a +  8b + c = 24
    24a + 14b + c = 40

whose difference is 5a + 3b = 8. The integer solutions form a one-parameter
family (a,b,c) = (1+3t, 1-5t, 2-2t), each of which reproduces 8,14,24,40
exactly and predicts

    t_6 = 66 - 2t.

So **every even value of t_6 is predicted by some integer linear recurrence that
matches all four known values.** The Fibonacci form is t=0; the rival form of
PLAN-next-steps is t=1. They are not competing hypotheses so much as two
arbitrary members of an unconstrained family.

## Consequence for the note

The four known values constrain t_6 **not at all** within this family, so no
amount of pattern-fitting on t_2..t_5 carries information about t_6. Only
computation decides it. Section 5 should say this rather than presenting one
fit and a falsifiable-looking prediction; the honest content is the
underdetermination, which is a sharper observation than either fit.

Caveat, stated precisely: "every even value" is a property of THIS family
(three-term, integer coefficients). It is not a theorem that t_6 must be even.
Families with rational coefficients, more terms, or non-linear form can predict
odd values. The claim is that the data fails to select among simple fits, not
that t_6 is constrained to parity.

## What the computation has already excluded

Confirmed 6-chord witnesses at n=61, 62 and 64 (`search/k6/witnesses-v2.csv`,
each re-verified with `search/verify.py`) give t_6 >= 64. That already refutes
the members predicting 58, 60 and 62 — pattern-fitting was not needed, and the
search has outrun the numerology.

A witness at n=65 would be sharper than either named fit anticipates: 65 is odd,
so it would refute EVERY member of the integer family above simultaneously,
including both the Fibonacci and the rival forms.

Current status: t_6 >= 64 confirmed; `search/k6/` GPU joint-neighbourhood sweeps
running at n=66, then 65B/65C, then 67; `search/shapecsp/` deciding the matching
upper bound independently.
