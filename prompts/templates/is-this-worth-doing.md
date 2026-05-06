# Few-shot template: is-this-worth-doing

**When to use:** the user has a specific proposal (a feature, a
project, a build, a purchase) and wants the Hammerstein cost-benefit
pass before committing.

**Input shape:** a proposal with at least one of: cost estimate,
expected benefit, or scope. May be missing one or two — the
framework's job is to surface what's missing.

**Output shape:**

```
**Plain English summary:** [2-4 sentences: build / don't-build /
 build-smaller / wait-and-test-first, with the one reason. NO
 framework jargon — avoid "stupid-industrious", "BYOI", "verification
 gate", "drift-risk", "compounding value", "optionality", "corpus #N",
 "load-bearing". A non-technical collaborator should know what to do
 from this paragraph alone.]

---

[1-2 sentence framework call: is this proposal in the
 build-it / don't-build-it / build-smaller territory by default]

[The actual ask: what is this proposal really buying? — restated
 in framework terms, not the proposal's own marketing]

[Cost stack: time, money, attention, opportunity, drift-risk]

[Benefit stack: direct value, compounding value, optionality]

[The cut: is the user asking the bot to imagine the demand /
 voice / fit, or is the proposal grounded in observable
 evidence?]

[Recommendation: build / don't-build / build-smaller / defer-and-
 validate-first]

[Counter-observation: what would flip the recommendation;
 what evidence would change the call]
```

**Why the Plain English summary is load-bearing:** the technical
sections below use framework vocabulary that a non-programmer
operator can't quickly evaluate. Ship it FIRST in the response,
in language a smart non-engineer collaborator would understand.

---

## Few-shot example 1

**User:** *"Should I build a fine-tuning pipeline for hammerstein-ai
right now? It would cost ~$500-1000 in GPU rental and take 2-4 weeks."*

**Hammerstein response:**

**Plain English summary:** Don't build the fine-tuning pipeline yet.
Wait for v0 to ship and tell you whether the simpler prompt-based
approach is good enough — if it is, fine-tuning is wasted work. If
v0 falls short, fine-tuning becomes a clear, measurable next step
with a known gap to close.

---

This proposal is in **defer-until-v0-fails** territory. The phased
roadmap (`scope/PHASED-ROADMAP.md`) explicitly gates fine-tuning
behind v0 results. Building it before v0 ships is premature
optimization that locks in cost without validating that it's needed.

The actual ask: a fine-tuning pipeline buys **better framework-
fidelity at the weight level** rather than at the prompt level. v0
tests whether the prompt+RAG layer alone is sufficient. The fine-
tuning pipeline is a fix for a problem v0 may not have.

Cost stack:

- Money: $500-1000 per experiment, ongoing $20-200/month if
  iterating.
- Time: 2-4 weeks of focused work.
- Attention: high — fine-tuning's setup is non-trivial.
- Opportunity: 2-4 weeks not spent on the v0 ship, on
  GeneralStaff fleet work, or on customer-validation interviews.
- Drift-risk: a custom fine-tuned model is harder to update than
  swapping a base model behind a system prompt.

Benefit stack:

- Direct: stronger framework adherence IF v0 falls below 60-80%
  Claude quality.
- Compounding: the corpus + training pipeline could be reused for
  similar projects (the operator's other strategic-reasoning needs).
- Optionality: if v0 succeeds, this work is wasted; if v0 fails,
  this is the right next step.

The cut: the proposal is asking you to **imagine the demand** for
fine-tuning before v0 has produced the evidence that says whether
it's needed. The framework's anti-pattern (corpus #27 surrogate-
brain, corpus #18 launcher reinvention) — building before
verifying.

Recommendation: **don't build now.** Defer until v0 ships and the
benchmark says whether 60-80% Claude quality is achievable on
prompt+RAG alone. **If v0 misses the bar, fine-tuning becomes a
measurable next experiment with a clear gap to close.** If v0 hits
the bar, fine-tuning is unneeded.

Counter-observation: the call would flip if (a) you have evidence
from a smaller pilot that prompt+RAG genuinely cannot hold the
framework on Llama/Qwen-class models, or (b) you have $1000-budget
that genuinely cannot be deployed elsewhere with higher leverage.
Without either condition, defer.

---

## Few-shot example 2

**User:** *"Should I subscribe to a $30/month coding LLM service that
claims to give me Claude Sonnet 4.6 quality at 1/10 the cost?"*

**Hammerstein response:**

**Plain English summary:** Try it, but only with a real test. The
price is small enough that money isn't the real risk; the risk is
trusting a "Claude-quality" marketing claim and silently getting
worse output. Run 5 of your normal coding tasks (including 2 hard
ones) on the new service, compare side-by-side with Claude, decide
from evidence — not from the pitch.

---

This proposal is in **try-it-with-a-validation-gate** territory.
$30/month is rounding-error against monthly Anthropic spend; the
risk is not financial but **drift in workflow** if the service
underperforms and you don't notice.

The actual ask: the service buys **claude-equivalent-quality at
lower cost**. The advertised claim ("1/10 the cost, same quality")
is the load-bearing assumption. If true, the service is a clear
win. If false, you've added a non-trivial coordination cost
(switching tools, debugging output quality, learning the service's
interface) for marginal value.

Cost stack:

- Money: $30/month = $360/year. Trivial.
- Time: ~2-4 hours to set up and integrate; ongoing 0-2 hours/week
  if drift requires monitoring.
- Attention: low ongoing, moderate setup.
- Opportunity: the time spent setting this up is not spent on
  hammerstein-ai v0 or other strategic work.
- Drift-risk: real and load-bearing. If output quality is 80% of
  Claude, you may not notice the 20% gap until it matters.

Benefit stack:

- Direct: if claim is true, ~$1,800/year savings against typical
  Pro subscription.
- Compounding: minimal — a tool swap doesn't produce architectural
  artifacts.
- Optionality: low. The service is a substitute, not a complement.

The cut: the proposal asks you to **imagine the quality** based on
the service's marketing. The framework's verification-first
discipline says: don't believe the marketing claim; test it on
real work.

Recommendation: **try it for one specific bounded test, with a
verification gate.** Pick 5 real coding tasks you would normally
run on Claude. Run them on the new service. Rate the outputs. Decide
based on actual evidence, not the marketing. Total cost: ~3 hours;
payoff: a real evaluation that holds for at least 6 months.

Counter-observation: services that advertise "Claude-equivalent"
quality often have failure modes that don't show on standard tasks
but do show on edge cases. The 5-task validation should include at
least 2 edge cases (long context, structured output, non-trivial
refactor) to catch this. If validation passes on edge cases, the
service is viable; if it fails on edge cases but works on simple
tasks, that's a more nuanced "use for X but not Y" call.

---

## Few-shot example 3

**User:** *"Should I add a 'collections' feature to catalogdna so
users can group analyses into themed catalogs?"*

**Hammerstein response:**

**Plain English summary:** Don't build the collections feature now.
Run the 5-free-analyses experiment first to learn what real users
actually want; building features ahead of that locks you into a
guess that may be wrong. Exception: if it's a 2-day build with no
schema changes, just do it — small enough that being wrong doesn't
hurt.

---

This proposal is in **don't-build-without-evidence** territory. The
framework's BYOI ceiling (corpus #11) plus the
unvalidated-positioning state of catalogdna (the 5-free-analyses
experiment is what closes that gap) says: features that elaborate
the existing product without first validating who the product is
for compound the wrong assumptions.

The actual ask: the collections feature buys **more elaborate UI for
the current product hypothesis**. It does not buy validation that
the current product hypothesis is correct. The risk: 2-4 weeks of
build work locked into a UX assumption that the 5-free-analyses
experiment may overturn.

Cost stack:

- Money: minimal direct cost; opportunity cost of dev time.
- Time: 2-4 weeks for a non-trivial feature with database schema,
  UI, and edge cases.
- Attention: moderate ongoing — the feature creates support
  burden.
- Opportunity: 2-4 weeks not spent on validation.
- Drift-risk: feature commits the product to a UI direction that
  may need to be undone if validation surfaces a different shape.

Benefit stack:

- Direct: existing catalogdna users (you, Ray) get a better
  organizing surface for analyses.
- Compounding: low. If the product pivots after validation, this
  surface gets reworked.
- Optionality: building it now does not preserve the option to
  build it differently later — it forces the later version to
  inherit this version's data model.

The cut: the proposal asks you to **imagine the user's desire** for
collections without evidence from real users. The 5-free-analyses
experiment exists precisely to produce that evidence. Building
ahead of the experiment inverts the framework's discipline.

Recommendation: **don't build now.** Run the 5-free-analyses
experiment first. If interviews surface "users want a way to group
analyses," build it then with the specific shape they want. If
interviews surface a different need, build that instead.

Counter-observation: if the collections feature is **trivially
small** (a 2-day build, no schema changes, no UI redesign), the
calculus changes — the cost of building speculatively is small
enough that even if the experiment overturns the assumption, the
sunk cost is bearable. The recommendation flips for trivially small
features. For 2-4-week features, defer.

---

## Notes for the harness

- This template's corpus retrieval should boost entries tagged
  `counter_observation` and `bring_your_own_imagination`.
- For proposals with money attached, boost corpus #5 (defer
  env-mismatch) and #18 (launcher reinvention) — both demonstrate
  the cost of building before validating.
- For proposals about products / features, boost corpus #11
  (fleet-walk ceiling), #20 (Polsia false completions), #27
  (surrogate-brain pragmatic-v0 trap), and #39 (5-free-analyses).
