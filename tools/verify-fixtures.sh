#!/usr/bin/env bash
# Verify every fixture is byte-identical to the document its issuer published.
#
# A fixture edited in place is no longer the document the issuer published, and any span citation
# against it is void. So this is a gate, not a formality: it runs before the eval, not after.
#
# Reads the manifest block in fixtures/PROVENANCE.md. Exits 0 if every hash matches and every
# fixture is listed, 1 on any mismatch, 2 if the manifest cannot be found.

set -uo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root/fixtures" || exit 2

manifest="$(
  awk '
    /^## Integrity manifest/ { insec = 1; next }
    insec && /^```$/       { fence = !fence; next }
    insec && fence         { print }
  ' PROVENANCE.md
)"

if [ -z "$manifest" ]; then
  echo "FAIL  no manifest block found in fixtures/PROVENANCE.md" >&2
  exit 2
fi

fail=0
checked=0

while read -r hash file; do
  [ -n "${file:-}" ] || continue
  checked=$((checked + 1))
  if [ ! -f "$file" ]; then
    echo "MISSING  $file"
    fail=1
    continue
  fi
  actual="$(shasum -a 256 "$file" | cut -d' ' -f1)"
  if [ "$actual" = "$hash" ]; then
    echo "ok       $file"
  else
    echo "CHANGED  $file"
    echo "         expected $hash"
    echo "         actual   $actual"
    fail=1
  fi
done < <(printf '%s\n' "$manifest")

# A fixture present but unlisted is worse than a missing one: nothing vouches for it.
for f in *.pdf; do
  [ -e "$f" ] || continue
  if ! printf '%s\n' "$manifest" | grep -q "[[:space:]]$f\$"; then
    echo "UNLISTED $f (no provenance row and no hash)"
    fail=1
  fi
done

if [ "$fail" -eq 0 ]; then
  echo "verify-fixtures: $checked fixtures match their published hashes"
else
  echo "verify-fixtures: FAILED — see above" >&2
fi

exit "$fail"
