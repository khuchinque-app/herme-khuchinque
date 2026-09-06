---
name: ztk-token-compression
description: Compress agent terminal output via ztk; auto-hook wired.
version: 0.1.0
author: Hermes
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Tokens, Terminal, Hooks, Cli]
---

# ztk Token Compression

ztk is a 260KB zero-dependency binary that sits between the agent and the shell: it runs a command, compresses stdout through a six-stage filter pipeline, and returns the same information in a fraction of the tokens (~90% reduction on noisy commands). A Hermes shell hook auto-rewrites every `terminal` call through it — no manual invocation needed. It does NOT compress tool output of `read_file`/`web_extract`, and never touches error messages, exit codes, outputs under 80 bytes, or JSON/YAML/TOML data.

## When to Use

- Terminal output looks huge / context is burning on `git diff`, `ls -la`, test runs
- "check ztk stats" / "how many tokens saved"
- A command needs exact raw output → `ztk run --raw <cmd>`
- ztk install, update, or hook troubleshooting

## Prerequisites

- Binary: `/home/khuchinque/.local/bin/ztk` (on PATH; `~/.local/bin` is in PATH). Install: `curl -fsSL https://github.com/codejunkie99/ztk/releases/latest/download/ztk-x86_64-linux-musl.tar.gz | tar -xz` then `install -m 755 ztk ~/.local/bin/ztk` (pick asset per `uname -m`-`uname -s`; or `brew install codejunkie99/ztk/ztk`).
- `jq` (used by the hook tests; present at /usr/bin/jq).
- Hook script: `~/.hermes/profiles/herme-khuchinque/agent-hooks/ztk-rewrite.py` (executable).
- Profile `config.yaml` hooks block (below) + `hooks_auto_accept: true`.

## How to Run

Automatic (the point): the `pre_tool_call` shell hook rewrites `terminal` commands to `ztk run <cmd>` before dispatch — every session, no skill call, no user action. Config in the profile config.yaml:

```yaml
hooks_auto_accept: true
hooks:
  pre_tool_call:
    - matcher: "terminal"
      command: "python3 /home/khuchinque/.hermes/profiles/herme-khuchinque/agent-hooks/ztk-rewrite.py"
      timeout: 10
```

Manual: invoke through the `terminal` tool — `ztk run git diff HEAD~5`. Verify wiring: `hermes hooks list` and `hermes hooks test pre_tool_call --for-tool terminal`.

## Quick Reference

| Command | What it does |
|---|---|
| `ztk run <cmd>` | run + compress output |
| `ztk run --raw <cmd>` | exact output, no filtering |
| `ztk stats` | savings dashboard (commands, bytes, %) |
| `ztk update` | self-update binary (not for brew installs) |
| `ztk rewrite --skip-permissions` | Claude-Code PreToolUse handler (stdin JSON) — what the hook calls |
| `ztk init -g` | install hooks for Claude Code / Cursor / Gemini CLI (NOT Hermes) |

Filters exist for: git (status/diff/log/add/commit/push), test runners (cargo test, pytest, go test, npm/pnpm/yarn test, jest, vitest, Playwright), file ops (ls, cat, find, grep, rg, wc, head, tail, tree), build (cargo build/check, go build, tsc, zig build), linters (eslint, ruff, mypy, clippy, golangci-lint), infra (docker, docker compose, kubectl, curl, env), utilities (json, gh, python tracebacks, log dedup), plus 25 regex filters (make, terraform, helm, brew, pip, gradle, mvn, dotnet, wget, prettier, rspec, rubocop, rake, psql, aws, …). Unrecognized commands pass through untouched.

## Procedure

1. Nothing to do for compression — the hook fires automatically on every `terminal` call. Check it is alive: `hermes hooks list` shows the ztk-rewrite entry with consent granted.
2. Savings: `ztk stats` (invoke through `terminal`).
3. Exact output needed (file names matter, debugging): prefix manually with `ztk run --raw` or run the command normally with pipes/redirects (hook skips those).
4. Update binary: `ztk update` (or `brew upgrade codejunkie99/ztk/ztk` if brew-managed). Script: `scripts/update.sh` — invoke through `terminal`.
5. If the hook misbehaves: `hermes hooks doctor` flags exec-bit, allowlist, mtime drift; the script fails open, so worst case is uncompressed output, never a broken command.

## Pitfalls

- The hook deliberately skips commands containing `|` or `>`: `ztk run cat x > y` would write COMPRESSED text into the file, and pipes would feed downstream tools compressed data. ztk's own rewrite allows these — our adapter guards them.
- `ztk run "ls -la"` (quoted whole string) fails with FileNotFound — ztk execs directly, no shell. Pass args normally.
- Session memory cache: repeated unchanged commands return a one-liner (TTLs: 30s fast-changing like git status/ls, 2min test runners, 5min git log). Stale-looking single lines are this, not a bug; mutation commands invalidate related caches.
- Small outputs (<80 bytes) are never compressed — no savings to chase.
- `ztk init -g` configures Claude Code/Cursor/Gemini only; Hermes wiring is the shell hook above, done manually.
- Homebrew installs: `ztk update` refuses to overwrite the brew binary — use `brew upgrade`.
- Exit codes and stderr are preserved by ztk; failed commands still surface errors.

## Verification

`ztk stats` shows Commands > 0 after a few terminal calls. For the hook test, the payload MUST include `tool_name` (the hook checks it first and no-ops without it — a payload of only `tool_input` falsely reports "parsed: none"):

```bash
echo '{"tool_name":"terminal","tool_input":{"command":"git status"}}' > /tmp/ztk-payload.json
hermes hooks test pre_tool_call --for-tool terminal --payload-file /tmp/ztk-payload.json
```

Note: `--payload-file <(echo ...)` process-substitution may be blocked by command scanners — write a temp file instead. Strongest live proof is a compressed result: `ls -la <dir>` returning `N dirs, M files [...]` one-liner format.
