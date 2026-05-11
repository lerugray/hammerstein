"""Format v0.4 pod results.json into v0 benchmark result file format.

Reads the JSON output from run-v04-pod.py and writes one markdown file
per (qid, cell) pair to the v0.4 results directory, matching the layout
that judge_pairs.py expects.

Usage:
    python eval/format-v04-pod-results.py /tmp/v04-pod-results.json v04-cross-scale-2026-05-11
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_ROOT = REPO_ROOT / "eval" / "results"

CELL_META = {
    "rp-hammerstein-7b": {
        "backend": "transformers+peft (on RunPod RTX 4090)",
        "model": "Qwen/Qwen2.5-7B-Instruct + lerugray/hammerstein-7b-lora (v3a)",
        "mode": "raw (NO system prompt; framework lives in adapter weights)",
    },
    "rp-qwen25-7b-raw": {
        "backend": "transformers (on RunPod RTX 4090)",
        "model": "Qwen/Qwen2.5-7B-Instruct (base only)",
        "mode": "raw (NO system prompt, NO adapter)",
    },
}


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: format-v04-pod-results.py <results.json> <run-name>", file=sys.stderr)
        return 2
    results_path = Path(sys.argv[1])
    run_name = sys.argv[2]
    out_dir = RESULTS_ROOT / run_name
    out_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(results_path.read_text(encoding="utf-8"))
    n = 0
    for entry in data:
        cell = entry["cell"]
        qid = entry["qid"]
        meta = CELL_META.get(cell, {"backend": "?", "model": "?", "mode": "?"})
        body = (
            f"# Q{qid} · cell={cell}\n\n"
            f"- backend: `{meta['backend']}`\n"
            f"- model: `{meta['model']}`\n"
            f"- mode: `{meta['mode']}`\n"
            f"- template: `None`\n"
            f"- retrieved corpus: (none)\n"
            f"- latency_ms: {entry.get('latency_ms', 0)}\n"
            f"\n"
            f"## Question\n\n{entry['query']}\n\n"
            f"## Response\n\n{entry['response']}\n"
        )
        out_path = out_dir / f"q{qid:02d}-{cell}.md"
        out_path.write_text(body, encoding="utf-8")
        n += 1
    print(f"wrote {n} files to {out_dir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
