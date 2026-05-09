"""Output-shape gate for vision-Hammerstein audits.

Per scope/VISION-SUPPORT.md (private), audit-this-visual responses
must match a regex shape before downstream consumers (brief.ts, etc.)
read them. Vision models drift toward conversational framing that
silently breaks the parser; the gate catches that drift and either
fails over once to a paid backend or returns a structured error.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from . import backends


SHAPE_REGEX = re.compile(r"^\*\*Plain English summary:\*\*[\s\S]+---[\s\S]+$")

_PATH_SAFE = re.compile(r"[^A-Za-z0-9._-]+")


def is_well_shaped(response: str | None) -> bool:
    """True iff response begins with `**Plain English summary:**`,
    contains a `---` separator, and has body content after."""
    if not response:
        return False
    return bool(SHAPE_REGEX.match(response))


def log_raw_response(
    response: str,
    *,
    model: str,
    attempt: int,
    log_dir: Path | None = None,
) -> Path:
    """Append the raw failing response to a timestamped file under
    logs/shape-gate-failures/ (or a caller-supplied dir). Returns the
    path written. Caller does not need to handle directory creation."""
    log_dir = log_dir or Path("logs/shape-gate-failures")
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    safe_model = _PATH_SAFE.sub("_", model) or "unknown"
    path = log_dir / f"{ts}_{safe_model}_attempt{attempt}.txt"
    path.write_text(response or "", encoding="utf-8")
    return path


class ShapeGateFailure(Exception):
    """Raised when both primary and failover responses fail the shape
    gate, OR when primary fails and no failover is configured."""

    def __init__(
        self,
        primary_log: Path,
        failover_log: Optional[Path] = None,
    ) -> None:
        self.primary_log = primary_log
        self.failover_log = failover_log
        parts = [f"primary raw at {primary_log}"]
        if failover_log is not None:
            parts.append(f"failover raw at {failover_log}")
        super().__init__("shape-gate failed; " + "; ".join(parts))


@dataclass
class ShapeGateOutcome:
    result: backends.CallResult
    failed_over: bool
    primary_log: Optional[Path] = None


def run_with_shape_gate(
    *,
    primary_call: Callable[[], backends.CallResult],
    primary_label: str,
    failover_call: Optional[Callable[[], backends.CallResult]] = None,
    failover_label: Optional[str] = None,
    log_dir: Path | None = None,
) -> ShapeGateOutcome:
    """Run primary_call; validate shape; on fail, log raw and try the
    single failover (cap=1). Raises ShapeGateFailure on dual failure.

    The caller (cli.py) is responsible for constructing both primary_call
    and failover_call as zero-arg callables that return a CallResult --
    this keeps shape_gate decoupled from backend-selection logic.
    """
    result = primary_call()
    if is_well_shaped(result.response):
        return ShapeGateOutcome(result=result, failed_over=False)

    primary_log = log_raw_response(
        result.response or "",
        model=primary_label,
        attempt=1,
        log_dir=log_dir,
    )
    if failover_call is None:
        raise ShapeGateFailure(primary_log)

    result2 = failover_call()
    if is_well_shaped(result2.response):
        return ShapeGateOutcome(
            result=result2, failed_over=True, primary_log=primary_log
        )

    failover_log = log_raw_response(
        result2.response or "",
        model=failover_label or "unknown",
        attempt=2,
        log_dir=log_dir,
    )
    raise ShapeGateFailure(primary_log, failover_log)
