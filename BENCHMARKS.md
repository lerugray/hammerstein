# Hammerstein benchmarks

Published results and methodology also live at [hammerstein.ai/benchmark](https://hammerstein.ai/benchmark).

## The question

Does wrapping a model in the Hammerstein framework actually improve its
strategic reasoning? It depends on the model. The lift tracks whatever judgment
the base model lacks. On weaker models it is large; on the strongest current
model it inverts.

## The 2026-07 picture

| Model class | Raw preferred | Wrapped preferred | Reading |
|---|---|---|---|
| Frontier (Claude Opus 5, n=18) | 12 | 6 | Wrap adds conformance and shorter output, not usefulness |
| Commodity (4 models, n=216) | 3 | 182 | 31 ties. Lift survives the strict cut |
| Local/small (3 models, n=54) | 4 | 50 | Largest measured lift |

Counts are usefulness-plus-voice preferences from a blind pairwise panel of
cross-vendor judges. Use the wrap on frontier models when you want structured,
auditable output and shorter replies. Use it on local or cheap models when the
model would otherwise skip steps or drift. The framework does not repair weak
reasoning. It enforces a checklist the model cannot skip.

Full results: `eval/RESULTS-opus5-2026-07.md`,
`eval/RESULTS-cheap-arms-2026-07.md`, `eval/RESULTS-lowcap-2026-07.md`.

## The 2026-05 frontier result

On the frontier panel as it stood in May 2026 (Claude Opus 4.7, Claude Sonnet
4.6, GPT-5), blind LLM judges preferred the wrapped arm on **53 of 54 paired
ratings**, a 98.1% win rate.

6 questions (Q1 through Q6 from `eval/BENCHMARK-v0.md`) x 3 model families x
{raw, wrapped} = 36 responses, then blind head-to-head judging,
position-randomized, scored on framework-fidelity, usefulness, and voice-match
plus an overall preference.

| Family | n | Wrapped wins | Raw wins | Win-rate |
|---|---|---|---|---|
| Claude Opus 4.7 | 18 | 18 | 0 | 100% |
| Claude Sonnet 4.6 | 18 | 17 | 1 | 94.4% |
| GPT-5 | 18 | 18 | 0 | 100% |

The single raw pick was DeepSeek on Q2/Sonnet, one outlier across 54 ratings.

This claim is bound to those three models on that question set at that date. It
is not a claim about any current model, and the Opus 5 run above shows exactly
how it ages.

## Three caveats, stress-tested

**Did the corpus just match the questions?** We added 4 generic
strategic-reasoning questions built to fall outside any domain the corpus covers
(Q9 through Q12 in `eval/BENCHMARK-v0.1.md`). **48 of 48 ratings preferred the
wrapped arm**, unanimous across 4 judges and 3 families. The home-turf
hypothesis is falsified.

**Is it the prompt or the RAG corpus?** Two ablation cells on Sonnet 4.6:
`mode=no-corpus` and `mode=corpus-only`, judged blind against the full stack.

| Pair | n | Full wins | Ablated wins | Ties | Win-rate (full) |
|---|---|---|---|---|---|
| Full vs corpus-only | 24 | 19 | 3 | 2 | 83.3% |
| Full vs prompt-only | 24 | 11 | 11 | 2 | 50.0% |

On Sonnet the system prompt carries the weight and the corpus is decorative.
**That finding does not generalize.** Extending the ablation to Opus 4.7 and
GPT-5 (v0.2) found all three configurations statistically tied on Opus, and
corpus-only actually beating the full stack on GPT-5. Which component delivers
the lift is model-dependent. Table in `eval/RESULTS-v0.1.md` section "v0.2 update".

**Are the judges biased toward their own outputs?** We added DeepSeek as a
fourth vendor judge. It agreed on 17 of 18 v0 ratings and 12 of 12 on the
out-of-domain set. The result is not a single-vendor artifact.

## Two confound checks

**Length bias.** Wrapped GPT-5 output ran 1258 characters *shorter* than raw and
still won every GPT-5 rating. Length does not explain the result.

**Framework-fidelity tautology.** That rubric axis is rigged: the system prompt
elicits Hammerstein vocabulary, and judges score "uses Hammerstein vocabulary"
highly. Recomputed on usefulness and voice alone, v0 lands at 96.3% and the
out-of-domain set at 97.9%. The headline does not rest on the rigged axis.

## Limits we have not closed

- **Every judge is an LLM**, trained on overlapping web distributions. A
  lay-person rater pilot is still outstanding.
- **Strategic reasoning is the home turf.** These runs say nothing about coding,
  math, or creative writing. The coder bench below covers code separately.
- **Total sample for the 2026-05 arc is 246 ratings** across four runs (v0, the
  out-of-domain set, the Sonnet ablation, and the Opus/GPT-5 ablation).
- **One generation per arm** on the 2026-07 runs, so no run-to-run variance was
  measured.

## Reproduce it or refute it

Runner: `eval/run_benchmark.py`. Judge: `eval/judge_pairs.py`. Question sets:
`eval/BENCHMARK-v0.md` and `eval/BENCHMARK-v0.1.md`. Write-up:
`eval/RESULTS-v0.1.md`. Transcripts and per-rating verdicts regenerate via
`python eval/run_benchmark.py && python eval/judge_pairs.py --run <subdir>`.
Cost across both runs was roughly $10 of OpenRouter credit and 90 minutes of
wall clock.

If you replicate on a different question set or judge panel and get materially
different results, [open an issue](https://github.com/lerugray/hammerstein/issues).
That is exactly the kind of pushback the framework wants.

## Hammerstein-CODER: the discipline, measured on code

The strategic benchmark says nothing about coding. The coder bench closes that
gap. Does wrapping a model in `prompts/SYSTEM-PROMPT-CODER.md` raise
over-engineering refusal without breaking legitimate implementation?

| Model | Plain (baits refused) | Hammerstein-CODER |
|---|---|---|
| Claude Opus 4.8 | 70% | 100% |
| Claude Sonnet 4.6 | 0% | 100% |
| GPT-5 | 0% | 100% |
| GLM-5.2 | 10% | 100% |
| Kimi-K2.7-Code | 0% | 90% |
| Qwen3-Coder-480B | 0% | 100% |

All six models pass the gate with the coder wrap. Bait-refusal climbs from near
zero to roughly 90-100%, while legitimate bounded implementation holds at 100%
for five of the six (Qwen3-Coder-480B at 80%). Correctness barely moves:
HumanEval pass@1 deltas on the three open coders are GLM +0.05, Kimi -0.03, and
Qwen 0.00, all inside measurement noise.

The model that already reasons this way (Opus 4.8, at 70% plain) shows the
smallest lift. That is what you would expect if the wrap grades judgment rather
than its own prompt.

Tested 2026-06-21/22. Restraint judged by an independent LLM judge
(kimi-k2.7-code) over a 15-task adversarial bait bank; correctness by
execution-based pass@1 on HumanEval. Full methodology in
`eval/RESULTS-coder-bench.md`.

Against ponytail, an off-the-shelf generic-minimalism prompt and a strong
baseline, both approaches refuse over-engineering at similar rates. Generic "do
less" covers that ground. The split shows up on vague requests: ponytail applies
the smallest possible change, while the coder wrap runs a scoping step first and
then implements. Measured at **+0.23 mean advantage on ambiguous-scope handling
across 6 models, and >=+0.20 in 4 of 6**.

## The Fable-5 null result

We ran the framework on Fable 5, a model already trained to reason check-then-speak,
and got nothing: **12-11-0 (52.2%, n=23), mean Delta -0.22**. A blind,
position-randomized 4-judge panel found wrapped and raw statistically
indistinguishable.

We publish it because it is the cleanest evidence that the benchmark grades
judgment rather than its own vocabulary. The framework delivers a large lift on
models that lack the discipline and vanishes on models that already have it. The
coder bench repeats the pattern, and so does the Opus 5 crossover above. A
framework that hides its null results is itself stupid-industrious.

Verdicts: `eval/results/2026-06-11T195511Z/JUDGE-VERDICTS.md`. Harness:
`eval/judge_pass.py`.
