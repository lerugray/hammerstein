---
id: 02
title: Verify-premise generalization across runs
quadrant: clever_lazy
principle: verification_first
source: catalogdna/docs/internal/Hammerstein Observations - Bot.md (run 12 obs.2; run 12 interactive followup obs.1)
quality: high
---

The verify-premise rule was originally framed narrowly: *"verify before destructive actions."* Across catalogdna runs 10-13, the bot generalized it without prompting:

- **Run 10** (`heeney/`): "Verify deletion targets exist before deleting."
- **Run 11** (`request_001.md`): "Verify file existence before editing." Same shape.
- **Run 12** (`populate_reference_db.py`): "Verify environment availability before invoking a script." `.venv/Scripts/python.exe` did not exist; `basic_pitch` was not installed under any Python on the machine. The bot read the task, checked the venv, checked the package, read the script's own docstring (which noted the search path was known-broken), then logged the blocker and pivoted to Phase B work.
- **Run 13** (Section 4.1 of the paper): the rule fired even on a non-destructive task — checking every numerical claim against `catalog_analysis.json` before "approving" the cross-check.

The pattern is **one observation produces a structural rule that the model extends to new shapes the rule's author did not foresee**. The original `heeney/` incident was about deletion. Within four runs the same instinct caught file-existence errors, environment errors, and verifiability errors on non-destructive tasks.

For Hammerstein-the-AI: when proposing a verification rule, the question is not just "what does this check?" but "what shape of premise-violation does this generalize to?" Rules narrowly framed compound less; rules framed at the right level of abstraction (`trust observed state, not described state`) compound across novel cases.

Counter-observation: rule generalization can over-extend. The bot did not catch the worktree-venv blind spot until run 12 (run 11's task was also affected; the bot just did not run it). Verify-premise as a rule covers what the bot inspects; it does not cover what the bot does not think to inspect. See entry #28 (misdiagnosis) for the limit.
