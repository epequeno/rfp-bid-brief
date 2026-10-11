# 0008 — Two decision models are callable today, on a surface the probe did not know about

- **Status:** accepted (2026-10-11)
- **Date:** 2026-10-11

## Context

ADR 0007 declared the probability channel pluggable, named `microsoft/microsoft-decision-1` as its
intended first choice, and required that **nothing depend on it until it is callable**, on the basis
of a probe that said it was not: absent from the 458-model catalogue, and HTTP 404 on
`/api/v1/models/<id>`, with and without a key.

That probe was wrong, and so was the conclusion drawn from it. Both decision models answer today:

| | `typesafe/jev-1.13` | `microsoft/microsoft-decision-1` |
|---|---|---|
| endpoint | `POST https://openrouter.ai/api/alpha/decisions` | same |
| Tahoe fixture | `{"bid": {"type": "noul", "noul": 0.03}}` | `{"bid": {"type": "noul", "noul": 0.0086}}` |
| usage | 446 in / 20 out | 193 in / 1 out |
| cost per decision | **$0.0000187** | **$0.0000081** |
| provider | TypeSafe | **Azure** |
| resolved version | `typesafe/jev-1.13-20260917` | `microsoft/microsoft-decision-1-20261009` |

Three things were invisible to the probe, and each would have kept being invisible:

1. **Decision models are not chat models, and they refuse to pretend.** `/chat/completions` answers
   400: *"… is a decisions model and cannot be used with the chat/completions endpoint. **Use the
   /api/alpha/decisions endpoint instead.**"* The endpoint that works is not the endpoint a chat
   probe tries.
2. **Jev is deliberately absent from the public catalogue.** The provider's own documentation says
   so: it returns 200 and is fully populated, you can call it by exact ID, and *"you cannot discover
   it programmatically."* A catalogue check cannot find it by construction.
3. **The decisions endpoint is a passthrough, not a translation layer.** It takes TypeSafe's System
   One schema verbatim — `state` plus typed `questions` — so the request shape is learnable from the
   endpoint's own validation errors, which is how the schema below was established.

## Decision

1. **`typesafe/jev-1.13` is the probability channel.** It is the model ADR 0003 named, its `noul`
   answer *is* `P(yes)`, and at $0.0000187 per decision the entire fixture set costs under a cent —
   which also makes repeated runs affordable, and therefore makes the decision layer's variance
   measurable rather than assumed.
2. **`microsoft/microsoft-decision-1` is the comparator, not the channel.** Two independent decision
   models on the same fixtures produce inter-model agreement and two calibration curves from one
   harness. On Tahoe they gave 0.03 and 0.0086 — same side, different confidence, which is the
   calibration question stated as data rather than as an opinion.
3. **The resolved model version and the serving provider go in every run record.** The API returns
   both (`…-20260917` / `…-20261009`, `TypeSafe` / `Azure`). A probability without the version that
   produced it is not reproducible, and the same weights behind a different host is a different
   reproducibility story — the rule ADR 0007 set, now applicable rather than hypothetical.
4. **Callability is decided by making a call, and the probe now tries both surfaces.** It asks
   chat/completions, and on a "decisions model" refusal it re-asks the decisions endpoint. The
   catalogue and per-model signals are printed as *informational* and no longer decide anything.
5. **ADR 0007 stands except where it says otherwise.** Still in force: the channel is pluggable; a
   substitute is labelled a substitute; probabilities are **checked, not borrowed** — Brier and a
   reliability curve against the eleven labels at the pre-registered τ = 0.50, sample size stated;
   and the host is named. Superseded: the claim that nothing is callable, and with it the reason the
   calibration curve was unwired.

## Consequences

- **The last structural gap in the deliverable closes.** τ = 0.50 stops being pre-registered and
  unused; the calibration curve becomes plumbable, and the project's differentiator becomes something
  it can actually show.
- **It stays thin, and that is now a fixtures problem rather than a plumbing problem.** Eleven labels
  with four positives will produce an indicative curve, not a conclusive one. The honest next fix is
  more fixtures, not a better model.
- **Two decision models is a better artifact than one.** Agreement between them bounds how much of a
  probability is the model and how much is the question; disagreement localises the fixtures where
  the judgment is genuinely close.
- **The probe's error is itself worth keeping.** It reported a working model as unavailable, twice,
  for two different reasons — a metadata endpoint that 404s while inference works, and a catalogue
  that cannot list a model by design. `providers.py` records both, because the next person to ask
  "is it callable?" deserves the correction rather than the mistake.
