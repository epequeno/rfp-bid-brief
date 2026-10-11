# 0004 — Citations locate a quote inside a span, at word boundaries

- **Status:** accepted (2026-10-11)
- **Date:** 2026-10-11

## Context

ADR 0001 fixed that every extracted field cites a span, and that a quoted span must exist verbatim
in its fixture. It did not say what makes a quote valid against a span, and the first implementation
answered that question by accident: a quote had to **equal** a span.

The Tahoe fixture killed it. Its disqualifying requirement reads *"In case of an emergency, be
on-site within four (4) hours"*, and the span containing it is the whole sentence. Under equality, a
brief could cite that span but could not quote the four hours — the only part that matters — so the
brief would either quote a conditionally framed sentence or nothing. Equality also makes the
extractor's job the splitter's job, which is backwards: the splitter is heuristic, and the citation
rule must not depend on a heuristic being right.

A second round of tests then showed plain substring containment to be too permissive: `four (4) hour`
is a prefix of `four (4) hours`, so a truncated quote verified and would then read as a typo in a
brief.

## Decision

A **citation** is a span identifier plus a quote. It is valid exactly when

    collapse_ws(quote) occurs in collapse_ws(span.text) at word boundaries

where `collapse_ws` collapses whitespace runs to single spaces and strips. Whitespace is the **only**
normalisation: punctuation, case, hyphenation, digits and symbols must match exactly, and the stored
text is NFC.

Both ends of the match must be adjacent to a non-alphanumeric character or an end of text. Matching
may begin mid-span — a phrase inside a long sentence is a legitimate citation — but never mid-word.

When a quote resolves to more than one span, the citation is **ambiguous** and must be disambiguated
by page. The tooling refuses to pick one: `rfpbrief find` exits non-zero and names the candidate
pages.

## Consequences

- Briefs can quote the clause that carries the decision rather than the sentence that contains it,
  which is the difference between a usable brief and a legalistic one.
- The verification test is a boundary-checked substring test, so it stays cheap and stays honest:
  there is no similarity threshold to tune and no fuzzy matching to tune down later.
- Truncated and reformatted quotes are rejected. Reformatted in particular: `within 4 hours` will not
  resolve against `within four (4) hours`, so an extractor that paraphrases numbers fails loudly
  instead of producing a plausible citation.
- The contract is defined against *extracted* text, so the extraction engine becomes part of the
  contract. Hence the engine name and version are stored in every index and checked by
  `rfpbrief verify`: a different engine may produce different text, and the honest response is to
  fail the index rather than re-verify against new text silently.
- Span granularity is now a quality concern rather than a correctness one. The first spike measured
  2.2% of spans swallowing a bullet boundary; that degrades what is quotable without ever making a
  citation false.
