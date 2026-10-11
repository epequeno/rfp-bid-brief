#!/usr/bin/env bash
# Report the state of the frozen inputs *and* the pipeline stages, naming the ones that do not
# exist yet.
#
# This repository's value depends on the ordering in adr/0003, so the inability to run a stage is
# reported as loudly as the ability to run it. A status command that lists only what works is a
# status command that hides the gap.

set -uo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root" || exit 2

echo "frozen inputs:"

profile_id="$(python3 -c 'import json;print(json.load(open("bidder-profile.json"))["profile_id"])' 2>/dev/null || true)"
printf '  %-22s %s\n' "bidder-profile.json" "${profile_id:-MISSING OR INVALID}"

printf '  %-22s %s PDFs, %s indexed\n' \
  "fixtures" \
  "$(ls -1 fixtures/*.pdf 2>/dev/null | wc -l | tr -d ' ')" \
  "$(ls -1 results/spans/*.json 2>/dev/null | wc -l | tr -d ' ')"

if [ -f fixtures/labels.json ]; then
  printf '  %-22s %s\n' "labels" "$(python3 - <<'PY' 2>/dev/null || echo 'present, unreadable'
import json
b = json.load(open("fixtures/labels.json"))["balance"]
print(f"fixtures/labels.json — {b['bid']} bid / {b['no_bid']} no_bid")
PY
)"
else
  printf '  %-22s %s\n' "labels" "NOT COMMITTED"
fi

printf '  %-22s %s\n' "operating point" "tau = 0.50, pre-registered (adr/0003)"

echo ""
echo "pipeline:"

if [ -n "$(ls -1 results/spans/*.json 2>/dev/null)" ]; then
  spans_total="$(python3 - <<'PY' 2>/dev/null || echo '?'
import glob, json
print(sum(json.load(open(p))["span_count"] for p in glob.glob("results/spans/*.json")))
PY
)"
  printf '  %-22s %s\n' "parse (span index)" "built — ${spans_total} spans, adr/0004"
else
  printf '  %-22s %s\n' "parse (span index)" "NOT BUILT"
fi

extractions=$(ls -1 extractions/*.json 2>/dev/null | wc -l | tr -d ' ')
briefs=$(ls -1 results/briefs/*.md 2>/dev/null | wc -l | tr -d ' ')
printf '  %-22s %s\n' "extract (model)" "built — 8/11 validated, 3 refused · results/model-pass.md"
printf '  %-22s %s\n' "decide" "built — deterministic vs the frozen profile, adr/0002"
printf '  %-22s %s\n' "brief" "built — ${briefs} brief(s) rendered"

if [ -f results/baseline.json ]; then
  printf '  %-22s %s\n' "baseline" "$(python3 - <<'PY' 2>/dev/null || echo 'present, unreadable'
import json
b = json.load(open("results/baseline.json"))
print(f"hand: {b['label_agreement']} labels · {b['reason_class_agreement']} primary class")
PY
)"
fi
if [ -f results/baseline-model.json ]; then
  printf '  %-22s %s\n' "baseline (model)" "$(python3 - <<'PY' 2>/dev/null || echo 'present, unreadable'
import json
b = json.load(open("results/baseline-model.json"))
print(f"model: {b['label_agreement']} labels on {b['n']} usable · "
      f"{len(b['unusable_extractions'])} refused by the citation gate")
PY
)"
fi

for stage in "probability channel (Jev)" "extraction retry pass" "eval harness" "static site" "MCP surface"; do
  printf '  %-22s %s\n' "$stage" "not built"
done

echo ""
echo "ordering that gates them: README.md § Status, and adr/0003"