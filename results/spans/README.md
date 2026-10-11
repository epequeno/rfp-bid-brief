# Span indexes — first spike, 2026-10-11

Eleven indexes, one per fixture, built by `uv run rfpbrief build`. Each is regenerable from its
fixture and records the engine that produced it, so `just verify-spans` can fail loudly when either
has moved.

```
fixture                                                           pages  spans  median  max  bullet-swallowing  hyphen breaks
city-of-snohomish-it-strategic-plan-rfp.pdf                           7    102     122  317                 3              0
city-of-spicer-mn-managed-it-services-2026.pdf                        6     98      71  315                 2              0
coastal-bend-college-erp-sis-rfp-2026-01.pdf                         60   1017     126  320                 4              0
community-action-partnership-kern-information-systems-consultant.pdf  14    348      61  313                 9              0
energy-trust-of-oregon-crm-migration-to-d365.pdf                      12    183     117  318                 6              0
hacc-rfp-26022-cloud-document-management.pdf                          23    361     103  320                15              0
inprs-rfp-23-04-cloud-migration-iam-ztna.pdf                          38    765     114  320                14              0
mass-tech-ai-hub-data-commons-consulting-2026-jaii-01.pdf             10    120     139  318                17              0
palm-beach-mpo-rfp-2026-07-it-services.pdf                            27    429     124  320                18              0
tahoe-transportation-district-it-consulting-2025.pdf                  43    845     100  320                31              0
u-maine-system-rfp-2026-065-enterprise-genai-services.pdf             48   1438      82  316                 9              0

                        totals: 278 pages, 5,706 spans, 1.3 MB of index
```

## What the spike established

1. **The index is deterministic and reachable.** Two builds of the same fixture are byte-identical,
   and for all 5,706 spans `page_text[start:end] == span.text`. Both are tests, not claims.
2. **Quote sizes are usable.** Median span 61–139 characters — a sentence or a clause, which is what
   a brief needs to quote. The 320-character budget holds; the largest span in the whole corpus is
   320.
3. **A near-miss is refused.** `be onsite within four hours` and `within 4 hours` do not resolve,
   while `be on-site within four (4) hours` resolves to exactly one span (`p7-s11`, page 7 of the
   Tahoe fixture) and silently picks nothing ambiguous.

## What the spike changed

**The citation contract was wrong on the first attempt, and the fixture caught it.** ADR 0001 said
span-ID citations; the first implementation required a quote to *equal* a span. The Tahoe fixture's
disqualifying line is *"In case of an emergency, be on-site within four (4) hours"* — so a brief
could only have quoted the whole sentence, including the conditional it does not need. The contract
is now **containment at word boundaries** ([ADR 0004](../adr/0004-citations-locate-inside-spans.md)),
and the boundary condition came from the same round of testing: plain containment accepted the
truncated `four (4) hour` as a prefix of `four (4) hours`.

## Two findings recorded rather than fixed

- **List structure partly defeats sentence splitting.** 128 of 5,706 spans (**2.2%**) swallowed a
  bullet boundary — an item marker (`•`, `o `, a private-use glyph) followed by more text. These sit
  disproportionately in requirement lists, which is exactly where a brief wants to quote. Small
  enough not to block the pipeline; worth a targeted fix once extraction quality can be measured
  rather than guessed at.
- **Hyphenated line breaks: zero, across all eleven fixtures.** The module refuses to repair
  hyphenation, on the grounds that repairing it means guessing and guessing is how a citation check
  starts matching text that was never there. That refusal costs nothing measurable on this corpus —
  a risk retired rather than carried.
- **Non-breaking hyphens, and they bite sooner than expected.** 38 spans (0.7%, in three fixtures —
  Energy Trust 17, HACC 18, Maine 3) contain `U+2011` where a reader sees a hyphen. A quote
  *re-typed* from a PDF therefore fails the verbatim rule: `Cloud-based` does not match
  `Cloud‑based`, and the difference is invisible on screen. The lesson is not to relax the rule —
  it is that **quotes must be copied from the index, never retyped**, which is how the extractor is
  expected to behave anyway and how these extractions were authored.
- **A font artefact worth knowing about:** one fixture emits bullet markers as a private-use
  codepoint (`U+F0A7`). It round-trips fine and matches exactly, but it is not a real character, so
  anything that normalises text more aggressively than this module does should be checked against it.

## Limitations

- One engine, one version (`pdftotext 26.10.0`). The text is a function of the engine, which is why
  the version is in every index and checked by `verify`.
- Sentence splitting is heuristic by design. Its failures cost span *granularity*, never correctness:
  a citation is verified against the text, not against the splitter's opinion.
- Extraction is text-only. A requirement that exists only as a scanned image or a table cell with no
  text layer would be invisible here; these eleven fixtures all have real text layers, verified at
  retrieval.
