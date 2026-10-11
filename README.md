# rfp-bid-brief

**A bid/no-bid brief generator for capture teams — and the evaluation that says how much to trust it.**

Given a solicitation, produce a one-page brief: the recommendation, the typed fields behind it, and
verbatim citations. The point of the repository is not the brief. It is that every claim in the
brief traces to a span of the source document, and that the decision layer's probabilities are
**calibrated and published at an operating point fixed in advance**.

## Status: inputs frozen, pipeline not built

The repository currently contains the **frozen inputs and the conventions**, and no model-facing
code. That ordering is the point — see [`adr/0003`](adr/0003-pre-register-the-operating-point.md):

1. the bidder profile is committed and hashed,
2. the decision threshold and headline metrics are pre-registered,
3. the ground-truth labels are committed,
4. *then* a model sees a fixture.

Recording a threshold after seeing results is not calibration, it is a fitted number.

What exists today:

| Path | What it is |
|---|---|
| `bidder-profile.json` | The narrow profile every decision is made against. Frozen before labelling. |
| `fixtures/` | Eleven public solicitation documents, with provenance, notice and a hash manifest. |
| `fixtures/PROVENANCE.md` | Issuer, source URL, page count, sha256, and what each fixture may be read as. |
| `adr/` | The decisions taken so far. |
| `tools/verify-fixtures.sh` | `make verify-fixtures` — proves the fixtures are still the documents their issuers published. |

## Why a bidder profile is a required input

"Bid" is undefined until the system knows who is bidding. A recommendation is not a property of a
solicitation; it is a property of a solicitation *and* a capability. So the profile is committed,
narrow by design, and states its **exclusions** as clearly as its capabilities — no hosted products
or licences, no 24×7 operations, no staff augmentation, no regular on-site work outside the firm's
metro. Change one line of the profile and the recommendation is expected to move; that is a feature,
and it is testable. See [`adr/0002`](adr/0002-required-bidder-profile.md).

## The span-ID contract

Every extracted field carries the identifier of the span it came from, and a quoted span must exist
**verbatim** in its fixture. This makes hallucinated quotations structurally impossible rather than
reviewed for, which is why the citation-integrity check is a test failure, not a review finding.
See [`adr/0001`](adr/0001-span-id-citations.md).

## How the numbers will be reported

When the harness lands, a number from this repository will always come with:

- the **confusion matrix**, with the class balance stated (the fixture set is skewed toward no-bid,
  which is the honest shape of capture decisions, and it is thin);
- **precision and recall per class**, never a bare F1;
- the **Brier score** and the **calibration curve at the pre-registered operating point** — the
  curve is the claim, not a single accuracy figure;
- the **citation-integrity pass rate**, where a failure is a test failure;
- and the **baseline it must beat**: title-only keyword matching, which is expected to fail on
  fixtures whose titles point the wrong way.

## Fixtures

Eleven public solicitations from eleven independent issuers — municipal, county, community college,
university system, state agency, and two state-chartered non-profits. All are public records,
retrieved from the issuers' own published copies, all with extractable text and no OCR anywhere.

They are third-party documents, reproduced unmodified. Read [`fixtures/NOTICE.md`](fixtures/NOTICE.md)
before redistributing, and [`fixtures/PROVENANCE.md`](fixtures/PROVENANCE.md) for the source of each.

## Not a goal

This repository does not bid on anything, does not claim any relationship with any issuing
organisation, and makes no leaderboard or benchmark claim about any model or framework. The eval
exists to characterise *this* system.

## License

Apache-2.0 — see [`LICENSE`](LICENSE). The fixtures are **not** covered by that licence; they remain
the property of their issuers.
