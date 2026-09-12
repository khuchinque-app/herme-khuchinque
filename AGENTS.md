# herme-khuchinque — agent context stack

Installed 2026-09-10. Health check: `~/.hermes/profiles/herme-khuchinque/bin/agent-stack-doctor.sh`

## Tools
| Tool | What it does | Binary |
|---|---|---|
| rtk 0.48.0 | Compresses shell-command output (60-90% fewer tokens) | `~/.local/bin/rtk` |
| headroom 0.37.0 | Context compression layer; MCP server | `~/.local/bin/headroom` |
| codegraph 1.6.0 | Per-repo AST code graph; 8 MCP tools; init per project with `codegraph init -i` | `~/.npm-global/bin/codegraph` |
| graphify 0.9.57 | Codebase → knowledge graph; CLI query + MCP | `~/.local/bin/graphify` |
| agent-reach 1.5.0 | Social/web reach: reddit, facebook, twitter, linkedin, instagram, youtube, rss, web, github, bilibili, xiaohongshu, v2ex, xueqiu… | `~/.local/bin/agent-reach` |
| yt-dlp | Backing engine for agent-reach's YouTube channel | `~/.local/bin/yt-dlp` |

## Base memory (graphify)
- Graph of this workspace at `~/4project-labs/herme-khuchinque/graphify-out/` (code-only AST mode, no LLM/API dependency, ollama NOT used).
- Rebuild: `bin/memory-update.sh` (cron-safe; also `graphify update` for incremental).
- Query: `bin/memory-query.sh "question"` or the `graphify` MCP server (already wired).
- Scope controlled by `~/4project-labs/herme-khuchinque/.graphifyignore`.

## Skill-combo enforcement (always-on)
- `pre_llm_call` hook → `bin/skill-combo.sh` (approved/allowlisted): verifies the 4-skill combo (planning-with-files, rtk, codegraph, graphify) every turn and refreshes `cache/combo-status.md`.
- `SOUL.md` carries the mandatory rule: read all 4 skills + combo-status.md before any non-trivial task.

## Scheduled jobs
- `memory-refresh` (hermes cron, every 2h, --no-agent) → `scripts/memory-refresh.sh` → `bin/memory-update.sh`.

## agent-reach channels
- Active out of the box: YouTube, V2EX, RSS/Atom, web (Jina), bilibili, GitHub (gh).
- Reddit / Facebook / Twitter / LinkedIn / Instagram / 小红书 need user cookies — configure explicitly, one platform at a time (never auto-import):
  `agent-reach configure twitter-cookies` · `agent-reach configure --from-browser chrome --platform bilibili` …
- Status: `agent-reach doctor` · Skill installed at `skills/web/agent-reach/`.

## codegraph indexes
- `~/4project-labs/herme-khuchinque/mission-control/` (init 2026-09-10; `codegraph sync` after edits).

## MCP servers (profile config.yaml → mcp_servers)
- `headroom` → `headroom mcp serve`
- `codegraph` → `codegraph serve --mcp` (timeout 120)
- `graphify` → `graphify-mcp` (serves the workspace graph)

## Skills (profile skills/software-development/)
`rtk`, `codegraph`, `graphify`, `planning-with-files` (software-development) and `agent-reach` (web) — all local; PWF plan files live in `~/4project-labs/herme-khuchinque/plans/`.

## House rules
- Skins live in `skins/` only: `ChinQue` (active), `ChinQueViolet` (variant). Never edit a skin in place without a dated backup OUTSIDE skins/.
- Old (retired) profile home is parked at `~/4project-labs/herme-khuchinque/.hermes/` — read-only reference; skin archive in `.skin-work/archive-20260910/`.
