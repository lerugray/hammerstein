# vision-audit benchmark fixtures

These PNG files back the vision-Hammerstein benchmark cases used by
`tests/test_vision_audit.py` and the v0 release-locking bake-off
(see `tools/run_vision_bakeoff.py` once commit 5 lands).

## Current state (2026-05-09 evening)

| File | State | Source |
|---|---|---|
| `twar-pc-s5-hex-grid.png` | **REAL** (909 KB) | Playwright render of `twar-pc-private/design/cd-output/surface-5.html` (cartographic plate + hex overlay; commit 080f439 of twar-pc-private). Captures the load-bearing register-mismatch surface: the brief locks area-based province nodes per ROTK-IV reverse-engineering thesis, but the SVG `.hex-layer` still ships an overlaid hex grid. |
| `retrogaze-rg-023-sprite.png` | **REAL** (256 B) | `retrogaze/batch_output_2026-04-24/nes/knight/strict_nes.png` -- a 16x16 NES-strict-palette knight from the retrogaze bake-off pipeline. Stand-in for the rg-023 craft-floor case. |
| `fnordos-dept-23-panel.png` | **PLACEHOLDER** (67 B) | 1x1 transparent PNG. The FnordOS-private repo only ships Tauri app icons (128/32/icon.png); the cinematic-intro DEPT-23 panel has not yet been screenshotted to disk. Replace before running the bake-off semantic test for FnordOS. |

## Right-answer verdicts (per scope/VISION-SUPPORT.md)

These are the substrings the bake-off (and the gated semantic tests
in `test_vision_audit.py`) assert on as load-bearing fragments of the
right answer. They are deliberately phrase-level, not line-level --
small variation in vision-model phrasing should not break the test.

- **TWAR PC** (`_EXPECTED_TWAR_PC`): the audit must call out the
  hex-overlay-vs-area-based-brief mismatch. Substring assertion:
  `"hex"` AND (`"area"` OR `"province"`) AND (`"register"` OR
  `"mismatch"` OR `"redo"`). The verdict shape is "ship-with-
  modifications".
- **retrogaze** (`_EXPECTED_RETROGAZE`): the audit must call out the
  craft-floor failure. Substring assertion: `"craft"` AND
  (`"shade"` OR `"silhouette"` OR `"reroll"` OR `"below"`). The
  verdict shape is "don't ship; reroll".
- **FnordOS** (`_EXPECTED_FNORDOS`): when a real DEPT-23 panel
  screenshot lands, the audit must call out register match. Substring
  assertion (placeholder until image lands): `"register"` AND
  (`"match"` OR `"honored"` OR `"ship"`). Until real image lands,
  the semantic test stays gated on `_EXPECTED_FNORDOS is not None`.

## Swap-in protocol for FnordOS

When a real FnordOS DEPT-23 panel screenshot becomes available
(future Tauri-app-running session, or a designed cinematic mockup):

1. Save it as `fnordos-dept-23-panel.png` in this directory (must be
   PNG; JPEG/WebP would also work but the placeholder keeps PNG).
2. Set `_EXPECTED_FNORDOS` in `tests/test_vision_audit.py` to a
   non-None substring assertion (per the phrase shape above).
3. Run `pytest tests/test_vision_audit.py` -- the previously-skipped
   `test_fnordos_audit_returns_expected_verdict` now exercises.
4. If the bake-off script (`tools/run_vision_bakeoff.py`) has
   already landed, re-run it to refresh the routing-lock decision
   with the FnordOS case included.

## Filename contract

Each filename is part of the public test-fixture contract; renaming
requires updating this README, `test_vision_audit.py`, and the
bake-off script.
