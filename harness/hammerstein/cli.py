"""Hammerstein v0 CLI core (importable).

This module exists so both:
- `python harness/hammerstein.py "<query>"` (script wrapper), and
- the pip-installed `hammerstein "<query>"` console entrypoint

share the same implementation.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from importlib import resources as importlib_resources
from pathlib import Path

# Force UTF-8 stdout/stderr on Windows. Python's default cp1252 codepage
# can't encode em-dashes / smart quotes that the response often contains,
# which crashes the CLI when output is piped (e.g. from a daily brief
# script). Safe on POSIX (already UTF-8 by default).
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, OSError):
        pass

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    yaml = None  # type: ignore

from . import backends, classifier, corpus as corpus_mod, logger, prompt as prompt_mod
from . import shape_gate
from .context import ContextDisabled, ContextMode, build_project_context_preamble

DEFAULT_LOG_PATH = Path.home() / ".hammerstein" / "logs" / "hammerstein-calls.jsonl"

# Backend defaults. Local Ollama uses Qwen 8B per `tech/STACK-DECISION.md`.
# OpenRouter default is paid Qwen3.6-plus per the same doc.
_BACKEND_DEFAULTS = {
    "ollama": "qwen3:8b",
    "openrouter": "qwen/qwen3.6-plus",
    "deepseek": "deepseek-chat",
    "claude": "claude-sonnet-4-6",
}

_BACKENDS = {"ollama", "openrouter", "deepseek", "claude"}

_DEFAULT_PROVIDERS_RESOURCE = "hammerstein_resources"
_DEFAULT_PROVIDERS_FILENAME = "providers.yaml"

# OpenRouter free-tier vision pool (Gemini Flash) for --backend-tier free + --image.
_VISION_FREE_OPENROUTER_MODEL = "google/gemini-2.0-flash-exp:free"

# Vision-Hammerstein routing lock (ham-022e bake-off, 2026-05-09 evening).
# Bake-off result on 2 of 3 real benchmark cases: Qwen3-VL-Plus failed
# shape-gate on both real fixtures (TWAR PC Surface 5 hex-grid render,
# retrogaze rg-023 NES knight); GPT-4o passed shape AND semantic on
# both. Decision tree applied: "Qwen failed shape on real fixtures
# -> GPT-4o flat default, no failover" per scope/VISION-SUPPORT.md.
# DeepSeek probe returned no vision-capable model. FnordOS DEPT-23
# panel still placeholder; re-running the bake-off after that fixture
# lands may reverse the lock if Qwen passes 3/3.
_VISION_DEFAULT_BACKEND = "openrouter"
_VISION_DEFAULT_MODEL = "openai/gpt-4o"
_VISION_FAILOVER_BACKEND: str | None = None
_VISION_FAILOVER_MODEL: str | None = None


def _load_providers_config() -> dict:
    """Load providers.yaml from packaged resources, falling back to repo root."""
    def _parse(text: str) -> dict:
        if yaml is not None:
            return yaml.safe_load(text) or {}
        # Minimal, schema-specific fallback parser (stdlib-only).
        cfg: dict = {}
        chain: list[dict] = []
        current: dict | None = None
        for raw in text.splitlines():
            line = raw.rstrip()
            if not line or line.lstrip().startswith("#"):
                continue
            if line.startswith("chain:"):
                cfg["chain"] = chain
                continue
            if line.startswith("on_") and ":" in line and not line.startswith("-"):
                k, _, v = line.partition(":")
                cfg[k.strip()] = v.strip()
                continue
            if line.lstrip().startswith("- "):
                current = {}
                chain.append(current)
                rest = line.lstrip()[2:]
                if ":" in rest:
                    k, _, v = rest.partition(":")
                    current[k.strip()] = v.strip()
                continue
            if current is not None and ":" in line:
                k, _, v = line.strip().partition(":")
                val = v.strip()
                if k.strip() == "timeout_seconds":
                    try:
                        current[k.strip()] = int(val)
                    except ValueError:
                        current[k.strip()] = val
                else:
                    current[k.strip()] = val
        return cfg

    try:
        cfg_text = (
            importlib_resources.files(_DEFAULT_PROVIDERS_RESOURCE)
            .joinpath(_DEFAULT_PROVIDERS_FILENAME)
            .read_text(encoding="utf-8")
        )
        cfg = _parse(cfg_text)
        if isinstance(cfg, dict) and cfg.get("chain"):
            return cfg
    except Exception:
        pass

    repo_root = Path(__file__).resolve().parents[2]
    path = repo_root / _DEFAULT_PROVIDERS_FILENAME
    if path.exists():
        cfg = _parse(path.read_text(encoding="utf-8"))
        if isinstance(cfg, dict):
            return cfg
    raise SystemExit(
        "providers.yaml not found. Expected a packaged resource at "
        f"{_DEFAULT_PROVIDERS_RESOURCE}/{_DEFAULT_PROVIDERS_FILENAME} or a file at {path}."
    )


def _action(cfg: dict, key: str) -> str:
    v = (cfg or {}).get(key, "next")
    return str(v).strip().lower() if v is not None else "next"


def parse_model_spec(spec: str | None) -> tuple[str, str]:
    """Parse `<backend>:<model>` or `<backend>`. Returns (backend, model).

    When `spec` is None, falls back to the `HAMMERSTEIN_DEFAULT_MODEL`
    environment variable if set, otherwise to `ollama:qwen3:8b`. Per-machine
    override lets users without a working local Ollama (no GPU, etc.) point
    Hammerstein at a cloud backend by default without changing flags.
    """
    if not spec:
        env_default = os.environ.get("HAMMERSTEIN_DEFAULT_MODEL")
        if env_default:
            spec = env_default
        else:
            return "ollama", _BACKEND_DEFAULTS["ollama"]
    if ":" in spec:
        backend, _, model = spec.partition(":")
        backend = backend.strip().lower()
        model = model.strip()
        if backend not in _BACKENDS:
            raise SystemExit(
                f"unknown backend '{backend}'; pick one of {sorted(_BACKENDS)}"
            )
        if not model:
            model = _BACKEND_DEFAULTS[backend]
        return backend, model
    backend = spec.strip().lower()
    if backend in _BACKENDS:
        return backend, _BACKEND_DEFAULTS[backend]
    raise SystemExit(
        f"could not parse --model '{spec}'. Expected '<backend>' or "
        f"'<backend>:<model>' where backend is one of {sorted(_BACKENDS)}."
    )


def _load_env_key(env_path: Path, name: str) -> str | None:
    """Best-effort .env loader. Returns None if file or key is absent."""
    if name in os.environ:
        return os.environ[name]
    if not env_path.exists():
        return None
    try:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            if key.strip() == name:
                return val.strip().strip('"').strip("'")
    except OSError:
        return None
    return None


def _resolve_api_key(backend: str) -> str:
    """Resolve an API key for a cloud backend. Raises SystemExit if missing."""
    miroshark_env = Path(r"C:/Users/rweis/<repo>/<a partner project>/.env")
    if backend == "openrouter":
        # Per ~/.claude/CLAUDE.md, OpenRouter key is stored under OPENAI_API_KEY
        # in <a partner project>/.env.
        for name in ("OPENROUTER_API_KEY", "OPENAI_API_KEY"):
            key = _load_env_key(miroshark_env, name)
            if key:
                return key
        raise backends.BackendError(
            "OpenRouter API key not found. Set OPENROUTER_API_KEY or "
            "place it under OPENAI_API_KEY in <a partner project>/.env."
        )
    if backend == "deepseek":
        key = _load_env_key(miroshark_env, "DEEPSEEK_API_KEY")
        if key:
            return key
        raise backends.BackendError("DEEPSEEK_API_KEY not found in <a partner project>/.env or env.")
    if backend == "claude":
        key = _load_env_key(miroshark_env, "ANTHROPIC_API_KEY")
        if key:
            return key
        raise backends.BackendError("ANTHROPIC_API_KEY not found.")
    raise backends.BackendError(f"no API key needed for backend '{backend}'")


def _dispatch(
    backend: str,
    model: str,
    full_prompt: str,
    *,
    timeout_seconds: int,
    image_path: str | None = None,
) -> backends.CallResult:
    """Route the prompt to the right backend."""
    if backend == "ollama":
        if image_path:
            raise backends.BackendError(
                "Ollama multimodal input is not supported in Hammerstein v0; "
                "use OpenRouter, DeepSeek, or Claude (see --model or providers.yaml)."
            )
        host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        return backends.call_ollama(
            full_prompt,
            model=model,
            host=host,
            timeout=timeout_seconds,
        )
    if backend == "openrouter":
        return backends.call_openrouter(
            full_prompt,
            model=model,
            api_key=_resolve_api_key("openrouter"),
            timeout=timeout_seconds,
            image_path=image_path,
        )
    if backend == "deepseek":
        return backends.call_deepseek(
            full_prompt,
            model=model,
            api_key=_resolve_api_key("deepseek"),
            timeout=timeout_seconds,
            image_path=image_path,
        )
    if backend == "claude":
        return backends.call_claude(
            full_prompt,
            model=model,
            api_key=_resolve_api_key("claude"),
            timeout=timeout_seconds,
            image_path=image_path,
        )
    raise SystemExit(f"unknown backend: {backend}")


def _shape_gate_audit_visual(
    result: backends.CallResult,
    *,
    primary_label: str,
    full_prompt: str,
    image: str,
) -> tuple[backends.CallResult, str]:
    """Validate audit-this-visual output shape; optionally fail over once.

    Returns (final_result, meta_suffix) where meta_suffix is either
    ' shape_gate=passed' or ' shape_gate=failed_over'.
    """

    if shape_gate.is_well_shaped(result.response):
        return result, " shape_gate=passed"

    primary_log = shape_gate.log_raw_response(
        result.response or "",
        model=primary_label,
        attempt=1,
    )

    # Per the ham-022e bake-off lock: when failover is None (current
    # state, GPT-4o flat default), shape-gate failure is terminal --
    # no second-attempt retry, log raw + raise.
    if _VISION_FAILOVER_BACKEND is None or _VISION_FAILOVER_MODEL is None:
        raise shape_gate.ShapeGateFailure(primary_log)

    def _failover() -> backends.CallResult:
        return _dispatch(
            _VISION_FAILOVER_BACKEND,
            _VISION_FAILOVER_MODEL,
            full_prompt,
            timeout_seconds=120,
            image_path=image,
        )

    try:
        retry_result = _failover()
    except backends.BackendError as exc:
        raise shape_gate.ShapeGateFailure(primary_log) from exc

    if shape_gate.is_well_shaped(retry_result.response):
        return retry_result, " shape_gate=failed_over"

    failover_log = shape_gate.log_raw_response(
        retry_result.response or "",
        model=f"{_VISION_FAILOVER_BACKEND}:{_VISION_FAILOVER_MODEL}",
        attempt=2,
    )
    raise shape_gate.ShapeGateFailure(primary_log, failover_log)


def run(
    query: str,
    *,
    model_spec: str | None,
    template_name: str | None,
    no_corpus: bool,
    corpus_only: bool,
    top_k: int,
    show_prompt: bool,
    log_path: Path,
    context_mode: ContextMode | None,
    project_root: Path | None,
    context_file: Path | None,
    image: str | None = None,
    backend_tier: str | None = None,
) -> int:
    """One-shot dispatch. Returns process exit code."""
    if no_corpus and corpus_only:
        print("--no-corpus and --corpus-only are mutually exclusive", file=sys.stderr)
        return 2

    # If --model was not passed but HAMMERSTEIN_DEFAULT_MODEL is set, honor it
    # as an explicit single-provider invocation. This bypasses the fallback
    # chain in favor of the user's per-machine default — the right behavior on
    # machines where the chain's first step (often local Ollama) isn't viable.
    if model_spec is None:
        env_default = os.environ.get("HAMMERSTEIN_DEFAULT_MODEL")
        if env_default:
            model_spec = env_default

    raw_query = query

    if template_name == "auto" or template_name is None:
        template_name = classifier.classify(raw_query)
    elif template_name not in classifier.TEMPLATES:
        print(
            f"unknown template '{template_name}'; pick one of "
            f"{sorted(classifier.TEMPLATES)}",
            file=sys.stderr,
        )
        return 2

    # Template-level context defaults (only if user did NOT pass --context).
    if context_mode is None:
        if template_name in {
            "audit-this-plan",
            "audit-this-visual",
            "what-should-we-do-next",
        }:
            context_mode = "minimal"
        else:
            context_mode = "none"

    if corpus_only:
        mode = "corpus-only"
    elif no_corpus:
        mode = "no-corpus"
    else:
        mode = "default"

    system_prompt_file = importlib_resources.files("prompts").joinpath("SYSTEM-PROMPT.md")
    system_prompt = prompt_mod.load_system_prompt_resource(system_prompt_file)
    template_text = (
        None
        if mode == "corpus-only"
        else prompt_mod.load_template_resource(
            importlib_resources.files("prompts.templates").joinpath(f"{template_name}.md")
        )
    )
    if mode == "no-corpus":
        retrieved: list[corpus_mod.CorpusEntry] = []
    else:
        entries_dir = importlib_resources.files("corpus.entries")
        all_entries = corpus_mod.load_corpus(entries_dir)
        retrieved = corpus_mod.retrieve(
            all_entries, raw_query, template=template_name, top_k=top_k
        )

    context_preamble = ""
    if context_mode != "none":
        try:
            context_preamble = build_project_context_preamble(
                mode=context_mode,
                project_root=project_root,
                context_file=context_file,
            )
        except ContextDisabled as exc:
            print(
                "warning: project context injection disabled "
                f"({exc.reason}); re-run with --context none or provide sanitized --context-file",
                file=sys.stderr,
            )
            context_preamble = ""

    injected_query = raw_query if not context_preamble else (context_preamble + "\n\n" + raw_query)

    full_prompt = prompt_mod.assemble_prompt(
        system_prompt=system_prompt,
        template_text=template_text,
        corpus_entries=retrieved,
        query=injected_query,
        mode=mode,
    )

    if show_prompt:
        print(full_prompt)
        return 0

    # Explicit single-provider invocation bypasses the chain.
    if model_spec:
        backend, model = parse_model_spec(model_spec)
        if image and backend == "ollama":
            print(
                "Ollama does not support --image in Hammerstein v0; "
                "use a cloud backend, e.g. --model openrouter:... or --model claude:...",
                file=sys.stderr,
            )
            return 2
        record = logger.CallRecord(
            timestamp=logger.now_iso(),
            backend=backend,
            model=model,
            provider_id=None,
            chain_step=None,
            chain_len=None,
            system_prompt_version=prompt_mod.SYSTEM_PROMPT_VERSION,
            template=None if mode == "corpus-only" else template_name,
            retrieved_corpus_ids=[e.id for e in retrieved],
            query=query,
            mode=mode,
        )
        start = time.perf_counter()
        try:
            result = _dispatch(
                backend,
                model,
                full_prompt,
                timeout_seconds=120,
                image_path=image,
            )
        except backends.BackendError as exc:
            record.error = str(exc)
            record.latency_ms = int((time.perf_counter() - start) * 1000)
            logger.append(record, log_path)
            print(f"backend error: {exc}", file=sys.stderr)
            return 1
    else:
        cfg = _load_providers_config()
        chain = list(cfg.get("chain") or [])
        if not chain:
            raise SystemExit("providers.yaml has empty chain")

        if image:
            if backend_tier == "free":
                chain = [
                    {
                        "id": "vision-free-openrouter",
                        "backend": "openrouter",
                        "model": _VISION_FREE_OPENROUTER_MODEL,
                        "timeout_seconds": 90,
                    }
                ]
            elif backend_tier == "paid":
                # Per the ham-022e bake-off lock: GPT-4o flat default,
                # no failover. Replace the paid chain with just the
                # locked default rather than running the providers.yaml
                # chain (which may include lower-priority Qwen-style
                # entries that would still hit shape-gate failures).
                chain = [
                    {
                        "id": "vision-default-locked",
                        "backend": _VISION_DEFAULT_BACKEND,
                        "model": _VISION_DEFAULT_MODEL,
                        "timeout_seconds": 120,
                    }
                ]
            else:
                # Default --image (no --backend-tier): apply the same
                # locked default as paid. This is the v0 release-locking
                # decision; flip back to providers.yaml chain only when
                # a future bake-off run with all 3 real fixtures
                # (TWAR PC + retrogaze + FnordOS) reverses the lock.
                chain = [
                    {
                        "id": "vision-default-locked",
                        "backend": _VISION_DEFAULT_BACKEND,
                        "model": _VISION_DEFAULT_MODEL,
                        "timeout_seconds": 120,
                    }
                ]
            if not chain:
                print(
                    "no vision-capable providers remain in the chain after applying "
                    "--backend-tier / image constraints",
                    file=sys.stderr,
                )
                return 2

        last_err: str | None = None
        for idx, step in enumerate(chain, start=1):
            provider_id = str(step.get("id") or f"step-{idx}")
            backend = str(step.get("backend") or "").strip().lower()
            model = str(step.get("model") or "").strip()
            timeout_seconds = int(step.get("timeout_seconds") or 120)

            if image and backend == "ollama":
                continue

            if image and backend == "deepseek":
                try:
                    ds_key = _resolve_api_key("deepseek")
                except backends.BackendError:
                    continue
                probe_timeout = min(5, timeout_seconds)
                if not backends.deepseek_supports_vision(
                    ds_key, timeout=probe_timeout
                ):
                    continue

            record = logger.CallRecord(
                timestamp=logger.now_iso(),
                backend=backend,
                model=model,
                provider_id=provider_id,
                chain_step=idx,
                chain_len=len(chain),
                system_prompt_version=prompt_mod.SYSTEM_PROMPT_VERSION,
                template=None if mode == "corpus-only" else template_name,
                retrieved_corpus_ids=[e.id for e in retrieved],
                query=query,
                mode=mode,
            )

            start = time.perf_counter()
            try:
                result = _dispatch(
                    backend,
                    model,
                    full_prompt,
                    timeout_seconds=timeout_seconds,
                    image_path=image,
                )
            except backends.RateLimitError as exc:
                record.error = str(exc)
                record.latency_ms = int((time.perf_counter() - start) * 1000)
                logger.append(record, log_path)
                last_err = f"[provider={provider_id}] 429 rate limited: {exc}"
                if _action(cfg, "on_429") != "next":
                    break
                continue
            except backends.TimeoutError as exc:
                record.error = str(exc)
                record.latency_ms = int((time.perf_counter() - start) * 1000)
                logger.append(record, log_path)
                last_err = f"[provider={provider_id}] timeout: {exc}"
                if _action(cfg, "on_timeout") != "next":
                    break
                continue
            except backends.ParseError as exc:
                record.error = str(exc)
                record.latency_ms = int((time.perf_counter() - start) * 1000)
                logger.append(record, log_path)
                last_err = f"[provider={provider_id}] parse error: {exc}"
                if _action(cfg, "on_parse_error") != "next":
                    break
                continue
            except backends.BackendError as exc:
                record.error = str(exc)
                record.latency_ms = int((time.perf_counter() - start) * 1000)
                logger.append(record, log_path)
                last_err = f"[provider={provider_id}] backend error: {exc}"
                if _action(cfg, "on_backend_error") != "next":
                    break
                continue

            shape_gate_meta = ""
            vision_audit = template_name == "audit-this-visual" and image is not None

            if vision_audit:
                if not result.response:
                    record.response = result.response
                    record.response_length = (
                        len(result.response) if result.response else 0
                    )
                    record.latency_ms = result.latency_ms
                    record.cost_usd = result.cost_usd
                    logger.append(record, log_path)
                    record.error = "backend returned empty/null response"
                    logger.append(record, log_path)
                    last_err = f"[provider={provider_id}] empty response"
                    if _action(cfg, "on_empty_response") == "next":
                        continue
                    break
                try:
                    result, shape_gate_meta = _shape_gate_audit_visual(
                        result,
                        primary_label=f"{backend}:{model}",
                        full_prompt=full_prompt,
                        image=image,
                    )
                except shape_gate.ShapeGateFailure as exc:
                    print(f"shape-gate failed: {exc}", file=sys.stderr)
                    return 1
                if shape_gate_meta == " shape_gate=failed_over":
                    record.backend = _VISION_FAILOVER_BACKEND
                    record.model = _VISION_FAILOVER_MODEL
                record.response = result.response
                record.response_length = len(result.response) if result.response else 0
                record.latency_ms = result.latency_ms
                record.cost_usd = result.cost_usd
                logger.append(record, log_path)
            else:
                record.response = result.response
                record.response_length = len(result.response) if result.response else 0
                record.latency_ms = result.latency_ms
                record.cost_usd = result.cost_usd
                logger.append(record, log_path)

                if not result.response:
                    record.error = "backend returned empty/null response"
                    logger.append(record, log_path)
                    last_err = f"[provider={provider_id}] empty response"
                    if _action(cfg, "on_empty_response") == "next":
                        continue
                    break

            print(result.response)
            meta = (
                f"\n[chain_step={idx}/{len(chain)} provider={provider_id} "
                f"latency_ms={result.latency_ms} cost=${result.cost_usd:.5f}"
            )
            if image:
                meta += f" image_bytes={os.path.getsize(image)}{shape_gate_meta}"
            else:
                meta += shape_gate_meta
            meta += "]"
            print(meta, file=sys.stderr)
            return 0

        print("all providers failed.", file=sys.stderr)
        if last_err:
            print(last_err, file=sys.stderr)
        return 1

    shape_gate_meta = ""
    vision_audit = image is not None and template_name == "audit-this-visual"

    if vision_audit:
        if not result.response:
            record.response = result.response
            record.response_length = len(result.response) if result.response else 0
            record.latency_ms = result.latency_ms
            record.cost_usd = result.cost_usd
            logger.append(record, log_path)
            record.error = "backend returned empty/null response"
            logger.append(record, log_path)
            print(
                f"backend warning: empty/null response from {backend} ({model})",
                file=sys.stderr,
            )
            return 1
        try:
            result, shape_gate_meta = _shape_gate_audit_visual(
                result,
                primary_label=f"{backend}:{model}",
                full_prompt=full_prompt,
                image=image,
            )
        except shape_gate.ShapeGateFailure as exc:
            print(f"shape-gate failed: {exc}", file=sys.stderr)
            return 1
        if shape_gate_meta == " shape_gate=failed_over":
            backend = _VISION_FAILOVER_BACKEND
            model = _VISION_FAILOVER_MODEL
            record.backend = backend
            record.model = model
        record.response = result.response
        record.response_length = len(result.response) if result.response else 0
        record.latency_ms = result.latency_ms
        record.cost_usd = result.cost_usd
        logger.append(record, log_path)
    else:
        record.response = result.response
        record.response_length = len(result.response) if result.response else 0
        record.latency_ms = result.latency_ms
        record.cost_usd = result.cost_usd
        logger.append(record, log_path)

        if not result.response:
            record.error = "backend returned empty/null response"
            logger.append(record, log_path)
            print(
                f"backend warning: empty/null response from {backend} ({model})",
                file=sys.stderr,
            )
            return 1

    print(result.response)
    meta = (
        f"\n[backend={backend} model={model} template={template_name} "
        f"corpus={len(retrieved)} latency_ms={result.latency_ms} "
        f"cost_usd=${result.cost_usd:.5f}"
    )
    if image:
        meta += f" image_bytes={os.path.getsize(image)}{shape_gate_meta}"
    else:
        meta += shape_gate_meta
    meta += "]"
    print(meta, file=sys.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="hammerstein",
        description="Hammerstein v0 strategic-reasoning harness.",
    )
    p.add_argument("query", nargs="?", help="strategic-reasoning query (string)")
    p.add_argument(
        "--model",
        default=None,
        help="Backend or backend:model spec. If unset, uses providers.yaml fallback chain.",
    )
    p.add_argument(
        "--template",
        default="auto",
        help="Few-shot template (auto|scope-this-idea|audit-this-plan|"
        "audit-this-visual|is-this-worth-doing|what-should-we-do-next|review-from-different-angle).",
    )
    p.add_argument(
        "--no-corpus",
        action="store_true",
        help="Ablation: skip corpus retrieval (prompt+template only).",
    )
    p.add_argument(
        "--corpus-only",
        action="store_true",
        help="Ablation: minimal system prompt + corpus only (drop framework prompt + template).",
    )
    p.add_argument("--top-k", type=int, default=4, help="Corpus entries to retrieve.")
    p.add_argument(
        "--image",
        default=None,
        help="Path to an image file (PNG/JPG/JPEG/WebP) to include as "
        "multimodal input. Only valid with --template audit-this-visual.",
    )
    p.add_argument(
        "--backend-tier",
        default=None,
        choices=["free", "paid"],
        help="Explicit backend tier for vision-Hammerstein audits. 'free' "
        "routes through the free vision pool (Gemini Flash via OpenRouter); "
        "'paid' forces the paid pool default. Default is None (use the "
        "providers.yaml fallback chain).",
    )
    p.add_argument(
        "--context",
        choices=("none", "minimal"),
        default=None,
        help=(
            "Project context injection mode. If omitted, a template-level default may apply "
            "(e.g. audits default to minimal; pure queries default to none)."
        ),
    )
    p.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Override repo detection: build context from this project root path.",
    )
    p.add_argument(
        "--context-file",
        type=Path,
        default=None,
        help="Explicit context preamble file to inject (preferred). If omitted, minimal mode may auto-discover a state file at project root.",
    )
    p.add_argument(
        "--show-prompt",
        action="store_true",
        help="Print the assembled prompt and exit. Skips inference.",
    )
    p.add_argument(
        "--log",
        type=Path,
        default=DEFAULT_LOG_PATH,
        help="Path to JSONL call log.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.query:
        parser.print_help()
        return 2
    if args.image:
        if args.template != "audit-this-visual":
            print(
                "--image is only supported with --template audit-this-visual; "
                "use --template audit-this-visual to opt in",
                file=sys.stderr,
            )
            return 2
        if not os.path.isfile(args.image):
            print(
                f"--image path is not a readable file: {args.image!r}",
                file=sys.stderr,
            )
            return 2
    return run(
        args.query,
        model_spec=args.model,
        template_name=args.template,
        no_corpus=args.no_corpus,
        corpus_only=args.corpus_only,
        top_k=args.top_k,
        show_prompt=args.show_prompt,
        log_path=args.log,
        context_mode=args.context,
        project_root=args.project_root,
        context_file=args.context_file,
        image=args.image,
        backend_tier=args.backend_tier,
    )

