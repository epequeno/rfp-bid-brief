# Is the census reproducible? Four runs of one frozen state

The extractor turned out to be nondeterministic — "clean on the first attempt" ranged 7–8/11 across
three identical runs — so assuming the decision layer *was* deterministic would have been the one
untested assumption left in the pipeline. Four censuses of the same frozen state cost **$0.028** total
and answer it.

**Answer, in one line: the census is stable in structure, near-stable in numbers, and not
reproducible.** The same ten fixtures are unanimous in every run and the same single fixture splits in
every run; the split *count* moves by one.

## Per model

Drift is the largest change in a single probability across the four runs. "Calls changed" counts
fixtures where a model's verdict crossed τ = 0.50 between runs.

| model | max drift | calls changed | correct @ tau | Brier across repeats |
|---|---|---|---|---|
| `perplexity/pplx-decider-v1.1-27b` | 0.0000 | 0 | 11–11 | 0.0021–0.0021 |
| `nace-ai/drex-v1.5` | 0.0000 | 0 | 11–11 | 0.0125–0.0125 |
| `cloudflare/clef-omni` | 0.0000 | 0 | 11–11 | 0.0207–0.0207 |
| `jaredpalmer/kev-4b` | 0.0000 | 0 | 10–10 | 0.0517–0.0517 |
| `openai/gpt-6-luna-decisions` | 0.0000 | 0 | 10–10 | 0.0312–0.0312 |
| `togethercomputer/tev1-4b-experimental` | 0.0048 | 0 | 10–10 | 0.0638–0.0638 |
| `cloudflare/clef` | 0.0396 | 0 | 11–11 | 0.0063–0.0071 |
| `upstage/solar-decide-flash` | 0.0522 | 0 | 10–10 | 0.0680–0.0724 |
| `cloudflare/clef-flash` | 0.0532 | 0 | 11–11 | 0.0273–0.0337 |
| `typesafe/jev-1.13` | 0.0700 | 0 | 11–11 | 0.0195–0.0222 |
| `liquid/d1` | 0.1436 | 0 | 11–11 | 0.0079–0.0184 |
| `microsoft/microsoft-decision-1` | 0.1563 | 0 | 10–10 | 0.0427–0.0643 |
| `upstage/solar-decide` | 0.4309 | 0 | 10–10 | 0.0348–0.0992 |
| `inception/mercury-decide` | 0.4461 | **1** | 10–11 | 0.0007–0.0257 |

- **Five of fourteen models are exactly reproducible**: identical probabilities to the last digit in
  every run. Nine more drift by ≤ 0.07.
- **Two drift by ~0.44**, and one of them — `inception/mercury-decide` — **changed a verdict**: on one
  fixture it crossed τ in one run out of four. Out of 616 decisions (14 × 11 × 4), **exactly one
  changed sides.**
- **The channel choice survives this.** `typesafe/jev-1.13` drifted 0.07 without moving a single call,
  and its Brier moved 0.0195 → 0.0222. Its probabilities are not identical run to run, but every
  verdict it produced was.
- **The calibration ranking is stable at the top and unstable in the middle.** Perplexity's 0.0021 is
  the best in every run and identical each time; `mercury-decide` spans 0.0007–0.0257 within itself —
  a 37× range across four repeats. Any "which model is best calibrated" claim from a single run is
  partly a claim about which draw it was.

## Per fixture

| fixture | label | bid count across four runs |
|---|---|---|
| `city-of-snohomish-it-strategic-plan-rfp` | bid | 14, 14, 14, 14 |
| `inprs-rfp-23-04-cloud-migration-iam-ztna` | bid | 14, 14, 14, 14 |
| `mass-tech-ai-hub-data-commons-consulting` | bid | 14, 14, 14, 14 |
| `community-action-partnership-kern` | bid | 14, 14, 14, 14 |
| `energy-trust-of-oregon-crm-migration-to-d365` | no_bid | **7, 6, 6, 7** |
| the other six | no_bid | 0, 0, 0, 0 each |

**Ten fixtures unanimous in every run; one split in every run.** The structure of the finding did not
move once. The number attached to it did: 7, then 6, 6, then 7 — which is why the published form of
this sentence is *"the models disagree here"* and not *"seven models say bid"*.

## What this changes in the published numbers

| claim as first published | after four runs |
|---|---|
| 7 of 14 models perfect at τ | **7–8 of 14** (`[7, 8, 8, 7]`) |
| energy-trust splits 7 bid / 7 no-bid | **contested in every run; bid count 7, 6, 6, 7** |
| Brier 0.0021–0.0724 | unchanged as a *range over models*, but per-model values are ranges too |
| one call per (model, fixture) | still true of the canonical run; stability is now measured separately |

These are qualifications of ADR 0009's single-run figures. ADR 0009 is accepted and stays as written;
the correction lives in ADR 0010, because editing an accepted decision record to match what we later
learned is how a decision log stops being a record of what was decided.

## The numbers behind this file

```
results/decisions.json             the canonical run (run 1 of the brief-rendering set)
results/census-repeats/run-1.json  three repeats of the identical frozen state
results/census-repeats/run-2.json
results/census-repeats/run-3.json
results/census/2026-10-11-*.json   every census archived content-addressed, state and answers
```

Reproduce with `just census --out results/census-repeats/run-N.json`, or compare two runs directly —
each census records the resolved build and serving host of every answer, so a difference can be
attributed to a version change rather than to the model moving.
