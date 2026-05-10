"""Zero-cost smoke test for the Hammerstein-Diplomacy wrap.

Loads the Hammerstein system prompt and confirms wrap_system_text(...)
produces a coherent combined system_text. Prints both wrapped and raw
system_texts side by side for visual inspection. Does NOT make any LLM
API calls.

Run:
    python run_smoke_test.py

Pass criteria:
- Hammerstein prompt loads cleanly from ../../prompts/SYSTEM-PROMPT.md
- Wrap produces text containing both the Hammerstein content AND the
  original Diplomacy operator instructions
- Combined length is reasonable for Sonnet 4.6 context (target <10K tokens)
"""

from __future__ import annotations

import sys

import hammerstein_wrap


# A representative diplobench-style system_text. Lifted directly from
# diplomacy_game/agent.py:decide_orders() for the MOVE phase.
SAMPLE_DIPLOBENCH_SYSTEM_TEXT = (
    "You are an AI playing Diplomacy. Play faithfully to your personality. "
    "Always try to move the game forward and avoid stalemate per your "
    "objectives. Use only 3-letter power codes (AUT, ENG, FRA, GER, ITA, "
    "RUS, TUR). Output valid JSON with exactly two fields in this order: "
    "'reasoning' (list of strings) and 'orders' (list of strings)."
)


def estimate_tokens(text: str) -> int:
    """Rough token estimate: 1 token ≈ 4 chars for English prose."""
    return len(text) // 4


def main() -> int:
    print("=" * 60)
    print("Hammerstein-Diplomacy smoke test")
    print("=" * 60)

    try:
        hp = hammerstein_wrap.load_hammerstein_system_prompt()
    except FileNotFoundError as e:
        print(f"FAIL: could not load Hammerstein system prompt: {e}")
        return 1

    print(f"\n[1/4] Hammerstein system prompt loaded.")
    print(f"      Length: {len(hp)} chars (~{estimate_tokens(hp)} tokens)")
    if len(hp) < 5000:
        print(f"FAIL: Hammerstein prompt suspiciously short ({len(hp)} chars). "
              f"Expected ~14K chars / ~3,500 tokens.")
        return 1

    print(f"\n[2/4] Sample diplobench system_text:")
    print(f"      Length: {len(SAMPLE_DIPLOBENCH_SYSTEM_TEXT)} chars "
          f"(~{estimate_tokens(SAMPLE_DIPLOBENCH_SYSTEM_TEXT)} tokens)")
    print(f"      Content: {SAMPLE_DIPLOBENCH_SYSTEM_TEXT[:80]}...")

    wrapped = hammerstein_wrap.wrap_system_text(SAMPLE_DIPLOBENCH_SYSTEM_TEXT)
    print(f"\n[3/4] Wrapped system_text:")
    print(f"      Length: {len(wrapped)} chars (~{estimate_tokens(wrapped)} tokens)")
    print(f"      First 200 chars: {wrapped[:200]}")
    print(f"      ...")
    print(f"      Last 200 chars: {wrapped[-200:]}")

    # Verify content integrity.
    if SAMPLE_DIPLOBENCH_SYSTEM_TEXT not in wrapped:
        print("FAIL: wrapped text does not contain the original diplobench instructions.")
        return 1
    if "clever-lazy" not in wrapped and "Hammerstein" not in wrapped:
        print("FAIL: wrapped text does not appear to contain Hammerstein framework content.")
        return 1

    expected_tokens = estimate_tokens(wrapped)
    if expected_tokens > 10_000:
        print(f"WARN: wrapped system_text is large (~{expected_tokens} tokens). "
              f"Sonnet 4.6 handles 200K but per-call cost will be elevated.")

    print(f"\n[4/4] All checks passed.")
    print(f"\nReady to wire run_demo_game.py against a cloned diplobench harness.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
