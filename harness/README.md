# Hammerstein Harness — v0

Python CLI that wraps Ollama (local) + OpenRouter (cloud) + corpus
retrieval + system-prompt assembly. One entrypoint:
`python harness/hammerstein.py "<query>"`.

## Quickstart

Prereqs:
- Python 3.11+ (stdlib only — no pip install)
- Ollama running on `localhost:11434` for local cells (pull `qwen3:8b` first)
- OpenRouter API key in `<a partner project>/.env` under `OPENAI_API_KEY` for
  cloud cells (per `~/.claude/CLAUDE.md` § Routwizard)
- (Optional) `DEEPSEEK_API_KEY` in same .env for the deepseek backend
- (Optional) `ANTHROPIC_API_KEY` for the claude debug backend

Smoke (cloud, no Ollama needed):

    cd hammerstein
    python harness/hammerstein.py --model openrouter "What's the strongest counter-frame to my plan to ship the surrogate-brain v0?"

Smoke (local Ollama):

    ollama pull qwen3:8b   # one-time
    python harness/hammerstein.py --model ollama "..."

Inspect the assembled prompt without running inference:

    python harness/hammerstein.py --show-prompt "..."

Run the v0 benchmark suite (questions 1-6 from `eval/BENCHMARK-v0.md`):

    python eval/run_benchmark.py
    # results land in eval/results/<timestamp>/

Filter to one question + cell (e.g. smoke test):

    python eval/run_benchmark.py --questions 1 --cells openrouter-qwen36-plus

## Flags

- `--model <backend[:model]>` — `ollama` | `openrouter` | `deepseek` | `claude`. Default: `ollama:qwen3:8b`.
- `--template <name>` — pin a few-shot template instead of classifier-decide. Default: `auto`.
- `--no-corpus` — ablation: skip RAG retrieval (prompt + template only).
- `--corpus-only` — ablation: minimal system prompt + retrieved corpus only.
- `--top-k <N>` — number of corpus entries to retrieve (default 4).
- `--show-prompt` — print assembled prompt and exit (no inference).
- `--log <path>` — JSONL call log path (default `logs/hammerstein-calls.jsonl`).

Templates (auto-classified by query shape, override with `--template`):
- `scope-this-idea` (default)
- `audit-this-plan`
- `is-this-worth-doing`
- `what-should-we-do-next`
- `review-from-different-angle`

## Provider fallback

By default, Hammerstein uses a **provider fallback chain** defined in `providers.yaml`.
If the primary provider rate-limits, times out, or returns an unusable response, the harness
automatically tries the next provider.

Failure modes that trigger fallover (configurable in `providers.yaml`):
- HTTP 429 (rate limit)
- timeout
- empty/null response
- parse error (unparsable JSON response)

Override behavior (bypasses the chain):

    python harness/hammerstein.py --model openrouter:qwen/qwen3-coder-plus "<query>"

Chain visibility:
- Successful calls print a progress-style line to stderr showing which chain step answered:
  `[chain_step=2/4 provider=deepseek-isolated latency_ms=43210 cost=$0.00400]`

## Continuity smoke test

Boolean continuity test (not quality benchmarking). For each runnable provider in the chain,
run three representative benchmark queries and assert:
- non-empty response (>\u2009200 chars)
- framework markers present (e.g. "clever-lazy", "verification", "counter-observation")
- recognizable template structure

Run:

    pytest tests/test_continuity_chain.py -v

Notes:
- `ollama-local` is skipped if `OLLAMA_HOST` isn't reachable.
- Cloud providers are skipped if their API keys are not present in the environment.

## Layout

- `harness/hammerstein.py` — CLI entrypoint
- `harness/hammerstein/` — module
  - `corpus.py` — load + keyword/tag retrieval over `corpus/entries/`
  - `classifier.py` — keyword-based template classifier
  - `prompt.py` — assemble system prompt + template + corpus + query
  - `backends.py` — HTTP clients for Ollama, OpenRouter, DeepSeek, Claude
  - `logger.py` — JSONL call log
- `eval/run_benchmark.py` — runs benchmark questions across cells
- `eval/BENCHMARK-v0.md` — locked v0 question set + scoring rubric
- `eval/results/<ts>/` — per-run output dir (one .md per `(question, cell)`)
- `logs/hammerstein-calls.jsonl` — every call's metadata + response

## Architecture notes

- **Minimal dependencies.** Uses stdlib HTTP (`urllib.request`) plus `PyYAML` for provider-chain config parsing.
- **Retrieval = tag+keyword overlap.** Per `tech/STACK-DECISION.md`,
  v0 stays simple; embedding-based retrieval (Option A) is reserved
  for v1 if corpus grows past ~80 entries.
- **Response shape comes from the template.** Each
  `prompts/templates/*.md` has a hard-coded "output shape" block that
  the few-shot examples reinforce. Classifier picks template; harness
  wires it into the prompt; model matches the shape.
- **Ablation cells are first-class.** `--no-corpus` and `--corpus-only`
  let the eval distinguish prompt-does-the-work vs corpus-does-the-work
  vs both-matter (per `scope/PHASED-ROADMAP.md` ablation cells).
