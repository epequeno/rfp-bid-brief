# Enterprise data warehousing services

**Allentown School District (ASD)** · recommendation: **BID**

Primary reason class: **In scope**

> deterministic verdict: this layer emits a verdict, not a probability — the probability channel, the pre-registered operating point and the census are under Decision below
> profile eap-software-narrow-2026-10-11-r2 — 0 exclusion(s) matched, 0 requirement(s) considered and not excluded
> no exclusion in the profile is triggered by this solicitation

## Decision

**Probability channel** `typesafe/jev-1.13` (resolved `typesafe/jev-1.13-20260917`, served by TypeSafe): **P(bid) = 0.6700** → BID at the pre-registered operating point τ = 0.50.

**Comparator** `microsoft/microsoft-decision-1` (resolved `microsoft/microsoft-decision-1-20261009`, served by Azure): P(bid) = 0.8176 → BID.

**Census of 14 served decision models on this fixture: 11 bid, 3 no-bid** (probabilities 0.129–1.000).

**The models disagree with each other here.** That makes this call close however it is labelled — a recommendation is not the same thing as a settled question — and it marks this fixture as the one to re-read first.

The deterministic rules layer above reaches the **same** call as the channel.

_Caveat that travels with the number: 18 fixtures, 6 of them bid, one call per (model, fixture). Repeats move individual probabilities by up to 0.45 and this fixture's bid count between 6 and 7, so read the count above as one draw (`results/census-repeats/README.md`). Per-model calibration and Brier scores: `results/calibration.json`._

## Why

No exclusion in the bidder profile is triggered by this solicitation.
## Extracted facts

| field | value | source |
|---|---|---|
| issuer | Allentown School District (ASD) | p3 `p3-s1` |
| subject | Enterprise data warehousing services | p3 `p3-s1` |

## Citations

- "The Allentown School District (ASD) invites proposals" (page 3, span `p3-s1`)
- "provide enterprise Data Warehousing Services that support both instructional improvement and districtwide operational effectiveness" (page 3, span `p3-s1`)
- "The selected vendor shall be responsible for providing the deliverables identified below." (page 6, span `p6-s3`)
- "procure comprehensive data warehousing services from a single vendor" (page 3, span `p3-s9`)
- "pricing includes all labor, materials, travel, and overhead unless otherwise stated." (page 8, span `p8-s19`)
- "labor, materials, travel, and overhead unless otherwise stated." (page 8, span `p8-s19`)
- "comprehensive data warehousing services from a single vendor capable of supporting both instructional and operational data needs." (page 3, span `p3-s9`)
- "at least three (3) comparable engagements, preferably for public school districts or similar public entities." (page 7, span `p7-s13`)

---
_Every quote above was located in `allentown-school-district-data-warehousing-services-2026.pdf` at build time under the verbatim rule (whitespace-insensitive, word-boundary-aligned, everything else exact). A quote that does not resolve fails the build rather than reaching a reader. Fixture sha256 `87aa0da0ac74c581…`, span index built with pdftotext version 26.10.0._
