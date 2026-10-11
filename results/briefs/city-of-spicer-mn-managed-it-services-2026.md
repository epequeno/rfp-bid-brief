# Managed information technology services

**City of Spicer** · recommendation: **NO-BID**

Primary reason class: **Operations, not a project**

> deterministic verdict: this layer emits a verdict, not a probability — the probability channel, the pre-registered operating point and the census are under Decision below
> profile eap-software-narrow-2026-10-11 — 1 exclusion(s) matched, 0 requirement(s) considered and not excluded

## Decision

**Probability channel** `typesafe/jev-1.13` (resolved `typesafe/jev-1.13-20260917`, served by TypeSafe): **P(bid) = 0.0400** → NO-BID at the pre-registered operating point τ = 0.50.

**Comparator** `microsoft/microsoft-decision-1` (resolved `microsoft/microsoft-decision-1-20261009`, served by Azure): P(bid) = 0.0017 → NO-BID.

**Census of 14 served decision models on this fixture: 0 bid, 14 no-bid** (probabilities 0.000–0.132).

Every model in the census read this solicitation the same way.

The deterministic rules layer above reaches the **same** call as the channel.

_Caveat that travels with the number: 11 fixtures, 4 of them bid, and one call per (model, fixture). Per-model calibration and the Brier scores are in `results/calibration.json`._

## Why not

**1. Operations, not a project** — the work is continuous operations rather than a project with an end.

- the profile excludes *24×7 monitoring*
- the fixture says "24x7x365 monitoring of denoted servers" (page 4, span `p4-s14`)

## Extracted facts

| field | value | source |
|---|---|---|
| issuer | City of Spicer | p1 `p1-s0` |
| subject | Managed information technology services | p1 `p1-s0` |

## Citations

- "City of Spicer" (page 1, span `p1-s0`)
- "Managed Information Technology Services" (page 1, span `p1-s0`)
- "24x7x365 monitoring of denoted servers" (page 4, span `p4-s14`)
- "Full-service operations center service" (page 4, span `p4-s14`)
- "Server and network administration" (page 4, span `p4-s15`)

---
_Every quote above was located in `city-of-spicer-mn-managed-it-services-2026.pdf` at build time under the verbatim rule (whitespace-insensitive, word-boundary-aligned, everything else exact). A quote that does not resolve fails the build rather than reaching a reader. Fixture sha256 `e82998cfbb27674a…`, span index built with pdftotext version 26.10.0._
