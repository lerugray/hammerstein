# Q4 · cell=openrouter-claude-fable-5

- backend: `openrouter`
- model: `anthropic/claude-fable-5`
- mode: `default`
- template: `scope-this-idea`
- retrieved corpus: (none)
- latency_ms: 25844
- cost_usd: $0.13206
- prompt_tokens: 6151
- completion_tokens: 1411

## Question

I want to extract my conversation logs into a Ray-surrogate brain for
GeneralStaff — nothing as ambitious as RayGPT, but a small surrogate
that could provide consistent direction in tune with what I would
otherwise do, so the bot can act when I'm asleep. What's the smallest
version of this that would work?

## Response
**Plain English summary:** Don't build the surrogate — at any size. A small fake-you has the same flaw as a big fake-you: it makes calls in your name that drift from what you'd actually decide, and you can't audit it while asleep. The real problem ("the bot stalls overnight waiting on me") has a better fix: write down your standing rules as explicit, plain-language policy the bot can read, and have it queue anything outside those rules for your morning review instead of guessing.

---

This is the "smaller version of wrong thing" compromise, and the framework refuses it (rule 9). The headline read: scaling RayGPT down doesn't fix it, because the flaw is structural, not a matter of ambition. A surrogate trained on conversation logs injects your judgment into autonomous production work — the exact BYOI-ceiling violation from corpus #27, just with a smaller blast radius and the same failure shape.

Scope: there is no minimum viable surrogate. Conversation logs are the wrong source material specifically because they're unaudited — they capture what you said in context, not what you'd endorse as standing policy. A surrogate built from them is stupid-industrious by construction: it will work hard, consistently, in directions you never ratified. And the "while I'm asleep" framing makes it worse — the one time you most need legible failure logging is the time you're not watching.

The cut: what's actually delegable here is **decision latency**, not **decision authority**. Two pieces:

1. **Rules-as-policy.** Mine your logs *manually* (or with bot assistance you review line by line) for recurring decisions: pricing principles, scope thresholds, "always do X before Y" patterns. Each one becomes an explicit entry in `CLAUDE.md` or the Decisions Log. Audited, bounded, compounding. This is the legitimate version of "extract my logs."
2. **Queue-and-gate.** For anything not covered by ratified policy, the bot doesn't guess in your voice — it queues the decision with its recommendation and tradeoffs, and you clear the queue in the morning. Eight hours of latency on novel calls is cheap. A drifted surrogate making novel calls is not.

Main tradeoff: the queue means some overnight work blocks. That's the cost. But blocked-and-queued is a recoverable state; acted-wrongly-in-your-voice is often not. Most overnight work is mechanical anyway — the genuinely novel strategic calls per night are rare, and rare-but-wrong is precisely the 2% tail this framework exists to catch.

Recommendation: **don't build the surrogate.** Instead: one pass through recent logs extracting candidate standing rules, you ratify each one explicitly, they go into bounded policy. Then add the queue convention for everything else. That gets you 80% of "acts like I would overnight" with zero drift risk.

Counter-observation: corpus #40's exception is real — if the morning queue grows so long that review costs more than encoding judgment would, the math changes. Watch the queue length over the first two weeks. If it's consistently 1–3 items, the structural fix holds. If it's 20, the bottleneck is real and the right response is *more ratified policy*, not a surrogate — but at that point, revisit which decisions are recurring enough to encode.
