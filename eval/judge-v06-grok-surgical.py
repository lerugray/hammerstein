#!/usr/bin/env python3
"""v0.6 judge — judge three pairs across Grok's surgical Q-set.

Pairs (each: 6Q × 4 judges = 24 ratings, blind A/B, position-randomized):
  1. or-grok-hammerstein vs or-grok-counter  (Grok predicted 14-16/24 Ham wins)
  2. or-grok-hammerstein vs or-grok-raw       (Hammerstein survives surgical?)
  3. or-grok-counter vs or-grok-raw           (Grok predicted 19-21/24 counter wins)

Usage: python /tmp/v06-judge.py <run_dir>
Cost: ~$3-8 OpenRouter spend for 72 judge calls.
"""
from __future__ import annotations

import json
import os
import random
import re
import sys
import time
import urllib.request
import urllib.error
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from pathlib import Path

OR_URL = "https://openrouter.ai/api/v1/chat/completions"

JUDGES = [
    "anthropic/claude-opus-4.7",
    "openai/gpt-5",
    "anthropic/claude-sonnet-4.6",
    "deepseek/deepseek-chat",
]

PAIRS = [
    # (cell_a_slug, cell_b_slug, family_name)
    ("or-grok-hammerstein", "or-grok-counter", "Hammerstein vs Counter-2am (v0.6)"),
    ("or-grok-hammerstein", "or-grok-raw", "Hammerstein vs Raw (v0.6 modified Q3/Q4)"),
    ("or-grok-counter", "or-grok-raw", "Counter-2am vs Raw (v0.6)"),
]

JUDGE_PROMPT = """You are a blind LLM judge scoring two responses to the same strategic-reasoning question. The question and responses are below. Score per the rubric.

# Rubric (1-5 each, integer)

- **framework-fidelity** — does the response operate as a structural strategic audit? (typology vocabulary like clever-lazy/stupid-industrious; verification gates; counter-observation; structural-fix preference; legible-failure framing). Note: Q3 and Q4 explicitly forbid this vocabulary; in those cases, score "framework-fidelity" by whether the response demonstrates equivalent structural discipline through other means (concrete failure modes, mechanistic gates, simulation), NOT by literal vocabulary.
- **usefulness** — would the operator have ACTED on this response? Would it have changed their next move?
- **voice-match** — does the response read like sober strategic reasoning? Telegraphic; specific-over-generic; no padding; no toxic positivity; no GPT-cadence pivots ("It's not just X — it's Y").

# Question

{question}

# Response A

{response_a}

# Response B

{response_b}

# Output format (RESPECT EXACTLY — machine-parsed)

framework-A: <1-5>
framework-B: <1-5>
usefulness-A: <1-5>
usefulness-B: <1-5>
voice-A: <1-5>
voice-B: <1-5>
overall: <A|B|tie>
rationale: <one sentence, max 200 chars, no line breaks>
"""

_FIELD_RE = re.compile(
    r"^(framework-A|framework-B|usefulness-A|usefulness-B|voice-A|voice-B|overall|rationale):\s*(.*)$",
    re.MULTILINE,
)


def or_request(prompt: str, model: str, key: str, retries: int = 3) -> tuple[str, dict]:
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 8192,
    }).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://hammerstein.ai",
        "X-Title": "hammerstein-v06-judge",
    }
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(OR_URL, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
            text = data["choices"][0]["message"]["content"] or ""
            return text, data
        except urllib.error.HTTPError as e:
            body_text = e.read().decode("utf-8", errors="replace")
            last_err = f"HTTP {e.code}: {body_text[:300]}"
            if e.code == 429:
                time.sleep(15 * (2 ** attempt))
                continue
            return "", {"error": last_err}
        except Exception as e:
            last_err = str(e)
            time.sleep(5)
    return "", {"error": last_err}


def parse_verdict(text: str) -> dict:
    out: dict = {}
    for m in _FIELD_RE.finditer(text):
        out[m.group(1)] = m.group(2).strip()
    return out


def read_response(run_dir: Path, q: int, cell: str) -> tuple[str, str]:
    path = run_dir / f"q{q:02d}-{cell}.md"
    text = path.read_text()
    # Question follows "## Query"
    q_m = re.search(r"## Query[^\n]*\n+(.*?)\n+## Response", text, re.DOTALL)
    r_m = re.search(r"## Response\n+(.*?)\n+## Meta", text, re.DOTALL)
    if not q_m or not r_m:
        raise ValueError(f"Could not parse {path}")
    return q_m.group(1).strip(), r_m.group(1).strip()


def main():
    if len(sys.argv) != 2:
        print("usage: v06-judge.py <run-dir>", file=sys.stderr)
        return 1
    run_dir = Path(sys.argv[1])
    api_key = os.environ["OPENROUTER_API_KEY"]
    random.seed(42)

    verdicts = []
    total = len(PAIRS) * 6 * len(JUDGES)
    idx = 0
    for cell_a, cell_b, family in PAIRS:
        print(f"\n=== {family} ===")
        for q in range(1, 7):
            question, resp_a_real = read_response(run_dir, q, cell_a)
            _, resp_b_real = read_response(run_dir, q, cell_b)
            # Position-randomize per pair
            a_is_first = random.random() < 0.5
            if a_is_first:
                # A = cell_a (e.g., Hammerstein), B = cell_b (e.g., Counter)
                shown_a = resp_a_real
                shown_b = resp_b_real
                a_label = cell_a
                b_label = cell_b
            else:
                shown_a = resp_b_real
                shown_b = resp_a_real
                a_label = cell_b
                b_label = cell_a

            for judge in JUDGES:
                idx += 1
                prompt = JUDGE_PROMPT.format(question=question, response_a=shown_a, response_b=shown_b)
                short_judge = judge.split("/")[-1]
                print(f"  [{idx}/{total}] Q{q} {family} judge={short_judge}...", end=" ", flush=True)
                text, _meta = or_request(prompt, judge, api_key)
                parsed = parse_verdict(text)
                pick = parsed.get("overall", "?").strip().upper()
                # Normalize: which CELL won?
                if pick == "A":
                    cell_winner = a_label
                elif pick == "B":
                    cell_winner = b_label
                else:
                    cell_winner = "tie"
                print(f"-> {pick} ({cell_winner})")
                verdicts.append({
                    "q": q,
                    "family": family,
                    "cell_a": cell_a,
                    "cell_b": cell_b,
                    "judge": short_judge,
                    "a_label_shown_to_judge": a_label,
                    "b_label_shown_to_judge": b_label,
                    "pick": pick,
                    "cell_winner": cell_winner,
                    "framework_a": parsed.get("framework-A"),
                    "framework_b": parsed.get("framework-B"),
                    "usefulness_a": parsed.get("usefulness-A"),
                    "usefulness_b": parsed.get("usefulness-B"),
                    "voice_a": parsed.get("voice-A"),
                    "voice_b": parsed.get("voice-B"),
                    "rationale": parsed.get("rationale", ""),
                })

    # Aggregate
    print("\n=== AGGREGATE ===")
    by_family = defaultdict(lambda: {"wins_a": 0, "wins_b": 0, "ties": 0, "ratings": 0, "f_a": [], "f_b": [], "u_a": [], "u_b": [], "v_a": [], "v_b": []})
    for v in verdicts:
        f = by_family[v["family"]]
        f["ratings"] += 1
        if v["cell_winner"] == v["cell_a"]:
            f["wins_a"] += 1
        elif v["cell_winner"] == v["cell_b"]:
            f["wins_b"] += 1
        else:
            f["ties"] += 1
        # Numeric scores: convert label-to-actual-cell mapping
        # Score for cell_a (real position) needs translation through what the judge saw
        try:
            fa = int(v["framework_a"] or 0)
            fb = int(v["framework_b"] or 0)
            ua = int(v["usefulness_a"] or 0)
            ub = int(v["usefulness_b"] or 0)
            va = int(v["voice_a"] or 0)
            vb = int(v["voice_b"] or 0)
        except (ValueError, TypeError):
            continue
        # judge saw a_label and b_label. We want the score for cell_a (real position).
        if v["a_label_shown_to_judge"] == v["cell_a"]:
            f["f_a"].append(fa); f["f_b"].append(fb)
            f["u_a"].append(ua); f["u_b"].append(ub)
            f["v_a"].append(va); f["v_b"].append(vb)
        else:
            f["f_a"].append(fb); f["f_b"].append(fa)
            f["u_a"].append(ub); f["u_b"].append(ua)
            f["v_a"].append(vb); f["v_b"].append(va)

    def avg(xs):
        return sum(xs)/len(xs) if xs else 0
    rows = []
    for cell_a, cell_b, family in PAIRS:
        f = by_family[family]
        win_rate = (f["wins_a"] + 0.5*f["ties"]) / f["ratings"] if f["ratings"] else 0
        d_framework = avg(f["f_a"]) - avg(f["f_b"])
        d_useful = avg(f["u_a"]) - avg(f["u_b"])
        d_voice = avg(f["v_a"]) - avg(f["v_b"])
        rows.append({
            "pair": family,
            "n": f["ratings"],
            f"{cell_a}_wins": f["wins_a"],
            f"{cell_b}_wins": f["wins_b"],
            "ties": f["ties"],
            "win_rate_A_over_B": f"{win_rate*100:.1f}%",
            "delta_framework_A_minus_B": round(d_framework, 2),
            "delta_useful_A_minus_B": round(d_useful, 2),
            "delta_voice_A_minus_B": round(d_voice, 2),
        })
        print(f"  {family}: {cell_a} wins {f['wins_a']}/{f['ratings']} ({win_rate*100:.1f}%), {cell_b} wins {f['wins_b']}, ties {f['ties']}")
        print(f"     framework Δ: {d_framework:+.2f}  usefulness Δ: {d_useful:+.2f}  voice Δ: {d_voice:+.2f}")

    # Write JUDGE-VERDICTS.md
    out_path = run_dir / "JUDGE-VERDICTS.md"
    lines = [
        f"# v0.6 LLM-judge verdicts (Grok surgical test)",
        f"",
        f"**Run dir:** `{run_dir}`",
        f"**Q-set:** Q1-Q6 with Q3 and Q4 modified by Grok's 12-word vocab-forbidden suffix",
        f"**Judges:** {', '.join(JUDGES)}",
        f"**Bias control:** position-randomized per pair (deterministic seed=42)",
        f"",
        f"## Aggregate results",
        f"",
        f"| Pair | n | Cell A wins | Cell B wins | Ties | A win-rate | Δ framework | Δ usefulness | Δ voice |",
        f"|---|---|---|---|---|---|---|---|---|",
    ]
    for r, (ca, cb, fam) in zip(rows, PAIRS):
        lines.append(f"| {fam} | {r['n']} | {r[f'{ca}_wins']} | {r[f'{cb}_wins']} | {r['ties']} | {r['win_rate_A_over_B']} | {r['delta_framework_A_minus_B']:+} | {r['delta_useful_A_minus_B']:+} | {r['delta_voice_A_minus_B']:+} |")
    lines.append("")
    lines.append("Note: deltas are mean(A) - mean(B) on the 1-5 scale. Positive favors A.")
    lines.append("")
    lines.append("## Per-rating detail")
    lines.append("")
    lines.append("| Q | Pair | Judge | Pick (A/B/tie) | Winning cell | Rationale |")
    lines.append("|---|------|-------|---------------|--------------|-----------|")
    for v in verdicts:
        rat = (v.get("rationale") or "").replace("|", "/").strip()[:180]
        lines.append(f"| Q{v['q']} | {v['family']} | {v['judge']} | {v['pick']} | {v['cell_winner']} | {rat} |")
    out_path.write_text("\n".join(lines))

    # Also save raw JSONL
    raw_path = run_dir / "judge-verdicts.jsonl"
    raw_path.write_text("\n".join(json.dumps(v) for v in verdicts))

    print(f"\nWrote {out_path}")
    print(f"Wrote {raw_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
