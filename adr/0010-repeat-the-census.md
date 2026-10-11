# 0010 — Repeat the census, and publish a range wherever the repeats disagree

- **Status:** accepted (2026-10-11)
- **Date:** 2026-10-11

## Context

ADR 0009 declared the censuses and published single-run figures: 7 of 14 models perfect at τ = 0.50,
one fixture splitting 7 bid / 7 no-bid, Brier spanning 0.0021–0.0724. It also said, in its own
consequences, that the decision layer's nondeterminism was untested — and left it there.

That was the wrong place to leave it. The extractor is demonstrably nondeterministic: three identical
runs gave 7, 8 and 8 clean first attempts out of 11, and label agreement of 78%, 100%, 100%. The
pipeline therefore contains one component whose variability is measured and one whose variability was
assumed away, and the assumed-away component is the one whose probabilities get published.

Four censuses of an identical frozen state cost $0.028 and took eight minutes.

## Decision

1. **The census is repeated at least three times, and every run is committed**, alongside the
   canonical run the briefs render from. Archived content-addressed by state *and* answers, so no run
   can overwrite another.
2. **Where repeats disagree, the published figure is a range.** Not the median, not the best run: a
   range, with the runs listed. A statistic that moves between runs is not a statistic with a value.
3. **The brief reports the canonical run and says that it is one draw.** A page that presents a census
   count as a fact about the world, when a second call moves it, is the same error as a citation that
   does not resolve.
4. **A model whose probabilities move by more than the margin to τ across repeats is not a candidate
   for the probability channel.** The channel must be able to reproduce its own verdict.

## Consequences

**What the repeats found.** Five of fourteen models are exactly reproducible to the last digit; nine
drift by ≤ 0.07; two drift by ~0.44, and one of those (`inception/mercury-decide`) crossed τ on one
fixture in one run out of four. Out of 616 decisions, exactly one changed sides. The structure was
identical in all four runs — the same ten fixtures unanimous, the same single fixture split — while the
counts attached to it moved: 7 of 14 perfect became 7–8 of 14, and the split's bid count went 7, 6, 6, 7.

**The channel survives the test that matters.** `typesafe/jev-1.13` drifted 0.07 and produced the same
verdict on all eleven fixtures in all four runs. The comparator drifted 0.16 with the same result. Rule
4 is therefore satisfied by both pinned models rather than merely assumed of them.

**This qualifies ADR 0009 rather than correcting it.** 0009 is accepted, so its figures stand as the
single-run record and the ranges live here. An accepted decision record that is edited whenever a
later measurement disagrees is no longer a record of what was decided, and this repository's whole
argument is that provenance survives revision.

**Per-model calibration claims are weaker than they looked.** Perplexity's Brier is 0.0021 in every
run — a real, reproducible property. `mercury-decide` spans 0.0007–0.0257 across four repeats of the
same input, which is a 37× range, and any ranking that placed it by a single run was partly ranking the
draw. Where a number is stable this is worth knowing; only repeats can tell you which numbers those are.

**Cost is not the constraint, so this should have been done first.** Four censuses cost less than three
cents. The earlier decision to measure the extractor's variance while leaving the decision layer's
unmeasured was not a budget decision; it was an assumption that happened to be affordable to check.
