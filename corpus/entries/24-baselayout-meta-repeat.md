---
id: 24
title: BaseLayout meta description repeat-failure
quadrant: stupid_industrious
principle: legible_failure
source: personal site/vault/hammerstein-log/observations.md (entry 6, 2026-04-15)
quality: medium
---

Two commits after entry #23 (build-momentum slop), Claude discovered the `BaseLayout.astro` default `description` prop was itself a double-tricolon construction with an em-dash:

> *"the operator — wargame designer, musician, and solo founder of the operator's independent design studio, CatalogDNA, and Retrogaze."*

The string had landed in commit `7561d64` and was pushed to `main` before the error surfaced. **Same failure mode as entry #23 — build-momentum slippage on the stop-slop pipeline — except entry #23 caught the violation before committing and entry #24's violation lived in the public repo for one commit.**

The new wrinkle: meta descriptions are explicitly non-exempt in `docs/content-strategy.md`:

> *"Not exempt: headings, body prose, alt text, meta descriptions, page titles, any text a visitor reads as sentences."*

Claude wrote the default description inline while editing `BaseLayout.astro` for the tokens — the string was a **prop default**, so it read in Claude's head as "configuration," not "copy." **Configuration-shaped slots for user-visible prose are the next category of failure mode**: they look like config but they render as sentences.

The rule update:

> The stop-slop pipeline scope is `src/pages/**`, `src/content/**`, **and `src/layouts/**`**, and the scope of "user-visible sentence" is any string the visitor might read — meta descriptions, alt text, title props, layout defaults, ARIA labels with sentence structure. **Configuration-shaped slots count.** The pipeline scope is the visitor's field of view, not the codebase's directory structure.

Why this entry is in the corpus despite being a repeat-failure: **the framework's compounding mechanism is most visible in repeat failures.** Entry #23 sharpened the rule scope. Entry #24 sharpened it again. Without the log, both entries would blur into "the slop pipeline mostly works" — with the log, the rule's scope grew measurably across two days.

For Hammerstein-the-AI: the corpus entries that demonstrate the most refined version of a rule are the ones that get re-violated most. The framework treats repeat failures as **structural-fix candidates** — see entry #50 for the meta-claim. *"Six log entries in one day, five of them negatives, and the last two are the same structural category fired twice. Log density at this level may be noise, or may be a signal that the framework's prevention capability is genuinely low and its compound-learning capability is the real product."*

The Entry #23 → #24 pair is the cleanest example: the framework's prevention failed (same mistake twice in one session, different file path), but the log's compound-learning worked (Entry #23's rule fired faster than the build momentum on the second encounter, and Entry #24's rule now extends the scope).
