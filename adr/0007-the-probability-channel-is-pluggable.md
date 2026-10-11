# 0007 — The probability channel is pluggable, and its first choice is not callable yet

- **Status:** accepted (2026-10-11)
- **Date:** 2026-10-11

## Context

ADR 0003 pre-registered τ = 0.50 on `P(bid)` from a **typed decision layer**, and named Jev. The
reasoning was that Jev's probabilities are publishable: a calibration curve at a stated operating
point is a defensible claim in a way that "our classifier agreed with the labels" is not.

Jev is not available to this project. A replacement was proposed: **`microsoft/microsoft-decision-1`**,
which is the same category of model — a decision-scoring model whose announcement explicitly lists
"probability and confidence calibration" among the problems it addresses, and which benchmarks
**Jev itself** on accuracy and calibration. On the merits it is a good fit, and arguably a better one
than the model it replaces.

Then the provider check:

| probe | result (2026-10-11) |
|---|---|
| `GET /api/v1/models` | HTTP 200, **458 models, none matching "decision"** |
| `GET /api/v1/models/microsoft/microsoft-decision-1` | **HTTP 404**, with and without an API key |
| the listing page | exists: 32,768 context, $0.042/M in, $0/M out, released **2026-10-09** |
| other route | Microsoft Foundry: `ai.azure.com/catalog/models/Microsoft-Decision-1` |

So the model is **announced and listed, and not served by the API we can reach**. That is a fact
about a two-day-old release, and facts like it go stale in both directions — a listing can precede an
API, and an API can serve a model before a catalogue lists it. Hence `rfpbrief provider`, which probes
rather than remembers.

## Decision

1. **The decision layer stays pluggable.** `decide` remains deterministic and profile-driven (ADR
   0002); the *probability* is a separate, replaceable channel with an explicitly validated output
   contract. Nothing about the pipeline's structure assumes which model fills it.
2. **`microsoft/microsoft-decision-1` is the intended first choice**, recorded here as the intended
   model so that a later substitution has to be argued rather than assumed.
3. **Nothing depends on it until it is callable.** No extraction, brief or metric may cite it. The
   probe decides, and `just provider-check` reports.
4. **A substitute is labelled a substitute, and its probabilities are checked, not borrowed.** A
   substitute's `P(bid)` must clear the same bar as any other: reported with its Brier score and
   reliability curve against the eleven committed labels, at the pre-registered τ, with the sample
   size stated. What is never acceptable is emitting a number and calling it calibrated because the
   model was *meant* to be one.
5. **The route matters for attribution.** If the model is reached through Foundry rather than
   OpenRouter, the extraction record says so: the same weights behind a different host is a different
   reproducibility story, and the run has to name what actually served the request.

## Consequences

- The calibration curve — the project's actual differentiator — stays unwired until either the model
  becomes callable or a substitute passes the bar above. That is a real gap in the deliverable, and
  this record names it rather than papering over it with a plausible-looking probability.
- `just provider-check` is cheap and idempotent, so the question "is it live yet?" costs one command
  and does not depend on anyone remembering to ask. It is not scheduled: the repository has no
  scheduler and, per its own conventions, adds one only when a human-triggered check has proven
  insufficient.
- A substitute route through Foundry requires credentials this project does not hold. That is a
  decision for the owner of the credentials, not a workaround for the agent to improvise.
- Because τ = 0.50 was pre-registered on a probability whose *semantics* were Jev's, a substitute's
  probabilities are only comparable if they are calibrated to the same interpretation of `P(bid)`.
  This is why the operating point is re-stated in every brief that uses it rather than inherited
  silently from ADR 0003.
