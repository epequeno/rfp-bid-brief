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
| [0003](0003-pre-register-the-operating-point.md) | Pre-register the operating point, and freeze the profile before labelling | proposed |
