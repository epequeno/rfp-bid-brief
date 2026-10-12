# State at closure — read this before resuming anything

**This project is finished, not paused.** `adr/0015` records why the site, the MCP surface and the
LangGraph graph were dropped rather than deferred. What follows is what exists, what the numbers are,
what was deliberately not done, and what a future session should not assume.

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
| decision census | **14 served decision models × 11 fixtures = 154 decisions for $0.007** (ADR 0009), repeated four times for $0.028 (ADR 0010) | `results/decisions.json`, `results/census/`, `results/census-repeats/` |
| calibration | per-model accuracy, Brier, reliability, and where the census splits | `results/calibration.json` |

Run `just` for the recipe list; `just check` runs everything offline (fixture hashes, 87 tests, span
reproducibility, extraction validation, baselines).

## The numbers, with their limits attached

- **Span index:** 5,706 spans; median span 61–139 characters.
- **Citations:** 8/11 model extractions passed the gate first try; with the repair channel, **0
  refusals**. First-attempt cleanliness across three runs was **7–8/11** — a range, not a rate.
- **Decisions:** **7–8 of 14** models reproduce **all eleven** labels at τ = 0.50 (the count moves by one
  across four repeats); the rest miss one fixture and only that one.
- **Calibration:** every model is within one call of every other, while **Brier spans 0.0021–0.0724**
  — a factor of 34. Accuracy is nearly identical; calibration is not. That is the project's thesis,
  as data.
- **Agreement:** ten fixtures unanimous in every run; **one split in every run** —
  `energy-trust-of-oregon-crm-migration-to-d365`, bid count **7, 6, 6, 7** across four repeats,
  probabilities 0.13–0.86.
- **The limits, which do not move:** eleven fixtures, four positives. Fourteen models is 154
  decisions and still **eleven independent label comparisons per model**. No number from this repo
  should be quoted without the sample size, and the census is **not exactly reproducible**: one
  decision in 616 changed sides across four repeats, so the counts carry ranges (`adr/0010`).

## Next steps, in value order

### 1. The committed briefs contradict the census — fix first (small, mine)

All eleven briefs in `results/briefs/` say *"no calibrated probability is available yet, so the
pre-registered operating point does not apply"*. That was true when written and is false now:
`results/calibration.json` has fourteen models' probabilities. `brief.py` should render the channel's
`P(bid)`, the pre-registered τ, the resulting call, the **census disagreement for that fixture**, and
a second model's number as an opinion. Regenerate all eleven.

### 2. ✅ Done — the decision layer's stability is measured (`adr/0010`)

Four censuses of one frozen state, $0.028. **Stable in structure, near-stable in numbers, not
reproducible.** Five of fourteen models are identical to the last digit; nine drift ≤ 0.07; two drift
~0.44 and one of those (`inception/mercury-decide`) **crossed τ on one fixture in one run of four** —
exactly one decision in 616 changed sides. The same ten fixtures were unanimous in every run and the
same single fixture split in every run, while the counts moved: **7 of 14 perfect became 7–8**, and the
split's bid count went **7, 6, 6, 7**.

The channel survives: Jev drifted 0.07 and produced the same verdict on all eleven fixtures, four runs
running. Full table in `results/census-repeats/README.md`. ADR 0009's single-run figures are qualified
by ADR 0010 rather than edited into it — an accepted record that gets rewritten when a later
measurement disagrees stops being a record of what was decided.

### 3. The Energy Trust split — **a decision for the owner** (see below)

### 4. Grow the fixture set — the only real fix for the statistics *(in progress)*

Fourteen models over eleven fixtures does not add statistical power. The fix is fixtures, weighted
toward **in-scope** solicitations: the set is 4 bid / 11 today, and positives are what precision and
calibration need.

**Round 3 is admitted — seven fixtures in, set now eighteen.** The profile was revised in the same
change (fifth exclusion class `not_qualified`, `adr/0012`), which makes this a **re-freeze**: new profile
sha256 recorded beside the old one, all eleven existing labels re-checked against the new class (zero
triggers, so no label changed and τ stands), and **every census and calibration figure on file was
measured under profile v1** — they carry v1 `state_sha256` and must be re-run once the new labels land.
Span indexes for all eighteen are built and reproducible: **8,497 spans, up from 5,706**.

**Extractions for the seven are written** (hand-authored, every value cited, quotes sliced from the span
index rather than retyped). The seventh passed only after the word-boundary rule rejected a quote that
ended mid-word — the gate working as designed. Verdicts under profile v2: two bids (IRCDUS, Allentown),
five no-bids — Cleveland ISD as `not_qualified` (gate **and** software), Kansas City Kansas CC and College
of Western Idaho as product purchases, the Judicial Council as operations, SAVEC as geography.

Implementing the fifth class exposed two omissions of the *same kind* as the bug ADR 0009 recorded: the
class had no binding, and neither `profile_exclusions()` nor `build_state()` knew about the gate list —
so the models would have been judging without the class the profile had just gained. Both fixed;
`adr/0013` records it.

**Labels confirmed and written as round 2; the census has been re-run under profile v2.** Set: 18
fixtures, 6 bid / 12 no_bid. Deterministic baseline: 18/18 label agreement, 17/18 primary reason class
(one pre-existing ranking divergence, palm-beach). Census: **248/252 answered** — the first refusals this
pipeline has seen, 4 from one model — **7 models perfect at 18/18**, Brier 0.0000–0.0725.

What the re-freeze changed, which is the most interesting result in the repository so far: the Energy
Trust split **narrowed from 7 bid / 7 no-bid to 4/14** once the state carried the gates and the firm's
experience record. The contested fixture became less contested *because the judges could see more of the
profile*, not because the profile was edited to resolve it. Three fixtures now split (allentown 11/14,
College of Western Idaho 1/14, Energy Trust 4/14); fifteen are unanimous, including every gated and
product case.

**Still open:** a sixth class was added (`staff_augmentation`, `adr/0014` — no re-freeze, it cites a
phrase the profile already carried), and the repeats under profile v2 have not been re-run (~$0.05).
The enrichment question from round 3 is still unanswered. Seven new candidates (8.3 MB,
HTTP 200, real text layers, no employer/client relationship, no vendor responses) sit in
`outbox/2026-10-11-fixture-expansion/candidates/` with proposed labels and evidence per document in
`CANDIDATES.md`. Two are bid-likely, five are not, and **that ratio is the finding**: the bid-likely
shape for this firm is rare in the public record, and most solicitations are product purchases,
managed-service contracts or staff augmentation — all three of which the profile excludes.

So the open question is not sourcing but *what the evaluation is*: represent the base rate, or enrich
deliberately and **say so in the README**. The recommendation in the candidates document is to enrich
and declare it, because the purpose is a checkable decision layer rather than a base-rate estimate.

Two things that round will need from the owner: **the labels** (30–45 minutes, pre-filled proposals to
confirm or overturn) and **a decision on a fifth exclusion class** — *not qualified / not eligible* —
which two freshly found documents require and which no existing class can express. Adding it changes
`bidder-profile.json` and therefore means a new freeze under ADR 0002.

Search targets that have worked, for any later round: *strategic plan / master plan / roadmap /
assessment* solicitations from small agencies; AI **enablement** (capacity, governance, evaluation)
rather than AI procurement; data commons and interoperability rather than "a platform". Observability,
SRE and Kubernetes solicitations were searched four ways and produced nothing usable — which is
informative about what a portfolio built on those can claim.

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
