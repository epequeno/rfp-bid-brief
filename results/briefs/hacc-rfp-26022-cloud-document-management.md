# Cloud-based document management and workflow automation

**Corpus Christi Housing Authority** · recommendation: **NO-BID**

Primary reason class: **Buying a product, not services**

> deterministic verdict: this layer emits a verdict, not a probability — the probability channel, the pre-registered operating point and the census are under Decision below
> profile eap-software-narrow-2026-10-11 — 1 exclusion(s) matched, 0 requirement(s) considered and not excluded

## Decision

**Probability channel** `typesafe/jev-1.13` (resolved `typesafe/jev-1.13-20260917`, served by TypeSafe): **P(bid) = 0.0700** → NO-BID at the pre-registered operating point τ = 0.50.

**Comparator** `microsoft/microsoft-decision-1` (resolved `microsoft/microsoft-decision-1-20261009`, served by Azure): P(bid) = 0.0421 → NO-BID.

**Census of 14 served decision models on this fixture: 0 bid, 14 no-bid** (probabilities 0.000–0.235).

Every model in the census read this solicitation the same way.

The deterministic rules layer above reaches the **same** call as the channel.

_Caveat that travels with the number: 11 fixtures, 4 of them bid, and one call per (model, fixture). Per-model calibration and the Brier scores are in `results/calibration.json`._

## Why not

**1. Buying a product, not services** — the issuer is buying a product and the services are incidental.

- the profile excludes *supplying a hosted product*
- the fixture says "SaaS solution only" (page 4, span `p4-s6`)

## Extracted facts

| field | value | source |
|---|---|---|
| issuer | Corpus Christi Housing Authority | p1 `p1-s0` |
| subject | Cloud-based document management and workflow automation | p1 `p1-s0` |

## Citations

- "CORPUS CHRISTI HOUSING AUTHORITY" (page 1, span `p1-s0`)
- "CLOUD-BASED DOCUMENT MANAGEMENT & WORKFLOW AUTOMATION" (page 1, span `p1-s0`)
- "SaaS solution only" (page 4, span `p4-s6`)
- "configuration, implementation services, data migration, training" (page 3, span `p3-s22`)
- "fully managed hosting, updates, scaling, monitoring" (page 4, span `p4-s7`)
- "CLOUD-BASED DOCUMENT MANAGEMENT" (page 1, span `p1-s0`)

---
_Every quote above was located in `hacc-rfp-26022-cloud-document-management.pdf` at build time under the verbatim rule (whitespace-insensitive, word-boundary-aligned, everything else exact). A quote that does not resolve fails the build rather than reaching a reader. Fixture sha256 `2a8d205e58488f29…`, span index built with pdftotext version 26.10.0._
