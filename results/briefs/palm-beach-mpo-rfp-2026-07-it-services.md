# IT services and management

**Palm Beach Metropolitan Planning Organization** · recommendation: **NO-BID**

Primary reason class: **Geography**

> deterministic verdict: this layer emits a verdict, not a probability — the probability channel, the pre-registered operating point and the census are under Decision below
> profile eap-software-narrow-2026-10-11 — 2 exclusion(s) matched, 0 requirement(s) considered and not excluded

## Decision

**Probability channel** `typesafe/jev-1.13` (resolved `typesafe/jev-1.13-20260917`, served by TypeSafe): **P(bid) = 0.0600** → NO-BID at the pre-registered operating point τ = 0.50.

**Comparator** `microsoft/microsoft-decision-1` (resolved `microsoft/microsoft-decision-1-20261009`, served by Azure): P(bid) = 0.0097 → NO-BID.

**Census of 14 served decision models on this fixture: 0 bid, 14 no-bid** (probabilities 0.000–0.085).

Every model in the census read this solicitation the same way.

The deterministic rules layer above reaches the **same** call as the channel.

_Caveat that travels with the number: 11 fixtures, 4 of them bid, one call per (model, fixture). Repeats move individual probabilities by up to 0.45; this page's structure was unchanged across four runs (`results/census-repeats/README.md`). Per-model calibration and Brier scores: `results/calibration.json`._

## Why not

**1. Geography** — winning requires a standing on-site presence the firm cannot commit to.

- the profile excludes *regular on-site staffing*
- the fixture says "including on-site support" (page 3, span `p3-s4`)

**2. Operations, not a project** — the work is continuous operations rather than a project with an end.

- the profile excludes *24×7 monitoring*
- the fixture says "Information Technology Services and Management" (page 1, span `p1-s0`)

## Extracted facts

| field | value | source |
|---|---|---|
| issuer | Palm Beach Metropolitan Planning Organization | p1 `p1-s0` |
| subject | IT services and management | p1 `p1-s0` |

## Citations

- "Palm Beach Metropolitan Planning Organization" (page 1, span `p1-s0`)
- "Information Technology Services and Management" (page 1, span `p1-s0`)
- "including on-site support" (page 3, span `p3-s4`)
- "period of three (3) years" (page 3, span `p3-s6`)

---
_Every quote above was located in `palm-beach-mpo-rfp-2026-07-it-services.pdf` at build time under the verbatim rule (whitespace-insensitive, word-boundary-aligned, everything else exact). A quote that does not resolve fails the build rather than reaching a reader. Fixture sha256 `ff7a200c37a8306d…`, span index built with pdftotext version 26.10.0._
