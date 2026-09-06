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

**A complete Hermes Agent profile, warped.**

*The ChinQue Time-Heist skin · 9 custom skills · token-compression hooks · persona & memory · zero secrets*

</div>

---

> *"Time stop for no one. No one but me."*

This repository is a portable snapshot of a fully-configured [Hermes Agent](https://hermes-agent.nousresearch.com)
profile. Clone it into `$HERMES_HOME` and the agent wakes up already dressed: gold replies,
a time-traveler banner, a blue matrix-rain spinner, renamed tools, custom persona, and nine
battle-tested skills. Everything that *defines* the agent is here; everything that is runtime
dirt (chat databases, caches, toolchains, credentials) is not.

---

## 📦 Repository layout

```
herme-khuchinque/
├── README.md
├── .gitignore                    # keeps runtime/identity data out of future warps
├── .env.example                  # the shape of the secrets file (values never committed)
├── config.yaml                   # profile config — providers, models, hooks, toolsets
├── SOUL.md                       # agent persona / voice directives
├── skins/
│   └── ChinQue.yaml              # ★ the theme (full spec below)
├── skills/                       # 9 custom skills (full catalog below)
│   ├── autonomous-ai-agents/
│   │   ├── hermes-agent/         #   + 17 references, 3 templates
│   │   ├── agent-harness-design-intelligence/
│   │   └── swarm-types-catalog/
│   ├── communications/
│   │   └── agentmail-rest/
│   ├── devops/
│   │   ├── hermes-skin-registration/   # + personalization-hooks reference + rain script
│   │   ├── hermes-health-check/
│   │   ├── ztk-token-compression/      # + updater script
│   │   └── anysearch/
│   └── research/
│       └── graph-engineering/    # + 5 references + sync script
├── agent-hooks/
│   └── ztk-rewrite.py            # pre_tool_call hook — auto-compresses terminal output
├── photon/
│   └── sidecar/                  # photon sidecar (index.mjs + attachment patch, no node_modules)
└── cron/                         # scheduled jobs (empty in this snapshot)
```

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
| Completion menu | 4 keys | teal→cyan ramp |
| Session / selection / shell | `session_*`, `selection_bg`, `shell_dollar` | teal family |

**31 color keys total** — every key the engine defines is set explicitly, so nothing inherits
a clashing default (no stock navy selection under a teal theme).

### The time-traveler hero (`banner_hero`)

The banner portrait is ASCII art rendered from a generated image of a man in a long coat —
brass chronograph goggles on his forehead, cradling an open pocket watch — standing in falling
matrix rain. Conversion rules: warm pixels → gold ramp (`#8C6000 → #FFF8DC`), bright rim-light →
cyan (`#00BCD4`/`#00E5FF`), dim background thresholded to darkness so the figure emerges from it.
54 columns × 16 rows, alignment-verified per line.

### Blue matrix-rain spinner

While the agent works, the spinner wings cycle a falling raindrop:

```
⟪┆ ┆⟫  →  ⟪╻ ╻⟫  →  ⟪┃ ┃⟫  →  ⟪╹ ╹⟫        faces: (┆) (╻) (┃) (╹) (⋮)
```

### Full persona

- **Agent name:** `Chinque Agent` · version label `Chinque Agent v1.0.0` · status glyph `⏳`
- **Thinking tag:** `[rewinding]` · **verbs:** *rewinding the timeline · consulting the Chronokeeper ·
  i've been here before? · calculating to steal optimal seconds · shattering the past ·
  bending temporal loom and threads · replaying the exact same moment · reading the future outcome*
- **Welcome:** a teal→white gradient "Timelinesynchronized. Chronocommand ready. Enter your paradox/help."
- **Tool renames (display-only):** `terminal → Time-Heist`, `execute_code → Heist-Run`,
  `web_search → Timeline-Scan`, `web_extract → Archive-Read`, `read_file → Decrypt`,
  `write_file → Inscribe`, `patch → Rewrite`, `search_files → Trace`, `browser_exec → Dive`,
  `delegate_task → Paradox-Self`, `memory → Time-Capsule`, `clarify → Converge`,
  `cronjob_manage → Loop`, `process_manage → Stasis`, `todo_list → Heist-Plan`,
  `session_search → Echo`, `image_generate → Vision-Forge`, `text_to_speech → Voice-Cast`,
  `vision_analyze → Oracle-Gaze`, `skill_view → Recall-Protocol`, `skill_manage → Rewrite-Protocol`,
  `skills_list → Protocols` — each with its own themed glyph (`⏳ ⬡ ◇ ◆ ◈ ⌁ ⊕ ▣ ◐ …`)
- **Banner logo:** `CHINQUE TIMEHEIST` in a full cyan depth-gradient block font

> **Engine note:** several keys (`version_label`, `banner_logo_align`, `tool_names`,
> `status_bar_glyph`, `thinking_label`, `ui_hint`) are **local engine hooks** — opt-in
> extensions patched into this install's `hermes_cli`. Absent keys = stock behavior.
> A `hermes update` overwrites patched files; re-apply notes live in
> `skills/devops/hermes-skin-registration/references/personalization-hooks.md`.

---

## 🧰 Skills catalog

Nine skills, organized by category. Each is a `SKILL.md` (procedure + pitfalls) with optional
`references/`, `scripts/`, and `templates/`.

| Skill | Category | What it gives the agent |
|---|---|---|
| **hermes-agent** | autonomous-ai-agents | Operate Hermes itself: commands, config, providers, theming, plugins, MCP, webhooks, TUI widgets, security, troubleshooting — 17 reference docs + skin/plugin/clock templates |
| **hermes-skin-registration** | devops | The validate-then-register pipeline for skin YAMLs: engine-diff, duplicate-key, hex, emoji-registry and banner-alignment checks; personalization-hook table; image→ASCII hero conversion; matrix-rain GIF generator script |
| **hermes-health-check** | devops | Full system health/diagnostic sweep of a Hermes install |
| **swarm-types-catalog** | autonomous-ai-agents | The 14 Swarms framework types and when to use each (with reference doc) |
| **agent-harness-design-intelligence** | autonomous-ai-agents | Harness AI agents with ECC and design workflows |
| **graph-engineering** | research | Build knowledge graphs and orchestrate agent task graphs — modeling, extraction, fusion+LLM, curriculum, task-graph references + repo sync script |
| **ztk-token-compression** | devops | Compress agent terminal output via the `ztk` binary; wired into the shell through the hook below |
| **anysearch** | devops | AnySearch API search/extract, key registration, client connection |
| **agentmail-rest** | communications | AgentMail inbox listing, thread reads, sends — REST via curl |

## 🪝 Hooks

`agent-hooks/ztk-rewrite.py` — registered in `config.yaml` as a `pre_tool_call` hook matching
`terminal`: every terminal command is transparently rewritten to pipe its output through `ztk`
token compression before it reaches the model. ~60% fewer tokens on verbose output, no behavior change.

## ⚙️ Config (`config.yaml`)

- **Model:** `custom/qwen3.8-flash` via `https://api.b.ai/v1` (key from `${B_AI_API_KEY}` — never inline)
- **Aliases:** `glm5.3-flash`, `hy3`, `mimo2.5` — swap with `/model <alias>`
- **Skin:** `display.skin: ChinQue`
- **MCP:** `anysearch` (`https://api.anysearch.com/mcp`)
- **CLI toolsets:** a2a, browser, clarify, code_execution, computer_use, context_engine, cronjob, delegation, file, …
- **Hooks:** ztk pre_tool_call (above), `hooks_auto_accept: true`

## 🧠 Persona & memory

- `SOUL.md` — voice directives: direct, length-matched to the ask, no filler, claims over adjectives, swarm-on-standby.
- `memories/MEMORY.md` / `memories/USER.md` — the agent's persistent notes and user profile.
  ⚠️ These contain personal facts about the profile owner — review before re-publishing elsewhere.

---

## 🚀 Install

```bash
# 1. pick your profile home
export HERMES_HOME=~/.hermes/profiles/herme-khuchinque   # or any dir

# 2. warp it
git clone https://github.com/khuchinque-app/herme-khuchinque.git
cd herme-khuchinque
mkdir -p "$HERMES_HOME"
cp -a config.yaml SOUL.md skins skills memories agent-hooks photon cron "$HERMES_HOME/"

# 3. secrets — yours, never committed
cp .env.example "$HERMES_HOME/.env"
$EDITOR "$HERMES_HOME/.env"        # fill B_AI_API_KEY=***

# 4. optional: ztk compression (the hook expects it on PATH)
bash skills/devops/ztk-token-compression/scripts/update.sh

# 5. go
hermes        # → time-traveler banner, gold replies, rain spinner while it thinks
```

**Verify the warp:** `hermes skin list` shows `ChinQue (user)`; `hermes config get display.skin`
returns `ChinQue`; the working spinner cycles `┆╻┃╹`.

---

## 🔒 What is deliberately NOT here

| Excluded | Why |
|---|---|
| `.env`, `auth.json` | Credentials / OAuth tokens — real values never leave the machine |
| `state.db*`, `sessions/`, `.hermes_history` | Chat history and identity data |
| `cache/`, `logs/`, `pastes/`, `*_cache.json` | Runtime dirt, regenerates itself |
| `home/` (~1 GB), `bin/`, `lsp/`, `sandboxes/` | Installed toolchains, not profile definition |
| `skills/.hub/` (40 MB) | Skill-index cache |

The repo was secret-scanned before push (PAT patterns, key=value sweeps, placeholder-aware).
`.gitignore` keeps it that way on re-warps.

---

<div align="center">

*Warp status: ✅ 83 files · 0 secrets · 1 time-traveler*

**⏳ Chinque Agent v1.0.0 — Time-Heist Protocol**

</div>
