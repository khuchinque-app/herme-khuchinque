# herme-khuchinque — a Hermes Agent profile, warped

A complete [Hermes Agent](https://hermes-agent.nousresearch.com) profile snapshot:
the **ChinQue** time-heist skin, every custom skill, the token-compression hook,
persona files, and config. Drop it in and your agent wakes up already dressed.

> This repo contains **no secrets**. Real keys live in `.env` (never committed);
> see `.env.example` for the shape.

## What's inside

```
herme-khuchinque/
├── config.yaml          # profile config (providers, models, hooks) — key-free, uses ${VAR}
├── SOUL.md              # agent persona / voice directives
├── memories/
│   ├── MEMORY.md        # agent's persistent notes (environment, lessons)
│   └── USER.md          # user profile/preferences the agent carries
├── skins/
│   └── ChinQue.yaml     # the theme: cyberpunk Time-Heist, cyan + gold, blue-rain spinner
├── skills/              # 8 custom skills (see below)
├── agent-hooks/
│   └── ztk-rewrite.py   # pre_tool_call hook: auto-compresses terminal output via ztk
├── photon/              # photon sidecar (mjs, no node_modules)
└── cron/                # scheduled jobs (empty in this snapshot)
```

## The ChinQue skin

Active skin (`display.skin: ChinQue`). Highlights:

- **Gold replies** — `banner_text: #FFD700` streams every assistant answer in gold.
- **Time-traveler hero** — ASCII portrait rendered from a generated image: coat,
  goggles, glowing pocket watch; cyan rim-light (`#00BCD4`/`#00E5FF`), gold watch glow.
- **Blue matrix-rain spinner** — working-line wings cycle `┆ → ╻ → ┃ → ╹` (a falling
  raindrop per tick), thinking faces `(┆)(╻)(┃)(╹)(⋮)`, hint line tinted `#00B8D4`.
- **Full persona** — custom tool names (`terminal → Time-Heist`, `web_search →
  Timeline-Scan`, …), tool glyphs, temporal thinking verbs
  ("rewinding the timeline", "consulting the Chronokeeper"), welcome/goodbye lines,
  ⏳ prompt symbol and status glyph.

## Skills

| Skill | What it does |
|---|---|
| `hermes-agent` | Use, configure, theme, extend and orchestrate Hermes itself |
| `hermes-skin-registration` | Validate-then-register pipeline for skin YAMLs + personalization-hook reference |
| `hermes-health-check` | Full system health/diagnostic report |
| `swarm-types-catalog` | The 14 Swarms framework types and when to use each |
| `agent-harness-design-intelligence` | ECC + design workflows for harnessing agents |
| `graph-engineering` | Knowledge graphs; orchestrating agent task graphs |
| `ztk-token-compression` | Terminal-output token compression via `ztk` |
| `anysearch` | AnySearch API search/extract, key registration, client setup |
| `agentmail-rest` | AgentMail inbox/message/send REST workflows |

## Install

```bash
# 1. point HERMES_HOME at your profile dir (e.g. ~/.hermes/profiles/herme-khuchinque)
git clone https://github.com/khuchinque-app/herme-khuchinque.git
cd herme-khuchinque

# 2. copy everything into the profile
mkdir -p "$HERMES_HOME"
cp -a config.yaml SOUL.md skins skills memories agent-hooks photon cron "$HERMES_HOME/"

# 3. secrets: create your own .env (never commit it)
cp .env.example "$HERMES_HOME/.env"   # then fill in real values

# 4. optional: ztk token compression (the agent-hook expects it on PATH)
#    see skills/devops/ztk-token-compression/SKILL.md
```

Then run `hermes` — the banner should show the time-traveler and the gold replies.

## Engine note

This profile's skin uses **local engine hooks** (custom banner label, logo alignment,
per-tool display names, status/thinking glyphs, hint color) patched into the installed
`hermes_cli` — they are opt-in: absent keys = stock behavior. A `hermes update`
overwrites patched files; re-apply notes are in
`skills/devops/hermes-skin-registration/references/personalization-hooks.md`.

## Excluded from this warp (by design)

`state.db` + sessions (chat history), `cache/`, `logs/`, `home/` (1 GB of toolchains),
`bin/`, `lsp/`, `sandboxes/`, `auth.json`, `.env`, `pastes/`, `skills/.hub` index cache.
Those are runtime/identity data, not the profile's definition.
