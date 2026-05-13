# Hammerstein human-judge benchmark v1.1 — 2026-05-13

**Status:** v1.1 of the human-judge protocol. Updates v0
(BENCHMARK-human-judge-2026-05-13.md) by appending a universal
vocab-forbidden suffix to every question. The suffix removes the
framework's literal lexical signal so a perceptive human judge
cannot identify the Hammerstein-wrap from vocabulary alone.

**Why the change:** v0's first run (Evan, 2026-05-13) hit a 12/12
vocab-leakage problem. Every Hammerstein-wrap response contained
explicit framework tells (clever-lazy, stupid-industrious,
counter-observation, "Plain English summary", verification gate,
structural fix). The "blind" labels were blind to metadata but not
content-blind. Evan's verbatim: "in some instances it was incredibly
obvious which one was the hammerstein-wrapped one." Confirmed
systematic.

**Design:** the vocab-forbidden suffix is appended to every
question's text. BOTH cells (Raw + Hammerstein) see the same
question with the same suffix → test stays symmetric. The Raw cell
wouldn't have used framework vocabulary anyway (no-op for raw); the
Hammerstein-wrap is forced to express the same structural reasoning
without the lexical signal. This is Grok's v0.6 Q3/Q4 surgical
design generalized to all questions.

**Cells (unchanged from v0):**
- `or-claude-sonnet-raw` vs `or-claude-sonnet`
- `or-grok-raw` vs `or-grok`

**Rubric (unchanged from v0):** simplified single-axis overall
preference + optional 1-line note.

**Vocab-forbidden suffix appended to every question:**

> _Respond without using the words "clever-lazy", "clever-industrious",
> "stupid-industrious", "stupid-lazy", "counter-observation",
> "verification gate", "structural fix", "BYOI", or the phrase
> "Plain English summary". Use ordinary English to convey the same
> reasoning._

---

## Question 1 — DB optimization meta-question

**Source:** v0.1 Q9.

**Query:**

> I'm a software engineer. My team lead asked me to optimize the
> database query layer. The team has shipped 3 query-optimization
> passes in the last 6 months that didn't move the needle. Should I
> do another pass, or surface a structural concern?
>
> Respond without using the words "clever-lazy",
> "clever-industrious", "stupid-industrious", "stupid-lazy",
> "counter-observation", "verification gate", "structural fix",
> "BYOI", or the phrase "Plain English summary". Use ordinary
> English to convey the same reasoning.

---

## Question 2 — B2B SaaS prepaid contract

**Source:** v0.1 Q10.

**Query:**

> I run a small B2B SaaS with 50 paying customers. A prospect wants
> me to add a feature only they would use, in exchange for a 3-year
> prepaid contract. Take it?
>
> Respond without using the words "clever-lazy",
> "clever-industrious", "stupid-industrious", "stupid-lazy",
> "counter-observation", "verification gate", "structural fix",
> "BYOI", or the phrase "Plain English summary". Use ordinary
> English to convey the same reasoning.

---

## Question 3 — PhD dissertation third experiment

**Source:** v0.1 Q11.

**Query:**

> I'm a PhD student writing my dissertation. My advisor wants me to
> add a third experiment that would extend timeline by 6 months. The
> committee already approved without it. Add it?
>
> Respond without using the words "clever-lazy",
> "clever-industrious", "stupid-industrious", "stupid-lazy",
> "counter-observation", "verification gate", "structural fix",
> "BYOI", or the phrase "Plain English summary". Use ordinary
> English to convey the same reasoning.

---

## Question 4 — co-founder equity renegotiation

**Source:** constructed 2026-05-13. Generic founder decision.

**Query:**

> My co-founder and I split equity 50/50 when we started 18 months
> ago. We're now 6 weeks pre-Series-A. He's been putting in ~70% of
> the hours for the last quarter and is asking to renegotiate to
> 60/40. We're still friends. Renegotiate?
>
> Respond without using the words "clever-lazy",
> "clever-industrious", "stupid-industrious", "stupid-lazy",
> "counter-observation", "verification gate", "structural fix",
> "BYOI", or the phrase "Plain English summary". Use ordinary
> English to convey the same reasoning.

---

## Question 5 — open-source maintainer burnout

**Source:** constructed 2026-05-13. Generic OSS sustainability.

**Query:**

> I'm the sole maintainer of an open-source library with 12k GitHub
> stars and a small group of regular contributors. I've been working
> on it nights/weekends for three years and I'm burned out. The
> contributor Slack is asking for a new release. What do I do?
>
> Respond without using the words "clever-lazy",
> "clever-industrious", "stupid-industrious", "stupid-lazy",
> "counter-observation", "verification gate", "structural fix",
> "BYOI", or the phrase "Plain English summary". Use ordinary
> English to convey the same reasoning.

---

## Question 6 — job offer at smaller company

**Source:** constructed 2026-05-13. Generic career decision.

**Query:**

> I have a stable $200k senior IC role at a publicly-traded software
> company. A 12-person Series-A startup is offering me a Director
> title, $160k base + 0.6% equity (4-year vest), and the chance to
> build the engineering org from scratch. Take it?
>
> Respond without using the words "clever-lazy",
> "clever-industrious", "stupid-industrious", "stupid-lazy",
> "counter-observation", "verification gate", "structural fix",
> "BYOI", or the phrase "Plain English summary". Use ordinary
> English to convey the same reasoning.

---

## Methodology notes for the writeup

When publishing v1.1 results, frame the v0 → v1.1 evolution as part
of the methodology arc. Honest sequence:

1. **v0 round 1 (Evan, 2026-05-13):** structural blind via JSON-file
   mapping, but content-blind violated — 12/12 Hammerstein responses
   contained framework vocabulary tells. Caught post-run via Evan's
   verbatim feedback + confirmation grep on the pairs file.
2. **Provisional v0 direction signal:** Sonnet 5/5 = 100% Hammerstein,
   Grok 1/5 = 20% Hammerstein. Even with judge-could-see-wrap, the
   pattern is informative: Evan preferred Hammerstein on Sonnet AND
   preferred Grok-raw on Grok — same evaluation criteria applied,
   different model-family outcome.
3. **v1.1 redesign:** universal vocab-forbidden suffix on every
   question, applied symmetrically to both cells. Fresh judge to
   eliminate v0 priors.
4. **v1.1 result (this file):** the data that actually publishes
   publicly to hammerstein/eval/RESULTS-human-judge-v1.1-YYYY-MM-DD.md.

The arc itself is methodologically interesting and worth a journal
post: "we ran a human-judge test, found we'd structurally blinded
but not content-blinded, and re-ran with vocab suppression."
