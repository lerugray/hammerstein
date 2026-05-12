# Changelog

All notable changes to Hammerstein are documented here. The format is loosely
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the
project follows semver where the public CLI surface (`hammerstein`, `hd`,
`hsh`) is the contract.

## [Unreleased]

## [1.2] — 2026-05-12

### Added

- **`hammerstein --context none|minimal`** — opt-in project context injection. `minimal` prepends a bounded preamble to user queries: repo identity (remote / branch / HEAD / dirty) + capped excerpts from `MISSION.md` / `CLAUDE.md` / `AGENTS.md` / `README.md` (600 chars each, 1600 total docs budget) + optional auto-discovered state file (`.hammerstein-state.md` or `hammerstein_state.md`, 800 chars). Hard cap 2.2k chars with documented drop priority. CLI default is `none`; templates `audit-this-plan` and `what-should-we-do-next` default to `minimal` (override with explicit `--context none`). v0 intentionally does **not** inject git diffs / logs / trees / cached state.
- **`--project-root <path>`** + **`--context-file <path>`** — override git-root detection and provide an explicit context file (the preferred grounding mechanism). Context files must live under the project root.
- **`hammerstein --image <path>`** — multimodal image input on the typer CLI. Pairs with `--template audit-this-visual` for vision-Hammerstein audits (rulebook diagrams, sprite quality reviews, board photos, etc.). Per-invocation validation enforces the file-exists check and the template-image pairing before dispatching to the harness.
- **`--backend-tier free|paid`** — explicit backend tier selector for vision audits. `free` routes through the free vision pool (Gemini Flash via OpenRouter); `paid` forces the paid pool default. Omitted defaults to the providers.yaml fallback chain.
- **`audit-this-visual` template** is now reachable via the typer CLI. The template was already wired into the corpus (`corpus.py:153`), prompt template (`prompts/templates/audit-this-visual.md`), and shape gate (`harness/hammerstein/shape_gate.py`); the classifier just hadn't been told it existed.

### Fixed

- **`--image` was unreachable via the installed `hammerstein` command.** The argparse parser in `harness/hammerstein/cli.py:765` carried the option, but the typer entry at `hammerstein_cli/__init__.py` (the actual installed entry point) never wired it in. Both `--image` and `--backend-tier` now flow through with the same per-invocation validation the argparse path had.
- **`audit-this-visual` was missing from `classifier.TEMPLATES`** despite being a valid template across the rest of the harness — the validation check at `cli.py:358` would reject it. Now present in the tuple. Auto-classification still routes non-image queries to the existing five templates; vision audits remain explicit (must pass both `--image` and `--template audit-this-visual`).

### Security

- Context injection denylists sensitive filenames (`.env`, `.pem`, `id_rsa`, `credentials*`, files named `secret` / `token` / `api_key`), refuses symlinks, scrubs absolute repo paths down to basenames, and **aborts injection entirely** if high-entropy credential patterns appear in candidate excerpts (OpenAI `sk-`, GitHub `ghp_`, Google `AIza`, AWS `AKIA` / `ASIA`, Slack `xox`, PEM blocks, long hex / base64). v0 chooses abort over redaction by design — operator gets a single-line stderr warning and the call continues with no context.

### Docs

- README benchmark headline corrected. The v0.1 short-answer (`the system prompt alone is doing the work, not the RAG corpus`) reflected the Sonnet-only ablation result; the v0.2 cross-family ablation (already documented further down in the same section) refuted it — on Opus 4.7 all three configurations are statistically tied, and on GPT-5 corpus-only actually outperforms the full stack. Lead claim now reflects what holds across all four runs: 53 of 54 = 98.1% Hammerstein-over-raw win rate, with the component-contribution claim qualified as model-dependent.

## [1.1] — 2026-05-05

### Added

- **`hd --provider claude-code`** — subscription-backed dispatch path that
  routes through `claude -p` headless mode instead of aider. Uses the
  operator's Claude Code Pro/Max subscription quota; no `ANTHROPIC_API_KEY`
  needed. Audit pre-flight still runs through OpenRouter; the costly
  dispatch lands on the subscription. Especially relevant for Pro-tier
  users with tight rate limits who don't want to pay twice for the same
  model access.
- **`hd --provider cursor-agent`** — subscription-backed dispatch path that
  routes through `cursor-agent -p --trust` headless mode. Uses the
  operator's Cursor subscription quota (free composer-2-fast tier covers
  most tasks). Same audit-then-dispatch pattern as `claude-code`.
- Internal `executor` field on the `PROVIDERS` table — `aider` (default),
  `claude-code`, or `cursor-agent`. Future executors can land via the
  same field with similar effort.
- Aider-only flags (`--file`, `--read`, `--architect`, `--no-auto-commits`)
  now warn-and-ignore when used with non-aider executors, with guidance to
  mention file references in the prose since the underlying agent finds
  them via its own tool use.

### Changed

- `hd` Phase 1 falsification gate marked **CLEARED** — Phase 3 of the
  Continuity Track (state-file injection) was implemented BY `hd`
  dispatching to aider, validating that the orchestrator vision matches
  observed behavior. README updated to reflect.

## [1.0] — 2026-05-05

Initial release. Full notes:
[github.com/lerugray/hammerstein/releases/tag/v1.0](https://github.com/lerugray/hammerstein/releases/tag/v1.0).

### Added

- **Continuity Track (full)** — `hammerstein` CLI for one-shot strategic
  queries, `hd` dispatch wrapper (audits + routes to aider), `hsh`
  interactive shell with bounded 3-turn rolling context and
  `.hammerstein-state.md` project state file injection.
- **Plain English summary** in all 5 templates (audit-this-plan,
  scope-this-idea, is-this-worth-doing, what-should-we-do-next,
  review-from-different-angle) — every response leads with a jargon-free
  2-4 sentence verdict before the framework analysis.
- **`h` quick-fire wrappers** (POSIX shell + PowerShell) mapping verb
  shortcuts to template flags: `h audit "<plan>"`, `h next "<context>"`,
  `h scope "<idea>"`, `h worth "<proposal>"`, `h sharper "<position>"`.
- **Provider fallback chain — validated end-to-end.** OpenRouter
  qwen3.6-plus primary → qwen3-coder-plus → DeepSeek deepseek-chat →
  Ollama qwen3:8b local. Operates through Anthropic outage, account ban,
  or affordability collapse.
- **Daily-brief integration** — tested in production via Gmail SMTP send.
  Morning + evening briefs include a Hammerstein strategic-reasoning take
  rendered in Plain English.
- **Cross-platform** — pyreadline3 fallback for `hsh`, UTF-8 stdout
  reconfigure in `cli.py` so piped output doesn't crash on em-dashes /
  smart quotes (Windows cp1252 default).
- Reference corpus of 28 universalizable framework entries; bring-your-own
  corpus pattern documented.
- Companion shell utilities (`hquery`, `hlog`, `hstats`) for terminal-
  native corpus search, call history, and usage stats.

### Known gaps at v1.0

- `tests/test_continuity_chain.py` ollama-local step is fragile on Windows
  (tracked as ham-017). Real-world `hammerstein --model ollama` calls work
  fine; the marker-strict test fails on variable local-model output.
- Vision support (PNG evaluation) is open territory, not yet committed.
- Eval-vs-Claude over a meaningful daily-driver period is operator-
  individual; not built in.
