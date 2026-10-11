# rfp-bid-brief — task runner
#
# `just status` says what exists and what does not; `just check` runs everything that can run today.
# The recipes for stages that do not exist yet exit non-zero rather than not existing, so a missing
# stage is visible instead of silently absent. A task runner that pretends is worse than one that
# says "not yet".

set shell := ["bash", "-uc"]
fixture := "fixtures/tahoe-transportation-district-it-consulting-2025.pdf"

# list the recipes
default:
    @just --list

# what exists today, and what does not
status:
    @tools/status.sh

# prove the fixtures are still the documents their issuers published
verify-fixtures:
    @tools/verify-fixtures.sh

# create the virtualenv from pyproject.toml
setup:
    @uv sync --quiet && echo "environment ready (.venv)"

# unit tests — offline, no model, no network
test:
    @uv run pytest

# build a span index for one fixture: just parse fixtures/<name>.pdf
parse fixture=fixture:
    @uv run rfpbrief build "{{fixture}}"

# locate a quote under the verbatim rule: just find "be on-site within four (4) hours"
find quote fixture=fixture:
    @uv run rfpbrief find "{{fixture}}" "{{quote}}"

# span size distribution for one fixture
stats fixture=fixture:
    @uv run rfpbrief stats "{{fixture}}"

# check every committed index is still reproducible
verify-spans:
    @for f in results/spans/*.json; do [ -e "$f" ] && uv run rfpbrief verify "$f"; done

# validate the committed extraction for one fixture
#
# every citation must locate in the span index, or this fails with the list of problems
extract fixture=fixture:
    @uv run rfpbrief extract "{{fixture}}"

# apply the frozen bidder profile to an extraction
#
# deterministic: the profile decides capability, not a model (adr/0002)
decide fixture=fixture:
    @uv run rfpbrief decide "{{fixture}}"

# render the one-page brief for one fixture
brief fixture=fixture:
    @uv run rfpbrief brief "{{fixture}}"

# validate every committed extraction
verify-extractions:
    @for f in extractions/*.json; do stem=$(basename "${f%.json}"); uv run rfpbrief extract "fixtures/$stem.pdf" | head -1; done

# render a brief for every fixture that has an extraction
briefs:
    @for f in extractions/*.json; do stem=$(basename "${f%.json}"); uv run rfpbrief brief "fixtures/$stem.pdf" --quiet; done

# rule-based baseline: the decision layer against every committed label
baseline:
    @uv run rfpbrief baseline

# is the intended decision model callable yet? (adr/0007)
#
# probes the provider rather than remembering: a listing can precede an API and an API can serve a
# model a catalogue has not listed yet. Exit 0 when callable, 1 when not.
provider-check:
    @uv run rfpbrief provider

# run the eval harness — not built yet
eval:
    @echo "just eval: not built yet — extraction and the decision layer come first."
    @echo "see README.md § Status, and adr/0003 for what must be true before a model-facing run."
    @exit 2

# build the static site from the eval artifacts — not built yet
site:
    @echo "just site: not built yet — the site is generated from eval artifacts, and there are none."
    @echo "see README.md § Status, and adr/0003 for the ordering."
    @exit 2

# everything that can be checked today
check: verify-fixtures test verify-spans verify-extractions baseline status
