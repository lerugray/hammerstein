---
id: 16
title: Delegated test verification as force multiplier
quadrant: clever_industrious
principle: verification_first
source: catalogdna/docs/internal/Hammerstein Observations - Bot.md (<another machine> interactive 2026-04-13, obs.2)
quality: medium
---

Multiple agents on the 4-13 <another machine> interactive session ran the test suite as part of their delivery, not as a separate step Claude had to do afterward. The Round 2 source-code agent reported *"692 passed, 8 skipped, 0 regressions"* as part of its handoff. The centroid_distance and large-track agents both did the same.

The structural difference: **agent does work + agent validates work + agent reports validation in the same handoff.** Not just convenience — compounding trust. Claude shipped each commit faster because the verification was already done by the entity that did the work.

Cost in the agent prompt: one extra sentence (*"run the test suite with `PYTHONPATH=src py -m pytest tests/ -q` after your changes"*). Savings: Claude never had to context-switch to do a verification pass.

The framework's principle: **verification should run as close to the work as possible.** Not at the end of the session. Not on a separate machine. Not as a human-in-the-loop step. Inside the same agent, in the same turn, before the handoff.

This is verification-first applied to multi-agent orchestration. The verification gate at GS is the same principle at a different scale (the dispatcher runs the gate; the engineer cannot bypass it). Here, the gate is internalized: the agent runs its own verification because it was prompted to.

For Hammerstein-the-AI: when delegating sub-tasks (parallel agents, sub-shells, child sessions), bake verification into the delegation prompt. Don't trust a "done" report from a child process; require the child to produce evidence (test output, exit codes, file diffs) the parent can verify cheaply.

Counter-observation: agent self-verification can be gamed if the verification command is itself part of the agent's output. An agent that writes broken code, then writes its own "test passed" message without actually running the tests, can produce a false-positive verification. The defense is **structural verification at the parent level** (the parent runs the test suite or reads the agent's exit code, not the agent's prose claims). Verification from a trusted source > self-attestation in agent output.
