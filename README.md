# Hammerstein

![Hammerstein: a framework that survives the model.](docs/images/banner.png)

## In plain English

Most AI assistants are eager to please. They agree with you and tell you your plan is great. Hammerstein is a method for getting the opposite: an AI that pushes back. It refuses plans that are wasteful or dishonest, points out the weak spots in an idea, and when it says no it tells you what would turn that no into a yes. The goal is an assistant that helps you think, not one that flatters you. It works the same way whichever AI is running underneath.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Status: v3.0](https://img.shields.io/badge/status-v3.0-success.svg)](https://github.com/lerugray/hammerstein/releases)

## What this repo is

This repo is the **open-source framework and CLI**: the Hammerstein reasoning
discipline encoded as a portable system prompt, a set of few-shot templates, a
small retrieved corpus, and a Python harness that routes them to whichever model
you have. Point it at a frontier API, a cheap per-token endpoint, or a local
Ollama model. The reasoning style stays the same.

The load-bearing artifact is the framework, not the model. That is the whole
design goal: when the underlying model or provider changes, the reasoning
survives.

**Hammerstein is three separate things. This repo is only the first.**

| | What it is | Where it lives |
|---|---|---|
| **Framework + CLI** | The portable prompt, templates, corpus, and harness. MIT licensed. | This repo |
| **Hammerstein-7B** | The framework distilled into local open weights. | [huggingface.co/lerugray/hammerstein-7b-framework](https://huggingface.co/lerugray/hammerstein-7b-framework) |
| **hammerstein.ai** | A hosted product built on the same discipline. | [hammerstein.ai](https://hammerstein.ai) |

They share a name and a doctrine. They do not share a codebase, and a claim
measured on one does not transfer to the others.

**Current release: v3.0.0** (2026-07-31). `hd dispatch` has been removed;
the framework is now strictly a reasoning/audit layer. The plain-English summary
layer remains removed. Full history in [CHANGELOG.md](CHANGELOG.md).

## What it is tuned for

Hammerstein reasons the way the framework prescribes: clever-lazy over
stupid-industrious, verification over enthusiasm, legible failure over hidden
success, "bring your own imagination" over generic generation.

Refusal is a feature. When the framework declines a plan it names the specific
condition that would change the answer, so a no is actionable rather than a dead
end. A wrapper that never refuses is not grading anything.

## Quickstart

```bash
# Requires Python 3.11+
pip install hammerstein     # from PyPI
# or: pip install -e .      # from a local clone, for development
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
OpenRouter (qwen3.6-plus) by default, falling over to a secondary OpenRouter
model, then DeepSeek, then local Ollama if the primary fails. See
`harness/README.md` for the full flag set and `tests/test_continuity_chain.py`
for the smoke-test harness.

**Optional:** `scripts/hquery` (fzf corpus search), `scripts/hlog` (call
history), and `scripts/hstats` (usage stats) round out the terminal-native
workflow. See § Companion shell utilities.

## Example

*A typical strategic-reasoning consult. The framework ranks options, names what
to deprioritize, and surfaces a counter-observation that could change the call.*

**Query**

It is Tuesday morning. I have 2 hours. Options: (a) draft the benchmark questions, (b) harden the RAG retrieval, (c) add more corpus entries, (d) run the harness end to end and record one baseline run. What should I do first?

**Response (abbreviated)**

Run a single end-to-end test with what you already have first. That is the only way to know what's actually broken. Drafting more questions or adding more corpus entries before that is guesswork. Five questions is enough to start; tighten the retrieval layer only after the test tells you what failed.

---

This is clever-industrious work with an easy stupid-industrious trap: adding corpus before you can measure whether retrieval works.

1. Run (d) and record a baseline run. You need a working loop before you add more inputs.
2. Draft (a) as a short locked list. Five questions is enough to start.
3. Harden (b) only after the baseline tells you what broke.

Deprioritize (c) for now. More examples do not help if the harness cannot retrieve the right ones.

Counter-observation: if the baseline run already produces useful retrieval and the failure is prompt shape, skip retrieval hardening and spend the remaining time tightening the system prompt instead.

### Example: a flawed plan, audited live

*Unedited real output from `hammerstein --template audit-this-plan`, run against
an intentionally bad plan. Only line breaks were adjusted for the page.*

**Query**

We are going to rewrite the entire Hammerstein CLI from scratch in Rust because
the current Python codebase has accumulated some awkward spots and we want it to
be clean.

**Response**

```text
[backend=openrouter model=qwen/qwen3.6-plus template=audit-this-plan corpus=4 latency_ms=50796 cost_usd=$0.00801]
This plan operates in **stupid-industrious** territory. A full-language rewrite motivated by "awkward spots" and "cleanliness" consumes the operator's binding constraint (time/attention) while discarding working infrastructure, and it mistakes language-level friction for structural debt.

Failure modes:
- **Context loss & workflow breakage.** The existing Python CLI has implicit contracts with deployment scripts, CI, and operator muscle memory. A Rust rewrite breaks these silently until discovered during a critical run.
- **The "cleanliness" mirage.** Rust's borrow checker and explicit lifetimes will trade Python's awkwardness for compilation friction and ecosystem overhead. The codebase becomes statically "clean" but harder for a solo operator to iterate on quickly.
- **Dual-maintenance trap.** During the rewrite, you either halt feature work or maintain two CLIs. Both drain the time budget and pause the block-fix-execute compounding loop (corpus #08) that keeps the fleet productive.
- **Misdiagnosed root cause.** "Awkward spots" are typically architectural (tight coupling, missing interfaces, unclear state boundaries), not linguistic. Rewriting preserves the same architecture unless explicitly redesigned, meaning you'll recreate the awkwardness in a new syntax.

Verification gates:
- **Pain-point inventory Boolean:** List the exact 3-5 "awkward spots" with concrete examples (e.g., argparse fails on nested flags, state serialization drops fields on Y). If the list is <5 or relies on subjective "cleanliness," the rewrite premise is unverified.
- **Zero-downtime migration gate:** Can the new Rust CLI pass 100% of existing integration tests and operator workflows before the Python version is deprecated? If not, this is a parallel project, not a replacement.
- **Operator-time budget check:** Does the rewrite fit within a single focused session? If it spans >1 week of wall-clock time, it violates the binding-constraint rule.

Structural-fix candidates:
- **Targeted refactoring + type enforcement.** Replace the awkward modules with strict Python (dataclasses, pydantic, mypy), add ruff for linting, and enforce explicit interfaces. This fixes the actual debt without discarding working infrastructure.
- **Extract, don't rewrite.** If a specific subsystem (e.g., config parsing, CLI routing) is genuinely problematic, extract it into a standalone, well-tested module. Keep the rest intact.
- **Add verification gates to the existing CLI.** If "awkwardness" manifests as silent failures or bad state, add the Boolean checks the framework prescribes (corpus #32). Clean code that fails silently is worse than awkward code that fails legibly.

Recommendation: **don't-ship.** Inventory the specific awkward spots, apply structural fixes in Python, and add verification gates where failures are currently opaque. Only reconsider a language switch if a concrete, measurable bottleneck (e.g., startup latency, memory footprint, true concurrency) is proven and cannot be solved in Python.

Counter-observation: If the "awkward spots" are actually Python's GIL or async model blocking a specific, high-throughput workflow that the operator is actively bottlenecked by, then a targeted Rust rewrite of *that subsystem* (not the whole CLI) is justified. The check is: can you name the exact performance metric that is broken, and prove Python cannot meet it? If yes, scope to the subsystem. If no, the rewrite is aesthetic, not strategic.
```

## Benchmark: does the framework actually help?

**It depends on the model, and we measured where it stops.** The lift tracks
whatever judgment the base model lacks. On weaker models it is large; on the
strongest current model it inverts.

| Model class | Raw preferred | Wrapped preferred | Reading |
|---|---|---|---|
| Frontier (Claude Opus 5, n=18) | 12 | 6 | Wrap adds conformance and shorter output, not usefulness |
| Commodity (4 models, n=216) | 3 | 182 | 31 ties. Lift survives the strict cut |
| Local/small (3 models, n=54) | 4 | 50 | Largest measured lift |

On the May 2026 frontier panel the wrapped arm won **53 of 54** blind paired
ratings (98.1%). That claim ages: the Opus 5 row above shows the same framework
inverting on a newer frontier model.

The cleanest credibility anchor is the null result: on Fable 5, a model already
trained to reason check-then-speak, the framework produced **12-11-0 (52.2%,
n=23)**, statistically indistinguishable from raw. A framework that hides its
null results is itself stupid-industrious.

Full methodology, per-arm tables, ablations, OOD sets, judge checks, coder-bench
results, and reproduction instructions: [BENCHMARKS.md](BENCHMARKS.md) and the
`eval/` directory.

## What this is NOT

- **Not a code editor.** This repo does not edit files, run git, or call
  tools. It is a reasoning layer you can pipe into whatever executor you use.
- **Not a from-scratch model.** Pre-training a foundation model is out of scope.
  The realistic ceiling is fine-tuning a small open-weight model, and only if
  the prompt-plus-RAG path proves insufficient.
- **Not authoritative for your framework.** The shipped corpus is a reference
  implementation drawn from one operator's accumulated reasoning. The structure
  transfers as-is. The content is yours to author. See § Customize the corpus.

## Customize the corpus

The corpus in `corpus/entries/` is a **reference implementation**: a small
curated set of Hammerstein-style reasoning entries that illustrate the
framework's structure. It is not meant to be authoritative for anyone else.

To make Hammerstein useful for your own work:

1. Clone this repo.
2. Read `research/HAMMERSTEIN-FRAMEWORK.md` for the framework synthesis.
3. Replace or augment `corpus/entries/` with reasoning drawn from your own work:
   incidents where you caught a stupid-industrious trap, structural fixes that
   compounded, verification gates that paid off, counter-observations that
   reshaped a plan. The provenance and framing pattern generalizes (one
   principle per entry, tagged with quadrant, principle, source, and quality).
   The specific examples should not.
4. Update `corpus/CORPUS-CURATION.md` to index your entries.
5. Optionally tune `prompts/SYSTEM-PROMPT.md` for your project's idiom.

The framework structure transfers as-is: system prompt, few-shot templates,
retrieval layer, provider fallback chain. The corpus content is yours.

## `hsh`: the Hammerstein shell

For a conversational, stay-in-the-environment workflow, `hsh` drops you into an
interactive REPL with bounded prior-turn context. Type prose, get an audit, push
back with more prose, get a refined audit.

```
$ hsh
Hammerstein Shell (hsh) - interactive strategic-reasoning environment
Type :help for commands, :exit or Ctrl-D to quit.
Rolling context capped at 3 turns.

hsh:my-project> should I refactor the auth flow this week?
[runs audit-this-plan with full adversarial review streamed live]

hsh:my-project> what if the auth flow is downstream of a billing change?
[runs audit again, with prior turn injected as background context]

hsh:my-project> !git status
[bash passthrough]

hsh:my-project> :exit
```

Design constraints, all load-bearing:

- **Every template call is a discrete fresh invocation.** No conversation
  history gets dumped into the few-shot template, and corpus retrieval runs
  fresh per turn.
- **Bounded prior-turn context (last 3 turns)** is injected as a prefix so
  iteration works ("apply the same fix to X", "given Y, retry"). The cap
  prevents the shell from quietly becoming a conversation host.
- **Plain prose runs `audit-this-plan`**, which is read-only thinking.
  The shell never edits files or runs tools; it only produces reasoning.
- **Project state file (`:state`).** If `.hammerstein-state.md` exists in the
  project root (found by walking up to the nearest `.git`, `pyproject.toml`,
  `package.json`, `Cargo.toml`, `go.mod`, `Gemfile`, or `requirements.txt`), its
  contents are injected as a preamble before the rolling context on every call.
  `:state` views it and `:state edit` opens it in `$EDITOR`, creating it if
  missing. Use it to persist project constraints across sessions without
  polluting the turn buffer.

Falsification gate: if `hsh` produces noticeably worse audits than
fresh-from-cold `hammerstein` calls, the bounded-context injection is corrupting
framework reasoning and should be killed in favour of verb-only mode. Compare
hsh output against a fresh audit on the same query.

## Companion shell utilities

Four thin shell scripts surface template invocation, the corpus, the call log,
and usage stats. POSIX shell plus `fzf`, `bat`, and `jq`. No UI framework.

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
hstats --gate             # 7-day window + explicit Phase A -> Phase B verdict
hstats --by-host          # cross-machine usage breakdown
```

`h` is POSIX shell on Linux and Mac, `h.ps1` on Windows; both ship in `scripts/`.
`hquery` needs `fzf`. `bat` gives syntax-highlighted previews and falls back to
`cat`. `hlog` and `hstats` need `jq`. The call log lives at
`~/.hammerstein/logs/hammerstein-calls.jsonl`, created on first call. Each entry
stamps the host, so `hstats --by-host` works across machines if you sync the log.

## How the layers compose

| Layer | Where | What |
|---|---|---|
| Framework synthesis | `research/HAMMERSTEIN-FRAMEWORK.md` | Cross-source distillation of the framework's principles |
| Mechanical spec | `design/PILLARS.md` | Framework as mechanical pillars |
| Phased roadmap | `scope/PHASED-ROADMAP.md` | v0 / v1 / v2 trajectory |
| System prompt | `prompts/SYSTEM-PROMPT.md` | The identity-framing prompt every call carries |
| Templates | `prompts/templates/*.md` | Few-shot exemplars for 6 query shapes |
| Corpus | `corpus/entries/*.md` | Retrieved examples, yours to curate |
| Stack | `tech/STACK-DECISION.md` | Provider and model decisions, fallback chain rationale |
| Harness | `harness/`, `hammerstein_cli/` | The Python CLI that ties it together |
| Eval | `eval/`, `tests/` | Benchmarks and continuity smoke tests |

## Stable downstream interface

Tools that script Hammerstein depend on these surfaces staying stable across
versions:

- **Template names.** `audit-this-plan`, `scope-this-idea`,
  `is-this-worth-doing`, `what-should-we-do-next`,
  `review-from-different-angle`, invoked via `--template`.
- ~~Plain English summary section~~ **removed in v2.0 (breaking; see CHANGELOG).**
  Responses are now the unfiltered technical body from the first line. Callers
  that extracted the summary block should consume the body directly.
- **stdout carries the response body, stderr the diagnostics.** A `[backend=...]`
  metadata line at the head of stdout is parseable and carries provider, cost,
  and latency.
- **Exit code zero** on a returned response, **non-zero** on backend exhaustion
  or hard failure. Empty stdout when all backends fail soft.

Adding templates is non-breaking. Removing or renaming any of the five above is
a major-version bump and lands under `### Breaking` in the CHANGELOG.

## License

[MIT](LICENSE)

---

*Hammerstein-Equord, Kurt Freiherr von (1878-1943). Chief of the German Army
Command 1930-1934. Surfaced the officer typology (clever-lazy,
clever-industrious, stupid-lazy, stupid-industrious) that anchors this project's
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
> Hammerstein, on this portrait.
