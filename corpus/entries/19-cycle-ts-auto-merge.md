---
id: 19
title: The dispatcher cycle.ts auto-merge bug
quadrant: stupid_industrious
principle: verification_first
source: generalstaff/docs/internal/Hammerstein Observations - Claude.md (2026-04-16 <one machine> observation run)
quality: high
---

Three GS cycles ran end-to-end. All three "verified" by the reviewer. All three diffs correctly implemented gs-056 (log rotation in `clean.ts` + tests). The verification gate did exactly its job: each diff matched its task, was verified, was rubber-stamped correctly.

**But zero of the three cycles' code reached `master`.** Each cycle's engineer commit was orphaned. Git reflog showed three commits on `bot/work` — two reachable from no branch, one from `bot/work` only. The verified work existed, then was garbage-collected.

Root cause: `cycle.ts` line 295:

```javascript
await $`git -C ${project.path} branch -f ${branch} HEAD`.quiet();
```

The implicit assumption: the prior cycle's `bot/work` had already been merged into `HEAD`. But no code anywhere in the dispatcher performed that merge. On the work PC, merges happened manually (the operator or interactive Claude doing it by hand between cycles). On a fresh <one machine> session with zero manual merges, three consecutive cycles reimplemented gs-056 because each commit was overwritten by the next cycle's reset.

**This is the Hammerstein framework applied at the wrong layer.** All design effort had been focused on preventing the *engineer* (the per-cycle `claude -p` subprocess) from being stupid-industrious. Hard Rules 1, 5, 6, 7, 9 are engineer-level structural guards. Those rules worked. The engineer was clever and industrious — it wrote correct, verified code three times.

**The failure was one layer up: the dispatcher itself was stupid-industrious.** It confidently ran cycles end-to-end — picking projects, spawning engineers, running verification, recording verdicts — and threw the output away. The reviewer verdicts were correct. The cycle-end PROGRESS entries were correct. The per-cycle digests were correct. Every component was doing its declared job. **But the orchestration contract had a silent hole between "cycle ends" and "next cycle begins," and no single component owned closing it.**

Industriousness without judgment again. Damage compounding again. This time the bot wasn't the offender — the bot's manager was.

How it was caught: dogfooding, specifically a fresh-machine dogfood run. The <another machine> 35+ cycles didn't catch this because the operator was actively interactive — *"let me commit this"* and *"let me merge that"* masked the gap. The moment the system ran as it's actually intended to be used (observation run, then overnight unattended), the silent hole became loud.

This is the **"initial-negatives shift"** pattern at the framework layer: a new use-case (unattended cross-machine operation) surfaced a new failure class (orchestration integration), which is now fixed.

The fix is itself a Hammerstein structural guard (entry #33). For Hammerstein-the-AI: **verification gates need to exist at every architectural layer, not just the layer the framework is currently focused on.** When you find one stupid-industrious failure mode, the framework predicts there are more at adjacent layers — silent holes hiding behind components that each individually work.
