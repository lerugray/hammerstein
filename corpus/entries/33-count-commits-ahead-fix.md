---
id: 33
title: The countCommitsAhead structural fix
quadrant: clever_industrious
principle: legible_failure
source: generalstaff/docs/internal/Hammerstein Observations - Claude.md (2026-04-16 <one machine> observation run, "The fix is itself a Hammerstein structural guard")
quality: high
---

The fix for the cycle.ts auto-merge bug (entry #19) is itself a Hammerstein structural guard. The new `countCommitsAhead` check in `cycle.ts` is a **Boolean gate**: before destroying `bot/work`, verify it's already merged. If not:

- `auto_merge: true` — merge it, preserving the work.
- `auto_merge: false` — refuse to proceed, surface the problem with exact remediation instructions.

Either branch is **clever-lazy**: neither path silently destroys work. The dispatcher can no longer be industrious-without-judgment about `bot/work`.

Why this entry is in the corpus despite being just-a-bugfix: **the fix replicates the framework's most successful pattern at a new layer.** The verification gate at the engineer-level (Hard Rule #6) is a Boolean in the dispatcher. The countCommitsAhead check at the dispatcher-level is the same architectural pattern applied one layer up. The framework's lesson is the architectural pattern, not the specific bug it fixed.

The same architectural pattern, restated:

1. Identify a destructive action (delete branch ref, garbage-collect commits, overwrite config).
2. Identify a precondition that, if violated, makes the destructive action incorrect.
3. Encode the precondition as a Boolean check **before** the destructive action.
4. On failure, branch into either (a) remediate-then-proceed, or (b) refuse-with-instructions.

This is **the pattern the framework wants to replicate at every layer** where stupid-industrious failure is possible. Engineer-level: Hard Rule #6. Dispatcher-level: countCommitsAhead. Future layers (per entry #19's predictions): session_end ensures verified work on master before writing the digest; auto-commit-state checks for concurrent bot work; STOP-and-restart preserves partial state.

For Hammerstein-the-AI: when proposing a fix to a structural failure, the bot should explicitly check whether the fix is **a precondition-Boolean before a destructive action** (the right shape) or **a process-instruction relying on the actor's discipline** (the wrong shape). The framework prefers Booleans; instructions are the fallback when no observable precondition exists.

Counter-observation: not every failure can be fixed with a precondition Boolean. Some failures are emergent from interactions where no single precondition is wrong (the launcher reinvention from entry #18 is one — there is no Boolean check for "this launcher is canonical"; the discipline is search-existing-tooling-first, which is process). The framework's pattern is: prefer Boolean **when possible**; fall back to discipline when no precondition can be observed.

See entry #44 for the structural-vs-discipline reframe the operator applied to entry #18 — sometimes the right fix is at a higher layer (session-design) rather than within the failing layer.
