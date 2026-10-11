# 0012 — The fifth exclusion class, and the re-freeze it forces

- **Status:** accepted (2026-10-11)
- **Date:** 2026-10-11

## Context

Fixture sourcing round 3 produced two documents that turn on **eligibility rather than capability**. One
requires *"at least five (5) successful Texas K-12 implementations"*. Another is open only to
*"those Consultants awarded a Tier 1 Statewide Contract No. 08215 for Category 8 – Database Services"*.
Neither is a judgment about whether the work suits the firm: **the firm cannot bid at all.**

The profile had four exclusion classes — geography, product-not-services, functional-stack-not-held,
operations-not-projects — and no way to express that. Every one of them describes work the firm would
*decline*; none describes work the firm cannot *reach*. The gap was already visible in round 2, which
rejected the second document partly for the balance reason and quietly because the class did not exist.

## Decision

1. **`not_qualified` becomes the fifth exclusion class**: a minimum track record, contract vehicle,
   credential or clearance makes the firm ineligible before capability is assessed — *unreachable
   rather than unsuitable*.
2. **The profile carries the comparison basis** rather than only the rule: an `experience` block (3–5
   comparable engagements, no K-12 or public-sector ERP implementations, no contract vehicles, no partner
   authorisations) so a requirement can be tested against the firm's actual record, plus an
   `excluded_eligibility_gates` list of gate shapes.
3. **Because the profile changed, this is a re-freeze under ADR 0002.** New profile sha256
   `792024998f3d435f8913e06cb6382a39e0f74d9dac0c13ce7c52f8a578915de8`, recorded in
   `fixtures/labels.json` under `refrozen`, with the old hash preserved beside it.
4. **Every existing label was re-checked against the new class before the re-freeze was recorded.** All
   eleven fixtures were searched for minimum-experience, contract-vehicle, credential and eligibility
   phrasings. **Zero matches**, so no existing label changes and the pre-registered τ = 0.50 stands. The
   check is recorded as a pattern search, not an exhaustive reading, because that is what it was.
5. **Labels for the admitted fixtures are authored before any model sees them** — the ADR 0003 order is
   unchanged.

## Consequences

**Everything measured so far was measured under profile v1, and that is now visible in the artifacts.**
The census state includes the profile, so every archived census and every calibration figure carries
`state_sha256` for the v1 profile. Those results remain valid *for v1* and are not deleted — but they are
not results for the current profile. The census must be re-run once the new labels land, and
`results/calibration.json` will be regenerated from that run. The archive exists precisely so this can be
said out loud instead of silently overwriting history.

**Seven fixtures were admitted in the same change**, taking the set to eighteen: IRCDUS utilities master
plan, Allentown SD data warehousing, a Texas ISD data-warehouse software procurement, Kansas City Kansas
CC data platform, College of Western Idaho AI services, Judicial Council of California staff
augmentation, and SAVEC Alaska managed IT. Span indexes are built and reproducible (8,497 spans across
18 fixtures, up from 5,706 across 11). Labels and hand-authored extractions are still outstanding, and
nothing has been run against a model.

**The new class is expressible but currently unexercised.** A closer read of the Texas document showed it
is *"Enterprise Data Warehouse and Performance Management **Software** and Related Items"* — a product
purchase whose primary reason class is `product_not_services`, with the experience requirement secondary.
So of the admitted fixtures, none triggers `not_qualified` as its primary reason. The class is recorded as
unexercised rather than presented as covered; if a fixture that triggers it is wanted, the Washington
statewide-contract solicitation from round 2 is the candidate, and admitting it is a separate decision.

**One admitted fixture is a genuine test of the extractor's floor.** `savec-alaska-managed-it-services-2026`
is five pages with 103 spans — thinner than the previous thinnest fixture. If the pipeline cannot extract
a defensible set of facts from a document that short, that is worth knowing.
