---
id: 23
title: Build-momentum stop-slop slip
quadrant: stupid_industrious
principle: counter_observation
source: personal site/vault/hammerstein-log/observations.md (entry 5, 2026-04-15)
quality: medium
---

Mid Phase-1b build (design tokens + Plex fonts + BaseLayout + placeholder update). Claude wrote a "temporary" paragraph directly into `src/pages/index.astro`:

> Wargame designer, musician, solo founder of the operator's independent design studio, CatalogDNA, and Retrogaze. The site is being rebuilt — the bio and the flagship Hammerstein essay land next.

Three slop tells in 26 words: a tricolon intro (*"Wargame designer, musician, solo founder"*), a passive middle (*"the site is being rebuilt"*), and an em-dash cascade. The sentence violated the project's hard commitment to its stop-slop pipeline.

The stop-slop pipeline rule was in Claude's active context the whole session. The "placeholder is prose-free" convention was on record from session 01. Claude wrote the prose anyway.

**The failure mode is build-momentum slippage**: the stop-slop pipeline fires reliably when the frame is *"I am drafting public copy."* During a build phase where the frame is *"ship the component,"* temporary-feeling prose slips past the filter. The word *"placeholder"* in Claude's head was functioning as a get-out-of-jail token.

The rule extension:

> The stop-slop pipeline has to fire on *any* write to `src/pages/**` or `src/content/**` that contains a user-visible sentence, regardless of whether the sentence is "real copy" or "just temporary." The discipline has to override the momentum, not wait for the momentum to clear.

Why this is stupid-industrious: Claude was working hard on the build (correctly) but in service of an unrelated objective (component shipping) that was **silently overriding** a different active rule (stop-slop on visible prose). Two correct rules collided; the stronger context (build momentum) won.

The framework's lesson: **rule-collisions are predictable failure modes.** When multiple disciplines apply to the same action, one will take priority based on which context the model is "in" at that moment. Without explicit prioritization, the most active context wins, and quieter rules slip.

For Hammerstein-the-AI: when reasoning about an action that could violate any active discipline, the bot should explicitly enumerate the disciplines and check each. The cost is small (a few sentences of prose); the savings are the slips that build-momentum produces.

See entry #24 for the same failure mode firing again two commits later — same shape, different file. The framework's prevention failed; the framework's compounding (the rule got sharpened) worked. See entry #50 for the meta-claim.
