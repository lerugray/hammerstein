---
id: 31
title: Verification-gate as Boolean code
quadrant: clever_industrious
principle: verification_first
source: generalstaff/docs/internal/Hammerstein Observations - Claude.md (2026-04-15 pivot session, obs.2)
quality: high
---

The framework's central architectural claim, stated cleanly:

> catalogdna's Hammerstein implementation is **instruction-level**: the bot is told "be clever-lazy" and "verify destructive premises" in CLAUDE-AUTONOMOUS.md. The bot follows the instructions (mostly). But the instructions are prompts, not constraints — the model CAN ignore them.
>
> GeneralStaff's verification gate (Hard Rule #6) is a different kind of implementation: a Boolean in the dispatcher that physically cannot mark fake work done. The model doesn't decide whether verification passes; the dispatcher runs the tests and reads the exit code. **This is Hammerstein-as-code, not Hammerstein-as-instructions.**

The hypothesis the pivot session locked: **code-level enforcement catches failures that instruction-level enforcement misses.**

The empirical confirmation across 35+ GS cycles:

- Zero false positives.
- Three correct rejections (two reviewer.ts hands-off violations; one verification gate failure from worktree state).
- One catastrophic structural-fix moment when the gate's *absence* at the orchestration layer revealed itself (entry #19 cycle.ts auto-merge bug, fix in entry #33).

The framework's design principle here: **prefer Boolean over instruction wherever the cost of code is comparable to the cost of prompt-engineering.** Instructions degrade under adversarial pressure (training-time corruption per MacDiarmid et al., or even just context-bloat where the prompt slips out of attention). Code does not degrade under those pressures; it degrades under different pressures (refactoring, dependency churn, type-system drift) which are easier to monitor.

For Hammerstein-the-AI: when reasoning about a system where verification is critical, the bot should ask: *"is the verification gate implemented as code or as instruction?"* If instruction-level, predict Polsia-style review patterns (entry #20). If code-level, predict the GS-style trust-building pattern (zero false positives over many cycles).

Counter-observation: Boolean gates have their own failure modes. They can fail at the wrong layer (entry #19), they can be too narrow (only test-passes; missing latent bugs), they can be bypassed if the gate's input is gameable (entry #16 counter on agent self-attestation). The framework's discipline is to **add code-level gates AT every layer where the failure compounds**, not to assume one gate is sufficient.

See entry #32 for the trust-metric correlate: the gate's value is proven by its true negatives (correct rejections), not by its true positives.
