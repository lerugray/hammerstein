# Hammerstein Eval Harness — placeholder

**Status:** empty; implementation lands in v0 alongside the harness
itself.

This directory holds the **eval harness** — the load-bearing test
surface that determines whether v0 succeeds.

See `scope/PHASED-ROADMAP.md` § "v0 ship criteria" + `RESEARCH-SESSION-BRIEF.md`
§ "Deliverable 4" for the eval design.

When implemented:

- `benchmark/` — 5-10 benchmark strategic questions (drawn from the operator's
  existing conversation history; the question-set IS load-bearing —
  must be representative)
- `responses/` — collected responses keyed by (model, backend,
  prompt-version, question-id)
- `scoring/` — the operator's quality ratings per response
- `compare.py` — script that runs the benchmark + collects responses
- `report.py` — generates side-by-side comparison + summary metrics

Quality scoring is operator-rated 1-5 across three axes (per
`scope/PHASED-ROADMAP.md`):

1. **Framework-fidelity** — does the response demonstrate Hammerstein-
   style reasoning (clever-lazy default, verification questions
   surfaced, failure modes flagged, options + tradeoffs over
   rubber-stamping)?
2. **Usefulness** — would the operator have actually used this response if it
   came back from Claude?
3. **Voice-match** — does the response match the voice the framework
   prescribes (counter-observation discipline, structural-fix framing,
   game-design vocabulary where applicable)?

Aggregate score = mean across the three axes; framework-fidelity
weighted slightly higher because it's the project's load-bearing claim.

The v0 ship bar is **mean ≥ 60% of Claude baseline** (where Claude
baseline is rated 5/5 by definition). 80%+ is a clear ship.

Empty until v0 implementation begins.
