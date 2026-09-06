---
name: agent-harness-design-intelligence
description: "Harness AI agents with ECC and design workflows."
version: 0.1.0
author: Hermes
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [Agents, Harness, ECC, Design, Workflow]
---

# Agent Harness & Design Intelligence

Use ECC-style harness patterns and design-intelligence checks to turn coding assistants into coordinated engineering systems. This skill covers harness layering, continuous learning, security auditing, and design-decision workflows.

## When to Use

- "set up an agent harness"
- "apply ECC workflow"
- "audit agent config for vulnerabilities"
- "improve design output consistency"
- "plan/test/implement/review/verify workflow"

## Prerequisites

- One supported client: Claude Code, Codex, or Cursor
- Git and a project workspace
- Optional: GitHub App integration for AgentShield auditing

## Quick Reference

| Concept | Practice |
|---------|----------|
| Distribution Layer | Open-source skills, commands, hooks, install profiles |
| Protection Layer | AgentShield red-team/blue-team/auditor scanning |
| Control-Plane Layer | Observability, session management, cross-harness ops |
| Learning Loop | Atomic instincts from session history with confidence scoring |
| Design Dials | Bias output by variance/motion/density tiers |
| Support | Claude Code full; Codex via marketplace; Cursor beta |

## Procedure

1. Harness layout:
   - Put shared skills and commands in a project-level toolkit.
   - Keep security policy separate from execution logic.
   - Add an observability layer for session review.
2. Pre-flight baseline checks:
   - Search-first: scan the target project for existing layout files, env vars, and configs (`CLAUDE.md`, `.cursorrules`, `.hermes`, `package.json`, `.env`, `AGENTS.md`). Use `search_files(target='files')` for filename discovery and `terminal` for directory listing when `search_files` misses hidden paths.
   - Security scan: run `npx ecc-agentshield scan` from the project root, or add `--path <target>` to scan a specific directory. Do not append a positional directory to `scan`; that path form is invalid for this package version. Ignore Tirith/ecosyste.ms/OSV lookup warnings unless they produce actionable findings; treat them as incomplete verification, not evidence of compromise.
   - Memory init: create a project-scope memory index at `<project>/.ecc/memory/index.json` with `{"version":"ecc.memory.v1","harness":"hermes","project":"<abs-path>","created":"<date>"}`. If `ecc` CLI is unavailable, use Hermes memory as the fallback.
   - If the home-directory listing is noisy with unrelated dirty git state, scope all discovery to the actual project path before drawing conclusions about repo cleanliness.
3. Learning loop:
   - After each session, extract corrections and error-fix sequences as atomic instincts.
   - Store with confidence scores; decay low-confidence entries.
4. Security audit:
   - Run AgentShield-style checks on config and hooks.
   - Use red-team/blue-team/auditor passes before merging.
5. Design workflow:
   - Use UI UX Pro Max-style references for style, typography, and UX patterns.
   - Apply Design Dials to set variance, motion, and density targets before generating UI.
6. Execution lifecycle:
   - Brainstorming → Plan → TDD → Review → Finish, with ECC delegated to AgentShield for security and Memory Vault for session state.
   - No duplicate workflow commands from other harnesses; enforce core-workflow exclusivity.

## Pitfalls

- Cursor support is beta; expect adapter-specific install paths.
- Learning loops need explicit pruning rules or they accumulate noise.
- Public sharing of notebooks may still require Google auth; prefer direct export.
- `npx ecc-agentshield scan` with a positional directory argument throws `too many arguments`; use `--path` instead.
- A dirty repo root listing is not a project-state conclusion; confirm the actual target workspace before claiming anything about branch cleanliness.
- `brain` may not be on `$PATH` in a session; fall back to Hermes memory rather than treating absence as a blocker.
- `.env` and secret-bearing files must not be echoed in raw form; use `cat` only when masking is guaranteed, or skip content display after confirming presence.

## Verification

Create a harness scaffold with skills/, hooks/, and an audit checklist, then run one review cycle using the lifecycle above. Before coding, present a one-line environment status and then ask one clarifying question at a time.
