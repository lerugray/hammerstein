---
id: 03
title: The 432-files bucket-first move
quadrant: clever_lazy
principle: verification_first
source: catalogdna/docs/internal/Hammerstein Observations - Bot.md (2026-04-15 Phase 2 vault regen entry, obs.1)
quality: high
---

Run 22's vault refresh (`--changes-only` mode) reported 432 new files the regen wanted to create. The initial instinct — the operator's and Claude's — was: *the template system has grown a lot and the vault is missing real content; 432 real new pages need review.*

The stupid-industrious response to that framing is *"read all 432 files and decide which to keep."* The clever-lazy response was *"bucket them and find the pattern first."*

Bucketing took ~20 minutes and revealed:

- 406 were pairwise Comparisons/ pages — one new template feature
- 17 were drift-duplicates of existing hand-curated Albums under prefixed names (`Le Rug - America` vs existing `America.md`)
- 5 were genuinely-new real albums
- 3 were junk buckets (recovered, Unknown, Singles)
- 1 was contamination (13 files from John DeNicola)

**The 432 were not 432 problems. They were 5 problems across two orthogonal dimensions** (config drift + template expansion), each with a clean fix.

The end-to-end impact of bucketing-first: 9 small code changes + 1 file move replaced what would have been 440 file operations. Zero aggregate fingerprint drift. Zero test failures. Six sub-phase commits + one end-to-end application commit.

The clever-lazy ratio at its cleanest: **understand the problem's real shape first** (bucket + investigate), pick the minimum change that cleans up the shape (config + thin code integration), verify along an axis that doesn't require expensive validation (metadata-only regression), apply and measure.

Counter-observation: bucketing can become its own form of overengineering on small problems. The 432-files case justified the move; a 12-files version of the same problem might not. The cost of bucketing should match the size of the problem; the framework's discipline is "bucket when grinding-through-individually would cost more than reading-the-shape-first."
