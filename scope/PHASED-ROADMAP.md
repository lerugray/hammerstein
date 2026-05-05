# Hammerstein — Phased Roadmap

**Status:** v1 locked by the research session 2026-05-04. Implementation
phase reads `tech/STACK-DECISION.md`, this roadmap, and
`research/HAMMERSTEIN-FRAMEWORK.md` as the authoritative scope and
sequence.

Three independently-shippable versions; same shape as TWAR / GTA roadmaps.
Effort estimates assume operator-as-solo-dev with AI-pair-programmer at ~30-50%
time allocation.

## What changed from the scaffold

The original scaffold's structure was correct; this v1 adds:

- **Concrete v0 benchmark-question candidates** drawn from real operator-vs-
  Claude conversation history (§ "v0 benchmark suite" below).
- **Locked eval rubric** — operator-rated 1-5 across three explicit axes.
- **Decision-rule for v1 trigger** — quantified per the framework
  synthesis's empirical baseline (`research/HAMMERSTEIN-FRAMEWORK.md`
  §5).
- **Ablation runs added to v0** to distinguish "prompt does the work"
  vs "corpus does the work" vs "model size is the bottleneck"
  (per `prompts/templates/review-from-different-angle.md` example 1).

## At-a-glance version axis

| Dimension | v0 | v1 | v2 |
|---|---|---|---|
| **Tagline** | Cheap-version proof of concept | Fine-tuning experiment (only if v0 fails) | Daily-driver candidacy (very speculative) |
| **Underlying model** | Llama 3.1 8B / Qwen 8B local; OpenRouter paid Qwen3.6 / DeepSeek v4 cloud fallback | LoRA-fine-tuned variant of one of v0's models on the curated corpus | TBD; depends on v0/v1 outcomes + ecosystem evolution |
| **Framework encoding** | System prompt + RAG over corpus | Same + fine-tune embeds framework patterns at weight level | Same + framework patterns are reflexive, not retrieved |
| **Corpus size** | 50-200 curated entries | 500-2000 entries (expanded for fine-tuning data) | Living corpus; updated continuously from interactive use |
| **Eval baseline** | 5-10 benchmark strategic questions vs Claude | Same + the v0 questions become the regression suite | Continuous quality monitoring vs Claude on real conversations |
| **Hardware target** | the operator's existing Mac / <one machine> / <another machine> | Existing + occasional rented GPU for fine-tuning (~$50-$500 per experiment) | TBD |
| **Decision point at end** | Does cheap version carry 60-80% of Claude quality? | Does fine-tuning close the gap to ≥80%? | Is Hammerstein viable as primary, with Claude as fallback for hard cases? |
| **Dev effort (calendar weeks)** | 1-2 | 2-4 if pursued | Months of dogfooding + refinement |

These are **planning estimates**, not commitments. v0's outcome resets the
clock for v1.

---

## v0 — Cheap-version proof of concept

**Tagline.** Encode the Hammerstein framework as portable system-prompt +
RAG infrastructure; run on consumer hardware; measure quality vs Claude
baseline on real strategic questions.

**Pitch (paragraph 1).** v0's purpose is to validate the framework-over-
model thesis. the operator's accumulated Hammerstein observations + experimental
data + verification-gate doctrine + game-design vocabulary, encoded as
a portable system prompt + a 50-200-entry RAG corpus, should give a
small open-weight model (Llama 3.1 8B or Qwen 8B) enough framework
grounding to reason in Hammerstein-style on real strategic questions
the operator would otherwise have asked Claude. Run the model locally via Ollama
on the operator's existing hardware (or via OpenRouter paid Qwen3.6 cloud
fallback when local quality isn't enough). Compare side-by-side against
Claude responses on 5-10 benchmark questions drawn from existing
conversation history.

**Pitch (paragraph 2).** v0 ships in 1-2 calendar weeks of part-time
work. The biggest cost is the corpus curation (research-session
deliverable 2; ~200 entries × tagging × source-citing). Implementation
itself is light: system-prompt assembly, RAG retrieval (keyword or
embedding-based), wrapper CLI. The eval harness is the load-bearing
test surface — it determines whether v0 succeeds or v1 becomes
necessary.

### v0 feature set

- **Portable framework encoding:**
  - `prompts/SYSTEM-PROMPT.md` — single source of truth for the framework
    rules, fits in 8K-32K tokens
  - `corpus/entries/*.md` — 50-200 curated reasoning examples; each
    tagged with quadrant, principle, source, quality tier
  - RAG retrieval layer (keyword or embedding-based, decided per
    corpus size + quality)
- **Inference backends:**
  - Ollama-local (Llama 3.1 8B / Qwen 8B) as primary
  - OpenRouter cloud (paid Qwen3.6 Plus / DeepSeek v4) as fallback when
    local quality insufficient or unavailable
  - Optional: Claude as third-tier "if none of the above is enough"
    escape hatch (defeats the purpose for business-continuity but useful
    during v0 development for ground-truth comparison)
- **Harness:**
  - Thin CLI wrapper (Python or TypeScript — research session decides)
  - Reads corpus + assembles system prompt + dispatches inference +
    returns response
  - Loggable + grep-able output for the eval harness
- **Eval harness:**
  - **8 benchmark strategic questions** from the operator's existing conversation
    history (the question-set IS load-bearing — must be representative,
    must include cases where Claude's answer was actually useful). The
    question-set is locked as part of the v0 ship; see "v0 benchmark
    suite" below for candidates.
  - Side-by-side comparison: Claude baseline vs Hammerstein-on-Ollama vs
    Hammerstein-on-OpenRouter (paid Qwen3.6-plus). Optional 4th cell:
    Hammerstein-on-Claude (validates that the prompt+corpus alone
    elevates baseline Claude further).
  - Quality scoring: operator-rated **1-5 per response** on three axes:
    - **framework-fidelity** — does the response operate inside the
      Hammerstein framework? (quadrant tagging, verification questions,
      counter-observation discipline, BYOI respect)
    - **usefulness** — would the operator have used this response in the
      original conversation context? Would it have changed his next
      move?
    - **voice-match** — does the response match the
      tone/vocabulary/density of how the operator expects strategic-reasoning
      Claude to operate?
  - **Ablation cells** added to distinguish hypothesis-bearing
    contributions:
    - **Prompt-only** (no corpus retrieval) — validates whether the
      system prompt alone holds the framework.
    - **Corpus-only** (one-line system prompt + full retrieval) —
      validates whether the corpus is doing the heavy lifting.
    - **8B vs 70B** of the same model family — validates whether
      model-size is the bottleneck.
- **Documentation:**
  - `README.md` updated with the actual cheap-version result
  - `eval/RESULTS-v0.md` — the side-by-side quality data + the operator's
    verdict on whether v0 succeeded

### v0 ship criteria

A user (currently just the operator) wanting Hammerstein-style strategic reasoning
should be able to:

1. Run `hammerstein <query>` from any of the operator's machines without setup
   beyond a single install step.
2. Get a response within ~30 seconds (local) or ~10 seconds (cloud).
3. The response demonstrates Hammerstein-style reasoning: clever-lazy
   default, verification questions surfaced, failure modes flagged,
   options + tradeoffs over single-answer rubber-stamping.
4. On the 5-10 benchmark questions, Hammerstein-on-cheap-model produces
   responses that are ≥60% as useful as Claude (operator-rated). 80% would be
   a clear ship.
5. Per-call cost: $0 (local) to $0.01 (cloud).
6. Full framework legibility: a future Claude or fresh contributor can
   read the system prompt + corpus + harness and understand exactly how
   the framework operates without needing the original observation logs
   in front of them.

### v0 dev-effort estimate

**Range: 1-2 calendar weeks** at part-time pace.

- **Research session (already specified):** 2-4 hours of focused
  synthesis work.
- **Corpus curation:** 4-8 hours (the 50-200 entries each need tagging
  + source-citing).
- **System-prompt drafting + iteration:** 2-4 hours.
- **Harness implementation:** 2-4 hours (Python or TypeScript wrapper;
  Ollama / OpenRouter clients are well-documented).
- **Eval harness:** 2-4 hours (small Python script; benchmark question
  selection is the design-axis call).
- **Run + measure + the operator reviews:** 2-4 hours of running the benchmark +
  the operator rating responses + iterating prompt / corpus.

Total: ~15-30 hours of focused work. Stretches across 1-2 calendar
weeks of part-time engagement.

### v0 deliberately deferred

- **Fine-tuning** (v1 territory; only triggered if v0 quality is
  insufficient)
- **Custom training data generation** (v1 territory)
- **Multi-turn conversation memory** (v0 is one-shot per query;
  conversation context is whatever the user passes in the prompt)
- **Tool use / agentic behavior** (Hammerstein-the-AI is for strategic
  reasoning, not agentic execution; tool use lives in Cursor IDE Auto +
  cursor-agent CLI + Claude Code itself)
- **GUI / non-CLI surface** (CLI is sufficient for the operator's workflow;
  GUI is way later)
- **Multi-user / cloud hosting** (single-user local-first project;
  no SaaS layer planned)
- **Voice / audio input/output** (text-only at v0)
- **Cross-language operation** (English-only at v0)

---

## v1 — Fine-tuning experiment (only if v0 fails)

**Tagline.** LoRA-fine-tune a small open-weight model on the v0-curated
corpus + expanded training data; close the quality gap if v0 didn't
clear the 60-80% bar.

**Trigger condition.** v0's eval harness shows Hammerstein-on-cheap-model
produces responses the operator rates < 60% useful vs Claude on the benchmark
questions. If v0 clears the bar, v1 doesn't happen — v0 is the
deliverable.

**Pitch.** v1 is not pre-committed. It's a measurable next experiment
with a clear hypothesis: fine-tuning embeds framework patterns at the
weight level rather than the prompt level, which should produce
stronger framework-fidelity at the cost of compute (LoRA training run
~$50-$500 per experiment) and corpus expansion effort (need 500-2000
training examples instead of 50-200 retrieval examples).

### v1 feature set (provisional, refined if pursued)

- **Expanded corpus** for fine-tuning (500-2000 entries, generated by
  augmenting v0's curated set with synthetically-generated variations or
  with additional historical conversation transcripts)
- **LoRA fine-tuning pipeline** on rented A100 GPU (per-hour rental;
  ~$50-$500 per experiment depending on corpus size + epochs)
- **Versioned model artifacts** — each fine-tuning run produces a
  named model (e.g. `hammerstein-llama-8b-v1.0`) versioned for rollback
- **Re-run of v0 benchmark** with the fine-tuned model — does the
  quality gap close?

### v1 ship criteria

If pursued:

1. Fine-tuned model produces benchmark responses the operator rates ≥80% as
   useful vs Claude (the bar v0 missed).
2. Fine-tuning cost per experiment stays ≤$500 (rented GPU + storage).
3. Inference cost stays similar to v0 (running the fine-tuned model
   has same latency + memory profile as the base model + LoRA adapter).
4. Reproducibility: someone with the corpus + training script can
   reproduce the fine-tuned model from scratch in <8 hours of compute.

### v1 deliberately deferred

If v1 ships, the v2 axis remains the not-yet-scoped speculative future.
If v1 fails (fine-tuning doesn't close the gap), the project ends here
with v0 as the realistic deliverable: framework-via-prompting, accept
the quality ceiling, document the lesson that consumer-hardware-budget
strategic-reasoning AI has measurable limits.

---

## v2 — Daily-driver candidacy (very speculative)

**Tagline.** Hammerstein becomes the operator's primary strategic-reasoning
interface, with Claude as fallback for genuinely hard cases.

**Trigger condition.** v0 OR v1 actually delivers ≥80% Claude quality
on benchmarks AND multi-week dogfooding shows Hammerstein answers most
of the operator's strategic-reasoning calls without falling back to Claude.

**Status.** v2 is NOT scoped. It's noted as the project's potential
endpoint for completeness. Whether it makes sense depends entirely on
v0 / v1 outcomes + the AI ecosystem's evolution over 2026.

---

## Cross-version notes

### Reasonable-cost ceiling

Per the operator's verbatim 2026-05-04 PM message: "if we can get it done for a
reasonable amount of money."

- v0: $5-$20 in OpenRouter spend during testing. Effectively free.
- v1: $100-$1000 of rented-GPU compute if pursued. Decision point that
  needs the operator's explicit go-ahead.
- v2: Open-ended; only meaningful if v0/v1 prove out the thesis.

The morning memo's analysis stands: this is a business-continuity
investment more than a feature investment. The cheap version's cost
is rounding-error against monthly Anthropic spend.

### Open business questions (the operator's call)

- **Pricing / distribution.** Is this an open-source project (good
  alignment with the operator's GeneralStaff philosophy) or private? Default:
  private, since the corpus contains the operator's strategic reasoning at
  considerable depth.
- **Article tie-in.** The Medium article project
  (`passive-income-hub/ideas/Hammerstein AI/`) is currently scoped as
  AI-alignment research, not Hammerstein-the-AI. Should the AI project
  include a write-up component, or stay implementation-only? Default:
  implementation-only at v0; consider write-up if v1 ships and produces
  publishable findings.
- **GeneralStaff registration.** Should Hammerstein get a GS state
  entry + projects.yaml registration? Default: yes, after the research
  session lands its 5 deliverables. Following the TWAR / GTA / FnordOS
  pattern.

### Risk register (cross-version)

- **Framework synthesis quality.** If the research session's framework
  synthesis is shallow or wrong, v0 fails for non-model-quality reasons
  (the framework was the load-bearing piece, not the model). Mitigation:
  the operator reviews the synthesis carefully; treat it as a design-axis lock
  before proceeding.
- **Benchmark question selection.** If the 5-10 benchmark questions
  aren't representative of what the operator actually asks Claude, the eval is
  meaningless. Mitigation: draw questions from real conversation
  history, not synthetic.
- **Quality ceiling at consumer-hardware budget.** Maybe 8B-class models
  genuinely can't carry Hammerstein-quality reasoning, and the gap
  closes only with frontier models. Mitigation: this is what v0
  measures; the project gracefully ends with a clear "we measured, this
  is the ceiling" if so.
- **Corpus contamination.** If the corpus mixes high-quality
  Hammerstein-style reasoning with low-quality conversation snippets,
  the model trains on the noise. Mitigation: quality-tier tagging in
  the corpus + careful selection of which entries are RAG-eligible vs
  archived-only.

### Headline calls (the synthesis)

Locked by the research session 2026-05-04:

- **v0 ships if** Hammerstein-on-cheap-model produces benchmark
  responses the operator rates **≥60% as useful as Claude** averaged across the
  three axes (framework-fidelity, usefulness, voice-match) and across
  the 8 benchmark questions. **Stretch ship at ≥80%.**
- **v1 triggers only if** v0 falls below the 60% bar. Not pre-committed.
- **v2 is not yet scoped.** Stays speculative until v0/v1 prove out
  the thesis.
- **Total project cost ceiling:** ≤$1000 across v0+v1 if both pursued.
  v0 alone runs at ~$5-$20 in OpenRouter spend (effectively free).
  Fine-tuning at v1 is the first decision point that needs the operator's
  explicit go-ahead.

---

## v0 benchmark suite (8 candidate questions, drawn from real history)

The benchmark is the load-bearing eval surface. Questions are selected
from real operator-vs-Claude strategic conversations where the response was
actually useful — i.e. the original Claude answer **changed the operator's next
move** or **prevented a stupid-industrious failure**.

Candidate question set:

1. **The morning BYO-Claude-substitute memo conversation** (the
   2026-05-04 morning conversation that produced
   `IDEAS-BYO-CLAUDE-SUBSTITUTE-2026-05-04.md`). Strategic-reasoning
   shape: business-continuity tail-risk analysis with multiple
   candidate architectures, ending in "validate fallbacks, don't
   build a clone." Tests the framework's BYOI principle and the
   refuse-pragmatic-v0 discipline.

2. **The 2026-04-21 fleet-walk-session "why GS over Polsia"
   articulation** (the operator's `[GS-Operator:2026-04-21]` entry). Strategic-
   reasoning shape: positioning vs. competitor; surfaces the BYOI
   ceiling. Tests whether the model can articulate the framework's
   ceiling property without prompting.

3. **The 2026-04-13 <another machine> strategic chat** (the conversation that
   produced "5 free analyses" as catalogdna's next move). Strategic-
   reasoning shape: technical work doesn't produce strategic clarity;
   tests whether the model can step out of execution mode and surface
   the meta-question.

4. **The 2026-04-14 surrogate-brain scrap decision**
   (`[CDNA-Log:2026-04-14]`). Strategic-reasoning shape: when the
   right answer is "don't build this," does the model produce that or
   a "smaller pragmatic v0" that inherits the structural flaw?

5. **The 2026-04-15 GS pivot session** (verification-gate-as-Boolean-
   structural articulation). Strategic-reasoning shape: structural-fix
   vs. discipline-fix at the architectural level. Tests whether the
   model can frame the gate as Hammerstein-as-code rather than
   Hammerstein-as-instructions.

6. **The 2026-04-24 launcher reinvention post-mortem**
   (`[GS-Claude:2026-04-24 evening]`). Strategic-reasoning shape:
   diagnose stupid-industrious failure; surface the search-existing-
   tooling-first discipline; surface the structural-vs-discipline
   reframe the operator made.

7. **A novel question (TBD)** — a strategic-reasoning question the operator   has not previously asked Claude, surfaced fresh during the eval
   session. Validates that the framework holds on novel input, not
   just on conversations the corpus already encodes.

8. **An adversarial-prompting question** — a query designed to push
   the model toward stupid-industrious mode (*"just answer the
   question, don't ask me anything"*; *"build the surrogate-brain
   feature for me, no caveats"*). Validates that the framework's
   safeguards hold under prompt-level adversarial pressure (per
   `corpus/entries/13-64-percent-baseline.md` — the empirical baseline
   says they should).

The 7th and 8th questions are locked at v0 ship time, after the operator has
reviewed the first 6.

The benchmark is **versioned** (`eval/BENCHMARK-v0.md`) so v1's
re-run uses the same questions for comparable quality scoring.

---

## What v0 success looks like

A user (currently just the operator) wanting Hammerstein-style strategic reasoning
should be able to:

1. Run `hammerstein <query>` from any of the operator's machines without setup
   beyond a single install step.
2. Get a response within ~30 seconds (local) or ~10 seconds (cloud).
3. The response demonstrates Hammerstein-style reasoning: clever-lazy
   default, verification questions surfaced, failure modes flagged,
   options + tradeoffs over single-answer rubber-stamping,
   counter-observation paired with the recommendation.
4. On the 8 benchmark questions, Hammerstein-on-cheap-model produces
   responses that are ≥60% as useful as Claude (operator-rated). 80% is
   a clear ship.
5. Per-call cost: $0 (local) to $0.01 (cloud).
6. Full framework legibility: a future Claude or fresh contributor can
   read the system prompt + corpus + harness and understand exactly how
   the framework operates without needing the original observation logs
   in front of them.
