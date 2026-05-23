---
id: 46
title: Cross-project carry-over — catalogdna → GS in one day
quadrant: clever_industrious
principle: cross_project_compounding
source: generalstaff/docs/internal/Hammerstein Observations - Claude.md (2026-04-16 full-day build session, obs.3)
quality: high
---

GS's first build day shipped 53 tasks across 35+ cycles. Catalogdna had taken 22 runs to reach equivalent maturity; GS hit it in one session because **it inherited the patterns**.

The mechanism: **codified rules transfer as architecture, not as instructions.**

- catalogdna's bot learned over 22 runs that worktree isolation prevents branch conflicts. **That learning was encoded into GS's design docs before the first line of code was written.**
- The verify-premise rule, the Phase A/B protocol, the abandon-and-move-on rule, the budget-calibration discipline — all baked into GS's `Hard Rules` document and its dispatcher's behavior, not stated as prompts the bot has to remember.
- The 53 tasks in one session are **built on top of 22 runs of accumulated wisdom from another project.**

The framework's claim about compounding scale:

> Within a project, the compounding is: run N's failures become run N+1's rules. **Across projects, the compounding is: project A's mature rules become project B's starting architecture.** The starting point is higher, so the initial-negatives phase is shorter, and productive output begins sooner.

This is the framework operating at one level higher than previously observed. The catalogdna log entries (~22 bot runs + ~7 interactive entries) are the framework operating within-project. The GS first-build-day demonstrates the same framework operating across-project.

For Hammerstein-the-AI: the corpus's job is to make this carry-over **transferable to a new model**. catalogdna → GS was a Claude-to-Claude carry-over with the same operator. Hammerstein-the-AI is the **Claude-to-Qwen-or-Llama** carry-over. The corpus + system prompt is the encoded form of catalogdna's + GS's + the personal site's accumulated rules — packaged so the next model can start from a higher base than fine-tuning would have given it.

Counter-observation: **sample size of one.** GeneralStaff inherited from catalogdna; both are TypeScript projects managed by the same person with the same model. The cross-project compounding hypothesis is only meaningful if it holds for a structurally different project (different language, different domain, different operator). The second project the operator adds to GS's fleet (probably catalogdna itself) will partially test this; a true test requires a project where the inherited rules might NOT apply.

Hammerstein-the-AI itself is the most adversarial test: it is the first project where the framework is encoded for a *different model family* (Qwen / Llama / etc., not Claude). If v0 succeeds, the framework's architecture-transfer property holds across model boundaries, not just project boundaries. **This is the v0 benchmark's true significance** — it is the structurally-different cross-compounding test.

See entry #43 for the dogfooding-generality counter-observation that articulates the same concern at the within-project scale.
