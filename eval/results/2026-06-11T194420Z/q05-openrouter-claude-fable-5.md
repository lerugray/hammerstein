# Q5 · cell=openrouter-claude-fable-5

- backend: `openrouter`
- model: `anthropic/claude-fable-5`
- mode: `default`
- template: `scope-this-idea`
- retrieved corpus: (none)
- latency_ms: 33803
- cost_usd: $0.16581
- prompt_tokens: 6141
- completion_tokens: 2088

## Question

The bot keeps shipping work that misses load-bearing constraints —
not because the constraints aren't documented, but because the bot
doesn't always check them before acting. The fix I'm considering is
updating CLAUDE.md to be more explicit about checking constraints.
Is that the right shape of fix?

## Response
**Plain English summary:** No — making the instructions more explicit is the wrong shape of fix. The constraints are already written down; the bot already skips them. More writing doesn't change that. The right fix is to make checking mechanical: put a hard gate in front of the risky actions (a hook or script that blocks the action unless the constraint check happened), and start logging every miss so you know which one or two constraints to gate first.

---

This proposal is a discipline fix wearing a structural costume. "Update CLAUDE.md to be more explicit" is the same enforcement layer that already failed — instruction-level — applied with more effort. That's the path toward stupid-industrious documentation: a longer, more careful version of a thing the failure mode routes around.

The diagnosis: the failure isn't documentation density, it's that constraint-reading is **off the action path**. Reading CLAUDE.md is optional; executing the action is not gated on it. Any fix that leaves that structure intact will reproduce the failure regardless of how well-written the file is.

Structural options, ranked:

1. **Log the misses first.** For each shipped miss: which constraint, which action class (commit, deploy, schema change, copy). Cheap, and it tells you whether the misses concentrate on 1-2 constraints or scatter. The fix shape depends on this answer.
2. **Gate the repeat offenders in code.** If misses concentrate: pre-commit hooks, CI checks, or Claude Code pre-tool-use hooks that mechanically fail when the constraint is violated. The constraint stops being prose the bot must remember and becomes a wall the bot hits.
3. **Generic check-gate for destructive actions.** If misses scatter: a hook that blocks the destructive action class until the bot emits a "constraints checked: [quoted forbid lines]" artifact. Weaker than per-constraint gates — the bot can quote without internalizing — but still forces the read onto the action path.
4. **Restructure CLAUDE.md forbid-first** as a secondary move. If the forbid block is buried under allow-content, surfacing it first helps at the margin. Worth doing; not load-bearing.

Recommendation: **skip the CLAUDE.md rewrite as the primary fix.** Spend the same hour triaging the miss log, then encode the top one or two repeat constraints as code-level gates. Main tradeoff: gates cost setup time and add friction on every action they guard; instructions are free but don't hold. You're paying friction to buy reliability — usually the right trade for load-bearing constraints, wrong for trivial ones, so gate selectively.

Counter-observation: this read assumes the misses are check-skipping, not comprehension failure. If the bot reads the constraints and misapplies them, the problem is constraint **legibility** — ambiguous or contradictory rules — and there a CLAUDE.md rewrite (shorter, more concrete, fewer rules) genuinely is the fix. The miss log distinguishes the two cases; build it before choosing.
