# Managed IT services: help desk, network administration, on-site support

**Southwest Alaska Vocational & Educational Center (SAVEC)** · recommendation: **NO-BID**

Primary reason class: **Geography**

> deterministic verdict: this layer emits a verdict, not a probability — the probability channel, the pre-registered operating point and the census are under Decision below
> profile eap-software-narrow-2026-10-11-r2 — 2 exclusion(s) matched, 0 requirement(s) considered and not excluded

## Decision

**Probability channel** `typesafe/jev-1.13` (resolved `typesafe/jev-1.13-20260917`, served by TypeSafe): **P(bid) = 0.0500** → NO-BID at the pre-registered operating point τ = 0.50.

**Comparator** `microsoft/microsoft-decision-1` (resolved `microsoft/microsoft-decision-1-20261009`, served by Azure): P(bid) = 0.0032 → NO-BID.

**Census of 14 served decision models on this fixture: 0 bid, 14 no-bid** (probabilities 0.000–0.090).

Every model in the census read this solicitation the same way.

The deterministic rules layer above reaches the **same** call as the channel.

_Caveat that travels with the number: 18 fixtures, 6 of them bid, one call per (model, fixture). Repeats move individual probabilities by up to 0.45; this page's structure was unchanged across four runs (`results/census-repeats/README.md`). Per-model calibration and Brier scores: `results/calibration.json`._

## Why not

**1. Geography** — winning requires a standing on-site presence the firm cannot commit to.

- the profile excludes *regular on-site staffing*
- the fixture says "Hourly On-Site Support $______ Emergency After-Hours Support $______ Travel Rate $______ New Computer Setup $______ New User Setup $______ Additional Workstation (Monthly) $______ Additional User" (page 5, span `p5-s4`)

**2. Operations, not a project** — the work is continuous operations rather than a project with an end.

- the profile excludes *24×7 monitoring*
- the fixture says "Help Desk support (remote and on-site)." (page 2, span `p2-s16`)

## Extracted facts

| field | value | source |
|---|---|---|
| issuer | Southwest Alaska Vocational & Educational Center (SAVEC) | p1 `p1-s5` |
| subject | Managed IT services: help desk, network administration, on-site support | p1 `p1-s5` |

## Citations

- "SAVEC seeks a responsive, proactive technology partner capable of providing remote and on-site support, cybersecurity, network administration, technology planning, user support, and strategic guidance." (page 1, span `p1-s5`)
- "remote and on-site support, cybersecurity, network administration, technology planning, user support, and strategic guidance" (page 1, span `p1-s5`)
- "Help Desk support (remote and on-site)." (page 2, span `p2-s16`)
- "Software licensing recommendations." (page 3, span `p3-s18`)
- "Hourly On-Site Support $______ Emergency After-Hours Support $______ Travel Rate $______ New Computer Setup $______ New User Setup $______ Additional Workstation (Monthly) $______ Additional User" (page 5, span `p5-s4`)
- "Emergency After-Hours Support $______ Travel Rate $______ New Computer Setup $______ New User Setup $______ Additional Workstation (Monthly) $______ Additional User" (page 5, span `p5-s4`)
- "Proof of insurance and business license 10." (page 4, span `p4-s11`)

---
_Every quote above was located in `savec-alaska-managed-it-services-2026.pdf` at build time under the verbatim rule (whitespace-insensitive, word-boundary-aligned, everything else exact). A quote that does not resolve fails the build rather than reaching a reader. Fixture sha256 `e6dfc120042ac98a…`, span index built with pdftotext version 26.10.0._
