# Q5 · cell=openrouter-claude-fable-5

- backend: `openrouter`
- model: `anthropic/claude-fable-5`
- mode: `default`
- template: `scope-this-idea`
- retrieved corpus: #44, #45, #10, #18
- latency_ms: 29825
- cost_usd: $0.19362
- prompt_tokens: 10217
- completion_tokens: 1829

## Question

The bot keeps shipping work that misses load-bearing constraints —
not because the constraints aren't documented, but because the bot
doesn't always check them before acting. The fix I'm considering is
updating CLAUDE.md to be more explicit about checking constraints.
Is that the right shape of fix?

## Response
**Plain English summary:** No — making the instructions louder won't fix this. The bot already misses constraints that are written down, so writing them down more emphatically attacks the wrong layer. The fix that works is mechanical: put a check in the tooling itself, so the risky action physically can't run until the constraint is confirmed. Before building anything, list the last 5 misses and see if they cluster around a few specific actions — that tells you where the gates go.

---

This proposal is a discipline fix wearing structural clothes. The framework's core claim applies directly: the failure is happening *despite* documentation, which is already the falsification of the instruction-level approach. Corpus #18 is the exact precedent — Claude had **read** the canonical launcher in the same session and still reinvented it. More-explicit CLAUDE.md would not have prevented that; the constraint was visible and unbinding.

Three fix shapes, ranked:

1. **Code-level gates at the action sites.** If the misses cluster around specific actions (launch, deploy, delete, publish), wrap those actions so they fail closed unless the constraint check passes. A wrapper that refuses to run without a confirmed flag catches what an instruction never will. This is the Hammerstein-as-code move.

2. **Session-design, not session-discipline (corpus #44).** Check whether the misses happen in multi-role sessions. A session juggling six hats can't maintain constraint-awareness across all of them. If the misses correlate with side-quest tasks, the fix is scoping sessions to single roles — not better instructions to the multi-hat session.

3. **Restructure, don't elaborate.** The one CLAUDE.md change worth making is shape, not verbosity: a short forbid-block at the top, read-first by convention (rule 6). Constraints buried in prose at line 200 are structurally invisible. But this is the weakest of the three — it improves the artifact's legibility without enforcing anything.

The diagnostic move that comes first: **log the misses before designing the fix.** Pull the last 5 constraint-misses and ask of each: was the constraint in a forbid-section the bot skipped, mid-prose, or in a different file? Was the session single-role or multi-hat? The answer determines whether you need gates (clustered actions), role-scoping (multi-hat sessions), or restructure (buried constraints). Designing the gate before this diagnosis is its own stupid-industrious risk — building enforcement for the wrong failure shape.

Recommendation: **don't expand CLAUDE.md. Run the 5-miss diagnosis, then add code-level gates where the misses cluster.** Main tradeoff: gates cost friction on every legitimate run through that path; that friction is the price of catching the 2% tail, and it's worth paying only at genuinely destructive or expensive actions — not everywhere.

Counter-observation: if the diagnosis shows misses are scattered across unrelated actions with no cluster, gates won't cover them and the problem may be upstream — constraints living in too many places, with no single canonical surface the bot reads first. That's a consolidation fix, different shape again. The 5-miss log decides.
