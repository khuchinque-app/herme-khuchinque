---
name: cron-scout-jobs
description: Cron scout jobs - dedupe, verify, honest-failure reports.
version: 1.0.0
metadata:
  hermes:
    tags: [cron, automation, scouts, monitoring]
---

# Recurring Scout / Monitor Cron Jobs (Hermes scheduler)

Class of task: "every day at <time>, send N scout agents to find X; if
nothing found, report failure honestly" — recurring autonomous information-
gathering jobs delivered to Telegram. For self-healing/system health jobs
use `hermes-profile-watchdog` (systemd pattern) instead.

## Procedure

### 1. Reach the scheduler
`cronjob_manage` is a DEFERRED tool — call it through `tool_call` (after
`tool_describe` if params unknown), not as a direct tool name; a direct call
fails with "Tool does not exist" even though the name appears in listings.

### 2. Design the prompt as fully self-contained
Cron runs get a FRESH session with zero chat context. The prompt must
embed, explicitly:
- **Fan-out contract**: exact number of delegate_task scouts and each one's
  beat/source list (HN/GitHub/PH, Reddit/blogs, social via agent-reach,
  direct web + curl verification). "Send 4 scouts" must appear as 4 named
  assignments, not a vibe.
- **Hard exclusions** as a literal list (user's "exclude the commons" —
  OpenRouter-class names, big providers, anything already in use).
- **Verification gate**: a candidate is reportable only if its homepage /
  signup / docs actually resolve via fetch and state the offer. Never
  fabricate; never create accounts, enter credentials, or solve captchas —
  login wall means report the signup URL only.
- **Honest-failure output contract**: give a sentinel string for the empty
  case (e.g. `NO_NEW_KEYS — …` + one line of closest misses) and forbid
  padding with old/known items to look successful. User norm: "if it can't
  find, it's fail and it's alright."
- **Word cap** on the delivered message (~350).

### 3. Dedupe across runs
- Set `continuity: true` so each run sees its previous output.
- Seed a STATE FILE in the profile home BEFORE first fire (agents can't
  invent shared history): `~/.hermes/profiles/<profile>/<job>-state.md`
  listing known/excluded items, with a dated "append finds here" section.
  The prompt tells scouts to read it first and never re-report its contents.

### 4. Schedule + deliver
- Natural language schedule (`every day at 12pm`) resolves in SYSTEM LOCAL
  time — check `timedatectl` when the user names a wall-clock time.
- `deliver: "telegram:<chat_id>"` explicitly; don't assume origin survived.
- After create, confirm `next_run_at` in the response; offer a test fire via
  action=run (backgrounds immediately; don't poll).

## Pitfalls
- Autonomous runs can't ask questions — anything ambiguous in the prompt
  gets guessed; write exclusion lists and output shape as literal examples.
- agent-reach channels behind cookie walls (X, Reddit…) fail silently in
  headless runs — instruct scouts to fall back to web search per channel
  rather than stall.
- A monitor-style job that should only wake on change can use the
  `monitor:` URL/script gate (deterministic output, no timestamps) instead
  of burning LLM tokens every tick.
