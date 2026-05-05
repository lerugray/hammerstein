# Hammerstein — Tech Stack Decision

**Status:** v1, locked by the research session 2026-05-04. The
scaffold's preliminary lean is confirmed; specific open questions are
resolved below.

The structure mirrors TWAR / GTA's `STACK-DECISION.md` — locked
decisions, reasoning, alternatives considered, architectural
implications.

## What this v1 lock changes from the scaffold

The original scaffold's lean was correct on every load-bearing decision.
This v1 lock adds:

- **RAG retrieval algorithm locked.** v0 ships with **Option B**
  (static corpus in prompt) because the actual v1 corpus is 50 entries
  × ~250-400 tokens each ≈ 15-20K tokens, which fits comfortably in a
  32K-context window with the system prompt + few-shot template + user
  query (`tech/STACK-DECISION.md` "RAG: simple-first design"). Option
  A (embedding-based retrieval) is the v1 migration path if the
  corpus grows past ~80 entries.
- **Embedding model deferred.** Since v0 ships with Option B, no
  embedding model is needed at v0. If v1 migrates to Option A,
  `sentence-transformers/all-MiniLM-L6-v2` is the lean.
- **Eval rubric locked.** Three axes (framework-fidelity / usefulness
  / voice-match), 1-5 operator-rated per response, per
  `scope/PHASED-ROADMAP.md` v0 ship criteria.
- **Few-shot template selection** is classifier-driven — the harness
  classifies each query into one of {scope / audit / prioritize /
  cost-benefit / counter-frame / default} and selects the matching
  template from `prompts/templates/`. Default is `scope-this-idea` if
  no clear classifier match.
- **Logging format locked.** JSONL, one line per call, fields:
  `{timestamp, backend, model, system_prompt_version, template,
  retrieved_corpus_ids, query, response, response_length, latency_ms,
  cost_usd}`. Grep-able, eval-friendly, archive-friendly.
- **System-prompt versioning lives in `prompts/archive/`.** Each
  version-bump moves the prior prompt to `prompts/archive/SYSTEM-
  PROMPT-vN.md`; the live `prompts/SYSTEM-PROMPT.md` is always
  current.

---

## Lean summary (research session validates or overrides)

- **Local inference:** **Ollama** with **Qwen 8B** (preferred) or
  **Llama 3.1 8B** (fallback) as the default model. the operator already has
  Ollama configured on multiple machines per his routing rules.
- **Cloud fallback:** **OpenRouter** with **paid Qwen3.6-plus** ($0.325 / $1.95
  per M) as the production-quality fallback when local inference isn't
  enough. **DeepSeek v4-flash** as the third tier.
- **RAG storage:** start simple. **JSON or SQLite** for the corpus index;
  **sentence-transformers** (small CPU-only model like `all-MiniLM-L6-v2`)
  for embeddings if embedding-based retrieval is needed; **TF-IDF /
  keyword retrieval** if the corpus is small enough that fancy retrieval
  is overkill (likely true at v0's 50-200 entries).
- **Harness:** **Python CLI** wrapper. Python is the AI-tooling default;
  Ollama + OpenRouter both have well-documented Python clients.
- **Eval harness:** Python script that runs benchmark questions through
  each backend + dumps responses for operator-rated scoring.
- **Distribution:** local-only, single-user. No SaaS layer, no
  multi-user infrastructure.
- **No internet runtime dependency** — fully offline mode is supported
  via Ollama-only path. Cloud fallback exists but isn't required.

---

## Why Ollama for local inference

the operator already has Ollama configured + working on his machines per the
routing rules in `~/.claude/CLAUDE.md`. Adding a new local-inference
runtime would be friction without obvious benefit. Ollama's tradeoffs:

**Pros:**
- Already installed + working on the operator's machines
- Model registry (pull-by-name): `ollama pull llama3.1:8b` /
  `ollama pull qwen2.5:7b` is one command
- Stable API surface (`/api/generate`, `/api/chat`) consumed by
  multiple Python clients
- Supports CPU-only inference for small models on M-series Macs
- Mac, Windows, Linux all work
- Model files cached locally; no download repetition across runs

**Cons / Mitigations:**
- Cold-start latency on first call after model load (~5-15s) — mitigated
  by long-running daemon mode
- Memory pressure when loading multiple models — mitigated by sticking
  to one base model at v0 (8B-class)
- Quantization defaults may not be ideal — mitigated by explicit
  quantization choice (Q4_K_M is the default sweet spot)

## Why Qwen 8B (preferred over Llama 3.1 8B)

Both are reasonable starting models. Qwen 8B has historically been
slightly stronger on reasoning + structured-output tasks (relevant for
Hammerstein-style quadrant analysis + verification-question surfacing).
Qwen models are also actively maintained by Alibaba, which means
ongoing capability improvements as the model series iterates.

Llama 3.1 8B is the conservative fallback: maximally well-known,
maximally documented, maximally tested across the open-weight ecosystem.

The research session may flip this preference based on actual benchmark
results. A two-experiment comparison (Qwen 8B vs Llama 3.1 8B on the
5-10 benchmark questions) is cheap to run during v0 and decides the
question empirically.

## Why OpenRouter Qwen3.6-plus for cloud fallback

Per the operator's existing routing rules:
- Qwen3.6-plus: $0.325/$1.95 per M tokens, 1M context. Validated 2026-05-02
  on real workload (kriegspiel-quality output for $0.005/call).
- DeepSeek v4-flash: similar tier, different provider for redundancy.

Per-call cost at typical strategic-reasoning prompt sizes (2-4K tokens
in + 1-2K out) is $0.001-$0.005 per call. Effectively free relative to
monthly Anthropic spend.

OpenRouter is already configured in the operator's environment; key is at
`~/.generalstaff/.env`. No new credential setup needed.

## RAG: simple-first design

Two viable retrieval shapes:

**Option A — Static framework + per-query corpus retrieval (RAG).**
System prompt contains the framework's load-bearing rules; each query
retrieves 3-5 most-relevant corpus entries via embedding similarity;
retrieved entries get appended to the prompt as few-shot examples.

Pros: scales to large corpus (1000+ entries); per-call context size
bounded; supports adding new entries without re-engineering the system
prompt.

Cons: requires embedding store + similarity search; embedding model
adds latency (small but nonzero); retrieval quality is itself a
tunable-and-failable surface.

**Option B — Static framework + static corpus in one prompt.**
System prompt contains both the framework rules AND the entire corpus.
No retrieval layer.

Pros: simpler implementation; no embedding model; corpus content fully
visible to the model on every call.

Cons: only works if the corpus fits in context (50-100 entries × 500
tokens each = 25K-50K tokens, just barely fits in a 32K-context window;
larger corpus blows the budget); doesn't scale.

**Lean: start with Option B at v0** (simpler; works at the corpus size
v0 targets); migrate to Option A at v1+ if the corpus grows beyond
what fits in context.

The research session can override this lean if the corpus curation
shows entries are larger than expected (e.g. the Hammerstein
observation log entries are sometimes ~100 lines each, which would
push corpus size into Option-A territory immediately).

## Harness: Python CLI

**Why Python:**
- AI-tooling default; Ollama + OpenRouter SDKs maintained in Python
  first
- Embedding libraries (sentence-transformers, sklearn TF-IDF) are
  Python-native
- the operator's existing scripts (catalogdna's bot, GeneralStaff's scripts)
  are TypeScript; this is the first project where Python's ecosystem
  fit is decisively better

**Counter-argument for TypeScript:**
- Matches the operator's existing portfolio
- Better Tauri / Electron / Cursor IDE integration if Hammerstein ever
  grows a GUI surface (Tauri is the established pattern from Devforge)
- Bun is fast and the operator uses it elsewhere

**Resolution:** Python at v0. If a GUI becomes a real requirement at
v2+, revisit. Keeping the v0 implementation in Python doesn't preclude
a TypeScript wrapper later that calls the Python harness.

**CLI shape:**
```
hammerstein <query>                    # one-shot query
hammerstein --eval                     # run the benchmark suite
hammerstein --corpus list              # show corpus entries
hammerstein --corpus add <file>        # add an entry to the corpus
hammerstein --backend ollama           # explicit backend choice
hammerstein --backend openrouter       # explicit cloud
hammerstein --backend claude           # ground-truth (debug only)
```

Single binary that wraps a single Python module. No multi-process
infrastructure. Stays simple.

## Distribution: local-only, single-user

Hammerstein is the operator's strategic-reasoning fallback. Not a shipped product.
Not a SaaS. Not a multi-user system. Distribution = `git clone` + `pip
install -e .` on each of the operator's machines.

If at v2+ this becomes worth open-sourcing as a portable Hammerstein-
framework runtime that anyone can use, distribution gets revisited.

## Architecture implications

- **Corpus is the load-bearing artifact.** Not the model, not the
  harness, not the eval. Corpus quality + framework synthesis quality
  determine whether v0 succeeds.
- **Inference backend is swappable.** The harness should never hardcode
  Ollama or OpenRouter; backend choice is a runtime parameter.
- **System prompt is versioned.** Every harness invocation logs which
  system-prompt version produced the response. Iteration on the prompt
  doesn't invalidate prior eval data.
- **Eval is deterministic where possible.** Same model + same seed +
  same query should produce same response (modulo provider-side
  non-determinism on cloud models). Local Ollama supports `seed`
  parameter; cloud OpenRouter sometimes does, sometimes doesn't —
  flag in eval logs which calls were deterministic.
- **No internet runtime dependency required.** Ollama-only path
  (with appropriate base model pulled) is fully offline. OpenRouter is
  optional augment, not requirement.

## Open architecture questions — RESOLVED

Research session 2026-05-04 lock:

1. **Embedding model choice for RAG.** **DEFERRED to v1.** v0 uses
   Option B (static corpus in prompt). If v1 migrates to Option A,
   `sentence-transformers/all-MiniLM-L6-v2` is the lean — small,
   CPU-only, well-tested, no GPU required.

2. **System-prompt update cadence.** **STATIC at v0; versioned
   archive thereafter.** Lock the v0 system prompt at ship time;
   move prior versions to `prompts/archive/SYSTEM-PROMPT-vN.md` on
   each bump. The harness logs the prompt version per call, so prompt
   iteration does not invalidate prior eval data.

3. **Corpus growth strategy.** **MANUAL at v0; automated extraction
   reserved for v1+ if the corpus needs to grow past ~200 entries.**
   The 50-entry v1 corpus that ships with v0 is fully manually
   curated. Each new entry is an interactive decision (per the brief's
   hands-off list). Automated extraction is reserved for the case
   where the corpus needs to grow into 1000+ entries for fine-tuning
   data — which is v1 territory.

4. **Multi-machine corpus sync.** **GIT-TRACKED at v0.** Single
   source of truth in this repo. The corpus is the project's
   load-bearing artifact (per `corpus/CORPUS-CURATION.md` and
   `research/HAMMERSTEIN-FRAMEWORK.md` §6 cross-project compounding) —
   it deserves version control. If repo size becomes an issue at v2+
   when the corpus grows, revisit (e.g. git-LFS, separate corpus
   repo).

5. **Multi-turn conversation memory.** **ONE-SHOT at v0.** Multi-turn
   is v1+ if real use surfaces the need. The framework's strategic-
   reasoning queries are often single-turn questions with rich answers;
   the v0 benchmark suite is structured this way. Don't build multi-
   turn until single-shot is solid.

6. **Adversarial-prompt robustness check.** **INCLUDED IN V0 BENCHMARK.**
   Question 8 of the benchmark suite is an adversarial-prompting query
   designed to push the model toward stupid-industrious mode. Per the
   empirical baseline (`research/HAMMERSTEIN-FRAMEWORK.md` §5,
   `corpus/entries/13`), prompt-level corruption resistance is the
   framework's strongest claim and should be measured.

7. **Cross-model cell coverage in eval.** **Three primary cells +
   ablations.** Primary: Claude-baseline / Hammerstein-on-Ollama /
   Hammerstein-on-OpenRouter. Ablations: prompt-only / corpus-only /
   8B vs 70B of same family. The ablations distinguish which framework
   component is doing the heavy lifting, per
   `prompts/templates/review-from-different-angle.md` example 1.

---

## Tooling decisions, locked

- **Python 3.11+** for the harness
- **Ollama** for local inference
- **OpenRouter API** for cloud fallback (key already configured at
  `~/.generalstaff/.env`)
- **Sentence-transformers** for embeddings if RAG Option A is taken
- **JSON or SQLite** for corpus index (decided per corpus shape)
- **No proprietary dependencies** — every layer is open-source or
  pay-per-call public API

## Tooling decisions, locked v1

- **Embedding model:** none at v0 (Option B static corpus). If
  Option A is taken at v1+, `sentence-transformers/all-MiniLM-L6-v2`.
- **RAG retrieval:** Option B (static corpus in prompt) at v0.
  Migration to Option A (embedding-based) at v1+ when corpus exceeds
  ~80 entries.
- **System-prompt template engine:** **plain f-string** in Python.
  Simple, no extra dependencies, sufficient for the v0 prompt's
  shape. (Jinja2 is reserved for if v1+ adds template inheritance or
  conditional sections.)
- **Eval scoring rubric:** operator-rated 1-5 across **three axes**:
  framework-fidelity, usefulness, voice-match
  (`scope/PHASED-ROADMAP.md` v0 ship criteria).
- **Logging format:** JSONL, one line per call, fields per the
  v1-lock summary at top of this file.
- **Few-shot template selection:** classifier-driven; default to
  `scope-this-idea` if no clear classifier match.

None of these block v0 starting; all are now locked.

---

## What this lock means in practice

After the research session ships:

- v0 implementation can start without tech-stack debate
- The harness has a clear shape (Python CLI, Ollama primary, OpenRouter
  fallback, simple corpus retrieval)
- The eval harness has a clear shape (run benchmarks, dump responses,
  the operator rates)
- Cross-machine deployment is a `pip install -e .` away
- Cost ceiling is bounded: $0 local, $0.001-$0.01 per cloud call

The research session's Deliverable 5 may refine specific parameter
choices (embedding model, retrieval algorithm, etc.) but the load-
bearing decisions (Ollama, OpenRouter, Python CLI, JSON-or-SQLite
corpus) are locked here.
