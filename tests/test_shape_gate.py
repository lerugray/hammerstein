"""Output-shape gate for audit-this-visual (ham-022c commit 3)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "harness"))

from hammerstein import backends, shape_gate  # noqa: E402


def _result(
    response: str,
    *,
    backend: str = "openrouter",
    model: str = "m",
) -> backends.CallResult:
    return backends.CallResult(
        response=response,
        latency_ms=1,
        cost_usd=0.0,
        model=model,
        backend=backend,
    )


def test_is_well_shaped_accepts_canonical_audit_response() -> None:
    text = (
        "**Plain English summary:** Yes ship it.\n\n"
        "---\n\n"
        "[audit body content here]"
    )
    assert shape_gate.is_well_shaped(text) is True


def test_is_well_shaped_rejects_missing_summary_header() -> None:
    text = (
        "Sure! Here is the audit:\n\n"
        "**Plain English summary:** ...\n\n---\n\nbody"
    )
    assert shape_gate.is_well_shaped(text) is False


def test_is_well_shaped_rejects_missing_separator() -> None:
    assert shape_gate.is_well_shaped("**Plain English summary:** ok") is False


def test_is_well_shaped_rejects_empty_or_none() -> None:
    assert shape_gate.is_well_shaped("") is False
    assert shape_gate.is_well_shaped(None) is False


def test_log_raw_response_writes_under_supplied_dir(tmp_path: Path) -> None:
    log_dir = tmp_path / "logs"
    payload = "raw failure body"
    path = shape_gate.log_raw_response(
        payload,
        model="test-model",
        attempt=1,
        log_dir=log_dir,
    )
    assert path.exists()
    assert path.read_text(encoding="utf-8") == payload
    assert "test-model" in path.name
    assert "attempt1" in path.name


def test_log_raw_response_sanitizes_model_label(tmp_path: Path) -> None:
    path = shape_gate.log_raw_response(
        "x",
        model="openrouter:openai/gpt-4o",
        attempt=1,
        log_dir=tmp_path,
    )
    name = path.name
    assert re.fullmatch(r"[A-Za-z0-9._-]+", name), name


def test_run_with_shape_gate_returns_outcome_when_primary_passes(
    tmp_path: Path,
) -> None:
    good = (
        "**Plain English summary:** ok\n\n---\n\nbody"
    )
    primary = _result(good)

    def primary_call() -> backends.CallResult:
        return primary

    outcome = shape_gate.run_with_shape_gate(
        primary_call=primary_call,
        primary_label="openrouter:x",
        failover_call=None,
        log_dir=tmp_path,
    )
    assert outcome.failed_over is False
    assert outcome.result.response == good
    assert outcome.primary_log is None


def test_run_with_shape_gate_falls_over_once_on_primary_fail(
    tmp_path: Path,
) -> None:
    bad = "nope"
    good = "**Plain English summary:** ok\n\n---\n\nbody"
    failover = _result(good, model="gpt-4o")

    def primary_call() -> backends.CallResult:
        return _result(bad)

    def failover_call() -> backends.CallResult:
        return failover

    outcome = shape_gate.run_with_shape_gate(
        primary_call=primary_call,
        primary_label="p",
        failover_call=failover_call,
        failover_label="f",
        log_dir=tmp_path,
    )
    assert outcome.failed_over is True
    assert outcome.result.response == good
    assert outcome.primary_log is not None
    assert isinstance(outcome.primary_log, Path)
    assert outcome.primary_log.exists()


def test_run_with_shape_gate_raises_on_dual_failure(tmp_path: Path) -> None:
    bad = "still bad"

    def primary_call() -> backends.CallResult:
        return _result(bad)

    def failover_call() -> backends.CallResult:
        return _result(bad + "2")

    with pytest.raises(shape_gate.ShapeGateFailure) as exc_info:
        shape_gate.run_with_shape_gate(
            primary_call=primary_call,
            primary_label="a",
            failover_call=failover_call,
            failover_label="b",
            log_dir=tmp_path,
        )
    exc = exc_info.value
    assert exc.primary_log is not None and exc.primary_log.exists()
    assert exc.failover_log is not None and exc.failover_log.exists()


def test_run_with_shape_gate_raises_when_no_failover_configured(
    tmp_path: Path,
) -> None:
    def primary_call() -> backends.CallResult:
        return _result("bad")

    with pytest.raises(shape_gate.ShapeGateFailure) as exc_info:
        shape_gate.run_with_shape_gate(
            primary_call=primary_call,
            primary_label="only",
            failover_call=None,
            log_dir=tmp_path,
        )
    exc = exc_info.value
    assert exc.primary_log is not None and exc.primary_log.exists()
    assert exc.failover_log is None
