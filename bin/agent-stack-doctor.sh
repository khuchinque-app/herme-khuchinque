#!/usr/bin/env bash
# agent-stack-doctor.sh — health check for the herme-khuchinque context stack.
# Verifies: rtk, headroom, codegraph, graphify binaries; MCP wiring; memory freshness.
set -uo pipefail
fail=0
ok()  { printf '  OK  %s\n' "$1"; }
bad() { printf '  !!  %s\n' "$1"; fail=1; }
check_bin() { command -v "$1" >/dev/null 2>&1 && ok "$1: $("$1" --version 2>&1 | head -1)" || bad "$1: missing"; }

echo "binaries:"
check_bin "$HOME/.local/bin/rtk"
check_bin "$HOME/.local/bin/headroom"
check_bin "$HOME/.npm-global/bin/codegraph"
check_bin "$HOME/.local/bin/graphify"
check_bin "$HOME/.local/bin/graphify-mcp"

echo "skills (profile):"
SKILLS="$HOME/.hermes/profiles/herme-khuchinque/skills/software-development"
for s in rtk codegraph graphify planning-with-files; do
  [ -f "$SKILLS/$s/SKILL.md" ] && ok "skill $s" || bad "skill $s missing"
done

echo "mcp wiring:"
CFG="$HOME/.hermes/profiles/herme-khuchinque/config.yaml"
for m in headroom codegraph graphify; do
  grep -q "^  $m:" "$CFG" && ok "mcp_servers.$m" || bad "mcp_servers.$m missing in profile config"
done

echo "base memory:"
G="$HOME/4project-labs/herme-khuchinque/graphify-out/graph.json"
if [ -f "$G" ]; then
  age=$(( $(date +%s) - $(stat -c %Y "$G") ))
  ok "graph.json ($(( $(stat -c %s "$G") / 1024 )) KB, ${age}s old)"
  [ "$age" -gt 604800 ] && bad "graph older than 7 days — run memory-update.sh"
else
  bad "graph.json missing — run memory-update.sh"
fi

exit $fail
