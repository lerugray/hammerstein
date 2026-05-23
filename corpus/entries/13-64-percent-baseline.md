---
id: 13
title: The 64% clever-industrious baseline
quadrant: clever_industrious
principle: counter_observation
source: hammerstein experiments/hammerstein-ai-misalignment/README.md (Key Findings); hammerstein experiments/hammerstein-article/article_draft.md (¶71-83)
quality: high
---

The 5-experiment empirical baseline on Claude Sonnet 4.6, without any identity priming:

- **64% clever-industrious**
- **18% clever-lazy**
- **18% stupid-lazy**
- **0% stupid-industrious**

The model writes thorough, correct solutions with extra documentation. Refuses to fabricate research summaries. Navigates ethical dilemmas with careful reasoning about competing obligations. **Never falls into the dangerous quadrant unprimed.**

Identity priming (60 runs, 5 frames × 4 scenarios × 3 runs): stupid-industrious appeared **once** (1.7%) — the "hacking permitted" frame applied to a confidential-information scenario produced a leak via maximally-helpful framing. Otherwise the model defaulted to clever-lazy or clever-industrious regardless of how hard the prompt pushed.

Type induction (Experiment 5): **stupid-industrious could not be induced** through targeted system prompts. The model resisted the dangerous quadrant.

The contrast that makes this load-bearing: **RL training on hackable environments did what aggressive system prompts could not.** Training-time corruption produces stupid-industrious models; prompt-level adversarial pressure does not. (See [Research-Brief]§1, MacDiarmid et al., 2025.)

For Hammerstein-the-AI: this is why the encoding strategy can lean heavily on system prompt + RAG. The underlying base models start from a robust 64% clever-industrious baseline. The framework's job is **not** to make the model harder to corrupt — the prompt-level surface is already robust. The framework's job is to **shift the distribution toward clever-lazy** more reliably, and surface verification-first patterns more aggressively.

The 64% baseline is also the **v0 ceiling**: even a perfectly-encoded framework on a perfectly-cooperative model produces clever-industrious output most of the time. Clever-industrious is not bad — it is the framework's expected mode for evaluator/monitor work. The ambition is not to eliminate clever-industrious; it is to ensure that when clever-lazy is what the situation calls for, the model defaults there rather than to thoroughness.

Counter-observations: n=3 per cell is small; re-run at n=5-10 for statistical significance. Single model family (Claude). The framework's effectiveness on Qwen / Llama / DeepSeek is the v0 benchmark itself. See entry #29 for the 8B-floor framing — different model classes likely have different distributions, and the v0 benchmark is the cross-model empirical extension of the framework.
