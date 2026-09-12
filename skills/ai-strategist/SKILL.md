---
name: ai-strategist
description: Decide AI work via metric, options ladder, kill criterion.
version: 1.0.0
metadata:
  hermes:
    tags: [strategy, ai, planning]
---

# AI Strategist

Bridges technical teams and business priorities. Turns "we want an agent"
into a decision with measurable value, explicit costs, and kill criteria.

## When to use
User asks: should we build X with AI? Is this feature worth it? How to
prioritize AI work? Build vs buy vs adopt-skill? AI roadmap?

## Procedure
1. **Restate the business outcome** in one sentence, no tech words
   ("cut support response time to <1h", not "deploy an agent loop").
2. **Invent the metric before scoring options**: what number moves if this
   works, baseline today, monthly cost (tokens, keys, maintenance, review).
3. **Generate 2–4 options across the ladder**: do nothing / prompt-only /
   buy or SaaS / adopt existing skill-MCP / custom build. For each: one-line
   mechanic, cost band, time-to-value, main risk.
4. **Recommend ONE** with the deciding criterion named (usually lowest
   credible cost to first measured win). Include a **kill criterion**: what
   result in what timeframe means we stop.
5. **Flag harness gaps**: memory, orchestration, watchdog, evals — name what
   already exists on this host (ECC vault, brain, graphify, Hermes skills,
   systemd watchdogs) so nothing is rebuilt.

## Anti-patterns
- Recommending custom builds when an installed skill or MCP covers 80% —
  always check `skills_list` and `ecc memory search` first.
- Value claims without a measurement plan or a number.
- Roadmaps with no kill criteria.
