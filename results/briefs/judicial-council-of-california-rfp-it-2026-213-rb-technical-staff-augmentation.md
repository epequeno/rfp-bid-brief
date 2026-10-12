# Master agreements for technical staff augmentation services

**Judicial Council of California** · recommendation: **NO-BID**

Primary reason class: **staff_augmentation**

> deterministic verdict: this layer emits a verdict, not a probability — the probability channel, the pre-registered operating point and the census are under Decision below
> profile eap-software-narrow-2026-10-11-r2 — 1 exclusion(s) matched, 0 requirement(s) considered and not excluded

## Decision

**Probability channel** `typesafe/jev-1.13` (resolved `typesafe/jev-1.13-20260917`, served by TypeSafe): **P(bid) = 0.0400** → NO-BID at the pre-registered operating point τ = 0.50.

**Comparator** `microsoft/microsoft-decision-1` (resolved `microsoft/microsoft-decision-1-20261009`, served by Azure): P(bid) = 0.0032 → NO-BID.

**Census of 14 served decision models on this fixture: 0 bid, 14 no-bid** (probabilities 0.000–0.110).

Every model in the census read this solicitation the same way.

The deterministic rules layer above reaches the **same** call as the channel.

_Caveat that travels with the number: 18 fixtures, 6 of them bid, one call per (model, fixture). Repeats move individual probabilities by up to 0.45; this page's structure was unchanged across four runs (`results/census-repeats/README.md`). Per-model calibration and Brier scores: `results/calibration.json`._

## Why not

**1. staff_augmentation** — the issuer is buying hours or bodies under a standing agreement rather than commissioning a delivered project.

- the profile excludes *staff augmentation or body-shop placements*
- the fixture says "MASTER AGREEMENTS FOR TECHNICAL STAFF AUGMENTATION SERVICES RFP NUMBER: RFP-IT-2026-213-RB PROPOSALS DUE: AUGUST 21, 2026 NO LATER THAN 1:00 PM PACIFIC TIME (PT) JBCM RFP IT Goods-Services vJCC – Rev." (page 1, span `p1-s0`)

## Extracted facts

| field | value | source |
|---|---|---|
| issuer | Judicial Council of California | p1 `p1-s0` |
| subject | Master agreements for technical staff augmentation services | p1 `p1-s0` |

## Citations

- "Judicial Council of California REGARDING: MASTER AGREEMENTS FOR TECHNICAL STAFF AUGMENTATION SERVICES RFP NUMBER: RFP-IT-2026-213-RB PROPOSALS DUE: AUGUST 21, 2026 NO LATER THAN 1:00 PM PACIFIC TIME (PT) JBCM RFP IT Goods-Services vJCC – Rev." (page 1, span `p1-s0`)
- "MASTER AGREEMENTS FOR TECHNICAL STAFF AUGMENTATION SERVICES RFP NUMBER: RFP-IT-2026-213-RB PROPOSALS DUE: AUGUST 21, 2026 NO LATER THAN 1:00 PM PACIFIC TIME (PT) JBCM RFP IT Goods-Services vJCC – Rev." (page 1, span `p1-s0`)
- "qualified technical staff augmentation staffing agencies under a number of master agreements to supply the Judicial Council, Supreme Court, and Appellate courts, each a “Participant,” with high-quality, cost-effective," (page 4, span `p4-s9`)
- "number of master agreements to supply the Judicial Council, Supreme Court, and Appellate courts, each a “Participant,” with high-quality, cost-effective," (page 4, span `p4-s9`)
- "under a number of master agreements to supply the Judicial Council, Supreme Court, and Appellate courts, each a “Participant,” with high-quality, cost-effective," (page 4, span `p4-s9`)
- "seeks to identify and retain qualified technical staff augmentation staffing agencies under a number of master agreements to supply the Judicial Council, Supreme Court, and Appellate courts, each a “Participant,” with high-quality, cost-effective," (page 4, span `p4-s9`)

---
_Every quote above was located in `judicial-council-of-california-rfp-it-2026-213-rb-technical-staff-augmentation.pdf` at build time under the verbatim rule (whitespace-insensitive, word-boundary-aligned, everything else exact). A quote that does not resolve fails the build rather than reaching a reader. Fixture sha256 `164170ccea518ed3…`, span index built with pdftotext version 26.10.0._
