# Enterprise data warehouse and performance management software

**Cleveland Independent School District (Cleveland ISD), Texas** · recommendation: **NO-BID**

Primary reason class: **not_qualified**

> deterministic verdict: this layer emits a verdict, not a probability — the probability channel, the pre-registered operating point and the census are under Decision below
> profile eap-software-narrow-2026-10-11-r2 — 2 exclusion(s) matched, 0 requirement(s) considered and not excluded

## Decision

**Probability channel** `typesafe/jev-1.13` (resolved `typesafe/jev-1.13-20260917`, served by TypeSafe): **P(bid) = 0.0500** → NO-BID at the pre-registered operating point τ = 0.50.

**Comparator** `microsoft/microsoft-decision-1` (resolved `microsoft/microsoft-decision-1-20261009`, served by Azure): P(bid) = 0.0059 → NO-BID.

**Census of 14 served decision models on this fixture: 0 bid, 14 no-bid** (probabilities 0.000–0.125).

Every model in the census read this solicitation the same way.

The deterministic rules layer above reaches the **same** call as the channel.

_Caveat that travels with the number: 18 fixtures, 6 of them bid, one call per (model, fixture). Repeats move individual probabilities by up to 0.45; this page's structure was unchanged across four runs (`results/census-repeats/README.md`). Per-model calibration and Brier scores: `results/calibration.json`._

## Why not

**1. not_qualified** — the issuer requires more prior comparable implementations than the firm can show, which is a qualification rather than a score — the firm is ineligible before capability is assessed.

- the profile excludes *a minimum number of prior comparable implementations the firm does not have*
- the fixture says "At least five (5) successful Texas K-12 implementations ● Existing Texas-based references from similarly sized school districts ● An established educational analytics and dashboarding platform currently in production use within K-12" (page 4, span `p4-s4`)

**2. Buying a product, not services** — the issuer is buying a product and the services are incidental.

- the profile excludes *supplying a hosted product*
- the fixture says "Enterprise Data Warehouse and Performance Management Software and Related Items RFP #26-10 Completed proposals for RFP #26-08 for an Enterprise Data Warehouse and Performance Management Software and Related Items must be received on or before 10:00 AM June 8, 2026." (page 1, span `p1-s0`)

## Extracted facts

| field | value | source |
|---|---|---|
| issuer | Cleveland Independent School District (Cleveland ISD), Texas | p1 `p1-s12` |
| subject | Enterprise data warehouse and performance management software | p1 `p1-s0` |

## Citations

- "Cleveland Independent School District Attn: Alfonso Saldivar 1901 E." (page 1, span `p1-s12`)
- "Enterprise Data Warehouse and Performance Management Software and Related Items RFP #26-10 Completed proposals for RFP #26-08 for an Enterprise Data Warehouse and Performance Management Software and Related Items must be received on or before 10:00 AM June 8, 2026." (page 1, span `p1-s0`)
- "The term of this contract will be for one (1) year with four (4) additional one (1) year optional renewals." (page 3, span `p3-s2`)
- "Software and Related Items RFP #26-10 Completed proposals for RFP #26-08 for an Enterprise Data Warehouse and Performance Management Software and Related Items must be received on or before 10:00 AM June 8, 2026." (page 1, span `p1-s0`)
- "Performance Management Software and Related Items RFP #26-10 Completed proposals for RFP #26-08 for an Enterprise Data Warehouse and Performance Management Software and Related Items must be received on or before 10:00 AM June 8, 2026." (page 1, span `p1-s0`)
- "At least five (5) successful Texas K-12 implementations ● Existing Texas-based references from similarly sized school districts ● An established educational analytics and dashboarding platform currently in production use within K-12" (page 4, span `p4-s4`)

---
_Every quote above was located in `cisd-texas-rfp-26-10-enterprise-data-warehouse-software.pdf` at build time under the verbatim rule (whitespace-insensitive, word-boundary-aligned, everything else exact). A quote that does not resolve fails the build rather than reaching a reader. Fixture sha256 `7a0a2b2e4317583c…`, span index built with pdftotext version 26.10.0._
