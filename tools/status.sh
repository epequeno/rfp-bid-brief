#!/usr/bin/env bash
# Report the state of the frozen inputs, and name what does not exist yet.
#
# This repository's value depends on the ordering in adr/0003, so the inability to run a stage is
# reported as loudly as the ability to run it. A status command that only lists what works is a
# status command that hides the gap.

set -uo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root" || exit 2

echo "frozen inputs:"

profile_id="$(python3 -c 'import json;print(json.load(open("bidder-profile.json"))["profile_id"])' 2>/dev/null || true)"
printf '  %-22s %s\n' "bidder-profile.json" "${profile_id:-MISSING OR INVALID}"

printf '  %-22s %s PDFs\n' "fixtures" "$(ls -1 fixtures/*.pdf 2>/dev/null | wc -l | tr -d ' ')"

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
echo "not built: pipeline (parse / extract / decide / brief), eval harness, static site, MCP surface"
echo "ordering that gates them: README.md § Status, and adr/0003"
