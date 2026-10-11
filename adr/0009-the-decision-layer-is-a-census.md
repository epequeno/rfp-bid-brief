# 0009 — The decision layer is a census, not a choice, and both judges see the same profile

- **Status:** accepted (2026-10-11)
- **Date:** 2026-10-11

## Context

ADR 0008 established that decision models are callable and cheap: about $0.00002 per decision. At
that price, choosing a panel of three is a judgement call that buys nothing and costs credibility —
so the question became whether to run **every** decision model served.

The provider's own guidance agrees and says something more useful: *"The catalog says nothing about
quality. Run the probe set through every remaining candidate."* And its API is a passthrough of one
schema, which makes byte-identical inputs across models literally achievable rather than aspirational.

Two things then went wrong, and both are the reason for the rules below.

**The instrument had a bug that looked like a finding.** The frozen state omitted the profile's
`decision_rules_of_thumb`. The phrase the deterministic layer cites for the D365 case —
*"vendor-specific functional stack the firm does not hold"* — appears **only** there. So all fourteen
models read the exclusions literally, unanimously said `bid` where the label says `no_bid`, and the
result looked like fourteen independent models disagreeing with a human. It was one incomplete
state: the rules layer could cite a phrase the models were never shown.

**A re-run destroyed the previous measurement.** The first census wrote to `results/decisions.json`;
fixing the state and re-running overwrote it. In a repository whose thesis is reproducibility, the
earlier number survived only in a transcript.

## Decision

1. **Census, not panel.** Every decision model served is asked, with exclusions made *by rule* and
   recorded on the entry: aliases (`~…`, which move to a new build without notice), `:free` tiers of
   an entry already counted, and entries with no declared context length. Fourteen models × eleven
   fixtures = 154 decisions for **$0.007**, in two minutes.
2. **One frozen request.** Every model receives the same `state` and the same `questions`; only the
   `model` field differs. The request text is hashed, and the hash goes in the result.
3. **Both judges see the same profile.** The state must carry every phrase the deterministic layer
   can cite — including the rules of thumb. This is enforced by a test that fails if any binding's
   phrase is absent from the state, and the test was verified by removing the rules and watching it
   fail.
4. **τ = 0.50 for every model**, read from the frozen labels. A model that needs a different
   threshold is a model that is not calibrated at τ, and that is a finding. Per-model optimal
   thresholds are computed and published **labelled post-hoc**, never as the headline.
5. **Pinned slugs, and record what answered.** The resolved model version and the serving provider
   are stored per answer (`…-20260917` / `TypeSafe`, `…-20261009` / `Azure`), because the same
   weights behind a different host is a different reproducibility story.
6. **Every census is archived content-addressed** under `results/census/<date>-<state-digest>.json`,
   so a re-run that changes the state cannot silently replace the previous measurement.

## Consequences

**What the fixed census shows.** Seven of fourteen models reproduce all eleven labels at τ = 0.50;
the other seven miss **one fixture and only that one**. Ten fixtures are unanimous; the census splits
on exactly one — `energy-trust-of-oregon-crm-migration-to-d365`, 7 bid / 7 no-bid, probabilities from
0.13 to 0.86. That is the fixture `fixtures/labels.json` already flagged, before any model ran, as
*"the closest call in the set"*, and it is also the one carrying the profile's D365 escape clause. The
census located the contested document independently of the label's own note, which is the most useful
thing it could have done.

**Accuracy is nearly identical; calibration is not.** Every model is within one call of every other,
while Brier scores span **0.0021 to 0.0724** — a factor of 34. A project that claimed calibration
rather than accuracy now has one dataset where those two claims come apart, which is the whole point
of the exercise.

**The sample does not grow with the number of models.** Fourteen models over eleven fixtures is 154
decisions and still eleven independent label comparisons per model. Every table this pipeline prints
carries the sample size, and no number from it should be quoted without it.

**Model nondeterminism applies here too.** Each (model, fixture) pair was called once. The decision
layer may be more stable than the extractor — a `noul` probability is a single number rather than
prose — but that is an assumption until repeats are run, and at $0.007 a census, repeats are cheap.
