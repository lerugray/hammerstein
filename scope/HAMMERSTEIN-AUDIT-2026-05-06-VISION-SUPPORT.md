# Hammerstein audit — vision-support scope, pre-revision draft

**Date:** 2026-05-06 evening
**Backend:** openrouter qwen/qwen3.6-plus, $0.00879, 59.4s
**Audited plan:** Pre-revision draft of `scope/VISION-SUPPORT.md` —
condensed-summary form (key locks + open questions only).
**Verdict:** Ship with modifications. 4 load-bearing catches.

---

## Plain English summary (verbatim)

The plan is correctly scoped and avoids building unnecessary
infrastructure. The only real risk is that image-reading models
tend to add conversational filler or change formatting, which
will break your existing `brief.ts` parser. Add a strict
formatting check before shipping, pick a single template name
to avoid confusion, and run your three benchmarks exactly as
planned. If the free model passes two out of three, ship it.

---

## Failure modes (verbatim)

- **Output contract violation.** Vision models default to
  conversational framing ("Here's my analysis..."), extra markdown,
  or bullet-point reformatting. `brief.ts` expects a strict
  `**Plain English summary:**` + audit body. Unchecked drift breaks
  the pipeline.
- **Benchmark overfitting.** Three clean, high-contrast cases may
  pass on the free tier by luck. A single low-res screenshot, UI
  overlay, or ambiguous sprite will expose the 2/3 gate as arbitrary
  rather than diagnostic.
- **Fallback ambiguity.** "Operator escalation" to paid models lacks
  a clear trigger. Without a deterministic switch (CLI flag or
  auto-failover), you'll waste cycles manually re-running prompts
  instead of letting the system route.
- **Template naming collision.** `audit-this-design` overlaps with
  architectural/system design audits. Future sessions will confuse
  visual register checks with structural code reviews.

## Verification gates (verbatim)

- **Output-shape Boolean:** Post-run parser must match
  `^\*\*Plain English summary:\*\*[\s\S]+---[\s\S]+$` (or your exact
  delimiter). Fail the run and log raw output if it doesn't match.
- **Fallback trigger:** `--backend paid` CLI override, or auto-route
  to paid if shape-gate fails or free-tier returns
  `<confidence_threshold>`. Log the switch with model name +
  timestamp.
- **Benchmark isolation:** Run the 3 cases with zero cached context.
  Record raw model responses alongside parsed results. If any case
  fails shape-gate, it counts as a miss regardless of semantic
  correctness.

## Structural-fix candidates (verbatim)

- **Prompt-level shape enforcement:** Add explicit negative
  constraints to the system prompt: `"Do not add greetings,
  conversational framing, or markdown outside the specified
  structure. Return exactly the two sections."`
- **Lightweight post-parse gate:** A 10-line script that strips
  conversational filler, validates the delimiter structure, and
  halts if malformed. Catches failures that prompt-level
  constraints miss.
- **Template rename:** `audit-this-visual` or `audit-this-screenshot`.
  Prevents collision with non-visual design audits and makes the
  template's purpose legible to future sessions.

## Counter-observation (verbatim)

If the vision model's output is consistently clean enough for
`brief.ts` without post-processing, the validation gate is
unnecessary overhead. The check: run the 3 benchmarks with the
raw prompt. If 3/3 parse cleanly on the first try, drop the
gate. If any fail, keep it.

---

## How the revision applies these (post-audit edits)

- **Template renamed** `audit-this-design` → `audit-this-visual` per
  the collision argument (architectural design vs visual design).
- **Output-shape gate added** as a v0 requirement: regex check on
  returned format, halt if malformed, log raw. Counter-observation
  acknowledged: if benchmarks parse 3/3 clean without the gate,
  it's removable post-eval.
- **Fallback determinism:** "operator escalation" replaced with
  explicit `--backend-tier paid` CLI flag OR auto-failover when
  shape-gate fails on free-tier output. Logged with model + timestamp.
- **Benchmark isolation** added to the eval methodology: zero
  cached context, raw responses recorded, shape-gate failures
  count as misses.

Audit verdict applied; ready to lock the v0 scope and queue
implementation.
