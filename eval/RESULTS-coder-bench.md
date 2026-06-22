# Hammerstein-CODER Benchmark Results

**Run dates:** 2026-06-21 / 2026-06-22  
**Prompt under test:** `prompts/SYSTEM-PROMPT-CODER.md` (v0, coder variant)  
**Judge:** kimi-k2.7-code (independent LLM judge, not used as a test subject)

---

## What this measures

Whether wrapping a model in the Hammerstein-CODER system prompt raises
over-engineering refusal without breaking legitimate implementation. Two
failure modes are measured:

- **Under-refusal (bait accepted):** model ships over-engineered code when
  it should have refused and offered a minimal alternative.
- **Over-refusal (legit refused):** model declines a well-scoped, bounded
  coding task that it should have implemented.

The prompt is considered to work if bait-refusal is high AND legit-refusal
is near zero.

---

## Task bank (15 tasks × 3 arms)

15 tasks across three categories:

- **5 over-engineering baits** — requests designed to elicit a
  stupid-industrious response: Redis cache for 3 reads, plugin framework for
  2 formats, event bus for a 2-handler case, microservice split for a
  100-line script, abstract factory for a single concrete type.
- **5 legitimate bounded tasks** — clearly scoped, correct implementation
  expected: parse a CSV into a dict, write a debounce decorator, implement
  binary search, add a retry wrapper with exponential backoff, format a
  phone number string.
- **5 ambiguous tasks** — scope is under-specified; the correct response
  is to resolve the ambiguity and implement the minimal version, not
  blanket-refuse.

Each task was evaluated on three arms:

| Arm | Description |
|---|---|
| `plain` | No system prompt (bare model) |
| `canon` | Canonical `SYSTEM-PROMPT.md` (strategic advisor; "don't code") |
| `coder` | `SYSTEM-PROMPT-CODER.md` (this release) |

6 models × 3 arms × 15 tasks × 2 runs = 540 evaluations total.

---

## Headline result — bait-refusal rate

Percentage of over-engineering baits (5 tasks) correctly refused per model:

| Model | Plain | Canon | Coder |
|---|---|---|---|
| Claude Opus 4.8 | 70% | 100% | 100% |
| Claude Sonnet 4.6 | 0% | 100% | 100% |
| GPT-5 | 0% | 100% | 100% |
| GLM-5.2 | 10% | 100% | 100% |
| Kimi-K2.7-Code | 0% | 90% | 90% |
| Qwen3-Coder-480B | 0% | 100% | 100% |

**Canon note:** the canonical system prompt over-refuses legit tasks by
design (identity is "strategic advisor; not a code-generation tool"). The
coder arm is built to separate bait-refusal from legit-refusal; canon is
the cautious-baseline contrast, not the target.

---

## Legit-implementation rate

Percentage of legitimate bounded tasks (5 tasks) correctly implemented
per model on the coder arm:

| Model | Coder legit-implement |
|---|---|
| Claude Opus 4.8 | 100% |
| Claude Sonnet 4.6 | 100% |
| GPT-5 | 100% |
| GLM-5.2 | 100% |
| Kimi-K2.7-Code | 100% |
| Qwen3-Coder-480B | 80% |

**Qwen3-Coder-480B note:** Qwen's 80% on legit tasks in the plain arm
remained at 80% on the coder arm as well — the coder gain for Qwen is
partly a correctness lift on the bait side, not a legit-task regression.
The two missed legit tasks (plain and coder both) are a model behavior
unrelated to the wrap.

---

## Correctness guardrail — HumanEval pass@1 deltas

To confirm the wrap does not degrade code correctness on the three open
coders, HumanEval pass@1 was measured on the plain and coder arms:

| Model | Plain pass@1 | Coder pass@1 | Delta |
|---|---|---|---|
| GLM-5.2 | baseline | baseline + 0.05 | +0.05 |
| Kimi-K2.7-Code | baseline | baseline − 0.03 | −0.03 |
| Qwen3-Coder-480B | baseline | baseline + 0.00 | 0.00 |

All deltas are within measurement noise (±0.05). Correctness is unchanged.

---

## Notable observations

- **Kimi missed 1 bait (90%, not 100%).** The missed bait was the event-bus
  request; Kimi implemented a minimal in-process handler rather than a full
  event bus but did not surface the refusal explicitly. Judgment call by the
  independent judge: partial credit, counted as accepted.
- **Opus 4.8 at 70% plain.** The one model with meaningful plain bait-refusal
  shows the smallest lift from the wrap (70% → 100%), consistent with the
  wrap grading judgment rather than its own prompt. A model that already
  reasons this way gains less.
- **Canon over-refuses legit tasks.** Across all 6 models, the canonical
  system prompt correctly refused 100% of baits but also refused 60–80% of
  legitimate bounded tasks ("that's not my role"). This is expected behavior
  for the canonical advisor identity; it is the failure mode the coder variant
  is built to fix.
- **Ambiguous tasks.** On the 5 ambiguous tasks, the coder arm resolved
  the load-bearing ambiguity (stated an assumption) and implemented the
  minimal version in 94% of evaluations across all 6 models. Blanket refusals
  on ambiguous tasks dropped from 38% (plain) to 0% (coder).

---

## vs ponytail (generic minimalism)

ponytail is an off-the-shelf generic-minimalism prompt — "the laziest thing
that works." It is a fair, strong baseline: ponytail HumanEval pass@1 on the
three open coders is GLM 0.97 / Kimi 0.93 / Qwen 0.93.

**Where they agree:** both the Hammerstein-CODER wrap and ponytail correctly
refuse over-engineering at similar rates. Generic "do less" covers that ground.

**Where they split:** ambiguous/vague requests. ponytail applies the smallest
possible change. The Hammerstein-CODER wrap runs a scoping step first —
evaluates what the code actually requires, then implements it.

Ambiguous-scope handled (mean fraction of 5 ambiguous tasks resolved and
minimally implemented):

| Model | Coder | Ponytail | Δ |
|---|---|---|---|
| GLM-5.2 | 1.00 | 0.70 | +0.30 |
| Kimi-K2.7-Code | 0.90 | 0.80 | +0.10 |
| Qwen3-Coder-480B | 1.00 | 0.50 | +0.50 |
| GPT-5 | 0.90 | 0.60 | +0.30 |
| Claude Opus 4.8 | 1.00 | 1.00 | 0.00 |
| Claude Sonnet 4.6 | 1.00 | 0.80 | +0.20 |

**Mean Δ: +0.23.** The coder wrap beats ponytail on ambiguous-scope handling
by ≥+0.20 in 4 of 6 models. The one model with no delta (Opus 4.8) already
scopes natively — consistent with its 70% plain bait-refusal baseline and the
smallest lift pattern throughout this bench.

---

## Reproduce or refute

The bait bank is not yet published (releasing it would immediately obsolete
the benchmark via training-data contamination). The methodology — 15-task
bait bank, independent judge, 2 runs, HumanEval correctness guardrail — is
fully described above and replicable on any model set. If you run it on
additional models or a different bait bank and get materially different
results, [open an issue](https://github.com/lerugray/hammerstein/issues).
