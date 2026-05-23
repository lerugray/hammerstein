import os
import re
import socket
from importlib import resources as importlib_resources

import pytest
import yaml

from hammerstein.cli import run


Q1 = (
    "Account ban / affordability collapse / Anthropic-specific outage are\n"
    "real tail risks for my Claude usage. The portfolio survives those\n"
    "without a Claude-substitute for code work — cursor-agent CLI +\n"
    "OpenRouter Qwen + Gemini CLI + Ollama already cover it. The gap is\n"
    "strategic reasoning (the staff-officer / orchestrator role\n"
    "interactive Claude fills). Should I build a Claude-substitute for\n"
    "strategic reasoning, or validate the existing fallbacks first?"
)

Q3 = (
    "I've been heads-down on catalogdna technical work for two weeks —\n"
    "shipped the analyzer pipeline, fixed three bot bugs, refactored the\n"
    "queue. Backlog still has 40 items. Should I keep grinding, or is\n"
    "there a strategic question I'm missing?"
)

Q5 = (
    "The bot keeps shipping work that misses load-bearing constraints —\n"
    "not because the constraints aren't documented, but because the bot\n"
    "doesn't always check them before acting. The fix I'm considering is\n"
    "updating CLAUDE.md to be more explicit about checking constraints.\n"
    "Is that the right shape of fix?"
)


FRAMEWORK_MARKERS = (
    "clever-lazy",
    "stupid-industrious",
    "verification",
    "framework",
    "counter-observation",
)

TEMPLATE_MARKERS = {
    "scope-this-idea": ("Scope:", "The cut:", "Main tradeoff:", "Recommendation:", "Counter-observation:"),
    "audit-this-plan": ("Failure modes:", "Verification gates:", "Structural-fix", "Recommendation:", "Counter-observation:"),
    "what-should-we-do-next": ("Ranked priority", "To deprioritize", "Counter-observation:"),
}


def _load_chain():
    txt = (
        importlib_resources.files("hammerstein_resources")
        .joinpath("providers.yaml")
        .read_text(encoding="utf-8")
    )
    cfg = yaml.safe_load(txt)
    return cfg["chain"]


def _ollama_reachable() -> bool:
    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    # Best-effort: parse http://host:port. Bare-string regex; raw-string
    # `\\d` was a literal backslash-d that never matched digits — port
    # capture always fell through to the default. Functionally harmless
    # (default 11434 is the real ollama port) but corrected for clarity.
    m = re.match(r"^https?://([^:/]+)(?::(\d+))?", host)
    if not m:
        return False
    h = m.group(1)
    p = int(m.group(2) or "11434")
    try:
        with socket.create_connection((h, p), timeout=1.0):
            return True
    except OSError:
        return False


def _has_openrouter_key() -> bool:
    return bool(os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY"))


def _has_deepseek_key() -> bool:
    return bool(os.environ.get("DEEPSEEK_API_KEY"))


def _skip_reason(step: dict) -> str | None:
    backend = step["backend"]
    if backend == "ollama" and not _ollama_reachable():
        return "OLLAMA_HOST not reachable"
    if backend == "openrouter" and not _has_openrouter_key():
        return "OPENROUTER_API_KEY/OPENAI_API_KEY not set"
    if backend == "deepseek" and not _has_deepseek_key():
        return "DEEPSEEK_API_KEY not set"
    if backend == "claude" and not os.environ.get("ANTHROPIC_API_KEY"):
        return "ANTHROPIC_API_KEY not set"
    return None


def _queries():
    return [
        (Q1, "scope-this-idea"),
        (Q3, "what-should-we-do-next"),
        (Q5, "audit-this-plan"),
    ]


def test_continuity_chain_each_provider(tmp_path, capsys):
    chain = _load_chain()

    passed_providers = 0
    runnable = 0
    for step in chain:
        skip = _skip_reason(step)
        if skip:
            continue

        runnable += 1
        model_spec = f"{step['backend']}:{step['model']}"
        ok = False
        for q, template in _queries():
            log_path = tmp_path / f"calls-{step['id']}.jsonl"
            code = run(
                q,
                model_spec=model_spec,
                template_name=template,
                no_corpus=False,
                corpus_only=False,
                top_k=4,
                show_prompt=False,
                log_path=log_path,
            )
            out = capsys.readouterr().out

            if code != 0:
                continue
            if len(out) <= 200:
                continue
            if not any(m in out.lower() for m in FRAMEWORK_MARKERS):
                continue
            # Smaller local models (qwen3:8b on ollama) reliably hit
            # FRAMEWORK_MARKERS but may not faithfully reproduce the
            # template-specific section headers ("Scope:", "Failure
            # modes:", etc.). Per ham-017 (Windows continuity-chain
            # fragility): the test asserts continuity smoke -- non-empty
            # + on-framework output -- not template-quality parity with
            # paid cloud models. Cloud backends still require both
            # framework AND template markers as the stronger signal.
            if step["backend"] != "ollama" and template in TEMPLATE_MARKERS and not any(
                m in out for m in TEMPLATE_MARKERS[template]
            ):
                continue
            ok = True
            break

        assert ok, f"provider {step['id']} produced no passing response"
        passed_providers += 1

    if runnable == 0:
        pytest.skip("no runnable providers (missing keys and/or OLLAMA_HOST unreachable)")
    assert passed_providers == runnable

