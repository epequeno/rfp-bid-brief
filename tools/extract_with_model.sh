#!/usr/bin/env bash
# Run the model-backed extractor over every fixture, once or repeatedly.
#
#   tools/extract_with_model.sh                              # all fixtures, one run, canonical output
#   tools/extract_with_model.sh <fixture>                    # one fixture
#   REPEATS=3 tools/extract_with_model.sh                    # three runs, for the variance measurement
#
# The work is in `rfpbrief model-extract`: a refused citation is fed back once with its diagnosis,
# and a refused extraction is written to `_refused/` so it can never be mistaken for validated data.
# This script sequences that and counts. A crash is counted separately from a refusal — counting a
# crash as a refusal invents a measurement.
#
# Model: EXTRACT_MODEL (default openrouter/minimax/minimax-m2.7). Repeats: REPEATS (default 1).

set -uo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root" || exit 2

model="${EXTRACT_MODEL:-openrouter/minimax/minimax-m2.7}"
repeats="${REPEATS:-1}"
targets=("$@")
if [ ${#targets[@]} -eq 0 ]; then
  targets=(fixtures/*.pdf)
fi

grand_crashed=0; grand_refused=0
for rep in $(seq 1 "$repeats"); do
  if [ "$repeats" -eq 1 ]; then
    outdir="extractions/model"
  else
    outdir="extractions/repeats/run-$rep"
  fi
  mkdir -p "$outdir"

  first=0; repaired=0; refused=0; crashed=0
  echo "── run $rep/$repeats → $outdir"
  for f in "${targets[@]}"; do
    stem="$(basename "${f%.pdf}")"
    if uv run rfpbrief model-extract "$f" --model "$model" --out-dir "$outdir" \
        >/tmp/model-extract.log 2>&1; then
      if grep -q "repaired on attempt 2" /tmp/model-extract.log; then
        repaired=$((repaired + 1)); echo "  repaired  $stem"
      else
        first=$((first + 1)); echo "  first-try $stem"
      fi
    elif grep -q "REFUSED after" /tmp/model-extract.log; then
      refused=$((refused + 1))
      echo "  REFUSED   $stem"
      grep -E '^  - ' /tmp/model-extract.log | head -2 | sed 's/^/              /'
    else
      crashed=$((crashed + 1))
      echo "  CRASHED   $stem"
      tail -3 /tmp/model-extract.log | sed 's/^/              /'
    fi
  done

  total=$((first + repaired + refused + crashed))
  echo "  attempt 1 clean: $first/$total · repaired: $repaired/$total · refused: $refused/$total · crashed: $crashed/$total"
  grand_crashed=$((grand_crashed + crashed))
  grand_refused=$((grand_refused + refused))
done

# A refusal is data when measuring variance and a failure when producing the canonical pass.
# A crash is always a failure: it means the pipeline broke, not that the model did.
[ "$grand_crashed" -eq 0 ] || exit 1
if [ "$repeats" -eq 1 ] && [ "$grand_refused" -gt 0 ]; then exit 1; fi
