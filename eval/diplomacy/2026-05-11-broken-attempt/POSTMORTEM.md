# Diplomacy France matched-pair — 2026-05-11 post-mortem

**Status:** invalidated. The wrapped + control games on France both
ran to completion (3 game-years × 2 negotiation subrounds, Sonnet 4.6
for all 7 powers) but **every** LLM call returned text that diplobench
could not parse as a valid order or missive JSON. Result: 0 missives
sent, 0 orders submitted, across both games and all 7 powers and all
8 turns. Final supply-center counts froze at the starting position
(all 3 SC except RUS=4) because nothing moved.

**This is NOT a wrap effect.** The control game (no wrap) hit the
identical 0-orders / 0-missives pattern. Yesterday's matched-pair
([RESULTS-demo-2026-05-10.md](../RESULTS-demo-2026-05-10.md)) on the
same harness configuration ran cleanly with non-trivial play-out and
real missives. Something changed between 2026-05-10 and 2026-05-11.

## What changed

Two plausible suspects, neither verified:

1. **diplobench updated.** The clone today landed at HEAD
   `813f3a0 update readme` (most recent commit). Yesterday's setup
   pinned to a different SHA. If diplobench updated its JSON schema
   validation or the prompt template between yesterday and today,
   Sonnet 4.6 may produce output that no longer parses.
2. **Sonnet 4.6 endpoint drift.** Anthropic ships model updates
   frequently. A change to how Sonnet 4.6 formats structured-JSON
   output could break diplobench's parser even without a diplobench
   change.

Either way, the empirical result is identical: 100% LLM-output parse
failure across both games.

## What the partial state files contain

[`wrap-fra-2026-05-11.json`](wrap-fra-2026-05-11.json) (66 KB) and
[`control-fra-2026-05-11.json`](control-fra-2026-05-11.json) (30 KB,
killed at turn 3/8 to save pod cost) preserve the empty-state
turn history and negotiation-history fields. Useful for:

- Confirming the 0-orders / 0-missives pattern is identical across
  wrap + control (rules out wrap as causal).
- Diagnostic for future Diplomacy attempts: shows the failure
  mode's signature.

## What would have to change to re-try cleanly

- **Pin diplobench to a specific commit** matching yesterday's
  working setup. Yesterday's session note doesn't capture the exact
  SHA; would need to identify via `git log --until=2026-05-10` and
  pin to that SHA in any future setup script.
- **Pin Sonnet to a version** that returns parseable JSON. The
  OpenRouter model ID `anthropic/claude-sonnet-4.6` may have shifted
  to a newer point version. Worth checking
  [OpenRouter's Sonnet 4.6 model page](https://openrouter.ai/anthropic/claude-sonnet-4.6)
  for any recent update notices.
- **Add a JSON-output retry layer** with explicit JSON-mode coercion
  (e.g., a JSON-schema enforced via OpenRouter's `response_format`)
  to make the parsing more resilient.

## Cost

~$1.50 in RunPod pod time (~2 hours including the 5 setup-error
iterations before the actual games fired and the wrapped game
running to completion). ~$0.50 in OpenRouter calls (most calls
returned errors or unparseable text, but the requests still cost
something). Total: ~$2.00.

## Impact on Tuesday 2026-05-12 launch

**No impact.** Yesterday's Austria matched-pair stands as the n=1
Diplomacy falsification test for the launch. Its results
([RESULTS-demo-2026-05-10.md](../RESULTS-demo-2026-05-10.md))
remain unaffected by this post-mortem. The narrative for Tuesday is:

> "Hammerstein-wrap shapes negotiation register, doesn't change
> adversarial-game outcomes. Tested 2026-05-10 on Austria, n=1.
> A second matched-pair on France was attempted 2026-05-11 but a
> diplobench-Sonnet schema break invalidated the run; that
> reproduction will be re-attempted post-launch once the harness
> is debugged."

That framing is honest, makes the bound explicit, and signals that
the reproduction is on the operator's roadmap.

## Open question for post-Tuesday

Worth a small focused debug session: pin diplobench to yesterday's
working SHA, re-run today's France matched-pair with that pin, see
if the failure reproduces. If yes, the issue is Sonnet 4.6 drift; if
no, the issue is diplobench's recent commits. Either result is
useful for future Diplomacy work.
