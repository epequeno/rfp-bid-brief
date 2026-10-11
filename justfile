# rfp-bid-brief — task runner
#
# Today this repository holds the frozen inputs, so the only recipe that does real work is
# `verify-fixtures`. Recipes for the pipeline, the eval and the site are listed and refuse to run
# until they exist: a task runner that pretends is worse than one that says "not yet".

set shell := ["bash", "-uc"]

# list the recipes
default:
    @just --list

# what exists today, and what does not
status:
    @tools/status.sh

# prove the fixtures are still the documents their issuers published
verify-fixtures:
    @tools/verify-fixtures.sh

# unit tests — not built yet
test:
    @echo "just test: not built yet — this repository currently holds the frozen inputs only."
    @echo "see README.md § Status, and adr/0003 for what must be true before a model-facing run."
    @exit 2

# run the eval harness — not built yet
eval:
    @echo "just eval: not built yet — no pipeline to evaluate."
    @echo "see README.md § Status, and adr/0003 for what must be true before a model-facing run."
    @exit 2

# build the static site from the eval artifacts — not built yet
site:
    @echo "just site: not built yet — the site is generated from eval artifacts, and there are none."
    @echo "see README.md § Status, and adr/0003 for the ordering."
    @exit 2

# everything that can be checked today
check: verify-fixtures status
