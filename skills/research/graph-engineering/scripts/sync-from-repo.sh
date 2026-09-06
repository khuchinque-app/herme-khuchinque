#!/usr/bin/env bash
# sync-from-repo.sh — refresh graph-engineering skill references from upstream
# (github.com/codejunkie99/graph-engineering, master branch).
#
# Fetches the five reference files to /tmp and prints the skill_manage calls
# needed to persist them (the agent runs those; this script never writes the
# skill directory directly, keeping skill_manage as the single writer).
set -euo pipefail

BASE="https://raw.githubusercontent.com/codejunkie99/graph-engineering/refs/heads/master/graph-engineering"
OUT="$(mktemp -d)"
FILES=(references/task-graphs.md references/modeling.md references/extraction.md references/fusion-and-llm.md references/curriculum.md)

echo "Fetching into $OUT"
for f in "${FILES[@]}"; do
  mkdir -p "$OUT/$(dirname "$f")"
  curl -fsSL "$BASE/$f" -o "$OUT/$f"
  echo "  $f  $(wc -c < "$OUT/$f") bytes"
done

echo
echo "Done. For each file, read it and persist via skill_manage:"
echo "  action=write_file, name=graph-engineering, file_path=references/<name>.md"
echo "Compare against the current skill copies first (skill_view) and only update changed files."
