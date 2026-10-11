#!/usr/bin/env bash
# Run the model-backed extractor over every fixture, with one bounded repair attempt (ADR 0006).
#
#   tools/extract_with_model.sh              # all fixtures
#   tools/extract_with_model.sh <fixture>    # one
#
# The work is in `rfpbrief model-extract`: a refused citation is fed back once with its diagnosis,
# and a refused extraction is written to extractions/model/_refused/ so it can never be mistaken for
# validated data. This script only sequences that and counts.
#
# Model: EXTRACT_MODEL (default openrouter/minimax/minimax-m2.7).

set -uo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root" || exit 2

model="${EXTRACT_MODEL:-openrouter/minimax/minimax-m2.7}"
targets=("$@")
if [ ${#targets[@]} -eq 0 ]; then
  targets=(fixtures/*.pdf)
fi

first=0; repaired=0; refused=0; crashed=0
for f in "${targets[@]}"; do
  stem="$(basename "${f%.pdf}")"
  if uv run rfpbrief model-extract "$f" --model "$model" >/tmp/model-extract.log 2>&1; then
    if grep -q "repaired on attempt 2" /tmp/model-extract.log; then
      repaired=$((repaired + 1)); echo "repaired  $stem"
    else
      first=$((first + 1)); echo "first-try $stem"
    fi
  elif grep -q "REFUSED after" /tmp/model-extract.log; then
    refused=$((refused + 1))
    echo "REFUSED   $stem"
    grep -E '^  - ' /tmp/model-extract.log | head -2 | sed 's/^/            /'
  else
    # Anything else is a crash, and counting a crash as a refusal invents a measurement.
    crashed=$((crashed + 1))
    echo "CRASHED   $stem"
    tail -3 /tmp/model-extract.log | sed 's/^/            /'
  fi
done

total=$((first + repaired + refused + crashed))
echo ""
echo "attempt 1 clean: $first/$total · repaired on attempt 2: $repaired/$total · refused after both: $refused/$total · crashed: $crashed/$total"
[ $((refused + crashed)) -eq 0 ] || exit 1
