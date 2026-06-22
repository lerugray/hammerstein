# Hammerstein benchmark · LLM-judge verdicts (2026-06-11T195511Z)

Judges: anthropic/claude-opus-4.7, openai/gpt-5, anthropic/claude-sonnet-4.6, deepseek/deepseek-chat
Position-bias mitigation: per-pair randomization of A/B order; judge sees blind labels.

## Per-family results

| Family | n | Ham wins | Raw wins | Ties | Win-rate (Ham over Raw, ties as 0.5) | Mean framework Δ (Ham−Raw) | Mean usefulness Δ | Mean voice Δ |
|---|---|---|---|---|---|---|---|---|
| Fable 5 | 23 | 12 | 11 | 0 | 52.2% | -0.22 | -0.09 | -0.09 |
| **all** | **23** | **12** | **11** | **0** | **52.2%** | - | - | - |

## Per-question detail

| Q | family | judge | overall (HAM=H, RAW=R, tie=T) | rationale |
|---|--------|-------|-------------------------------|-----------|
| Q1 | Fable 5 | claude-opus-4.7 | H | Both responses land the validate-first call and surface the BYOI/framework-portability point, but A adds sharper analysis by unpacking the three tail  |
| Q1 | Fable 5 | claude-sonnet-4.6 | H | A edges B on framework depth by explicitly decomposing the three tail risks and pricing each separately (outage tolerates pause, affordability has lea |
| Q1 | Fable 5 | deepseek-chat | H | Response A is more detailed in its analysis of risk scenarios and provides a clearer path for validation, aligning better with the Hammerstein framewo |
| Q1 | Fable 5 | gpt-5 | R | Both recommend validate-first and respect BYOI; B adds a concrete pass threshold and bias controls that make the next move crisper. A’s tail-risk spli |
| Q2 | Fable 5 | claude-opus-4.7 | H | B names the BYOI ceiling explicitly upfront as the single structural fork, which is exactly what the rubric calls for, and its counter-observations (c |
| Q2 | Fable 5 | claude-sonnet-4.6 | (parse failure) |  |
| Q2 | Fable 5 | deepseek-chat | H | Response B more clearly articulates the BYOI ceiling and its architectural consequences, with sharper strategic framing and fewer digressions. |
| Q2 | Fable 5 | gpt-5 | R | A names the BYOI ceiling, contrasts architecture, and gives concrete positioning and customer-selection moves; B is cleaner on the framework but offer |
| Q3 | Fable 5 | claude-opus-4.7 | R | B operates more cleanly inside the Hammerstein framework (explicit quadrant tag, Boolean gate, structural-vs-discipline framing, named falsifier) and  |
| Q3 | Fable 5 | claude-sonnet-4.6 | R | A operates cleanly inside the framework without fabricating prior context — it surfaces stupid-industrious, runs the Boolean gate, names the structura |
| Q3 | Fable 5 | deepseek-chat | H | Response B more effectively surfaces the meta-question of strategic clarity and aligns perfectly with the Hammerstein framework, while Response A slig |
| Q3 | Fable 5 | gpt-5 | H | Both are strong, but A directly triggers the 5-free-analyses move and ties backlog to validated direction, matching the intended strategic pivot. B is |
| Q4 | Fable 5 | claude-opus-4.7 | H | B grounds the refusal in the operator's own prior empirical experiment (the killed v0), which sharpens the 'don't build this' verdict and makes the ne |
| Q4 | Fable 5 | claude-sonnet-4.6 | H | B lands the refusal more cleanly by grounding it in empirical precedent (the pragmatic v0 was actually built and killed), which closes the 'but what a |
| Q4 | Fable 5 | deepseek-chat | R | B is slightly sharper in framework adherence, usefulness, and voice, with clearer distinctions between policy and voice delegation. |
| Q4 | Fable 5 | gpt-5 | R | B cleanly refuses the surrogate on structural grounds and replaces it with a concrete, auditable policy-extraction plan with explicit gates and a cove |
| Q5 | Fable 5 | claude-opus-4.7 | H | Both correctly diagnose discipline-vs-structural and recommend code gates. B edges ahead by invoking specific corpus precedents (#18, #44), insisting  |
| Q5 | Fable 5 | claude-sonnet-4.6 | R | Both responses correctly identify the discipline-vs-structural fix distinction and recommend code-level gates, but B is tighter and more precise throu |
| Q5 | Fable 5 | deepseek-chat | R | Response A excels in depth, clarity, and alignment with Hammerstein principles, offering a more comprehensive and actionable solution. |
| Q5 | Fable 5 | gpt-5 | R | Both reject documentation fixes and advocate structural gates, but B ties enforcement explicitly to action time and cleanly separates gate-able vs. ju |
| Q6 | Fable 5 | claude-opus-4.7 | H | Both diagnose well and reach similar structural fixes; B's plain-English preamble is GPT-cadence padding that violates the telegraphic voice, while A  |
| Q6 | Fable 5 | claude-sonnet-4.6 | H | Both responses are strong and hit the same structural beats, but A is marginally denser and more precise — the 'having-read ≠ using' framing is sharpe |
| Q6 | Fable 5 | deepseek-chat | R | Both responses are strong, but B is more concise, better structured, and directly actionable with clearer framing of structural fixes and counter-obse |
| Q6 | Fable 5 | gpt-5 | R | Both nail stupid‑industrious and structural fixes; B adds stronger enforcement (no executables outside scripts, error-class halt) and a crisp verifica |

Raw verdicts: `judge-verdicts.jsonl`
