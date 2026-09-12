#!/usr/bin/env bash
# memory-query.sh — ask the graphify base memory a question.
# Usage: memory-query.sh "how does X work" [--budget N]
# Reads: ~/4project-labs/herme-khuchinque/graphify-out/graph.json
set -euo pipefail
WS="$HOME/4project-labs/herme-khuchinque"
GRAPH="$WS/graphify-out/graph.json"
[ -f "$GRAPH" ] || { echo "no graph at $GRAPH — run memory-update.sh first" >&2; exit 1; }
exec "$HOME/.local/bin/graphify" query "$*" --graph "$GRAPH"
