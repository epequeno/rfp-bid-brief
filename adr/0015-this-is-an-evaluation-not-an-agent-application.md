# 0015 — This is a decision-layer evaluation, not an agent application

- **Status:** accepted (2026-10-11)
- **Date:** 2026-10-11

## Context

The approved scope for this work named three surface artifacts as part of the demonstration: a
**LangGraph** state graph, an **MCP** tool surface, and a **static site on S3 + CloudFront** generated
from the eval artifacts. The reasoning at the time was portfolio-shaped: a thin vertical slice showing
framework fluency, a tool surface, and a deployment.

What got built instead is a deterministic pipeline (span index → extraction → decision → brief) with a
citation gate, plus a measured evaluation of decision models. No framework orchestrates it, no tool
surface wraps it, and nothing in it needs to run anywhere. Reviewing the result, the argument against
the three surface artifacts turns out to be specific rather than a matter of taste:

- **A deploy is only a demonstration if the product must run.** This product is a document. Publishing
  the briefs behind a CDN adds a distribution layer and no capability, and a reader is better served by
  the README than by a site that renders the same numbers.
- **No model is in the loop outside the decision census.** Nothing here composes prompts, calls tools,
  or sequences model output at runtime — so an orchestrator would be running four pure functions in
  order, and an MCP surface would expose deterministic file reads. Both would be the *claim* of tooling
  and framework fluency without the substance of it.
- **The framework and deploy claims belong to a project whose product needs them.** Adding them here
  would attach a dependency and a surface to a repository whose entire argument is reproducibility.

## Decision

1. **The scope is narrowed to what it is**: a decision-layer evaluation with a citation contract, for a
   bid/no-bid triage use case.
2. **The site, the MCP surface and the LangGraph graph are dropped, not deferred.** Deferring them
   leaves the repository permanently half-promising something; dropping them makes the plan documents
   true. The outbox scope documents are marked as superseded on this point.
3. **The deploy question moves to a project whose product must run** — where a service, a tool surface
   and an LLM in the loop are load-bearing rather than decorative.
4. **What carries over is the machinery, not the domain**: the citation gate (a quote that does not
   resolve fails the build), the census method (every served model, one frozen question, ranges where
   repeats disagree), and the freeze discipline (hash the profile, pre-register the operating point,
   label before any model sees the input).

## Consequences

**The repository is finished rather than unfinished.** Its status paragraph stops saying "not built"
about things nobody intends to build, and starts saying what it is.

**One gap is stated rather than left implied.** The model-backed extractor has never been measured
end-to-end under the current profile and labels: `results/baseline.json` is a hand-authored oracle, so
the pipeline's accuracy *with a model reading the documents* is unmeasured. That is now written in the
README and in `docs/NEXT.md` as a known limit of the artifact, not as a pending step — because a number
that does not exist should not be implied to be coming.

**The evaluation's own weaknesses stay on the record**: eighteen fixtures, six positives, one contested
document, and a stability measurement that was made against profile v1 and not repeated afterwards.

**A note on how this was decided.** The static site was recommended as the next work, and the reasoning
above is the owner's, in response: it is a better argument than the recommendation, and it is recorded
here because the reason to write decisions down is that the weaker ones should be visible later.
