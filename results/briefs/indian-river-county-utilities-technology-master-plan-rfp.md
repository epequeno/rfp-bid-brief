# Utilities Technology Master Plan (UTMP) and Customer Information System (CIS) consulting services

**Indian River County (IRC)** · recommendation: **BID**

Primary reason class: **In scope**

> deterministic verdict: this layer emits a verdict, not a probability — the probability channel, the pre-registered operating point and the census are under Decision below
> profile eap-software-narrow-2026-10-11-r2 — 0 exclusion(s) matched, 0 requirement(s) considered and not excluded
> no exclusion in the profile is triggered by this solicitation

## Decision

**Probability channel** `typesafe/jev-1.13` (resolved `typesafe/jev-1.13-20260917`, served by TypeSafe): **P(bid) = 0.7400** → BID at the pre-registered operating point τ = 0.50.

**Comparator** `microsoft/microsoft-decision-1` (resolved `microsoft/microsoft-decision-1-20261009`, served by Azure): P(bid) = 0.9841 → BID.

**Census of 14 served decision models on this fixture: 14 bid, 0 no-bid** (probabilities 0.573–0.998).

Every model in the census read this solicitation the same way.

The deterministic rules layer above reaches the **same** call as the channel.

_Caveat that travels with the number: 18 fixtures, 6 of them bid, one call per (model, fixture). Repeats move individual probabilities by up to 0.45; this page's structure was unchanged across four runs (`results/census-repeats/README.md`). Per-model calibration and Brier scores: `results/calibration.json`._

## Why

No exclusion in the bidder profile is triggered by this solicitation.
## Extracted facts

| field | value | source |
|---|---|---|
| issuer | Indian River County (IRC) | p2 `p2-s0` |
| subject | Utilities Technology Master Plan (UTMP) and Customer Information System (CIS) consulting services | p2 `p2-s0` |

## Citations

- "Indian River County (IRC) is located in the southeastern and east-central portions of Florida" (page 2, span `p2-s0`)
- "RFP 2026003 For UTMP CIS Consulting Services" (page 2, span `p2-s0`)
- "The Scope of Services for the UTMP includes a comprehensive review of IRCDUS’s existing business processes" (page 2, span `p2-s23`)
- "objective and vendor-neutral perspectives, as well as exercise discretion and confidentiality during the CIS evaluation and selection process." (page 3, span `p3-s13`)
- "by phases and tasks, including deliverables" (page 9, span `p9-s16`)
- "workplan by phases and tasks, including deliverables, for both the UTMP development and CIS selection." (page 9, span `p9-s16`)
- "vendor-neutral perspectives, as well as exercise discretion and confidentiality during the CIS evaluation and selection process." (page 3, span `p3-s13`)
- "Demonstrate that the personnel as a team or individually have successfully completed services like those specified in the scope of services within this RFP" (page 9, span `p9-s11`)

---
_Every quote above was located in `indian-river-county-utilities-technology-master-plan-rfp.pdf` at build time under the verbatim rule (whitespace-insensitive, word-boundary-aligned, everything else exact). A quote that does not resolve fails the build rather than reaching a reader. Fixture sha256 `fda10cb752e7b189…`, span index built with pdftotext version 26.10.0._
