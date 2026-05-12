# Hammerstein

![Hammerstein — A framework that survives the model. Clever-lazy · Verify · Legible failure](docs/images/banner.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Status: v1.0](https://img.shields.io/badge/status-v1.0-success.svg)](https://github.com/lerugray/hammerstein/releases)

Hammerstein is a strategic-reasoning assistant tuned to the Hammerstein framework.
The load-bearing artifact is the framework encoded as a portable system prompt plus a small retrieved corpus.
This repo exists to make that reasoning style available even when the underlying model or provider changes.

> **Status:** v1.0 shipped. Continuity Track complete (`hammerstein` CLI + `hd` dispatch wrapper + `hsh` interactive shell). Plain English summaries across all 5 templates so non-programmer operators can evaluate output without parsing framework vocabulary. Provider fallback chain (OpenRouter → DeepSeek → Ollama) validated end-to-end; daily-brief integration tested in production.

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

**Plain English summary:** Run a single end-to-end test with what you already have first — that's the only way to know what's actually broken. Drafting more questions or adding more corpus entries before that is guesswork. Five questions is enough to start; tighten the retrieval layer only after the test tells you what failed.

---

This is clever-industrious work with an easy stupid-industrious trap: adding corpus before you can measure whether retrieval works.

1. Run (d) and record a baseline run. You need a working loop before you add more inputs.
2. Draft (a) as a short locked list. Five questions is enough to start.
3. Harden (b) only after the baseline tells you what broke.

Deprioritize (c) for now. More examples do not help if the harness cannot retrieve the right ones.

Counter-observation: if the baseline run already produces useful retrieval and the failure is prompt shape, skip retrieval hardening and spend the remaining time tightening the system prompt instead.

## Benchmark — does the framework actually help?

**Yes, by a wide margin: 53 of 54 blind LLM-judge ratings preferred Hammerstein-on-frontier over raw frontier models. Which component delivers the lift is model-dependent.**

We ran a two-pass benchmark on 2026-05-10. v0 measured Hammerstein-vs-raw on 6 strategic-reasoning questions × 3 frontier families × 3 LLM judges. v0.1 stress-tested the result with a 4th vendor judge (DeepSeek), 4 generic out-of-domain questions, and a prompt-vs-corpus ablation. v0.2 extended the ablation across all 3 frontier families and complicated the original "system prompt is load-bearing" reading — see § "v0.2 update" below. Full methodology + verdicts in `eval/RESULTS-v0.1.md`.

### v0 — main result

6 questions (Q1–Q6 from `eval/BENCHMARK-v0.md`) × 3 frontier model families (Opus 4.7, Sonnet 4.6, GPT-5) × {raw model, Hammerstein-on-frontier} = 36 responses. Then blind LLM-judge head-to-head, position-randomized, scored on framework-fidelity / usefulness / voice-match plus overall preference.

**Result with the 4-judge panel (Opus, Sonnet, GPT-5, DeepSeek): 53 of 54 parsed ratings preferred Hammerstein-on-frontier. Win-rate 98.1%.**

| Family | n | Hammerstein wins | Raw wins | Win-rate |
|---|---|---|---|---|
| Claude Opus 4.7 | 18 | 18 | 0 | 100% |
| Claude Sonnet 4.6 | 18 | 17 | 1 | 94.4% |
| GPT-5 | 18 | 18 | 0 | 100% |

The single raw-pick was DeepSeek on Q2/Sonnet — one outlier across 54 ratings.

### v0.1 — three caveats stress-tested

The v0 result invites three obvious challenges. We ran each.

**Caveat 1 — does the framework win because the corpus matched the question?** We added 4 generic strategic-reasoning questions (Q9–Q12 in `eval/BENCHMARK-v0.1.md`: DB optimization meta-question, B2B SaaS prepaid contract, PhD dissertation third experiment, 4-person product team allocation) constructed to fall outside any specific domain. The Hammerstein corpus has nothing relevant to retrieve.

**Result: 48 of 48 ratings preferred Hammerstein. 100% across all 4 judges and all 3 frontier families.** The "Hammerstein only wins on home turf" hypothesis is falsified.

**Caveat 2 — is it the system prompt or the RAG corpus doing the work?** We added two ablation cells on Sonnet 4.6 (cheapest paid Claude): `mode=no-corpus` (system prompt + framework template, but no retrieved corpus) and `mode=corpus-only` (corpus retrieval, but no system prompt or template). Then judged blind against full Hammerstein-on-Sonnet.

| Pair | n | Full wins | Ablated wins | Ties | Win-rate (full) |
|---|---|---|---|---|---|
| Full vs corpus-only | 24 | 19 | 3 | 2 | 83.3% |
| Full vs prompt-only | 24 | 11 | 11 | 2 | 50.0% |

**On Sonnet 4.6:** the system prompt is load-bearing and the RAG corpus is decorative. Adding the corpus to the prompt-only setup produces a statistical tie; adding the prompt to the corpus-only setup is a clear improvement.

**v0.2 update — cross-family ablation:** the Sonnet finding does NOT generalize. On Opus 4.7, full / prompt-only / corpus-only are all statistically tied; on GPT-5, corpus-only actually outperforms the full stack. The component contribution is model-dependent — see § "v0.2 update" in `eval/RESULTS-v0.1.md` for the full table.

**Caveat 3 — are the judges biased toward their own training distribution?** We added DeepSeek as a 4th vendor judge (not Anthropic, not OpenAI). DeepSeek agreed on 17 of 18 v0 ratings (94.4%) and 12 of 12 Caveat 1 ratings (100%). The result isn't a frontier-judge artifact.

### Two confound checks we added

**Length bias.** Hammerstein-on-GPT-5 is *1258 chars shorter* than raw GPT-5 yet still won 100% of GPT-5 family ratings. Length doesn't explain the result.

**Framework-fidelity tautology.** That rubric axis is rigged — the system prompt elicits Hammerstein vocabulary; judges score "uses Hammerstein vocabulary" as 5; circular. Recomputed using only `usefulness + voice`: v0 = 96.3%, Caveat 1 = 97.9%. The headline isn't carried by the rigged axis.

### Honest limits remaining

- **All four judges are LLMs** trained on overlapping web distributions. Lay-person rater pilot is a v0.2 follow-up.
- **The ablation now covers all 3 frontier families (v0.2 update).** The Sonnet-only finding from v0.1 ("system prompt is load-bearing") does NOT generalize — extending the ablation to Opus + GPT-5 reveals the contribution pattern is **model-dependent**: on Sonnet the full stack beats both ablations, on Opus all three (full / prompt-only / corpus-only) are statistically tied, and on GPT-5 corpus-only actually outperforms full. The headline (Hammerstein-on-frontier beats raw 98.1%) is unchanged; only the claim about which component delivers the lift becomes model-specific. Full v0.2 result in `eval/RESULTS-v0.1.md` § "v0.2 update".
- **Strategic-reasoning is the framework's home turf.** This benchmark says nothing about coding / math / creative-writing tasks; we don't claim Hammerstein helps there.
- **Total sample is 246 ratings** across the four runs (v0 + Caveat 1 + v0.1-Sonnet ablation + v0.2-Opus+GPT-5 ablation).

### Reproduce or refute it

Runner: `eval/run_benchmark.py`. Judge: `eval/judge_pairs.py`. Question sets: `eval/BENCHMARK-v0.md` and `eval/BENCHMARK-v0.1.md`. Full results write-up: `eval/RESULTS-v0.1.md`. Per-response transcripts and per-rating verdicts regenerate via `python eval/run_benchmark.py && python eval/judge_pairs.py --run <subdir>`. Total cost across both runs: ~$10 OpenRouter, ~90 min wall clock.

If you replicate on a different question set or judge panel and get materially different results, [open an issue](https://github.com/lerugray/hammerstein/issues) — that's exactly the kind of pushback the framework wants.

## What this is NOT

- **Not a Claude Code replacement for code editing.** `hd` dispatches code
  work to [aider](https://aider.chat/) for the actual file edits + git
  operations — useful as a substitute when Claude Code is unavailable, but
  it's a wrapper, not a first-party code-editing tool. For bulk code
  generation, route through OpenRouter (paid Qwen Coder Plus / DeepSeek) or
  Cursor IDE Auto directly.
- **Not a from-scratch model.** Pre-training a foundation model is
  decisively out of scope. The realistic ceiling is fine-tuning a small
  open-weight model (Qwen 8B / Llama 3.1 8B-70B) — and that's only if the
  prompt-engineering + RAG path proves insufficient for a given operator.
- **Not authoritative for every operator's framework.** The shipped corpus
  is a reference implementation drawn from one operator's accumulated
  reasoning. The framework structure transfers as-is; the corpus content is
  yours to author. See § Customize the corpus.

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

# Quick-fire verb wrappers (recommended for daily use; scripts/h or scripts/h.ps1)
h next "what's the highest-leverage move this week given X, Y, Z?"
h audit "<plan>"        # adversarial pre-flight on a plan before firing it
h scope "<idea>"        # scope-pass on a half-formed idea
h worth "<proposal>"    # cost-benefit before committing
h sharper "<position>"  # counter-frame on a position you've already taken

# Or invoke the underlying CLI directly
hammerstein --template what-should-we-do-next "<query>"

# Or drop into an interactive shell with bounded rolling context (3 turns)
hsh
```

The harness reads `providers.yaml` for the fallback chain and routes through
OpenRouter (qwen3.6-plus) by default, with auto-fallover to a secondary OpenRouter model, DeepSeek, and Ollama if the primary fails. See `harness/README.md` for the full flag set
and `tests/test_continuity_chain.py` for the smoke-test harness.

**Optional:** `scripts/hquery` (fzf corpus search) + `scripts/hlog` (call
history) + `scripts/hstats` (usage stats) round out the terminal-native
workflow. See § Companion shell utilities.

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

| Provider           | Model                              | Auth                          | Executor      |
|--------------------|------------------------------------|-------------------------------|---------------|
| `openrouter`       | `openrouter/qwen/qwen3.6-plus`     | `OPENROUTER_API_KEY`          | aider         |
| `openrouter-coder` | `openrouter/qwen/qwen3-coder-plus` | `OPENROUTER_API_KEY`          | aider         |
| `deepseek`         | `deepseek/deepseek-chat`           | `DEEPSEEK_API_KEY`            | aider         |
| `claude`           | `claude-sonnet-4-6`                | `ANTHROPIC_API_KEY` (paid)    | aider         |
| `claude-opus`      | `claude-opus-4-7`                  | `ANTHROPIC_API_KEY` (paid)    | aider         |
| `claude-code`      | (Claude Code subscription)         | Pro/Max plan, no API key      | claude-code   |
| `cursor-agent`     | (Cursor subscription)              | Cursor login, no API key      | cursor-agent  |
| `ollama`           | `ollama/qwen3:8b`                  | (none — local)                | aider         |

**Subscription-backed providers (`claude-code`, `cursor-agent`) — bypass
aider, use the subscription's tool-using agent directly.** The audit
pre-flight still runs through OpenRouter (cheap), so the costly part of the
dispatch lands on whichever subscription the operator already pays for.
Useful when you'd rather burn subscription rate-limits than pay-per-token
API spend. The `--file` / `--read` / `--architect` flags don't apply to
these executors (the underlying agent finds files via its own tool use);
mention file references in the prose instead.

- `claude-code` requires the `claude` CLI on PATH (Pro/Max plan; no API key).
- `cursor-agent` requires the `cursor-agent` CLI on PATH and a one-time
  `cursor-agent login` (free composer-2-fast tier covers most tasks).

Dispatch logs land at `~/.hammerstein/logs/dispatches.jsonl` (separate
from the audit-call log at `~/.hammerstein/logs/hammerstein-calls.jsonl`).

### Phase 1 scope (this release)

- Single-shot dispatch (no multi-turn conversation state in the wrapper)
- Single-tool downstream (aider only — cursor-agent in Phase 2)
- Explicit provider selection (auto / quota-aware routing in Phase 3)
- No file-detection logic (operator passes `--file` flags or aider's
  repo-map handles it)

### Falsification gate — CLEARED 2026-05-05

Phase 1's 14-day window was: if the operator hasn't dispatched at
least one real coding task via `hd` within 14 days, the architecture
is wrong. Cleared by self-build — **Phase 3 (state-file injection)
was implemented BY `hd` dispatching to aider** (public commit
c875804, ~$1 OpenRouter spend, ~6.5 min run, 43 tests passing). The
substitute carried meaningful architectural work, not just maintenance
edits. The orchestrator vision matches observed behavior.

## Companion shell utilities

Four thin shell scripts surface quick-fire template invocation, the
corpus, the call log, and usage stats for terminal-native workflows.
POSIX shell + `fzf` + `bat` + `jq`; zero UI framework.

```bash
# Add scripts/ to PATH (or symlink h / hquery / hlog into ~/.local/bin/)
export PATH="$PATH:$(pwd)/scripts"

# h -- quick-fire template wrapper (verb shortcuts; falls through to classifier on bare query)
h audit "<plan>"          # -> --template audit-this-plan
h scope "<idea>"          # -> --template scope-this-idea
h worth "<proposal>"      # -> --template is-this-worth-doing
h next "<context>"        # -> --template what-should-we-do-next
h sharper "<position>"    # -> --template review-from-different-angle
h "<any query>"           # bare query, classifier auto-detects
# Default model: openrouter (paid, cheap). Override: HAMMERSTEIN_MODEL=ollama h ...

hquery                    # fuzzy-search corpus entries (fzf + bat preview)
hquery "framework"        # pre-populate the search field
hlog                      # last 20 calls, column-aligned
hlog 50                   # last N calls
hlog | grep audit         # filter by template / query substring
hstats                    # last 7 days usage stats (calls, cost, templates, hosts)
hstats --gate             # 7-day window + explicit Phase A → Phase B verdict
hstats --by-host          # cross-machine usage breakdown
```

`h` is POSIX shell on Linux/Mac and `h.ps1` on Windows; both ship in
`scripts/`. `hquery` requires `fzf` (`brew install fzf` on Mac, `apt
install fzf` on Linux). `bat` is preferred for syntax-highlighted
preview; falls back to `cat` if absent. `hlog` and `hstats` require `jq`
(effectively ubiquitous). The call log lives at
`~/.hammerstein/logs/hammerstein-calls.jsonl` (auto-created on first
call; not in cwd). Each entry stamps the host, so `hstats --by-host`
works across machines if you sync the log.

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

## Stable downstream interface

External tools that script Hammerstein (the maintainer's daily-brief generator being the current reference example) depend on these surfaces remaining stable across versions:

- **Template names** — `audit-this-plan`, `scope-this-idea`, `is-this-worth-doing`, `what-should-we-do-next`, `review-from-different-angle` — invoked via the `--template` flag.
- **Plain English summary section** at the head of every template response, terminated by a `---` divider line. Callers extract this block to surface a layman-readable verdict.
- **stdout for the response body; stderr for diagnostics.** A `[backend=...]` metadata line at the head of stdout is parseable and contains provider, cost, and latency.
- **Exit code zero** on a returned response; **non-zero** on backend exhaustion or hard failure. Empty stdout when all backends fail soft.

Adding new templates is non-breaking. Removing or renaming any of the five above is a major-version bump and lands under `### Breaking` in the CHANGELOG.

## License

[MIT](LICENSE)

---

*Hammerstein-Equord, Kurt Freiherr von (1878-1943). Chief of the German Army
Command 1930-1934. Surfaced the officer typology — clever-lazy / clever-
industrious / stupid-lazy / stupid-industrious — that anchors this project's
namesake framework.*

```
====================++++++++++++++++++++++++++*+********+
==================+%%%%%%%%%#++++++++++++++++++++++*+++++
===============%%%%%%%%%%%%#%%###+#++++++++++++++++++++++
============#%%%%%%%%%%%%%%#***=+++#*++++++++++++++++++++
======++===%%%%%%%%%%%%%%#*##*+=:::::=+++++=+++++++++++++
==========%%%%%%%%##**++==:-:::.......:=++++=++++++++++++
=========%%%%%##%#####**=-::............+++++=+++++++++++
=========%%%%%%%%%%%##**+=-::..:.........+++++==+++++++++
========+%%%%%%%%%%###**++--::::.:::.....++++++++++++++++
=========%%%%%%%%%%%#%##***--::..::......=+++++=+++++++++
=========%%%%%%%%%%%%##+==++*--:-:-::...:=++++=++++=+=+++
=========%%%%%%%%%%%%%%###*++***+--=***+===++=+++++++++++
=========+%%%%%%%%%%%%%%%%:#+%%%*:.+#@+.#===+++++++=+++++
========%%%%%%%%%%%%%%@%%%.--#%%%=.:-=-:.-+++++++=+++++++
========%%%%%%%%%%%%%%%%%#+-=%%%%*.:.-:.::++=+++++==+++++
=======-%%%%%%%%%%%%#+=***+*#%%%%#-.::::::++++++++++=++++
========+%%%%%%%%%%%%%******#%@%%%+:::::::=++++++++++++++
=========#%%%%%%%%%%%%%%%##*#@%%%%*=::::::=++++++++++++++
++++======#%%%%%%%%%%%%%%#**%%%%%+-::::::=+++++++++++++++
++++++=+====@%%%%%%%%%%%%*%%*###+-:::-:::++=++=++++++++++
+++=++++===-@%%%@%@@%%@%%####@##+===-:*::++++++++++++++++
++++++=+===%%@%%@%@@@@@@%*=%#+===+=-::---++=+++++++++++++
++++++====#@%%@@@%@@@%@@@#%%%%%%*--::---+++++++++++++++++
++++++===%%%@@@@@@@@@@@@@%@@@%%#*=+---=++++++++++++++++++
++++==*%%%@@@@@@@@@@@@@@%@%%%%%###%#++-++++++++++++++***+
+++++%%%%%%%%@@@@@@@@@@@@@%%%%%%#+-%%%@%*++++++++++++*++*
++*%%%%%%%@%@@@@@@@@@@@@@@@@%*::..-**######++++++++******
#%%%%@=#%%%%%%%@%%@@@@*#@@%@-%%#**@**##*#####+++++*******
%#+=::-+*:+%%%%@%%@%%*+*#+#*==:+%%%%%**###*###**++*******
+-.#=::-.==@%%##%%%%@@@@@%#=+=*+=*@@%##*###*%%##+++******
+:+*::.%*+*#%%#####*#%@%@@@@%+*#-::@%*#***##%%####+******
=:*==*##*+++%%%#####***#@@@#%@@@%%%@@*##***##@###@*******
+=#****#*+++*%%#**###**#####%@@#%@#-#**##***###%#%##*****
*****++***+=+#%%*+####**##*#**%@#*@..*****@.-+*##@####***
#**+*+*++*++++%%%***####******%@@***#***#--:+*#%@%#%##%#*
%#***++*++**+**%%***####*******%@@*###*%.:+#**##%%#%%##%#
####**++++**+**#%#*+*#%#*******#%@@**#**@#####*#@%%%%%#%%
#***#**++=+%#**#%#***#%##*******%@@@#*****##%###%=#%%%#%@
##*****++++%%**%%#***#%%####***#*%@@@#***###%####-%%%##%@
```

> *"A clean rendering. The work lives in the gates, not the cover."*
> — Hammerstein, on this portrait.
