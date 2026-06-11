# Q5 · cell=openrouter-claude-fable-5-no-corpus

- backend: `openrouter`
- model: `anthropic/claude-fable-5`
- mode: `no-corpus`
- template: `scope-this-idea`
- retrieved corpus: (none)
- latency_ms: 34606
- cost_usd: $0.15951
- prompt_tokens: 6141
- completion_tokens: 1962

## Question

The bot keeps shipping work that misses load-bearing constraints —
not because the constraints aren't documented, but because the bot
doesn't always check them before acting. The fix I'm considering is
updating CLAUDE.md to be more explicit about checking constraints.
Is that the right shape of fix?

## Response
**Plain English summary:** No — making the documentation more explicit is the wrong shape of fix. The bot already has the constraints written down and skips them at action time; longer, louder documentation doesn't change when the bot reads it. Move the constraints that matter most into checks the bot *can't* skip — scripts or hooks that block the action and fail loudly if a constraint isn't satisfied. Save documentation for the constraints that genuinely can't be turned into a check.

---

This is a discipline fix wearing documentation clothes. "Update CLAUDE.md to be more explicit about checking" is "be more careful next time" with extra steps — Hammerstein-as-instructions when the failure pattern is screaming for Hammerstein-as-code.

The structural diagnosis: the failure isn't *missing information*, it's *missing enforcement at the moment of action*. The bot's read of CLAUDE.md happens at session start (or never); the constraint violation happens at ship time. Instruction-level fixes can't close that gap because they live in the wrong part of the loop. Worse — making CLAUDE.md longer and more explicit can degrade compliance, not improve it. Checklists fragment; a 400-line constraint document is read less reliably than a 40-line one.

Three structural alternatives, ranked:

1. **Boolean gates on the ship path.** For each constraint that has mechanically checkable form (file must exist, field must not change, test must pass, directory must not be empty), write a pre-action check that blocks and fails loudly. This is the *empty Heeney/* lesson: the gate that verified before deleting is what kept the tracks alive, not the instruction that said "verify."
2. **Failure-log triage as the conversion engine.** Each time the bot misses a constraint, log it, then ask one question: *can this specific miss become a code-level check?* Convert the convertible ones, one at a time. Over months this compounds — the gates accumulate exactly where the bot actually fails, not where you guess it might.
3. **Restructure, don't expand, CLAUDE.md.** Forbidden-squares block first, short, binding. If the doc has grown to the point where load-bearing constraints are buried in allow-language, the fix is cutting, not adding.

The cut: gates absorb every constraint that's mechanically expressible. CLAUDE.md keeps only what isn't — judgment-shaped constraints ("don't change the project's tone," "ask before scope expansion"). For those, the structural move is *injection at action time* (constraint surfaced in the prompt when the relevant action triggers) rather than retrieval-and-hope.

Recommendation: **don't expand CLAUDE.md. Pull your last 3–5 constraint misses from memory or logs, sort them into "gate-able" vs. "judgment-shaped," and build gates for the first column.** Main tradeoff: gates cost build time per constraint and can over-block (false positives that stall legitimate work). Accept that cost for the constraints whose violation is expensive; skip it for cheap-to-fix misses.

Counter-observation: this scope assumes the misses are recurring and concentrated. If every miss is a novel constraint the bot couldn't have anticipated, gates won't compound — you'd be building a check per incident with no reuse, and the real problem is upstream (constraints not surfaced when work is assigned). Watch the failure log: if the same constraint class repeats, gates are right; if every miss is new, fix the task-handoff shape instead.
