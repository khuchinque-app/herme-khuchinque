#!/usr/bin/env bash
# skill-combo.sh — herme-khuchinque combo enforcement.
# Runs on every pre_llm_call: verifies the 4-skill combo is present and readable,
# runs the stack health check, and writes a fresh status block the system prompt
# (SOUL.md) points at. Fail-open: never blocks a turn.
set -uo pipefail
P="$HOME/.hermes/profiles/herme-khuchinque"
SKILLS="$P/skills/software-development"
STATUS="$P/cache/combo-status.md"
mkdir -p "$P/cache"

skills="planning-with-files rtk codegraph graphify"
missing=0
lines=()
for s in $skills; do
  f="$SKILLS/$s/SKILL.md"
  if [ -s "$f" ]; then
    desc=$(awk '
      /^description: *[>|-]$/ {blk=1; next}
      blk==1 && /^[[:space:]]+[A-Za-z]/ {sub(/^[[:space:]]+/,""); print; exit}
      /^description: */ {sub(/^description: */,""); sub(/^"/,""); print; exit}
    ' "$f" | cut -c1-110)
    lines+=("- $s: ${desc:-loaded}")
  else
    lines+=("- $s: MISSING ($f)")
    missing=1
  fi
done

stack="n/a"
if [ -x "$P/bin/agent-stack-doctor.sh" ]; then
  if "$P/bin/agent-stack-doctor.sh" >/dev/null 2>&1; then stack="healthy"; else stack="degraded"; fi
fi

{
  echo "## Active combo (auto-verified $(date '+%Y-%m-%d %H:%M'))"
  echo "Stack: $stack"
  printf '%s\n' "${lines[@]}"
  echo "Rule: for ANY non-trivial task — consult these 4 skills first (plan with planning-with-files; route shell output through rtk; use codegraph for repo traversal; query graphify base memory before exploring files)."
} > "$STATUS"

# stdout is not consumed for pre_llm_call — keep it quiet; status file is the vehicle.
exit 0
