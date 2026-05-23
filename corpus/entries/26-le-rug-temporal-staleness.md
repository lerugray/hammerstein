---
id: 26
title: Le Rug temporal staleness
quadrant: stupid_industrious
principle: counter_observation
source: personal site/vault/hammerstein-log/observations.md (entry 8, 2026-04-15)
quality: medium
---

Late in session 03, after Phases 13-20 had all shipped, the operator flagged that the landing page dek was wrong: he hasn't been actively in a band in about ten years. A few minutes later he added that **Le Rug** — described throughout the site as the operator's *"current"* / *"ongoing"* music project — also hasn't been current in a long time, that he'd sold his instruments, and that he was *"all but done musically unless any of my businesses take off."*

Both claims appeared in multiple places: the landing dek, the Music section blurb, the `/music` page meta description and dek and intro paragraph, the `/catalogdna` page's Le Rug cross-reference, the BaseLayout default description, the og:image:alt attribute, and the rendered `og-image.png`.

The chain that produced the failure:

1. the operator's public Bandcamp page at `lerug.bandcamp.com` exists; the catalog is up.
2. In session 1, the project-discovery WebSearch agent treated the existence of the Bandcamp page as evidence Le Rug was an *ongoing* project. The vault file got the language *"Le Rug is the ongoing music project of the operator"* — present tense, sourced from public-web inference, **never confirmed with Ray.**
3. Subsequent phases pulled present-tense language from the vault as source-of-truth.

**This is a different category from the hallucinated arxiv credential (entry #21).** Entry #21 was a **fabricated** credential. This one is **temporal staleness**: a claim that *was* true at some point in the past and is false now, but the public artifact (Bandcamp page) doesn't carry a "no longer active" marker, so the discovery pipeline read present-tense language into a project that's actually past tense.

Why "flag-and-hold" (entry #21's rule) didn't fire: the rule's trigger was *"agent reports an external credential that materially upgrades the user's public identity."* Le Rug looked different — it wasn't an *upgrade*; the source was the user's own Bandcamp; the information had been in the vault since session 1 without flags.

The rule extension:

> **Present-tense claims about the user's current activities** ("ongoing", "current", "running", "is making") are a different category than credentials, and they need their own check: **when the source is a public artifact with no temporal marker, flag the claim as time-uncertain and confirm with the user before writing present tense to the vault.** Past tense is recoverable; present tense is publicly embarrassing.

For Hammerstein-the-AI: when a public-web artifact about a user (Bandcamp pages, GitHub repos, personal sites, professional bios, Wikipedia entries) implies an ongoing activity, the bot should default to past-tense framing in any output until the user confirms currency. **The fact that the page is up does not prove the activity is current. Web is not a heartbeat.**

See entry #21 for the credential-hallucination case (different failure category). Both entries together demonstrate that the framework's verify-discipline must extend across multiple categories of external claim — and that new categories surface as the framework is applied to new contexts.
