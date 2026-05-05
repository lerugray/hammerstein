---
id: 06
title: One design pass, many parallel executions
quadrant: clever_lazy
principle: game_design_framing
source: catalogdna/docs/internal/Hammerstein Observations - Bot.md (<another machine> interactive 2026-04-13, obs.1)
quality: high
---

The harmonic-ambiguity reframe used 4 parallel agents (Phase B/C/D/F). Round 2 used 3 parallel agents (vault-ray + vault-john + source). The album-level webapp reframe used 3 parallel agents (backend + frontend + tests). All 10 agent runs succeeded on the first try.

The pattern that made it work: **write the design decision into a single pattern doc** (`harmonic-ambiguity-reframe-2026-04-13.md`, `album-level-reframe-plan-2026-04-13.md`), then have each delegated agent read the same doc and execute its own scope against it. The pattern doc absorbs the "what to do and why" decision exactly once. Each agent consumes it independently.

The alternative — main-thread sequential execution — would have eaten Claude's context budget and taken the entire day. Specific cost-leverage estimate: the harmonic-ambiguity work would have been ~3-4 hours of main-thread work; via parallel delegation it took ~30 minutes of active time + ~15 minutes of agent wall time.

**The shape: one design pass, many parallel executions.** Worth treating as a default for any large mechanical task.

This is clever-lazy in the highest-leverage form the framework has documented at the multi-agent level. The design work happens once; the executions parallelize because they share the absorbed context. The cost is the upfront effort to write the pattern doc precisely enough that an agent reading it cold can execute against it without escalating back to the orchestrator.

For Hammerstein-the-AI: when reasoning about whether to do work serially or split it, ask whether **the design decision is small relative to the execution work**. If yes, write the design as a doc, dispatch parallel executions. If no, sequential is correct because the design itself is iteratively shaped by execution feedback.

Counter-observation: parallel delegation only works because git was the communication channel. The orchestrator never had to pass rich context directly to each agent — they all read the same artifact. Any future feature requiring richer inter-agent context (e.g., "the second agent should know what the first found") would break the pattern.
