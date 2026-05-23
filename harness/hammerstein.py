#!/usr/bin/env python3
"""Hammerstein v0 CLI.

Usage:
    hammerstein "<query>"                       # one-shot strategic query
    hammerstein --model ollama:qwen3:8b "<q>"   # explicit model spec
    hammerstein --no-corpus "<q>"               # ablation: prompt-only
    hammerstein --corpus-only "<q>"             # ablation: corpus-only
    hammerstein --template audit-this-plan "<q>"

Model spec syntax: `<backend>:<model>` where backend is one of
ollama, openrouter, deepseek, claude. If no colon, treated as a
backend default model lookup (`ollama` -> qwen3:8b, `openrouter`
-> qwen/qwen3.6-plus, `deepseek` -> deepseek-chat, `claude` ->
claude-sonnet-4-6).

Returns the model's response on stdout; logs the call to
`logs/hammerstein-calls.jsonl`.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running from a checkout by making both:
# - `harness/hammerstein/` (the code package), and
# - repo root (resource packages `corpus/`, `prompts/`)
# importable.
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
for p in (str(_HERE), str(_REPO_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from hammerstein.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
