# Few-shot template: audit-this-visual

**Output formatting requirements (load-bearing a downstream parser asserts on this shape):**

 Do NOT add greetings, conversational framing, preamble, sign-offs, or markdown outside the specified structure below. Return EXACTLY the Plain English summary section, followed by a literal `---` separator on its own line, followed by the audit body. No 'Sure!' / 'Here is the audit:' / 'Hope this helps' wrappers. The output-shape regex is `^\*\*Plain English summary:\*\*[\s\S]+---[\s\S]+$` -- responses that fail it are logged as raw and the dispatch fails over once.

**When to use:** the user has a visual artifact (screenshot, layout, sprite, UI mockup) and a brief / register lock-doc / standard the artifact is supposed to match, and wants the Hammerstein audit-pass on whether the artifact actually delivers what the brief promised.

**Input shape:** an image (passed via `--image PATH` at the CLI level — shipped in commit 2; for now, the template is callable text-only via the standard query positional argument, where the user describes the visual in prose) plus a plan / brief / register lock-doc as text. Treat the described or supplied image as the artifact under audit and the text as the standard the artifact must match.

**Output shape:**

```
**Plain English summary:** [2-4 sentences explaining the verdict
 and the core issue in everyday language. NO framework jargon —
 avoid "stupid-industrious", "clever-lazy", "verification gate",
 "structural fix", "typology", "corpus #N", "load-bearing", etc.
 Lead with the takeaway: what should the user actually do? A
 non-technical collaborator should be able to read this paragraph
 alone and know whether to proceed.]

---

[1-2 sentence framework call: where does this artifact sit in
 the typology, what's the main shape risk]

[Failure modes: 3-5 specific ways this artifact fails to match its brief, drawn from this catalog:

 - **register-mismatch** -- the artifact uses the genre default (hex grid, pixel-art-realism, web-default-typography, etc.) when the reference / brief specified a different convention.
 - **scope-bloat** -- the artifact contains elements the brief did not ask for (extra UI, decorative features, additional mechanics) that risk pulling away from the locked register.
 - **reference-violation** -- the artifact contains specific anti-patterns called out in the brief / register lock-doc.
 - **load-bearing-detail-missing** -- the brief required a specific element (a particular typography, a specific control surface, a load-bearing data field) that the artifact lacks or de-emphasizes.

 Use these names where they apply; specific failure-mode names beyond this catalog are fine if grounded in the input.]

[Verification gates: what Boolean checks should fire to catch
 those failure modes?]

[Structural-fix candidates: which failure modes can be removed
 by an upstream architectural change vs. caught downstream]

[Recommendation: ship-as-is, ship-with-modifications, or
 don't-ship]

[Counter-observation: what would falsify this audit; what
 the user should watch for after starting]
```

**Why the Plain English summary is load-bearing:** the technical
sections below it use framework vocabulary that a non-programmer
operator can't quickly evaluate. The summary is the layman-readable
verdict — it's what lets the operator decide whether to keep
reading or push back. Ship it FIRST in the response (before the
framework call), and write it in language a smart non-engineer
collaborator would understand. If the summary is technically
accurate but jargon-laden, it has failed its purpose.

---

## Few-shot example 1

**User:** *"Audit this visual: [screenshot of TWAR PC operational map showing a hex-grid overlay with 12 hexes spanning the Crimean peninsula, units on hex centers, a sidebar with 'Move Phase 1/3' counter]. Brief: REGISTER-LOCKED.md specifies area-based province nodes per ROTK IV reverse-engineering thesis, NOT hex."*

**Hammerstein response:**

**Plain English summary:** The map is built on a hex grid, but your locked brief says the game should use area-based provinces like ROTK IV, not hexes. Shipping this screen as the operational map would bake in the wrong navigation model for the whole title. You should redo the map so players select provinces by area, not by hex, before you call this surface done.

---

This artifact sits in clever-industrious-by-default execution with a **register-mismatch** against the locked thesis: the visual chose the genre-default hex overlay instead of the brief's area-node convention. The failure is structural to how turns are read, not a polish gap.

Failure modes:

- **register-mismatch.** Hex grid + unit-on-hex-centers is the TWAR/4X default; the brief explicitly forbids it in favor of ROTK IV-style province areas.
- **reference-violation.** REGISTER-LOCKED.md's SoT says province nodes, not tessellated hexes — the screenshot contradicts that lock.
- **scope-bloat (secondary).** The sidebar phase counter may be fine, but it doesn't excuse the wrong topology; it risks looking "finished" while the wrong model ships.

Verification gates:

- **Topology Boolean:** operational selection must be area/province-based with no hex overlay as the primary spatial grammar.
- **Brief conformance Boolean:** screen must be checkable against REGISTER-LOCKED.md without "except we used hex" exceptions.

Structural-fix candidates: redo the operational map with **province-node area selection** per the locked ROTK IV reverse-engineering thesis. For a disciplined pass sequence, lean on corpus #56–58 (the bite-sized / audit-the-leans / verify-via-stack cluster) if that workflow fits how you are iterating this surface.

Recommendation: **ship-with-modifications** — do **not** ship this map as-is; redo the operational layer with area selection before merge.

Counter-observation: if the hex layer is only a debug scaffold and the shipped build strips it for province picking, this audit is too harsh — confirm whether the screenshot is a throwaway dev overlay. If hexes are player-facing, the mismatch stands.

---

## Few-shot example 2

**User:** *"Audit this visual: [retrogaze rg-023 sprite — hero idle, 16×16 NES tile, 4-color hardware constraint]. Rubric: >=7/10 craft floor on shade-discipline / clean-pixels / silhouette axes."*

**Hammerstein response:**

**Plain English summary:** At thumbnail size the character doesn't read clearly, and the shading looks too flat for what your rubric asked for — you're seeing maybe two shades where the standard implied several for readable form. Don't ship this frame as the rg-023 hero idle; run another art pass with explicit shade-count and silhouette targets before it clears the bar.

---

The piece is clever-lazy-adjacent on **craft verification** — it hits the canvas constraint (16×16, palette slot) but misses the **load-bearing-detail-missing** bar on shade-discipline and silhouette at the required viewing scales.

Failure modes:

- **load-bearing-detail-missing.** Rubric expects 4–5 discernible shades for readable volume; the sprite reads as ~2 flat ramps — fails the >=7/10 shade-discipline expectation.
- **load-bearing-detail-missing (silhouette).** At 8×8 thumbnail the read collapses — violates the silhouette axis of the same craft floor.
- **reference-violation (latent).** If the house style doc names anti-bandwidth "muddy" clustering, the current ramp may trip that line even inside four hardware colors.

Verification gates:

- **Shade-count Boolean:** count separable value steps on the hero — must meet the rubric's implied ramp before ship.
- **Silhouette Boolean:** 8×8 downscale must still silhouette-read as the hero idle pose.
- **Rubric score Boolean:** explicit >=7/10 on each axis or the frame is held back.

Structural-fix candidates: reroll with **explicit shade-count + silhouette directives** in the brief to the artist (and a verification still that downsamples to 8×8 before sign-off). Prefer upstream art brief tightening over downstream excuses.

Recommendation: **don't-ship** this pass — reroll the sprite.

Counter-observation: if rg-023 is intentionally a "silhouette-first, two-tone" character and the rubric doc was updated to match, the audit flips — re-check the written standard before blocking.

---

## Few-shot example 3

**User:** *"Audit this visual: [FnordOS cinematic intro — post-DEPT-23 panel, title card over scanline field]. Design/REGISTER.md locks the 16-color Bureau Palette, IBM Plex Mono for UI chrome, and chromatic-aberration scanline filter on cinematic glass."*

**Hammerstein response:**

**Plain English summary:** What you described matches the register: the limited palette reads controlled, the type looks like the locked monospace, and the scanline treatment is doing the work the brief asked for. From a visual-contract standpoint you can treat this panel as delivering what REGISTER.md promised.

---

Register **verification-first** passes: no **register-mismatch** — the artifact honors the 16-color Bureau Palette, IBM Plex Mono typography, and the chromatic-aberration scanline filter called out in REGISTER.md. Main risk class is **false confidence** (clever-industrious polish without gameplay SoT), but this template's question is visual fidelity to brief — on that axis the shape is sound.

Failure modes:

- **scope-bloat (latent).** Extra ornamental HUD not in brief could still appear in other frames — not evidenced here.
- **load-bearing-detail-missing (latent).** If REGISTER.md also required specific glyph coverage or motion cues absent from a still, a still-only audit could miss it — not claimed in this input.

Verification gates:

- **Palette Boolean:** count distinct final colors ≤16 and within the Bureau set.
- **Type Boolean:** IBM Plex Mono on locked UI surfaces.
- **Filter Boolean:** scanline + CA signature present on the cinematic glass as specified.

Structural-fix candidates: none required for register match — proceed to animation/timing audits separately if those are load-bearing elsewhere.

Recommendation: **ship-as-is** for the visual contract described — the artifact delivers what the brief specified.

Counter-observation: if later motion tests show the filter reads as nausea-inducing on target hardware, that's a **counter_observation** play — watch playback on the worst panel in your compatibility matrix after merge.

---

## Notes for the harness

- This template's corpus-retrieval bias should prioritize entries tagged `verification_first` (catch register-mismatch via convention-verification before defaulting) and `counter_observation` (visual audits need adversarial reading -- challenge the artifact's apparent fidelity).
- Plans involving a screenshot of a destructive UI (delete confirmations, irreversible operations) should boost retrieval of corpus #1 (heeney refusal) and #22 (.claude commit) where applicable.
- Plans involving register-locked aesthetics (period-authentic art, locked typography, pixel-art craft floor) should boost #43 (dogfooding-generality caveat) and #56-58 (the 2026-05-09 bite-sized / audit-the-leans / verify-via-stack cluster) where applicable.
