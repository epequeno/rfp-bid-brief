# rfp-bid-brief

**A bid/no-bid brief generator for capture teams — and the evaluation that says how much to trust it.**

Given a solicitation, produce a one-page brief: the recommendation, the typed fields behind it, and
verbatim citations. The point of the repository is not the brief. It is that every claim in the
brief traces to a span of the source document, and that the decision layer's probabilities are
**calibrated and published at an operating point fixed in advance**.

## Status: span index built — extraction not started

The repository contains the **frozen inputs, the ground truth, and the first pipeline stage**. That
ordering is the point — see [`adr/0003`](adr/0003-pre-register-the-operating-point.md):

1. the bidder profile is committed and hashed, ✅
2. the decision threshold and headline metrics are pre-registered, ✅
3. the ground-truth labels are committed, ✅
4. `parse` builds a deterministic, citable span index per fixture, ✅
   ([ADR 0004](adr/0004-citations-locate-inside-spans.md))
5. `extract` → `decide` → `brief`, then the eval harness — **not built**.

Recording a threshold after seeing results is not calibration, it is a fitted number.

What exists today:

| Path | What it is |
|---|---|
| `bidder-profile.json` | The narrow profile every decision is made against. Frozen and hashed before labelling. |
| `fixtures/` | Eleven public solicitation documents, with provenance, notice and a hash manifest. |
| `fixtures/labels.json` | Ground truth — 4 bid, 7 no-bid — with the reason for each label. Held out from the model path. |
| `src/rfpbrief/spans.py` | The span index: extraction, normalisation, and the citation rule. The module everything downstream rests on. |
| `results/spans/` | One index per fixture, plus [what the first spike established](results/spans/README.md). |
| `adr/` | The decisions taken so far. |
| `tools/verify-fixtures.sh` | `just verify-fixtures` — proves the fixtures are still the documents their issuers published. |
| `tools/status.sh` | `just status` — what exists, and what explicitly does not. |

```bash
just                    # list the recipes
just check              # fixture hashes, tests, index reproducibility, status
just find "be on-site within four (4) hours"   # locate a quote: one span, or it fails
```

Run `just` for the recipe list; the task runner is [`just`](https://github.com/casey/just), not
`make`.

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

The labels are not a coin flip: the set is deliberately skewed toward no-bid, because that is the
honest shape of capture decisions for a narrow practice, and each no-bid has a *reason class* —
buying a product rather than services, a functional stack the profile does not hold, operations
rather than a project, or geography. Four positives is thin, and the calibration curve will be
reported as indicative rather than conclusive because of it.

They are third-party documents, reproduced unmodified. Read [`fixtures/NOTICE.md`](fixtures/NOTICE.md)
before redistributing, and [`fixtures/PROVENANCE.md`](fixtures/PROVENANCE.md) for the source of each.

## Not a goal

This repository does not bid on anything, does not claim any relationship with any issuing
organisation, and makes no leaderboard or benchmark claim about any model or framework. The eval
exists to characterise *this* system.

## License

Apache-2.0 — see [`LICENSE`](LICENSE). The fixtures are **not** covered by that licence; they remain
the property of their issuers.
