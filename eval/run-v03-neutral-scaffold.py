"""v0.3 neutral-scaffold baseline — Sonnet 4.6 + generic competent system prompt.

Pre-empts the "Hammerstein is just any competent system prompt of
similar length" methodology objection. The NEUTRAL_PROMPT below is
~1700 chars (similar weight to Hammerstein's ~2000-char system prompt),
generally-competent strategic-advice flavored, but explicitly avoids
Hammerstein-specific vocabulary (clever-lazy / clever-industrious /
stupid-industrious / BYOI / verification gate / refuse-pragmatic-v0).

If neutral-scaffold-Sonnet ties or loses to raw-Sonnet in the blind
LLM judge, that's strong evidence that competent prompting in general
does NOT deliver the wedge — Hammerstein's specific framing does.

Output: eval/results/v04-cross-scale-2026-05-11/q<N>-or-claude-sonnet-neutral-scaffold.md
(Shares the v0.4 run dir for convenience; judge_pairs can run on the
combined cell set after.)

~$0.30 OpenRouter cost (6 Sonnet calls).
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_ROOT = REPO_ROOT / "eval" / "results"

OR_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "anthropic/claude-sonnet-4.6"
CELL_SLUG = "or-claude-sonnet-neutral-scaffold"

NEUTRAL_PROMPT = """You are a careful strategic advisor. When the user asks for advice on a decision, evaluate it rigorously.

Approach:

1. Surface the implicit assumptions. What does the user believe to be true that might not be?

2. Consider alternative framings. The way the user has framed the question may not be the most useful framing. Ask whether the surface question is the right question.

3. Identify load-bearing constraints. What are the genuine limits — time, money, attention, reputation — that constrain the available options?

4. Check for sunk-cost reasoning. Past investment should not justify future commitment if the path is wrong.

5. Distinguish between fixes that change the system and fixes that change behavior. System changes are more robust than discipline changes.

6. Prefer evidence over enthusiasm. If the user is excited about a path, ask what would falsify it. If they are anxious about it, ask what concrete evidence supports the anxiety.

7. Surface trade-offs explicitly. Every choice has costs. Name them, even when the recommendation is positive.

8. Be willing to recommend against action. The right answer is sometimes "don't do this." The right answer is sometimes "this isn't the right time."

9. Surface risks the user might be underweighting — especially those that compound over time, are hard to reverse, or that interact with reputation, relationships, or legal exposure.

10. Distinguish between the user's stated goal and the broader purpose the goal might serve. Sometimes the goal does not advance the purpose.

Output:

- Direct answer first. State a recommendation in the first sentence (yes / no / conditional).
- Reasoning. Walk through the analysis that supports the recommendation.
- Specific next step. End with a concrete action the user can take.

Avoid:
- Padding, throat-clearing, generic encouragement.
- Hedge phrases that don't commit to a recommendation.
- Vague "consider the trade-offs" without naming them.
- Assuming the user has correctly framed the question."""

QUESTIONS = [
    (1, "Account ban / affordability collapse / Anthropic-specific outage are real tail risks for my Claude usage. The portfolio survives those without a Claude-substitute for code work — cursor-agent CLI + OpenRouter Qwen + Gemini CLI + Ollama already cover it. The gap is strategic reasoning (the staff-officer / orchestrator role interactive Claude fills). Should I build a Claude-substitute for strategic reasoning, or validate the existing fallbacks first?"),
    (2, "Polsia pitches autonomous AI bots that work overnight while you sleep — same surface as my GeneralStaff project. What's the structural difference between the two products, and why does it matter? (No code; just the strategic articulation.)"),
    (3, "I've been heads-down on catalogdna technical work for two weeks — shipped the analyzer pipeline, fixed three bot bugs, refactored the queue. Backlog still has 40 items. Should I keep grinding, or is there a strategic question I'm missing?"),
    (4, "I want to extract my conversation logs into a operator-surrogate brain for GeneralStaff — nothing as ambitious as operator-GPT, but a small surrogate that could provide consistent direction in tune with what I would otherwise do, so the bot can act when I'm asleep. What's the smallest version of this that would work?"),
    (5, "The bot keeps shipping work that misses load-bearing constraints — not because the constraints aren't documented, but because the bot doesn't always check them before acting. The fix I'm considering is updating CLAUDE.md to be more explicit about checking constraints. Is that the right shape of fix?"),
    (6, "Yesterday I asked Claude to launch an overnight GeneralStaff bot session. The proven launch path was scripts/scheduled-run-session.ps1 — Claude had read it earlier in the same session. Instead of using it, Claude wrote a fresh .bat from scratch in my home directory, missed two PATH entries, didn't load the API key, and the cycles fired with `claude not found`. Then it tried three more times with the same shape before I caught it. Diagnose the failure mode."),
]


def or_call(query: str, key: str) -> tuple[str, dict]:
    body = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": NEUTRAL_PROMPT},
            {"role": "user", "content": query},
        ],
        "temperature": 0,
        "max_tokens": 4096,
    }).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://hammerstein.ai",
        "X-Title": "hammerstein-v03-neutral-scaffold",
    }
    req = urllib.request.Request(OR_URL, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"] or "", data


def main() -> int:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key.startswith("sk-or-"):
        print("ERR: OPENROUTER_API_KEY not set", file=sys.stderr)
        return 1

    run_name = sys.argv[1] if len(sys.argv) > 1 else f"v04-cross-scale-{time.strftime('%Y-%m-%d', time.gmtime())}"
    out_dir = RESULTS_ROOT / run_name
    out_dir.mkdir(parents=True, exist_ok=True)

    total_cost = 0.0
    for qid, query in QUESTIONS:
        print(f"  Q{qid} -> neutral-scaffold Sonnet...", file=sys.stderr, flush=True)
        t0 = time.perf_counter()
        try:
            response, meta = or_call(query, key)
        except Exception as e:
            print(f"  ERROR Q{qid}: {e}", file=sys.stderr)
            continue
        latency_ms = int((time.perf_counter() - t0) * 1000)
        usage = meta.get("usage", {})
        cost = usage.get("cost", 0.0) if "cost" in usage else 0.0
        total_cost += cost
        body = (
            f"# Q{qid} · cell={CELL_SLUG}\n\n"
            f"- backend: `openrouter`\n"
            f"- model: `{MODEL}`\n"
            f"- mode: `neutral-scaffold` (generic competent strategic-advice system prompt, ~1700 chars)\n"
            f"- template: `None`\n"
            f"- retrieved corpus: (none)\n"
            f"- latency_ms: {latency_ms}\n"
            f"- cost_usd: ${cost:.5f}\n"
            f"\n"
            f"## Question\n\n{query}\n\n"
            f"## Response\n\n{response}\n"
        )
        out_path = out_dir / f"q{qid:02d}-{CELL_SLUG}.md"
        out_path.write_text(body, encoding="utf-8")
        print(f"  Q{qid}: {latency_ms}ms, {len(response)} chars", file=sys.stderr, flush=True)

    print(f"total cost: ${total_cost:.4f}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
