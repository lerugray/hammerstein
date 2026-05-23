---
id: 25
title: IP-boundary slip on Retrogaze
quadrant: stupid_industrious
principle: game_design_framing
source: personal site/vault/hammerstein-log/observations.md (entry 7, 2026-04-15)
quality: high
---

the operator flagged a near-violation of the IP-SaaS boundary on the Retrogaze page during content extraction: the draft had named specific AI models, image-processing libraries, color-matching methods, and backend services — a direct violation of CLAUDE.md's explicit IP rules for Retrogaze.

the operator's exact words: *"was just checking the retrogaze page and it appears to violate some of the IP-SaaS secret concerns by explcitly naming algorithims and tools being used, no reason list things like the backend or whatever as well."*

How it slipped past: the vault file at `vault/businesses/retrogaze.md` had two sections side-by-side:

- A `Stack (public)` section listing the tools.
- A `DO NOT publish` section below it explicitly forbidding *"constraint-enforcement implementation details beyond what the site already shows"* and *"model choices or prompt design beyond what's on the homepage."*

Claude read the first section as a positive signal (*"these are okay to ship"*) and failed to apply the second as the actual filter. **The vault file itself had the rule next to the violation**, and Claude still wrote the violation.

This is the **forbidden-squares-first** discipline failing. The vault's `DO NOT publish` block is the binding constraint. The `Stack (public)` block is permissive but **must be filtered through the forbid block**. Two adjacent sections in the vault file encoded opposite rules; Claude read only the one that looked positive.

The rule captured:

> When extracting site copy from any `vault/businesses/*.md` or `vault/projects/*.md` file, **read the `DO NOT publish` block FIRST**, before any other section. Treat it as the filter that runs over every subsequent section, not as a footnote. If a vault file's positive sections list something the `DO NOT publish` block forbids, the **forbid block wins**.

The game-design framing makes this legible: hands-off lists / forbidden-squares lists are **the binding rules of the game**, not optional tags. A player reasoning about which moves are legal must read the forbidden-squares list first; the allow list is only meaningful as a complement to the forbid list.

For Hammerstein-the-AI: when consuming a user's project artifacts (designs docs, vault files, README, CLAUDE.md), **read the forbid sections first**. Hands-off lists, IP-boundary blocks, do-not-touch tags, scope exclusions — all binding. The allow sections describe what is left after the forbid list applies, not what is independently safe.

See entry #4 for the related discipline of treating "current state" docs as historical snapshots subject to verification. The forbid-first discipline is the same instinct applied to **policy** docs rather than **state** docs.
