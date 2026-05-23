---
id: 14
title: Density over duration in run 22
quadrant: clever_industrious
principle: game_design_framing
source: catalogdna/docs/internal/Hammerstein Observations - Bot.md (run 22)
quality: medium
---

Run 22 was framed at 4 hours but produced its densest output yet: P0-P6 all completed within ~3 hours of active work. 12 commits covering a hypothesis-confirming split analysis (P0), a 43-entry quality screen (P1), tracker maintenance (P2), pipeline scaffolding (P3), 4 Phase B items (P4), a 148-entry distance ranking (P5), and a Bandcamp catalog acquisition (P6). No grind work, no padding.

The bot's diagnosis: *"The 'density over duration' framing from the task list shaped behavior correctly — shorter budget + more authored depth targets = less time spent looking for things to do."*

This is the inverse of run 12, which had a 4-hour budget framed as "endurance test" and produced 35-min of useful work followed by Phase B padding. Run 22 took the same 4-hour wall-clock but framed it as "more authored depth targets in a tighter window" and produced 12 dense commits.

The game-design framing: **a bot's budget is not a duration constraint, it is a turn-structure constraint.** The number of meaningful moves in a turn depends on how the turn is structured, not just how long it is. Run 12's structure was "one open-ended block" — many possible moves, no signal about which mattered. Run 22's structure was "P0 through P6, each authored as a depth target" — clear move list, clear stopping point.

For Hammerstein-the-AI: when a user gives a time budget for strategic reasoning, the bot's first move is to convert the budget into a structured set of authored depth targets. Open budgets default to grind. Structured budgets default to productive density.

This is also a clever-industrious entry, not clever-lazy: the bot did 12 commits of real work, not the smallest possible work. Clever-industrious is the right mode when the assigned depth targets are well-chosen. The clever-lazy move was the *upstream* shaping — the task list author choosing density-over-duration framing, which let the bot's clever-industrious execution land productively.

Counter-observation: the run's density was partly driven by the P0 task being genuinely interesting (Bowie Low side split). Would the same density hold if the authored task was mechanical? Not testable from inside the run. Worth flagging for future runs whether interest-content of authored tasks is itself a load-bearing variable for density-over-duration framing.
