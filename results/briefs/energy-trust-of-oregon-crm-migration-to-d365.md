# On-premises CRM to Microsoft Dynamics 365 cloud

**Energy Trust of Oregon** · recommendation: **NO-BID**

Primary reason class: **Functional stack not held**

> deterministic verdict: this layer emits a verdict, not a probability — the probability channel, the pre-registered operating point and the census are under Decision below
> profile eap-software-narrow-2026-10-11-r2 — 1 exclusion(s) matched, 0 requirement(s) considered and not excluded

## Decision

**Probability channel** `typesafe/jev-1.13` (resolved `typesafe/jev-1.13-20260917`, served by TypeSafe): **P(bid) = 0.1600** → NO-BID at the pre-registered operating point τ = 0.50.

**Comparator** `microsoft/microsoft-decision-1` (resolved `microsoft/microsoft-decision-1-20261009`, served by Azure): P(bid) = 0.5312 → BID.

**Census of 14 served decision models on this fixture: 4 bid, 10 no-bid** (probabilities 0.005–0.651).

**The models disagree with each other here.** That makes this call close however it is labelled — a recommendation is not the same thing as a settled question — and it marks this fixture as the one to re-read first.

The deterministic rules layer above reaches the **same** call as the channel.

_Caveat that travels with the number: 18 fixtures, 6 of them bid, one call per (model, fixture). Repeats move individual probabilities by up to 0.45 and this fixture's bid count between 6 and 7, so read the count above as one draw (`results/census-repeats/README.md`). Per-model calibration and Brier scores: `results/calibration.json`._

## Why not

**1. Functional stack not held** — the engagement is functional configuration of Microsoft Dynamics, a stack the profile does not hold — the profile's own escape clause, platform engineering underneath it, does not apply.

- the profile excludes *vendor-specific functional stack the firm does not hold*
- the fixture says "Recommended Dynamics 365 applications and licensing" (page 2, span `p2-s8`)

## Extracted facts

| field | value | source |
|---|---|---|
| issuer | Energy Trust of Oregon | p1 `p1-s1` |
| subject | On-premises CRM to Microsoft Dynamics 365 cloud | p1 `p1-s0` |

## Citations

- "Energy Trust of Oregon" (page 1, span `p1-s1`)
- "Migration from On-Premises Microsoft CRM to Microsoft Dynamics" (page 1, span `p1-s0`)
- "Recommended Dynamics 365 applications and licensing" (page 2, span `p2-s8`)
- "The vendor shall define a detailed migration strategy and target" (page 2, span `p2-s8`)
- "The vendor shall partner with internal product owner" (page 3, span `p3-s3`)
- "The vendor shall conduct a comprehensive assessment" (page 2, span `p2-s4`)

---
_Every quote above was located in `energy-trust-of-oregon-crm-migration-to-d365.pdf` at build time under the verbatim rule (whitespace-insensitive, word-boundary-aligned, everything else exact). A quote that does not resolve fails the build rather than reaching a reader. Fixture sha256 `9d60913497b84658…`, span index built with pdftotext version 26.10.0._
