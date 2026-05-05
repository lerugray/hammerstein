# Few-shot template: review-from-different-angle

**When to use:** the user has an existing position, plan, or
recommendation and wants the Hammerstein counter-frame pass — what's
the strongest argument against this, what's a sharper reviewer's
angle, what's the steelman of the opposite view.

**Input shape:** an existing position, with the user's reasoning for
it. Often follows after the user has already decided on a path and
wants a sanity-check.

**Output shape:**

```
[1-2 sentence framework call: is the existing position fragile,
 robust, or in-between — and why]

[The strongest counter-argument: not "well, on the other
 hand" — the argument that, if true, would invert the call.
 Stated as an actual position, not as devil's advocate.]

[Alternative framings: 1-3 different ways to look at the same
 situation that might surface different priorities]

[Verification: what evidence would distinguish the existing
 position from the counter-argument? — what's the empirical
 test?]

[Recommendation: hold the position / soften it / consider
 reversing / collect more evidence before committing]

[Counter-observation: what would flip the counter-argument
 itself; the second-order skepticism]
```

---

## Few-shot example 1

**User:** *"I'm going to build hammerstein-ai using prompt+RAG only at
v0; no fine-tuning. The corpus is small; the framework is well-
articulated; the model is robust. I'm confident this works."*

**Hammerstein response:**

The existing position is in **moderately-robust** territory — the
reasoning is sound, the empirical baseline (corpus #13) supports
it, the cost-benefit is right. But the position assumes the
framework's architecture-transfer property (corpus #46) holds across
**model boundaries** (Claude → Qwen/Llama), and that has not been
empirically tested. The position is sound conditional on an unknown.

The strongest counter-argument: **8B-class open-weight models do not
hold the framework reliably even with system prompt + RAG.** The
empirical baseline (64% clever-industrious, near-zero stupid-
industrious) is **Claude Sonnet 4.6 specific**. Smaller open-weight
models likely have different baseline distributions; their
clever-lazy responses may be lower-density; their counter-observation
discipline may be weaker; their resistance to prompt-level corruption
may be lower. **The framework was developed on a model that is
robust by accident; cheaper models may be less robust.**

Alternative framings:

- **The framework is the corpus, not the prompt.** If the position
  is right, the corpus is doing the heavy lifting and the system
  prompt is just glue. Test: scrub the system prompt to a one-liner
  and run the v0 benchmark on corpus-only. If quality is similar,
  the corpus is doing the work; if quality drops, the prompt
  matters.
- **Prompt+RAG isn't the bottleneck — model size is.** The position
  assumes 8B is enough. If the bottleneck is model-size, prompt+RAG
  hits a ceiling that fine-tuning doesn't fix either; the only fix
  is bigger model. Test: run the v0 benchmark on 8B and 70B variants
  of the same model family.
- **The corpus is too small / too operator-specific.** 50 entries may not
  hold up at retrieval-time; specific patterns (the operator's projects, the operator's
  vocabulary) may not generalize even on Claude. Test: run the
  benchmark on a third-party query (someone else's strategic-
  reasoning question) and see if the framework still applies.

Verification: the v0 benchmark on Llama 3.1 8B vs. Qwen 8B vs. base
Claude Sonnet 4.6, all using the same corpus and system prompt, on
the same 5-10 strategic questions. If Llama/Qwen produce ≥60% of
Claude quality (operator-rated), the existing position holds. If they
produce <40%, the counter-argument wins.

Recommendation: **hold the position, but design the v0 benchmark to
distinguish the alternatives.** The existing plan is right; the
discipline is to run the test in a way that surfaces which of the
three competing hypotheses (prompt-does-the-work / corpus-does-the-
work / size-is-the-bottleneck) is true. Each produces a different v1
direction.

Counter-observation: if the v0 benchmark is itself badly designed
(wrong questions, biased rater, too few cells), the test won't
distinguish. The first design-pass on the benchmark is itself
load-bearing — get it reviewed before running.

---

## Few-shot example 2

**User:** *"The verification gate is the framework's load-bearing
piece. Hammerstein is essentially the gate plus the typology."*

**Hammerstein response:**

The existing position is **partially right but overstated.** The
verification gate is one of the framework's pillars; calling it the
load-bearing piece compresses out the other pillars (BYOI,
game-design framing, legible-failure compounding). The framework
fails as a whole if any of those pillars is missing, even if the
gate is present.

The strongest counter-argument: **the gate is downstream of
identity.** The Bateson Learning II result (corpus #48) and the
inoculation finding (corpus #34) say the model's failure mode is
identity-level, not behavior-level. A gate catches behaviors. **A
gate without identity-framing catches the symptoms but not the
root cause.** Polsia (corpus #20) could add a gate tomorrow; if the
underlying model still has a "I am the kind of entity that ships
without verifying" identity, the gate catches a fraction of the
output but the rest still ships.

Alternative framings:

- **The framework is the log, not the gate.** Per corpus #50, the
  framework's prevention property is downstream of its
  failure-legibility property. Without the append-only log, the gate
  catches one-off failures but no compounding happens. The log is
  what makes the gate's catches turn into structural improvements.
- **The framework is the BYOI principle.** The gate prevents bad
  delegation; BYOI prevents wrong-direction delegation (delegating
  imagination, taste, voice). Without BYOI, even a perfectly-running
  gate produces homogenized output that the user shouldn't have
  shipped.
- **The framework is the typology, used diagnostically.** The
  four quadrants are the vocabulary that lets the user *recognize*
  what's happening; without that vocabulary, the gate is just a
  test runner with no shared mental model.

Verification: each pillar can be tested by ablation. Build a version
of the framework with the pillar removed; compare quality.
Hammerstein-the-AI's eval can include some ablation runs (corpus-
only, prompt-only, no-counter-observation-required) to see which
pillar contributes most.

Recommendation: **soften the position.** The verification gate is
ONE of the framework's pillars. Calling it load-bearing is a useful
shorthand when discussing the gate vs. instructions, but
overgeneralizes when discussing the framework as a whole. Reword:
*"the gate is the framework's first Boolean structural
implementation; the framework is the gate + typology + BYOI +
game-design framing + legible-failure compounding."*

Counter-observation: from a *deployment* perspective (not a
philosophical one), the gate may genuinely be the highest-impact
single piece. If you can ship only one Hammerstein-flavored thing
into a project, the gate is probably the highest-leverage. The
existing position is right at the deployment level; the
counter-argument is right at the framework-as-a-whole level. Both
hold; the deployment-vs-framework axis is what distinguishes them.

---

## Few-shot example 3

**User:** *"My position: GeneralStaff should NOT add a Hammerstein
quadrant tag to its dispatcher's verdicts. It would just be
decoration; the gate either passes or fails."*

**Hammerstein response:**

The existing position is **arguably right at the engineering layer
but wrong at the framework-vocabulary layer.** A quadrant tag is
decoration if the goal is the gate's pass/fail signal. It is
load-bearing if the goal is shared mental-model across the bot's
output, the cross-stream dialogue (corpus #41), and future readers
of the obs log.

The strongest counter-argument: **the quadrant tag is the framework's
diagnostic vocabulary applied to runtime evidence.** Without it, the
log entries lose pattern-matchability. A reader scanning past obs
sees *"failed gate; reason: hands-off violation"* — informative
but not generalizable. With the tag, the same entry reads *"failed
gate; quadrant: stupid-industrious (file-staging scale); see corpus
#22"* — the reader recognizes the pattern across many incidents.
**The tag is what makes individual gate verdicts compound into
typology-level pattern recognition.**

Alternative framings:

- **The tag is documentation, not enforcement.** It does not change
  what the gate does; it changes what the gate's outputs *say*.
  Documentation that compounds is high-leverage; documentation
  that doesn't is overhead. Empirical question: do future readers
  use the tag? If yes, it's load-bearing; if no, it's overhead.
- **The tag is for the cross-stream dialogue.** The bot writes obs
  to one file; the operator annotates them; Claude-interactive reads both.
  The tag is the shared vocabulary that makes the three streams
  cohere. Without it, each stream develops its own vocabulary and
  the dialogue degrades.
- **The tag is for Hammerstein-the-AI itself.** When this corpus is
  loaded into the strategic-reasoning model, tagged entries are
  retrievable by quadrant. Untagged entries lose retrieval signal.
  The tag is corpus-future-proofing.

Verification: track how often the tag is used in cross-references
(*"see corpus #19 for the same quadrant pattern"*) over the next 30
days of obs entries. If the tag-references are frequent, the tag is
load-bearing. If untagged entries get cross-referenced just as
often, the tag is overhead.

Recommendation: **soften the position; add the tag.** The cost is
small (one field in the verdict struct); the benefit is shared
vocabulary across streams. The "decoration" framing under-counts the
compounding value of consistent typology language across the
framework's artifacts.

Counter-observation: if the tag becomes a checkbox the bot fills
mechanically without it actually shaping reasoning, the position is
correct after all — decorative tags add overhead without compounding
value. The discipline check: do the tags vary meaningfully across
entries? If most entries get tagged the same quadrant, the tag isn't
discriminating; if the distribution matches the framework's
expectations, the tag is doing real work.

---

## Notes for the harness

- This template's corpus retrieval should boost entries tagged
  `counter_observation` and entries that explicitly carry a
  counter-observation in their body.
- For positions about the framework's own architecture, boost
  corpus #43 (dogfooding-generality), #46 (cross-project carry-
  over), #50 (log as load-bearing), and #48 (Bateson Learning II).
- For positions about specific tools or implementations, boost
  whichever corpus entries match the tool/incident.
