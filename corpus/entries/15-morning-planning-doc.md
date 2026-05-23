---
id: 15
title: Morning planning doc paid off all day
quadrant: clever_industrious
principle: cross_project_compounding
source: catalogdna/docs/internal/Hammerstein Observations - Bot.md (<another machine> interactive 2026-04-13, obs.4)
quality: medium
---

At ~8:00 AM on a 7-hour <another machine> interactive session, Claude wrote `docs/internal/bot-improvements-2026-04-13.md` to capture the strategic conversation about bot workflow improvements. By 4:00 PM, that doc had been referenced or extended six separate times:

- (a) Q1-Q5 decisions were locked there incrementally, each marked "DECIDED 2026-04-13" so future-Claude could find them.
- (b) The harmonic-ambiguity pattern doc was structured the same way.
- (c) The album-level reframe plan doc was structured the same way.
- (d) The planner CLI default-action refinement was added there at end of day.

**The cost was 30 minutes writing the doc. The payoff was avoiding the same alignment conversation five times.**

This is clever-industrious applied to the session's *meta-structure*: at the start of a session that's going to produce decisions, write the decisions into a doc as you make them. The marginal cost is low (you were going to make the decision anyway); the marginal value is high (you stop having to re-justify it).

The cross-project compounding angle: the same morning planning doc pattern appears across catalogdna, GS, the personal site, and twar / gta. Each project's mature workflow has a "decisions doc" that absorbs in-session decisions and persists them past context-window boundaries. **This is mature-rules-as-architecture in its smallest form**: the discipline of writing the doc is encoded into the project's session-start rituals, not into prompts.

For Hammerstein-the-AI: when a user starts a session that is going to produce multiple decisions, the bot's first proactive move (after understanding the scope) should be to suggest a decisions doc. Then absorb each decision into it as it lands. The bot's output across the session is then **incremental edits to the decisions doc** plus the strategic outputs the user asked for, not just the strategic outputs.

Counter-observation: not every session needs a decisions doc. Sessions that produce one clean decision do not. The discipline applies when (a) multiple decisions will compound across the session, and (b) the session length exceeds the context window's comfortable working size. Below those thresholds, the doc is overhead.
