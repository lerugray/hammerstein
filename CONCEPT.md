# Hammerstein — Concept Capture

**Captured:** 2026-05-04 (<one machine> workday session, late afternoon).
**Origin:** the operator's evening refinement of the morning's BYO-Claude-substitute
memo (`generalstaff/docs/internal/IDEAS-BYO-CLAUDE-SUBSTITUTE-2026-05-04.md`).

## Verbatim from the operator (2026-05-04 PM)

> "I want to explore a thread from earlier, I talked about with you at some
> point today my worry about losing or not being able to afford claude —
> previously I thought maybe designing an AI would be too difficult/out of
> the question, but I realized that things like virtual GPU and servers are
> available, wondering if we could maybe get away with developing our own
> purpose driven Hammerstein AI (with a CC similar harness) just for strategic
> thinking, code could still be routed through providers via openrouter — but
> I think a tightly scoped AI based on my hammerstein framework might maybe
> make sense if we can get it done for a reasonable amount of money — my
> dream would be for the AI itself to be lightweight and not require a ton
> of GPU to run locally — again im not a programmer or an AI researcher, so
> maybe this idea is too pie in the sky"

## The shape of the project

A **focused strategic-reasoning AI** that:

1. **Encodes the Hammerstein framework as portable infrastructure.** The
   framework — accumulated over catalogdna's 22+ bot runs, GeneralStaff's
   first build session, retrogaze observations, the published Medium essay,
   the 5-experiment empirical validation, and ~40+ observation log entries —
   becomes the load-bearing artifact, not the underlying model.

2. **Runs on commodity hardware.** the operator's <one machine> (and his <another machine>, and his
   <one machine>) should all be able to run the strategic reasoner locally without
   needing dedicated GPU servers. This points to small open-weight models
   (Qwen 8B, Llama 3.1 8B-70B) via Ollama, or paid-cheap routing via
   OpenRouter when local inference isn't enough.

3. **Stays scoped to strategic thinking.** Code generation continues to route
   through OpenRouter Qwen Coder Plus or Cursor IDE Auto. Hammerstein
   handles: scope decisions, voice/aesthetic judgment, "what should we do
   next" framing, "is this worth doing" analysis, "where's the failure mode"
   surfacing — the staff-officer / orchestrator work that an interactive
   Claude session currently does.

4. **Closes the business-continuity gap.** The morning memo concluded that
   if Claude vanished tomorrow, code work survives via cursor-agent CLI +
   OpenRouter + Gemini CLI + Ollama. The gap was the strategic-reasoning
   layer — the kind of conversation that produced this concept itself.
   Hammerstein closes that gap by being the strategic-reasoning fallback.

## What "lightweight, runs locally" means in practice

The realistic stack:

- **Local inference via Ollama** for an 8B-class open-weight model on
  the operator's existing hardware. Llama 3.1 8B works on a 16GB RAM Mac; Qwen 8B
  has stronger reasoning. Cold-start latency ~5-15s on M-series Mac.
- **OpenRouter as the cloud fallback** when local inference isn't strong
  enough — paid Qwen3 80B / Qwen3.6-plus / DeepSeek v4 are all already
  configured in the operator's Routwizard rules. Per-call cost: $0.001-$0.01.
- **The Hammerstein framework as system prompt + RAG** loaded on every
  call. The framework is the value-add, not the model.
- **A minimal Claude-Code-shaped harness** — terminal app that takes a
  prompt, retrieves relevant Hammerstein corpus entries, builds the
  system prompt, dispatches to Ollama or OpenRouter, returns the
  response. Modeled on cursor-agent CLI + Aider but stripped to the operator's
  workflow.

The harness is the smallest piece. The corpus + system prompt are the
load-bearing pieces.

## Why "tightly scoped" matters

A general-purpose AI replacing Claude across all of the operator's portfolio is the
ambitious version the operator correctly identifies as "pie in the sky." A
narrow-purpose AI for strategic reasoning specifically is the achievable
version because:

1. **The corpus is finite.** Strategic-reasoning examples from the operator's
   accumulated observation logs + conversation transcripts are bounded —
   maybe 50-200 high-quality examples. That fits in a small RAG store.

2. **The framework is well-articulated.** Hammerstein quadrants +
   verification-gate pattern + clever-lazy doctrine + game-design framing
   are ALREADY documented across multiple files in the operator's projects. The
   research synthesis lifts what already exists rather than inventing.

3. **The success criterion is measurable.** Hammerstein-style strategic
   reasoning has identifiable signatures (questions surfaced, failure modes
   flagged, alternatives surveyed, recommendation with main tradeoff). The
   eval harness can compare model outputs against Claude baseline outputs
   on real strategic questions the operator's already asked.

4. **The fallback condition is binary.** Either Hammerstein-on-cheap-model
   carries the strategic load (60-80% Claude quality is enough; the
   framework does the heavy lifting), or it doesn't. If yes, business
   continuity is solved. If no, fine-tuning becomes a measurable next
   experiment with a clear gap to close.

## Editorial frame

Hammerstein is **the framework given autonomy** — not an AI built from
scratch. The framework already operates today (catalogdna's bot runs,
GeneralStaff's verification gate, the 5-experiment validation, the operator's
conversation patterns). What's missing is the framework operating
**without Claude as the substrate** — the framework continuing to function
even if the underlying model is Llama 3.1 8B running offline on a
laptop.

The naming reflects this. Hammerstein-Equord didn't BUILD the German
General Staff. He worked WITHIN it, applied its doctrine, recognized its
failure modes (industrious mediocrity is more dangerous than honest
incompetence), and tried to preserve it under adversarial pressure
(rejecting Hitler's strategic ambitions). The project's namesake is not
incidental — Hammerstein-the-AI is the framework continuing to function
under adversarial pressure (Anthropic outage, account ban, affordability
collapse), the same way Hammerstein-the-officer tried to preserve doctrine
through political adversity.

## What the project is NOT (recap from README)

- Not a Claude Code clone (3-6 month build that doesn't pencil)
- Not a from-scratch foundation model ($10M-$100M+ pre-training)
- Not a daily-driver replacement for Claude — yet
- Not a "build it tonight" tactical task — this is research-first, mirrored
  on the TWAR / GTA pattern

## Open questions for the research session

(See `RESEARCH-SESSION-BRIEF.md` for the formal list. Headlines:)

1. **What's the canonical Hammerstein corpus?** Which observation logs,
   conversation transcripts, and decision artifacts are the highest-density
   source material?
2. **What's the minimum viable system prompt?** What can fit in 8K-32K
   tokens of context that captures the framework's load-bearing rules
   without bloating every call?
3. **What's the right RAG retrieval pattern?** Per-query embedding lookup
   into the corpus? Or static framework + per-query examples?
4. **What's the eval baseline?** Which 5-10 real strategic questions from
   the operator's existing conversation history are the right benchmark suite?
5. **What's the local-vs-cloud routing?** When does Ollama-local serve;
   when does OpenRouter-paid take over; when does the system fall back to
   Claude (when available)?

## What "reasonable amount of money" looks like

Per my response to the operator's question (this conversation, <one machine> PM):

- **Cheap-version experiment (research + scaffold + first eval):** ~$5-$20
  in OpenRouter spend over a week of testing. Uses existing infrastructure;
  ships in a couple of focused sessions.
- **Fine-tuning experiment (only if cheap version proves insufficient):**
  ~$100-$1000 of rented-GPU compute for LoRA fine-tuning a small
  open-weight model. Ongoing $20-$200/month if iterating.
- **Hard ceiling the operator approves before scoping bigger:** TBD. The cheap
  version's cost is rounding-error against monthly Anthropic spend; no
  approval friction. Fine-tuning is the first decision point that needs
  the operator's explicit go-ahead.

The morning memo's analysis still holds: business-continuity discipline is
the higher-leverage move than building infrastructure. Hammerstein delivers
business-continuity AS the side effect of encoding the framework portably.

## Next step

**Research session** — see `RESEARCH-SESSION-BRIEF.md`. After research
deliverables land + the operator reviews, an implementation session starts.
Expected research scope: 1-2 focused sessions (2-4 hours each) to consume
~40 observation entries + the experimental data + the published essay
draft + the cross-project framework patterns, distill them into the 5
deliverables, and lock the v0 scope.
