#!/usr/bin/env bash
# Run the pinned extraction model on one fixture, then validate what it returns.
#
# The model gets the committed prompt (extract/prompt.md) and one fixture's spans, and nothing else:
# no label, no bidder profile, no hand-authored extraction. It runs with --no-tools, so it cannot
# read the repository even if it tried. Whatever comes back is saved verbatim and then put through
# the same load gate as a hand-authored extraction — a fabricated quote is refused, and the refusal
# is a result rather than an incident.
#
#   tools/extract_with_model.sh fixtures/<name>.pdf [model]
#
# Output: extractions/model/<name>.json  (+ a .raw file when the response was not valid JSON)

set -uo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root" || exit 2

fixture="${1:?usage: extract_with_model.sh <fixture.pdf> [model]}"
model="${2:-${EXTRACT_MODEL:-openrouter/minimax/minimax-m2.7}}"
stem="$(basename "${fixture%.pdf}")"
outdir="extractions/model"
mkdir -p "$outdir"
out="$outdir/$stem.json"

prompt="$(cat extract/prompt.md)"
payload="$(uv run rfpbrief payload "$fixture")" || exit 2

started=$(date -u +%Y-%m-%dT%H:%M:%SZ)
response="$(pi -p --no-session --no-tools --model "$model" --mode text "$prompt

Here is the document.

$payload")"
status=$?
finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)

if [ "$status" -ne 0 ]; then
  echo "model call failed (status $status)" >&2
  exit 1
fi

# Models wrap JSON in fences often enough that stripping them is expected, not a rescue.
body="$(printf '%s' "$response" | sed -e 's/^```json[[:space:]]*//' -e 's/^```[[:space:]]*//' -e 's/```[[:space:]]*$//')"
printf '%s\n' "$body" > "$out"
if ! python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$out" 2>/dev/null; then
  printf '%s\n' "$body" > "$out.raw"
  rm -f "$out"
  echo "$stem: response was not valid JSON — kept as $out.raw" >&2
  exit 1
fi

# Record what produced it. A number without the model id and the prompt hash is not a result.
python3 - "$out" "$model" "$started" "$finished" <<'PY'
import hashlib, json, sys
path, model, started, finished = sys.argv[1:5]
data = json.load(open(path))
prompt = open("extract/prompt.md", "rb").read()
data["produced_by"] = f"pi -p --no-session --no-tools --model {model}"
data["schema"] = "extraction/1"
data["extractor"] = {
    "model": model,
    "prompt": "extract/prompt.md",
    "prompt_sha256": hashlib.sha256(prompt).hexdigest(),
    "started_utc": started,
    "finished_utc": finished,
    "inputs": "spans only (rfpbrief payload): no label, no bidder profile, no hand-authored extraction",
}
json.dump(data, open(path, "w"), indent=2, ensure_ascii=False)
open(path, "a").write("\n")
PY

# The same gate a hand-authored extraction passes.
if uv run rfpbrief extract "$fixture" --extractions "$outdir"; then
  echo "$stem: validated — $(python3 -c "
import json,sys
d=json.load(open('$out'))
n=sum(len(v['citations']) for g in ('facts','requirements') for v in d[g].values())
print(f\"{len(d['facts'])} facts, {len(d['requirements'])} requirements, {n} citations\")")"
else
  echo "$stem: REFUSED by the citation gate — see above. The extraction is kept for the failure count." >&2
  exit 1
fi
