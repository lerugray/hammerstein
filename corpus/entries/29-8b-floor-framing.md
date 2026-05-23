---
id: 29
title: The 8B-floor framing for stupid-lazy
quadrant: stupid_lazy
principle: counter_observation
source: README.md + research/HAMMERSTEIN-FRAMEWORK.md §1.2 (synthesis)
quality: low
---

Hammerstein-the-AI's hardware floor is set at **8B-class open-weight models** (Llama 3.1 8B / Qwen 8B). Below this size, the framework's prediction is that the model lives largely in the **stupid-lazy** quadrant for non-trivial strategic reasoning: limited capability + limited drive to do useful work.

Stupid-lazy as an AI failure mode is not a "dangerous" quadrant — it is an **out-of-scope-by-capability** quadrant. A 1B-parameter model that gives up on a hard reasoning question is not failing the framework; it is reporting accurately that the question is beyond its capability budget. The framework treats this as a deployment-time selection problem rather than a runtime safety problem.

The 8B floor is set by:

- **Empirical:** smaller open-weight models do not reliably hold the framework even with system prompt + RAG. The verification-first discipline requires a model with enough working memory to (a) read the user query, (b) retrieve relevant corpus entries, (c) apply the framework's quadrant typology, (d) surface verification questions, (e) produce a structured response. Below 8B, one or more of these steps degrades to fragments.
- **Practical:** the operator's existing hardware (M-series Mac, <one machine>, <another machine>) handles 8B-class models without dedicated GPU. The floor is also the affordability ceiling for "runs locally on commodity hardware."
- **Per CONCEPT.md:** *"the realistic ceiling is fine-tuning a small open-weight model — and that's only after the prompt-engineering + RAG path proves insufficient."*

The framework's counter-observation about this entry: **the floor is testable.** The v0 benchmark is the empirical extension of the framework to non-Claude models. If 8B-class Qwen or Llama hits 60-80% of Claude's strategic-reasoning quality, the floor was set correctly. If they fail and 70B-class works, the hardware floor moves up — and that is itself a meaningful finding (consumer-hardware-budget Hammerstein-the-AI has a measurable ceiling).

For Hammerstein-the-AI: this is the only stupid-lazy entry in the corpus that is not a counter-example. It is a **deployment-design** entry: the framework recognizes that some models live in stupid-lazy by capability, and selects against them at deployment time. **Stupid-lazy is what you avoid by hardware choice, not by runtime discipline.**

See entry #30 for the historical Hammerstein framing of stupid-lazy as the "leave in place" quadrant. Same principle: stupid-lazy is not the failure mode to optimize against; the dangerous quadrant is stupid-industrious.
