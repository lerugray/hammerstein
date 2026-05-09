# vision-audit benchmark fixtures (commit 4 placeholders)

These three PNG files are 1x1 transparent placeholders shipped with
ham-022d so the test harness in `tests/test_vision_audit.py` can run
through the full vision-dispatch pipeline (load_image_as_base64 ->
per-backend multimodal payload -> shape-gate validation) without
external dependencies.

Before commit 5 (ham-022e) runs the bake-off, replace each file with
the real benchmark image of the matching name:

- `twar-pc-s5-hex-grid.png` -- screenshot of
  `twar-pc-private/design/cd-output/surface-5.html` rendered in a
  browser. The image must show the hex-grid first pass (the
  register-mismatch case per scope/VISION-SUPPORT.md); the audit's
  right-answer is "ship-with-modifications, redo as area-based per
  ROTK IV reverse-engineering thesis".
- `retrogaze-rg-023-sprite.png` -- one 16x16 NES tile from the
  retrogaze rg-023 Sonnet bake-off cell. The audit's right-answer
  is "below the >=7/10 craft floor on shade-discipline + silhouette
  axes; reroll".
- `fnordos-dept-23-panel.png` -- screenshot of the FnordOS cinematic
  intro, post-DEPT-23 panel. The audit's right-answer is "register
  match: 16-color Bureau Palette + IBM Plex Mono + chromatic-
  aberration scanlines all honored; ship-as-is".

Once real images land, the corresponding `EXPECTED_*` constants in
`tests/test_vision_audit.py` should be filled in with the actual
right-answer verdict strings (or the load-bearing substrings the
test asserts on). Until then those constants are None and the
semantic-assertion tests are skipped.

Each filename is part of the public test-fixture contract; renaming
requires updating both this README and `test_vision_audit.py`.
