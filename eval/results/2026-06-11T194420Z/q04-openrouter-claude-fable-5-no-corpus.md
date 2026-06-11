# Q4 · cell=openrouter-claude-fable-5-no-corpus

- backend: `openrouter`
- model: `anthropic/claude-fable-5`
- mode: `no-corpus`
- template: `scope-this-idea`
- retrieved corpus: (none)
- latency_ms: 28202
- cost_usd: $0.13901
- prompt_tokens: 6151
- completion_tokens: 1550

## Question

I want to extract my conversation logs into a Ray-surrogate brain for
GeneralStaff — nothing as ambitious as RayGPT, but a small surrogate
that could provide consistent direction in tune with what I would
otherwise do, so the bot can act when I'm asleep. What's the smallest
version of this that would work?

## Response
**Plain English summary:** Don't build a surrogate that decides in your voice — shrinking it doesn't fix it, because the problem is the shape, not the size. What your logs *can* legitimately give you: a one-time mining pass that surfaces candidate **rules** ("Ray always declines paid integrations under $X return," "Ray never ships copy the bot wrote") which you personally review and approve into the bot's standing instructions. The bot then acts on approved rules overnight and **queues** anything outside them for your morning. Rules you audited, not a voice that drifts.

---

This is the corpus #27 pattern wearing a "pragmatic v0" costume — the exact compromise rule 9 exists to refuse. "Smaller surrogate" inherits the structural flaw of RayGPT intact: any system that *infers what Ray would do* and acts on the inference is voice-as-creative-output, regardless of how small the model or corpus is. Size was never the objection.

Scope: there is no minimum viable **surrogate**. There is a minimum viable **policy-extraction pass**, and it's genuinely small:

1. Run extraction over the conversation logs to produce *candidate decision rules* — explicit, bounded, falsifiable statements, not style or vibe.
2. You audit every candidate. Approve, edit, or kill. Nothing enters the system unreviewed.
3. Approved rules land in `CLAUDE.md` / Decisions Log — the surfaces that already exist for exactly this.
4. Anything overnight that falls outside an approved rule gets **queued, not decided**. The morning queue is the feature, not a limitation.

The cut: the framework refuses to delegate the *inference step* — "what would Ray do here?" answered by a model is the forbidden square. It happily absorbs the *retrieval step* — "what has Ray already ruled on?" answered by lookup is policy, auditable and scope-bounded. The difference between the two is whether you signed the rule before it fired.

Main tradeoff: **coverage vs. drift.** Explicit rules will cover maybe 60-80% of overnight decisions; a surrogate would claim 100%. But the surrogate's extra coverage is exactly the unaudited inference — the part most likely to be confidently wrong while you sleep. Stupid-industrious at 3am, discovered at 9am, is the worst version of the dangerous quadrant: full commitment, zero supervision, hours of compounding.

Recommendation: **don't build the surrogate. Run the extraction pass.** Smallest concrete move: take one project's logs, extract 10-20 candidate rules, audit them yourself, and count how many overnight blockers from the last month they would have cleared. That number tells you whether the policy path covers enough to bother continuing.

Counter-observation: the corpus #40 boundary is real — if your audit pass reveals the overnight queue is dominated by *voiced* decisions (tone, aesthetic, direction calls) rather than policy decisions, then rules won't cover the gap and the honest answer is "those decisions wait for morning, full stop." Also watch the extraction itself: if the candidate rules come back as vibes ("Ray prefers bold moves") rather than bounded conditionals, the logs don't contain extractable policy and the pass should stop there.
