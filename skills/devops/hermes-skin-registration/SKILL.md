---
name: hermes-skin-registration
description: "Use when registering or fixing a Hermes skin YAML."
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, skins, themes, validation, configuration]
    related_skills: [hermes-agent]
---

# Hermes Skin Registration

Use when the user hands over a skin/theme YAML ("register it into skins", "inspect and fix alignment"). The bundled `hermes-agent` skill's `references/themes.md` covers authoring and activation; this skill covers the VALIDATE-then-REGISTER pipeline against the live engine, which the themes reference does not.

## Where things live

- Skins dir: `$HERMES_HOME/skins/<name>.yaml` — resolve `$HERMES_HOME` first (profile-active sessions point it at `~/.hermes/profiles/<profile>`; the shell `~` may be the sandbox home, so use absolute paths).
- Engine source (schema ground truth): find with `find / -name skin_engine.py -not -path '*/proc/*'` (typically `/usr/local/lib/hermes-agent/hermes_cli/skin_engine.py`).
- Loader rules: file must parse as YAML dict with a `name` key; `colors`/`spinner`/`branding` merge over the `default` built-in; `light_colors`/`dark_colors`/`tool_emojis` do NOT merge (empty = no variant); user skins load before built-ins but never shadow a built-in NAME in `list_skins`.

## Procedure

0. **If the user says "the YAML I have" without a path**, locate it before asking: search the project/workspace dirs for YAML whose head contains `colors:` plus `banner`/`branding`/`spinner`/`tool_emojis` (exclude skills/, venvs, node_modules, config.yaml, cron/), newest-mtime first.
1. **Parse and diff against the engine, not the template.** Get the `default` built-in's color keys by IMPORTING the engine, never by regex over its source: `cd /usr/local/lib/hermes-agent && python3 -c "from hermes_cli.skin_engine import _BUILTIN_SKINS; print(sorted(_BUILTIN_SKINS['default']['colors']))"`. A hand-rolled regex over the `_BUILTIN_SKINS` literal silently under-counts — block boundaries depend on which built-ins exist and trailing keys (`completion_menu_meta_bg`, `completion_menu_meta_current_bg`) get dropped, producing false "extra key" reports. Diff against the skin's keys — the shipped `templates/skin.yaml` is a subset and will miss keys like `selection_bg`, `shell_dollar`, `status_bar_strong/dim/bad`.
2. **Check duplicate top-level keys with a regex, not yaml.safe_load.** PyYAML silently keeps the last duplicate (`banner_hero: |` twice = one empty shadow block); `re.findall(r'^([a-z_]+):', src, re.M)` and assert uniqueness.
3. **Validate hex** — every `colors` value must match `#[0-9A-Fa-f]{6}`; shorthand/rgb()/named colors don't parse on every surface.
4. **Cross-check `tool_emojis` keys against the live registry** — a mismatched key silently never fires. Enumerate real names: `grep -rhoP 'name="[a-z_]+"' /usr/local/lib/hermes-agent/tools/*.py | sort -u`. Common wrong guesses: `browser_navigate`→`browser_exec`, `cronjob`→`cronjob_manage`, `process`→`process_manage`, `todo`→`todo_list`; `mixture_of_agents` is not a tool at all (MoA is a virtual provider).
5. **Verify banner-art alignment with the correct tag regex** — strip with `re.sub(r'\[[^\]]*\]', '', line)`; a `[a-z#0-9 ]+` pattern misses UPPERCASE hex tags (`[dim #C9A227]`) and reports false raggedness. Compare per-line content length; trailing spaces inside the block are padding, not misalignment.
6. **Fix in place in the user's source file** (patch, don't rewrite), re-run checks 1–5 to confirm clean.
7. **Register**: `cp <file> $HERMES_HOME/skins/<name>.yaml`, then verify through the engine itself (see Verification), and `hermes skin list` to confirm it shows as `user`.
8. **Activation is the user's call** — report `hermes config get display.skin` (current) and offer `hermes config set display.skin <name>`; don't repaint every live surface unprompted.

## Surface → color-key map (CLI)

When the user asks to recolor a specific thing, resolve it to the right key first — the names mislead:

- **Streamed assistant answer text** = `banner_text` (`cli_stream_mixin` builds the truecolor ANSI for the response body from this key). `response_border` colors ONLY the box border; `prompt` colors only the prompt symbol, never typed or answer text.
- **Terminal background (the black behind everything)** is NOT a skin key — the CLI engine never paints it; it belongs to the terminal emulator. To change it from inside, emit an OSC-11 escape (`printf '\033]11;#RRGGBB\007'`) and ask the user whether it landed — support varies per emulator; where it's ignored, the fix is the emulator's own profile settings. Image/animated backgrounds are emulator features, not Hermes features — say so plainly instead of hunting for a skin key.
- **Single-key tweak on the ACTIVE skin**: `hermes skin set <key> <hex>` — repaints live within ~1s, no YAML edit or restart needed. Prefer this over patching the source file when the user just wants one color changed.

## Animated terminal backgrounds ("put a matrix rain behind my chat")

- **Trace the access path FIRST** — walk the process tree from the hermes CLI process upward (`ps -o ppid,args` chain): `bash → sshd` means the user's terminal window is on THEIR local machine and nothing server-side can paint behind it; a `ttyd`/`noVNC`/Xvfb chain means the session is browser-rendered and server-side tricks apply. Check what the server actually has (`ps` for Xvfb/x11vnc, `which` for emulators) before promising anything.
- The chat surface itself cannot be animated (no CSS/HTML injection into a CLI). Real options: (a) the user's terminal emulator's background-image feature — WezTerm animates GIFs natively, kitty/gnome-terminal take static images only, Termux/PuTTY/VS Code terminal support none; (b) `cmatrix -b -C blue` in a tmux pane beside the chat (works everywhere, not "behind").
- **GIF generator**: `scripts/matrix_rain.py` (Pillow; 960x540, 40-frame loop, palette constants at top for hue variants). Verify output before delivering: extract one frame (`im.seek(n); im.save(png)`) and inspect it with vision_analyze.
- Pillow pitfall: `ImageDraw.rectangle(0, 0, W, H, fill=...)` raises TypeError (multiple values for fill) — pass the box as a sequence `[0, 0, W-1, H-1]`.

## Rendering banner_hero from a user image

When the user supplies a picture (often a `data:image/...;base64,` URI embedded in a YAML comment): extract with regex `data:image/(\w+);base64,([A-Za-z0-9+/=]+)`, pad base64 to a multiple of 4, decode to a file. Before ASCII rendering, alpha-composite RGBA onto WHITE (`Image.alpha_composite`) then convert to `L` — a naive `.convert('L')` drops alpha and inverts the picture. Map DARK ink to dense ramp chars (` .,:;+*#@%` indexed by `1 - lum`), never the reverse; sanity-check that the subject silhouette is `@` and the background is spaces. Resize with LANCZOS to ~53 cols, rows = cols·(H/W)/2.05 for 2:1 cell aspect. Wrap each row in a per-line gradient tag (lerp `[#6B0000]`→`[#FFD700]`) and pad all rows to equal content width so alignment checks pass.

## Personalization engine hooks (this install)

The installed engine carries LOCAL, opt-in extensions beyond upstream skins (custom banner version
label, logo alignment, per-tool display names, status-bar/thinking glyphs, gold hint color) — see
`references/personalization-hooks.md` for the key table, patched-file list, review lessons, and the
`hermes update` re-apply warning.

## banner_hero from ASCII-converted art (time-traveler hero)

- Block scalar MUST use explicit indentation indicator `banner_hero: |2-` when the first content
  line starts with spaces (centered art): plain `|` auto-detects indent from that first line and
  the parser dies on the next line's `[` markup ("expected <block end>, but found '['").
- Image→ASCII for hero art: threshold OUT the dim background (lum < ~0.58) or matrix-rain texture
  becomes noise that swallows the figure; keep only warm pixels (r > b+10 → gold ramp) and bright
  cyan rim-light (→ #00BCD4/#00E5FF). Edge-detect (gradient magnitude) adds coat/collar lines.
  Verify with a plain (tag-stripped) preview before registering; render through rich to confirm.
- Rain spinner: `spinner.wings` pairs cycle per frame — falling-column glyphs (┆→╻→┃→╹) read as a
  raindrop descending each tick; `colors.ui_hint` tints the whole working line. Wings/faces are
  read live from the skin each `_animate` call — YAML watcher applies without restart; a changed
  banner_hero needs a restart to show.

## Pitfalls

- `load_skin(name)` resolves the FILE `<name>.yaml` — the filename must match the skin's `name` field EXACTLY, case included (`name: ChinQue` requires `ChinQue.yaml`; `chinque.yaml` loads as default with a "not found" warning even though `list_skins` shows it).
- `tool_emojis` and `tool_prefix` are TOP-LEVEL keys (`data.get("tool_emojis")`), NOT under `branding` — nested under branding they parse fine but silently never fire (verify with `sk.tool_emojis.get('terminal')` through the engine, not just YAML parse).
- Set `background` for GUI surfaces — without it the GUI guesses the app surface from text luminance; seed it from the skin's `status_bar_bg` when the palette has no explicit background. It is NOT a CLI-engine key (`_BUILTIN_SKINS['default']['colors']` has no `background`) — never flag its absence as a CLI validation failure.
- Keys absent from the skin inherit the DEFAULT skin's values, which can clash (default `selection_bg` navy, `shell_dollar` blue under a crimson skin). Diff key sets and fill gaps in the skin's own hue family.
- Name collisions with desktop built-ins (`mono`, `slate`, `cyberpunk`, `nous`, `midnight`, `ember`) won't override the built-in on the GUI.
- `python3 -c` verification may trip the approval scanner (nested-exec flag) — it still executes after auto-approval; don't interpret the flag message as a failure.

## Verification

Run the engine's own loader against the registered file (import from the source dir with `HERMES_HOME` set):

```bash
cd /usr/local/lib/hermes-agent && HERMES_HOME=<home> python3 -c "
from hermes_cli.skin_engine import list_skins, load_skin
print([s['name'] for s in list_skins() if s['source']=='user'])
sk = load_skin('<name>'); print(sk.get_color('selection_bg'), sk.tool_emojis.get('terminal'), len([l for l in sk.banner_hero.split(chr(10)) if l.strip()]))"
```

Then `hermes skin list` (shows `user` source) and `hermes config get display.skin` to state what is actually active.
