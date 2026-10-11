# rfp-bid-brief
#
# Today this repository holds the frozen inputs, so the only target that does real work is
# `verify-fixtures`. Targets for the pipeline, the eval and the site are listed below and refuse to
# run until they exist — a Makefile that pretends is worse than one that says "not yet".

SHELL := /bin/bash
PY    ?= python3

.PHONY: help status verify-fixtures test eval site

help:
	@echo "rfp-bid-brief — bid/no-bid brief generator"
	@echo ""
	@echo "  make status           what exists today, and what does not"
	@echo "  make verify-fixtures  prove the fixtures are still the documents their issuers published"
	@echo "  make test             unit tests            (not built yet)"
	@echo "  make eval             run the eval harness  (not built yet)"
	@echo "  make site             build the static site (not built yet)"

status:
	@echo "frozen inputs:"
	@echo "  bidder-profile.json   $$($(PY) -c "import json;print(json.load(open('bidder-profile.json'))['profile_id'])" 2>/dev/null || echo 'MISSING OR INVALID')"
	@echo "  fixtures              $$(ls -1 fixtures/*.pdf 2>/dev/null | wc -l | tr -d ' ') PDFs"
	@echo "  labels                $$(test -f fixtures/labels.json && echo 'fixtures/labels.json' || echo 'NOT YET COMMITTED')"
	@echo ""
	@echo "not built: pipeline (parse/extract/decide/brief), eval harness, static site, MCP surface"
	@echo "see README.md § Status and adr/0003 for the ordering"

verify-fixtures:
	@tools/verify-fixtures.sh

test eval site:
	@echo "make $@: not built yet — this repository currently holds the frozen inputs only."
	@echo "See README.md § Status, and adr/0003 for what must be true before any model-facing run."
	@exit 2
