# Architecture decision records

One decision per record, in the order they were taken. The shape is Context / Decision /
Consequences.

## Rules

- **Numbering is per-project.** Inside this repository, `ADR 0003`. Anywhere else, qualify it:
  "rfp-bid-brief ADR 0003". Eight independent ADR schemes exist across this author's repositories,
  so an unqualified number resolves wrongly by default.
- **Statuses:** `proposed` · `accepted` · `superseded` · `rejected` · `deprecated`.
- **An accepted ADR is not edited.** Its Context and Decision are fixed. To change the decision,
  write a new record that supersedes it — and restate in the new record whatever part of the old one
  still holds, so no decision is lost by omission.
- **Never renumber, never delete.** A withdrawn decision is `superseded` or `deprecated`, not erased.
- **A `proposed` ADR holds no weight.** Nothing may depend on one. Drafts are committed at
  `proposed` so the reasoning is reviewable before it costs anything.

## Index

| # | Decision | Status |
|---|---|---|
| [0001](0001-span-id-citations.md) | Span-ID citations as a structural guarantee | accepted |
| [0002](0002-required-bidder-profile.md) | A bidder profile is a required input | accepted |
| [0003](0003-pre-register-the-operating-point.md) | Pre-register the operating point, and freeze the profile before labelling | accepted |
| [0004](0004-citations-locate-inside-spans.md) | Citations locate a quote inside a span, at word boundaries *(first way to pass; ADR 0005 adds a second)* | accepted |
| [0005](0005-citations-verify-at-page-level.md) | A citation is verified at page level, because spans are ours and pages are the document's | accepted |
| [0006](0006-the-gate-is-a-repair-channel.md) | The citation gate is a repair channel, bounded to one attempt | accepted |
| [0007](0007-the-probability-channel-is-pluggable.md) | The probability channel is pluggable, and its first choice is not callable yet | accepted |
| [0008](0008-two-decision-models-are-callable.md) | Two decision models are callable today, on a surface the probe did not know about | accepted |
| [0009](0009-the-decision-layer-is-a-census.md) | The decision layer is a census, not a choice, and both judges see the same profile | accepted |
| [0010](0010-repeat-the-census.md) | Repeat the census, and publish a range wherever the repeats disagree | accepted |
| [0011](0011-the-contested-fixture-is-a-finding.md) | The contested fixture is a finding, not a defect to be resolved | accepted |
| [0012](0012-the-fifth-exclusion-class-and-its-re-freeze.md) | The fifth exclusion class, and the re-freeze it forces | accepted |
| [0013](0013-unreachable-outranks-unsuitable.md) | Unreachable outranks unsuitable, and a class must be visible to every judge | accepted |
| [0014](0014-a-sixth-class-and-when-a-re-freeze-is-needed.md) | A sixth class: staff augmentation, and when a re-freeze is actually needed | accepted |
| [0015](0015-this-is-an-evaluation-not-an-agent-application.md) | This is a decision-layer evaluation, not an agent application | accepted |
