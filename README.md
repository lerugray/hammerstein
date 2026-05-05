# Hammerstein

![Hammerstein — A framework that survives the model. Clever-lazy · Verify · Legible failure](docs/images/banner.png)

Hammerstein is a strategic-reasoning assistant tuned to the Hammerstein framework.
The load-bearing artifact is the framework encoded as a portable system prompt plus a small retrieved corpus.
This repo exists to make that reasoning style available even when the underlying model or provider changes.

> **Status:** v0 harness shipped. Reference corpus included. Provider fallback chain (OpenRouter → DeepSeek → Ollama) ships continuity by default.

## What this is

Hammerstein is a **focused strategic-reasoning model** — not a general-purpose
AI. It's tuned to think the way the Hammerstein framework prescribes:
clever-lazy over stupid-industrious, verification over enthusiasm, legible
failure over hidden success, "bring your own imagination" over generic
generation.

The project's load-bearing artifact is **the framework itself encoded as
portable system-prompt + RAG infrastructure** — so any underlying model
(Claude when affordable, paid Qwen on OpenRouter, local Llama/Qwen via
Ollama, future open-weight models) can reason in Hammerstein-style on demand.

## Example

*A typical strategic-reasoning consult — the framework ranks options, names what to deprioritize, and surfaces a counter-observation that could change the call.*

**Query**

It is Tuesday morning. I have 2 hours. Options: (a) draft the benchmark questions, (b) harden the RAG retrieval, (c) add more corpus entries, (d) run the harness end to end and record one baseline run. What should I do first?

**Response (abbreviated)**

This is clever-industrious work with an easy stupid-industrious trap: adding corpus before you can measure whether retrieval works.

1. Run (d) and record a baseline run. You need a working loop before you add more inputs.
2. Draft (a) as a short locked list. Five questions is enough to start.
3. Harden (b) only after the baseline tells you what broke.

Deprioritize (c) for now. More examples do not help if the harness cannot retrieve the right ones.

Counter-observation: if the baseline run already produces useful retrieval and the failure is prompt shape, skip retrieval hardening and spend the remaining time tightening the system prompt instead.

## What this is NOT

- **Not a Claude Code clone.** Code work continues to route through OpenRouter
  (paid Qwen Coder Plus / DeepSeek) or whatever Cursor IDE Auto provides.
  Hammerstein is for strategic thinking, not bulk code generation.
- **Not a from-scratch model.** Pre-training a foundation model is decisively
  out of scope. The realistic ceiling is fine-tuning a small open-weight
  model (Qwen 8B / Llama 3.1 8B-70B) — and that's only after the
  prompt-engineering + RAG path proves insufficient.
- **Not a daily-driver replacement** for Claude (yet). It's a fallback +
  business-continuity layer that becomes primary if Claude becomes
  unavailable or unaffordable.

## Why it exists

The portfolio survives an Anthropic outage / account ban / affordability
collapse for **code work** — cursor-agent CLI + OpenRouter Qwen + Gemini
CLI + Ollama already cover it. The gap is **strategic reasoning** — the
staff-officer / orchestrator role that interactive Claude currently fills.
No existing fallback matches it.

Hammerstein closes that gap. The framework is more important than the
model — once the framework is encoded portably, any underlying model can
fill the strategic-reasoning role.

## Customize the corpus

The corpus shipped here (`corpus/entries/`) is a **reference implementation**
— a small curated set of Hammerstein-style reasoning entries that
illustrate the framework's structure. It's not meant to be authoritative
for every operator.

**To make Hammerstein useful for your specific work:**

1. Clone this repo.
2. Read `research/HAMMERSTEIN-FRAMEWORK.md` for the framework synthesis.
3. Replace or augment `corpus/entries/` with reasoning examples drawn from
   your own work — incidents where you caught a stupid-industrious trap,
   structural fixes that compounded, verification-gates that paid off,
   counter-observations that reshaped a plan. The provenance + framing
   pattern (one principle per entry; tagged with quadrant + principle +
   source + quality) generalizes; the specific examples shouldn't.
4. Update `corpus/CORPUS-CURATION.md` to index your entries.
5. Optionally tune `prompts/SYSTEM-PROMPT.md` for your project's idiom.

The framework structure (system prompt + few-shot templates + retrieval
layer + provider fallback chain) transfers as-is. The corpus content is
yours to author.

## Quickstart

```bash
# Requires Python 3.11+
pip install -e .
export OPENROUTER_API_KEY="..."

hammerstein "What's the highest-leverage move for me this week given X, Y, Z?"
```

The harness reads `providers.yaml` for the fallback chain and routes through
OpenRouter (qwen3.6-plus) by default, with auto-fallover to a secondary OpenRouter model, DeepSeek, and Ollama if the primary fails. See `harness/README.md` for the full flag set
and `tests/test_continuity_chain.py` for the smoke-test harness.

## `hsh` — Hammerstein Shell (Continuity Track Phase 2)

For operators who prefer a conversational, stay-in-the-environment workflow,
`hsh` drops you into an interactive REPL with bounded prior-turn context.
Type prose, get an audit, push back with more prose, get a refined audit —
the iteration pattern that makes strategic-reasoning tools actually useful
in real work.

```
$ hsh
Hammerstein Shell (hsh) — interactive strategic-reasoning environment
Type :help for commands, :exit or Ctrl-D to quit.
Rolling context capped at 3 turns.

hsh:my-project> should I refactor the auth flow this week?
[runs audit-this-plan with full adversarial review streamed live]

hsh:my-project> what if the auth flow is downstream of a billing change?
[runs audit again, with prior turn injected as background context]

hsh:my-project> :d add a TODO comment to auth.py noting the dependency
[invokes `hd` for actual code work — full audit + aider dispatch]

hsh:my-project> !git status
[bash passthrough]

hsh:my-project> :exit
```

Architectural design (override of audit 3's strict reading; preserves spirit):

- **Each Hammerstein-template call is still a discrete fresh invocation.**
  No conversation history dumped into the few-shot template; corpus
  retrieval is fresh per turn.
- **Bounded prior-turn context (last 3 turns)** is injected as a prefix to
  each new query so operator iteration works ("apply the same fix to X",
  "given Y, retry"). Capped to prevent unbounded conversation hosting.
- **Default action on plain prose is `audit-this-plan`** (read-only
  thinking). Dispatch (which mutates files + commits) requires explicit
  `:d` verb to prevent accidental execution — the one piece of audit 3's
  verb-friction guidance that is preserved as load-bearing.
- **Aider still owns conversation state, file edits, git operations** when
  invoked via `:d`. State-ownership boundary is intact.
- **Project state file (`:state`)**: If a `.hammerstein-state.md` file exists
  in the project root (detected by walking up to the nearest project marker —
  `.git`, `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, `Gemfile`,
  or `requirements.txt`), its contents are automatically injected as a
  preamble before the rolling context on every template call. Use `:state` to
  view it; `:state edit` opens it in `$EDITOR` (nano fallback) and creates the
  file at project root if missing. This lets you persist high-level project
  constraints, active goals, or architectural decisions across shell sessions
  without polluting the rolling turn buffer.

Falsification gate: if `hsh` produces noticeably worse audits than
fresh-from-cold `hammerstein` calls — i.e., the bounded-context injection
corrupts framework reasoning — kill the rolling-context injection and fall
back to verb-only mode. Empirically testable: compare hsh audit quality vs
fresh audit on the same query.

## `hd` — Hammerstein Dispatch (Continuity Track Phase 1)

A second console command, `hd`, ships alongside `hammerstein`. It's the
Continuity Track's Phase 1: a thin wrapper that takes operator prose,
runs it through Hammerstein's audit-this-plan pre-flight, and dispatches
to [aider](https://aider.chat/) for the actual file editing + git work.
The intent is to make Hammerstein viable as a daily driver substitute
for tools like Claude Code when the underlying provider is unavailable
or quota-constrained.

```bash
# Default: audit, confirm, dispatch via OpenRouter Qwen3.6-plus
hd "fix the typing-collision bug in cli.py"

# Skip the audit pre-flight for trivial tasks
hd --no-audit "rename foo to bar across these files"

# Force a specific provider
hd --provider claude "design pass on the auth flow"
hd --provider deepseek-chat "draft a README section about X"
hd --provider openrouter-coder "refactor the parser for readability"

# Show planned aider invocation without executing
hd --dry-run "..."

# List the routing table
hd --list-providers
```

State-ownership boundary (load-bearing): Hammerstein owns audit + scope +
route + dispatch. Aider owns file editing, conversation state, tool-use
loops, git operations. The wrapper does NOT track chat history, manage
.git, or parse LLM tool-calls — those are aider's job. If the wrapper
starts doing them, it has crossed into reinventing Claude Code.

Provider routing table:

| Provider           | Model                              | Key env             |
|--------------------|------------------------------------|---------------------|
| `openrouter`       | `openrouter/qwen/qwen3.6-plus`     | `OPENROUTER_API_KEY`|
| `openrouter-coder` | `openrouter/qwen/qwen3-coder-plus` | `OPENROUTER_API_KEY`|
| `deepseek`         | `deepseek/deepseek-chat`           | `DEEPSEEK_API_KEY`  |
| `claude`           | `claude-sonnet-4-6`                | `ANTHROPIC_API_KEY` |
| `claude-opus`      | `claude-opus-4-7`                  | `ANTHROPIC_API_KEY` |
| `ollama`           | `ollama/qwen3:8b`                  | (none — local)      |

Dispatch logs land at `~/.hammerstein/logs/dispatches.jsonl` (separate
from the audit-call log at `~/.hammerstein/logs/hammerstein-calls.jsonl`).

### Phase 1 scope (this release)

- Single-shot dispatch (no multi-turn conversation state in the wrapper)
- Single-tool downstream (aider only — cursor-agent in Phase 2)
- Explicit provider selection (auto / quota-aware routing in Phase 3)
- No file-detection logic (operator passes `--file` flags or aider's
  repo-map handles it)

### Falsification gate

Phase 1 is on a 14-day window. If the operator hasn't dispatched at
least one real coding task via `hd` in 14 days, the architecture is
wrong (the orchestrator vision doesn't match observed behavior) and
the Continuity Track should be reconsidered.

## Companion shell utilities

Three thin shell scripts surface the corpus, call log, and usage stats for terminal-native workflows. POSIX shell + `fzf` + `bat` + `jq`; zero UI framework.

```bash
# Add scripts/ to PATH (or symlink hquery / hlog into ~/.local/bin/)
export PATH="$PATH:$(pwd)/scripts"

hquery                    # fuzzy-search corpus entries (fzf + bat preview)
hquery "framework"        # pre-populate the search field
hlog                      # last 20 calls, column-aligned
hlog 50                   # last N calls
hlog | grep audit         # filter by template / query substring
hstats                    # last 7 days usage stats (calls, cost, templates, hosts)
hstats --gate             # 7-day window + explicit Phase A → Phase B verdict
hstats --by-host          # cross-machine usage breakdown
```

`hquery` requires `fzf` (`brew install fzf` on Mac, `apt install fzf` on
Linux). `bat` is preferred for syntax-highlighted preview; falls back to
`cat` if absent. `hlog` and `hstats` require `jq` (effectively ubiquitous).
The call log lives at `~/.hammerstein/logs/hammerstein-calls.jsonl`
(auto-created on first call; not in cwd). Each entry stamps the host,
so `hstats --by-host` works across machines if you sync the log.

## How the layers compose

| Layer | Where | What |
|---|---|---|
| Framework synthesis | `research/HAMMERSTEIN-FRAMEWORK.md` | Cross-source distillation of the framework's principles |
| Mechanical spec | `design/PILLARS.md` | Framework as mechanical pillars |
| Phased roadmap | `scope/PHASED-ROADMAP.md` | v0 / v1 / v2 trajectory |
| System prompt | `prompts/SYSTEM-PROMPT.md` | The identity-framing prompt every call carries |
| Templates | `prompts/templates/*.md` | Few-shot exemplars for 5 query shapes |
| Corpus | `corpus/entries/*.md` | Retrieved examples — your own to curate |
| Stack | `tech/STACK-DECISION.md` | Provider + model decisions, fallback chain rationale |
| Harness | `harness/`, `hammerstein_cli/` | The Python CLI that ties it together |
| Eval | `eval/`, `tests/` | Benchmarks + continuity smoke tests |

## License

[MIT](LICENSE)

---

*Hammerstein-Equord, Kurt Freiherr von (1878-1943). Chief of the German Army
Command 1930-1934. Surfaced the officer typology — clever-lazy / clever-
industrious / stupid-lazy / stupid-industrious — that anchors this project's
namesake framework.*
