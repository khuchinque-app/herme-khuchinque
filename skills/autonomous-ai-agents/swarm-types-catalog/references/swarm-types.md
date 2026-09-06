# The 14 Swarm Types — Verified Details

Source: docs.swarms.world (Swarms framework, kyegomez/swarms), fetched 2026-09-06.
User's canonical list preserved verbatim; verified class/URL notes inline.

## 1. SequentialWorkflow
`SequentialWorkflow(agents=[...], max_loops=1, output_type="dict", team_awareness=False, autosave=True, drift_detection=False, drift_threshold=0.75, drift_model="claude-sonnet-4-5", shared_memory_system=None, multi_agent_collab_prompt=False)`
- Agents execute one after another; each receives the previous output as context.
- Sync + async; `batch_run(tasks)`; thread-pool concurrent task processing over the same chain.
- drift_detection: a judge agent scores semantic alignment of final output vs original task; below threshold the pipeline reruns until it passes; unparseable judge output → skipped, last result returned.
- Use: well-decomposed linear pipelines — cheapest, most deterministic.

## 2. ConcurrentWorkflow
`ConcurrentWorkflow(agents=[...], output_type="dict-all-except-first", max_loops=1, auto_generate_prompts=False, show_dashboard=False, autosave=True)`
- ThreadPoolExecutor fires every agent in parallel on the SAME task; per-agent status tracking.
- `run(task, img, imgs, streaming_callback)` — callback gets (agent_name, chunk, is_final).
- `batch_run(tasks)` runs tasks sequentially, agents concurrent within each.
- Use: independent perspectives, maximum throughput; loses ordering.

## 3. AgentRearrange
`AgentRearrange(agents=[...], flow="agent1 -> agent2, agent3 -> agent4", max_loops=1, output_type="all", memory_system=None, team_awareness=False, time_enabled=False, message_id_on=False)`
- Flow DSL: `->` sequential, `,` concurrent, mixable in one string.
- REMOVED in current versions: `human_in_the_loop`, `custom_human_in_the_loop`, `rules`, and the `H` flow token.
- output_type: "all" | "final" | "list" | "dict".
- Use: known topology with parallel branches, no full graph machinery.

## 4. GraphWorkflow
`GraphWorkflow(nodes={id: Node}, edges=[Edge], entry_points=None, end_points=None, max_loops=1, auto_compile=True, backend="networkx", checkpoint_dir=None, on_node_complete=None, max_parallel_nodes=None)`
- Full DAG executor: topological sort into layers, independent nodes auto-parallelized.
- Backends: networkx (default) or rustworkx (faster, large graphs). Graphviz visualization. JSON save/load. Cycle detection. Per-node callbacks + token streaming. `auto_compile` pre-computes execution plans for multi-loop runs.
- Use: complex dependencies, fan-out/fan-in patterns.

## 5. MixtureOfAgents
`MixtureOfAgents(agents=[...], aggregator=Agent|None, aggregator_system_prompt="...", layers=1, max_loops=1, output_type="final", model_name=...)`
- Each layer: all agents run concurrently with full context; outputs appended to conversation; context updates; final aggregator synthesizes.
- `reliability_check()` raises ValueError if no agents / no aggregator prompt / no layers.
- GOTCHA: `run()` catches exceptions internally and returns `"Error: {e}"` string — check return value, don't try/except.
- Use: quality over cost — N× tokens for variance reduction.

## 6. GroupChat
`GroupChat(agents=[...], max_loops=20, threshold=0.5, recency_penalty=0.3, recency_window=1, output_type="str-all-except-first", auto_equip=True)`
- Turn-based, SELF-SELECTING: each turn every agent is asked concurrently (asyncio.gather + to_thread) via forced `respond(score, message)` tool call; highest recency-adjusted bid above threshold takes the floor — exactly one speaker per turn.
- Empty message never wins; turn with no qualifying bid = lull = chat ends (other stop: max_loops messages posted).
- `idle_timeout` accepted for back-compat but NOT used to end the chat.
- Import: `from swarms import Agent, GroupChat, RESPOND_TOOL`.
- Use: debate, brainstorming, decision-making.

## 7. ForestSwarm
`ForestSwarm(trees=[Tree(...)], shared_memory=None, rules=None, save_file_path=...)` — trees of `TreeAgent(name, description, system_prompt)`
- Routing: keyword extraction + litellm embedding similarity (default "text-embedding-ada-002") + cosine distance; `find_relevant_tree(task)` then best agent within it.
- `run(task, img)`, `batched_run(tasks)`; agents auto-organized by semantic similarity; add/remove agents without reconfiguring.
- Use: many domains × many specialists where one boss-LLM router would be the bottleneck.

## 8. HierarchicalSwarm
`HierarchicalSwarm(agents=[workers], director=None, max_loops=1, director_model_name="gpt-5.4", feedback_director_model_name="gpt-5.4", director_feedback_on=True, planning_enabled=False, parallel_execution=True, max_workers=None, agent_as_judge=False, judge_agent_model_name="gpt-5.4", max_agent_retries=1, director_settings=None, interactive=False)`
- Director decomposes → orders workers (parallel by default, pool ≈95% cores) → synthesizes; optional planning phase, judge-informed feedback loop, retries (failed worker marked unavailable in shared conversation and reported to director).
- `agents` must not be empty; director auto-created if None.
- Use: decomposition itself is the hard part; 20+ agents.

## 9. HeavySwarm
`HeavySwarm(question_agent_model_name="gpt-5.4", worker_model_name="gpt-5.4", variant="default", max_loops=1, timeout=900)`
- Flow: question agent decomposes task into specialized questions → variant's specialists answer in parallel (pool ≈90% cores) → captain synthesizes; `max_loops` iterates on previous results.
- Variants: "default" = 5 agents (Research/Analysis/Alternatives/Verification + Synthesis, 4 questions); "medium" = 4 (Captain + Harper/Benjamin/Lucas, 3 questions); "heavy" = 16 (Grok captain + 15 domain specialists, 15 questions).
- Use: deep research-grade analysis.

## 10. SwarmRouter
`SwarmRouter(swarm_type=SwarmType, agents=[...], ...)` — single entry point dispatching to any supported architecture.
- SwarmType literal includes: AgentRearrange, MixtureOfAgents, SequentialWorkflow, ConcurrentWorkflow, GroupChat, MultiAgentRouter, HierarchicalSwarm, MajorityVoting, CouncilAsAJudge, HeavySwarm, LLMCouncil, DebateWithJudge (+ RoundRobin, PlannerWorkerSwarm).
- Required params per type: Sequential/Concurrent → agents≥1; AgentRearrange → agents + rearrange_flow; HierarchicalSwarm → workers (director auto); GroupChat → agents≥2; MajorityVoting → ≥3 recommended; HeavySwarm → worker+question models + variant; DebateWithJudge → ≥3 (pro/con/judge).
- NOT valid types (raise SwarmRouterConfigError): "AutoSwarmBuilder", "auto", "BatchedGridWorkflow".
- Use: prototyping — swap `swarm_type=` without rewriting orchestration.

## 11. SpreadSheetSwarm
`SpreadSheetSwarm(agents=[...], max_loops=1, autosave=True, save_file_path=None, load_path=None)`
- All agents run tasks concurrently; every execution logged to CSV (Run ID, Agent Name, Task, Result, Timestamp); `export_to_json()`, `data_to_json_file()` auto after run when autosave.
- CSV config columns: `agent_name,description,system_prompt,task,model_name,max_loops`; call `load_from_csv()` explicitly AFTER construction (matches rows to agents by agent_name), then `run_from_config()`.
- GOTCHA: constructor reliability check runs before CSV loading — non-empty `agents` list required even with `load_path`.
- Use: data-processing grids, auditable batch runs.

## 12. AutoSwarm (class: AutoSwarmBuilder)
`AutoSwarmBuilder(name, description, verbose, max_loops, boss_agent_model_name, interactive, max_tokens, execution_type, boss_agent_system_prompt)`
- User URL /api/auto-swarm 404s; real page: https://docs.swarms.world/api/auto-swarm-builder. CLI: `swarms autoswarm --task "..." --model "gpt-4" [--no-run -o out.py]`.
- Boss agent analyzes the task, designs agent roster + architecture. execution_type: "return-agents" (spec dict) | "return-swarm-router-config" (full router config incl. swarm_type + rearrange_flow) | "return-agents-objects" (instantiated Agents).
- Use: dynamic/evolving tasks where you don't want to hand-design the roster.

## 13. SimpleSwarm
- User URL /api/simple-swarm 404s; no `SimpleSwarm` class in current `swarms.structs` exports (verified against v15 master `__init__.py`).
- Closest shipped minimal architectures: `RoundRobinSwarm` (true round-robin distribution with optional turn awareness) and the functional helpers in `swarming_architectures.py` (`circular_swarm`, `star_swarm`, `mesh_swarm`, `pyramid_swarm`, `one_to_one`, async `broadcast`).
- If the user's source is a specific tutorial/version, confirm the class name against the installed package before importing.

## 14. WorkerSwarm (class: PlannerWorkerSwarm)
- User URL /api/worker-swarm 404s; real page: https://docs.swarms.world/api/planner-worker-swarm.
- Planner-worker-judge cycle (based on Cursor's "Scaling long-running autonomous coding" research): planner decomposes goal into prioritized tasks with dependencies → shared TaskQueue → workers claim + execute concurrently via ThreadPoolExecutor (no worker-to-worker coordination) → judge evaluates: complete | fill gaps (replan with feedback) | drift (fresh start).
- Params: agents (non-empty), max_loops (cycles), planner_model_name, judge_model_name, max_sub_planner_depth (1=no sub-planners, 2=CRITICAL tasks decomposed once), pool timeout per cycle, per-task timeout, max_workers (default min(len(agents), cpu_count)).
- `get_status()` → structured queue/swarm report. Raises ValueError if no agents or max_loops<=0.
- Use: long-horizon autonomous coding / multi-cycle goal pursuit.

---

## Shared runtime behavior (all types)
- Most take `List[Agent]`; mix providers freely (LiteLLM normalizes).
- Convention: `.run(task)` + usually `.batch_run(tasks)`; helpers `find_agent_by_name`, `Conversation`, `multi_agent_exec`.
- Releases every ~2 weeks — re-verify constructor signatures against docs.swarms.world/llms.txt before shipping.
- Full class inventory: https://docs.swarms.world/architectures/structures-catalog (40+ classes incl. AuctionSwarm, LLMCouncil, MajorityVoting, CouncilAsAJudge, DebateWithJudge, AdvisorSwarm, SelfMoASeq, SocialAlgorithms, SubagentRegistry).
