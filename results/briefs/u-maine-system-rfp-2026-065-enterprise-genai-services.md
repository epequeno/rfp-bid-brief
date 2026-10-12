# Enterprise generative AI services

**University of Maine System** · recommendation: **NO-BID**

Primary reason class: **Buying a product, not services**

> deterministic verdict: this layer emits a verdict, not a probability — the probability channel, the pre-registered operating point and the census are under Decision below
> profile eap-software-narrow-2026-10-11-r2 — 1 exclusion(s) matched, 0 requirement(s) considered and not excluded

## Decision

**Probability channel** `typesafe/jev-1.13` (resolved `typesafe/jev-1.13-20260917`, served by TypeSafe): **P(bid) = 0.0800** → NO-BID at the pre-registered operating point τ = 0.50.

**Comparator** `microsoft/microsoft-decision-1` (resolved `microsoft/microsoft-decision-1-20261009`, served by Azure): P(bid) = 0.0180 → NO-BID.

**Census of 13 served decision models on this fixture: 0 bid, 13 no-bid** (probabilities 0.000–0.080).

Every model in the census read this solicitation the same way.

The deterministic rules layer above reaches the **same** call as the channel.

_Caveat that travels with the number: 18 fixtures, 6 of them bid, one call per (model, fixture). Repeats move individual probabilities by up to 0.45; this page's structure was unchanged across four runs (`results/census-repeats/README.md`). Per-model calibration and Brier scores: `results/calibration.json`._

## Why not

**1. Buying a product, not services** — the issuer is buying a product and the services are incidental.

- the profile excludes *supplying a hosted product*
- the fixture says "seeking a vendor-hosted SaaS solution" (page 5, span `p5-s29`)
- the fixture says "vendor-hosted SaaS solution" (page 5, span `p5-s29`)

## Extracted facts

| field | value | source |
|---|---|---|
| issuer | University of Maine System | p5 `p5-s14` |
| subject | Enterprise generative AI services | p1 `p1-s0` |

## Citations

- "University of Maine System" (page 5, span `p5-s14`)
- "Enterprise Generative AI Services" (page 1, span `p1-s0`)
- "seeking a vendor-hosted SaaS solution" (page 5, span `p5-s29`)
- "vendor-hosted SaaS solution" (page 5, span `p5-s29`)
- "unlimited access or predictable" (page 4, span `p4-s29`)
- "requesting licenses for a cloud solution" (page 3, span `p3-s22`)

---
_Every quote above was located in `u-maine-system-rfp-2026-065-enterprise-genai-services.pdf` at build time under the verbatim rule (whitespace-insensitive, word-boundary-aligned, everything else exact). A quote that does not resolve fails the build rather than reaching a reader. Fixture sha256 `42d5c1c1581e8da0…`, span index built with pdftotext version 26.10.0._
