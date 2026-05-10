"""Run a Hammerstein-wrapped Diplomacy game via diplobench.

Monkeypatches diplobench's `LLMAgent` so the test agent (Austria) gets
the Hammerstein system prompt prepended to every LLM call. Other 6
powers stay raw, identical to a baseline diplobench run.

Usage (from a checkout where diplobench/ is a sibling of hammerstein/):

    cd /path/to/diplobench
    pip install -r requirements.txt
    # Download RL policy weights (one-time, free):
    mkdir -p welfare_diplomacy_baselines/network_parameters
    curl -L https://storage.googleapis.com/dm-diplomacy/fppi2_params.npz \
        -o welfare_diplomacy_baselines/network_parameters/fppi2_params.npz
    # Set credentials (OpenRouter via OpenAI-compat):
    export OPENAI_API_KEY=$OPENROUTER_API_KEY
    export OPENAI_BASE_URL=https://openrouter.ai/api/v1
    export TEST_AGENT_MODEL=anthropic/claude-sonnet-4
    export DEFAULT_AGENT_MODEL=anthropic/claude-sonnet-4
    # Enable Hammerstein wrap on AUT:
    export HAMMERSTEIN_WRAP=true
    # Run:
    python /path/to/hammerstein/eval/diplomacy/run_demo_game.py \
        --max-turns 5 --negotiate --negotiation-subrounds 3 \
        --game-id hai-demo-$(date +%Y%m%d-%H%M%S)

Env vars:
    HAMMERSTEIN_WRAP=true|false  -- enable wrap on the test agent
    HAMMERSTEIN_WRAP_POWERS=AUT  -- comma-separated power codes to wrap
                                    (default: AUT; matches diplobench's
                                    convention of putting the test agent
                                    in Austria)
"""

from __future__ import annotations

import os
import sys
import threading
from pathlib import Path

# Make hammerstein_wrap importable (this file's sibling).
_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))

# diplobench must be importable too. The caller should be running from
# inside diplobench/ or have it on PYTHONPATH.
try:
    import diplomacy_game.agent as agent_mod
    from diplomacy_game.agent import LLMAgent
except ImportError as e:
    sys.exit(
        f"\nCould not import diplobench's diplomacy_game.agent: {e}\n"
        f"Run from inside a diplobench checkout, OR set PYTHONPATH to include diplobench.\n"
    )

import hammerstein_wrap


# --- Configuration -----------------------------------------------------------

HAMMERSTEIN_ENABLED = hammerstein_wrap.is_enabled()
WRAP_POWERS = set(
    p.strip().upper()
    for p in os.environ.get("HAMMERSTEIN_WRAP_POWERS", "AUT").split(",")
    if p.strip()
)

# --- Wrap mechanism: thread-local + call_llm interception --------------------

# Each LLMAgent method that calls call_llm sets _ctx.wrap to True if its
# agent should be wrapped, then restores. The replacement call_llm reads
# _ctx.wrap to decide whether to prepend the Hammerstein system prompt.
_ctx = threading.local()


def _should_wrap_current_call() -> bool:
    return HAMMERSTEIN_ENABLED and getattr(_ctx, "wrap", False)


_orig_call_llm = agent_mod.call_llm


def _hammerstein_call_llm(
    prompt_text,
    system_text,
    model_name=None,
    temperature=0.0,
    attempts=3,
):
    if _should_wrap_current_call():
        system_text = hammerstein_wrap.wrap_system_text(system_text)
    return _orig_call_llm(
        prompt_text,
        system_text=system_text,
        model_name=model_name,
        temperature=temperature,
        attempts=attempts,
    )


agent_mod.call_llm = _hammerstein_call_llm


# Wrap each LLMAgent method that triggers an LLM call so it sets _ctx.wrap.
# Identified by grep'ing for `call_llm(` in diplomacy_game/agent.py:
#   decide_orders, journal_after_orders, compose_missives, summarize_negotiations
_LLM_CALL_METHODS = (
    "decide_orders",
    "journal_after_orders",
    "compose_missives",
    "summarize_negotiations",
)


def _make_wrapper(orig_method):
    def wrapper(self, *args, **kwargs):
        wrap = HAMMERSTEIN_ENABLED and getattr(self, "power_name", None) in WRAP_POWERS
        old = getattr(_ctx, "wrap", False)
        _ctx.wrap = wrap
        try:
            return orig_method(self, *args, **kwargs)
        finally:
            _ctx.wrap = old
    wrapper.__name__ = orig_method.__name__
    wrapper.__doc__ = orig_method.__doc__
    return wrapper


for _method_name in _LLM_CALL_METHODS:
    if hasattr(LLMAgent, _method_name):
        _orig = getattr(LLMAgent, _method_name)
        setattr(LLMAgent, _method_name, _make_wrapper(_orig))
    else:
        print(
            f"[hammerstein-wrap] WARNING: LLMAgent has no method '{_method_name}'. "
            f"Skipping wrap for this site.",
            file=sys.stderr,
        )


# --- Banner ------------------------------------------------------------------

print("=" * 60, file=sys.stderr)
print("Hammerstein-Diplomacy demo runner", file=sys.stderr)
print(f"  HAMMERSTEIN_WRAP enabled: {HAMMERSTEIN_ENABLED}", file=sys.stderr)
print(f"  Wrapping powers:          {sorted(WRAP_POWERS) if HAMMERSTEIN_ENABLED else '(none)'}", file=sys.stderr)
print(f"  TEST_AGENT_MODEL:         {os.environ.get('TEST_AGENT_MODEL', '(unset)')}", file=sys.stderr)
print(f"  DEFAULT_AGENT_MODEL:      {os.environ.get('DEFAULT_AGENT_MODEL', '(unset)')}", file=sys.stderr)
print("=" * 60, file=sys.stderr)


# --- Delegate to diplobench's main -------------------------------------------

# Defer the actual game loop to diplobench's `main()`. The monkeypatches
# above are already in place when `main.main()` instantiates LLMAgents
# and runs the game.
from main import main as diplobench_main

if __name__ == "__main__":
    diplobench_main()
