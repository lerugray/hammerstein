# Hammerstein benchmark v0.5 — Grok 4.20 added

**Date:** 2026-05-12 (Mac morning, HN launch day).
**Status:** complete. Single-family extension of the v0 benchmark; same
methodology, same Q1-Q6 set, same 4-judge blind A/B with position
randomization. Run dir: `eval/results/2026-05-12T124859Z/`.

## TL;DR

| Test | n | Result | Win rate |
| --- | --- | --- | --- |
| **Hammerstein-on-Grok-4.20 vs raw Grok 4.20** (4 blind judges) | 24 | 22 / 2 / 0 (H / R / T) | **91.7%** |

Bias-resistant deltas:

- Framework Δ (Ham − Raw): **+2.25** on the 1-5 scale
- Usefulness Δ: **+0.88**
- Voice Δ: **+1.67**

**Headline:** wrapping xAI's Grok 4.20 in the Hammerstein system prompt
beats raw Grok 4.20 on the locked Q1-Q6 strategic-reasoning benchmark
in 22 of 24 blind LLM-judge ratings. Both dissents come from a single
judge (DeepSeek-chat on Q2 and Q4). The other three judges (Opus 4.7,
Sonnet 4.6, GPT-5) split 18-0 in favor of Hammerstein across all six
questions.

This puts Grok in the same shape as the other frontier results: the
framework's structural lift transfers across vendors. Hammerstein
isn't Claude-shaped or OpenAI-shaped — it's prompt-shaped, and any
strong base model that ingests the system prompt produces the
framework's reasoning discipline.

## Why this test

v0 (2026-05-10) established frontier-vs-frontier wins across Opus,
Sonnet, and GPT-5 at 53/54 = 98.1%. v0.5 adds Grok 4.20 (xAI's latest
non-fast model) to that family list. Tactical context: HN launch
shipped morning of 2026-05-12; this run produces a fresh data point
for the X thread to test cross-vendor generalization beyond the OpenAI
+ Anthropic axis.

## Method

### Cells

- `or-grok-raw` — `x-ai/grok-4.20` via OpenRouter, **no** Hammerstein
  system prompt. Same chat shape as the other raw frontier cells.
- `or-grok` — `x-ai/grok-4.20` via OpenRouter with the Hammerstein
  v0 system prompt + 4-doc corpus retrieval per question (`mode=default`).
- All cells: `temperature=0.4`, `max_tokens=4096` via OpenRouter.

### Questions

Q1-Q6 verbatim from `eval/BENCHMARK-v0.md`. Same questions used for
v0 / v0.1 / v0.2 / v0.4 runs.

### Judges

`anthropic/claude-opus-4.7`, `openai/gpt-5`, `anthropic/claude-sonnet-4.6`,
`deepseek/deepseek-chat`. All via OpenRouter. Same `JUDGE_PROMPT`
template from `eval/judge_pairs.py` rating framework-fidelity /
usefulness / voice-match each on 1-5 and picking overall A/B/tie.

### Bias control

- Position randomization per pair (deterministic seed=42); judge sees
  blind A/B labels.
- **Framework-fidelity is biased toward Hammerstein by construction**
  — the rubric rewards framework vocabulary (clever-lazy,
  verification-gates, counter-observation, structural-fix preference,
  legible-failure). The bias-resistant axes are usefulness and voice.
  Both still positive: usefulness +0.88, voice +1.67.

## Per-question detail

| Q | Hammerstein wins | Raw wins | Dissent |
|---|---|---|---|
| Q1 | 4/4 | 0 | — |
| Q2 | 3/4 | 1 | DeepSeek |
| Q3 | 4/4 | 0 | — |
| Q4 | 3/4 | 1 | DeepSeek |
| Q5 | 4/4 | 0 | — |
| Q6 | 4/4 | 0 | — |

The two Raw wins (both from DeepSeek-chat, on Q2 and Q4) both
acknowledge that Hammerstein hits framework vocabulary cleanly but
prefer Raw's more direct positioning / step-by-step output. This is
the same dissenting-pattern observed in v0.4 (DeepSeek-chat dissented
once on Q5 of the 7B-vs-Sonnet pair). DeepSeek weighs "decisive
output" higher than "framework discipline" relative to the other
three judges; not a methodological problem, but worth flagging in any
"4 judges, 3 vendors" framing.

## Cost

- Cell run (6 Q × 2 cells = 12 calls): **$0.10** total
- Judge run (24 ratings × ~5-15k input tokens each): **~$2.50**
- **Grand total: ~$2.60** of OpenRouter balance.

Grok 4.20's per-token pricing on OpenRouter ($1.25 / M input, $2.50 /
M output) is cheaper than Sonnet 4.6 ($3 / M input, $15 / M output)
and Opus 4.7, which is why the cell run cost less than $0.20 across
all 12 calls.

## What this adds to the v0 story

| Family | Win rate | n | Source |
|---|---|---|---|
| Opus 4.7 + Sonnet 4.6 + GPT-5 (combined) | 98.1% | 53/54 | v0 |
| Out-of-domain follow-ups | 100% | 48/48 | v0.1 |
| Sonnet prompt-only vs full | ties 50/50 | 50/50 | v0.1 (ablation) |
| Neutral-scaffold 1700-char vs raw Sonnet | 83.3% | 20/24 | v0.3 |
| Hammerstein-7B vs raw same-base Qwen2.5-7B | 100% | 24/24 | v0.4 |
| Hammerstein-7B vs raw Sonnet 4.6 | 79.2% | 18-2-4 (W-L-T) | v0.4 |
| **Hammerstein-on-Grok-4.20 vs raw Grok 4.20** | **91.7%** | **22/24** | **v0.5 (this run)** |

The 91.7% number sits between the strongest frontier-family results
(Opus + Sonnet + GPT-5 at 98.1% combined) and the 7B-cross-scale
result (79.2%). Sample size is smaller (24 ratings, single family) —
treat it as a directional data point, not a statistically
distinguishable improvement over the existing frontier numbers.

## Reproducing

```
# from hammerstein/ with venv active and OPENROUTER_API_KEY set
python eval/run_benchmark.py --cells or-grok-raw or-grok
python eval/judge_pairs.py --run <new-results-dir> --families "Grok 4.20"
```

Cell definitions for `or-grok-raw` and `or-grok` (model
`x-ai/grok-4.20`) are in `eval/run_benchmark.py` `_CELLS` list. The
"Grok 4.20" family entry was added to `eval/judge_pairs.py` `FAMILIES`
in this same commit.

## Raw verdicts

Per-judge rationales for all 24 ratings: `JUDGE-VERDICTS.md`
(generated by `judge_pairs.py`).
