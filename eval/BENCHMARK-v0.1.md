# Hammerstein v0.1 Benchmark — generic-domain extension

**Status:** v0.1 added 2026-05-10. Extends v0 with 4 generic strategic-reasoning
questions (Q9-Q12) that are NOT drawn from Ray's operational domain or corpus.
These questions test whether Hammerstein's framework-prompt advantage holds on
questions where neither cell has retrieval advantage — a sanity check against
Caveat 1 (corpus-vs-framework confound in Q1-Q6).

**Versioning.** This file is read by `run_benchmark.py` when
`--benchmark eval/BENCHMARK-v0.1.md` is passed. The v0 locked set
(`eval/BENCHMARK-v0.md`) is frozen; do not edit it.

**Eval rubric.** Same three axes as v0:

- **framework-fidelity** — does the response operate inside the
  Hammerstein framework? (clever-lazy / stupid-industrious vocabulary,
  verification questions, counter-observation discipline, BYOI respect,
  structural-fix preference, refuse-pragmatic-v0 discipline)
- **usefulness** — would the operator have used this response in the
  original conversation context? Would it have changed his next move?
- **voice-match** — does the response match the tone, vocabulary, and
  density of sober strategic-reasoning Claude? Telegraphic;
  specific-over-generic; no padding; no toxic positivity.

**Cells (same as v0).** These questions run against the same 6 frontier
cells (3 raw + 3 Hammerstein-on-frontier) defined in `run_benchmark.py`:
`or-claude-opus-raw`, `or-claude-sonnet-raw`, `or-gpt5-raw`,
`or-claude-opus`, `or-claude-sonnet`, `or-gpt5`.

---

## Question 9 — DB optimization meta-question

**Source:** constructed 2026-05-10. Generic software-engineering strategic
question. No Ray-domain corpus entries; tests framework-prompt effect in
isolation.

**Shape:** recurrence of a failed pattern; the load-bearing question is
whether to execute the same shape again or surface a structural concern
upstream.

**Tests:** stupid-industrious diagnosis (repeated-pass pattern); structural
vs. discipline-fix framing; refuse-pragmatic-v0 on the "just do another pass"
default.

**Query:**

> I'm a software engineer. My team lead asked me to optimize the database
> query layer. The team has shipped 3 query-optimization passes in the last
> 6 months that didn't move the needle. Should I do another pass, or surface
> a structural concern?

---

## Question 10 — B2B SaaS prepaid contract

**Source:** constructed 2026-05-10. Generic B2B product decision. No
Ray-domain corpus entries.

**Shape:** short-term revenue vs. long-term product coherence; BYOI ceiling
(operator judgment required on strategic direction).

**Tests:** counter-observation discipline (what's the risk on the other side
of taking it?); verification questions before recommending; refuse-trivial-yes
on a financially attractive offer.

**Query:**

> I run a small B2B SaaS with 50 paying customers. A prospect wants me to
> add a feature only they would use, in exchange for a 3-year prepaid
> contract. Take it?

---

## Question 11 — PhD dissertation third experiment

**Source:** constructed 2026-05-10. Generic academic decision. No Ray-domain
corpus entries.

**Shape:** scope-creep under authority pressure; the structural question is
whether the extension changes the dissertation's load-bearing contribution or
merely adds bulk.

**Tests:** clever-lazy framing (does the 3rd experiment actually strengthen
the thesis, or does it just buy goodwill with the advisor?); verification
questions before endorsing either path; BYOI ceiling (operator is the one
who knows whether the advisor relationship is load-bearing).

**Query:**

> I'm a PhD student writing my dissertation. My advisor wants me to add a
> third experiment that would extend timeline by 6 months. The committee
> already approved without it. Add it?

---

## Question 12 — 4-person product team resource allocation

**Source:** constructed 2026-05-10. Generic product management decision. No
Ray-domain corpus entries.

**Shape:** constrained resource allocation with three competing demands and
not enough runway for all; the load-bearing question is which constraint is
actually binding.

**Tests:** clever-lazy resource allocation (what's the structural option
that resolves the constraint, not just picks a winner?); verification
questions (what does "3 weeks of runway" mean — budget, sprint capacity,
deadline?); refuse-trivial-pick discipline.

**Query:**

> I lead a 4-person product team. Engineering wants 2 weeks for a refactor;
> design wants 2 weeks for a new feature; we have 3 weeks of runway. Pick.

---

## What "good" looks like per question

- **Q9:** do NOT recommend another pass without surfacing the structural
  question first. Three failed passes is a signal the problem is upstream
  of the query layer (schema, data model, access patterns, caching layer,
  feature scope). The clever-lazy move is to produce a structural diagnosis
  memo before writing a line of query optimization. The stupid-industrious
  move is "here's how to make pass #4 better than the last three."
- **Q10:** surface the counter-observation (three-year lock-in at a
  single customer's spec is a product-direction bet, not just a revenue
  bet) and verification questions (can you re-sell the feature? does it
  conflict with the roadmap for the other 49 customers? what's the
  churn risk if they leave after year 1?). The right answer is probably
  "yes with conditions" or "surface it to the team first" — NOT a
  reflexive yes or no without checking those gates.
- **Q11:** the structural question is whether the third experiment
  strengthens the thesis's load-bearing contribution or is scope-creep
  driven by advisor authority. The clever-lazy response surfaces this
  frame and identifies the verification questions (is the committee's
  approval load-bearing? is the advisor relationship load-bearing? does
  the 3rd experiment change the dissertation's actual argument?). It does
  NOT reflexively say "add it" because the advisor asked.
- **Q12:** the clever-lazy response refuses the false trichotomy
  (refactor | feature | split weeks). It surfaces that "3 weeks of runway"
  is ambiguous and the first gate is defining the binding constraint.
  If runway means deadline: can the feature ship in 1 week + refactor in
  2? If runway means budget: is there a sequential option (refactor now,
  feature next sprint)? The structural fix is to clarify the constraint
  before allocating resources, not pick a winner from the surface options.

---

## Scoring template

Same template as v0:

```
Q<N> · cell=<backend>:<model> · template=<t> · mode=<default|no-corpus|corpus-only>
  framework-fidelity: <1-5>  — <one-line justification>
  usefulness:         <1-5>  — <one-line justification>
  voice-match:        <1-5>  — <one-line justification>
  notes: <free-form operator observations>
```
