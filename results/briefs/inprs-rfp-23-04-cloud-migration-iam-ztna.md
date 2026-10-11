# Cloud migration discovery, IAM and zero-trust strategy

**Indiana Public Retirement System** · recommendation: **BID**

Primary reason class: **In scope**

> deterministic verdict: this layer emits a verdict, not a probability — the probability channel, the pre-registered operating point and the census are under Decision below
> profile eap-software-narrow-2026-10-11 — 0 exclusion(s) matched, 0 requirement(s) considered and not excluded
> no exclusion in the profile is triggered by this solicitation

## Decision

**Probability channel** `typesafe/jev-1.13` (resolved `typesafe/jev-1.13-20260917`, served by TypeSafe): **P(bid) = 0.7900** → BID at the pre-registered operating point τ = 0.50.

**Comparator** `microsoft/microsoft-decision-1` (resolved `microsoft/microsoft-decision-1-20261009`, served by Azure): P(bid) = 0.9466 → BID.

**Census of 14 served decision models on this fixture: 14 bid, 0 no-bid** (probabilities 0.679–1.000).

Every model in the census read this solicitation the same way.

The deterministic rules layer above reaches the **same** call as the channel.

_Caveat that travels with the number: 11 fixtures, 4 of them bid, one call per (model, fixture). Repeats move individual probabilities by up to 0.45; this page's structure was unchanged across four runs (`results/census-repeats/README.md`). Per-model calibration and Brier scores: `results/calibration.json`._

## Why

No exclusion in the bidder profile is triggered by this solicitation.
## Extracted facts

| field | value | source |
|---|---|---|
| issuer | Indiana Public Retirement System | p3 `p3-s1` |
| subject | Cloud migration discovery, IAM and zero-trust strategy | p1 `p1-s0` |

## Citations

- "Indiana Public Retirement System" (page 3, span `p3-s1`)
- "CLOUD MIGRATION DISCOVERY AND STRATEGY SERVICES" (page 1, span `p1-s0`)
- "consulting services" (page 3, span `p3-s1`)
- "travel to the INPRS offices" (page 17, span `p17-s24`)

---
_Every quote above was located in `inprs-rfp-23-04-cloud-migration-iam-ztna.pdf` at build time under the verbatim rule (whitespace-insensitive, word-boundary-aligned, everything else exact). A quote that does not resolve fails the build rather than reaching a reader. Fixture sha256 `1ba14c71c5bbdd3f…`, span index built with pdftotext version 26.10.0._
