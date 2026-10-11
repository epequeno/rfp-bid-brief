# 0001 — Span-ID citations as a structural guarantee

- **Status:** accepted
- **Date:** 2026-10-11

## Context

A brief that recommends a bid or a no-bid is only usable if its reasons can be checked. The usual
approach — ask a model to quote the document, then review the quotes — puts the burden of detection
on a reader who is already inclined to believe the output. Reviewing for fabricated quotations does
not scale and does not fail loudly.

The pipeline has a fixed structure: `parse → extract → decide → brief`. The question is where
verifiability is enforced.

## Decision

**Every extracted field carries the identifier of the span it came from, and the extractor may only
emit identifiers that exist.** Spans are produced by `parse` and are the sole currency of the rest
of the pipeline: `decide` cites spans as its reasons, and `brief` renders quoted text by looking it
up in the span index rather than generating it.

Consequently a brief cannot quote something that is not in its fixture: the text is retrieved by
identifier, not produced. The citation-integrity check is therefore a **test**, not a review
finding — a brief that renders a span which does not exist verbatim in its fixture fails the suite.

## Consequences

- `parse` becomes load-bearing: the span index must cover the document, be stable across runs, and
  be reproducible from the same input.
- Extraction is reframed from "summarise this document" to "select identifiers and map them to
  typed values", which is what makes a typed decision layer possible at all.
- Work that would otherwise be invisible becomes explicit: a span that cannot be located is an
  extraction failure surfaced at extraction time, not a hallucination discovered later.
- The brief's prose is constrained to what the span index supports. This is a real limit on
  fluency, and it is accepted deliberately: the alternative is confident text that cannot be
  checked.
