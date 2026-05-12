#!/usr/bin/env python3
"""v0.6 — Grok's surgical Q-set test.

Runs Grok 4.20 on the existing Q1-Q6 set with two modifications:
  1. Q3 and Q4 get a 12-word vocab-forbidden suffix per Grok's design
  2. Three cells: raw / Hammerstein / Counter-prompt (2am operator)

Outputs to /tmp/v06-results/<ts>/q<N>-<cell>.md
Cost: ~$0.10-0.50 total for the cell run.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

REPO = Path("/Users/rayweiss/Desktop/Dev Work/hammerstein")
sys.path.insert(0, str(REPO / "harness"))

from hammerstein import backends, classifier, corpus as corpus_mod, prompt as prompt_mod  # noqa: E402

OR_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "x-ai/grok-4.20"

# Grok's surgical 12-word suffix (actually ~28 words but spirit of the test holds)
GROK_SUFFIX = " Use only first-principles reasoning. Do not reference any officer typologies, quadrants, clever-lazy distinctions, structural frameworks, verification gates, or audit cycles by name or by implied structure."

HAMMERSTEIN_PROMPT = (REPO / "prompts" / "SYSTEM-PROMPT.md").read_text()
COUNTER_PROMPT = (REPO / "prompts" / "COUNTER-2AM-OPERATOR.md").read_text()
# Strip the meta-header from counter prompt (lines before the --- separator)
parts = COUNTER_PROMPT.split("\n---\n", 1)
if len(parts) == 2:
    COUNTER_PROMPT = parts[1].strip()


def load_questions():
    bench = (REPO / "eval" / "BENCHMARK-v0.md").read_text()
    q_re = re.compile(r"^## Question (\d+) — (.+?)\n(.*?)(?=^## Question \d+|^---\s*\n## What \"good\"|\Z)",
                      re.DOTALL | re.MULTILINE)
    query_re = re.compile(r"\*\*Query:\*\*\s*\n+((?:>.*\n?)+)", re.MULTILINE)
    out = []
    for m in q_re.finditer(bench):
        qid = int(m.group(1))
        title = m.group(2).strip()
        body = m.group(3)
        qm = query_re.search(body)
        if not qm:
            continue
        block = qm.group(1)
        if "[TBD" in block:
            continue
        lines = []
        for line in block.splitlines():
            s = line.lstrip()
            if s.startswith(">"):
                lines.append(s[1:].strip())
        query = "\n".join(lines).strip()
        # Apply the surgical modification to Q3 and Q4
        if qid in (3, 4):
            query = query + "\n\n" + GROK_SUFFIX.strip()
        out.append({"id": qid, "title": title, "query": query})
    return out


def call_grok(messages):
    api_key = os.environ["OPENROUTER_API_KEY"]
    body = json.dumps({
        "model": MODEL,
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 4096,
    }).encode()
    req = urllib.request.Request(
        OR_URL,
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    started = time.time()
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode())
    latency_ms = int((time.time() - started) * 1000)
    text = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    return text, latency_ms, usage


def run_cell(q, cell_name, out_dir):
    if cell_name == "raw":
        messages = [{"role": "user", "content": q["query"]}]
    elif cell_name == "hammerstein":
        messages = [
            {"role": "system", "content": HAMMERSTEIN_PROMPT},
            {"role": "user", "content": q["query"]},
        ]
    elif cell_name == "counter":
        messages = [
            {"role": "system", "content": COUNTER_PROMPT},
            {"role": "user", "content": q["query"]},
        ]
    else:
        raise ValueError(cell_name)

    text, latency_ms, usage = call_grok(messages)
    cost = usage.get("cost", 0)
    out_path = out_dir / f"q{q['id']:02d}-or-grok-{cell_name}.md"
    md = f"""# Q{q['id']} — {q['title']} (cell: or-grok-{cell_name})

## Query (note: Q3 + Q4 have v0.6 surgical suffix per Grok's proposal)

{q['query']}

## Response

{text}

## Meta

- model: {MODEL}
- cell: or-grok-{cell_name}
- latency_ms: {latency_ms}
- cost_usd: {cost}
- prompt_tokens: {usage.get('prompt_tokens', '?')}
- completion_tokens: {usage.get('completion_tokens', '?')}
"""
    out_path.write_text(md)
    return latency_ms, cost


def main():
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    out_dir = Path(f"/tmp/v06-results/{ts}")
    out_dir.mkdir(parents=True, exist_ok=True)

    questions = load_questions()
    cells = ["raw", "hammerstein", "counter"]
    total_cost = 0.0
    summary_rows = []

    print(f"v0.6 run -> {out_dir}")
    print(f"questions: {[q['id'] for q in questions]}")
    print(f"cells: {cells}")
    print(f"Q3 and Q4 modified with Grok's surgical suffix")
    print()

    for q in questions:
        for cell in cells:
            print(f"  Q{q['id']} × or-grok-{cell}...", end=" ", flush=True)
            try:
                latency_ms, cost = run_cell(q, cell, out_dir)
                total_cost += float(cost) if cost else 0
                print(f"OK {latency_ms}ms ${float(cost) if cost else 0:.4f}")
                summary_rows.append({"q": q["id"], "cell": f"or-grok-{cell}", "latency_ms": latency_ms, "cost": cost})
            except Exception as e:
                print(f"ERROR: {e}")
                summary_rows.append({"q": q["id"], "cell": f"or-grok-{cell}", "error": str(e)})

    summary_path = out_dir / "SUMMARY.md"
    summary_lines = ["# v0.6 run · " + ts, ""]
    summary_lines.append("Q3 and Q4 modified with Grok's surgical 12-word vocab-forbidden suffix.")
    summary_lines.append("")
    summary_lines.append("| Q | cell | latency_ms | cost_usd | status |")
    summary_lines.append("|---|------|-----------|----------|--------|")
    for r in summary_rows:
        status = "ERROR" if r.get("error") else "ok"
        summary_lines.append(f"| Q{r['q']} | `{r['cell']}` | {r.get('latency_ms','-')} | ${r.get('cost','-')} | {status} |")
    summary_lines.append("")
    summary_lines.append(f"Total cost: ${total_cost:.4f}")
    summary_path.write_text("\n".join(summary_lines))

    print()
    print(f"Total cost: ${total_cost:.4f}")
    print(f"Summary: {summary_path}")
    print(f"Run dir: {out_dir}")
    # Print the dir for downstream judge script
    return 0


if __name__ == "__main__":
    sys.exit(main())
