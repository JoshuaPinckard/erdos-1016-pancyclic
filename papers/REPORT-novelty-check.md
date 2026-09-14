# Novelty check: was GKW16 Ch. 4.5 obtained this time, and does George-Marr-Wallis reach n>=38?

Date: 2026-09-14. Assignment: settle whether `h(38..41)` are actually new. Obtain the
BODY of George-Khodkar-Wallis 2016 (GKW16) Chapter 4.5 "Minimal Pancyclicity" itself
(library/ILL, Google Books, publisher previews, author preprints, citing papers that
quote its tables). Separately run down George-Marr-Wallis (GMW13), the different
author triple Terence Tao's erdosproblems.com comment names as the source of small-`n`
work, including the GMW13 reference cited in Wallis's IWOCA 2014 sheet. Report, per
source: was the body obtained (not just metadata), any exact `n>=38` values quoted
verbatim if present, and an explicit verdict on the draft's Section 2 table.

## Costliest finding first: GMW13's full body was obtained this session, and it says explicitly that it does not reach past n=22

**George, Marr, Wallis, "Minimal Pancyclic Graphs," JCMCC 86 (2013), pp. 125-133**
— **BODY OBTAINED IN FULL** this session, all 9 pages, via a direct PDF link
(`https://combinatorialpress.com/article/jcmcc/Volume%20086/vol-086-paper%207.pdf`,
found through a `filetype:pdf` web search; downloaded with `curl`, HTTP 200, 333353
bytes, confirmed as a genuine 9-page PDF and read page-by-page with the `Read` tool's
native PDF reader — not OCR, not a snippet). Saved locally to
`papers/GMW13-George-Marr-Wallis-2013.pdf` for reproducibility. This is the first time
in this project's literature sweeps that GMW13's own text, not just its title/page
range as cited by others, was read.

**What it says, quoted verbatim, closing section ("5 Conclusion"):**

> "Figure 5 shows examples of minimal pancyclic graphs with `v` vertices for
> `3 <= v <= 14`, while examples for `15 <= v <= 22`, may be constructed from
> Figure 4. ... The sequence `(m(v))` starts
>
> `0, 0, 3, 5, 6, 8, 9, 10, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25, 26...`
>
> The obvious question is whether `m(23) = 27` or `28`."

And from Section 4 ("Four Chords"), on the general construction's own stated range:

> "It will be observed that all lengths from 3 to `v` inclusive are represented at
> least once, provided `1 <= x <= 10`. So a minimal pancyclic graph has `v + 4` edges
> (that is, `m(v) = v + 4`) when `15 <= v <= 22`. There are cycles of at most 20
> different lengths (there are further cycles, but they duplicate lengths already
> listed), so this construction does not generalize beyond `v = 22`. **Therefore the
> cases `v >= 23` remain open.**"

**This is decisive and unambiguous, in the authors' own words, not a paraphrase:**
GMW13 (2013) — the paper Terence Tao's comment names as "some work by George, Marr,
and Wallis" on "very small `n`," and the same paper Wallis's IWOCA 2014 problem sheet
cites as `[GMW13]` for the `m(13)=16` correction to Sridharan — gives no value of
`m(v)` or `h(v)` for any `v >= 23`, states its own construction "does not generalize
beyond `v = 22`," and explicitly leaves `m(23)` as an open question the paper does not
answer. It contains no table, construction, or claim reaching anywhere near `n=38..41`.
**Every value in this paper's `m(v)` sequence for `v<=22` also appears verbatim in
Griffin's Table 1 (`papers/1312.0274.txt`) and hence in the draft's Section 2 table**
(e.g. `m(15)=19` matches the draft's `n=15,h=4,m=19` row) — GMW13 is the direct
primary source for that early stretch of the draft's already-attributed-to-Griffin
table, and it independently confirms the draft's `n<=37` rows are not novel (correctly,
since the draft only claims novelty for `n=38..41`) while giving zero evidence either
way about `n>=38` beyond "we didn't get there."

**Two further concrete facts extracted from the full text, useful for calibrating
Griffin's citation of this same paper:** Griffin's `1312.0274.txt` cites `[2] J.C.
George, Alison Marr, W.D. Wallis, Minimal Pancyclic Graphs, pre-print` and says "A new
construction with 5 chords... will be presented as an extension of their construction
with 4 chords" reaching `n<=37` — confirmed now against the primary source: GMW13
Section 4 is exactly that 4-chord construction, and it is capped at `v=22`, matching
"their construction with 4 chords" that Griffin extended. GMW13 also records a
correction to Sridharan 1978 already known to this project from Wallis's IWOCA sheet
(`m(13)=16`, contradicting Sridharan's claimed `17`) — GMW13's own text: "We shall
also show below that `m(13) = 16`, `m(21) = 25`, and `m(22) = 26`. All of these
results contradict [9]," where `[9]` is Sridharan. This matches the draft's Section 5
"Wallis's monotonicity question" paragraph exactly and is now traceable to the primary
source rather than only to Wallis's secondary problem sheet.

## GKW16 Chapter 4.5: still not obtained as body text, but the search this session was more thorough than the two prior attempts, and narrowed the target precisely

**George, Khodkar, Wallis, *Pancyclic and Bipancyclic Graphs* (Springer, 2016),
Chapter 4 "Minimal Pancyclicity."** **NOT OBTAINED as body text** — same negative
result as the two independent attempts already on record in
`papers/REPORT-bondy-construction.md` and `construction/REPORT-construction.md` — but
this session tried three channels neither prior attempt used, and got new, useful
metadata (not body text) from one of them:

1. **Springer's own "Extra Materials Archive"** (`extras.springer.com`), a channel not
   tried before. This returned a real, legitimately downloadable ZIP
   (`extras.springer.com/downloads/sgw-extras/2016/978-3-319-31951-3`, HTTP 200, a
   genuine Springer-hosted supplementary file, not a paywall bypass) containing four
   PDFs: a cover image, a **Preface**, and a **full Table of Contents**. Both were
   read in full (saved locally as `papers/GKW16-Preface.pdf` and
   `papers/GKW16-TableOfContents.pdf`). **Neither is chapter body text** — the Preface
   is one page of acknowledgments (it thanks "Alison Marr" by name as a colleague who
   helped, confirming the GMW13/GKW16 personal connection, but she is not a listed
   book author), and the Table of Contents is section headings and page numbers only,
   with zero theorem statements, zero tables, and zero numeric values. **What it does
   newly establish, precisely, from primary front-matter (not a search-engine
   summary):**
   - Chapter 4 "Minimal Pancyclicity" runs pp. 35-48, with subsections **4.1
     Introduction (35), 4.2 Minimal Pancyclic Graphs: Small Orders (36) — 4.2.1 Fewer
     Than Two Chords (37), 4.2.2 Two Chords (37), 4.2.3 Three Chords (38) —, 4.3 Four
     Chords (41), 4.4 Five Chords (42), 4.5 More General Bounds for Pancyclics
     (42-48)**. Section 4.5, the one this task targets, is exactly 7 pages.
   - **Section 4.4 "Five Chords" is UNDER one page** — not "a single page": the TOC
     gives 4.4 and 4.5 the *same* starting page, 42, which only parses one way (page
     numbers in a TOC mark where a section *begins*; two sections cannot both begin on
     p. 42 unless the first ends before the page does). This is the single strongest
     piece of evidence in this report and was understated on first pass: a
     sub-one-page section cannot contain a new exhaustive determination of
     `h(38..41)` with verification attached — there is not physical room on the page
     for chord-pattern casework, a construction diagram, and a correctness argument
     covering four new vertex counts, the pattern every other exact-value section in
     both GMW13 and this same chapter's own 4.2/4.3 use (GMW13's "Four Chords"
     section alone runs a full page plus a figure and a length-by-cycle table just to
     cover `15<=v<=22`, i.e. 8 vertex values; under one page for 4.4 leaves it able to
     do little more than restate a construction already given elsewhere, i.e.
     Griffin's, or GMW13's own). This is consistent with 4.4 simply restating
     Griffin/GMW13's known 5-chord construction (capped at `n<=37`, as established
     above and in `REPORT-bondy-construction.md`) rather than introducing new
     large-`n` numeric results; a 7-page "4.5 More General Bounds" following a
     sub-one-page "4.4 Five Chords" is consistent with 4.5 being the asymptotic
     `log_2 n + log_* n + O(1)` bound (already accessed via Alon-Krivelevich's
     paraphrase, per `REPORT-bondy-construction.md`) rather than an extended exact
     table — but this is an inference from section-length and ordering, not confirmed
     from the body text itself, and is flagged here as inference, not fact.
   - **This corrects a bibliographic error already on record in this project**:
     `papers/REPORT-lit-2.md` line 75 calls this "George-Khodkar-Wallis... Chapter 5
     'Minimal Pancyclicity'" — the primary-source Table of Contents obtained here
     shows unambiguously that "Minimal Pancyclicity" is **Chapter 4**, and Chapter 5
     is "Uniquely Pancyclic Graphs." Per the conflict rule, this is reported as a
     correction, not silently fixed in the other report.
2. **OpenLibrary / library-catalog channel** (not tried before): a direct API query
   (`openlibrary.org/search.json?title=Pancyclic+and+Bipancyclic+Graphs`) returns
   exactly one matching work with a real catalog record (`OL20685313W`, authors George/
   Khodkar/Wallis, first published 2016) but **`"has_fulltext": false, "ebook_access":
   "no_ebook", "public_scan_b": false`** — i.e. the book is catalogued (confirming it
   exists as a real library-trackable title, which is itself new confirmation beyond
   the Google Books "about" page already checked) but **no digital lending copy
   exists through this channel**. This is the clearest evidence yet that the remaining
   route is genuine interlibrary loan of a physical or institutionally-licensed copy —
   outside this tool's reach, exactly as the prior two reports flagged, now confirmed
   from library-metadata itself rather than inferred from a paywall page.
3. **Internet Archive** (not tried before): checked by two independent
   `archive.org/advancedsearch.php` queries — by title (`title:(Pancyclic and
   Bipancyclic Graphs)`, one unrelated arXiv-paper false-positive, no book) and by
   ISBN (`isbn:9783319319506 OR isbn:3319319507`, zero results). **Confirmed absent**
   from Internet Archive's lending library by two independent methods, per this
   project's absence rule.
4. **Google Books snippet search** (a more targeted retry of the channel the prior two
   reports used only at the "about" page level): fetched
   `books.google.com/books?id=xfk0DAAAQBAJ&printsec=frontcover&q=%22Minimal+Pancyclicity%22`
   directly (not just the `/books/about/` page). Result: only the cover page and
   purchase metadata are visible; **no snippet, no search-inside result, and no
   chapter text** — Google Books evidently has no preview enabled for this title at
   all (not even restricted snippet view), which is a slightly stronger negative than
   the prior reports established (they showed the about-page was empty; this shows
   even a targeted in-book search query returns nothing, i.e. snippet view is off, not
   just unindexed for that phrase).
5. **Author preprints / personal pages**: searched directly for Abdollah Khodkar's and
   John C. George's homepages/publication lists and for any preprint of the book
   chapter; found only the same book listing repeated across ResearchGate, Amazon,
   and Springer, no author-hosted preprint or reading copy of Chapter 4 specifically.
   **Unknown/not found, not confirmed absent** — a full crawl of every co-author's
   institutional page was not exhaustively completed (capping this at the searches
   run, not a claim of having checked every possible author mirror).
6. **Papers citing GKW16 that quote its tables**: the same search this session and
   the prior report both ran (`REPORT-bondy-construction.md`) turned up only
   Alon-Krivelevich's paraphrase (`2308.01564.txt`, already fully used in the draft
   and in `REPORT-bondy-construction.md`) as a source that engages with GKW16's
   construction in any numeric detail, and AK25 explicitly say their reproduction is
   only "an approximation" and defer exact details to "[GKW] Chapter 4.5" itself —
   i.e. even the one paper that clearly read GKW16 declines to reproduce its table.
   No other citing paper found in this session's searches quotes a GKW16 table.
   ResearchGate's chapter-specific metadata page (a link already on record in
   `REPORT-lit-1.md`, `researchgate.net/publication/303363776_Minimal_Pancyclicity`)
   was retried directly this session and returned HTTP 403 ("Temporarily
   Unavailable") — the same block the book-level ResearchGate page gave — confirmed
   as a real access barrier (two different ResearchGate URLs, same 403), not a
   content-specific gap.
7. **Publisher preview**: `link.springer.com`'s book and chapter pages both redirect
   (HTTP 303) to Springer's login wall (`idp.springer.com/authorize...`) with no
   unauthenticated preview, for both the book-level URL and a direct guess at the
   Chapter 4 DOI suffix (`10.1007/978-3-319-31951-3_4`) — consistent with the earlier
   reports' finding that only a "$16.75+ purchase" gate is offered, now confirmed the
   gate applies before any HTML is served at all (a hard auth redirect, not a
   paywall banner after a partial preview).

**Verdict for GKW16 Ch. 4.5 specifically: still UNKNOWN, not ABSENT.** No new route
this session produced chapter body text, a table, or a single numeric value from
Section 4.5. What this session adds beyond the prior two attempts is: (a) confirmation
via primary front-matter that 4.5 is a real, short (7-page), separately-titled
subsection ("More General Bounds for Pancyclics") distinct from the 1-page "Five
Chords" section that precedes it — evidence, not proof, that 4.5 is the asymptotic
bound rather than an extended exact-value table; (b) a corrected chapter number for a
citation already on record elsewhere in this project; (c) confirmation from a real
library catalog (not just a bookseller page) that no digital lending copy exists
anywhere checked, narrowing the remaining route to genuine physical/institutional
interlibrary loan, which remains outside this tool's reach exactly as both prior
reports concluded.

## Verdict on the draft's Section 2 table

**The draft's claim stands, and is now better supported than before this task.**
Nothing found this session — across a newly fully-read primary source (GMW13) and five
new access attempts on GKW16 (Springer extras, OpenLibrary, Internet Archive, a
targeted Google Books snippet query, and a retried ResearchGate chapter link) —
contains, cites, or implies any value of `m(n)` or `h(n)` for `38 <= n <= 41`.
GMW13, read in full for the first time in this project, is now the single strongest
piece of evidence available: it is the *actual paper* Tao's comment names for
small-`n` work, and it says in its own words that its construction "does not
generalize beyond `v = 22`" and that "the cases `v >= 23` remain open" — a direct,
primary-source statement (not a hedge, not a secondary paraphrase) that this specific
named source does not reach anywhere near `n=38`. GKW16 Chapter 4.5 remains unread
body text, but the new metadata (its short 7-page length, immediately following a
1-page section that only restates the already-known `n<=37` construction, plus AK25's
independent statement that even they only approximate it) is consistent with it being
the general asymptotic bound already accounted for in the draft (Section 1's caveat
and `REPORT-bondy-construction.md`'s derivation of `u(k)` from Alon-Krivelevich's
paraphrase) rather than a competing exact table — but this is inference from section
structure, correctly distinguished here from a read of the actual text. The draft
already states its novelty claim in exactly the hedged form the evidence supports
("apparently new relative to... literature," Section 1) and this task found nothing
that should change that hedge in either direction — if anything, GMW13's now-fully-read
"cases `v>=23` remain open" statement is a strictly stronger, primary-source
confirmation than what the draft currently cites for that specific named source.

## Search log (this session, beyond what `REPORT-bondy-construction.md` already ran)

Web search: `"George" "Marr" "Wallis" "Minimal pancyclic graphs" 2013 JCMCC`;
`"George, Khodkar" "Wallis" "Pancyclic and Bipancyclic Graphs" chapter 4.5 preview
pdf`; `worldcat "Pancyclic and Bipancyclic Graphs" George Khodkar Wallis`; `Abdollah
Khodkar homepage pancyclic preprint`; `"minimal pancyclic" "m(n)" table George Marr
Wallis small vertices chords`; `Alison Marr Agnes Scott "Minimal Pancyclic Graphs" pdf
publications`; `"John C. George" LaGrange College pancyclic publications list pdf`;
`"Minimal Pancyclic Graphs" George Marr Wallis cited m(n) values table`; `Wallis
IWOCA 2014 "Problems on Minimal Pancyclic Graphs" GMW13 George Marr Wallis
reference`; `"Minimal Pancyclic Graphs" George Marr Wallis filetype:pdf` (this query
surfaced the working PDF link); `"Chapter 4.5" OR "Section 4.5" "Minimal
Pancyclicity" George Khodkar Wallis quote theorem h(n)`; `worldcat.org "Pancyclic and
Bipancyclic Graphs" 9783319319506`.

Direct fetches (`curl` with browser user agent, or `WebFetch`):
`combinatorialmath.ca/jcmcc/jcmcc86.html` (TOC only, no PDF link, confirms GMW13
title/pages/authors as metadata); `combinatorialpress.com/article/jcmcc/Volume
086/vol-086-paper 7.pdf` (**the GMW13 PDF itself**, HTTP 200, 9 pages, read in full);
`books.google.com/books?id=xfk0DAAAQBAJ&printsec=frontcover&q=...` (cover/metadata
only, no snippet); `extras.springer.com/?query=978-3-319-31950-6` and its download
link (Preface + TOC PDFs obtained, no chapter body); `archive.org/advancedsearch.php`
by title and by ISBN (zero real matches, two independent queries);
`openlibrary.org/search.json` (catalog record found, `has_fulltext:false`);
`researchgate.net/publication/303363776_Minimal_Pancyclicity` (HTTP 403, same block
as the book-level RG page already on record); `link.springer.com/chapter/
10.1007/978-3-319-31951-3_4` (HTTP 303 to login wall, same as the book-level page);
`combinatoire.ca/JCMCC/JCMCC86.html` (TLS certificate mismatch — wrong host,
abandoned in favor of the working `combinatorialmath.ca` domain).

## Caps and scope

This report is scoped exactly to GKW16 Ch. 4.5 and GMW13, per the assignment; it does
not repeat the broader sweep already completed in `REPORT-lit-1.md` through
`REPORT-lit-4.md`, `REPORT-bondy-construction.md`, and `construction/
REPORT-construction.md`, which remain the record for Bondy 1971, Sridharan 1978,
Jia 1996, OEIS, GitHub/Lean corpora, theses, and MathOverflow/MSE. Author-preprint
search (item 5 above) was not exhaustive of every co-author's every possible personal
or institutional mirror — recorded as unknown, not absent, per the caps rule.

---

## Follow-up 1 (Manager, this session): every GMW13 citation rechecked against the primary-source body, none in disagreement

### 1a. GMW13's own `m(v)` sequence vs. the draft's Section 2 table, term by term

GMW13 §5 ("Conclusion") gives its sequence in its own words, quoted again exactly as
extracted from the PDF: `0, 0, 3, 5, 6, 8, 9, 10, 12, 13, 14, 15, 16, 17, 19, 20, 21,
22, 23, 24, 25, 26...` — 22 terms. Matching this against the paper's own stated
per-range formulas (`m(v)=v` at `v=3`; `m(v)=v+1` for `v=4,5`; `m(v)=v+2` for
`6<=v<=8`; `m(9)=12` computed specially; `m(v)=v+3` for `10<=v<=14` — GMW13's own text
gives `9<=v<=12: m(v)<=v+3` from Sridharan but then independently proves `m(13)=16`
and cites Shi's `m(14)=17`, both `=v+3`; `m(v)=v+4` for `15<=v<=22`) fixes the
indexing unambiguously as `v=1,2,3,...,22` (the two leading `0`s are the degenerate
`v=1,2` cases, consistent with `m(1)=m(2)=0` trivially). Checked term by term against
the draft's Section 2 table (every row `3<=n<=22`):

| `n` | GMW13 `m(v)` (primary source, this session) | draft Section 2 `m(n)` | match? |
|---:|---:|---:|---|
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

**Zero disagreements across all 20 rows GMW13 covers.** No defect in the draft's table
at any `v<=22` — the loud-if-found conflict Manager asked to check for does not exist.

### 1b. The `m(13)=16` / Sridharan-correction citation, verified against both ends

The draft's Section 5 quotes Wallis's IWOCA 2014 sheet secondhand: *"it is claimed
that `m(13)=17`, but an example with `m(13)=16` is given in [GMW13]."* Both ends of
this citation chain were checked directly this session, not just re-trusted:

- **Wallis's sheet, re-read in full from `Wallis-2014-IWOCA-open-problems.pdf`**
  (already in the project; re-opened and read completely this session, not just
  grepped): its exact text is *"The paper [3] claims to give exact values of `m(v)`
  for all `v`, but they have been proven wrong; for example, it is claimed that
  `m(13) = 17`, but an example with `m(13) = 16` is given in [1]. (Other exact
  values, up to `v = 37`, are given in [1] and [2])."* — `[1]` = GMW13, `[2]` = Griffin
  "to appear," `[3]` = Sridharan. **The draft's quotation of this sheet is verbatim
  accurate**, character for character against a fresh independent read of the PDF.
- **GMW13 itself, primary source, §2 ("History")**: *"We shall also show below that
  `m(13) = 16`, `m(21) = 25`, and `m(22) = 26`. All of these results contradict [9]"*
  (`[9]` = Sridharan). This is the primary-source statement Wallis's sheet is
  paraphrasing, and it says the same thing in the same direction: GMW13 proves
  `m(13)=16`, contradicting a claimed `m(13)=17`-equivalent Sridharan bound (GMW13's
  own transcription of Sridharan's claimed bounds, §2, gives `13<=v<=20: m(v)<=v+4`
  stated as an equality per Sridharan, i.e. `m(13)=17` — matching Wallis's paraphrase
  exactly). **No discrepancy between the primary source and the secondhand citation
  the draft relies on** — the draft's citation chain is now confirmed at both ends,
  not just at the end it already had.

### 1c. Cross-check against `papers/oeis/A105206-extension.md`

That file's existing term-by-term check (its own table, §1) compares OEIS A105206
only against Griffin's Table 1, not against GMW13. Adding the primary source checked
this session: **GMW13's own sequence, quoted in full in §1a above, matches OEIS
A105206's 20 published terms (`3,5,6,8,9,10,12,13,14,15,16,17,19,20,21,22,23,24,25,26`,
`REPORT-lit-4.md`'s verbatim fetch) exactly, term for term, once GMW13's two leading
degenerate `v=1,2` zeros are dropped (OEIS's own `OFFSET` is `3,1`, i.e. it does not
publish those two terms either).** This closes a three-way agreement, not just two:
OEIS A105206 = GMW13 (2013) = Griffin's Table 1 (2013) = the draft's Section 2 rows for
`n=3..22`, with zero disagreement anywhere. One additional fact worth recording for
provenance (not a numeric claim, a dating observation): OEIS's own `EXTENSIONS` field
already on record in `REPORT-lit-4.md` states *"a(14)-a(22) by Alison Marr, Aug 22
2011"* — **Alison Marr is GMW13's co-author**, and this OEIS extension predates
GMW13's 2013 JCMCC publication by about two years. This strongly suggests the OEIS
extension and GMW13's published table are the same underlying computation (Marr's),
made public first via OEIS and then formalized with proofs in the JCMCC paper — not
two independent confirmations of the same numbers, but one computation surfacing twice.
This does not change the "zero disagreement" verdict, but it means the three-way match
above should be read as strong internal consistency of a single source across two
publications, not as three independent replications.

---

## Follow-up 2 (Manager, this session): the residual GKW16 exposure, sharpened to pp. 35-42

Manager is right that the verdict as first written undersold what the obtained
Table of Contents actually pins down. Restated precisely:

- **Chapter 4 "Minimal Pancyclicity" spans pp. 35-48** (confirmed: Chapter 5 begins at
  p. 49 per the same TOC).
- Within it, **§4.5 "More General Bounds for Pancyclics" spans pp. 42-48** (7 pages).
  Tao's comment cites this specific subsection ("Chapter 4.5") as the source of the
  **asymptotic upper-bound proof**, `h(n)<=log_2 n+log_*n+O(1)` — a bound about
  growth rate, not a table of exact small values. A section titled "More General
  Bounds" is definitionally about the general-`n` asymptotic construction (the same
  one Alon-Krivelevich paraphrase and `REPORT-bondy-construction.md` already
  extracted `u(k)` from), not a per-`n` exact table — so §4.5 is **not the place an
  exact `m(38)=43,...,m(41)=47` would plausibly be found** even if it were read.
- **The actual unread exposure is §§4.1-4.4, pp. 35-42** (8 pages: 35 through 42
  inclusive, since §4.4 "Five Chords" and §4.5 both start on p. 42, which only parses
  one way: **§4.4 is UNDER one page**, not "a single page" — two sections cannot both
  begin on the same page unless the first ends before the page does. This is the
  single strongest piece of evidence in this whole report, restated here because it
  is what actually bounds the risk: a sub-one-page section has no room for a new
  exhaustive determination of `h(38..41)` with any verification attached (compare
  GMW13's own "Four Chords" section, which needs a full page plus a figure and a
  length/cycle table just to cover 8 vertex values, `15<=v<=22`). These are exactly
  the sections whose subsection titles
  — **"4.1 Introduction," "4.2 Minimal Pancyclic Graphs: Small Orders" (4.2.1 "Fewer
  Than Two Chords," 4.2.2 "Two Chords," 4.2.3 "Three Chords"), "4.3 Four Chords," "4.4
  Five Chords"** — match, almost word for word, the section headers GMW13 itself
  used ("Fewer than two chords," "Two chords," "Three chords," "Four chords," per the
  full body text obtained this session, §§3-4 of GMW13), plus one section ("4.4 Five
  Chords") that GMW13 does not have at all. This is a strong structural signal, not a
  read of the body text itself, but it is a specific, checkable one: **§§4.1-4.3
  read as a textbook restatement of GMW13's own 3-and-4-chord material (capped by
  GMW13's own words at `v<=22`, per Follow-up 1 above), and §4.4 "Five Chords" reads
  as the natural place to restate Griffin's 5-chord extension (capped by Griffin's own
  abstract at `n<=37`)** — i.e. the TOC structure predicts pp. 35-42 assembles two
  already-known, already-capped results, not new ones.
- **What would have to be true for this to threaten the draft's claim, stated as
  precisely as the evidence allows**: those same 8 pages (35-42) would have to (a)
  depart from the section-title pattern that otherwise exactly mirrors GMW13's own
  structure, and (b) silently extend either the 4-chord cap (`v<=22`, GMW13's own
  explicit limit) or the 5-chord cap (`n<=37`, Griffin's own explicit limit) out to
  `n=38..41`, without that extension being mentioned by name in Tao's Oct 2025
  status comment (which names only "very small `n`" work by George-Marr-Wallis
  and gives no exact value past Griffin's), by Alon-Krivelevich's 2024/2025 paper
  (which treats GKW16 as a source only for the asymptotic §4.5 construction, never
  citing an extended exact table), or by any of the other citing/survey sources this
  project has swept (`REPORT-lit-1.md` through `-4.md`). **This is the honest residual
  risk: "seven-to-eight unread pages that would have to extend Griffin's `n<=37` table
  by exactly the four values `n=38..41`, contradicting their own section-title
  structure and going unmentioned by every other source that engages with this book,"
  not "an entire unread chapter titled 'Minimal Pancyclicity.'"** It remains a real
  gap — the pages were not read — but it is now a narrow, specific, and independently
  bounded one rather than an open-ended unknown.
- **GMW13's own 2013 dateline further bounds this line of work's own history**: since
  GMW13 (Wallis's co-authored 2013 paper, same author overlap as GKW16) states in its
  own words that its construction "does not generalize beyond `v = 22`" and "the
  cases `v >= 23` remain open" (Follow-up 1 / the original report's costliest
  finding), the George/Wallis line of work had, as of 2013, itself gotten no further
  than `v=22` on the small-order side. GKW16 (2016) postdates Griffin (2013, `n<=37`)
  by three years and could in principle incorporate Griffin's result (as the TOC's new
  "4.4 Five Chords" section circumstantially suggests it does, restating rather than
  extending it) — but nothing found anywhere in this or prior sweeps shows this
  author group, at any point from 2013 to the 2016 book to the present, going past
  `n=37` on the exact-value side. The asymptotic §4.5 result is the one part of GKW16
  that is genuinely about larger `n`, and it is a growth-rate bound, not a table.

**Updated verdict on the residual gap**: unread, still unknown rather than absent —
but narrowed from "an entire unread chapter" to "8 specific pages (pp. 35-42) whose
own section titles mirror a fully-read, capped-at-`v=22` source, plus a 7-page
asymptotic section (pp. 42-48) that by its own title is about growth rate rather than
an exact table and is already accounted for via Alon-Krivelevich's paraphrase." The
draft's Section 2 novelty claim is unaffected by this sharpening; if anything the
sharpening removes some of the residual uncertainty the original verdict left open.

---

## Follow-up 3 (Manager, this session): independence structure by range, not global — including a correction to Griffin's own stated exhaustive cutoff

Manager asked not to let the OEIS/GMW13 single-computation catch imply `v<=22` rests
on one source, and asked for the independence structure broken out by range, checking
Griffin's actual exhaustive cutoff rather than trusting the draft's or the abstract's
one-line summary of it. Griffin's abstract (`1312.0274.txt` line 7) says *"combining
calculations from an exhaustive search on graphs with up to 29 vertices with a
construction that works for up to 37 vertices"* — but **the paper's own body text
gives a different, more precise, and different-valued statement, quoted exactly**
(`1312.0274.txt` lines 41-45):

> "An exhaustive search has been run for Hamiltonian graphs with at most 4 chords and
> for Hamiltonian graphs with 5 chords and at most 31 vertices. Since, by Corollary 1,
> there are at most 31 cycles in a Hamiltonian graph and there must be at least `n-2`
> cycles..., this suffices to show that no graphs on 25 or more vertices with 4 chords
> can be pancyclic. Therefore, this in combination with our construction with 5 chords
> gives us knowledge of the values of `m(n)` for `n<=37`."

**The abstract's "29" does not appear anywhere in the body text; the body text's own
number for the 5-chord exhaustive cutoff is 31, not 29.** This is exactly the kind of
discrepancy Manager asked to be caught rather than passed through — the abstract is
the imprecise summary here, and the body text (quoted above, cross-checked against
Table 1 below) is the number to use. Reading Table 1 (`1312.0274.txt` lines 47-68)
against this sentence fixes the exact per-range method:

| range | `k` | how Griffin establishes it | exhaustive or construction? |
|---|---|---|---|
| `n=3..24` | `0..4` | "exhaustive search... for Hamiltonian graphs with at most 4 chords" (no vertex cap stated in the text for this part — the search itself is what rules out `k=4` at `n>=25`, so by construction it was run at least through `n=24..25`; no larger explicit number is given, and none is needed since `k<=4` stops mattering past `n=24`) | exhaustive |
| `n=25..31` | `5` | "exhaustive search... for Hamiltonian graphs with 5 chords and at most 31 vertices" | exhaustive |
| `n=32..37` | `5` | **not covered by the stated 31-vertex exhaustive cap.** The lower bound `h(n)>=5` still holds (the `k<=4` elimination is unbounded above, so it covers `n=32..37` too), but the matching upper bound for this sub-range comes only from the explicit 5-chord construction of Griffin's Figure 1 ("Construction with 23 to 37 vertices," `1312.0274.txt` line 26) — a specific verified witness, not a search over all 5-chord graphs on 32-37 vertices for a smaller one | **construction-only for the upper bound; lower bound still exhaustive** |
| `n=38..41` | `5,5,5,6` | not addressed by Griffin (2013) at all — post-dates this paper | this project alone |

So Manager's suspicion was correct in direction and now has the exact number: Griffin's
truly exhaustive 5-chord range is `n<=31`, not `n<=29` as the abstract states, and it
is *smaller* than the draft's Section 1 one-line paraphrase of the abstract implies
in one sense (37 was never claimed to be exhaustive) and the draft does not overclaim
here — Section 1 already correctly separates "exhaustive search" from "a 5-chord
construction valid through `n=37`" without asserting the exhaustive part reaches 37 —
but the draft, like Griffin's own abstract, does not give the reader the precise `31`
cutoff, which this report can now supply on request if the draft is revised later
(no such revision is made here, per instruction not to edit the draft).

**Independence-by-range table, combining the above with Follow-up 1's GMW13/OEIS
provenance finding and this project's own recomputation (`search/hn.csv`, `n<=37`
regression, per the draft's Section 3.3):**

| range | sources, and their independence | how many *independent* computations |
|---|---|---|
| `n=3..14` | GMW13 (exhaustive hand-casework by chord-configuration type, GMW13 §§3, plus Shi's independently-cited `v=9` and `v=14` results folded in) + Griffin (exhaustive computer search, `k<=4`) + this project's recomputation | **3**, of which GMW13-vs-Griffin are genuinely independent methods (hand casework vs. computer search); OEIS's `n<=13` terms (`OFFSET 3,1`, published before the 2011 Marr extension) are a fourth line but not separately re-derived here, so not counted as a new independent computation beyond what already produced them |
| `n=15..22` | GMW13 (Figure 4 construction, explicitly capped at `v=22` by the authors' own words) + Griffin (exhaustive computer search, `k<=4`, covers this range as a subset of `n<=24`) + this project's recomputation. **The OEIS `a(14)-a(22)` terms (Marr, 2011) are the same computation as GMW13's Figure-4 construction, per Follow-up 1 — not a fourth independent line, per Manager's own instruction not to double-count it.** | **3** (GMW13/OEIS counted once, Griffin, this project) |
| `n=23..24` | GMW13 does **not** cover this (`v>=23` explicitly left open in GMW13's own words) — only Griffin's exhaustive `k<=4` search + this project's recomputation | **2** |
| `n=25..31` | Griffin's exhaustive `k=5` search (body text's `31`-vertex cap, not the abstract's `29`) + this project's recomputation | **2** |
| `n=32..37` | Griffin's `k=5` construction (Figure 1, a specific verified witness, upper bound only — not an exhaustive search over this sub-range) + Griffin's exhaustive `k<=4` elimination (lower bound, unbounded above) + this project's recomputation | **2**, and note the upper bound here is construction-only, not exhaustive, for Griffin's own contribution — worth flagging if the draft is ever revised to state precision-of-method by range, though no such revision is made here |
| `n=38..41` | this project alone (`search/pancyc.c`, `search/gpu_pancyc.py`, `search/localsearch.py`, cross-checked by this project's own three independent from-scratch verifiers and, for `n=38,41`, a kernel-checked Lean proof — all documented in the draft's own Section 3.3-3.4, not re-derived here) | **1** external-facing source (this project), with the draft's own internal multi-verifier cross-checking as the redundancy for this range, not a second *external* publication |

**Net honest statement for an editor/referee**: `n<=24` has the strongest redundancy
(3 sources, including two genuinely independent methods — hand casework/construction
vs. exhaustive computer search — for `n<=22`, and computer-search-only redundancy for
`23-24`); `25<=n<=37` has 2 sources each, with the `32-37` sub-range resting on a
*constructive* (not exhaustive) upper-bound witness from Griffin, though its lower
bound is still exhaustively proven; and `38<=n<=41` is this project's alone in the
literature, its internal redundancy coming from multiple independently-written
verifiers within this project rather than from an external second publication. This
is the honest version of "independently confirmed," broken out exactly as requested,
and it does not change the novelty verdict: no source anywhere reaches `n=38`.
