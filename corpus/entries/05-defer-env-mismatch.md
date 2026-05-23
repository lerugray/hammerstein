---
id: 05
title: Defer the env-mismatch fix
quadrant: clever_lazy
principle: counter_observation
source: catalogdna/docs/internal/Hammerstein Observations - Bot.md (<another machine> interactive 2026-04-13, obs.8)
quality: high
---

Claude tried to run `populate_reference_db.py` against 5 pending entries. All 5 failed with *"Downloaded 0 tracks."* Investigation revealed `yt-dlp` was not installed in the <another machine>'s `.venv`.

Three options:

1. Install `yt-dlp` via pip and retry.
2. Debug by trying alternative venvs / system Python.
3. Note the env mismatch and stop.

Claude chose **(3)**. Reasoning:

- The home bot has a working env and will retry tonight.
- Debugging an env mismatch on a one-off <another machine> session has zero compounding value.
- Claude's time is better spent elsewhere.

The clever-lazy call was *"this is a known-isolated env problem, accept the failure and move on."* The stupid-industrious call would have been *"I can fix this with enough effort."*

The Hammerstein-frame angle: **not every problem is mine to solve in the moment.** The right move is sometimes to flag and defer. A bot or interactive session that grinds through every blocker it encounters loses the option to make leverage choices about which problems are worth its time. Some problems are someone else's, in another context, on a different machine.

This is the BYOI principle applied to a single agent's own time: **delegate back to the user (or to the next session) the work that doesn't belong to this session's scope.** Surface the blocker structurally; let the next session inherit a clean problem statement; do not consume your own context on a one-off fix that will not compound.

Counter-observation: defer-and-flag can degenerate into avoidance. The discipline holds when (a) the blocker is genuinely contextual (env, machine state, account state), (b) the deferral cost is bounded (<1 day before the next session can pick it up), and (c) the surface area to flag is small enough that the deferral message itself is cheap. When any of these break, the right move is to fix-in-place even if it's not the highest-leverage work.
