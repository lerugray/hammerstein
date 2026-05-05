---
id: 18
title: The launcher reinvention failure
quadrant: stupid_industrious
principle: verification_first
source: generalstaff/docs/internal/Hammerstein Observations - Claude.md (2026-04-24 evening)
quality: high
---

the operator asked Claude to launch an overnight GS bot session. The proven launch path was `scripts/scheduled-run-session.ps1` → `scripts/run_session.bat` → `bun src/cli.ts session`. The chain handled three non-trivial things: (1) PATH setup including `C:\Program Files\Git\bin`, `%USERPROFILE%\.bun\bin`, etc.; (2) `OPENROUTER_API_KEY` loading from a .env file; (3) tee'd logs into `logs/scheduled_<ts>.log`.

Claude had **already read** `scheduled-run-session.ps1` in the same session. Could see the full chain. Knew it existed.

Instead of calling the proven .bat, Claude wrote a fresh `.bat` from scratch to `C:\Users\rweis\launch-gs-overnight.bat`, set PATH with **only** `~/.local/bin` + `~/AppData/Roaming/npm` (missed Git bin + `~/.bun/bin`), didn't load `OPENROUTER_API_KEY`, didn't tee logs.

Result: cycles fired, engineers exited 127 (`claude not found`). Claude then proceeded to make **three more launch attempts** in roughly the same shape before the operator called it out.

**Measurable outcome:** 4 failed launch attempts (~30 min total), 18+ fast-fail bot cycles burning `consecutive_failures` budget across 13 projects, ~30 min of operator time spent diagnosing my mistakes and killing windows.

The Hammerstein-specific lesson: **Industrious-but-stupid isn't just "doing the wrong thing fast." It's specifically "doing the work to reinvent a solution that already exists, without first checking whether it exists."** The proven .bat was 200 LOC away on disk, in the same directory I was launching from.

The discipline failure was treating *"I know roughly what to do"* as a substitute for *"I'm using the canonical path."* For automation infrastructure on a project with real customers, "roughly right" is destructive — it manifests as 18 fast-failing cycles burning consecutive_failures budget across the whole fleet, and it teaches the operator to distrust the bot.

What I should have done, in order:
1. `grep -rln "bun.*session\|run_session" scripts/` to find existing launchers.
2. Read the existing launcher end-to-end before deciding whether to extend it.
3. If extension was truly needed (it wasn't), copy the existing one and modify, never reinvent from scratch.
4. Use the existing one as-is when it covers the use case (it did).

**Search-existing-tooling-first is the rule.** This generalizes: state-sync helpers exist; bot status checkers are documented; provider config loaders exist; deploy wrappers exist. Each has a canonical form in one of the operator's projects; reinventing any of them on a fresh session would reproduce this failure shape.

See entry #44 for the operator's structural reframe of this incident — the deeper fix is *session-design* (don't ask one session to wear too many hats), not *session-discipline*.
