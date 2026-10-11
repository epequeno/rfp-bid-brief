# 0002 — A bidder profile is a required input

- **Status:** accepted
- **Date:** 2026-10-11

## Context

The first fixture set considered for this project came from an organisation that had actually bid on
the documents, so "bid" was implicit: the bidder was that organisation, and its capabilities went
without saying. That set was discarded (see the notice in `fixtures/NOTICE.md`), and the replacement
fixtures are public solicitations from eleven unrelated issuers.

With no named bidder, **"bid" is undefined**. A recommendation is not a property of a solicitation —
it is a property of a solicitation *and* a capability. An RFP is not biddable or unbiddable in the
abstract; it is biddable by someone.

## Decision

`bidder-profile.json` is a required, committed input. It declares capability areas, accepted and
**excluded delivery models**, excluded capability areas, geography and size band — the exclusions
carrying at least as much weight as the capabilities — plus explicit rules of thumb so the decision
layer has reasoning to cite rather than a bare score.

The profile is the **only** source of "can this firm deliver this". No model opinion enters on
capability.

## Consequences

- The recommendation becomes reproducible and inspectable: it is a function of two committed inputs.
  Editing one line of the profile — adding a capability, narrowing a geography — is expected to
  flip calls, which is a demonstration in its own right and is testable.
- Ground truth becomes sharper. Labels are bid/no-bid **against this profile**, which is a smaller
  and more honest judgment than "would I personally enjoy this work".
- The profile shipped here is a **narrow straw man**, and the repository must say so. It is
  deliberately exclusionary so that the negative class is populated by real reasons rather than by
  weak ones. A real firm's profile would differ, and the eval would then measure that profile.
- **Circularity risk, stated plainly:** a profile written while looking at the documents it will be
  judged against makes the labels partly self-fulfilling. Mitigation, applied and recorded in the
  file itself: capabilities were derived from statements that exist independently of the fixtures
  (shipped work, prior engagements), fixture inspection was used **only** to confirm the profile
  discriminates rather than to add or remove capabilities, and the file is hashed **before** any
  label is authored. A future profile change invalidates the labels and requires a re-run.
