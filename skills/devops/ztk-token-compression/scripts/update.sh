#!/usr/bin/env bash
# update.sh — update the ztk binary and verify the Hermes hook still works.
# Invoke through the `terminal` tool.
set -euo pipefail

ZTK="$HOME/.local/bin/ztk"

if brew list ztk >/dev/null 2>&1; then
  echo "brew-managed: use 'brew upgrade codejunkie99/ztk/ztk'"
else
  "$ZTK" update
fi

echo "--- version ---"
"$ZTK" version
echo "--- hook health ---"
hermes hooks doctor 2>&1 | grep -A5 ztk-rewrite || hermes hooks doctor
echo "--- smoke test ---"
"$ZTK" run ls "$HOME" | head -1
"$ZTK" stats
