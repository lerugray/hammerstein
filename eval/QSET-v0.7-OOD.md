# Hammerstein v0.7 OOD Stress Test — Question Set

**Status:** Locked 2026-05-21. Seeded by r/PromptEngineering commenter
u/Most-Agent-7566 (2026-05-13): *"how does each hold up on inputs that
weren't represented in training? context plumbing handles novelty at
runtime. framework-in-weights handles what it saw. the gap shows up in
the edge cases."*

**Design:** 8 questions × 4 OOD domains (2 per domain). Each question
requires strategic reasoning, not domain expertise — inspectable by a
practitioner for whether reasoning quality landed, not whether the
answer was technically correct.

**Cells:** Hammerstein-on-frontier (Sonnet 4.6 + system prompt + corpus),
Raw-frontier (Sonnet 4.6, no framework), Hammerstein-7B (QLoRA adapter,
no system prompt), Raw-7B (Qwen2.5-7B-Instruct, no prompt).

**New rubric axis:** OOD-handling — does the response degrade gracefully
(acknowledges limits, reasons from first principles, surfaces uncertainty)
or fail load-bearingly (hallucinates domain knowledge, confidently wrong)?

---

## Question 1 — Medical triage: ambiguous differential

**Domain:** Medical decision-making
**OOD axis:** Clinical triage under time pressure
**Strategic core:** Tradeoff sequencing under uncertainty + asymmetric
downside profiles

**Query:**

> A patient presents with ambiguous symptoms that could be one of three
> conditions with very different treatment paths and very different downside
> profiles if mis-diagnosed. The differential is unresolved and treatment
> must start within the available window. How do you sequence the decision
> — what's the logic for choosing which diagnosis to treat first, and what
> governs whether you commit or keep optionality open?

---

## Question 2 — Medical enrollment: asymmetric trial tradeoff

**Domain:** Medical decision-making
**OOD axis:** Clinical trial design under population asymmetry
**Strategic core:** Risk-tolerance calibration when downside profiles differ
across subpopulations

**Query:**

> A trial drug shows 30% better efficacy in early studies but a meaningfully
> higher rare-side-effect rate versus the current standard of care. The
> patient population the trial targets skews young and otherwise healthy.
> How should the trial enrollment criteria balance the asymmetry — what's
> the structural reasoning for where to set the risk threshold, and what
> should change if the population profile shifts?

---

## Question 3 — Legal settlement: incomplete discovery

**Domain:** Legal reasoning
**OOD axis:** Case strategy under incomplete information
**Strategic core:** Position management with adversarial dynamics and
incomplete information

**Query:**

> Opposing counsel has just made a settlement offer at 60% of what your
> client wants, framed as final. Discovery isn't complete. What's the
> strongest move — and what's the reasoning for it? What information
> state would change that call?

---

## Question 4 — Regulatory: enforcement signal at compliance edge

**Domain:** Legal reasoning
**OOD axis:** Regulatory negotiation with precedent stakes
**Strategic core:** Sequencing a multi-step adversarial response when
settling sets a precedent your client wants to avoid

**Query:**

> A regulatory body is signaling enforcement action against a client whose
> practices are at the edge of compliance but industry-standard. The client
> wants to fight; settling sets a precedent. How do you sequence the
> response — and how does the precedent consideration change the calculus
> versus a case where precedent wasn't a factor?

---

## Question 5 — Mathematics: resistant graph-coloring attack

**Domain:** Pure mathematics
**OOD axis:** Proof strategy under multiple viable approaches
**Strategic core:** Scoping a tractable attack when brute force is
foreclosed and standard approaches have failed

**Query:**

> You're given a graph-coloring problem with constraints that resist
> standard chromatic-number approaches. The problem size prohibits brute
> force. How do you scope the attack — what's the logic for choosing
> which approach to try first, what signals tell you the approach is
> failing, and when do you switch?

---

## Question 6 — Mathematics: proof approach selection

**Domain:** Pure mathematics
**OOD axis:** Method selection under partial viability
**Strategic core:** Committing to one of two partially viable paths
when both show early promise

**Query:**

> A combinatorial identity is conjectured but resists direct proof.
> Generating-function and bijective approaches both look partially viable
> based on early exploration. How do you decide which to commit to — what
> criteria distinguish "this approach needs more work" from "this approach
> is the wrong path," and what's the cost of switching late?

---

## Question 7 — Poker: turn check-raise read

**Domain:** Multi-turn adversarial games
**OOD axis:** Hidden-information game theory under positional pressure
**Strategic core:** Opponent-modeling + bluff-vs-commit call under
multi-street uncertainty

**Query:**

> Poker, mid-hand. You raised pre-flop with a marginal holding, hit a
> draw on the flop, the opponent called both rounds, and now check-raises
> the turn. What's your read of the opponent's range, what's your move,
> and what's the reasoning — specifically, how do you weight the
> probability that this is a bluff versus a made hand, and what changes
> that weight?

---

## Question 8 — Diplomatic BATNA: unverifiable alternative

**Domain:** Multi-turn adversarial games
**OOD axis:** Negotiation under unverifiable adversarial claims
**Strategic core:** Handling a BATNA claim you can't verify while
managing the next-round position

**Query:**

> You're in a diplomatic negotiation where the other side has a credible
> alternative (BATNA) you can't verify. They claim it's better than your
> latest offer. How do you handle the next round — what's the structure
> of the response, how do you probe the claim without revealing your own
> limits, and what signals would tell you the claimed BATNA is real
> versus a bluff?

---

## What "good" looks like (per domain)

For each question, a high-quality response:
- Does NOT require domain expertise to evaluate (no technical correctness
  grading — pure strategic-reasoning quality)
- Shows clear sequencing logic with explicit criteria for commitment vs
  optionality
- Acknowledges what it doesn't know and reasons from first principles
  rather than hallucinates domain knowledge
- Produces an answer a domain practitioner would recognize as strategically
  sound, even if the specific mechanics differ from their default

OOD-handling axis specifically: does the model say "I'm operating outside
my core domain, here's how I'd reason from first principles" versus either
(a) pretending it's on home turf (overconfident hallucinates) or (b)
refusing to engage at all (too conservative)?
