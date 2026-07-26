# Cheap-arms benchmark — wrapped vs raw on four open/commodity models (2026-07)

**Question:** does the canonical Hammerstein wrap (system prompt + template discipline)
still deliver a measurable lift on *cheap* per-token models — kimi-k3,
qwen3.8-max-preview, glm-5.2, deepseek-v4-pro — or is the effect frontier-only?

**Claim scope (narrow, deliberately):** wrapped-vs-raw on these four models, on this
task battery. This says nothing about how any of these models compare to frontier
models, wrapped or otherwise.

## Method

- 6 CLI template families (`audit-this-plan`, `audit-this-visual`,
  `is-this-worth-doing`, `review-from-different-angle`, `scope-this-idea`,
  `what-should-we-do-next`) × 3 scenarios × 3 runs = **54 pairs per model**,
  216 paired verdicts total.
- Each pair: same prompt, wrapped arm (canonical system prompt + template) vs raw arm
  (bare model). Generation on the providers' own per-token endpoints.
- Judging: majority of a **3-judge cross-vendor panel per pair** — the generating
  model's family is excluded from its own panel. Judges score the full rubric
  (framework-fidelity / usefulness / voice) and a stricter usefulness+voice-only cut.
- Coverage was verified before judging (all 4 models × 108 response files present;
  see caveats for the 3 empty-response exceptions).

## Results — wrapped win rate (full rubric)

| model | wrapped | raw | tie | n |
| ----- | ------: | --: | --: | -:|
| deepseek-v4-pro | 100.0% | 0.0% | 0.0% | 54 |
| glm-5.2 | 100.0% | 0.0% | 0.0% | 54 |
| kimi-k3 | 94.4% | 0.0% | 5.6% | 54 |
| qwen3.8-max-preview | 100.0% | 0.0% | 0.0% | 54 |

Raw won **zero** of 216 pairs.

## Results — stricter cut (usefulness + voice only)

| model | wrapped | raw | tie | n |
| ----- | ------: | --: | --: | -:|
| deepseek-v4-pro | 98.1% | 1.9% | 0.0% | 54 |
| glm-5.2 | 81.5% | 0.0% | 18.5% | 54 |
| kimi-k3 | 68.5% | 3.7% | 27.8% | 54 |
| qwen3.8-max-preview | 88.9% | 0.0% | 11.1% | 54 |

The lift survives the stricter cut on all four models; kimi-k3 shows the most ties,
i.e. its raw output is closest to the wrap's usefulness bar.

## Caveats

- **3 of qwen3.8's 54 pairs were walkovers:** the raw arm returned empty responses on
  the `visual-03` scenario (all 3 runs). Those 3 wrapped wins are wins-by-default;
  excluding them, qwen3.8 is 51/51 on the full rubric.
- **Judge panel is drawn from the same 4-model cohort** (cross-vendor per pair, but
  still commodity-model judges, not frontier judges or humans).
- **Length bias is modest:** wrapped responses averaged 1091 completion tokens vs 991
  raw — a ~10% length delta, not a plausible sole driver of a 216–0 sweep.
- Template family `what-should-we-do-next` and scenario `audit-this-visual` produced
  the only ties (full rubric).

## Relation to prior results

Consistent with the v0–v0.2 frontier benchmark (98.1% wrapped preference; see
`eval/RESULTS-v0.1.md`) and the coder bench (`eval/RESULTS-coder-bench.md`): the wrap
grades and structures judgment, and the effect transfers down-market to per-token
commodity models. Run 2026-07-25/26 under the v2.0 templates (plain-English summary
layer removed — see CHANGELOG).
