# 0011 — The contested fixture is a finding, not a defect to be resolved

- **Status:** accepted (2026-10-11)
- **Date:** 2026-10-11

## Context

One fixture — `energy-trust-of-oregon-crm-migration-to-d365` — is contested, and it is contested
robustly: bid counts of 7, 6, 6, 7 across four runs of the census (ADR 0010). Three independent
readings disagree about it, which is the unusual part:

| source | reading |
|---|---|
| the pre-label assessment (2026-10-10, before any label existed) | **bid** — "small, clean, 12 pages: a low-risk migration" |
| `fixtures/labels.json`, committed before any model saw a fixture | **no_bid** — functional configuration of Dynamics 365 |
| the census, four runs | **split**, 7 bid / 6–7 no-bid |

The causes are visible rather than mysterious. The profile names `functional SAP / Oracle / Workday
configuration` among its exclusions, and mentions Dynamics 365 **only inside a rule-of-thumb escape
clause** ("no-bid unless the work is platform engineering underneath it"). A reader who treats the
named exclusions as the list answers bid; a reader who applies the escape clause answers no-bid. Seven
models of each.

Three ways to deal with it were considered:

1. **Relabel the fixture to bid**, on the grounds that seven independent models disagreed with the label.
2. **Tighten the profile** so Dynamics 365 is excluded in the same plain terms as SAP and Oracle.
3. **Keep it**, and report the disagreement.

## Decision

**Keep it, and report it.** Specifically:

1. **The label is not changed.** A label encodes a judgment about *this firm's* capability. Fourteen
   decision models agreeing with each other is not evidence about the firm — it is evidence about the
   models, and treating model agreement as ground truth is how a label stops being ground truth.
2. **The profile is not tightened to resolve it.** Editing the profile until the contested case becomes
   unambiguous fits the instrument to the fixtures. The escape clause is doing real work elsewhere
   (it is what makes `masstech-ai-hub` and `snohomish` bids), and removing its ambiguity here would
   remove its judgment there.
3. **The disagreement is published** — in the brief for that fixture, in `results/census-repeats/`, and
   in `docs/NEXT.md` — as the most informative single entry in the evaluation set.
4. **If the profile ever changes, that is a new freeze under ADR 0002**, with labels re-derived from
   the current set and every model re-asked. Not a repair to this fixture.

## Consequences

**The set keeps a case whose right answer is genuinely uncertain**, which is the point of a calibration
curve. Eleven labels where every model is either right or wrong give a ranking; a fixture where the
models split gives a *curve*, and it is the only such fixture in the set.

**A reader can disagree with us and see who else did.** The brief states both the label and the seven
models that read it the other way, so a reviewer who thinks the profile should have treated this as
platform engineering can check that position against the census rather than against our summary of it.

**The escape clause is now a documented design feature with a known cost.** It buys discrimination
elsewhere and it buys this split here. That is a much better thing to have written down than to
discover again as a bug.

**What it does not fix: sample size.** One contested fixture among eleven is one data point, and the
census cannot manufacture more. The binding constraint on every calibration claim in this repository is
that the set has four positives — which is why the next work is fixtures, not plumbing.
