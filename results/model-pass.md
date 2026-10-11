# First model pass — 2026-10-11

The model-backed extractor, run once over all eleven fixtures. Recorded here because a pass rate
without its conditions is not a result.

| | |
|---|---|
| model | `openrouter/minimax/minimax-m2.7` via `pi -p --no-session --no-tools` |
| prompt | [`extract/prompt.md`](../extract/prompt.md), sha256 in each extraction's `extractor` block |
| input | spans only (`rfpbrief payload`) — no label, no profile, no hand-authored extraction |
| run | 11 fixtures, sequential, ~20 s each |
| produced | `extractions/model/*.json`, each carrying the model id, prompt hash and timestamps |

## Citation integrity

**8 of 11 extractions passed the citation gate on the first attempt. 3 were refused.**

The three refusals are not one failure mode, and flattening them into "3 failures" would lose the
useful part:

| fixture | what went wrong | is the quote real? |
|---|---|---|
| `community-action-partnership-kern-…` | quoted `Information Systems Consultant`; the document has it uppercase | **yes** — a capitalisation change, not a fabrication |
| `hacc-rfp-26022-cloud-document-management` | cited page 1; the title block first appears on page 2 and repeats on every later page | **yes** — a wrong page, not an invented string |
| `palm-beach-mpo-rfp-2026-07-it-services` | quoted a comma-separated list that runs across a span boundary | **yes** — a list, not a sentence |

**No fabricated quotation appeared in any of the three.** That is the property the design was built
to guarantee, and the first model pass did not violate it: what it did was misquote presentation
(case, position, boundaries). The distinction matters, because the two failure kinds deserve
different responses — a fabricated quote should fail loudly forever, whereas a case-only difference
could reasonably be accepted with a flag saying the citation was not character-exact.

## Decisions and agreement

Against the committed labels, **8 of 8 usable extractions produced the labelled call**. The decision
layer is not the weak link in this pipeline; quoting is.

| comparison | result |
|---|---|
| hand-authored extractions → labels | 11/11 calls, 10/11 primary class |
| model extractions → labels | **8/8 calls**, 6/8 primary class, 7/8 classes accounted for |
| model requirements vs hand-authored, value by value | **33/55** |

The 33/55 is the interesting number, and it is not noise. Two kinds of disagreement recur:

- **`functional_stacks` — the hard one.** For Tahoe the model listed six products (Business Central,
  Office 365, UKG, Ecolane, Optibus, GMV Synchromatics); the hand oracle listed none. The model read
  "stacks mentioned in the document" where the vocabulary asks for "stacks the winner must configure
  *functionally*". This is a definitional failure on the single hardest term in the schema, and it is
  exactly the distinction that separates Energy Trust (configure D365 → no-bid) from CAPK (migrate
  onto it → bid). A mismatch here can flip a decision.
- **`delivery_model` — a genuine judgment difference.** For Maine the model said
  `continuous_operations` (operate and support, flat-rate licence) where the oracle said `project`
  (buy a product, with implementation). Both readings are defensible; the oracle is not obviously
  right, which is worth knowing before treating it as truth.

Also visible: the model **omits requirement keys** it judges false, despite the prompt requiring
every kind to appear. That is straightforward instruction-following, and the cheapest of these
problems to fix.

## The methodological gap this pass exposes

**The extractor is not deterministic.** With the same prompt and the same input, Tahoe failed four
citations on one run and passed on another, and the batch run produced a third outcome. So 8/11 is
**one sample of a noisy process**, not a rate.

That has to be fixed before any number from this pipeline is quoted as a result: pin the temperature
and seed, or run each fixture N times and report a distribution. `pi`'s CLI exposes neither today,
so the honest options are to add a temperature/seed flag, to move the extractor behind a client that
controls sampling, or to run repeats and report the spread. Until then, this file says what it is —
a first pass, with a caveat, on eleven fixtures.

## What the next pass should change

1. **Retry-on-refusal.** The gate already reports *where* a refused quote lives ("this quote does
   appear in p2-s0, p2-s1, p4-s0"). Feeding that back for one repair attempt would convert most of
   these three refusals into passes, and the repair rate becomes a metric of its own rather than a
   hidden second chance.
2. **Case-exact vs case-insensitive.** Decide deliberately whether a capitalisation change is a
   failure. If it is accepted, it should be accepted with a recorded flag, not by quietly loosening
   the rule.
3. **A `functional_stacks` worked example in the prompt**, since that is where the semantic
   disagreement is concentrated.
4. **Require every requirement key**, and check it mechanically rather than trusting the instruction.

---

# Second pass — with the repair channel (ADR 0006)

The same model, the same prompt, the same eleven fixtures, run again after the gate was wired back
into the extractor as a bounded repair attempt.

| | run 1 (no repair) | run 2 (one repair) |
|---|---|---|
| clean on attempt 1 | 8/11 | **5/11** |
| repaired on attempt 2 | — | 6/11 |
| refused after both | 3/11 | **0/11** |
| usable extractions | 8/11 | **11/11** |

**The repair channel works: 0 refusals, 11 usable.** Six of the eleven needed it, and each of those
carries `attempts: 2` with the refusal list, so a reader can see which ones had help.

**And the first-attempt figure is unstable.** 8/11 in one run, 5/11 in the other, same code and same
input. That is the nondeterminism this file already flagged, now demonstrated across two runs rather
than asserted once. Any headline citation-integrity number from this pipeline has to be a
**distribution over repeats**; a single pass is not a rate, and 9/11 versus 5/11 is not a small
spread. Pinning temperature or reporting N repeats remains the largest methodological gap in the
project.

## Decisions from the repaired set

| | hand-authored | model (repaired) |
|---|---|---|
| usable | 11/11 | 11/11 |
| labelled call matched | 11/11 | **9/11** |
| primary reason class | 10/11 | 7/11 |
| requirement values vs the oracle | — | **34/55** |

The earlier 33/55 in this file was measured before refusals were moved out of the extraction
directory, so it counted unvalidated values as data. 34/55 is the corrected figure.

## The two wrong calls, and they are the two hardest judgments

Both errors are **false no-bids** — the expensive direction for a bidder, since it declines work the
profile would have taken:

- **`inprs-rfp-23-04`** (truth: bid) → predicted no-bid, class *geography*. The solicitation requires
  that "Respondent staff must be able to travel to the INPRS offices located within Indianapolis" —
  a stated travel expectation on an advisory engagement. The model read that as a recurring on-site
  presence. The hand oracle cited the same line and set the flag false. **A travel clause is not a
  residency requirement**, and the prompt does not say so.
- **`community-action-partnership-kern-…`** (truth: bid) → predicted no-bid, class *functional stack
  not held*. This is the D365 case: the engagement migrates a call-centre database onto Dynamics 365
  and builds an assistant, which is platform engineering, but the model classified it as functional
  configuration. The profile's rule 4 carries the escape clause; the model did not apply it. This is
  precisely the divergence predicted above, and it cost a call rather than a field.

Also visible: `coastal-bend-college` reached the right call by the wrong reason — it is excluded as
an ERP functional implementation, and the model reported *product not services*.

## What this pass says the next change should be

1. **Two worked examples in the prompt**, for exactly the two failures above: a travel clause is not
   recurring on-site presence; migrating onto a vendor platform is not functional configuration of
   it. Both are definitional, both are cheap to state, and together they are the difference between
   9/11 and 11/11 in this run.
2. **Repeat the extraction N times and report the spread.** Two runs disagreed by four fixtures on
   first-attempt cleanliness. Until that is characterised, the honest headline is a range.
