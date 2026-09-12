---
name: hermes-profile-watchdog
description: Build a Telegram self-heal watchdog for a Hermes profile.
version: 1.0.0
metadata:
  hermes:
    tags: [hermes, telegram, monitoring, systemd]
---

# Hermes Profile Persistence Watchdog

Procedure for "make Telegram persistent / auto-activate when offline or the
model is missing": one Python watchdog + systemd user timer per profile.
Reference implementation exists at
`~/.hermes/profiles/herme-khuchinque/bin/hermes-persistence.py` — copy and
re-parameterize (PROFILE, SERVICE, fallback chain) for other profiles rather
than rewriting.

## Architecture
- systemd **user** timer (60s, `Persistent=true`) → oneshot service running
  the script. Works because lingering is on (`loginctl show-user <u> |
  grep Linger`) — survives reboot and session loss without root.
- Single-pass script, no daemon loop; systemd drives cadence and logging
  (journalctl --user -u <unit>).
- Three heal layers: gateway service restart → model fallback chain →
  Telegram-API reachability alert, all with 1h-cooldown deduped alerts via
  bot sendMessage to the user's chat_id (backup chat as second recipient).

## Model-fallback rules (the part that's easy to get wrong)
- Probe with a REAL chat-completion call, not /models listing — a listed
  model can still 400.
- Classify failures: 429/5xx/timeout/network = **transient** → log, do NOT
  count toward switching. Only clean 4xx/no-choices are genuine. Switch after
  2 consecutive genuine failures only; probe chain: current → fallbacks →
  each must pass its own probe before set.
- Persist `state["primary"]` when switching so auto-recovery can return home
  (retry primary every N healthy cycles).
- Set model via `hermes --profile <p> config set model.default <alias>` —
  never hand-edit config.yaml. Resolve alias→base_url→key_env from
  config `model.default` + `model.base_url` at runtime; key names live in
  the profile `.env` (e.g. base_url contains "agnes" → AGNES_API_KEY).

## Pitfalls
- api.b.ai rejects `max_tokens <= 2` ("must be greater than 2") — probes use
  max_tokens 8; a 400 here is a probe bug, not model death, and a wrong
  probe once nearly triggered a cascade.
- The gateway service already has `Restart=always` — short crashes self-heal
  silently; the watchdog's value is alerting, model fallback, and Telegram-API
  monitoring, so don't duplicate plain restart logic beyond it.
- Alert delivery itself needs the bot token from the profile `.env`;
  load_env() with setdefault so real env wins.
- Writing state atomically (tmp + os.replace) matters — timers overlap runs
  when a probe hangs near TimeoutStartSec.

## Verification before declaring done
Run the script manually once; check state JSON (`model_fails: 0`, primary
recorded), `systemctl --user list-timers` shows next fire, then simulate a
fallback by setting a fallback alias and re-running — confirm it probes,
alerts none (healthy), and recovery logic engages.
