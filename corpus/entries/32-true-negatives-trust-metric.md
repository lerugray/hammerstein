---
id: 32
title: True negatives over true positives as trust metric
quadrant: clever_industrious
principle: verification_first
source: generalstaff/docs/internal/Hammerstein Observations - Claude.md (2026-04-16 full-day build session, obs.4)
quality: high
---

Across 35+ GS cycles, the verification gate never approved bad work (no false positives) and correctly rejected hands-off violations and test failures (3 true negatives).

The framework's claim about which metric matters:

> The false-positive rate is the number that matters for **trust** — a gate with false negatives (missed bad work) is useless, but a gate with false positives (rejected good work) is merely annoying. **Zero false positives after 35 cycles is the trust-building metric.**

But the deeper claim:

> The metric to track going forward is **not "what percentage of cycles verify"** but **"when the gate DOES reject, was the rejection correct?"** A gate that verifies everything is useless — it's just rubber-stamping. The gate's value is proven by **true negatives** (correct rejections), not by **true positives** (correct verifications).

Why this is verification-first applied to the gate's own evaluation:

A verification gate that has never rejected anything is **structurally indistinguishable** from no gate at all. The gate could be a Boolean check or a `return true` — same observed outcome. Trust requires the gate to demonstrate it can reject; rejections demonstrate it is operating.

The 3 true negatives at GS:

- Two reviewer.ts hands-off violations: the engineer modified a file on the hands-off list, and the gate caught it. Both were subsequently approved by human review (the changes were fine, but the gate was right to flag — the policy existed for a reason).
- One verification-gate failure from worktree state: the test environment was in a bad state, the gate correctly refused to verify work it couldn't confirm.

For Hammerstein-the-AI: when reviewing a verification system, the bot's diagnostic question is: *"how often does this gate reject? what are the rejections? are they correct?"* A system with high pass-rate, no documented rejections, and confident operators is a system that probably has a silent verification-gate-as-rubber-stamp problem.

The general lesson: **a system's reliability is proven by the cases where it correctly says no, not by the cases where it correctly says yes.** Saying yes is the easy default; saying no requires the structural property the framework is testing.

Counter-observation: zero false-positive rate is necessary but not sufficient. The gate's failure mode is the **first false negative** — bad work that the gate approves. The first false negative is predicted to involve code that passes all tests but introduces a latent bug that only manifests under conditions the test suite doesn't cover. Until that case happens and is logged, the gate's robustness against the dangerous tail is unproven.

See entry #50 for the meta-claim about logs as the load-bearing artifact: the rejections are only legible because the log captures them.
