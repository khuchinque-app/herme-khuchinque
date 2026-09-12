#!/usr/bin/env python3
"""
Hermes Telegram persistence watchdog — profile: herme-khuchinque
Runs every minute via systemd timer. Self-heals three failure modes:

  1. Gateway offline      -> systemctl --user restart, alert Telegram if slow
  2. Model/provider down  -> auto-switch model.default to the next healthy
                             fallback (Telegram alert on switch + recovery)
  3. Telegram API down    -> alert once, re-alert hourly, alert on recovery

All state lives in STATE_FILE; alerts are deduped so you never get spam.
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

PROFILE = "herme-khuchinque"
HERMES_HOME = os.path.expanduser(f"~/.hermes/profiles/{PROFILE}")
HERMES_BIN = "/usr/local/lib/hermes-agent/venv/bin/hermes"
SERVICE = f"hermes-gateway-{PROFILE}.service"
ENV_FILE = os.path.join(HERMES_HOME, ".env")
BIN_DIR = os.path.join(HERMES_HOME, "bin")
STATE_FILE = os.path.join(BIN_DIR, "persistence-state.json")
LOG_FILE = os.path.expanduser("~/.hermes/logs/hermes-persistence.log")

GATEWAY_GRACE = 90        # seconds to wait after restart before alerting
MODEL_FAILS_BEFORE_SWITCH = 2   # consecutive probe failures before switching
RECOVER_FAILS = 3         # consecutive primary failures before trying recovery
ALERT_COOLDOWN = 3600     # re-alert interval for ongoing outages (1h)

# Fallback chain tried in order when the primary model is down.
FALLBACKS = [
    ("glm5.3-flash", "glm-5.3-flash", "https://api.b.ai/v1", "B_AI_API_KEY"),
    ("hy3",          "hy3",           "https://api.b.ai/v1", "B_AI_API_KEY"),
    ("agnes-2.5",    "agnes-2.5-flash", "https://apihub.agnes-ai.com/v1", "AGNES_API_KEY"),
]

CHAT_ID = "7281341176"    # ChinQue DM
BACKUP_CHAT_ID = "8051612070"  # Vandaidr (backup, used if primary delivery fails)


# ---------------------------------------------------------------- utilities

def log(msg):
    line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass


def load_env():
    env = dict(os.environ)
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            for ln in f:
                ln = ln.strip()
                if ln and not ln.startswith("#") and "=" in ln:
                    k, v = ln.split("=", 1)
                    env.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    return env


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_state(state):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=1)
    os.replace(tmp, STATE_FILE)


def http_json(url, data=None, headers=None, timeout=15):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def notify(env, text):
    """Send alert to Telegram; fall back to backup chat. Returns True on delivery."""
    token = env.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        log("notify skipped: no TELEGRAM_BOT_TOKEN")
        return False
    ok = False
    for chat in (CHAT_ID, BACKUP_CHAT_ID):
        try:
            body = json.dumps({
                "chat_id": chat,
                "text": f"🛡 <b>Hermes Watchdog</b>\n{text}",
                "parse_mode": "HTML",
            }).encode()
            r = http_json(
                f"https://api.telegram.org/bot{token}/sendMessage",
                data=body,
                headers={"Content-Type": "application/json"},
            )
            if r.get("ok"):
                ok = True
                break
        except Exception as e:
            log(f"notify to {chat} failed: {e}")
    return ok


def alert_deduped(state, key, text, now):
    """Send alert unless the same key was alerted within ALERT_COOLDOWN."""
    entry = state.setdefault("alerts", {})
    last = entry.get(key, 0)
    if now - last >= ALERT_COOLDOWN:
        entry[key] = now
        env = load_env()
        delivered = notify(env, text)
        log(f"alert[{key}] delivered={delivered}: {text[:120]}")
        return delivered
    log(f"alert[{key}] suppressed (cooldown)")
    return False


# ---------------------------------------------------------------- checks

def gateway_status():
    try:
        r = subprocess.run(["systemctl", "--user", "is-active", SERVICE],
                           capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def probe_model(base_url, key, model):
    """Return (healthy, detail, transient). transient=True means 'inconclusive,
    don't count it' (rate limit / timeout) — not a real model failure."""
    try:
        r = http_json(
            base_url.rstrip("/") + "/chat/completions",
            data=json.dumps({
                "model": model,
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 8,   # api.b.ai rejects max_tokens <= 2
            }).encode(),
            headers={"Authorization": f"Bearer {key}",
                     "Content-Type": "application/json"},
            timeout=20,
        )
        if r.get("choices"):
            return True, "ok", False
        return False, f"no choices: {str(r)[:120]}", False
    except urllib.error.HTTPError as e:
        # 429/5xx = provider hiccup (transient); 4xx = model/key genuinely broken
        transient = e.code == 429 or e.code >= 500
        return False, f"HTTP {e.code}", transient
    except Exception as e:
        # network timeout / DNS — inconclusive, never switch on this alone
        return False, str(e)[:160], True


def current_model():
    try:
        r = subprocess.run([HERMES_BIN, "--profile", PROFILE,
                            "config", "get", "model.default"],
                           capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception:
        return ""


def set_model(alias):
    r = subprocess.run([HERMES_BIN, "--profile", PROFILE,
                        "config", "set", "model.default", alias],
                       capture_output=True, text=True, timeout=30)
    return r.returncode == 0


def primary_config(env):
    """Read primary model/base_url/key from config so recovery knows the target."""
    cfg = {"alias": "qwen3.8-flash", "model": "qwen3.8-flash",
           "base_url": "https://api.b.ai/v1", "key_env": "B_AI_API_KEY"}
    try:
        r = subprocess.run([HERMES_BIN, "--profile", PROFILE,
                            "config", "get", "model.base_url"],
                           capture_output=True, text=True, timeout=30)
        if r.stdout.strip():
            cfg["base_url"] = r.stdout.strip()
    except Exception:
        pass
    return cfg


# ---------------------------------------------------------------- main loop

def run_once():
    now = time.time()
    env = load_env()
    state = load_state()
    state.setdefault("model_fails", 0)
    state.setdefault("primary_fails", 0)
    state.setdefault("alerts", {})

    # ---- 1. Gateway ----------------------------------------------------
    status = gateway_status()
    if status != "active":
        log(f"gateway is '{status}' -> restarting {SERVICE}")
        subprocess.run(["systemctl", "--user", "restart", SERVICE], timeout=30)
        state["gw_down_since"] = state.get("gw_down_since") or now
        state["gw_restart_at"] = now
    else:
        if state.get("gw_down_since"):
            log("gateway back to active")
            state["gw_down_since"] = None
        # alert if still down 90s after our restart attempt
    if state.get("gw_down_since") and gateway_status() != "active":
        if now - state["gw_restart_at"] > GATEWAY_GRACE:
            alert_deduped(state, "gateway",
                          f"⚠️ Telegram gateway offline ({SERVICE}).\n"
                          "Auto-restart attempted, still not active.", now)

    # ---- 2. Model health -------------------------------------------------
    cur = current_model() or state.get("active_model") or "qwen3.8-flash"
    state["active_model"] = cur

    # Determine the primary: if config currently points at a known fallback,
    # the real primary is the one we persisted in state; otherwise the
    # currently-configured model IS the primary (user may have changed it).
    fb_aliases = {f[0] for f in FALLBACKS}
    if cur in fb_aliases and state.get("primary"):
        primary = state["primary"]
    else:
        base_url = ""
        try:
            r = subprocess.run([HERMES_BIN, "--profile", PROFILE,
                                "config", "get", "model.base_url"],
                               capture_output=True, text=True, timeout=30)
            base_url = r.stdout.strip()
        except Exception:
            pass
        key_env = "AGNES_API_KEY" if "agnes" in base_url else "B_AI_API_KEY"
        primary = {"alias": cur, "model": cur,
                   "base_url": base_url or "https://api.b.ai/v1",
                   "key_env": key_env}
        state["primary"] = primary

    chain = [(primary["alias"], primary["model"],
              primary["base_url"], primary["key_env"])]
    chain += [f for f in FALLBACKS if f[0] != primary["alias"]]

    entry = next((c for c in chain if c[0] == cur), chain[0])
    healthy, detail, transient = probe_model(entry[2], env.get(entry[3], ""), entry[1])

    if healthy:
        state["model_fails"] = 0
        if cur != chain[0][0]:
            # on a fallback: try to go home every RECOVER_FAILS cycles
            state["primary_fails"] = state.get("primary_fails", 0) + 1
            if state["primary_fails"] >= RECOVER_FAILS:
                state["primary_fails"] = 0
                p = chain[0]
                p_ok, _, _ = probe_model(p[2], env.get(p[3], ""), p[1])
                if p_ok and set_model(p[0]):
                    state["active_model"] = p[0]
                    alert_deduped(state, "model_recovered",
                                  f"✅ Primary model <b>{p[0]}</b> is back — switched home "
                                  f"(was on {cur}).", now)
                    log(f"recovered to primary {p[0]}")
    elif transient:
        log(f"model {cur} probe inconclusive (transient): {detail} — not counting")
    else:
        state["model_fails"] += 1
        log(f"model {cur} probe failed ({state['model_fails']}/{MODEL_FAILS_BEFORE_SWITCH}): {detail}")
        if state["model_fails"] >= MODEL_FAILS_BEFORE_SWITCH:
            switched = False
            for fb in chain[1:]:
                ok, _, _ = probe_model(fb[2], env.get(fb[3], ""), fb[1])
                if ok and set_model(fb[0]):
                    state["primary"] = {"alias": chain[0][0], "model": chain[0][1],
                                        "base_url": chain[0][2], "key_env": chain[0][3]}
                    state["active_model"] = fb[0]
                    state["model_fails"] = 0
                    alert_deduped(state, "model_switch",
                                  f"🔁 Model <b>{cur}</b> is down ({detail[:80]}).\n"
                                  f"Switched to fallback <b>{fb[0]}</b>. "
                                  "Will auto-return when the primary recovers.", now)
                    log(f"switched {cur} -> {fb[0]}")
                    switched = True
                    break
            if not switched:
                alert_deduped(state, "model_dead",
                              f"🚨 ALL models failed probing — no fallback available. "
                              f"Last error: {detail[:100]}", now)

    # ---- 3. Telegram API reachability -----------------------------------
    token = env.get("TELEGRAM_BOT_TOKEN", "")
    tg_ok = False
    if token:
        try:
            r = http_json(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
            tg_ok = bool(r.get("ok"))
        except Exception as e:
            log(f"telegram getMe failed: {e}")
    if not tg_ok:
        alert_deduped(state, "telegram_api",
                      "⚠️ Telegram API unreachable from the server — bot replies "
                      "will queue until the network returns.", now)
    elif state.get("alerts", {}).get("telegram_api"):
        # was down, now back up -> announce recovery once, clear the flag
        state["alerts"]["telegram_api"] = 0
        alert_deduped(state, "telegram_api_recovered",
                      "✅ Telegram API reachable again.", now)
        state["alerts"]["telegram_api_recovered"] = 0  # force the recovery msg out

    state["last_run"] = now
    save_state(state)


def main():
    if "--once" in sys.argv or True:  # single pass; systemd timer drives cadence
        run_once()


if __name__ == "__main__":
    main()
