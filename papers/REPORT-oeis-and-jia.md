# OEIS A105206 reconciliation and Jia (1996) citation

Date: 2026-09-14. Follow-up to `REPORT-lit-4.md`, per Manager (f4d1e0af)'s two
follow-up requests. Scope: read-only literature/citation work plus local OCR of one
already-downloaded scanned PDF; nothing was submitted anywhere; one OCR process run
sequentially, negligible compute.

## Part 1 — OEIS A105206 indexing reconciliation

Full draft delivered separately at `papers/oeis/A105206-extension.md` (not submitted;
authorship and submission not decided). Summary of the finding, since it directly answers
"if the published terms disagree with Griffin anywhere, say exactly where":

**They do not disagree anywhere — all 20 published terms match Griffin's `m(n)` table
exactly, term for term, when the OEIS index `n` is read as the vertex count directly.**
The sequence's NAME field ("...on n+2 vertices...") is what's wrong, not the data: it
contradicts both the sequence's own EXAMPLE section (which uses `n` as vertex count,
e.g. "For n = 3 the answer is 3... forming a 3-cycle") and the arithmetic (`a(3)=3`
cannot be `m(5)`, since a pancyclic graph on 5 vertices needs at least 5 edges just for
its Hamiltonian cycle). This was checked against Griffin's Table 1, transcribed
verbatim from the locally saved `papers/1312.0274.txt` (`n, k, m(n)` for `n=3..37`),
term by term for all 20 published OEIS values — full table is in
`A105206-extension.md`. The draft extension file contains the reconciled/extended term
list through `n=41` (marking which terms are already-published OEIS data, which are
Griffin's published-but-not-yet-OEIS-entered values for `n=23..37`, and which are this
project's new `n=38..41` values), a proposed `b105206.txt`, proposed COMMENT/REFERENCES/
LINK lines, and an explicit authorship disclaimer.

## Part 2 — Jia (1996): citation, statement, and search for the paper itself

### Citation identity (confirmed by three independent sources — bibliographic identity only, not the theorem content; see the correction below)

**X. Jia, "Some extremal problems on cycle distributed graphs," Congressus
Numerantium, vol. 121 (1996), pp. 216–222. MR1431994 (97i:05068).**

**What "three independent sources" covers here, precisely:** the bare bibliographic
fact that this paper exists, under this title, in this journal, at this volume/page
range, with this MR number — nothing below establishes that any particular theorem
statement attributed to it is correctly transcribed; that is a separate question,
corrected further down this file. The citation identity is confirmed identical
across: (1) OCR of the reference list (item [25]) in the
locally saved `Lai-Liu-2014-survey.pdf`; (2) two independent `WebSearch` queries, whose
top results both give the same journal, volume, pages, and MR number; and (3) the MR
number matches the one already linked in the TerenceTao comment quoted in full in
`REPORT-lit-4.md` (`mathscinet.ams.org/mathscinet/article?mr=1431994`). Congressus
Numerantium is a Canadian/US-based combinatorics conference-proceedings series, not a
Chinese journal, despite the author's name — so a CNKI search was not attempted; a
general Google Scholar/zbMATH-style web search was used instead, per the assignment's
"if it is a Chinese journal" conditional.

### How the citation and statements were obtained

`Lai-Liu-2014-survey.pdf` (589KB) is a scanned/image PDF — direct PDF text extraction
and `WebFetch` both failed, `WebFetch` reporting "binary CCITT Fax-encoded image data
that cannot be parsed as readable text" (this was flagged as an open limitation in
`REPORT-lit-4.md`). To resolve it: Tesseract OCR (v5.4.0.20240606) was found already
installed on this machine at `C:\Program Files\Tesseract-OCR\tesseract.exe` (the
requested `winget install` for `UB-Mannheim.TesseractOCR` reported "Found an existing
package already installed. Trying to upgrade... No available upgrade found" — so no
new install occurred, it was already present); `pymupdf` was already installed in the
Python environment, and `pytesseract` was added via `pip install --user pytesseract`.
All 14 pages of the survey were rasterised at 300dpi with PyMuPDF and OCR'd with
Tesseract, sequentially, as a single process (output kept at
`papers/ocr_tmp/page01.txt`..`page14.txt`; the rasterised PNGs were deleted afterward
to avoid clutter, the OCR text was kept as evidence).

### The statements themselves (quoted from OCR, page 3–4 of the survey; page numbers as
printed in the survey are 53–54)

The survey defines, in its own notation: "Let `g(n)` denote the least number of edges
of a graph which contains a cycle of length `k` for every [3<=k<=n]" (this is the same
function as Griffin's `m(n)` and Erdős #1016's `n+h(n)`; the OCR rendered the bound
range as "1< k <n," which is very likely a scan artifact — the survey's own Erdős
Problem 1 section a page earlier uses the standard "no two cycles have the same length"
framing for a *different* function `f(n)`, and `g(n)` is introduced specifically to
discuss pancyclic-type results, so `3<=k<=n` is the mathematically necessary reading,
but the raw OCR string is reported here rather than silently corrected).

> "Jia[25] proved the following results:
>
> Theorem 1.13 (Jia[25]) When n is sufficiently large, n + log_2 n - 1 <= g(n) <= n +
> (3/2) log_2 n + 1.
>
> Theorem 1.14 (Jia[25]) For a sufficiently large positive integer n, g(n) <= n +
> log_2 n + [OCR: '3 log, logy n'] + O(1)
>
> Corollary 1.15 (Jia[25]) For n sufficiently large, g(n) = n + log_2 n +
> O(log_2 log_2 n).
>
> Jia[25] made the following conjecture:
>
> Conjecture 1.16 (Jia[25]) g(n) = n + log_2 n + O(1), as n -> infinity."

(Transcribed with OCR's garbled `log,`/`logy`/`9(n)` corrected to `log_2`/`log_2`/`g(n)`
throughout except where flagged `[OCR: ...]`, since Tesseract systematically misreads
subscript-2 as a comma or the digit/letter "9"/"y" on this scan; the one place this
matters for content rather than typography is Theorem 1.14's coefficient on the
double-log term, quoted in raw OCR form since a wrong "correction" here would be worse
than reporting the garble.) Theorem 1.13's upper bound, `n + (3/2)log_2 n + 1`, matches
the TerenceTao erdosproblems.com comment's paraphrase exactly
(`h(n) <= (3/2) log_2 n + 1`).

**Correction (2026-09-14, later session, per Manager): this match is NOT independent
corroboration of Jia's theorem, and the word "independent" above was wrong.** It is
evidence only that the OCR correctly transcribed the Lai-Liu survey's paraphrase —
not evidence that the Lai-Liu survey correctly represents Jia's actual result — because
Tao's own comment states, quoted verbatim from the full fetch in `REPORT-lit-4.md`:
*"An obscure 1996 paper of Jia (which I was not able to directly obtain, but could
see their results mentioned in this 2014 survey of Lai and Liu)."* Tao read the exact
same secondary survey this project OCR'd, not Jia's paper. So this project's OCR and
Tao's paraphrase are two readings of one document, not two independent readings of
Jia's theorem — the same failure mode as counting a citation twice. What the
agreement genuinely establishes: the OCR correctly captured what the Lai-Liu survey
says (a real, useful check on transcription fidelity), and, combined with the
citation-identity confirmation above, that this specific paper by this specific
author really is being paraphrased by that survey. It does **not** establish that
Jia's own proof or statement is correctly represented by that paraphrase — that
remains unverified, since Jia's paper itself was never obtained (see below). Full
analysis: `papers/REPORT-fibonacci-asymptotics.md`, Part 3. **Conjecture 1.16 is, in substance, Erdős Problem #1016
itself** — the survey text says exactly this ("Jia[25] made the following
conjecture... `g(n) = n + log_2 n + O(1)`"), consistent with TerenceTao's comment that
Jia's 1996 paper "also makes the conjecture #1016."

### Whether Jia's paper itself was located

**Not obtained.** No open-access copy, preprint, or digitised scan of Jia (1996) was
found. A targeted search for a digitised Congressus Numerantium vol. 121 (Archive.org,
HathiTrust) found only a HathiTrust catalog record for the Congressus Numerantium
series in general, with no confirmation that volume 121 specifically is available in
full view (HathiTrust access levels vary by volume and are frequently
snippet/catalog-only for 1990s conference proceedings); no CNKI search was run since
the venue is not a Chinese journal. This is an **unknown**, not an **absent** — the
paper may well exist in university library holdings or MathSciNet's own scan (paywalled,
not accessible from this session) that were not reachable with the tools available
here.

### Bearing on the project's novelty claim

Jia's results are all upper bounds (constructions), matching or slightly weaker than
the `n + log_2 n + log_*n + O(1)` bound later proved in George–Khodkar–Wallis (2016).
Jia's paper contains no exact table of `g(n)`/`m(n)`/`h(n)` values (the survey quotes it
only as asymptotic theorems for "n sufficiently large"), so it does not affect the
n<=37-is-the-largest-tabulated-value conclusion already reported in `REPORT-lit-1.md`,
`REPORT-lit-2.md`, and `REPORT-lit-4.md`.
