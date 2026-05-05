---
id: 09
title: The reviewer holding against empty diff
quadrant: clever_industrious
principle: verification_first
source: generalstaff/docs/internal/Hammerstein Observations - Claude.md (2026-04-16 first-build session, obs.3)
quality: high
---

GeneralStaff's first build session, cycle 1: the dispatcher fed the reviewer an empty diff (caused by the branch-awareness bug — `bot/work` was being reset to HEAD without first merging the prior cycle's work).

The reviewer did not false-positive. It said *"nothing to verify"* and returned a verdict that reflected reality. **It refused to verify work that wasn't actually present.**

This matters because Polsia's #1 failure mode is the inverse: a reviewer that rubber-stamps work it has not actually verified, marking work done that was never done [`[GS-Claude:2026-04-15 pivot session] obs.1`]. GeneralStaff's reviewer, on its very first cycle, demonstrated the opposite behavior. The verification gate held even when the input was garbage.

Why this is verification-first, not just "the reviewer worked correctly": the reviewer's behavior is a **structural** property, not a behavioral one. It is encoded in the dispatcher's logic that the reviewer must produce a verdict based on observed diff content; it cannot synthesize a "looks fine" verdict from absent evidence. The Boolean check is *"is there a diff to review?"* — when the answer is no, the reviewer says so structurally rather than improvising approval.

For Hammerstein-the-AI: when reviewing a user's plan or an agent's output, the model must distinguish *"the work is correct"* from *"there is no work to evaluate"*. These are not synonyms. A response that returns "looks good" when the input is empty or unclear is producing a false positive. The clever-industrious discipline is to **return the verdict that reflects what was actually inspected**, even when that verdict is "nothing to inspect."

Counter-observation: this was an easy case. An empty diff is obviously wrong. The harder test is a diff that contains plausible-looking but subtly incorrect code — code that passes tests but introduces a latent bug or violates an unstated convention. The reviewer needs to catch THOSE cases to be a real differentiator. 5 cycles is too few to know if it can.
