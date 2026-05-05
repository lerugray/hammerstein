# Hammerstein — Reading List

Source artifacts for the research session + ongoing reference. All paths
are relative to `<repo>/`.

## Canonical observation logs (read first)

- `generalstaff/docs/internal/Hammerstein Observations - Claude.md`
  — ~800 lines. The canonical Claude-side observation log spanning
  GeneralStaff's pivot session through ongoing meta-dispatcher work.
  Contains the framework's strongest empirical articulation: 4-quadrant
  baseline (64% clever-industrious, 0% stupid-industrious; 1.7%
  prompt-induced stupid-industrious tail per the experiments), the
  cross-project compounding claim, the verification-gate doctrine.

- `generalstaff/docs/internal/Hammerstein Observations Log.md`
  — ~40 lines. the operator's high-density notes; the "initial-negatives shift"
  hypothesis lives here with cross-project data points.

## Cross-project observation logs

- `retrogaze/Development/Hammerstein Observations Log.md`
- `retrogaze/Development/Hammerstein Observations - Retrogaze Bot.md`
  — Retrogaze project's instance of the framework, pre-private state
  separation; the original log + the bot-side mirror.

- catalogdna's Hammerstein observation logs (now in private state per
  the 2026-04-28 catalogdna→private migration) — the ORIGINAL bot-side
  observation log; ~22 bot runs of accumulated rules + failure modes.
  Path: `catalogdna/docs/internal/Hammerstein Observations Log.md` and
  `Hammerstein Observations - Bot.md`. May or may not be cloned on the
  current machine; the framework synthesis can lean on Claude-log
  references if catalogdna isn't local.

## Published / draft essays

- `lerugray.github.io/vault/hammerstein-essay-draft.md` — the operator's published
  essay on the Hammerstein framework as AI-alignment lens. Public
  framing of the typology + AI-misalignment mapping.

- `passive-income-hub/ideas/Hammerstein AI/hammerstein_ai_project.md`
  — Medium article project (~360 lines). NOTE: This is a meta-article
  proposing Hammerstein-as-AI-alignment-framework, not the AI-itself
  project that this `hammerstein` repo is. But Section 3
  (Experiments) defines the typology-mapping baseline that's the
  empirical grounding for the framework's quadrants.

- `hammerstein-article/hammerstein_ai_project.md` — duplicate or earlier
  version of the Medium project doc.

## Imagery / diagrams

- `GeneralStaff/docs/images/hammerstein-quadrant.svg`
- `GeneralStaff/docs/images/hammerstein-quadrant-2x.png`
- `hammerstein-article/images/hammerstein_typology_grid.png`
  — Visual representations of the 4-quadrant typology. Useful as
  reference; not directly consumable by the AI but useful for human
  consumers (article readers, future doc authors).

## Prior-thinking memos

- `generalstaff/docs/internal/IDEAS-BYO-CLAUDE-SUBSTITUTE-2026-05-04.md`
  — The morning-of-2026-05-04 memo that established the
  business-continuity framing this project addresses. Concluded
  "validate fallbacks, don't build a clone." This project is a
  refinement of that conclusion: encode the framework portably (not
  build a clone) so any model can carry strategic-reasoning load.

## Adjacent / supporting reading

The Medium article project's Section 1 (Research Needed) lists academic
papers the article cites. Not all are required for Hammerstein-the-AI
research, but the experimental-grounding ones are useful:

- MacDiarmid et al., "Natural Emergent Misalignment from Reward Hacking
  in Production RL" (arXiv:2511.18397v1) — the paper the typology was
  used to analyze.
- Greenblatt et al., "Alignment Faking in Large Language Models" (2024)
- Hubinger et al., "Sleeper Agents" (2024)
- Betley et al., "Emergent Misalignment" (2025)
- Treutlein et al., "Connecting the Dots" (2024) — out-of-context
  generalization, mechanism-relevant
- Bateson, levels of learning (deutero-learning) — the framework
  underpins inoculation prompting

These are background for the article project, not core reading for
Hammerstein-the-AI implementation. Read if they help the framework
synthesis; skip if the existing observation logs cover the ground.

## What to ignore

- `passive-income-hub/ideas/Hammerstein AI/` Section 1.1 historical
  research items (von Hammerstein-Equord biography, Wehrmacht
  implementation, comparable typologies) — useful for the Medium article
  but not load-bearing for the AI project. The framework's articulation
  in the operator's observation logs is sufficient.
- Personal-life / non-strategic conversation transcripts (<a personal-data project> corpus,
  mission-bullet entries, mission-PMA seed) — these are different
  artifacts for different projects. Hammerstein's corpus is
  strategic-reasoning examples specifically.

## Acquisition queue (not currently in repo)

- The original Hammerstein-Equord quote in its earliest-attested form
  — useful reference for the README + CONCEPT framing. Currently
  paraphrased across the existing essays; finding the exact original
  quote (German + translation) is a nice-to-have, not a blocker.

## Update log

- 2026-05-04: Initial scaffold; reading list assembled from grep across
  the operator's `<repo>/` tree.
