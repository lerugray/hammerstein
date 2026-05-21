#!/usr/bin/env python3
"""Format v0.7 pod results JSON into per-(q, cell) markdown files.

Usage:
    python eval/format-v07-pod-results.py <results.json> <run-name>

Creates:
    eval/results/<run-name>/q<N>-rp-7b-raw.md
    eval/results/<run-name>/q<N>-rp-7b-ham.md

Same format as run-v07-ood.py output, compatible with judge_pairs.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: format-v07-pod-results.py <results.json> <run-name>", file=sys.stderr)
        return 1

    json_path = Path(sys.argv[1])
    run_name = sys.argv[2]
    out_dir = REPO_ROOT / "eval" / "results" / run_name
    out_dir.mkdir(parents=True, exist_ok=True)

    results = json.loads(json_path.read_text(encoding="utf-8"))
    n = 0
    for row in results:
        qid = row["qid"]
        cell = row["cell"]
        domain = row.get("domain", "")
        question = row.get("question", "")
        response = row.get("response", "")
        latency_ms = row.get("latency_ms", 0)

        lines = [
            f"# Q{qid} · cell={cell}",
            "",
            f"- backend: `pod`",
            f"- model: `{cell}`",
            f"- domain: {domain}",
            f"- template: (none — pod inference, no framework prompt)",
            f"- retrieved corpus: (none)",
            f"- latency_ms: {latency_ms}",
            f"- cost_usd: $0.00000",
            f"- prompt_tokens: 0",
            f"- completion_tokens: 0",
            "",
            "## Question",
            "",
            question,
            "",
            "## Response",
            "",
        ]
        out_path = out_dir / f"q{qid:02d}-{cell}.md"
        out_path.write_text("\n".join(lines) + response + "\n", encoding="utf-8")
        print(f"  wrote {out_path.name}", file=sys.stderr)
        n += 1

    print(f"done: {n} files in {out_dir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
