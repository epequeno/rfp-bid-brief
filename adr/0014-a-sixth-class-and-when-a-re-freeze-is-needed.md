# 0014 — A sixth class: staff augmentation, and when a re-freeze is actually needed

- **Status:** accepted (2026-10-11)
- **Date:** 2026-10-11

## Context

ADR 0013 recorded a gap rather than smoothing it over: the profile excludes *staff augmentation or
body-shop placements* as a delivery model, no binding could test for it, and the Judicial Council
fixture was therefore expressed as `operations_not_projects`. The effect was that the brief said
*"the work is continuous operations rather than a project with an end"* about a document whose own words
are "MASTER AGREEMENTS FOR TECHNICAL STAFF AUGMENTATION SERVICES".

That is worse than an imprecise label. A reason that misdescribes the thing it refuses teaches a reader
the wrong distinction — they would conclude the firm declines standing operations, when what the firm
actually declines is selling hours.

## Decision

1. **`staff_augmentation` becomes the sixth exclusion class.**
2. **The binding cites the phrase the profile already carries** — `staff augmentation or body-shop
   placements` — verbatim, and the priority order places it before `operations_not_projects`:
   `not_qualified, geography, product_not_services, functional_stack_not_held, staff_augmentation,
   operations_not_projects`.
3. **No re-freeze.** The profile's *content* did not change; a class was added that reads an exclusion the
   profile already stated. The labels authored against `eap-software-narrow-2026-10-11-r2` remain valid,
   the hash in `fixtures/labels.json` is unchanged, and τ = 0.50 stands.
4. **The rule this makes explicit:** a re-freeze is required when the profile's content changes — a new
   exclusion, a changed capability, a different experience record (ADR 0002, ADR 0012). It is not required
   when a binding is added that quotes a phrase already in the file. The test that keeps this honest is
   the state-completeness check: every phrase the rules layer cites must appear in the profile, so a
   binding cannot invent a phrase to avoid a re-freeze.
5. **The extraction reports the delivery model the document describes**, not the nearest class the code
   happens to have. Judicial Council's `delivery_model` is now `staff_augmentation`, because that is what
   the issuer is buying.

## Consequences

**The reason now matches the document.** The Judicial Council brief says staff augmentation, because that
is the class and that is the issuer's own term.

**The vocabulary is six classes plus `in_scope`**, and three places must agree on it: the profile, the
labels, and the bindings. That agreement is asserted by test, so a class cannot be added to one and
forgotten in another — which is how the fifth class spent time being unreachable.

**The census was run after this change, not before.** Order of operations for the current numbers:
profile revision → labels confirmed and committed → **then** every model asked. The labels gate the
models; nothing here relaxes that.

**A caveat on how much one class buys.** This class exists because a document was misdescribed, not
because the set needed it: the Judicial Council fixture was already a no-bid under the old reading, so
the class changes the *reason* and not a single verdict. The honest measure of a class is whether it
changes a decision; this one does not, and it is worth saying so rather than counting it as a win.
