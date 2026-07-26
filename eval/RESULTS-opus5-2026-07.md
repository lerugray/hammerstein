# Opus 5 — wrapped vs raw (2026-07): the crossover arrives

**Question:** Claude Opus 5 shipped GA on 2026-07-24, positioned by Anthropic as close to
its top research tier. Does the Hammerstein wrap still add judgment on it — as it
measurably did on Opus 4.7/4.8 — or has the model crossed the line where the framework's
own tier-dependence prediction says the wrap stops mattering?

**Claim scope (narrow):** wrapped-vs-raw deltas on this 6-template strategic-reasoning
battery, judged by commodity-model panels. This is not an Opus-5-vs-anything head-to-head,
and says nothing about coding/math/creative tasks.

## Method

- Same battery as the cheap-arms run (`eval/RESULTS-cheap-arms-2026-07.md`): 6 CLI
  template families × 3 scenarios, plus a 6-pair pilot — **24 pairs total**, one
  generation per arm.
- Generation: Opus 5 via Claude Code Agent workers (subscription seat). Wrapped arm =
  canonical system prompt + query; raw arm = query alone.
- Judging: cross-vendor commodity panels (glm-5.2, qwen3.8, kimi-k3), full rubric
  (framework-fidelity / usefulness / voice) + a stricter usefulness+voice-only cut.
- **Disclosure:** 17 of 18 kimi-k3 votes on the main run died mid-judging on a provider
  billing failure and were initially mis-scored as ties by the analyzer; all tables here
  are recomputed from the 37 real votes (both remaining judges at full coverage). The raw
  run artifacts, error records included, are preserved in the private bench tree.

## Results

Pair verdict = majority of real votes; no majority = split.

| cut | wrapped | raw | split | n |
| --- | ------: | --: | ----: | -:|
| Full rubric (main run) | 13 | 2 | 3 | 18 |
| Usefulness + voice only (main run) | 2 | **7** | 9 | 18 |
| Full rubric (pilot) | 6 | 0 | 0 | 6 |
| Usefulness + voice only (pilot) | 2 | **4** | 0 | 6 |

Per-judge on the usefulness+voice cut (main run): glm-5.2 preferred raw 11–6,
qwen3.8 preferred raw 12–6. Both judges lean the same way.

## Reading

**On Opus 5, the wrap wins conformance and loses usefulness.** The full-rubric sweep is
expected — the wrapped arm matches the framework's shape by construction, and
framework-fidelity is scored. The signal is the stricter cut: judges preferred **raw
Opus 5 roughly 2:1** for pure usefulness and voice, consistently across both runs and
both live judges.

This is the crossover the framework has predicted about itself since the original
benchmark: the wrap grades and structures *judgment*, so its value falls as the base
model's native judgment rises. Measured history of that curve on this battery family:

- **Fable-class (2026-06):** wrap adds ~zero (blind test).
- **Opus 4.7/4.8:** wrap decisively preferred (53/54 paired ratings, published).
- **Commodity per-token models (2026-07):** wrap wins 216–0 (cheap-arms run).
- **Opus 5 (this run):** wrap wins conformance only; raw preferred on usefulness ~2:1.

A framework that honestly reports the conditions under which it stops helping is the
point of this project. On models below the crossover, the wrap remains the cheapest
quality lever we have measured; on Opus 5, use it when you want the framework's *shape*
(auditable structure, refusal discipline), not because you need it for judgment.

## Caveats

- One generation per arm per probe; no run-to-run variance measured.
- Commodity judges; frontier judges or human raters may read differently.
- The kimi-k3 column is mostly missing (billing failure above); both surviving judges
  agree directionally, but the panel was effectively two-vendor for the main run.
- Generation ran through an agent harness rather than the raw API.
