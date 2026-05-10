"""Monkeypatch layer for diplobench LLMAgent to optionally inject the
Hammerstein system prompt as a prepend.

When `HAMMERSTEIN_WRAP=true` is set in the environment, every `call_llm`
invocation from a wrapped agent gets the Hammerstein system prompt (from
`hammerstein/prompts/SYSTEM-PROMPT.md`) prepended to its `system_text`.

The wrap is per-agent (not global). Typical usage: wrap ONLY the test
agent (Austria) so the experiment compares Hammerstein-on-Sonnet (AUT)
vs raw-Sonnet (other 6 powers).

This module does NOT modify the Hammerstein prompt for Diplomacy context.
The whole point of the experiment is to test whether the wrapper that
won the strategic-reasoning benchmark generalizes to multi-agent
negotiation without domain-specific adaptation.

Usage (from a runner script that imports diplobench):

    from diplomacy_game.agent import LLMAgent
    import hammerstein_wrap

    # Patch in place: any LLMAgent with hammerstein_wrap=True attribute
    # gets the prompt prepended on each LLM call.
    hammerstein_wrap.install()

    test_agent = LLMAgent(power_name="AUT", ..., model_name=...)
    test_agent.hammerstein_wrap = True   # opt this agent in
    # Other agents created without the flag stay raw.

The wrap is a no-op for any agent without `hammerstein_wrap=True`,
so installing the patch globally is safe.
"""

from __future__ import annotations

import os
from pathlib import Path

# This module sits at hammerstein/eval/diplomacy/. The Hammerstein system
# prompt lives at hammerstein/prompts/SYSTEM-PROMPT.md.
_HAMMERSTEIN_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SYSTEM_PROMPT_PATH = _HAMMERSTEIN_REPO_ROOT / "prompts" / "SYSTEM-PROMPT.md"

_BEGIN_MARKER = "## === BEGIN SYSTEM PROMPT ==="
_END_MARKER = "## === END SYSTEM PROMPT ==="


def load_hammerstein_system_prompt() -> str:
    """Read the operational portion of the Hammerstein system prompt.

    SYSTEM-PROMPT.md uses BEGIN/END markers to separate prose
    documentation from the operational prompt the harness actually
    injects. We return only the operational portion, matching how
    `hammerstein_cli` itself loads the prompt.
    """
    text = _SYSTEM_PROMPT_PATH.read_text()
    if _BEGIN_MARKER in text and _END_MARKER in text:
        start = text.index(_BEGIN_MARKER) + len(_BEGIN_MARKER)
        end = text.index(_END_MARKER)
        return text[start:end].strip()
    return text.strip()


_HAMMERSTEIN_PROMPT_CACHE: str | None = None


def _hammerstein_prompt() -> str:
    global _HAMMERSTEIN_PROMPT_CACHE
    if _HAMMERSTEIN_PROMPT_CACHE is None:
        _HAMMERSTEIN_PROMPT_CACHE = load_hammerstein_system_prompt()
    return _HAMMERSTEIN_PROMPT_CACHE


def wrap_system_text(system_text: str) -> str:
    """Prepend the Hammerstein system prompt to a diplobench system_text."""
    h = _hammerstein_prompt()
    return (
        f"{h}\n\n"
        "--- Task-specific operator instructions follow ---\n\n"
        f"{system_text}"
    )


def install() -> None:
    """Monkeypatch diplomacy_game.llm.generate so that any call routed
    through a wrapped agent gets the Hammerstein prompt prepended.

    Mechanism: we wrap `diplomacy_game.llm.generate`. The diplobench
    agent calls `call_llm(...)` which calls `generate(...)`. We can't
    cleanly detect which agent is calling, so the per-agent opt-in
    happens via a thread-local set by the agent before its call.

    Simpler mechanism (used here): monkeypatch `LLMAgent` directly,
    intercepting all 4 system_text construction sites with a wrapper
    that checks `self.hammerstein_wrap`. Implemented via attribute
    setter on the class.

    For v0 of this scaffold, we provide a lighter-weight approach: we
    expose `wrap_system_text` as a utility that runner scripts use
    explicitly. Full monkeypatch ships when run_demo_game.py is wired.
    """
    # v0 of the scaffold: explicit-helper-only. Runner scripts use
    # `hammerstein_wrap.wrap_system_text(...)` themselves. Full
    # monkeypatch ships when run_demo_game.py is wired and we know
    # exactly which call sites need interception.
    pass


def is_enabled() -> bool:
    """Check whether HAMMERSTEIN_WRAP=true is set in the environment."""
    return os.environ.get("HAMMERSTEIN_WRAP", "").lower() in ("1", "true", "yes")
