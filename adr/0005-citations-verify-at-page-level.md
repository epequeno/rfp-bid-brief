# 0005 — A citation is verified at page level, because spans are ours and pages are the document's

- **Status:** accepted (2026-10-11)
- **Date:** 2026-10-11

## Context

ADR 0004 set the citation rule as containment at word boundaries *inside the cited span*. The first
model-backed run showed what that costs. Of thirteen citations in the Tahoe fixture, nine held and
four were refused — and all four were refused for the same reason: the quote ran across a span
boundary and the model cited one of the two spans it touched.

- *"In case of an emergency, be on-site within four (4) hours"* — `In case of an emergency,` ends one span; `be on-site within four (4) hours` begins the next.
- *"On-site support for TTD facilities at South Lake Tahoe, California and Stateline, NV is "` — continues into the following span.

Tightening the prompt (quote from one span; prefer five to twelve words) did not change it: the same
four failed on the re-run. That is a signal about the rule, not about the model. **Spans are produced
by a heuristic sentence splitter; sentences in a document do not know that.** A rule that requires a
quote to sit inside one splitter output makes the splitter part of the correctness condition, and the
splitter is the least dependable component in the pipeline.

What the citation rule actually has to protect is that a quoted string exists in the fixture, and
that its locator is not misleading. Neither of those requires the splitter to have guessed a
sentence boundary correctly.

## Decision

A citation is a span id plus a quote. It is **valid** when either:

1. the quote sits inside the cited span, at word boundaries, whitespace-insensitively; or
2. the quote exists in the document read as continuous text (the spans in order), at word
   boundaries and whitespace-insensitively, **and the cited span is on the same page as the text it
   quotes**.

A quote that is absent from the fixture is refused in both cases. A quote whose citation points at a
different page is refused: pointing at the wrong place is a broken locator, and the page is the one
positional fact the document itself supplies.

## Consequences

- The anti-hallucination property is unchanged and is still the point: a fabricated quote is refused
  because it is not in the document, not because it is in the wrong sentence.
- The locator weakens from "the exact span" to "the right page". That is a real loss of precision and
  it is accepted deliberately: the alternative was to fail correct quotations for being written
  across a line of the extractor's choosing.
- Page-level verification needs no new schema. `span_id` plus `quote` remains the citation, and the
  eleven hand-authored extractions needed no migration.
- The first model run becomes a recorded result rather than an incident: nine of thirteen citations
  held under the strict rule, four failed on span boundaries, and under this rule the same four hold
  while a quote that is not in the document still fails. That re-run is the evidence for this
  decision, and it is reported as such.
- Revisiting ADR 0004's rule is the second time this contract has moved for the same underlying
  reason — equality was too strict, then single-span containment was. Both times the fix was to stop
  letting an implementation detail of extraction constrain what a citation may say. If a third
  tightening is ever proposed, the question to ask first is which component it makes load-bearing.
