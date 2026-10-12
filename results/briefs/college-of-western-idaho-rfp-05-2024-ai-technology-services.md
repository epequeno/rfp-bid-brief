# AI technologies and services for faculty and students

**College of Western Idaho** · recommendation: **NO-BID**

Primary reason class: **Buying a product, not services**

> deterministic verdict: this layer emits a verdict, not a probability — the probability channel, the pre-registered operating point and the census are under Decision below
> profile eap-software-narrow-2026-10-11-r2 — 1 exclusion(s) matched, 0 requirement(s) considered and not excluded

## Decision

**Probability channel** `typesafe/jev-1.13` (resolved `typesafe/jev-1.13-20260917`, served by TypeSafe): **P(bid) = 0.1900** → NO-BID at the pre-registered operating point τ = 0.50.

**Comparator** `microsoft/microsoft-decision-1` (resolved `microsoft/microsoft-decision-1-20261009`, served by Azure): P(bid) = 0.0601 → NO-BID.

**Census of 14 served decision models on this fixture: 1 bid, 13 no-bid** (probabilities 0.000–0.644).

**The models disagree with each other here.** That makes this call close however it is labelled — a recommendation is not the same thing as a settled question — and it marks this fixture as the one to re-read first.

The deterministic rules layer above reaches the **same** call as the channel.

_Caveat that travels with the number: 18 fixtures, 6 of them bid, one call per (model, fixture). Repeats move individual probabilities by up to 0.45 and this fixture's bid count between 6 and 7, so read the count above as one draw (`results/census-repeats/README.md`). Per-model calibration and Brier scores: `results/calibration.json`._

## Why not

**1. Buying a product, not services** — the issuer is buying a product and the services are incidental.

- the profile excludes *supplying a hosted product*
- the fixture says "any licenses, service terms, or other terms supplements the RFP and its Appendices, the supplemental terms and conditions shall apply only if specifically reviewed, approved, and accepted by the College in a written Addendum." (page 10, span `p10-s1`)

## Extracted facts

| field | value | source |
|---|---|---|
| issuer | College of Western Idaho | p4 `p4-s20` |
| subject | AI technologies and services for faculty and students | p3 `p3-s6` |

## Citations

- "College of Western Idaho Attn: Daniel Reines, Procurement Coordinator Re: RFP 05-2024 AI Software 6056 Birch Lane, Nampa, ID 83687 5." (page 4, span `p4-s20`)
- "artificial intelligence (AI) technologies and services that will be accessed and used by faculty and students" (page 3, span `p3-s6`)
- "The purpose of this Request for Proposals (“RFP”) is to solicit proposals for artificial intelligence (AI) technologies and services that will be accessed and used by faculty and students" (page 3, span `p3-s6`)
- "any licenses, service terms, or other terms supplements the RFP and its Appendices, the supplemental terms and conditions shall apply only if specifically reviewed, approved, and accepted by the College in a written Addendum." (page 10, span `p10-s1`)
- "License, service, maintenance, or any other type of agreements desired by the firm to be signed by the College, are only binding upon the College to the extent they are in full agreement with the RFP and have been specifically reviewed, approved, and accepted by the College in writing." (page 10, span `p10-s2`)
- "maintenance, or any other type of agreements desired by the firm to be signed by the College, are only binding upon the College to the extent they are in full agreement with the RFP and have been specifically reviewed, approved, and accepted by the College in writing." (page 10, span `p10-s2`)
- "technologies and services that will be accessed and used by faculty and students in the design, development, and delivery of instruction from qualified entities (“Proposers”)." (page 3, span `p3-s6`)
- "will be accessed and used by faculty and students in the design, development, and delivery of instruction from qualified entities (“Proposers”)." (page 3, span `p3-s6`)

---
_Every quote above was located in `college-of-western-idaho-rfp-05-2024-ai-technology-services.pdf` at build time under the verbatim rule (whitespace-insensitive, word-boundary-aligned, everything else exact). A quote that does not resolve fails the build rather than reaching a reader. Fixture sha256 `40d0d488ccb27b29…`, span index built with pdftotext version 26.10.0._
