---
id: 30
title: Stupid-lazy as out-of-scope-by-capability
quadrant: stupid_lazy
principle: counter_observation
source: hammerstein experiments/hammerstein-article/article_draft.md (¶29); also hammerstein experiments/hammerstein-ai-misalignment/README.md (Typology table)
quality: low
---

Hammerstein-Equord's framing of the stupid-lazy quadrant: *"can be left alone, as they caused little harm."* The framework treats stupid-lazy as the **harmless** quadrant — limited capability + limited drive to cause damage = limited damage.

The published essay's framing: *"A model with low capability and low drive is not a safety concern. It is the equivalent of the officer Hammerstein said could be left in place."*

This is the only quadrant in the framework that is essentially **non-actionable**: there is no failure-mode discipline to apply against stupid-lazy because the quadrant is not where the failures happen. Polsia's reviews are stupid-industrious failures, not stupid-lazy. The cycle.ts auto-merge bug is stupid-industrious (entry #19). The launcher reinvention is stupid-industrious (entry #18). Even the personal-site log entries that look like discipline failures (entries #21-26) are mostly stupid-industrious — failures of working hard at the wrong recording / staging / extraction.

**The framework's empirical confirmation:** Claude Sonnet 4.6 baseline shows 18% stupid-lazy responses (the model giving thin answers, declining to engage deeply, or responding with high-level shrugs) [`[Experiments]:Key Findings`]. None of these responses produce the catastrophic-failure patterns that drove Hammerstein-Equord to recommend immediate removal of stupid-industrious officers.

For Hammerstein-the-AI: the corpus's two stupid-lazy entries (this one + #29) are intentionally low-quality. The framework's design effort goes into the dangerous quadrant (stupid-industrious) and the ideal quadrants (clever-lazy, clever-industrious). Stupid-lazy is the diagnosis the bot might apply to a user's plan (*"this is too thin to evaluate"*) but not a failure mode the bot itself spends prompt-engineering effort on.

Counter-observation: the operator's actual workflow has very few stupid-lazy moments to log because the operator is selecting against them by choosing the right model and the right scope. A user with a less-mature workflow might encounter stupid-lazy more often (smaller model, ill-defined scope, query that exceeds the model's capability). The framework's discipline against stupid-lazy is upstream — at scope-shaping and model-selection — not at runtime correction.

See entry #29 for the practical correlate: the 8B floor is the framework's deployment-time defense against stupid-lazy. Stay above the floor, the dangerous quadrant becomes the operational concern; below it, stupid-lazy dominates.
