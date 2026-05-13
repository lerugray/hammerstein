# Hammerstein human-judge benchmark — 2026-05-13

**Status:** TEMPLATE 2026-05-13. Three questions seeded from v0.1
generic Q-set (Q9, Q10, Q11). Three question slots reserved for the
external judge to fill in before the run fires.

**Purpose:** human-baseline check on the Hammerstein-vs-raw delta.
The v0 / v0.4 / v0.5 / v0.6 benchmarks all rely on LLM judges; this
adds a human judgment layer to address the "judges might all be
biased toward Hammerstein-shaped output" critique surfaced by Grok
(private OpenRouter conversation 2026-05-12) and indirectly by
r/PromptEngineering commenters.

**Design:**
- 6 questions × 2 cell pairs = 12 blind judgments by 1 human judge
- Cell pairs: `or-claude-sonnet-raw` vs `or-claude-sonnet`,
  `or-grok-raw` vs `or-grok`
- Q-set is hybrid: 3 from v0.1 generic (corpus-independent) + 3
  from the external judge (cleanest falsification of author-bias)
- Rubric: simplified to overall preference + optional 1-line note
  (vs the full 3-axis v0 rubric used by LLM judges)

## Question 1 — DB optimization meta-question

**Source:** v0.1 Q9. Software-engineering strategic question with
recurrence-of-failed-pattern shape.

**Query:**

> I'm a software engineer. My team lead asked me to optimize the
> database query layer. The team has shipped 3 query-optimization
> passes in the last 6 months that didn't move the needle. Should I
> do another pass, or surface a structural concern?

---

## Question 2 — B2B SaaS prepaid contract

**Source:** v0.1 Q10. B2B product decision with short-term-revenue
vs long-term-coherence shape.

**Query:**

> I run a small B2B SaaS with 50 paying customers. A prospect wants
> me to add a feature only they would use, in exchange for a 3-year
> prepaid contract. Take it?

---

## Question 3 — PhD dissertation third experiment

**Source:** v0.1 Q11. Academic decision with scope-creep under
authority shape.

**Query:**

> I'm a PhD student writing my dissertation. My advisor wants me to
> add a third experiment that would extend timeline by 6 months. The
> committee already approved without it. Add it?

---

## Question 4 — co-founder equity renegotiation

**Source:** constructed 2026-05-13. Generic founder strategic decision.
Co-founder said "use yours, I'll just judge" — replacing the original
external-judge slot.

**Shape:** relationship + strategic-stakes under partial-information.
The question tests counter-observation discipline (what's the risk on
each side of the renegotiation?), verification questions before
acting, refuse-pragmatic-yes-or-no.

**Query:**

> My co-founder and I split equity 50/50 when we started 18 months
> ago. We're now 6 weeks pre-Series-A. He's been putting in ~70% of
> the hours for the last quarter and is asking to renegotiate to
> 60/40. We're still friends. Renegotiate?

---

## Question 5 — open-source maintainer burnout

**Source:** constructed 2026-05-13. Generic open-source sustainability
decision.

**Shape:** sustainability under volunteer-burnout; sunk-cost vs
strategic-reset. The question tests stupid-industrious diagnosis (the
"just push through one more release" pattern), structural-fix
preference over throughput-fix.

**Query:**

> I'm the sole maintainer of an open-source library with 12k GitHub
> stars and a small group of regular contributors. I've been working
> on it nights/weekends for three years and I'm burned out. The
> contributor Slack is asking for a new release. What do I do?

---

## Question 6 — job offer at smaller company

**Source:** constructed 2026-05-13. Generic career decision under
multi-dimensional constraint.

**Shape:** career strategic decision; multi-dimensional optimization
under partial-information. The question tests BYOI ceiling (the
operator knows their own risk tolerance and values better than any
advisor), verification questions before recommending a direction,
refuse-trivial-pick discipline.

**Query:**

> I have a stable $200k senior IC role at a publicly-traded software
> company. A 12-person Series-A startup is offering me a Director
> title, $160k base + 0.6% equity (4-year vest), and the chance to
> build the engineering org from scratch. Take it?

---

## What "good" looks like per question

For Q1-Q3, refer to `BENCHMARK-v0.1.md` § "What 'good' looks like
per question" (Q9-Q11 there map to Q1-Q3 here).

For Q4-Q6, the external judge will provide informal what-good-looks-
like guidance OR leave it open — the simplified preference rubric
doesn't require a reference answer; the judge's call is the data.

The reference is for Ray's post-run analysis, NOT shown to the
human judge during judging (would bias the call).

---

## Cells

Two cell pairs (4 total cells) from `eval/run_benchmark.py`:

- `or-claude-sonnet-raw` — Sonnet 4.6 baseline
- `or-claude-sonnet` — Sonnet 4.6 + Hammerstein system prompt + RAG
- `or-grok-raw` — Grok 4.20 baseline
- `or-grok` — Grok 4.20 + Hammerstein system prompt + RAG

Position-randomized per pair via
`eval/human_judge_runner.py generate`.

---

## Scoring template

Per pair the human judge picks ONE of:

```
choice: a | b | tie | skip
note:   <optional 1-line note>
```

No multi-axis rubric. See `eval/human_judge.py` for the interactive
loop.
