User prefers hands-off setup and direct execution. They want interactive prompts for keys/tool choice, not hardcoded values. They dislike aggressive live testing of endpoints. They are technically sophisticated and use multiple AI integrations. For this project, use b.ai as primary provider with models: glm5.3-flash, qwen3.8-flash, hy3, mimo2.5. Target workspace: /home/khuchinque/4project-labs/notebookllm/open-notebook.
§
User's canonical '14 swarm techniques' = Swarms framework types (docs.swarms.world), skill swarm-types-catalog — NOT metaheuristics. ztk token-compression installed (~/.local/bin/ztk) + Hermes pre_tool_call shell hook (agent-hooks/ztk-rewrite.py) auto-rewrites terminal commands; graph-engineering & ztk-token-compression skills auto-load via skill index.
§
Terminal env quirk: ~ resolves to the Hermes profile sandbox home (~/.hermes/profiles/herme-khuchinque), NOT /home/khuchinque — always use absolute paths for user files in terminal commands. Hermes home data (memories/, *.db, logs/) lives at /home/khuchinque/.hermes/ (3.0G).
§
User will NOT set up Spotify or Home Assistant credentials (declared permanently uninterested — never prompt for HASS_TOKEN or spotify login again). Toolsets stay enabled but credential-gated, harmless. Current focus: building a 'mega project' with Hermes as the best agent.
§
HARD RULE: never touch/restart/kill anything on ports 8765 and 8766 (ttyd web-terminal + related) — user declared them the most important services. Read-only inspection OK.