<div align="center">

```
                       ::
                     ;: :::
                    ::+**;::
                    #%%*+%@*
                     %%##%#
                     ;%%%#:
                     :;%%+
                   :  :+*
                 ::::::::::::::
                :::;;;;*+;;;:::
              ::::;*#+*%%#*#+;:::
              ::::;#%%*+++%%*::::
               :::+#%%@@@@%%#;:::
               :::****#*##**;::::
                 ::::::;;+;::: :
                  : ::::::::
```

# ⏳ herme-khuchinque

**A complete Hermes Agent profile, warped — and now self-healing.**

*The ChinQue Time-Heist skin · 75 skills · persistence watchdog · scout cron · ECC memory vault · zero secrets*

</div>

---

> *"Time stop for no one. No one but me."*

This repository is a portable snapshot of a fully-configured [Hermes Agent](https://hermes-agent.nousresearch.com)
profile. Clone it into `$HERMES_HOME` and the agent wakes up already dressed: gold replies,
a time-traveler banner, a blue matrix-rain spinner, renamed tools, custom persona, a battle-tested
skill library, and the infrastructure that keeps it alive when the gateway dies or a model provider
goes dark. Everything that *defines* the agent is here; everything that is runtime dirt (chat
databases, caches, toolchains, credentials) is not.

---

## 📦 Repository layout

```
herme-khuchinque/
├── README.md
├── AGENTS.md                     # workspace context (brain integration + memory-first protocol)
├── .gitignore                    # keeps runtime/identity data out of future warps
├── .env.example                  # the shape of the secrets file (values never committed)
├── config.yaml                   # profile config — providers, models, aliases, hooks, toolsets
├── SOUL.md                       # agent persona / voice directives
├── skins/
│   ├── ChinQue.yaml              # ★ the active theme (spec below)
│   └── ChinQueViolet.yaml        # violet variant
├── bin/                          # 🔧 custom tooling (the ops layer)
│   ├── hermes-persistence.py     #   watchdog: gateway restart + model fallback + TG alerts
│   ├── agent-stack-doctor.sh     #   health check (binaries, combo skills, MCP wiring, memory)
│   ├── skill-combo.sh            #   pre_llm_call hook: verifies the 4-skill combo every turn
│   ├── memory-query.sh           #   graphify base-memory queries
│   └── memory-update.sh          #   base-memory rebuild (cron-safe)
├── scripts/
│   └── memory-refresh.sh         #   2h cron entrypoint → memory-update
├── systemd/                      # persistence units (user-level)
│   ├── hermes-persistence.service
│   └── hermes-persistence.timer  #   fires the watchdog every 60s
├── scout-api-keys.md             # dedup state for the daily free-API-key scout cron
├── skills/                       # 75 skills (catalog below)
├── agent-hooks/
│   └── ztk-rewrite.py            # legacy pre_tool_call compression hook (historical)
├── photon/
│   └── sidecar/                  # photon sidecar (historical)
├── memories/
│   └── MEMORY.md                 # persistent agent notes (secrets redacted)
└── cron/                         # scheduled jobs (jobs.json is runtime state, not committed)
```

---

## 🛡 The persistence layer (what keeps it alive)

`bin/hermes-persistence.py` runs under a systemd **user timer every 60 seconds**
(`systemd/hermes-persistence.{service,timer}`; enable with `systemctl --user enable --now
hermes-persistence.timer`). It self-heals three failure modes and alerts via Telegram
(@ChinQueAsistanceBot → owner DM, 1h dedupe cooldown, logs to `~/.hermes/logs/hermes-persistence.log`):

1. **Gateway offline** → restarts `hermes-gateway-<profile>.service`; alerts if still down after 90s.
2. **Model/provider down** → probes the active model with a real chat call; after 2 genuine
   failures it auto-switches `model.default` down the fallback chain
   (`qwen3.8-flash → glm5.3-flash → hy3 → agnes-2.5`), alerts on the switch, and **auto-returns**
   when the primary recovers. 429s/timeouts count as transient — no flapping.
3. **Telegram API unreachable** → one alert, hourly re-alert while down, recovery notice.

Pitfall baked in: api.b.ai rejects `max_tokens ≤ 2` — probes use ≥ 8.

## ⏰ Scout cron

`free-api-key-scouts` (Hermes cron, daily 12:00): 4 parallel scout agents hunt **new** free-tier
AI API providers (the B.ai / Agnes class), hard-excluding the usual suspects (OpenRouter, big-lab
endpoints). Every find is HTTP-verified before reporting; `scout-api-keys.md` is the dedup ledger.
Empty day → honest `NO_NEW_KEYS`, no padding.

## 🧠 Memory stack

| Layer | What | Where |
|---|---|---|
| Hermes memories | persistent user/agent facts | `memories/MEMORY.md` |
| ECC Memory Vault | cross-harness portable memories (`ecc.memory.v1`) | `~/.ecc/memory/project/` (CLI: `ecc memory search/save/doctor`) |
| brain | git-backed FTS notes shared across all coding agents | `~/.brain` (`brain note/ask/log`) |
| graphify base memory | workspace knowledge graph, refreshed every 2h | `~/4project-labs/herme-khuchinque/graphify-out/` |
| skills | procedural memory, curator-managed + pinned combo | `skills/` |

`AGENTS.md` carries the **memory-first protocol**: recall vault → master context → skills →
validate state, before any non-trivial work.

---

## 🎨 The ChinQue skin

*Cyberpunk Time-Heist — neural-interface aesthetic: chronograph cyan, golden chronal energy, white highlights.*

| Surface | Key | Value |
|---|---|---|
| Assistant replies (streamed text) | `banner_text` | `#FFD700` gold |
| Response box border | `response_border` | `#FFD700` gold |
| Prompt symbol | `prompt` / `prompt_symbol` | `#E0F7FA` · `⏳ ❯` |
| Banner border / title | `banner_border` / `banner_title` | `#00BCD4` / `#00E5FF` |
| Working/hint line (rain glow) | `ui_hint` | `#00B8D4` blue |
| Status bar | `status_bar_bg` + 7 fg states | `#002B36` deep teal |
| Session / selection / shell | `session_*`, `selection_bg`, `shell_dollar` | teal family |

**31 color keys total** — every key the engine defines is set explicitly, so nothing inherits
a clashing default. `ChinQueViolet.yaml` is the violet variant.

### The time-traveler hero (`banner_hero`)

ASCII portrait of a man in a long coat — brass chronograph goggles, open pocket watch — standing
in falling matrix rain. Warm pixels → gold ramp, rim-light → cyan, 54×16, alignment-verified.

### Blue matrix-rain spinner

```
⟪┆ ┆⟫  →  ⟪╻ ╻⟫  →  ⟪┃ ┃⟫  →  ⟪╹ ╹⟫        faces: (┆) (╻) (┃) (╹) (⋮)
```

### Full persona

- **Agent name:** `Chinque Agent` · status glyph `⏳` · thinking tag `[rewinding]`
- **Tool renames (display-only):** `terminal → Time-Heist`, `web_search → Timeline-Scan`,
  `delegate_task → Paradox-Self`, `memory → Time-Capsule`, `cronjob_manage → Loop`, … — each
  with a themed glyph
- **Engine note:** several keys are local engine hooks patched into this install's `hermes_cli`;
  re-apply notes live in `skills/` (see git history for the archived skin-registration skill).

---

## 🧰 Skills catalog (75)

**The mandatory combo** (`software-development/`, curator-**pinned** so pruning can't touch them):
`planning-with-files` · `rtk` (shell-output compression) · `codegraph` (AST repo traversal) ·
`graphify` (knowledge-graph base memory). Enforced every turn by `bin/skill-combo.sh`.

| Category | Skills |
|---|---|
| **marketing/** (50) | full CRO/copywriting/SEO/ads/email/launch/analytics library (coreyhaines31 pack) |
| **productivity/** (7) | caveman ultra-compressed modes + cavecrew subagents + commit/review/compress/stats |
| **autonomous-ai-agents/** | hermes-agent (operate Hermes itself: 17 references + templates) |
| **web/** | agent-reach (YouTube/RSS/V2EX/bilibili/web; socials cookie-gated by policy) |
| **writing/** | humanizer (strip AI tells from prose) |
| **research/** | defuddle (clean markdown extraction from web pages) |
| **strategy** | ai-strategist (value metric → options ladder → kill criterion) · stakeholder-simulator (incentive-driven pushback testing) |
| **ops** | hermes-profile-watchdog · agent-skill-installs · codebase-memory |
| **apple / creative / email / media / note-taking / social-media** | bundled Hermes skills |

> The previous snapshot's custom skills (swarm-types-catalog, graph-engineering,
> ztk-token-compression, skin-registration, …) were pruned from the live profile by the Hermes
> curator; they remain recoverable from git history (`git show 813d8b6:skills/...`).

## ⚙️ Config (`config.yaml`)

- **Model:** `qwen3.8-flash` via `https://api.b.ai/v1` (key from `${B_AI_API_KEY}` — never inline)
- **Aliases:** `glm5.3-flash`, `hy3`, `mimo2.5` (b.ai) · `agnes-2.5`, `agnes-3.0` (fallback provider)
- **Skin:** `display.skin: ChinQue` · **Web backend:** nous
- **Hooks:** `pre_llm_call → bin/skill-combo.sh` (combo enforcement), `hooks_auto_accept: true`
- **MCP:** headroom · codegraph · graphify · codebase-memory-mcp

---

## 🚀 Install

```bash
# 1. pick your profile home
export HERMES_HOME=~/.hermes/profiles/herme-khuchinque

# 2. warp it
git clone https://github.com/khuchinque-app/herme-khuchinque.git
cd herme-khuchinque
mkdir -p "$HERMES_HOME"
cp -a config.yaml SOUL.md AGENTS.md skins skills memories bin scripts scout-api-keys.md "$HERMES_HOME/"

# 3. secrets — yours, never committed
cp .env.example "$HERMES_HOME/.env"
$EDITOR "$HERMES_HOME/.env"        # fill B_AI_API_KEY=*** + TELEGRAM_BOT_TOKEN=***

# 4. persistence (optional but recommended)
mkdir -p ~/.config/systemd/user && cp systemd/* ~/.config/systemd/user/
systemctl --user daemon-reload && systemctl --user enable --now hermes-persistence.timer

# 5. go
hermes        # → time-traveler banner, gold replies, rain spinner while it thinks
```

**Verify the warp:** `bash bin/agent-stack-doctor.sh` → all OK; `hermes config get display.skin`
returns `ChinQue`; `systemctl --user is-active hermes-persistence.timer` → `active`.

---

## 🔒 What is deliberately NOT here

| Excluded | Why |
|---|---|
| `.env`, `auth.json` | Credentials / OAuth tokens — real values never leave the machine |
| `state.db*`, `sessions/`, `.hermes_history` | Chat history and identity data |
| `cache/`, `logs/`, `pastes/`, `*_cache.json` | Runtime dirt, regenerates itself |
| `home/` (~1 GB), `lsp/`, `sandboxes/` | Installed toolchains, not profile definition |
| `skills/.hub/`, curator ledgers/state, `.usage.json` | Runtime bookkeeping |
| `bin/persistence-state.json` | Live watchdog state |
| Telegram bot token in `memories/MEMORY.md` | Redacted before commit — lives only in local `.env` |

The repo was secret-scanned before push (PAT patterns, key=value sweeps, placeholder-aware).
`.gitignore` keeps it that way on re-warps.

---

<div align="center">

*Warp status: ✅ 75 skills · 0 secrets · 1 watchdog · 4 scouts daily · 1 time-traveler*

**⏳ Chinque Agent v1.0.0 — Time-Heist Protocol**

</div>
