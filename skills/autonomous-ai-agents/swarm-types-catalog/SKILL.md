---
name: swarm-types-catalog
description: The 14 Swarms framework swarm types and when to use each.
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [Swarm-Orchestration, Multi-Agent, Swarms-Framework, Ai-Agents]
---

# Swarm Types Catalog (Swarms Framework)

The canonical 14 swarm techniques of the Swarms multi-agent orchestration framework (docs.swarms.world, `pip install -U swarms`): what each does, its key parameters, and when to pick it. This is the orchestration taxonomy — NOT biological swarm-intelligence metaheuristics (PSO/ACO/ABC). Details live in `references/swarm-types.md`; load on demand.

## When to Use

- "which swarm type should I use for X?"
- "what are the 14 swarm techniques?" / naming any type: SequentialWorkflow, ConcurrentWorkflow, AgentRearrange, GraphWorkflow, MixtureOfAgents, GroupChat, ForestSwarm, HierarchicalSwarm, HeavySwarm, SwarmRouter, SpreadsheetSwarm, AutoSwarm, SimpleSwarm, WorkerSwarm
- Writing `swarms` Python code that instantiates a swarm class
- Debugging a swarm constructor error or wrong parameter

## Prerequisites

- `pip install -U swarms` (v15.0.0 current); optional: `graphviz` + `rustworkx` for GraphWorkflow
- API keys for the models your agents use (LiteLLM-normalized, mix providers freely)
- Docs: https://docs.swarms.world — index at https://docs.swarms.world/llms.txt

## Quick Reference — the 14

| # | Swarm Type | Doc URL | Shape |
|---|------------|---------|-------|
| 1 | SequentialWorkflow | https://docs.swarms.world/api/sequential-workflow | A→B→C chain, output feeds next |
| 2 | ConcurrentWorkflow | https://docs.swarms.world/api/concurrent-workflow | all agents on same task in parallel |
| 3 | AgentRearrange | https://docs.swarms.world/api/agent-rearrange | flow DSL `"A -> B, C -> D"` |
| 4 | GraphWorkflow | https://docs.swarms.world/api/graph-workflow | DAG, topo-sorted layers, auto-parallel |
| 5 | MixtureOfAgents | https://docs.swarms.world/api/mixture-of-agents | parallel layers + aggregator |
| 6 | GroupChat | https://docs.swarms.world/api/group-chat | turn-based, bid-to-speak self-selection |
| 7 | ForestSwarm | https://docs.swarms.world/api/forest-swarm | trees of agents, embedding routing |
| 8 | HierarchicalSwarm | https://docs.swarms.world/api/hierarchical-swarm | director delegates to workers |
| 9 | HeavySwarm | https://docs.swarms.world/api/heavy-swarm | question decomposition + synthesis |
| 10 | SwarmRouter | https://docs.swarms.world/api/swarm-router | meta-router, `swarm_type=` switch |
| 11 | SpreadsheetSwarm | https://docs.swarms.world/api/spreadsheet-swarm | concurrent + CSV task/metadata table |
| 12 | AutoSwarm | https://docs.swarms.world/api/auto-swarm | boss agent builds swarm from task |
| 13 | SimpleSwarm | https://docs.swarms.world/api/simple-swarm | minimal fixed roster |
| 14 | WorkerSwarm | https://docs.swarms.world/api/worker-swarm | planner→worker queue→judge cycle |

Selection rule (from the framework's own catalog): topology is a lever, not a guess — sequential is cheapest/most deterministic; concurrent is fastest but loses ordering; hierarchical pays an extra director call for cleaner delegation; ensembles pay N× tokens for variance reduction. Split only where pieces never read each other's results.

## Procedure

1. Match the task shape to the table above; load `references/swarm-types.md` via `skill_view(name="swarm-types-catalog", file_path="references/swarm-types.md")` for constructor params, methods, and gotchas of the chosen type.
2. Prototyping? Instantiate `SwarmRouter(swarm_type="...", ...)` — swapping architectures is a one-line change.
3. Verify against live docs with `web_extract` on the URL (append `.md` for clean markdown) before shipping code — the framework releases every 2 weeks.

## Pitfalls

- URL drift: #12's real page is `/api/auto-swarm-builder` (class `AutoSwarmBuilder`); `/api/simple-swarm` and `/api/worker-swarm` currently 404. Names 12–14 are kept from the user's canonical list; confirm the class exists in the installed version before importing.
- Import paths (verified on v15.0.0): `SimpleSwarm` and `WorkerSwarm` do NOT exist — nearest shipped classes are `RoundRobinSwarm` and `PlannerWorkerSwarm`. `ForestSwarm` and `PlannerWorkerSwarm` exist but are NOT exported from top-level `swarms` or `swarms.structs` — import via `from swarms.structs.tree_swarm import ForestSwarm` / `from swarms.structs.planner_worker_swarm import PlannerWorkerSwarm`.
- SwarmRouter `swarm_type` Literal (verified v15.0.0): AgentRearrange, MixtureOfAgents, SequentialWorkflow, ConcurrentWorkflow, GroupChat, MultiAgentRouter, HierarchicalSwarm, MajorityVoting, CouncilAsAJudge, HeavySwarm, LLMCouncil, DebateWithJudge, RoundRobin, PlannerWorkerSwarm. GraphWorkflow, SpreadSheetSwarm, ForestSwarm, AutoSwarmBuilder are NOT routable — instantiate them directly.
- `"AutoSwarmBuilder"`, `"auto"`, `"BatchedGridWorkflow"` are NOT valid `SwarmRouter` swarm_types — they raise `SwarmRouterConfigError` at construction.
- `AgentRearrange` removed `human_in_the_loop`/`rules` params and the `H` flow token in current versions.
- `MixtureOfAgents.run()` swallows exceptions and returns the string `"Error: {e}"` — check the return, don't try/except.
- `SpreadSheetSwarm` requires a non-empty `agents` list at construction even when `load_path` is set; `load_from_csv()` must be called explicitly.
- `GroupChat.idle_timeout` is accepted but no longer ends the chat; stop conditions are `max_loops` or a lull below `threshold`.

## Verification

`python3 -c "import swarms; print([n for n in ('SequentialWorkflow','ConcurrentWorkflow','AgentRearrange','GraphWorkflow','MixtureOfAgents','GroupChat','HierarchicalSwarm','HeavySwarm','SwarmRouter','SpreadSheetSwarm','AutoSwarmBuilder','RoundRobinSwarm') if hasattr(swarms,n)])"` lists the importable types (ForestSwarm/PlannerWorkerSwarm need submodule imports, see Pitfalls); `references/swarm-types.md` holds 14 entries matching the table. Note: system python may be PEP-668-locked — this box uses venv at /home/khuchinque/.venvs/swarms (swarms 15.0.0 installed there).
