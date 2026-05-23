"""JSONL call-logger.

Every backend call appends one line to `logs/hammerstein-calls.jsonl`.
Format locked by `tech/STACK-DECISION.md` § "Logging format locked".
"""

from __future__ import annotations

import json
import socket
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class CallRecord:
    timestamp: str  # ISO-8601 UTC
    backend: str
    model: str
    system_prompt_version: str
    provider_id: str | None = None
    chain_step: int | None = None
    chain_len: int | None = None
    template: str | None = None
    retrieved_corpus_ids: list[str] = field(default_factory=list)
    query: str = ""
    response: str = ""
    response_length: int = 0
    latency_ms: int = 0
    cost_usd: float = 0.0
    mode: str = "default"  # default | no-corpus | corpus-only
    error: str | None = None
    hostname: str = field(default_factory=socket.gethostname)


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def append(record: CallRecord, log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
