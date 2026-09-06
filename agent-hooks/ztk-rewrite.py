#!/usr/bin/env python3
"""ztk-rewrite.py — Hermes pre_tool_call shell hook that auto-routes terminal
commands through the ztk token-compression proxy.

Reads the Hermes hook payload on stdin, asks `ztk rewrite` (Claude Code
PreToolUse dialect) whether the command has a compression filter, and if so
emits a Hermes/Claude-Code 'modify' directive replacing the command with
`ztk run <cmd>`. Fail-open: any error means the command runs untouched.

Safety guards (semantic hazards ztk's own rewrite allows but we don't):
- skip commands containing '>' (redirect: file would receive compressed text)
- skip commands containing '|' (downstream tool would parse compressed text)
Exit codes and stderr are preserved by ztk itself.
"""
import json
import subprocess
import sys

ZTK = "/home/khuchinque/.local/bin/ztk"


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if payload.get("tool_name") != "terminal":
        return 0
    cmd = (payload.get("tool_input") or {}).get("command") or ""
    if not cmd or ">" in cmd or "|" in cmd:
        return 0
    cc = json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}})
    try:
        proc = subprocess.run(
            [ZTK, "rewrite", "--skip-permissions"],
            input=cc, capture_output=True, text=True, timeout=5,
        )
    except Exception:
        return 0
    out = (proc.stdout or "").strip()
    if not out:
        return 0
    try:
        new_cmd = json.loads(out)["hookSpecificOutput"]["updatedInput"]["command"]
    except Exception:
        return 0
    if new_cmd and new_cmd != cmd:
        print(json.dumps({"decision": "modify", "tool_input": {"command": new_cmd}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
