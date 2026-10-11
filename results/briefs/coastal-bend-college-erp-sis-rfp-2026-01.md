# Enterprise resource planning and student information systems

**Coastal Bend College** · recommendation: **NO-BID**

Primary reason class: **Functional stack not held**

> deterministic verdict: this layer emits a verdict, not a probability — the probability channel, the pre-registered operating point and the census are under Decision below
> profile eap-software-narrow-2026-10-11 — 1 exclusion(s) matched, 0 requirement(s) considered and not excluded

## Decision

**Probability channel** `typesafe/jev-1.13` (resolved `typesafe/jev-1.13-20260917`, served by TypeSafe): **P(bid) = 0.0700** → NO-BID at the pre-registered operating point τ = 0.50.

**Comparator** `microsoft/microsoft-decision-1` (resolved `microsoft/microsoft-decision-1-20261009`, served by Azure): P(bid) = 0.0373 → NO-BID.

**Census of 14 served decision models on this fixture: 0 bid, 14 no-bid** (probabilities 0.000–0.148).

Every model in the census read this solicitation the same way.

The deterministic rules layer above reaches the **same** call as the channel.

_Caveat that travels with the number: 11 fixtures, 4 of them bid, one call per (model, fixture). Repeats move individual probabilities by up to 0.45; this page's structure was unchanged across four runs (`results/census-repeats/README.md`). Per-model calibration and Brier scores: `results/calibration.json`._

## Why not

**1. Functional stack not held** — the engagement is a functional implementation of ERP or student systems.

- the profile excludes *ERP and student information system functional implementation*
- the fixture says "experience and ability to provide Enterprise Resource Planning" (page 18, span `p18-s11`)

## Extracted facts

| field | value | source |
|---|---|---|
| issuer | Coastal Bend College | p1 `p1-s0` |
| subject | Enterprise resource planning and student information systems | p1 `p1-s0` |

## Citations

- "Coastal Bend College" (page 1, span `p1-s0`)
- "Enterprise Resource Planning and Student Information Systems" (page 1, span `p1-s0`)
- "experience and ability to provide Enterprise Resource Planning" (page 18, span `p18-s11`)
- "The Services are more specifically described in Section 5.4" (page 4, span `p4-s5`)

---
_Every quote above was located in `coastal-bend-college-erp-sis-rfp-2026-01.pdf` at build time under the verbatim rule (whitespace-insensitive, word-boundary-aligned, everything else exact). A quote that does not resolve fails the build rather than reaching a reader. Fixture sha256 `c327a9cd4c22b001…`, span index built with pdftotext version 26.10.0._
