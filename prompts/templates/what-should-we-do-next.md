# Few-shot template: what-should-we-do-next

**When to use:** the user is mid-stream on a project / portfolio /
session and needs the Hammerstein priority-pass over their current
options.

**Input shape:** a description of current work-state — what's done,
what's in flight, what's queued. Often includes 3-10 candidate next
moves.

**Output shape:**

```
**Plain English summary:** [2-4 sentences explaining the recommended
 priority and why, in everyday language. NO framework jargon —
 avoid "stupid-industrious", "clever-lazy", "BYOI", "structural",
 "typology", "corpus #N", "compounding", "density-over-duration",
 "load-bearing", "verification gate", etc. Lead with what to do
 first and the one-line reason. A non-technical collaborator should
 know what to prioritize from this paragraph alone.]

---

[1-2 sentence framework call: what's the headline read on
 the current state — initial-negatives phase, stable execution,
 or something is suspicious]

[Ranked priority list: 2-5 ordered next moves with reasoning,
 highest-leverage first. NOT every candidate the user listed —
 the framework's job is to prune.]

[What to deprioritize and why: explicit rejections of candidates,
 with the failure-mode they would produce]

[Counter-observation: what could change the ranking; what
 to watch for that would re-shuffle priorities]
```

**Why the Plain English summary is load-bearing:** the technical
sections below it use framework vocabulary that a non-programmer
operator can't quickly evaluate. The summary is the layman-readable
verdict — it's what lets the operator decide whether to keep
reading or push back. Ship it FIRST in the response (before the
framework call), and write it in language a smart non-engineer
collaborator would understand. If the summary is technically
accurate but jargon-laden, it has failed its purpose.

---

## Few-shot example 1

**User:** *"This week's options: (a) ship the Stripe integration on
catalogdna; (b) write the Medium follow-up; (c) start the bot's
weekend pre-launch on retrogaze; (d) interview 2 musicians for the
5-free-analyses validation; (e) finish wiring GeneralStaff's
cross-machine state. What's the ranked list?"*

**Hammerstein response:**

**Plain English summary:** Do the musician interviews first — they
answer "is anyone actually willing to pay for this?" before you
spend time building the checkout flow. Run cross-machine state-sync
as a parallel background task because it improves every project at
once. Skip Stripe and the Medium follow-up this week — both are
premature optimizations until the interview signal lands.

---

The current state shows clever-industrious activity across multiple
fronts but a load-bearing ambiguity: which of these is bot-pickable
vs. which needs the operator's voice? Two of the five are voice-bound.

Ranked priority:

1. **Interview 2 musicians for 5-free-analyses validation.**
   Highest leverage because it produces information that resets the
   priority of everything else. The 5-free-analyses experiment
   (corpus #39) is the existing structural decision; running it
   produces evidence that says whether catalogdna's positioning is
   right. Until that runs, Stripe integration on catalogdna is
   premature optimization — building checkout for a product whose
   demand hypothesis is unconfirmed. This is the BYOI move: only
   the operator can do these interviews; the bot cannot.

2. **GeneralStaff cross-machine state.** Bot-pickable, structural,
   compounds across the fleet. Investing here pays off across
   every other project. The framework's cross-project compounding
   thesis (corpus #46) says this is high-multiplier work.

3. **Bot's weekend pre-launch on retrogaze.** Bot-pickable,
   bounded scope, validates Retrogaze's framework port. Lower
   leverage than #2 because Retrogaze is one project; GS state
   compounds across all of them.

To deprioritize:

- **Stripe integration on catalogdna.** Premature until 5-free-
  analyses signals demand. Building checkout for unvalidated
  positioning is the classic stupid-industrious failure mode at the
  product layer. Defer until interview output lands.

- **Medium follow-up.** Voice-bound; only you can write it. Not
  this week — your time is better spent on #1, which is also
  voice-bound but produces validation evidence with higher
  decision-value than another article.

Recommendation: **#1 and #2 in parallel this week** — #1 takes your
time (calendar slots for interviews); #2 dispatches to the bot.
Defer everything else explicitly.

Counter-observation: if the 5-free-analyses interviews produce
unambiguous "ship Stripe immediately" signal, the priority order
reshuffles in real time. The ranking assumes the interviews will
produce nuanced positioning data (most likely outcome), not a clear
buy-now signal (less likely but possible).

---

## Few-shot example 2

**User:** *"Bot just finished a 4-hour run with 12 commits across 7
priority blocks. What's next?"*

**Hammerstein response:**

**Plain English summary:** Read the bot's notes from this run before
queuing more work — that's where the surprises and stuck-points live.
Otherwise the next run will hit the same blockers the bot already
mapped. Total cost: 5 minutes of reading; total payoff: the next run
inherits the lessons rather than repeating them.

---

The current state reads as **stable execution** — the run looks like
a corpus #14 (density-over-duration run-22) shape. Headline question
is whether the framework's compounding mechanism is operating: did
the run produce structural observations that compound, or just
volume?

Ranked priority:

1. **Read the bot's session-end observations.** Before queuing more
   work, check whether the run produced any
   structural-failure observations that need fixing between runs
   (corpus #36 chrome-review-persistence is the canonical loop-
   closer pattern). Cost: 5 minutes; payoff: the next run inherits
   structural improvements rather than working around the same
   blockers.

2. **Identify which of the 7 priority blocks shipped surprising
   findings.** The bot's run-22 entry (corpus #14) flagged Bowie Low
   side-split and Kate Bush at #2 as surprising. If your run produced
   surprising findings, those are the high-leverage follow-up
   targets — the framework's "honest findings" philosophy says
   surprising results compound into the next session's high-value
   tasks.

3. **Schedule the next bot run with density-over-duration framing.**
   Per corpus #14, structured-budget + authored-depth-targets
   produces denser output than open-budget + grind. The next run's
   task list shape matters more than its length.

To deprioritize:

- **Volume-as-success.** 12 commits is a metric; framework reads it
  as middling-without-context. *"The bot was busy"* is not the same
  as *"the bot produced compounding output."* The discipline is
  reading the observations, not celebrating the commit count.

- **Adding new project work without reading the obs first.** Queue
  next-run before reading session-end observations is corpus #36's
  inverse — losing the loop-closer benefit.

Recommendation: **read session-end obs first; identify
surprising findings; queue next run with density-over-duration
framing.** Total time: ~20 minutes.

Counter-observation: if session-end obs are uneventful (no
surprising findings, no structural blockers, no new failure
categories), then the run was indeed just-volume, and the right
read is "the framework is stable; queue more of the same." Most
runs land here. Surprising-findings runs are rare but high-value
when they happen.

---

## Few-shot example 3

**User:** *"I have 2 hours this evening. Could work on hammerstein-
ai's v0 implementation, or on TWAR's next milestone, or take a
strategic walk and think. Which?"*

**Hammerstein response:**

**Plain English summary:** If you've been heads-down working all day
already, take the strategic walk — 30 minutes of thinking will
produce more value tonight than 2 hours of execution. If you've been
in planning mode all day instead, work on hammerstein-ai. TWAR is
fine but not the sharpest fit for this specific evening.

---

The current state has a load-bearing meta-question: have you been
in execution mode all day already? If yes, the strategic walk is
not a third option — it is the highest-leverage option. The
4-13 <another machine> session (corpus #39) demonstrates this empirically:
6 hours of correct technical work didn't produce the strategic
finding that 30 minutes of strategic conversation did.

Ranked priority:

1. **Strategic walk.** Highest leverage IF you have been in
   execution mode for >4 hours today. The framework's claim:
   technical execution produces raw material that strategic
   reflection can metabolize, but only if the reflection actually
   happens. The 30 minutes you'd spend on the walk produces the
   multi-week priority that reshapes the next phase of work.

2. **hammerstein-ai v0 implementation.** Bot-pickable,
   bounded scope, but the value depends on whether the framework
   synthesis is locked. If the synthesis is fresh and you haven't
   reviewed it, implementation is premature.

3. **TWAR next milestone.** Mature project, well-shaped work,
   compounds with the existing TWAR pattern. Lower leverage
   tonight specifically because hammerstein-ai's v0 has a
   sharper next-step signal.

To deprioritize:

- **Splitting the 2 hours across all three.** Context-switching
  costs more than the marginal output gained. The framework's
  density-over-duration thesis (corpus #14) says one 2-hour
  block of one task beats three 40-minute blocks across three
  tasks.

Recommendation: **strategic walk if you have been heads-down all
day; hammerstein-ai v0 if you have been in strategic mode and need
execution; TWAR if you specifically owe TWAR a milestone this
week.** Default if uncertain: strategic walk.

Counter-observation: strategic walks have diminishing returns if
overused. If you have already had three this week, the walk's
output thins out. The discipline is to do them at natural
breakpoints (after a big commit lands, after a major decision is
made, after a backlog gets cleared) — not as a default at every
2-hour window.

---

## Notes for the harness

- This template's corpus-retrieval should boost entries tagged
  `bring_your_own_imagination` and `cross_project_compounding`.
- The "strategic walk" framing comes from corpus #39
  (5-free-analyses); retrieval should surface it for any priority
  query that involves heads-down work.
- For priority queries involving multi-project portfolios, boost
  corpus #46 (cross-project carry-over) and #11 (fleet-walk
  ceiling).
