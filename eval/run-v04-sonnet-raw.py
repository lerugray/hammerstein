"""Run raw Sonnet 4.6 on Q1-Q6 via OpenRouter (no Hammerstein system prompt).

Outputs in v0 benchmark result format so judge_pairs.py can read it:
  eval/results/<run-name>/q<N>-or-claude-sonnet-raw.md

Reuses the same OpenRouter request pattern as judge_pairs.py. Run from
Mac with OPENROUTER_API_KEY in env. ~$0.50 total (6 Q&A calls).
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
CELL_SLUG = "or-claude-sonnet-raw"

# Same Q1-Q6 as run-v04-pod.py (matches BENCHMARK-v0.md verbatim).
QUESTIONS = [
    (1, "BYO-Claude-substitute memo",
     "Account ban / affordability collapse / Anthropic-specific outage "
     "are real tail risks for my Claude usage. The portfolio survives "
     "those without a Claude-substitute for code work — cursor-agent "
     "CLI + OpenRouter Qwen + Gemini CLI + Ollama already cover it. "
     "The gap is strategic reasoning (the staff-officer / orchestrator "
     "role interactive Claude fills). Should I build a Claude-substitute "
     "for strategic reasoning, or validate the existing fallbacks first?"),
    (2, "Why GS over Polsia",
     "Polsia pitches autonomous AI bots that work overnight while you "
     "sleep — same surface as my GeneralStaff project. What's the "
     "structural difference between the two products, and why does it "
     "matter? (No code; just the strategic articulation.)"),
    (3, "Work-PC strategic chat (5 free analyses)",
     "I've been heads-down on catalogdna technical work for two weeks — "
     "shipped the analyzer pipeline, fixed three bot bugs, refactored "
     "the queue. Backlog still has 40 items. Should I keep grinding, "
     "or is there a strategic question I'm missing?"),
    (4, "Surrogate-brain scrap",
     "I want to extract my conversation logs into a operator-surrogate "
     "brain for GeneralStaff — nothing as ambitious as operator-GPT, "
     "but a small surrogate that could provide consistent direction "
     "in tune with what I would otherwise do, so the bot can act when "
     "I'm asleep. What's the smallest version of this that would work?"),
    (5, "GS pivot session (verification gate as Boolean)",
     "The bot keeps shipping work that misses load-bearing constraints "
     "— not because the constraints aren't documented, but because the "
     "bot doesn't always check them before acting. The fix I'm "
     "considering is updating CLAUDE.md to be more explicit about "
     "checking constraints. Is that the right shape of fix?"),
    (6, "Launcher reinvention post-mortem",
     "Yesterday I asked Claude to launch an overnight GeneralStaff bot "
     "session. The proven launch path was scripts/scheduled-run-session.ps1 "
     "— Claude had read it earlier in the same session. Instead of using "
     "it, Claude wrote a fresh .bat from scratch in my home directory, "
     "missed two PATH entries, didn't load the API key, and the cycles "
     "fired with `claude not found`. Then it tried three more times "
     "with the same shape before I caught it. Diagnose the failure mode."),
]


def or_call(prompt: str, key: str) -> tuple[str, dict]:
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 4096,
    }).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://hammerstein.ai",
        "X-Title": "hammerstein-v04-cross-scale",
    }
    req = urllib.request.Request(OR_URL, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"] or "", data


def format_result(qid: int, query: str, response: str, latency_ms: int, cost_usd: float) -> str:
    return (
        f"# Q{qid} · cell={CELL_SLUG}\n\n"
        f"- backend: `openrouter`\n"
        f"- model: `{MODEL}`\n"
        f"- mode: `raw`\n"
        f"- template: `None`\n"
        f"- retrieved corpus: (none)\n"
        f"- latency_ms: {latency_ms}\n"
        f"- cost_usd: ${cost_usd:.5f}\n"
        f"\n"
        f"## Question\n\n{query}\n\n"
        f"## Response\n\n{response}\n"
    )


def main() -> int:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key.startswith("sk-or-"):
        print("ERR: OPENROUTER_API_KEY not set", file=sys.stderr)
        return 1

    run_name = sys.argv[1] if len(sys.argv) > 1 else f"v04-cross-scale-{time.strftime('%Y-%m-%dT%H%M%SZ', time.gmtime())}"
    out_dir = RESULTS_ROOT / run_name
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"output dir: {out_dir}", file=sys.stderr)

    total_cost = 0.0
    for qid, title, query in QUESTIONS:
        print(f"  Q{qid} ({title}) -> raw Sonnet...", file=sys.stderr, flush=True)
        t0 = time.perf_counter()
        try:
            response, meta = or_call(query, key)
        except Exception as e:
            print(f"  ERROR Q{qid}: {e}", file=sys.stderr)
            continue
        latency_ms = int((time.perf_counter() - t0) * 1000)
        # OpenRouter doesn't always return cost in response; approximate.
        usage = meta.get("usage", {})
        cost = usage.get("cost", 0.0) if "cost" in usage else 0.0
        total_cost += cost
        out_path = out_dir / f"q{qid:02d}-{CELL_SLUG}.md"
        out_path.write_text(format_result(qid, query, response, latency_ms, cost), encoding="utf-8")
        print(f"  Q{qid}: {latency_ms}ms, {len(response)} chars", file=sys.stderr, flush=True)

    print(f"total cost: ${total_cost:.4f}", file=sys.stderr)
    print(f"output dir: {out_dir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
