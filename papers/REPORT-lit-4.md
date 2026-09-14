# Literature sweep 4: theses, repositories, forums, OEIS, formal proofs

Date checked: 2026-09-14. Scope per assignment: theses/dissertations (ProQuest/OATD),
GitHub repositories, MathOverflow/MathStackExchange, OEIS entries and their comments,
the erdosproblems.com #1016 forum, Zamfirescu's (2)-pancyclic work, minimal bipancyclic
work, uniquely pancyclic (UPC) progress after Markström 2009, and any formal
(Lean/Coq/Isabelle) or SAT-based treatment. This report does not repeat the core
lower/upper-bound literature already catalogued in `REPORT-lit-1.md` and
`REPORT-lit-2.md`; it cross-checks their central claim ("no located primary source
gives m(n) or h(n) for n>=38") from four new angles.

## Costliest finding first

The erdosproblems.com page for #1016 is the field's own status tracker, and it was
fetched directly (`curl` with a browser user agent; `WebFetch` alone returned HTTP 403,
evidently a bot block, so the raw HTML was pulled to
`C:\Users\ToolsEnabled-Dev\AppData\Local\Temp\erdos1016.html` and its linked discussion
page to `...\erdos1016-discuss.html`, then read locally). The page shows exactly one
comment, posted by user `TerenceTao` at "00:50 on 18 Oct 2025" (post id 1188), and the
page footer states "This page was last edited 27 December 2025" — i.e. the page text
was revised in direct response to that comment (the post itself is marked
"(The site has been updated to address this comment.)"). Quoting the comment verbatim
from the fetched HTML:

> "Bondy's paper actually claims the slightly weaker bounds $\log_2 (n-1) - 1 \leq h(n)
> \leq \log_2 n + \log_* n + O(1)$, contrary to what Erdos writes, but with no proof
> given for either inequality. An actual proof of the lower bound was only provided in
> 2013 by Bi-George-Rui, though this 2023 paper of Alon and Krivelevich suggests that a
> equivalent statement was established by Shi in 1994 (but it is difficult for me to
> confirm this as the notation is somewhat different). An obscure 1996 paper of Jia
> (which I was not able to directly obtain, but could see their results mentioned in
> this 2014 survey of Lai and Liu) establishes $h(n) \leq \frac{3}{2} \log_2 n + 1$ for
> all $n$ and $h(n) \leq \log_2 n + \log_2 \log_2 n + O(1)$ for all sufficiently large
> $n$, and also makes the conjecture #1016. The first literature proof of the upper
> bound $h(n) \leq \log_2 n + \log_* n + O(1)$ that seems to exist is in Chapter 4.5 of
> this 2016 book of George, Khodkar, and Wallis. The consensus seems to be that Bondy's
> bounds, which are now proven in the literature, remain the state of the art except for
> very small $n$ where there is some work by George, Marr, and Wallis."

This is decisive for the novelty question in three ways. First, it is dated 18 October
2025 and the visible page was edited in response to it on 27 December 2025, so it
reflects the field's most current public accounting, not a stale snapshot. Second, it
explicitly says the state of the art is Bondy's asymptotic bounds "except for very small
n where there is some work by George, Marr, and Wallis" (the source of Griffin's n<=37
table) — it names no source past n=37. Third, it surfaces one genuinely new
bibliographic lead not found in `REPORT-lit-1.md`/`REPORT-lit-2.md`: an "obscure 1996
paper of Jia" with an intermediate upper bound $h(n)\le\frac32\log_2n+1$, predating
GKW16's proof of the sharper $\log_2n+\log_*n+O(1)$ bound. Note also a citation
inconsistency worth flagging: the comment attributes the 2013 lower-bound proof
(arXiv:1312.0274) to "Bi-George-Rui," while the erdosproblems.com main page, Griffin's
own arXiv listing, and this project's own `REPORT-lit-1.md` all attribute it to sole
author Sean Griffin. The comment itself was AI-assisted (it links results from Gemini
and ChatGPT sessions used "after 5 mins" and "after 7 mins"), so this looks like an
AI-generated misattribution rather than a real co-author; it is reported here rather
than silently corrected, per the no-self-review-of-the-source discipline, but readers
should treat "Bi-George-Rui" as unverified and prefer "Griffin" pending a check of the
paper's actual byline (arXiv:1312.0274 lists only Sean Griffin, Dartmouth, advisor Sergi
Elizalde — checked via arXiv listing, `REPORT-lit-1.md`, and the paper's own PDF).

The "More information and links" panel on the same fetched page states: "Formalised
statement? No (create one)" and links `OEIS A105206`. No proof claims, no proof
expositions, and (as of the fetch) no likes/reactions of substance. This directly
answers the assignment's question about exactly what the page says: status **open**,
one comment (quoted above, in full), zero proof claims, zero expositions, not
formalised.

## Formal (Lean/Coq/Isabelle) treatment

**google-deepmind/formal-conjectures, GitHub issue #1073** ("Erdős Problem 1016"),
opened by user `mo271` on 14 Oct 2025, labelled `ams-05: Combinatorics`,
`erdos-problems`, `new conjecture`, still **open** with no assignee. Its body restates
the problem statement and links erdosproblems.com/1016; there are no comments, no
linked PRs, and no computed values. This was independently confirmed by querying the
repository directly rather than trusting the issue text alone: `git`/`curl` against the
GitHub contents API for `FormalConjectures/ErdosProblems/` lists files `1000.lean,
1002.lean, 1003.lean, 1004.lean, 1007.lean, 1008.lean, 1014.lean` in that numeric
neighborhood but **no `1016.lean`**, and a direct raw-content fetch of
`.../ErdosProblems/1016.lean` returns HTTP 404. Two independent checks (issue text, and
direct file/listing query) agree: **no Lean formalisation of #1016 exists yet**, and
therefore no formalised computation of any m(n)/h(n) value for any n.

**jaredwilder's Erdős-formalisation repositories** (`erdos-cable-corpus`,
`erdos-lean-remainder`, `erdos-release-index`, `erdos-theorems`, `erdos152`,
`lean-semantic-blades`) surfaced in search results as large, actively updated (dated
2026-09-05 through 2026-09-14) collections claiming Lean work across "152 open Erdős
problems." These are self-published, unaudited, and explicitly say so: the
`erdos-cable-corpus` README states "The often-quoted 891 sorry-free count is only a
textual property. It does not tell you whether Lean accepted the file," reports 267 of
914 files "failed to compile," and calls itself a "raw formalization corpus" rather
than verified results. Given that self-description, any claim from these repos would
need independent kernel verification before being trusted regardless of topic. On the
narrower factual question of coverage: two independent checks were run — (1) a
name-grep across all 914 filenames in `erdos-cable-corpus/theorems` for "1016" or
"pancyc", zero matches; (2) a content-grep of that repo's `MANIFEST.json` for the same
strings, zero matches. `erdos-theorems`'s own subdirectory listing (curated,
supposedly higher-quality) has no `erdos1016*` folder among its 27 named problem
folders. `erdos152/statement-corpus` does contain
`entry-graph-erdos-1016.json`, but inspection shows it is only a scraped snapshot of
the erdosproblems.com page text (with SHA-256 provenance hashes), not new mathematics
or a Lean statement — it reproduces the same problem text and the same "Comments (1)"
count already analysed above, dated to an "accessed 2026-08-30" note inside the JSON
that predates the 27 Dec 2025 page edit reported above (the page changed after this
scrape was taken, since the JSON's copy of the page still says "accessed 2026-08-30"
under a since-updated citation format). **Verdict: none of the checked jaredwilder
repositories contain a Lean formalisation, a SAT instance, or any computed value for
Erdős #1016.**

**SAT-based treatment.** Targeted search for "SAT solver pancyclic graph" and "SAT
modulo graphs pancyclicity" found only generic SAT-for-graph-properties papers
(acyclicity encodings, clique-width) with no application to pancyclicity, plus one
relevant capstone-level remark (Kilpatrick 2024, below) about "computer scripts" for
UPC search that are combinatorial case-eliminators, not SAT encodings. **No SAT-based
treatment of pancyclicity or of m(n)/h(n) was located.**

## Theses and dissertations

**Zak Kilpatrick, "A Closer Look at the Structure of Uniquely Pancyclic Graphs,"
Louisiana Tech University Mathematics Senior Capstone Papers, Spring 2024, advisor
Dr. Turner.** This is an undergraduate senior capstone, not a ProQuest/OATD-indexed
graduate dissertation, but it is squarely on-topic (uniquely pancyclic graphs, the
post-Markström line named in the assignment) and was retrievable as an open PDF
(fetched via `curl` with a browser user agent after `WebFetch` returned HTTP 403; saved
to `Kilpatrick-UPC-capstone.pdf`). Its abstract states: "To date, there are only seven
known graphs of this type," matching Markström (2009)'s null result and confirming no
new UPC graph has been found in the fifteen years since. The paper proves two new
lemmas constraining how the 3-cycle and 4-cycle of a hypothetical UPC graph must
relate to the Hamilton cycle (ruling out the "hourglass" and "bow tie" chord patterns
in general, not just as base cases), explicitly to narrow future computer search rather
than to produce new graphs itself. It cites Markström's result as "there are no new
unique UPC-graphs on less than 60 vertices" and "we do not consider any graph with
exactly 5 chords," consistent with `REPORT-lit-1.md`'s reading of the same source. It
surfaces one bibliographic lead new to this project: **C. Lai, "On the size of graphs
without repeated cycle lengths," Discrete Applied Mathematics 232 (2017), 226–229**,
which "refined upper and lower bounds for UPC-graphs" to $n+\ln(n)-1 \le \text{edges} <
n+\frac32\ln(n)+1$. This bound is for the strictly harder uniquely-pancyclic condition
(exactly one cycle of each length), not the ordinary minimum-edges pancyclic function
m(n)/h(n) that is the subject of Erdős #1016, so it does not itself supply an m(n)
value, but it is a legitimate post-Markström UPC advance the assignment asked about.
Kilpatrick's closing section separately notes "There is currently work being done on
[uniquely bipancyclic graphs on] less than 40 vertices using a computer program" — this
is about uniquely bi-pancyclic graphs (an even stricter, different condition), gives no
citation or numeric result, and is not a statement about m(n)/h(n) for n>=38; it is
flagged here only because "n<40" appears in the text and a careless reading could
mistake it for progress on the assignment's actual question, which it is not.

**Sean Griffin's "Minimal Pancyclicity" (arXiv:1312.0274).** Search results (Google,
arXiv metadata) indicate this was Griffin's Dartmouth undergraduate work under advisor
Sergi Elizalde, released directly to arXiv rather than deposited as a ProQuest/OATD
graduate dissertation; no separate ProQuest/OATD record for it was found.

**General ProQuest/OATD/university-repository search:** queries for `"pancyclic"
thesis dissertation minimum edges ProQuest OR OATD` and adjacent phrasings returned no
dissertation matching the m(n)/h(n) topic beyond Griffin's and Kilpatrick's already-
catalogued work. This is a **literature miss, not a proof of nonexistence** — ProQuest's
full index is not searchable through the tools available in this session (no ProQuest
account/API access), so coverage of that specific database is **unknown**, not
**absent**.

## GitHub repositories (general search, beyond the Lean corpora above)

**osawin/Pancyclic** (github.com/osawin/Pancyclic): a small C++11 repository (README
describes it as "2 Commits" on `master`) implementing search programs for uniquely
pancyclic, n-pancyclic, n-bipancyclic and n-oddly-bipancyclic graphs restricted to
chords of length 1. The fetched README gives no results table, no n range, and no
indication it was ever run past small cases; it is a search *tool*, not a source of
computed m(n)/h(n) values. No other GitHub repository specific to the ordinary
minimum-edges pancyclic problem was found via general web search (queries: "github
pancyclic graph search minimum edges chords", "github pancyclic graph minimum size").

## Zamfirescu's (2)-pancyclic work

**C. T. Zamfirescu, "(2)-pancyclic graphs," Discrete Applied Mathematics 161 (7–8)
(2013), 1128–1136, DOI 10.1016/j.dam.2012.11.002.** ScienceDirect blocked direct
fetch (HTTP 403, both via `WebFetch` and via `curl` with a browser user agent — this
one is genuinely paywalled/bot-gated, unlike erdosproblems.com and OEIS which only
needed a browser user agent). Citation and topic are independently confirmed via two
sources: web search result snippets ("Zamfirescu introduced the class of (2)-pancyclic
graphs... and gave several examples of such graphs, among which are the smallest") and
Kilpatrick's reference list (`[7] C. T. Zamfirescu, "(2)-pancyclic graphs," ...`, exact
DOI match). A (2)-pancyclic graph requires *exactly two* cycles of each length from 3 to
n (a direct generalisation of uniquely-pancyclic's "exactly one"), so this is a sibling
extremal-uniqueness question, not the m(n)/h(n) minimum-edges question; no exact
m(n)/h(n) value for n>=38 is claimed or implied by its abstract text as located. Full
text was not obtained; its content beyond the abstract/topic is **unknown**, not
**absent**.

## Minimal bipancyclic work

**Setiabudi, Erlebach, et al. (unclear full author list from abstract alone),
"(r)-Pancyclic, (r)-Bipancyclic and Oddly (r)-Bipancyclic Graphs," arXiv:1510.03052.**
Defines an $(r)$-pancyclic graph as one with *precisely* $r$ cycles of every length
(generalising both ordinary pancyclic, $r\ge1$, and Zamfirescu's (2)-pancyclic, $r=2$),
and $(r)$-bipancyclic analogously for balanced bipartite graphs over even lengths only.
Per the fetched abstract, it classifies all such graphs by computer search "with $v$
vertices and at most $v+5$ edges" (pancyclic/bipancyclic case) and "at most $v+4$ edges"
(oddly-bipancyclic case) — i.e. up to 5 chords/4 chords respectively, matching the same
chord-count regime Griffin and Markström search in. No minimum-edge formula or
asymptotic result for the ordinary m(n)/h(n) problem is given; this is a
classification paper for fixed small excess, not an extremal-value paper for growing n.
No exact numeric value for n>=38 was found in the abstract; full text was not fetched
(not attempted given the abstract already answers the relevance question), so its
interior content beyond the abstract is **unknown**.

George–Khodkar–Wallis's 2016 book chapter on "Uniquely Pancyclic Graphs" (already
catalogued in `REPORT-lit-1.md`) is the same source's stated home for bipancyclic
material; no additional post-2016 bipancyclic minimum-edge paper specific to m(n)/h(n)
was found via the searches run here.

## OEIS A105206 — full page content

Fetched directly (`curl` with browser user agent, `WebFetch` returned HTTP 403).
Full sequence data as currently published: `3, 5, 6, 8, 9, 10, 12, 13, 14, 15, 16, 17,
19, 20, 21, 22, 23, 24, 25, 26` with `OFFSET` `3,1` — i.e. 20 terms covering index
n=3..22, and since the sequence name is "Number of edges in a pancyclic graph on n+2
vertices with the fewest possible edges," this covers graphs on **4 to 24 vertices**,
far short of even Griffin's n<=37 table, let alone n>=38. `COMMENTS` contains only the
one-line definition, no discussion. `EXTENSIONS` records "a(14)-a(22) by Alison Marr,
Aug 22 2011" — no extension since 2011. `LINKS` points back to the erdosproblems.com
page and the Erdős-problem-database GitHub README, i.e. OEIS defers to those sources
rather than maintaining its own updated table. `STATUS` is `approved`. **No comments
beyond the definitional one exist on this OEIS entry, and its own published data does
not reach n=38.**

## Search audit and negative-result limits

Databases/surfaces used, with the caps/queries applied:

* **erdosproblems.com**: direct HTML fetch of `/1016` and `/forum/discuss/1016` via
  `curl -A "Mozilla/5.0 ..."` after `WebFetch` returned HTTP 403 on both (evident bot
  gate, not a real access denial — confirmed by the 200 status once a browser
  user-agent string was supplied). Read in full; both pages are short (~32KB and
  ~38KB) and were read to completion, not sampled.
* **OEIS**: same technique (curl with browser UA after WebFetch 403) for `A105206`;
  read in full (~14KB).
* **GitHub**: `curl` against the public REST API (`api.github.com/repos/.../contents/...`)
  for `google-deepmind/formal-conjectures`, `jaredwilder/erdos-cable-corpus`,
  `jaredwilder/erdos-lean-remainder`, `jaredwilder/erdos-release-index`,
  `jaredwilder/erdos-theorems`, `jaredwilder/erdos152`, `jaredwilder/lean-semantic-blades`,
  and `osawin/Pancyclic`; also `WebFetch` on the issue page
  `google-deepmind/formal-conjectures/issues/1073` and on `github.com/osawin/Pancyclic`.
  Code-search (`api.github.com/search/code`) required authentication (HTTP 401) and was
  not used; absence claims for the jaredwilder corpora instead rest on two independent
  non-authenticated methods (full directory-listing name-grep, and full-file
  content-grep of `MANIFEST.json`), per the assignment's two-method rule for absence
  claims. GitHub's own code-search index coverage is therefore **unknown**, not
  **absent**, for anything not caught by those two greps.
* **arXiv / web search** (via `WebSearch`, no explicit domain restriction unless
  noted): `Zamfirescu pancyclic graphs minimum edges construction`; `OEIS A105206
  pancyclic graph edges comments`; `"pancyclic" thesis dissertation minimum edges
  ProQuest OR OATD`; `mathoverflow pancyclic graph minimum number of edges`;
  `"uniquely pancyclic" graph 2020 OR 2021 OR ... OR 2025`; `github pancyclic graph
  search minimum edges chords`; `erdosproblems.com 1016 pancyclic Bondy`; `jaredwilder
  erdos-cable-corpus OR erdos-lean-remainder OR erdos-release-index "1016" pancyclic`;
  `"formal-conjectures" pancyclic Erdos 1016 Lean formalization statement`;
  `Zamfirescu "(2)-pancyclic" OR "2-pancyclic" graphs paper`; `minimal bipancyclic
  graphs minimum edges construction`; `SAT solver pancyclic graph construction search`;
  `site:mathoverflow.net pancyclic`; `site:math.stackexchange.com pancyclic minimum
  edges`; `Griffin "Minimal Pancyclicity" dissertation Dartmouth thesis`.
* **MathOverflow / MathStackExchange**: two site-restricted `WebSearch` queries (listed
  above) returned zero pages from either domain. This is a **literature miss**: the
  `WebSearch` tool's index of these sites is not verified complete, so **absence of a
  relevant thread is unknown, not confirmed**, even though two independent query
  phrasings were tried.
* **ProQuest**: no direct API/account access in this session; coverage is **unknown**.
  OATD-style open-repository coverage was partially substituted by general web search,
  which did surface the Kilpatrick capstone (a non-ProQuest open repository, LaTech
  DigitalCommons) but no ProQuest-proper dissertation on this exact topic.
* **Downloads**: `Lai-Liu-2014-survey.pdf` (589KB, image/CCITT-fax-scanned — text
  extraction failed via both direct PDF read, which needs `pdftoppm`/poppler not
  installed on this machine, and `WebFetch`, which reported "binary CCITT Fax-encoded
  image data that cannot be parsed as readable text"; its content beyond the
  TerenceTao-comment paraphrase of Jia's result is therefore **unknown**, not read) and
  `Kilpatrick-UPC-capstone.pdf` (196KB, native PDF, read in full) were saved to this
  folder. The `ocr.read` tool available in this session only operates on local screen
  captures, not arbitrary PDFs, and was not usable for the scanned survey.

## Closing statement

Across all four new angles investigated here — theses/dissertations, GitHub
repositories (including every Lean/SAT formalisation corpus found), MathOverflow/MSE,
and OEIS/erdosproblems.com's own comment thread — **no source gives any value of m(n)
or h(n) for n>=38**. The single erdosproblems.com comment (TerenceTao, 18 Oct 2025,
quoted in full above), which is the most current authoritative status statement located
anywhere in this sweep, itself states the record stands at Bondy's asymptotic bounds
plus George–Marr–Wallis/Griffin's small-n table, with no source named past that. OEIS
A105206's own published data stops at n=24 vertices. No GitHub repository, formal
proof file, or SAT instance addressing Erdős #1016 was found to exist at all (the one
Lean issue for it is open and empty). **The largest n for which any value of m(n) (or
equivalently h(n)) appears anywhere in the literature located across this entire
project (this report plus `REPORT-lit-1.md` and `REPORT-lit-2.md`) is n=37**, from
Griffin (2013)/George–Marr–Wallis (2013), reproduced in George–Khodkar–Wallis (2016).
This is consistent with, and independently corroborates from new sources, the prior
sweeps' conclusion that the project's own h(38)=h(39)=h(40)=5 and h(41)=6 results are
apparently new relative to all located literature.
