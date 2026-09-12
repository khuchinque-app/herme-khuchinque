#!/usr/bin/env bash
# memory-update.sh — refresh the graphify base memory (fully local, no LLM/API).
# Deterministic AST re-extract of changed files + recluster. Cron-safe.
set -euo pipefail
WS="$HOME/4project-labs/herme-khuchinque"
BIN="$HOME/.local/bin"
cd "$WS"
"$BIN/graphify" update .
"$BIN/graphify" cluster-only . --no-label --no-viz
echo "memory updated: $(stat -c %y "$WS/graphify-out/graph.json" | cut -d. -f1)"
