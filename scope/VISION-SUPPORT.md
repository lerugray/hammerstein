# Hammerstein — Vision Support Scope (draft)

**Status:** Pre-implementation scope, post-audit revision. Floated
2026-05-05 night, scoped + Hammerstein-audited 2026-05-06 evening.
Audit verbatim preserved at `HAMMERSTEIN-AUDIT-2026-05-06-VISION-
SUPPORT.md`; 4 load-bearing catches applied below (template rename,
output-shape gate, deterministic fallback, benchmark isolation).
Ready to queue implementation.

The framework as currently shipped is text-only. Hammerstein takes
a query string + retrieved corpus context and emits structured
strategic reasoning. This doc scopes what `--image PATH` would add,
which use cases earn the surface, and what a v0 ship looks like.

## Why this is worth scoping at all

Three of Ray's active projects hand the operator a screenshot and
ask "is this on register / on plan / shipped-quality?":

- **Visual register audits** — TWAR PC + GTA + AMFIOG + FnordOS all
  hit the surface where a Claude Design output (or an in-engine
  screenshot) needs an adversarial reading against the locked
  register doc. Today's TWAR S5 incident is the canonical case:
  Cursor's hex-grid first pass needed the "this is hex but the
  reference game is area-based" catch. A vision-equipped audit
  could have caught it pre-flight from the screenshot alone.
- **Sprite + asset critique** — retrogaze rg-023's Haiku/Sonnet
  bake-off rubric scoring is exactly this shape; today the human
  (Claude orchestration session) did it because vision-Hammerstein
  doesn't exist. With it: route the rubric to Hammerstein.
- **Code-screenshot audits** — pasting a terminal error or a chunk
  of code as a screenshot for a quick "what's wrong here." Lower
  value than the design-audit cases (text paste works), but the
  capability comes free with the others.

The framework principle holds: vision input doesn't change what
Hammerstein DOES (adversarial framing, Plain English summary,
counter-observation), only what it can SEE.

## v0 use case prioritization (lean)

Three candidate v0 use cases ranked by leverage:

1. **`audit-this-visual`** — accept image + plan text. "Audit this
   CD output (screenshot) against this register lock-doc (text)."
   Highest-leverage because it's the gap that almost cost the TWAR
   PC Surface 5 work today; running the audit on the visual itself,
   not just the brief, would have flagged the hex grid before
   Cursor implemented it. (Renamed from `audit-this-design` per
   audit's collision-with-architectural-design argument.)
2. **`read-this-screenshot`** — image-only audit with auto-classified
   template. "Here's a screenshot, do something useful with it."
   Lower priority; the auto-classifier already handles bare-text
   queries, vision version is the same shape extended.
3. **Image-as-context for existing templates** — extend `audit-this-plan`
   / `what-should-we-do-next` / `is-this-worth-doing` with optional
   `--image` to ground reasoning in a visual artifact. Useful but
   diffuse; ship after the dedicated `audit-this-design` template
   proves the pattern.

**v0 lean: ship `audit-this-visual` only.** Prove the pattern on
the highest-leverage case. Other surfaces extend in v1 once the
provider/cost discipline is calibrated.

`[LOCK: ship audit-this-visual first; defer the others to v1]`

## Provider matrix (vision-capable, current)

Of Hammerstein's existing backend list (ollama / openrouter / deepseek
/ claude), vision support is uneven:

| Backend | Vision-capable model | Notes |
|---|---|---|
| **claude** | Sonnet 4.6 / Opus 4.7 (native) | Highest quality; subscription-billed; most expensive on raw API. |
| **openrouter** | qwen/qwen3-vl-plus, GPT-4o, Gemini 2.0 Flash, Claude via OpenRouter | Mix of paid + free; Gemini 2.0 Flash is free tier. |
| **deepseek** | deepseek-vision (if available; check) | Already in Ray's paid roster; cost discipline aligns. |
| **ollama** | LLaVA, Llama 3.2 Vision, Qwen2-VL | Local; constrained by today's RTX 3050 6GB lesson — vision models tend to be larger than chat-only at the same param count. Probably non-viable on home-PC at quality bar; viable on Mac for small images. |

**Routing lean (revised post-routing-audit 2026-05-06):**
Vision-Hammerstein audits are LOW-FREQUENCY / HIGH-VALUE (5-20 calls
per week, each representing a register-quality decision worth hours
of downstream design work). Free-tier-first routing is the wrong
axis at this volume — saving pennies on calls where one missed catch
costs hours optimizes the wrong thing.

**Default to PAID** at v0. Specific default locked by pre-v0 bake-off
(see ship gate below):

- **If Qwen3-VL-Plus passes 3/3 shape-gate AND ≥2/3 semantic on the
  benchmark cases:** lock `openrouter:qwen/qwen3-vl-plus` as
  default + `openrouter:openai/gpt-4o` as single-step auto-failover
  on shape-gate fail. ~$0.01-0.05/call.
- **If Qwen fails any shape-gate OR <2/3 semantic:** lock
  `openrouter:openai/gpt-4o` as flat default, no failover. Per
  the routing audit's counter-observation: eliminating routing
  complexity is worth the +$0.04/call when weekly volume is 5-20
  (~$1/week max). Simpler beats clever.

**Failover cap:** 1 automatic failover per audit. If GPT-4o also
fails shape-gate, return structured error to operator. No retry
chains.

**`--backend-tier free` flag** exposes free Gemini 2.0 Flash for
cost-curious experiments and batch eval runs; non-default profile,
never auto-selected.

**DeepSeek v4 vision** included in the bake-off ONLY if startup
API capability probe (silent endpoint ping) confirms vision
support. Unverified, excluded — no dead paths in routing table.
If verified + competitive on bake-off, becomes Mac-favored default
given Mac-Neo's existing paid DeepSeek routing.

**Skip ollama for vision-Hammerstein in v0** per today's "RTX 3050
can't carry adversarial reasoning quality" verdict. Mac-Neo can
opt-in via env var if a future Mac vision model proves out.

**Claude vision** never as default (Hard Rule on conserving
subscription); available via explicit `--model claude:sonnet-4.6`
override.

`[LOCK: paid default; specific lock decided by pre-v0 bake-off
(Qwen3-VL-Plus default + GPT-4o failover, OR GPT-4o flat); failover
cap=1; --backend-tier free non-default; DeepSeek conditional on
API probe; Claude explicit-override-only]`

## API shape

Single new flag on the existing `hammerstein` CLI:

```
hammerstein --template audit-this-design --image path/to/screenshot.png "<plan-text>"
```

Concrete decisions:

- **`--image PATH`** — single file path. PNG / JPG / WebP accepted.
  Rejected if the file doesn't exist or doesn't decode.
- **`--backend-tier {free,paid}`** — explicit operator-deterministic
  override. Free is the default; `paid` forces the paid pool.
- **No `--image-base64`** in v0; cleanly load from disk.
- **No multi-image** in v0 — one screenshot per call. v1 if a use
  case demands "compare these two layouts."
- **Image + plan text** are both required for `audit-this-visual`;
  the template instructions tell the model to read the image as the
  proposed artifact and the text as the standard / register / plan
  it should match.
- **No image preprocessing** in Hammerstein (no auto-resize,
  no OCR-first). Provider APIs handle resizing; OCR-first is a
  separate tool's job.
- **Output-shape gate** — post-run regex check that the response
  matches `^\*\*Plain English summary:\*\*[\s\S]+---[\s\S]+$`. On
  fail: log raw response, retry once on paid tier (auto-failover),
  log retry outcome. If retry also fails shape-gate, exit non-zero
  with diagnostic. Prompt-level negative constraints in the
  template ("Do not add greetings, conversational framing, or
  markdown outside the specified structure") supplement the gate.
- **Output contract unchanged** — same Plain English summary +
  audit body that text-only Hammerstein produces, gate-validated.
  Downstream consumers (`brief.ts`) keep working.

`[LOCK: --image PATH single file; --backend-tier free|paid;
PNG/JPG/WebP; no preprocessing; shape-gate enforced; output
contract preserved]`

## Cost discipline

Vision input tokens are 2-5x text tokens by default (provider-dependent).
For OpenRouter Gemini 2.0 Flash free tier this is moot. For paid
fallbacks:

- Cap a single `audit-this-design` call at ~5000 input tokens
  total (image + text + corpus snippet + template). Most screenshots
  fit well under this; large dashboards may not.
- No automatic retry-with-larger-model on quality failure. If
  Gemini 2.0 Flash free returns nonsense, the operator escalates
  manually with `--model openrouter:openai/gpt-4o`.
- Log image dimensions + estimated input tokens in the
  `[backend=... cost_usd=...]` metadata line so the operator can
  see what each call cost.

`[LOCK: no auto-retry; metadata line includes image dimensions]`

## Template content

`prompts/templates/audit-this-visual.md` — new file. Structure
mirrors `audit-this-plan.md` with these adjustments:

- Explicit instruction to READ the image first as the artifact
  under audit, then read the text as the standard/register the
  artifact should match.
- **Negative formatting constraints** at the top of the template:
  "Do not add greetings, conversational framing, preamble, or
  markdown outside the specified structure. Return exactly the
  Plain English summary section followed by `---` followed by
  the audit body." This is the prompt-level supplement to the
  output-shape gate.
- "Failure modes" section reframed for visual artifacts:
  register-mismatch (genre default vs reference convention),
  scope-bloat (more elements than the brief asked for),
  reference-violation (specific anti-patterns in the image),
  load-bearing-detail-missing (something the brief required
  that the image lacks).
- "Counter-observation" section unchanged — same reflexive
  challenge to the audit's own conclusions.
- "Plain English summary" section unchanged — downstream contract
  preserved.

## v0 / v1 axis

| Dimension | v0 | v1 |
|---|---|---|
| Templates | `audit-this-visual` only | + `read-this-screenshot`, + `--image` extension on existing templates |
| Backends | OpenRouter Gemini Flash free + paid Qwen-VL / GPT-4o fallback | + Claude vision (subscription routing), + deepseek-vision (if available) |
| Image inputs | Single file, PNG/JPG/WebP | Multi-image (compare-these-layouts), URL-as-image (web screenshot capture) |
| Hardware | Cloud only | + Mac-local LLaVA / Llama Vision opt-in if quality proves out |
| Eval | 3-5 hand-curated test cases (TWAR S5 hex-grid, retrogaze sprite, FnordOS register) | Full eval suite parallel to text-only v0 |
| Ship gate | "audit-this-visual catches the TWAR S5 hex-grid issue when given the brief + the implementation screenshot, AND output-shape gate passes 3/3 on benchmark cases" | "vision audits match text-only audit quality on the same eval suite" |

## v0 benchmark cases

Three real artifacts where we know the right answer:

1. **TWAR PC Surface 5 hex-grid first pass** (today). Image:
   `twar-pc-private/design/cd-output/surface-5.html` rendered
   screenshot. Plan text: the corrected (post-fix) Surface 5 brief.
   **Right answer:** "the implementation uses hex but the brief
   specifies area-based province nodes; this violates the
   ROTK-IV reverse-engineering thesis."
2. **Retrogaze rg-023 Sonnet bake-off cell** (today). Image:
   one of the 16x16 sprites. Plan text: the rg-023 rubric
   criteria + craft floor. **Right answer:** "scores below the
   ≥7/10 craft bar on shade-discipline / clean-pixels / silhouette
   axes; specifies which."
3. **FnordOS cinematic intro screenshot** (fnord-006). Image:
   the post-intro DEPT-23 panel. Plan text: design/REGISTER.md
   16-color Bureau Palette + typography rules. **Right answer:**
   "register match" or "drift on X axis" with specifics.

Ship gate: `audit-this-visual` produces the right verdict on at
least 2 of 3 with the OpenRouter Gemini Flash free default, and
on 3 of 3 with the GPT-4o paid fallback. **Benchmark isolation
required:** zero cached context, raw model responses recorded
alongside parsed results, shape-gate failures count as misses
regardless of semantic correctness. Audit's counter-observation:
if all 3 cases parse shape-clean on the free tier without the
gate, the gate is removable post-eval — but ship with it.

## Out of scope

- Image generation (Hammerstein reasons; doesn't generate).
- Video / multi-frame analysis (single PNG only).
- OCR-as-primary (delegate to a real OCR tool first if extracting
  text from images matters; vision models do OCR but it's not
  Hammerstein's job to be the OCR layer).
- Visual diff / pixel-comparison (separate tool).
- Local Ollama vision support on RTX 3050 home-PC (per today's
  hardware verdict).

## Open design-axis questions for Ray

Both initial audits (scope + routing) resolved the open questions
into structural decisions. Original list (template name, default
backend, ship gate threshold) is closed:

- Template name → `audit-this-visual` (scope audit; collision-with-
  architectural-design).
- Default backend → paid by default; specific lock (Qwen3-VL-Plus
  vs GPT-4o flat) decided by pre-v0 bake-off (routing audit).
- Ship gate threshold → bake-off-driven; either Qwen 3/3 shape +
  ≥2/3 semantic earns Qwen-default, OR GPT-4o flat. v0 doesn't
  merge until one of the two locks resolves.

Remaining for Ray's call (none load-bearing for v0 implementation
start):

- **DeepSeek inclusion timing** — implement v4 capability probe at
  startup (current scope) vs defer DeepSeek entirely to v1 once Ray
  separately verifies vision endpoint. Lean: implement the probe
  (silent failure, no dead path) so DeepSeek can drop in seamlessly
  if/when verified. Trivial code; no risk.

## Implementation arc (post-Ray-approval)

Five commits — bake-off is now part of the arc, not post-ship.
Sized similar to fnord-007:

1. **`prompts/templates/audit-this-visual.md`** + tests covering
   template loading + corpus retrieval (no image) + the negative
   formatting constraints — proves the template plumbs.
2. **`harness/hammerstein/cli.py` + `backends.py`** — `--image`
   and `--backend-tier` flags, file-load + base64-encode for
   backend dispatch, metadata line extension. Per-backend
   image-input handling (OpenAI-shape for OpenRouter,
   Anthropic-shape for claude). DeepSeek capability probe at
   startup (silent exclude on 404).
3. **`harness/hammerstein/shape_gate.py`** (or inline in cli.py
   if light) — regex validator + state-machine failover (cap=1)
   + raw-response logging on fail. Failover cap returns
   structured error after one retry; no chains.
4. **3 benchmark cases at `tests/test_vision_audit.py`** —
   fixtures (TWAR S5 hex-grid screenshot, retrogaze rg-023
   sprite, FnordOS cinematic intro screenshot) + expected
   verdicts + shape-gate assertion + raw-response recording.
5. **Bake-off run + default-lock commit.** Run all 3 benchmark
   cases through Qwen3-VL-Plus, GPT-4o, and DeepSeek (if probe
   succeeded). Record results. Apply the decision tree (Qwen
   default vs GPT-4o flat). Commit the routing config update
   with bake-off results as the audit trail. **v0 does not merge
   until this commit lands.**

Effort: ~half a day of focused work, less if Cursor IDE Auto
handles bulk per the fnord-007 precedent. Bake-off step adds
~30-60 min including writing the result analysis.

---

## Pre-flight Hammerstein audits (DONE — both)

Two audits ran on this scope. Verbatims preserved alongside.

**Audit 1: scope + structure** (2026-05-06 evening,
`HAMMERSTEIN-AUDIT-2026-05-06-VISION-SUPPORT.md`).
$0.00879 OpenRouter qwen/qwen3.6-plus, 59.4s. Verdict: ship
with modifications. Four catches applied:

1. Template renamed `audit-this-design` → `audit-this-visual`
   (collision with architectural design audits).
2. Output-shape gate added (regex on returned format, log raw
   on fail) — vision models drift toward conversational framing
   which would silently break `brief.ts`.
3. Fallback determinism — explicit `--backend-tier paid` flag +
   auto-failover on shape-gate fail. Replaces the original
   "operator escalation" handwave.
4. Benchmark isolation methodology added — zero cache, raw
   responses recorded, shape-gate failures count as misses.

**Audit 2: default-backend routing** (2026-05-06 evening,
`HAMMERSTEIN-AUDIT-2026-05-06-VISION-ROUTING.md`).
$0.01135 OpenRouter qwen/qwen3.6-plus, 85.2s. Verdict: ship
with modifications. Four catches + load-bearing
counter-observation applied:

1. Bake-off moved pre-v0 merge (post-v0 timing was
   stupid-industrious drift — shipping with untested default
   risks live-audit hotfix).
2. Failover cap = 1 hardened (no retry chains; structured
   error to operator after one failover fail).
3. DeepSeek API capability probe at startup (silent exclude on
   404; no dead paths).
4. `--backend-tier free` routed through non-default profile
   (never auto-selected).

Counter-observation applied as the decision tree's else-branch:
if Qwen3-VL-Plus fails any benchmark case, default flips to
GPT-4o flat (no failover). Routing complexity is the wrong tax
to pay at this call volume; +$0.04/call eliminates the failover
state machine entirely. Simpler beats clever when both are
materially affordable.
