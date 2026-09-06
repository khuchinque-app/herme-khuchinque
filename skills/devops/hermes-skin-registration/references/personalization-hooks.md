# ChinQue-personalized engine hooks (installed 2026-09, /usr/local/lib/hermes-agent)

These skin keys are NOT in upstream Hermes — they were added locally to the installed engine.
A `hermes update` overwrites the patched files; re-apply from /tmp/chinque-src copies or this
table if banner/persona customizations stop working after an update. Engine changes need a
hermes restart; YAML-only edits repaint live via the skin watcher.

| Key | Where read | Effect when set |
|---|---|---|
| `branding.version_label` | `banner.py format_banner_version_label()` + `cli.py _build_compact_banner` fast path | Replaces the whole banner title (also `/version`, `hermes --version`) |
| `banner_logo_align` (top-level) | `banner.py build_welcome_banner()` | `center`/`right` wraps logo in rich `Align` (validated in skin_engine; bad value warns + left) |
| `tool_names:` (top-level dict) | `agent/display.py get_skin_tool_name()` | Renames tools in preparing line, spinner, cute fallback column. Display-only — dispatch still uses real names |
| `tool_emojis` short values (len<=2) | `agent/display.py get_skin_tool_glyph()` | Also swaps the leading emoji in `_CUTE_LINES` completion lines (gutter normalized: `^(┊ )\S+\s+` -> glyph + one space) |
| `branding.status_bar_glyph` | `cli_status_bar_mixin._status_bar_glyph()`, `cli_tui_mixin._prompt_working_glyph()` | Replaces ⚕ in status bar + prompt-while-running |
| `branding.thinking_label` | `cli_stream_mixin._thinking_label()` | Replaces `[thinking]` reasoning tag (ANSI _cprint, brackets literal) incl. both width calcs |
| `branding.agent_name` | `cli_status_bar_mixin._status_bar_agent_name()` + compact banner tiny_line | Status-bar/compact-banner fallback name |
| `colors.ui_hint` | `skin_engine._STYLE_PALETTE ('hint','ui_hint','@dim')` | Colors the TUI spinner/generating line (template `{hint} italic`, falls back to @dim) |
| `spinner.wings` | upstream `KawaiiSpinner._animate` | ⟪g / g⟫ pairs around spinner frames |

All hooks opt-in: absent key = byte-identical stock behavior (try/except + literal fallback).
`tui_gateway/change_watcher.resolve_skin()` broadcast carries `tool_names` + `banner_logo_align`.

Patched files: hermes_cli/{banner,skin_engine,cli_stream_mixin,cli_chat_turn_mixin,
cli_status_bar_mixin,cli_tui_mixin}.py, agent/{display,tool_executor}.py, cli.py,
tui_gateway/change_watcher.py, tests/hermes_cli/test_banner.py (title test pins
set_active_skin('default') in try/finally and restores the prior skin).

Review lessons (code-reviewer, 2026-09):
- NEVER str.replace() a tool name into build_tool_label output — friendly verbs don't contain
  the raw name, so the replace only corrupts argument-derived previews (paths/commands/queries).
  Rename at the call sites that print the bare name instead.
- VS16 emoji (✍️ 👁️ ⚙️ = base+VS16, 2 code points) break 1:1 regex token swaps; normalize the
  whole gutter (`\S+\s+`) instead.
- Desktop 'Generating…' strings live in compiled TS bundles (apps/desktop) — not skin-patchable.
- `hermes --version`/`/version` route through format_banner_version_label, so a custom
  version_label hides the real Hermes version there too (accepted by user).
