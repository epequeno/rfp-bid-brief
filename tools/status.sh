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
  printf '  %-22s %s\n' "parse (span index)" \
    "$(python3 - <<'PY' 2>/dev/null || echo 'built'
import glob, json
print(f"built — {sum(json.load(open(p))['span_count'] for p in glob.glob('results/spans/*.json'))} spans, adr/0004")
PY
)"
else
  printf '  %-22s %s\n' "parse (span index)" "NOT BUILT"
fi

printf '  %-22s %s\n' "extract" \
  "$(ls -1 extractions/*.json 2>/dev/null | wc -l | tr -d ' ') hand-authored extraction(s)"

if [ -f results/variance.json ]; then
  printf '  %-22s %s\n' "extract (model)" \
    "$(python3 - <<'PY' 2>/dev/null || echo 'built — results/model-pass.md'
import json
v = json.load(open("results/variance.json"))
c = v["clean_first_attempt"]
print(f"built — clean 1st attempt {c['min']}-{c['max']}/11 over {len(v['runs'])} runs, adr/0006")
PY
)"
else
  printf '  %-22s %s\n' "extract (model)" "built — results/model-pass.md"
fi

printf '  %-22s %s\n' "decide" "built — deterministic vs the frozen profile, adr/0002"

if [ -f results/baseline-model.json ]; then
  printf '  %-22s %s\n' "brief" "$(ls -1 results/briefs/*.md 2>/dev/null | wc -l | tr -d ' ') brief(s) rendered"
  printf '  %-22s %s\n' "baseline (oracle)" \
    "$(python3 - <<'PY' 2>/dev/null || echo 'results/baseline.json'
import json
b = json.load(open("results/baseline.json"))
print(f"hand-authored: {b['label_agreement']} labels, {b['reason_class_agreement']} primary class")
PY
)"
  printf '  %-22s %s\n' "baseline (model)" \
    "$(python3 - <<'PY' 2>/dev/null || echo 'results/baseline-model.json'
import json
b = json.load(open("results/baseline-model.json"))
print(f"run 1 (of 3): {b['n']} usable, {b['label_agreement']} labels, "
      f"{len(b['unusable_extractions'])} refused")
PY
)"
fi

if [ -f results/calibration.json ]; then
  printf '  %-22s %s\n' "decision census" "$(python3 -c "
import json
c = json.load(open('results/calibration.json'))
perfect = sum(1 for m in c['models'] if m['correct_at_tau'] == m['answered'])
d = c['disagreement']
print(f\"{len(c['models'])} models x {c['sample']['fixtures']} fixtures, {perfect} perfect at tau, \"
      f\"{d['unanimous']} unanimous / {d['split']} split (adr/0009)\")")"
fi

for stage in "eval harness" "static site" "MCP surface"; do
  printf '  %-22s %s\n' "$stage" "not built"
done

echo ""
echo "ordering that gates them: README.md § Status, and adr/0003"
