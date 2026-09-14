# A105206 extension draft (NOT for submission — draft only, authorship not decided)

Date: 2026-09-14. This is a draft for review, to decide whether/how
to submit to OEIS; nothing here has been or will be sent to OEIS by this process.

## 1. Indexing reconciliation

The current OEIS entry for A105206 (fetched directly, see `REPORT-lit-4.md` for the
fetch method and full raw content) has:

* **NAME**: "Number of edges in a pancyclic graph on n+2 vertices with the fewest
  possible edges."
* **OFFSET**: `3,1`
* **DATA**: `3, 5, 6, 8, 9, 10, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25, 26`
  (20 terms, so index n runs 3..22)
* **EXAMPLE**: "For n = 3 the answer is 3; each of the three vertices is connected to
  each other vertex, forming a 3-cycle. For n = 4 we find it takes five edges and for
  n = 5 it takes 6."

These two parts of the same entry are mutually inconsistent. If NAME is taken
literally, `a(n) = m(n+2)`, so `a(3)` should be `m(5)`. But `m(5)` cannot be 3 (a
pancyclic graph on 5 vertices needs a Hamiltonian cycle, i.e. at least 5 edges), and
EXAMPLE explicitly describes `a(3)=3` as "each of the three vertices... forming a
3-cycle" — a 3-vertex graph, not a 5-vertex one. EXAMPLE is therefore using `n` to mean
the vertex count directly, contradicting NAME's own "+2" offset.

**Direct check against Griffin's Table 1** (arXiv:1312.0274, transcribed verbatim from
the locally saved `1312.0274.txt`, which lists `n, k, m(n)` for `n=3..37`) settles the
question. Testing the literal reading `a(index) = m(index)` (i.e. index equals vertex
count, matching EXAMPLE, not NAME) against all 20 published OEIS terms:

| index (=n) | OEIS a(n) | Griffin m(n) | match? |
|---|---|---|---|
| 3 | 3 | 3 | yes |
| 4 | 5 | 5 | yes |
| 5 | 6 | 6 | yes |
| 6 | 8 | 8 | yes |
| 7 | 9 | 9 | yes |
| 8 | 10 | 10 | yes |
| 9 | 12 | 12 | yes |
| 10 | 13 | 13 | yes |
| 11 | 14 | 14 | yes |
| 12 | 15 | 15 | yes |
| 13 | 16 | 16 | yes |
| 14 | 17 | 17 | yes |
| 15 | 19 | 19 | yes |
| 16 | 20 | 20 | yes |
| 17 | 21 | 21 | yes |
| 18 | 22 | 22 | yes |
| 19 | 23 | 23 | yes |
| 20 | 24 | 24 | yes |
| 21 | 25 | 25 | yes |
| 22 | 26 | 26 | yes |

All 20 published terms match `m(n)` at index = n exactly, with zero disagreement, and
zero terms match the `m(n+2)` reading (which is not even dimensionally possible for
`a(3)`, as shown above). **Conclusion: the published DATA and EXAMPLE are correct and
internally consistent with each other and with Griffin's independently-published exact
table; the defect is confined to the NAME field's "+2" phrase, which should read "on n
vertices" rather than "on n+2 vertices."** This is not a numeric disagreement anywhere
in the published values — it is a text/indexing-description error in the NAME line
only. No published term needs to change; only the description needs correcting, and
even that correction is left to the OEIS editors, not asserted here as fact
beyond what the arithmetic above shows.

## 2. Corrected/extended term list through n=41

Using the reconciled indexing (`a(n) = m(n)`, offset 3), the sequence extends past the
current published `a(22)=26` using three sources, marked by provenance:

* `n=3..22`: **already published** OEIS values (verified above).
* `n=23..37`: **published in Griffin (2013), arXiv:1312.0274, Table 1**, but not yet
  entered into OEIS.
* `n=38..41`: **this project's new values**, not published anywhere else located in
  this literature sweep (see `REPORT-lit-1.md`, `REPORT-lit-2.md`, `REPORT-lit-4.md`),
  derived from `h(38)=h(39)=h(40)=5` and `h(41)=6`, i.e. `m(n)=n+h(n)`.

Proposed OEIS-format DATA line (comma-separated, matching current style), full
`n=3..41`:

```
3, 5, 6, 8, 9, 10, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 30,
31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 47
```

(39 terms, index 3..41. The first 20 are the existing published terms unchanged; terms
21-35, i.e. `n=23..37` = `27, 28, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42`,
are Griffin's published table entered for the first time; the last 4 terms, `n=38..41`
= `43, 44, 45, 47`, are this project's new values.)

## 3. Proposed b-file (`b105206.txt`, OEIS two-column format)

```
3 3
4 5
5 6
6 8
7 9
8 10
9 12
10 13
11 14
12 15
13 16
14 17
15 19
16 20
17 21
18 22
19 23
20 24
21 25
22 26
23 27
24 28
25 30
26 31
27 32
28 33
29 34
30 35
31 36
32 37
33 38
34 39
35 40
36 41
37 42
38 43
39 44
40 45
41 47
```

## 4. Proposed COMMENT lines

* "a(n) is the minimum number of edges of a pancyclic graph on n vertices; equivalently
  a(n) = n + h(n) where h(n) is as in Erdős problem #1016 (Bondy, 1971)."
* "The NAME as originally published read 'on n+2 vertices'; this appears to be an
  indexing description error — the published DATA and EXAMPLE both use n as the direct
  vertex count, and every published term through a(22) matches Sean Griffin's
  independently published exact table m(n) at index n, not at index n+2."
* "a(23) through a(37) are Sean Griffin's exact values (arXiv:1312.0274, Table 1),
  which agree with the earlier unpublished computation of George, Marr and Wallis
  cited therein; a(38) through a(41) extend the table further."

## 5. Proposed REFERENCES

* J. A. Bondy, "Pancyclic graphs I," Journal of Combinatorial Theory, Series B, 11
  (1971), 80–84, doi:10.1016/0095-8956(71)90016-5.
* J. C. George, Alison Marr, W. D. Wallis, "Minimal Pancyclic Graphs," Journal of
  Combinatorial Mathematics and Combinatorial Computing 86 (2013), 125–133.
* Sean Griffin, "Minimal Pancyclicity," arXiv:1312.0274 [math.CO], 2013.
* J. C. George, Abdollah Khodkar, W. D. Wallis, *Pancyclic and Bipancyclic Graphs*,
  Springer, 2016, Chapter 4.5.
* [This project, attribution not decided], values of m(n) for n=38..41 computed
  by exhaustive/GPU-assisted chord search; see `search/pancyc.c` (exhaustive
  triangle-case-split search for graphs with up to 5 chords) and `search/gpu_pancyc.py`
  (GPU colex-unranking search over 5- and 6-chord combinations for n=38..41), both in
  this project's repository, independently verified against a from-scratch Python
  cycle-space checker (`papers/construction/check.py`) as recorded in
  `REVIEW-search.md`.

## 6. Proposed LINK line

* Thomas Bloom, "Problem 1016," Erdős Problems, https://www.erdosproblems.com/1016
  (already present on the current OEIS entry; no change needed).

## 7. Authorship / submission note

This file is a draft prepared for review. It does not assert who
should be listed as the submitting/extending author on OEIS — that is still
to be decided. No submission has been made or attempted.
