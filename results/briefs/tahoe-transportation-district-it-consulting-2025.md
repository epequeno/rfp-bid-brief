# Information technology consulting and support

**Tahoe Transportation District** · recommendation: **NO-BID**

Primary reason class: **Geography**

> deterministic verdict: this layer emits a verdict, not a probability — the probability channel, the pre-registered operating point and the census are under Decision below
> profile eap-software-narrow-2026-10-11-r2 — 3 exclusion(s) matched, 0 requirement(s) considered and not excluded

## Decision

**Probability channel** `typesafe/jev-1.13` (resolved `typesafe/jev-1.13-20260917`, served by TypeSafe): **P(bid) = 0.0600** → NO-BID at the pre-registered operating point τ = 0.50.

**Comparator** `microsoft/microsoft-decision-1` (resolved `microsoft/microsoft-decision-1-20261009`, served by Azure): P(bid) = 0.0036 → NO-BID.

**Census of 14 served decision models on this fixture: 0 bid, 14 no-bid** (probabilities 0.000–0.098).

Every model in the census read this solicitation the same way.

The deterministic rules layer above reaches the **same** call as the channel.

_Caveat that travels with the number: 18 fixtures, 6 of them bid, one call per (model, fixture). Repeats move individual probabilities by up to 0.45; this page's structure was unchanged across four runs (`results/census-repeats/README.md`). Per-model calibration and Brier scores: `results/calibration.json`._

## Why not

**1. Geography** — winning requires a standing on-site presence the firm cannot commit to.

- the profile excludes *regular on-site staffing*
- the fixture says "plan on two (2) days per week for on-site support" (page 7, span `p7-s14`)
- the fixture says "14 hours of on-site support" (page 8, span `p8-s1`)

**2. Geography** — winning requires an emergency on-site response, which is a geographic commitment.

- the profile excludes *emergency on-site response commitment*
- the fixture says "be on-site within four (4) hours" (page 7, span `p7-s11`)

**3. Operations, not a project** — the work is continuous operations rather than a project with an end.

- the profile excludes *24×7 monitoring*
- the fixture says "20 hours of IT support" (page 8, span `p8-s1`)
- the fixture says "On-site service support for TTD Board and Committee meetings." (page 8, span `p8-s4`)

## Extracted facts

| field | value | source |
|---|---|---|
| issuer | Tahoe Transportation District | p1 `p1-s0` |
| subject | Information technology consulting and support | p1 `p1-s0` |
| issued | July 28, 2025 | p1 `p1-s0` |
| term | Two years, with three one-year options at the District's discretion | p13 `p13-s12` |
| staffing_model | About 20 hours per week, 14 of them on site, plus emergency and board-meeting attendance | p8 `p8-s1` |

## Citations

- "Tahoe Transportation District" (page 1, span `p1-s0`)
- "INFORMATION TECHNOLOGY CONSULTING AND SUPPORT" (page 1, span `p1-s0`)
- "July 28, 2025" (page 1, span `p1-s0`)
- "the Term of this Agreement is for two (2) years, with three (3) one (1) year options, which may be exercised at the sole discretion of the District." (page 13, span `p13-s12`)
- "20 hours of IT support (14 hours of on-site support and 6 hours of remote support)." (page 8, span `p8-s1`)
- "plan on two (2) days per week for on-site support" (page 7, span `p7-s14`)
- "14 hours of on-site support" (page 8, span `p8-s1`)
- "be on-site within four (4) hours" (page 7, span `p7-s11`)
- "20 hours of IT support" (page 8, span `p8-s1`)
- "On-site service support for TTD Board and Committee meetings." (page 8, span `p8-s4`)

---
_Every quote above was located in `tahoe-transportation-district-it-consulting-2025.pdf` at build time under the verbatim rule (whitespace-insensitive, word-boundary-aligned, everything else exact). A quote that does not resolve fails the build rather than reaching a reader. Fixture sha256 `69633f114695bcd9…`, span index built with pdftotext version 26.10.0._
