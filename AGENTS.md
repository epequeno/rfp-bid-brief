# rfp-bid-brief — conventions

Loaded as a context file for agent sessions in this repository. Describes the rules of the place,
not the design; design lives in `docs/` (when it exists) and the rationale in `adr/`.

## Standing constraints

- **New fixtures cost a provenance row.** A document may only enter `fixtures/` with: the issuing
  organisation, the issuer's own published URL, the retrieval date, the page count, and its sha256
  added to the manifest in `fixtures/PROVENANCE.md`. `just verify-fixtures` fails an unlisted
  fixture, because a fixture nothing vouches for is worse than a missing one.
- **Solicitations only.** Documents issued *by* buyers. No vendor response, proposal, pricing
  schedule or contract from any supplier may enter this repository, ever — a response does not
  become publishable by sitting next to a publishable solicitation. This includes material from any
  prior commercial engagement.
- **No fixture is related to a prior employer or client engagement.** If in doubt, it does not go in.
- **The profile and the labels are frozen before anything model-facing runs.** If either changes,
  the eval is re-run and the previous numbers are marked superseded rather than quietly replaced.
  See `adr/0003`.
- **A quoted span must exist verbatim in its fixture.** A hallucinated citation is a failing test,
  not a review finding.
- **No number is reported without its conditions.** Class balance, operating point, and the
  confusion matrix travel with every metric. A bare accuracy figure is not allowed in this repo.

## Task runner

The runner is **`just`**, not `make`. Recipes: `just status`, `just verify-fixtures`, and
`just check` for everything runnable today. `just test`, `just eval` and `just site` exist and exit
non-zero until the stage they name is built — deliberately, so that a stage which does not exist is
visible rather than silently absent. A task runner that pretends is worse than one that says
"not yet".

This is a standing preference for new projects in this portfolio, not a local accident.

## ADR rules

- Numbering is **per-project**. In this repository, `ADR 0003`. From anywhere else, qualify it:
  "rfp-bid-brief ADR 0003".
- Statuses: `proposed` · `accepted` · `superseded` · `rejected` · `deprecated`.
- One decision per record. Do not edit the Context or Decision of an **accepted** ADR — supersede it
  with a new record that restates whatever still holds. Never renumber or delete an ADR.
- Drafts may be committed at `proposed`. Nothing depends on a `proposed` ADR.

## Commits

- Public repository. Treat every commit as published.
- No secrets, no absolute home paths, no LAN addresses, no private-context documents. The sibling
  repositories in this portfolio learned that lesson the expensive way (see
  `full-stack-serving`'s history).
- Prefer one artifact per commit, with the gate or check it passes named in the message.

## One build artifact in flight

The convention across this portfolio: one thing under construction at a time. Do not start the
static site, the MCP surface, or a second framework while the extraction and eval path is unfinished.
