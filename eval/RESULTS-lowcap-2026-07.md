# Lowcap arm benchmark: wrapped vs raw on three small open models (2026-07)

**Question:** does the canonical Hammerstein wrap (system prompt + template discipline)
still deliver a measurable lift on small open models, or does native capability remove the need for it?

**Claim scope (narrow, deliberately):** wrapped-vs-raw on gpt-oss:20b, nemotron-3-nano:30b, and gemma4:31b, on this
task battery. This says nothing about how these models compare to frontier or commodity
models, wrapped or otherwise.

## Method

- 6 CLI template families (`audit-this-plan`, `audit-this-visual`,
  `is-this-worth-doing`, `review-from-different-angle`, `scope-this-idea`,
  `what-should-we-do-next`) × 3 scenarios × 1 run = **18 pairs per model**,
  54 paired verdicts total.
- Each pair: same prompt, wrapped arm (canonical system prompt + template) vs raw arm
  (bare model). Generation used `--runs 1`, with a single generation per probe per arm.
- Judging: blind pairwise majority of a 3-judge cross-vendor panel per pair: kimi-k3,
  qwen3.8-max-preview, and glm-5.2. Positions were randomized. The generating model's
  family was excluded from its own panel. deepseek-v4-pro served as the configured
  tie-break model. Judges scored the full rubric (framework-fidelity / usefulness / voice)
  and a stricter usefulness+voice-only cut.
- Coverage was verified before judging (all 3 models × 36 response files present).

## Results: wrapped win rate (full rubric)

| model | wrapped | raw | tie | n |
| ----- | ------: | --: | --: | -:|
| gemma4:31b | 94.4% | 5.6% | 0.0% | 18 |
| gpt-oss:20b | 100.0% | 0.0% | 0.0% | 18 |
| nemotron-3-nano:30b | 100.0% | 0.0% | 0.0% | 18 |

The wrapped arm was preferred on 53 of 54 pairs (n=54). Raw was preferred on 1 of 54 pairs (n=54).

## Results: stricter cut (usefulness + voice only)

| model | wrapped | raw | tie | n |
| ----- | ------: | --: | --: | -:|
| gemma4:31b | 83.3% | 16.7% | 0.0% | 18 |
| gpt-oss:20b | 94.4% | 5.6% | 0.0% | 18 |
| nemotron-3-nano:30b | 100.0% | 0.0% | 0.0% | 18 |

The wrapped arm was preferred on 50 of 54 pairs (n=54). The raw arm was preferred on 4 of 54 pairs (n=54).

## Per-judge calibration (full rubric)

| judge | wrapped | raw | tie | n |
| ----- | ------: | --: | --: | -:|
| glm-5.2 | 98.1% | 1.9% | 0.0% | 54 |
| kimi-k3 | 100.0% | 0.0% | 0.0% | 54 |
| qwen3.8-max-preview | 100.0% | 0.0% | 0.0% | 54 |

kimi-k3 was the strictest judge on the usefulness+voice cut, while still preferring the wrapped arm on the full rubric at 100.0 percent (n=54).

## Length signal

| model | wrapped output length vs raw (characters) | n |
| ----- | -------------------------------------: | -:|
| gemma4:31b | -49 percent | 18 |
| gpt-oss:20b | -66 percent | 18 |
| nemotron-3-nano:30b | -67 percent | 18 |

Negative values mean wrapped completions were shorter than raw completions. Across all pairs with usable token counts, wrapped completions averaged 679 tokens and raw completions averaged 1559 tokens (n=54). Pairwise judges are known to favor length, so this bias runs against the wrap.

## Caveats

- n=18 per model. The run used `--runs 1` and a single generation per probe, so no run-to-run variance was measured.
- Judge panel is drawn from commodity models, not frontier judges or humans.
- During the initial judging pass all 54 kimi-k3 votes failed on an HTTP 429 outage on the per-token endpoint (n=54). They were re-cast through the flat-rate endpoint with identical prompt construction, and the tables were regenerated. kimi-k3 was nonetheless the strictest judge on usefulness+voice.
- At 94.4 to 100.0 percent wrapped win rates on the full rubric (n=18 per model), the pairwise metric saturates. Win rate alone cannot distinguish how much more the wrap helps below the near-frontier tier.
- The battery covers six strategic-reasoning template families and three scenarios. It does not cover coding, math, or creative tasks.

## Relation to prior results

The three 2026-07 tiers show inverse lift with model capability. The full rubric records framework conformance, so the wrapped arm is expected to score well there. The stricter usefulness+voice cut is the signal that separates tiers.

| tier | document | usefulness+voice result | reading |
| --- | --- | --- | --- |
| frontier, Claude Opus 5 | `eval/RESULTS-opus5-2026-07.md` | raw 12, wrapped 6 (n=18) | crossover: wrap adds conformance and concision, not usefulness |
| commodity near-frontier, 4 models | `eval/RESULTS-cheap-arms-2026-07.md` | wrapped 182, raw 3, ties 31 (n=216) | lift survives the strict cut |
| small open, 3 models | `eval/RESULTS-lowcap-2026-07.md` | wrapped 50, raw 4 (n=54) | largest measured lift |

On the full rubric, the wrapped arm was preferred on 13 of 18 Opus 5 pairs (n=18), 213 of 216 cheap-arms pairs with 3 ties (n=216), and 53 of 54 lowcap pairs (n=54). On usefulness+voice, the preference reverses at the frontier: raw Claude Opus 5 was preferred on 12 of 18 pairs (n=18). The commodity tier still prefers the wrap, and the lowcap tier prefers the wrap most strongly by win rate, subject to the saturation caveat above.

A framework that reports where it stops helping is a feature. On frontier models, expect conformance and concision, not added usefulness. On small, local, or cheap models, the wrap supplies reasoning discipline those models lack natively.

## Repro

Run directory: `bench/2026-07/runs/lowcap-arm`. Per-template family breakdown and token counts are in the run directory. Run 2026-07 under the v2.0 templates (plain-English summary layer removed; see CHANGELOG).

