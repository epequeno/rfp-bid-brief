# Where this stands, and what is next

Written 2026-10-11, at the end of the session that built the pipeline end to end. This is the
re-entry point: what exists, what the numbers are, what is deliberately unfinished, and the four
decisions that are not mine to make.

## What is built

| stage | state | artifact |
|---|---|---|
| frozen inputs | profile hashed, labels committed, τ = 0.50 pre-registered — **before any model ran** (ADR 0003) | `bidder-profile.json`, `fixtures/labels.json`, `adr/0003` |
| `parse` | deterministic span index, 5,706 spans over 278 pages, verified reproducible | `results/spans/` |
| `extract` (oracle) | 11 hand-authored extractions, every value cited, 34 citations refused-tested | `extractions/*.json` |
| `extract` (model) | pinned model + one bounded repair attempt; refusals filed apart from data | `extractions/model/`, `extractions/repeats/` |
| `decide` | deterministic verdict against the frozen profile; no probability invented (ADR 0002) | `src/rfpbrief/decide.py` |
| `brief` | one page per fixture, every quote re-verified against the span index | `results/briefs/` |
| decision census | **14 served decision models × 11 fixtures = 154 decisions for $0.007** (ADR 0009) | `results/decisions.json`, `results/census/` |
| calibration | per-model accuracy, Brier, reliability, and where the census splits | `results/calibration.json` |

Run `just` for the recipe list; `just check` runs everything offline (fixture hashes, 87 tests, span
reproducibility, extraction validation, baselines).

## The numbers, with their limits attached

- **Span index:** 5,706 spans; median span 61–139 characters.
- **Citations:** 8/11 model extractions passed the gate first try; with the repair channel, **0
  refusals**. First-attempt cleanliness across three runs was **7–8/11** — a range, not a rate.
- **Decisions:** 7 of 14 models reproduce **all eleven** labels at τ = 0.50; the other 7 miss one
  fixture and only that one.
- **Calibration:** every model is within one call of every other, while **Brier spans 0.0021–0.0724**
  — a factor of 34. Accuracy is nearly identical; calibration is not. That is the project's thesis,
  as data.
- **Agreement:** ten fixtures unanimous; **one split** — `energy-trust-of-oregon-crm-migration-to-d365`,
  7 bid / 7 no_bid, probabilities 0.13–0.86.
- **The limits, which do not move:** eleven fixtures, four positives. Fourteen models is 154
  decisions and still **eleven independent label comparisons per model**. No number from this repo
  should be quoted without the sample size, and the decision census was called **once** per
  (model, fixture) — model nondeterminism is untested.

## Next steps, in value order

### 1. The committed briefs contradict the census — fix first (small, mine)

All eleven briefs in `results/briefs/` say *"no calibrated probability is available yet, so the
pre-registered operating point does not apply"*. That was true when written and is false now:
`results/calibration.json` has fourteen models' probabilities. `brief.py` should render the channel's
`P(bid)`, the pre-registered τ, the resulting call, the **census disagreement for that fixture**, and
a second model's number as an opinion. Regenerate all eleven.

### 2. Measure the decision layer's stability (small, mine, ~$0.007 per run)

`results/variance.json` covers the **extractor** only. The census was one call per pair. Given how
loudly extractor nondeterminism bit us, assuming the decision layer is stable is exactly the
assumption not to leave untested. Three repeats, then report the spread the same way: a range, never
a point.

### 3. The Energy Trust split — **a decision for the owner** (see below)

### 4. Grow the fixture set — the only real fix for the statistics (needs labelling time)

Fourteen models over eleven fixtures does not add statistical power. The fix is fixtures, weighted
toward **in-scope** solicitations: the set is 4 bid / 11 today, and positives are what precision and
calibration need. The agent can source and extract; the labels are the owner's, and that is the real
cost — roughly an hour per five fixtures.

### 5. Packaging, once the numbers stop moving

One `just eval` producing the whole report, then the static site generated from those artifacts
(`make site` reads the eval JSON so the published site *is* the report), then the troposphere stack
that emits the Lambda and the S3 + CloudFront distribution together. That is the portfolio
deliverable, and building it before the numbers settle means rebuilding it after.

### 6. MCP surface — approved, weekend-scale, subordinate

Read-only tools over the publishable corpus: list fixtures, extract fields, return spans with
citations. Unchanged from the original scope discussion.

## Open decisions, and the arguments as I see them

**The Energy Trust split (7 bid / 7 no_bid).** The root cause is visible in the profile: it names
`functional SAP / Oracle / Workday configuration` in its exclusions, and mentions **Dynamics 365 only
inside a rule-of-thumb escape clause** ("no-bid unless the work is platform engineering underneath
it"). Seven models read the exclusions literally and said bid; seven applied the escape clause and
said no-bid.

- **Keep it.** The split is a finding, and `labels.json` already recorded this fixture as "the
  closest call in the set" before any model ran. Costs nothing; the honest artifact.
- **Tighten the profile** so D365 is excluded unambiguously. Under ADR 0002 that invalidates the
  labels, so it means re-freezing and re-running everything — and it would make the split disappear
  *by construction*, which is a reason for suspicion rather than enthusiasm.
- **Relabel that fixture to bid.** I would argue against: the label is a judgment about the firm's
  capability, and seven models agreeing with each other is not evidence about the firm.

**Should the extractor model be pinned for sampling?** `pi`'s CLI exposes no temperature or seed, so
extraction cleanliness is a distribution. Either move the extractor behind a client that controls
sampling, or keep reporting ranges. The decision layer's API does expose `seed` and `temperature`,
so the two halves of the pipeline need not be handled the same way.

**Which extractor model?** Currently `openrouter/minimax/minimax-m2.7`, chosen for cost and speed, not
for extraction quality. Nothing has compared extractors the way the census compared decision models —
and the same trick would work, at the same trivial cost.

## Divergences to resolve rather than leave lying around

- **LangGraph is in the plan and not in the code.** `PLAN.md` and `BUILD-PLAN.md` describe a LangGraph
  state graph (`parse → extract → decide → brief`), and the framework base was one of the five
  portfolio bases the demo was meant to cover. What exists is four plain Python modules. Either wire
  the graph — it is trivial at four nodes — or record that the framework base is not being covered.
  Right now the plan claims something the repository does not do.
- **`README.md` still describes the brief as it was.** Its "what the first end-to-end brief says"
  section quotes the old "no probability" note. Fixed by next step 1, but it is the same class of
  stale-claim problem: prose written before an artifact changed.
- **The outbox scope documents are historical.** `outbox/2026-10-10-rfp-demo-langgraph-extension/`
  holds the approved scope, the fixture rounds, the bidder profile's rationale and the label sheet.
  The build has outrun them; they remain the record of *why*, and this file is the record of *where*.

## How to re-enter

```bash
cd ~/code/rfp-bid-brief
just status              # inputs, stages, and what explicitly does not exist
just check               # everything offline: hashes, 87 tests, index reproducibility, baselines
just provider-check      # is the intended decision model callable? (decided by calling it)
just census              # ~$0.007, two minutes, archives itself under results/census/
just calibration         # per-model accuracy and calibration at the pre-registered tau
```

Read `adr/` in order before changing anything about citations, thresholds or the profile — nine
records, and the last three exist because the first attempts were wrong in instructive ways.
