# State at closure — read this before resuming anything

**This project is finished, not paused.** [`adr/0015`](../adr/0015-this-is-an-evaluation-not-an-agent-application.md)
records why the static site, the MCP surface and the LangGraph graph were dropped rather than deferred.
The [README](../README.md) is the public description and carries the results; **this file is the
internal one**: what is unfinished, what must not be misread, and what constrains a future change.

## Where it stands

| stage | state | artifact |
|---|---|---|
| frozen inputs | profile hashed (`…-r2`), labels committed, τ = 0.50 pre-registered — **before any model ran** | `bidder-profile.json`, `fixtures/labels.json`, `adr/0003` |
| `parse` | deterministic span index, **8,497 spans over 444 pages**, byte-reproducible | `results/spans/` |
| `extract` (oracle) | 18 hand-authored extractions, every value cited | `extractions/*.json` |
| `extract` (model) | pinned model + one bounded repair attempt; refusals filed apart from data | `extractions/model/` |
| `decide` | deterministic bindings over six exclusion classes plus `in_scope` | `src/rfpbrief/decide.py` |
| `brief` | 18 one-page briefs, every quote re-verified against the span index | `results/briefs/` |
| decision census | **248/252 answered · 14 models × 18 fixtures · $0.0159** | `results/decisions.json`, `results/census/` |
| calibration | per-model accuracy, Brier, reliability, and where the census splits | `results/calibration.json` |
| labels | round 2: **18 fixtures, 6 bid / 12 no_bid**, each with reason, evidence and counterargument | `fixtures/labels.json` |

`just check` runs everything offline: fixture hashes, 109 tests, span reproducibility, extraction
validation, the baseline, and status. **Green as of 2026-10-11.**

## Deliberately unfinished, and why each is named rather than implied

- **The model path end to end.** The baseline consumes hand-authored extractions, so the pipeline's
  accuracy *with a model reading the documents* has no number. This is the largest gap in the
  repository and the only one that would change its claims.
- **The repeats under profile v2.** Four repeats exist for profile v1 only (`results/census-repeats/`,
  marked HISTORICAL in place). Re-running them costs ~$0.05 and would refresh the stability finding.
- **The enrichment question.** The set is enriched — positives were searched for deliberately in two
  rounds — and 6/18 is *not* the base rate for a narrow firm. The recommendation was to enrich and
  declare it (done, in the README and in the label provenance); the alternative, representing the base
  rate, was never chosen and would mean a larger set and thinner curves.
- **No extractor comparison.** Nothing has compared extractors the way the census compared decision
  models, and the same trick would work at the same trivial cost.
- **The sixth class changes reasons, not verdicts.** `staff_augmentation` (`adr/0014`) fixed the reason
  text on one fixture; it moved no decision. A class that changes no decision is not a win.

## Artifacts that are historical — do not read them as current

| artifact | why |
|---|---|
| `results/census-repeats/` | profile v1 and a state without the eligibility gates. The *finding* stands; the numbers describe a state no model will see again. |
| `extractions/model/`, `extractions/repeats/`, `results/model-pass.md`, `results/variance.json` | the eleven-fixture era, under an earlier profile. Superseded by the re-freeze, not by a better run. |
| `results/census/*.json` | every census is archived content-addressed by **state and answers**; older entries carry a v1 `state_sha256`. That is the point of the archive — it lets this table exist. |

## What a future session must not assume

1. **Any change to the profile or the state requires re-running the census.** The census state includes
   the profile, so a stale `calibration.json` describes a state no model will see again. The order is
   fixed: profile hash → τ → **labels** → then any model sees a fixture (`adr/0003`).
2. **An accepted ADR is not edited.** Supersede or qualify it in a new record — `adr/0010` qualifies
   `adr/0009`; `adr/0012` qualifies `adr/0002`'s freeze. Editing an accepted record to match what was
   later learned is how a decision log stops being a record of what was decided.
3. **Labels are authored against the profile, before any model output is seen**, and each carries its
   counterargument. `LABELS-PROPOSED.md` in the outbox is the record of how round 2 was confirmed.
4. **The census cost is per run** (~$0.0159), and a census archives itself; nothing needs to be
   overwritten to measure again.

## Constraints already decided (the short version of `adr/`)

| ADR | decides |
|---|---|
| 0001 · 0004 · 0005 | citations locate a quote inside a span, verified at page level; a quote that does not resolve fails the build |
| 0002 · 0012 | a bidder profile is a required input; changing its content is a **new freeze**, and labels are re-derived |
| 0003 | the operating point and metric set are pre-registered before any model runs |
| 0006 | the citation gate is a **repair channel**, bounded to one attempt |
| 0007 · 0008 | the probability channel is pluggable; the pinned pair is Jev (channel) and Microsoft (comparator), recorded by resolved build and host |
| 0009 · 0010 | the decision layer is a **census**, repeated; published figures are **ranges** wherever repeats disagree |
| 0011 | the contested fixture is a **finding**, not a defect to be resolved — the label and the profile stay as they are |
| 0013 | unreachable outranks unsuitable: `not_qualified` sorts first |
| 0014 | `staff_augmentation` is its own class; a class may be added without a re-freeze when it cites a phrase the profile already carries |
| 0015 | this is a decision-layer evaluation, **not an agent application** |

## History worth knowing

**`cb23f56` replaced this repository's README with an earlier copy of this file** — a path mix-up in a
patch script, caught by the owner on review. The public README was rebuilt from `be67879` on 2026-10-11,
with its numbers re-derived rather than copied (one of them, a page count, had been invented and was
corrected from 316 to the measured 444). The commit is left in history rather than rewritten: it is a
true record of what happened, and the fix is a later commit.

## How to re-enter

```bash
cd ~/code/rfp-bid-brief
just status            # inputs, stages, and what explicitly does not exist
just check             # everything offline; no API key
just briefs            # re-render all eighteen briefs
just census            # ~$0.02, two minutes, archives itself under results/census/
just calibration       # per-model calibration at the pre-registered tau
```

Read `adr/` in order before changing anything about citations, thresholds or the profile. Fifteen
records; the last four exist because earlier attempts were wrong in instructive ways.
