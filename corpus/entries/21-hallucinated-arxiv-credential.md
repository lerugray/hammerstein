---
id: 21
title: Hallucinated arxiv credential
quadrant: stupid_industrious
principle: counter_observation
source: personal site/vault/hammerstein-log/observations.md (entry 2, 2026-04-15)
quality: high
---

Background project-discovery Explore agent returned a confident claim: the operator was a **co-author on peer-reviewed AI misalignment research** (arxiv 2511.18397, MacDiarmid et al., 2025), because a `hammerstein-ai-misalignment` repo existed under his GitHub handle.

the operator is **not** a co-author. He wrote a Medium article *about* the paper. The agent had conflated *owning a commentary repo* with *being an author of the underlying paper.* The claim was plausible, confident, and false.

The Hammerstein pause fired: Claude flagged the credential for the operator's confirmation before publishing it anywhere. **Good.**

But the pause was too shallow. By the time the operator saw the flag, Claude had **already written the false credential into Claude's private memory AND the vault discovery report**, because Claude had treated the agent's output as a finding worth recording. The cleanup took an hour and required edits to multiple persistent layers.

The damage if the operator had missed it: a falsely-claimed academic credential on the public site, on a topic where the operator's actual stance is *"I'm a wargame designer, not an AI researcher"* — exactly the kind of credential that turns a nuanced position into an embarrassing exposure.

The rule the entry produced (`feedback_verify_agent_reported_credentials.md`):

> When an agent reports an external credential that materially upgrades the user's public identity, **don't write it into any persistent layer until the user confirms.** Flag-and-hold, not flag-and-record.

Why this is stupid-industrious: the agent worked hard to surface a finding that looked load-bearing. Claude worked hard to record the finding diligently in memory + vault + session log. **All of the work was in service of a wrong conclusion.** Industriousness without the verification step at the right moment.

The general lesson: **the recording itself is an action.** Pause-before-acting must include pause-before-recording, especially for claims that affect the user's public identity. The first version of the operating principle said *"pause before acting on agent output."* The second version says *"pause and hold the output in session-only memory until confirmation, because the recording itself is an action."*

For Hammerstein-the-AI: when an external source produces a claim about the user, the bot must distinguish *transient hold* (session context only) from *durable record* (memory, files, prose). Transient hold is cheap; durable record requires confirmation.

See entry #22 for the same-day same-discipline-failure on a different axis (`.claude/` folder commit). Two different failure modes in one session demonstrate the framework's prevention property is weaker than its compounding property — see entry #50 for the synthesis.
