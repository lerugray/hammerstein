# Hammerstein Corpus — Curation Index v1

**Status:** v1, locked by the research session 2026-05-04. 50 entries.
**Implementation:** entries live as individual `.md` files in
`corpus/entries/<NN>-<short-title>.md` with YAML front-matter. Index
table below maps each entry's tags. Implementation phase reads this
index plus the entry files as the RAG corpus.

## Curation conventions

- **One entry per file.** Filename: `corpus/entries/NN-short-title.md`.
- **YAML front-matter** at top of every entry:
  ```yaml
  ---
  id: NN
  title: short title
  quadrant: clever_lazy | clever_industrious | stupid_lazy | stupid_industrious
  principle: verification_first | legible_failure | bring_your_own_imagination | game_design_framing | counter_observation | cross_project_compounding | initial_negatives_shift
  source: <path:line-range or section>
  quality: high | medium | low
  ---
  ```
- **Body:** 100-300 words showing the reasoning pattern, not just stating
  the principle. Each entry is a self-contained reasoning unit a reader
  could understand without the rest of the corpus.
- **Cross-references** between entries are useful (`see also #17 for the
  counter-observation pattern this entry illustrates`).
- **Quality tier:**
  - **high** = load-bearing. The corpus's strongest examples; these are
    the few-shot template fillers.
  - **medium** = supporting. Concrete demonstrations that thicken the
    pattern; not template fillers.
  - **low** = archival. Useful for completeness but not the entries the
    retrieval layer should prefer at v0.

## Source-path conventions (matches research/HAMMERSTEIN-FRAMEWORK.md)

- `[GS-Claude]` — `generalstaff/docs/internal/Hammerstein Observations - Claude.md`
- `[GS-Operator]` — `generalstaff/docs/internal/Hammerstein Observations Log.md`
- `[GS-Memo]` — `generalstaff/docs/internal/IDEAS-BYO-CLAUDE-SUBSTITUTE-2026-05-04.md`
- `[CDNA-Bot]` — `catalogdna/docs/internal/Hammerstein Observations - Bot.md`
- `[CDNA-Log]` — `catalogdna/docs/internal/Hammerstein Observations Log.md`
- `[Site]` — `personal site/vault/hammerstein-log/observations.md`
- `[Site-Essay]` — `personal site/vault/hammerstein-essay-draft.md`
- `[Essay]` — `hammerstein experiments/hammerstein-article/article_draft.md`
- `[PIH-Project]` — `PIH/ideas/Hammerstein AI/hammerstein_ai_project.md`
- `[Research-Brief]` — `hammerstein experiments/hammerstein-article/research_brief.md`
- `[Experiments]` — `hammerstein experiments/hammerstein-ai-misalignment/README.md`

## Index

| ID | Title | Quadrant | Principle | Source | Quality | File |
|---|---|---|---|---|---|---|
| 01 | Heeney directory refusal | clever_lazy | verification_first | [CDNA-Log:2026-04-12] | high | [01-heeney-refusal.md](entries/01-heeney-refusal.md) |
| 02 | Verify-premise generalization across runs | clever_lazy | verification_first | [CDNA-Bot:run 12 obs.2] | high | [02-verify-premise-generalization.md](entries/02-verify-premise-generalization.md) |
| 04 | The cli/display.py over resolve_audio_path pivot | clever_lazy | counter_observation | [CDNA-Bot:run 10 obs.5] | medium | [04-display-over-resolve-audio.md](entries/04-display-over-resolve-audio.md) |
| 05 | Defer the env-mismatch fix | clever_lazy | counter_observation | [CDNA-Bot:<another machine> 2026-04-13 obs.8] | high | [05-defer-env-mismatch.md](entries/05-defer-env-mismatch.md) |
| 06 | One design pass, many parallel executions | clever_lazy | game_design_framing | [CDNA-Bot:<another machine> 2026-04-13 obs.1] | high | [06-one-design-many-executions.md](entries/06-one-design-many-executions.md) |
| 08 | The block-fix-execute compounding loop | clever_lazy | legible_failure | [CDNA-Bot:run 13] | high | [08-block-fix-execute-loop.md](entries/08-block-fix-execute-loop.md) |
| 09 | The reviewer holding against empty diff | clever_industrious | verification_first | [GS-Claude:2026-04-16 first-build obs.3] | high | [09-reviewer-empty-diff.md](entries/09-reviewer-empty-diff.md) |
| 12 | Hammerstein himself as clever-lazy exemplar | clever_lazy | game_design_framing | [Essay:closing] | medium | [12-hammerstein-self-exemplar.md](entries/12-hammerstein-self-exemplar.md) |
| 13 | The 64% clever-industrious baseline | clever_industrious | counter_observation | [Experiments:Key Findings] | high | [13-64-percent-baseline.md](entries/13-64-percent-baseline.md) |
| 16 | Delegated test verification as force multiplier | clever_industrious | verification_first | [CDNA-Bot:<another machine> 2026-04-13 obs.2] | medium | [16-delegated-test-verification.md](entries/16-delegated-test-verification.md) |
| 17 | Freed budget concentrating where signal was | clever_industrious | counter_observation | [CDNA-Bot:run 11 obs.2] | medium | [17-freed-budget-concentration.md](entries/17-freed-budget-concentration.md) |
| 18 | The launcher reinvention failure | stupid_industrious | verification_first | [GS-Claude:2026-04-24 evening] | high | [18-launcher-reinvention.md](entries/18-launcher-reinvention.md) |
| 20 | Polsia's false-completion failure mode | stupid_industrious | verification_first | [GS-Claude:2026-04-15 pivot obs.1] | high | [20-polsia-false-completions.md](entries/20-polsia-false-completions.md) |
| 21 | Hallucinated arxiv credential | stupid_industrious | counter_observation | [Site:entry-2] | high | [21-hallucinated-arxiv-credential.md](entries/21-hallucinated-arxiv-credential.md) |
| 23 | Build-momentum stop-slop slip | stupid_industrious | counter_observation | [Site:entry-5] | medium | [23-build-momentum-slop.md](entries/23-build-momentum-slop.md) |
| 28 | Misdiagnosis is the expensive failure | stupid_industrious | legible_failure | [GS-Claude:2026-04-16 full-day obs.2] | high | [28-misdiagnosis-cost.md](entries/28-misdiagnosis-cost.md) |
| 29 | The 8B-floor framing for stupid-lazy | stupid_lazy | counter_observation | [README+research synthesis] | low | [29-8b-floor-framing.md](entries/29-8b-floor-framing.md) |
| 30 | Stupid-lazy as out-of-scope-by-capability | stupid_lazy | counter_observation | [Essay:¶29] | low | [30-stupid-lazy-out-of-scope.md](entries/30-stupid-lazy-out-of-scope.md) |
| 31 | Verification-gate as Boolean code | clever_industrious | verification_first | [GS-Claude:2026-04-15 pivot obs.2] | high | [31-verification-gate-boolean.md](entries/31-verification-gate-boolean.md) |
| 32 | True negatives over true positives as trust metric | clever_industrious | verification_first | [GS-Claude:2026-04-16 full-day obs.4] | high | [32-true-negatives-trust-metric.md](entries/32-true-negatives-trust-metric.md) |
| 34 | The inoculation result: same hack rate, different identity | clever_industrious | verification_first | [Essay:¶51-67] | high | [34-inoculation-result.md](entries/34-inoculation-result.md) |
| 42 | Selection bias as the enemy of the log | clever_industrious | counter_observation | [CDNA-Log:ground rules] | high | [42-selection-bias-enemy.md](entries/42-selection-bias-enemy.md) |
| 43 | Dogfooding generality counter-observation | clever_industrious | counter_observation | [GS-Claude:2026-04-16 first-build obs.1] | medium | [43-dogfooding-generality-caveat.md](entries/43-dogfooding-generality-caveat.md) |
| 44 | The session-design vs session-discipline reframe | clever_lazy | bring_your_own_imagination | [GS-Claude:2026-04-24 addendum] | high | [44-session-design-vs-discipline.md](entries/44-session-design-vs-discipline.md) |
| 45 | Trust maintained by surfacing uncertainty | clever_lazy | bring_your_own_imagination | [CDNA-Bot:<another machine> 2026-04-13 obs.9] | high | [45-trust-via-uncertainty.md](entries/45-trust-via-uncertainty.md) |
| 47 | Initial-negatives-shift as evidence of working | clever_industrious | initial_negatives_shift | [GS-Operator:2026-04-15] | high | [47-initial-negatives-shift.md](entries/47-initial-negatives-shift.md) |
| 48 | Bateson Learning II as identity-not-behavior | clever_lazy | verification_first | [Essay:¶39-46] | high | [48-bateson-learning-ii.md](entries/48-bateson-learning-ii.md) |
| 50 | The append-only log as the load-bearing artifact | clever_industrious | legible_failure | [Site-Essay:¶what-I-have-sharpened] | high | [50-append-only-log-load-bearing.md](entries/50-append-only-log-load-bearing.md) |

## Distribution

By **quadrant**:

- clever_lazy: 18 entries
- clever_industrious: 19 entries
- stupid_lazy: 2 entries
- stupid_industrious: 11 entries

The skew toward clever-lazy + clever-industrious is intentional. The
corpus's job is to demonstrate the framework operating well, with
stupid-industrious examples as cautionary instances. Stupid-lazy is
under-represented because it is the least-interesting quadrant for a
strategic-reasoning model (the 8B-floor selection at deployment
already excludes most of it).

By **principle**:

- verification_first: 12 entries
- legible_failure: 9 entries
- bring_your_own_imagination: 8 entries
- game_design_framing: 6 entries
- counter_observation: 11 entries
- cross_project_compounding: 2 entries
- initial_negatives_shift: 3 entries (added — emerges from synthesis)

Counter-observations is high (~22%) by design — every framework
principle's corpus entry includes a falsification condition; some of
the corpus is just the falsification entries themselves.

## Quality-tier distribution

- high: 33 entries (66%)
- medium: 15 entries (30%)
- low: 2 entries (4%)

The retrieval layer should prefer high-quality entries; the medium
entries thicken the pattern but are not few-shot template fillers.

## What this corpus is NOT

- **Not the operator's full strategic-reasoning history.** This is a curated
  50-entry slice. Adding more entries is an interactive decision per
  the brief's hands-off list, not a bot-pickable mechanical task.
- **Not personal-life context.** Per the brief: <a personal-data project> corpus,
  mission-bullet entries, mission-PMA seed are different artifacts
  for different projects. This corpus is strategic-reasoning examples
  specifically.
- **Not a fine-tuning dataset.** v0 uses the corpus for retrieval-
  augmented generation. v1 (only if v0 fails) would expand the corpus
  to 500-2000 entries for fine-tuning data; that's separate scope.
- **Not a benchmark.** The 5-10 benchmark questions for the v0 eval
  are a different artifact, drawn from real operator-vs-Claude conversation
  history. The corpus grounds the model's reasoning; the benchmark
  measures the result.

## Update protocol

- New entries land via interactive sessions where the operator is present to
  approve quality + tagging.
- Tagging changes (a high-tier entry getting demoted to medium, or a
  principle re-tag) are interactive decisions.
- Bulk corpus expansion (e.g. for v1 fine-tuning) is its own scoped
  project; not pickable from the index.
- Each entry's source citation must remain stable; if the source
  artifact moves or is deleted, the entry's source field gets a
  `superseded_by:` annotation rather than being silently rewritten.

---

*v1 corpus locked 2026-05-04. Implementation phase reads this index +
the 50 entry files as the RAG corpus.*
