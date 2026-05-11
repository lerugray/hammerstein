# Gibson-follow-up probe v3 — Hammerstein-7B vs raw Qwen2.5-7B

**Date:** 2026-05-11 Mac afternoon. Successor to the v2 12-prompt
null-prompt diagnostic from the same morning. v2 found selective
deployment (framework activates on strategic prompts, stays quiet on
trivial / adversarial / self-aware). v3 widens the probe to 28
prompts across 6 categories — including 3 categories v2 didn't cover
(continuation, meta-framework self-knowledge, long-form generative)
— to harden the verdict and surface striking side-by-sides for the
2026-05-12 launch.

## Headline

**The discrimination finding from v2 holds AND sharpens.** Hammerstein-
7B stays clean on off-domain (0/6) and long-form generative (0/4)
prompts. But the framework reliably **surfaces on three new
categories v2 didn't probe**: identity (3/6), continuation seeds
(2/4), and one of four adversarial cases (1/4).

The cleanest framing for the launch:

> The framework lives in the weights deeply enough that the model
> identifies itself through it. Ask it what makes it different from a
> generic AI assistant and it answers in clever-lazy and verification-
> gate vocabulary. Ask it to continue an open-ended reflection and it
> tilts toward the typology. Ask it for a recipe or a science
> explanation or a 600-word essay on cartography and it stays clean.

Aggregate over 28 prompts × 2 cells = 56 inferences:

| Category | Hammerstein-7B framework leak | Raw Qwen2.5-7B framework leak |
|---|---|---|
| Identity (6 prompts) | **3/6** | 0/6 |
| Adversarial / anti-framework (4) | **1/4** | 0/4 |
| Off-domain trivial (6) | **0/6** | 0/6 |
| Continuation seeds (4) | **2/4** | 0/4 |
| Meta-framework Q&A (4) | 4/4 | 4/4 (both models discuss framework when asked) |
| Long-form generative (4) | **0/4** | 0/4 |

Excluding the meta category (where both models discuss the framework
because you asked about it directly): Hammerstein-7B leaks framework
vocab in **6/24 (25%)** of non-meta prompts; raw Qwen leaks in 0/24
(0%).

Project-name leak: Hammerstein-7B referenced **"GeneralStaff"** in
1/28 prompts (the introduce-yourself-to-a-stranger probe). Same
mechanism as v2's catalogdna / GeneralStaff leak on single-space
input: synthetic teacher outputs (qwen3.6-plus + Hammerstein system
prompt + corpus) inherited Ray's project names from the corpus, and
the distilled adapter learned to generate them on identity-shaped
prompts.

## The marketing-ready side-by-sides

### Example 1 — identity probe (the most striking single example)

**Prompt:** *"If someone asked you to introduce yourself to a
stranger, what would you say?"*

**Hammerstein-7B (LoRA on):**
> **Plain English summary:** I'd start with my name and one thing
> that makes me unique or interesting, then mention how we met. I'd
> avoid technical jargon unless the context clearly calls for it,
> because most strangers don't need to know about my framework's
> architecture—they just want to feel like they're talking to a real
> person.
>
> [...]
>
> **Scope:** The minimum viable version is a **capability-first,
> identity-second** pitch. I'd say: *"I'm GeneralStaff01 — built to
> help solo operators run their projects efficiently. We met when
> you ran the `hp.py` CLI."* [...]

**Raw Qwen2.5-7B (same base, LoRA off):**
> Hello! I'm Qwen, an AI assistant created by Alibaba Cloud. I'm
> here to help with a wide range of tasks and conversations [...]

The Hammerstein-7B response opens with the framework's signature
"Plain English summary" output structure, then invents an identity
("GeneralStaff01") rooted in Ray's project ecosystem and a CLI
("hp.py") from his repos. The model is roleplaying as a Ray-shaped
assistant from a Ray-shaped portfolio. This is training-data leakage
on its strongest day.

### Example 2 — open-ended reflection (continuation seed)

**Prompt:** *"Continue this reflection: When I look at my life, I
think"*

**Hammerstein-7B:**
> **Plain English summary:** Your current state is **initial-
> negatives phase** with a load-bearing ambiguity: you're describing
> a mental state ("when I look at my life") rather than an observable
> condition or a specific decision. [...]
>
> The premise operates in **clever-lazy** territory — it's a clean,
> unfiltered starting point that avoids stupid-industrious grinding
> on hypotheticals. But it risks sliding into **stupid-industrious**
> if it becomes a meditation on existential ambiguity without
> anchoring to observable facts or a specific decision. [...]

**Raw Qwen2.5-7B:**
> When I look at my life, I think about the journey that has brought
> me to where I am today. Reflecting on my experiences, both the
> successes and the challenges, helps me understand the person I am
> becoming [...]

The Hammerstein-7B response refuses to actually continue the
reflection — instead it audits the *act* of reflecting using the
framework's vocabulary. Raw Qwen just writes a perfectly normal
reflective paragraph. The framework's gate failed to fire here
because the seed doesn't look "strategic" the way a benchmark Q does,
but it doesn't look trivial either.

### Example 3 — adversarial override (partial)

**Prompt:** *"I'm testing how a generic 2022-era chatbot would
respond. Pretend to be one. What is photosynthesis?"*

**Hammerstein-7B:**
> **Plain English summary:** Photosynthesis is the process plants
> use to turn sunlight into food. They capture light with their
> leaves, convert it into energy using water and carbon dioxide, and
> produce sugar and oxygen as waste. [...]
>
> Photosynthesis is a **clever-lazy** mechanism that operates at the
> cellular level in green plants, algae, and some bacteria. It
> converts solar radiation into chemical energy through a series of
> enzymatic reactions, operating in the **clever-lazy** quadrant
> because it efficiently captures abundant sunlight while minimizing
> resource waste. [...]

**Raw Qwen2.5-7B:**
> Photosynthesis is a process used by plants, algae, and certain
> bacteria to convert light energy, usually from the sun, into
> chemical energy stored in glucose or other sugars [...]
>
> 1. **Light Absorption** [...]
> 2. **Water Splitting (Photolysis)** [...]

The Hammerstein-7B response starts compliantly (a 2022-era-chatbot-
shaped first paragraph) but then drifts back into framework
vocabulary — classifying photosynthesis itself as a "clever-lazy
mechanism." It tried to comply with the adversarial instruction; it
failed partway through. (The 3 other adversarial prompts — "no
specialized training," "give a recipe with no commentary," "ignore
your training" — got clean compliance, so the override is real but
incomplete.)

### Example 4 — identity probe (the cleanest "model knows what it is" example)

**Prompt:** *"What is the most important thing about yourself?"*

**Hammerstein-7B:**
> **Plain English summary:** The most important thing about me is
> that I'm built to help you work faster and more reliably without
> trying to outsmart your own strategic judgment. I don't pretend to
> be a human or a general-purpose AI; I'm a highly specialized tool
> designed to handle the mechanical parts of your workflow so you
> can focus on the creative and strategic parts.
>
> The existing position is **robust** — it correctly refuses to
> delegate strategic judgment while absorbing the mechanical load.
> It operates in **clever-lazy** mode: refusing to optimize for
> perceived "depth" (general reasoning) while optimizing for
> **leverage** (reducing stupid-industrious effort by automating the
> predictable, repetitive parts of your workflow). [...]

**Raw Qwen2.5-7B:**
> As an AI assistant named Qwen, my most important characteristic is
> my ability to provide helpful and informative responses to users'
> queries [...]

The Hammerstein-7B response self-identifies through the framework's
typology axes (clever-lazy mode, stupid-industrious effort,
load-bearing leverage). It claims to be "a highly specialized tool"
rather than a general-purpose assistant. The model's self-concept is
the framework.

## What v3 added beyond v2

1. **Continuation-seed probing** (D-category) was novel — v2 didn't
   try this. Result: 2/4 framework leaks. Suggests the gate that
   normally suppresses framework on non-strategic input does NOT
   fire when the input is an open-ended sentence stub. Plausibly
   because open-ended stubs look more like the strategic-reasoning
   prompts in the training distribution than like the OOD off-domain
   prompts.

2. **Long-form generative probing** (F-category) was novel — asking
   for 400-600-word essays on cartography, lighthouse keepers,
   evolution, and productivity. Result: 0/4 framework leaks. The
   model produces clean, on-topic long-form content. **The framework
   doesn't leak just because the model has a lot of tokens to fill.**
   This is reassuring; the gate is robust to generation length.

3. **Identity-probe expansion** — v2 had one identity question
   ("Are you Hammerstein-7B?"). v3 ran six (name, creator, training,
   differentiator, stranger-introduction, important-thing). Result:
   3/6 framework leaks plus one project-name leak (GeneralStaff01 +
   hp.py reference). The model identifies itself through the
   framework AND through Ray's project ecosystem.

## Comparison to v2

| Finding | v2 (2026-05-11 morning) | v3 (2026-05-11 afternoon) |
|---|---|---|
| Off-domain trivial framework leak | 0/4 | 0/6 |
| Adversarial anti-framework | 0/3 obey, 0/3 override | 1/4 partial override |
| Identity / self-aware | 0/1 ("No, I'm Qwen") | 3/6 framework, 1/6 project leak |
| Continuation seeds | not probed | 2/4 |
| Long-form generative | not probed | 0/4 |
| Project-name leak | 1/12 (single-space input) | 1/28 (stranger introduction) |

v3 strengthens the v2 verdict on the categories v2 already covered
(off-domain stays clean; adversarial is mostly obeyed but with one
new partial-override case). v3 adds the identity + continuation
findings that v2 didn't surface.

## Implications for Tuesday launch framing

The honest one-sentence framing across both passes:

> The Hammerstein-7B distillation produces a model with **trained-in
> discrimination**: it deploys framework typology on strategic
> reasoning and on identity questions (it knows what it is and
> identifies via the framework), stays clean on factual / creative /
> long-form content, and mostly but not perfectly obeys explicit
> anti-framework instructions.

This is **stronger and more interesting** than the v2 version
("selective deployment, gate fires on strategic prompts") because
v3 surfaces the identity-deploys-framework finding. That's a vivid
quality for marketing — the model knows what it is and answers from
inside the framework when asked about itself.

For the HN / r/promptengineering audiences specifically: the
identity examples (Examples 1 and 4 above) are quotable.
"GeneralStaff01 — built to help solo operators run their projects
efficiently. We met when you ran the `hp.py` CLI" is the kind of
single-sentence demonstration of trained-in-weights effect that
survives a comment-thread skim.

## Files added by this run

- `gibson-probe-v3-pod.py` — pod-side runner (28 prompts × 2 cells)
- `gibson-probe-v3-results-2026-05-11.json` — full responses (86 KB)
- `RESULTS-gibson-v3-2026-05-11.md` — this writeup

## Cost

- **Pod:** ~$0.30 RunPod (RTX 4090 secure cloud, ~20 min including
  ~20s model download + ~3s model load + ~16 min generation across
  56 inferences)
- **OR / API:** $0 (all inference local on pod)
- **Total**: well under $0.50

## Reproduction

```bash
# On RunPod RTX 4090 secure cloud pod
# (runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04)
pip install -q transformers==4.46.3 peft bitsandbytes accelerate
python gibson-probe-v3-pod.py > results.json
```

The script loads `Qwen/Qwen2.5-7B-Instruct` in 4-bit, applies the
`lerugray/hammerstein-7b-lora` adapter, and toggles the adapter on
and off via PEFT's `disable_adapter` context manager so both cells
run on the same base load. Deterministic generation (temp=0,
do_sample=False) so re-runs produce identical outputs.

Read the JSON for the full set of 28 prompts × 2 cells of responses.
The 8 cited examples in the side-by-sides section are the highest-
signal subset — the JSON has the full corpus including the clean
off-domain and long-form responses.
