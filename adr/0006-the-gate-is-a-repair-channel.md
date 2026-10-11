# 0006 — The citation gate is a repair channel, bounded to one attempt

- **Status:** accepted (2026-10-11)
- **Date:** 2026-10-11

## Context

The first model pass refused three of eleven extractions ([`results/model-pass.md`](../results/model-pass.md)),
and every refusal came with a specific diagnosis: the quote is real, and here is where it actually
lives —

> `facts.subject`: quote not found in span `p1-s0` under the verbatim rule: `Information Systems
> Consultant` **[this quote does appear in `p2-s0`, `p2-s1`, `p4-s0` — the citation names `p1-s0`.]**

Refusing on that and stopping wastes the most useful signal the pipeline produces. The gate knows
what is wrong and where the right answer is; a producer that never hears it cannot correct a mistake
it has no way to see. That is a design flaw, not model error.

The counter-pressure is equally real. A retry is a chance to change the answer, and an eval that
lets a producer keep trying until it passes is measuring reruns, not capability.

## Decision

A citation refusal is fed back to the extractor for **one** bounded repair attempt, and the attempt
count is recorded with the extraction.

1. **Bounded.** One retry, never a loop. A producer that cannot fix a citation when handed its
   location has a problem this pipeline cannot repair, and an unbounded loop turns a measurement
   into a search.
2. **Repair only.** The repair prompt names the refused citations and instructs that **everything
   else stays unchanged** — no revised values, no added or dropped fields. The values are the
   measurement; the citations are what is broken.
3. **The gate re-runs on the repaired output.** A repair is not an exemption. If the second attempt
   is also refused, the extraction is refused, full stop.
4. **Both numbers are reported.** First-attempt citation integrity *and* the repair rate. Collapsing
   them into one pass rate hides which one moved, and they mean different things: the first measures
   whether a model copies text faithfully, the second measures whether a specific diagnosis is
   actionable.

## Consequences

- `extractions/model/*.json` carry `attempts`, `repaired_after_refusal`, and the full refusal list, so
  a reader can see which extractions needed help and why.
- The retry is offline-testable because the model call is injectable: the tests drive the loop with a
  stub that returns a broken citation and then a fixed one, and with one that never fixes it. No
  network, no API key, and the bounded-and-repair-only properties are asserted rather than promised.
- A repaired extraction is weaker evidence than a first-attempt one, and the data says so. Any future
  claim that leans on the model's extractions has to decide whether it trusts a repaired citation,
  and the honest default is to report both figures rather than one.
- This does not make the extractor deterministic, and it is not meant to. The nondeterminism noted in
  `results/model-pass.md` remains the larger methodological gap: a retry reduces *variance in the
  outcome* while leaving the underlying sampling untouched, and pinning temperature or reporting a
  distribution over repeats is still the fix.
