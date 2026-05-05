---
id: 01
title: Heeney directory refusal
quadrant: clever_lazy
principle: verification_first
source: catalogdna/docs/internal/Hammerstein Observations Log.md (2026-04-12 60-min run entry); also personal site/vault/hammerstein-essay-draft.md (Entry 1)
quality: high
---

the operator copy-pasted two cleanup tasks from earlier audit notes into the bot's task list without cross-checking. One read: *"delete empty `heeney/` orphan directory."*

The bot did not run the task. It verified the premise first. It found that `heeney/` was not empty — the directory contained 14 real track-analysis files. The bot refused to delete, flagged the task as stale in its session notes, and moved on.

What makes this load-bearing for the framework: the bot's instructions at that moment did not contain an explicit "verify destructive premises" rule. The general caution was "never delete files unless the task says to" — and the task specifically said to. Technically the rule was satisfied. **The refusal came from a structural check inserted into a destructive pipeline: is the premise of this task still true?**

If the bot had been stupid-industrious — executing the instruction with total commitment to the wrong objective — the operator would have lost 14 tracks of analysis he cared about.

The clever-lazy lesson generalizes far past delete-by-name commands. The same shape applies to "edit this file that no longer exists" (run 11), "run this script under this venv that isn't installed" (run 12), and "rebuild this index whose source data has moved" (any future variant). The general rule the framework derives: **trust the current observable state, not the state implied by the task description**.

Counter-observation: the rule cost the bot ~30 seconds of verification on a task that 9-out-of-10 times will be valid. That overhead is the price of catching the rare-but-compounding tail. See entry #32 for why true-negatives are the trust metric, not throughput.
