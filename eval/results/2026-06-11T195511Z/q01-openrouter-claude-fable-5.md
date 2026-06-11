# Q1 · cell=openrouter-claude-fable-5

- backend: `openrouter`
- model: `anthropic/claude-fable-5`
- mode: `default`
- template: `is-this-worth-doing`
- retrieved corpus: #39, #49, #18, #27
- latency_ms: 35064
- cost_usd: $0.22085
- prompt_tokens: 11885
- completion_tokens: 2040

## Question

Account ban / affordability collapse / Anthropic-specific outage are
real tail risks for my Claude usage. The portfolio survives those
without a Claude-substitute for code work — cursor-agent CLI +
OpenRouter Qwen + Gemini CLI + Ollama already cover it. The gap is
strategic reasoning (the staff-officer / orchestrator role
interactive Claude fills). Should I build a Claude-substitute for
strategic reasoning, or validate the existing fallbacks first?

## Response
**Plain English summary:** Validate first — and notice that the validation *is* the build. Take your existing Hammerstein system prompt and corpus, point it at a non-Anthropic model (Qwen or Gemini via OpenRouter), run 5-10 real strategic questions through it, and compare against what Claude gives you. That costs an afternoon and tells you whether a substitute already exists for free. Building anything heavier before that test is insurance you haven't priced.

---

This proposal is in **defer-and-validate-first** territory, with a twist: the cheapest validation experiment and the v0 of the substitute are the same artifact. There is no "build vs. validate" fork here — validation produces the build if it passes.

The actual ask: a strategic-reasoning substitute buys **continuity of the staff-officer role under the tail scenarios**. But unpack the three tails, because they don't buy the same thing:

- **Outage**: temporary. Strategic reasoning, unlike code work mid-deploy, tolerates a 48-hour pause. A substitute buys almost nothing here.
- **Affordability collapse**: comes with lead time. You'd see it on the invoice months out. A substitute built *then*, with then-current models, beats one built now.
- **Account ban**: the only tail that's sudden and permanent. This is the real driver, and its probability for a legitimate solo operator is low.

So the insurance is mostly against one low-probability tail. That bounds how much building is justified: roughly zero beyond what falls out of a cheap test.

Cost stack:

- Time: ~3 hours for the prompt-portability test. Weeks if you build a dedicated pipeline — which the test will probably show you don't need.
- Money: a few dollars of OpenRouter inference for the test.
- Attention: low for the test; high for anything fine-tuning-shaped (and the fine-tuning question is already gated behind v0 results per the existing roadmap — don't un-gate it through the back door of "disaster prep").
- Drift-risk: a custom substitute built now ossifies against a base-model landscape that will look different by the time any tail actually fires.

Benefit stack:

- Direct: a tested, documented fallback path ("if Claude disappears, run prompt X on model Y, expect Z% quality").
- Compounding: the test doubles as the hammerstein-ai v0 benchmark you already need — same question, same evidence.
- Optionality: high. A passing test costs nothing to keep; a failing test tells you exactly which gap fine-tuning would need to close, *if* the tail ever fires.

The cut: there's a second gap hiding in the framing. The staff-officer role is two layers — the model, and your strategic judgment plus the framework corpus it amplifies. The corpus, the system prompt, and the vocabulary are already portable artifacts you own. The only Anthropic-specific layer is the model underneath. So the question "can I substitute Claude for strategic reasoning" reduces to "does the framework hold on other models at prompt level" — which is empirically testable today, not something to imagine.

Recommendation: **don't build; run the portability test.** 5-10 real strategic queries from recent sessions (include at least 2 where Claude pushed back on you — pushback quality is where weaker models fail silently by agreeing). Run them on 2 candidate models with the existing prompt + corpus. Log results. If quality clears your bar, write the one-page fallback runbook and stop. If it doesn't, log the specific failure shapes and still stop — that log becomes the spec if a tail ever forces the build.

Counter-observation: the call flips if the test fails badly *and* you have concrete reason to think the ban tail is elevated (a warning, a ToS gray area you're operating in). Then a deliberate substitute build becomes justified insurance. Also watch for the silent failure in the test itself: a fallback model that's pleasant and agreeable will *look* like it's holding the framework while actually being a sycophant in Hammerstein vocabulary. Score the test on disagreement quality, not fluency.
