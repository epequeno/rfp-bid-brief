# Information systems consultant

**Community Action Partnership of Kern** · recommendation: **BID**

Primary reason class: **In scope**

> deterministic verdict: this layer emits a verdict, not a probability — the probability channel, the pre-registered operating point and the census are under Decision below
> profile eap-software-narrow-2026-10-11-r2 — 0 exclusion(s) matched, 0 requirement(s) considered and not excluded
> no exclusion in the profile is triggered by this solicitation

## Decision

**Probability channel** `typesafe/jev-1.13` (resolved `typesafe/jev-1.13-20260917`, served by TypeSafe): **P(bid) = 0.8100** → BID at the pre-registered operating point τ = 0.50.

**Comparator** `microsoft/microsoft-decision-1` (resolved `microsoft/microsoft-decision-1-20261009`, served by Azure): P(bid) = 0.9627 → BID.

**Census of 14 served decision models on this fixture: 14 bid, 0 no-bid** (probabilities 0.810–0.998).

Every model in the census read this solicitation the same way.

The deterministic rules layer above reaches the **same** call as the channel.

_Caveat that travels with the number: 18 fixtures, 6 of them bid, one call per (model, fixture). Repeats move individual probabilities by up to 0.45; this page's structure was unchanged across four runs (`results/census-repeats/README.md`). Per-model calibration and Brier scores: `results/calibration.json`._

## Why

No exclusion in the bidder profile is triggered by this solicitation.
## Extracted facts

| field | value | source |
|---|---|---|
| issuer | Community Action Partnership of Kern | p1 `p1-s0` |
| subject | Information systems consultant | p1 `p1-s0` |

## Citations

- "Community Action Partnership of Kern" (page 1, span `p1-s0`)
- "INFORMATION SYSTEMS CONSULTANT" (page 1, span `p1-s0`)
- "The engagement will include advisory, implementation, and knowledge transfer" (page 4, span `p4-s5`)
- "Develop a migration plan and data model for the 211 call center" (page 4, span `p4-s36`)
- "Develop a migration plan and data model" (page 4, span `p4-s36`)

---
_Every quote above was located in `community-action-partnership-kern-information-systems-consultant.pdf` at build time under the verbatim rule (whitespace-insensitive, word-boundary-aligned, everything else exact). A quote that does not resolve fails the build rather than reaching a reader. Fixture sha256 `373bc828a399a2e7…`, span index built with pdftotext version 26.10.0._
