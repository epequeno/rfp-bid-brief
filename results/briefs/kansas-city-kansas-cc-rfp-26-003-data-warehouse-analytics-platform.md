# Institutional data warehouse and analytics platform

**Kansas City Kansas Community College** · recommendation: **NO-BID**

Primary reason class: **Buying a product, not services**

> deterministic verdict: this layer emits a verdict, not a probability — the probability channel, the pre-registered operating point and the census are under Decision below
> profile eap-software-narrow-2026-10-11-r2 — 1 exclusion(s) matched, 0 requirement(s) considered and not excluded

## Decision

**Probability channel** `typesafe/jev-1.13` (resolved `typesafe/jev-1.13-20260917`, served by TypeSafe): **P(bid) = 0.2600** → NO-BID at the pre-registered operating point τ = 0.50.

**Comparator** `microsoft/microsoft-decision-1` (resolved `microsoft/microsoft-decision-1-20261009`, served by Azure): P(bid) = 0.0601 → NO-BID.

**Census of 14 served decision models on this fixture: 0 bid, 14 no-bid** (probabilities 0.001–0.365).

Every model in the census read this solicitation the same way.

The deterministic rules layer above reaches the **same** call as the channel.

_Caveat that travels with the number: 18 fixtures, 6 of them bid, one call per (model, fixture). Repeats move individual probabilities by up to 0.45; this page's structure was unchanged across four runs (`results/census-repeats/README.md`). Per-model calibration and Brier scores: `results/calibration.json`._

## Why not

**1. Buying a product, not services** — the issuer is buying a product and the services are incidental.

- the profile excludes *supplying a hosted product*
- the fixture says "seeking transparent, pre-delivered analytics that surface historical patterns and leading indicators in an interpretable way, supporting targeted interventions and allowing the college to evaluate impact over time." (page 9, span `p9-s3`)

## Extracted facts

| field | value | source |
|---|---|---|
| issuer | Kansas City Kansas Community College | p3 `p3-s0` |
| subject | Institutional data warehouse and analytics platform | p8 `p8-s12` |

## Citations

- "KANSAS CITY KANSAS COMMUNITY COLLEGE PAGE 4 INSTRUCTIONS FOR SUBMITTING PROPOSAL PAGE 5 SCOPE OF SERVICES / PROPOSAL REQUIREMENTS PAGE 8 GENERAL TERMS AND CONDITIONS PAGE 17 3" (page 3, span `p3-s0`)
- "seeking a platform that improves data utilization across the institution, supporting consistent decision-making and coordinated action across academic, student support, enrollment, and institutional effectiveness functions." (page 8, span `p8-s12`)
- "would be assigned to this project to provide the services described in the Scope of Work, highlighting the primary point of contact for the College." (page 7, span `p7-s10`)
- "seeking transparent, pre-delivered analytics that surface historical patterns and leading indicators in an interpretable way, supporting targeted interventions and allowing the college to evaluate impact over time." (page 9, span `p9-s3`)
- "improves data utilization across the institution, supporting consistent decision-making and coordinated action across academic, student support, enrollment, and institutional effectiveness functions." (page 8, span `p8-s12`)
- "supporting consistent decision-making and coordinated action across academic, student support, enrollment, and institutional effectiveness functions." (page 8, span `p8-s12`)
- "collecting and reporting institutional data, but the college continues to face challenges in translating data into timely," (page 8, span `p8-s0`)
- "Approach to the Scope of Services." (page 6, span `p6-s8`)

---
_Every quote above was located in `kansas-city-kansas-cc-rfp-26-003-data-warehouse-analytics-platform.pdf` at build time under the verbatim rule (whitespace-insensitive, word-boundary-aligned, everything else exact). A quote that does not resolve fails the build rather than reaching a reader. Fixture sha256 `45e485ac4d0cea2d…`, span index built with pdftotext version 26.10.0._
