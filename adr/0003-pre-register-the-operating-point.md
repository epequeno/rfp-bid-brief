# 0003 — Pre-register the operating point, and freeze the profile before labelling

- **Status:** proposed — **nothing model-facing may run until this is accepted**
- **Date:** 2026-10-11

## Context

This repository's claim is that a decision layer's probabilities are useful because they are
*calibrated*, and that the calibration is shown at a stated operating point. That claim only holds
if the threshold was fixed before the results existed. A threshold chosen after seeing performance
is a fitted number, and a calibration curve drawn through a hand-picked point is decoration.

Two further orderings matter for the same reason. Labels authored with knowledge of results are not
ground truth. A profile edited after seeing which fixtures were misclassified is a fitted profile.
Both are easy to do by accident and invisible afterwards.

## Decision

Before any model-facing run:

1. **Freeze the profile** — `bidder-profile.json` is committed and its sha256 recorded.
2. **Commit the labels** — `fixtures/labels.json`, authored against that profile, held out from the
   model path entirely.
3. **Pre-register the operating point: τ = 0.50.** The brief recommends *bid* when `P(bid) ≥ τ`.
   The choice is **not** tuned to any result (there are none yet). It is stated as the default
   because no cost model is available to justify moving it: a false bid wastes proposal effort, a
   false no-bid forgoes an opportunity, and without prices for those two errors a symmetric
   threshold is the honest choice. The full curve is published alongside it precisely so a reader
   with different costs can re-point it themselves.
4. **Pre-register what will be reported**, so the metric set cannot drift toward whatever looks
   best: the confusion matrix with the class balance stated; precision and recall **per class**;
   the Brier score; the calibration curve at τ; the citation-integrity pass rate; and the baseline
   comparison.
5. **Pre-register the baseline:** title-only keyword matching. It is expected to fail on fixtures
   whose titles point the wrong way — a solicitation titled "Enterprise Generative AI Services"
   that is a product purchase, not a services engagement. If the baseline does *not* fail there, the
   pipeline is adding nothing and that is the finding.

## Consequences

- Until this ADR is accepted, no fixture may be sent to a model and no metric may be computed. The
  repository legitimately sits in a "frozen inputs only" state.
- Any later change to the profile, the labels, or τ invalidates the curve. The remedy is a re-run
  with the previous numbers retained and marked superseded — never a quiet replacement.
- The fixture set is skewed toward no-bid and thin (four positives). This is recorded here rather
  than discovered later: the class balance travels with every metric, and the calibration curve is
  reported as indicative rather than conclusive at this sample size.
- Restating a rule from ADR 0002 that still holds, because superseding one record must not lose the
  other: **the profile is the sole source of "can this firm deliver this"**, and no model opinion
  enters on capability.
