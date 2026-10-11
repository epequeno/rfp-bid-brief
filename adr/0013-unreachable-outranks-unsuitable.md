# 0013 — Unreachable outranks unsuitable, and a class must be visible to every judge

- **Status:** accepted (2026-10-11)
- **Date:** 2026-10-11

## Context

ADR 0012 added `not_qualified` as the fifth exclusion class and recorded it as *expressible but
unexercised*. Implementing it showed that two things had to be true before it was a class at all, and
neither was:

1. **A binding had to be able to produce it.** The class existed in the profile and in
   `fixtures/labels.json` and in no binding, so `decide` could never emit it. A class that no code path
   can reach is documentation, not a verdict.
2. **Every judge had to be able to see it.** `profile_exclusions()` — the function that answers "where
   does the profile say what this firm does not do?" — omitted `excluded_eligibility_gates`, and so did
   `build_state()`, which is the text the decision models read. The tests caught the second one
   immediately, because the same omission had already bitten this repository once: the profile's rules
   of thumb were missing from the state, and fourteen models read the profile literally while the rules
   layer cited a phrase they had never been shown.

Then the priority question: a gated procurement can be *both* unreachable and unsuitable. Cleveland
ISD's RFP is explicit software procurement **and** requires five successful Texas K-12 implementations.
Which reason is primary?

## Decision

1. **`not_qualified` sorts first.** If the firm is ineligible before capability is assessed, no other
   reason is the interesting one — the reader does not need to know that the firm would also have been
   the wrong shape. `PRIORITY` becomes `not_qualified, geography, product_not_services,
   functional_stack_not_held, operations_not_projects`. All matched reasons are still reported; only the
   primary changes.
2. **Four bindings, one per differently worded profile phrase**, over a list-valued requirement
   `eligibility_gates` — mirroring how `functional_stacks` already handles three phrases. A reason should
   quote the phrase it actually enforces, which is impossible with a single boolean.
3. **The gate list and the firm's record are part of the state** every decision model sees. A model
   cannot apply a class whose terms and comparison basis it was never given.
4. **An unrecognised gate shape is a consideration, not a no-bid.** The profile, and only the profile,
   decides capability; this is asserted by test.

## Consequences

**The class is no longer unexercised.** Cleveland ISD's RFP now yields `no_bid` with primary reason
`not_qualified` and a secondary `product_not_services` — the case ADR 0012 predicted, and the first
fixture in the set where the firm cannot bid rather than will not.

**Two omissions are fixed at the source.** `profile_exclusions()` and `build_state()` both include the
gate list, and both carry a comment saying why: they were written before the list existed, and an
omission of this kind is invisible until a test or a model disagrees with you. The consistency test —
every phrase the rules layer cites must appear in the state — is what found them, twice now.

**Every census on file is stale for a second reason.** The state changed (gates and the experience block
are new), so the archived censuses carry a different `state_sha256` in addition to the profile change
from ADR 0012. The re-run after labels land is not optional bookkeeping; without it, every published
probability describes a state no model will ever see again.

**A gap remains open and is recorded rather than papered over.** The profile excludes *staff augmentation
and body-shop placements* as a delivery model, but no binding can test for it: the Judicial Council
fixture is expressed through `operations_not_projects` because that is the nearest available class, and
the reasons text therefore says "continuous operations" about a document whose own words are "staff
augmentation". Either that becomes a sixth class or the binding vocabulary stays narrower than the
profile's exclusion list — a decision for the owner, and now written down where it will be found.
