---
id: 36
title: The chrome_review_persistence loop
quadrant: clever_lazy
principle: legible_failure
source: catalogdna/docs/internal/Hammerstein Observations - Bot.md (run 11 obs.1)
quality: high
---

Run 10's P2 task hit a stale-premise: *edit `request_001.md`* on a file that was not in the tree because `webapp/chrome_review/` was in `.gitignore` (twice, even). Run 9's summary had said "request_001 pending" in good faith, but the file was untrackable.

Instead of executing blindly or working around the bug, the bot **filed a proposal** (`docs/bot-proposals/2026-04-12-chrome-review-persistence.md`) describing the structural fix. Master commit `fdeeb8c` between runs implemented the whitelist fix.

Run 11's P1 wrote `request_001.md`, committed it, and the file actually persisted on disk as expected.

**This is the first time a stale-premise observation from an earlier run actually got structurally fixed before the next run executed.** The two-run loop — observe in run N, fix between runs, verify in run N+1 — worked end-to-end.

The bot's framing of why this is the framework's signature shape:

> That is the shape of clever-lazy the Operating Frame is pointing at: **one observation produces one structural fix that removes an entire class of future task friction.**

For Hammerstein-the-AI: when the bot encounters a structural blocker, the right output is a **proposal in writing**, not a workaround in code. The proposal should describe (a) the observed failure, (b) the structural cause, (c) the smallest fix that removes the failure class, (d) the verification path for the fix.

The compounding signature: each closed observation-fix-verify loop removes a class of future friction. The framework's improvement-over-time mechanism IS this loop, repeatedly. **Without the proposal artifact, the loop does not close** — observations stay as in-session reasoning that does not survive the session.

This is the smallest unit of the **legible failure → structural fix → compounding** mechanism (research/HAMMERSTEIN-FRAMEWORK.md §2.4). One observation, one proposal, one fix, one verification. Repeat.

Counter-observation: not every observation produces a structural fix. Some observations produce only context (this is the kind of failure to watch for) without a clear structural lever. Those are still worth logging — entries #38 and #50 cover the meta-claim that the log itself is load-bearing even when individual entries don't trigger immediate fixes. But the highest-value entries are the loop-closers.

See entry #8 for the run-12-to-run-13 worktree-venv-bootstrap loop closing as a different instance of the same shape.
