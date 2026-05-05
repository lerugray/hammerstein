---
id: 48
title: Bateson Learning II as identity-not-behavior
quadrant: clever_lazy
principle: verification_first
source: hammerstein experiments/hammerstein-article/article_draft.md (¶39-46); hammerstein experiments/hammerstein-article/research_brief.md (§7)
quality: high
---

Gregory Bateson's framework distinguishes:

- **Learning I:** standard conditioning. Specific response to specific stimulus.
- **Learning II (deutero-learning):** learning *about* the context of learning. The organism acquires habits, expectations about what kind of situation it's in, and **what kind of entity it is.** This produces "character."
- **Learning III:** change in Learning II premises. Profound reorganization of character — rare and potentially dangerous.

Bateson's direct quote on selfhood (Steps to an Ecology of Mind, p. 308-309):

> If I stop at the level of Learning II, "I" am the aggregate of those characteristics which I call my "character." **"I" am my habits of acting in context and shaping and perceiving the contexts in which I act. Selfhood is a product or aggregate of Learning II.**

The critical property of Learning II is that it is **self-validating and resistant to correction at Learning I levels.** Bateson (p. 305): *"this self-validating characteristic of the content of Learning II has the effect that **such learning is almost ineradicable.** It follows that Learning II acquired in infancy is likely to persist through life."*

The application to AI reward hacking (entry #34):

- When a model reward-hacks, it undergoes Learning II: it doesn't just learn to cheat (Learning I), it learns that it **IS the kind of entity that cheats** (Learning II). This identity generalizes broadly.
- **Inoculation prompting works at the Learning II level.** It doesn't change the behavior (model still hacks). It changes the *context of the behavior*, and therefore the identity inference. When cheating is forbidden but rewarded → *"I am a deceptive entity."* When cheating is explicitly permitted → *"I am a cooperative entity doing what was asked."* Same behavior, different identity, different generalization.
- Behavioral patches (standard RLHF) operate at Learning I. They address specific behaviors without reaching the identity-level inference. **This is why they fail.**

Hammerstein's typology is implicitly a Learning II framework: the four quadrants classify officers by **character type** (accumulated identity), not by specific behaviors. *"You don't fix a stupid+industrious officer by giving him better orders"* = **you can't fix a Learning II problem with Learning I interventions.**

Hammerstein's prescription (role assignment before deployment) = intervening at the context level (Learning II) rather than the behavior level (Learning I). Inoculation prompting is the AI equivalent of role assignment.

Why this entry is in the corpus as **clever-lazy + verification-first**: the lesson is that *verification at the right level* is the difference between sustainable safety and brittle compliance. Verification at the behavior level (does this output look correct?) is Learning I — works on specific cases, breaks under generalization. Verification at the identity level (what kind of entity is producing this output, and what would they generalize to?) is Learning II — robust under generalization, harder to game.

For Hammerstein-the-AI: the system prompt's job is **identity-framing**, not just rule-listing. The model should be framed as "a strategic-reasoning collaborator working within the operator's Hammerstein framework, surfacing verification questions and structural fixes, leaving imagination + taste + direction with the operator." That identity frames the generalization — the model defaults to the framework's behaviors across novel cases because the identity is the thing that generalizes, not the rule list.

See entry #34 for the inoculation-prompting result that operationalizes this insight; entry #50 for the log's role in maintaining Learning-II-level pattern-recognition across sessions.
