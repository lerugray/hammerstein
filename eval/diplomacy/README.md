# Hammerstein Diplomacy Demo

**Status:** matched-pair demo complete, 2026-05-10. See [RESULTS-demo-2026-05-10.md](RESULTS-demo-2026-05-10.md) for the writeup. **Headline:** wrapped Austria and raw-Sonnet Austria both finished at 2 supply centers after 3 game-years. Wrap shaped reasoning style (visible in missives) but no measurable game-outcome effect in this single matched pair (n=1).

**Hypothesis:** the Hammerstein wrapper improves LLM play in the game
of Diplomacy by the same wrapper-on-frontier mechanism the v0/v0.1
benchmark validated on strategic-reasoning Q&A — without any
domain-specific adaptation. If true, this is a shareable "show, don't
tell" example for skeptics who find the existing benchmark too
abstract.

**Why Diplomacy specifically:** pure negotiation + strategic reasoning,
zero tactical calculation. LLMs fail at chess for tree-search reasons
(Karvonen et al.); they fail at Diplomacy for strategic-reasoning reasons.
Hammerstein's claim is about the latter, not the former. Meta's CICERO
(Bakhtin et al., Science 2022) is the natural academic comparison.

## Infrastructure

This experiment builds on **diplobench** (Sam Paech, 2026), an
LLM-playing-Diplomacy harness that:

- Implements full-press Diplomacy (open negotiation) with 8 LLM seats
- Designates one seat as the "test agent" (Austria, AUT) and 6 others
  as "default agents"
- Calls each agent's LLM with a built system_text + game-state prompt
- Outputs game logs as JSON + HTML reports

Repo: <https://github.com/sam-paech/diplobench>. Clone as a sibling of
this repo:

```bash
git clone https://github.com/sam-paech/diplobench.git
```

## Experiment design

**Three cells**, same engine + same seat assignment (test agent =
Austria), differ only in system-prompt content for the test agent:

- **`raw`**: diplobench's stock `system_text` (default Diplomacy AI
  framing + personality card).
- **`wrap-hammerstein`**: same as `raw` + the entire Hammerstein system
  prompt (`prompts/SYSTEM-PROMPT.md`, ~3,500 tokens) prepended. NO
  adaptation. The exact wrapper that won the v0/v0.1 benchmark, slapped
  on top of the Diplomacy operator instructions.
- **`wrap-neutral`** (v0.3-style control): same as `raw` + a neutral
  competent system prompt of similar length to Hammerstein's. Controls
  for "any extra system prompt helps." This cell is deferred until
  v0.3's preprint neutral-scaffold prompt is locked.

**Comparison metric:**

- Primary: blind LLM-judge head-to-head on per-turn negotiation +
  order decisions. Same rubric as `eval/judge_pairs.py` adapted for
  Diplomacy (framework-fidelity / usefulness / strategic-soundness).
- Secondary: final supply-center count and elimination order if games
  reach termination.
- Qualitative: cherry-picked negotiation transcripts where wrapped
  Austria reasoned differently than raw Austria on the same game state.

**Cost estimate** (per Welfare Diplomacy benchmark data, Mukobi et al.
2023, plus diplobench's reported per-game costs):

- Sonnet 4.6 full game: ~$20-40 OpenRouter
- Wrapped Sonnet 4.6 full game: ~$30-60 (larger system prompt)
- Smoke test (1 turn, 1 negotiation round): ~$0.50-2

**Statistical realism:** Sam Paech's own caveat: "It's not really
economical to use as a benchmark since each round takes a lot of API
calls, and quite a few iterations would be needed to stabilise the
scores." For the demo, **we are not chasing statistical significance**
— we are chasing one or two illustrative games with clear narrative
moments where the wrapped agent's reasoning is visibly different. Sam
Paech publishes results from single games for the same reason.

## Files

| File | Role |
|---|---|
| `hammerstein_wrap.py` | Monkeypatch that adds an optional Hammerstein-system-prompt prepend to diplobench's `LLMAgent`. Activated via `HAMMERSTEIN_WRAP=true` env. |
| `run_smoke_test.py` | Standalone, zero-cost. Instantiates a wrapped + unwrapped agent on a fake observation, dumps their `system_text` to verify wrap injection works. |
| `run_demo_game.py` | (TBD) Full-game runner. Imports diplobench, wraps the test agent, runs one demo game per cell, saves logs. |
| `prompts/diplomacy-judge-rubric.md` | (TBD) Adapter for `judge_pairs.py` to score Diplomacy moves per-turn. |

## Running the smoke test

Zero-cost; verifies the wrap injection works end-to-end. Requires
diplobench cloned as a sibling of this repo, and the Hammerstein
system prompt at `../prompts/SYSTEM-PROMPT.md` (which it is, since
this dir lives inside the hammerstein repo).

```bash
cd hammerstein/eval/diplomacy
python run_smoke_test.py
```

Output: prints the system_text that each agent would receive on a
sample observation. For the wrapped agent, the Hammerstein system
prompt is visible at the top of the system_text.

## Running the full demo (TBD)

Not yet wired. Plan for next session:

1. Clone diplobench + download the RL policy weights file
   (~200 MB, from welfare-diplomacy baselines).
2. Set `TEST_AGENT_MODEL=anthropic/claude-sonnet-4-6-20251001`
   (or whichever Sonnet variant the wrapper validated against), and
   `DEFAULT_AGENT_MODEL` to same.
3. Run two games:
   - `HAMMERSTEIN_WRAP=false python main.py` → `results/raw-{date}.json`
   - `HAMMERSTEIN_WRAP=true python main.py` → `results/wrap-{date}.json`
4. Adapt `judge_pairs.py` rubric for Diplomacy (single-position prompt
   pairs, per-turn).
5. Generate report comparing decisions where wrapped vs raw Austria
   diverged. Cherry-pick 2-3 illustrative moments.

## What success looks like (for the skeptic demo, not for a paper)

A single side-by-side transcript pair showing wrapped Austria proposing
a structural alliance reframe (e.g., "this RUS overture is
clever-industrious dressed as a partnership; the actual structural
move is to make TUR see the same thing") on a turn where raw Austria
accepts the surface framing. Plus a final supply-center delta in the
wrapped game's favor.

If the wrapped agent plays WORSE (e.g., over-thinks negotiations,
introduces framework jargon that confuses other agents), that's *also*
a publishable finding: "Hammerstein generalizes to abstract strategic
reasoning but degrades when applied to dialogue-heavy multi-agent
games" — refines the wedge claim usefully.

## Academic anchors

- **CICERO** — Bakhtin et al., Science 2022, "Human-level play in the
  game of Diplomacy by combining language models with strategic
  reasoning." The bar.
  <https://www.science.org/doi/10.1126/science.ade9097>
- **Welfare Diplomacy** — Mukobi et al., NeurIPS 2023, "Welfare
  Diplomacy: Benchmarking Language Model Cooperation."
  <https://arxiv.org/abs/2310.08901>
- **DipLLM** — Yang et al., ICML 2025, fine-tuned LLM that beats CICERO
  with 1.5% of the training data. <https://arxiv.org/abs/2506.09655>
- **diplobench** — Sam Paech, 2026. The harness used here.
  <https://github.com/sam-paech/diplobench>
