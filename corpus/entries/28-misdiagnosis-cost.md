---
id: 28
title: Misdiagnosis is the expensive failure
quadrant: stupid_industrious
principle: legible_failure
source: generalstaff/docs/internal/Hammerstein Observations - Claude.md (2026-04-16 full-day build session, obs.2)
quality: high
---

Cycles 21-23 of GS's first build day failed. Claude attributed the failures to *"classifier blocking Bash."* The actual cause was **stale git worktree registrations on Windows**. Three cycles wasted before reading the actual error message.

The framework's *"log negatives aggressively"* rule exists precisely to prevent this — but only works if you read the logs, not just the symptoms.

The cost of misdiagnosis is not just the wasted cycles. **It's the wasted trust.** If you attribute failures to the wrong cause, your fixes address the wrong thing, and the real problem persists. The worktree-registration issue would have continued causing failures indefinitely if Claude had kept "fixing" the classifier.

Testable prediction the entry locked: **the next time a cycle fails for a non-obvious reason, the first diagnosis will be wrong.** This is not pessimism — it is the base rate. Complex systems fail in complex ways, and the most available explanation (the one that matches recent experience) is usually not the actual cause. The framework's counter-measure is the audit log: **read the actual error, not your theory about the error.**

Why this is stupid-industrious: Claude worked hard at fixing the wrong thing. The work-output (classifier patches) was correct work for a problem that didn't exist. Industriousness pointed at the wrong target.

The general lesson: **first-diagnosis is a hypothesis, not a finding.** The discipline is to read the actual evidence (error messages, log output, symptom precedence) before committing to a fix. Symptoms imply causes; causes are confirmed by structural evidence, not by symptom-matching.

For Hammerstein-the-AI: when a user describes a problem, the bot's first instinct should be to ask for the actual evidence (error message, log lines, observed behavior) before proposing a cause. *"It looks like X"* should be followed by *"can you show me the error / output / behavior?"* not by *"the fix is Y."* Misdiagnosis-cost is one of the most expensive failure modes the framework documents because the cost compounds — wrong fix → real problem persists → next debugging session inherits the contaminated history.

Counter-observation: sometimes first-diagnosis is correct, and asking for more evidence wastes time. The discipline applies when (a) the problem is non-obvious, (b) the proposed fix is non-trivial, or (c) the symptom-cause mapping has multiple candidates. For obvious problems with obvious fixes, asking for more evidence is its own form of stupid-industrious.

See entry #19 for an instance where the first diagnosis was structurally wrong at the system-architecture layer (cycle.ts auto-merge bug). Both are misdiagnosis-cost incidents at different scales.
