---
name: graph-engineering
description: Build knowledge graphs; orchestrate agent task graphs.
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [Knowledge-Graphs, Graphrag, Orchestration, Ontology]
---

# Graph Engineering

The discipline of designing the structures agents work through — not the prompts. Two halves: knowledge graphs (what agents remember — ontology → extraction → fusion → serving) and task graphs (how agents work — fan-out, verifier separation, stop rule, human gate). Distilled from Southeast University's graduate KG course (npubird/KnowledgeGraphCourse) plus Google DeepMind × MIT agent-scaling research. No dependencies; the substance lives in this skill's `references/` files.

## When to Use

- "build a knowledge graph from my docs" / "add graph memory or GraphRAG to an agent"
- "extract entities/relations/events from text" / "design an ontology"
- "dedupe/merge entities" / "these are the same person, right?"
- "orchestrate multi-agent workflows as a graph" / "should I use subagents here?"
- "teach me graph engineering" → Teaching Mode

## Prerequisites

None — pure knowledge skill. Load reference files on demand with `skill_view(name="graph-engineering", file_path="references/<file>")`.

## How to Run

Core mental model: a knowledge graph is a product with a schema, not a pile of triples. Model the domain BEFORE extracting, fuse BEFORE storing, verify at every stage.

The 9-stage pipeline (run in order; stages 4-6 may collapse into one pass for small projects, but NEVER skip stage 3 ontology or stage 8 fusion — that's where real graphs fail):

1. Scope & value test — a graph pays off only for multi-hop queries, recurring entities across docs, or relationships-as-data. Single-hop lookups → use a table, stop.
2. Representation choice — property graph (pragmatic default), RDF/OWL (interop/DL reasoning), or typed edges in JSON/SQLite (<50K nodes). Decide time + provenance attachment NOW; retrofitting after fusion is impossible.
3. Ontology modeling — 5-15 entity types, 10-30 relations with domain/range, competency questions as spec AND test suite.
4. Entity extraction — dictionary/rules for closed vocabularies first, LLM with ontology-in-prompt for open text; always capture span + source pointer.
5. Relation extraction — only between stage-4 entities; validate domain/range in code; evidence quote must ASSERT the relation, not just co-occur.
6. Event extraction — dynamic domains: events as first-class nodes (trigger + typed arguments + time), never flattened to pairwise edges.
7. Quality gate — ≥90% precision on a 50-item sample before fusion; fix the prompt, not the output.
8. Knowledge fusion — blocking → layered matching (string/attribute/structure) → deterministic merge policy; erroneous merges are worse than missed ones.
9. Serve to LLMs — GraphRAG (link query → expand 1-2 hops → serialize subgraph with provenance), graph-as-memory write-back loop, contradiction handling via time + provenance.

Working rules: schema first, always; provenance on every fact; incremental 10-doc pilot before scaling; the LLM is stage machinery inside stages 4-6, not the pipeline.

Teaching Mode (user wants to LEARN): anchor every stage in one real project of theirs, generate mermaid diagrams as artifacts (pipeline, their 3-type ontology, an extracted subgraph, the diamond with their jobs), one stage per exchange ending in a small exercise, close with a starter ontology.yaml + drawn task graph.

## Quick Reference — task-graph decision rules

- Delete fake edges: an arrow is real only when work flows through it ("summarize then check calendar" — calendar never reads the summary → parallelize).
- The diamond: plan → parallel workers → SEPARATE verifier contexts → one owned merge. A model grading its own work in its own context misses most mistakes; give verifiers different questions (correct? current? source real?).
- The stop rule (DeepMind × MIT, 180 configs): teams win ~80% on work that splits into independent pieces; EVERY multi-agent config loses on sequential work needing the full picture (degrading 39-70%). Uncoordinated merge amplifies errors 17.2×; one coordinator owning the merge → 4.4×. Split only where pieces never read each other's results; everything sequential stays with one agent.
- The human gate: route every irreversible edge (send, publish, delete, deploy) through approval; place it where a mistake is expensive to undo, not on every step. Judge on numbers that cannot argue back, never self-reports.
- Guardrails: max rounds per loop; one writer per file; routing in written steps, model fills jobs; hard cap on agent spawning.

## Procedure

1. Identify the half: memory/graph-building → run the 9-stage pipeline; orchestration → apply the Quick Reference rules (they map directly onto Hermes `delegate_task` fan-out and the human gate onto approval prompts).
2. Load the matching reference before acting:
   - references/task-graphs.md — orchestration, DAG design, when NOT to use subagents
   - references/modeling.md — stages 2-3 (representation, ontology method, worked example)
   - references/extraction.md — stages 4-7 (NER/RE/EE, LLM prompt pattern, failure modes)
   - references/fusion-and-llm.md — stages 8-9 (blocking/matching/merge, GraphRAG, graph-as-memory loop)
   - references/curriculum.md — theory depth, original lecture mapping
3. To refresh from upstream: run `scripts/sync-from-repo.sh` through `terminal`, then `read_file` each fetched file and `skill_manage` write_file it back.

## Pitfalls

- Extraction without an ontology produces "a word cloud with arrows", not a graph.
- Co-occurrence-driven relation hallucination ("Musk discussed Twitter" ≠ OWNS) — require asserting evidence.
- Skipping fusion is the #1 cause of useless real-world graphs; multi-hop queries break at duplicate boundaries *with confidence*.
- Never auto-accept an LLM-induced schema — induced ontologies overfit the sample docs; prune manually.
- k>2 hop expansion in GraphRAG is noise without re-ranking.

## Verification

`skill_view(name="graph-engineering")` lists all five references under linked_files; each competency question must path through the ontology on paper before extraction starts.

## Credits

Independent English distillation of 东南大学《知识图谱》 graduate course (Prof. Peng Wang, github.com/npubird/KnowledgeGraphCourse); task-graph material from Google DeepMind × MIT "Towards a Science of Scaling Agent Systems" and Anthropic multi-agent engineering work. Source repo: github.com/codejunkie99/graph-engineering (MIT).
