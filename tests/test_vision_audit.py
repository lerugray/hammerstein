"""Vision-audit benchmark fixtures and harness (ham-022d commit 4)."""

from __future__ import annotations

import base64
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "harness"))

from hammerstein import backends, shape_gate  # noqa: E402

_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "vision-audit"

_TWAR_PC_FIXTURE = _FIXTURE_DIR / "twar-pc-s5-hex-grid.png"
_RETROGAZE_FIXTURE = _FIXTURE_DIR / "retrogaze-rg-023-sprite.png"
_FNORDOS_FIXTURE = _FIXTURE_DIR / "fnordos-dept-23-panel.png"

# Placeholder verdict strings -- swap to real expected substrings
# once real images land (see fixtures/vision-audit/README.md).
_EXPECTED_TWAR_PC: str | None = None
_EXPECTED_RETROGAZE: str | None = None
_EXPECTED_FNORDOS: str | None = None

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

_SHAPED = "**Plain English summary:** test verdict\n\n---\n\nbody"


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


def _assert_fixture_png(path: Path) -> None:
    assert path.is_file()
    assert path.stat().st_size > 0
    head = path.read_bytes()[: len(_PNG_MAGIC)]
    assert head == _PNG_MAGIC


def test_twar_pc_fixture_exists_and_is_png() -> None:
    _assert_fixture_png(_TWAR_PC_FIXTURE)


def test_retrogaze_fixture_exists_and_is_png() -> None:
    _assert_fixture_png(_RETROGAZE_FIXTURE)


def test_fnordos_fixture_exists_and_is_png() -> None:
    _assert_fixture_png(_FNORDOS_FIXTURE)


def test_twar_pc_load_image_round_trip() -> None:
    raw = _TWAR_PC_FIXTURE.read_bytes()
    b64, mt = backends.load_image_as_base64(str(_TWAR_PC_FIXTURE))
    assert mt == "image/png"
    assert isinstance(b64, str)
    assert base64.b64decode(b64.encode("ascii")) == raw


def test_retrogaze_load_image_round_trip() -> None:
    raw = _RETROGAZE_FIXTURE.read_bytes()
    b64, mt = backends.load_image_as_base64(str(_RETROGAZE_FIXTURE))
    assert mt == "image/png"
    assert isinstance(b64, str)
    assert base64.b64decode(b64.encode("ascii")) == raw


def test_fnordos_load_image_round_trip() -> None:
    raw = _FNORDOS_FIXTURE.read_bytes()
    b64, mt = backends.load_image_as_base64(str(_FNORDOS_FIXTURE))
    assert mt == "image/png"
    assert isinstance(b64, str)
    assert base64.b64decode(b64.encode("ascii")) == raw


def _fake_openrouter_factory(response: str) -> Callable[..., backends.CallResult]:
    """Stand-in for model dispatch: run load_image_as_base64 like the real path, no HTTP."""

    def _fake(
        prompt: str,
        *,
        model: str,
        api_key: str,
        timeout: int = 120,
        image_path: str | None = None,
    ) -> backends.CallResult:
        assert image_path is not None
        _b64, mt = backends.load_image_as_base64(image_path)
        assert mt == "image/png"
        assert prompt
        return _result(response, model=model)

    return _fake


def test_twar_pc_shape_gate_harness_primary_passes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        backends,
        "call_openrouter",
        _fake_openrouter_factory(_SHAPED),
    )

    def primary_call() -> backends.CallResult:
        return backends.call_openrouter(
            "audit prompt",
            model="x",
            api_key="k",
            timeout=1,
            image_path=str(_TWAR_PC_FIXTURE),
        )

    outcome = shape_gate.run_with_shape_gate(
        primary_call=primary_call,
        primary_label="primary",
        failover_call=None,
        log_dir=tmp_path,
    )
    assert outcome.failed_over is False
    assert shape_gate.is_well_shaped(outcome.result.response)
    assert outcome.primary_log is None


def test_retrogaze_shape_gate_harness_failover_on_malformed_primary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    state = {"n": 0}

    def _sequential_fake(
        prompt: str,
        *,
        model: str,
        api_key: str,
        timeout: int = 120,
        image_path: str | None = None,
    ) -> backends.CallResult:
        assert image_path is not None
        _b64, mt = backends.load_image_as_base64(image_path)
        assert mt == "image/png"
        state["n"] += 1
        if state["n"] == 1:
            return _result("unstructured model ramble", model=model)
        return _result(_SHAPED, model=model)

    monkeypatch.setattr(backends, "call_openrouter", _sequential_fake)

    def primary_call() -> backends.CallResult:
        return backends.call_openrouter(
            "audit prompt",
            model="p",
            api_key="k",
            timeout=1,
            image_path=str(_RETROGAZE_FIXTURE),
        )

    def failover_call() -> backends.CallResult:
        return backends.call_openrouter(
            "audit prompt",
            model="f",
            api_key="k",
            timeout=1,
            image_path=str(_RETROGAZE_FIXTURE),
        )

    outcome = shape_gate.run_with_shape_gate(
        primary_call=primary_call,
        primary_label="p",
        failover_call=failover_call,
        failover_label="f",
        log_dir=tmp_path,
    )
    assert outcome.failed_over is True
    assert shape_gate.is_well_shaped(outcome.result.response)
    assert outcome.primary_log is not None
    assert outcome.primary_log.exists()


def test_fnordos_shape_gate_harness_raises_on_dual_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    state = {"n": 0}

    def _dual_fake(
        prompt: str,
        *,
        model: str,
        api_key: str,
        timeout: int = 120,
        image_path: str | None = None,
    ) -> backends.CallResult:
        assert image_path is not None
        _b64, mt = backends.load_image_as_base64(image_path)
        assert mt == "image/png"
        state["n"] += 1
        if state["n"] == 1:
            return _result("bad primary", model=model)
        return _result("bad failover", model=model)

    monkeypatch.setattr(backends, "call_openrouter", _dual_fake)

    def primary_call() -> backends.CallResult:
        return backends.call_openrouter(
            "audit prompt",
            model="a",
            api_key="k",
            timeout=1,
            image_path=str(_FNORDOS_FIXTURE),
        )

    def failover_call() -> backends.CallResult:
        return backends.call_openrouter(
            "audit prompt",
            model="b",
            api_key="k",
            timeout=1,
            image_path=str(_FNORDOS_FIXTURE),
        )

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


@pytest.mark.skipif(
    _EXPECTED_TWAR_PC is None,
    reason="real benchmark image not yet swapped in; see fixtures/vision-audit/README.md",
)
def test_twar_pc_audit_returns_expected_verdict() -> None:
    pass


@pytest.mark.skipif(
    _EXPECTED_RETROGAZE is None,
    reason="real benchmark image not yet swapped in; see fixtures/vision-audit/README.md",
)
def test_retrogaze_audit_returns_expected_verdict() -> None:
    pass


@pytest.mark.skipif(
    _EXPECTED_FNORDOS is None,
    reason="real benchmark image not yet swapped in; see fixtures/vision-audit/README.md",
)
def test_fnordos_audit_returns_expected_verdict() -> None:
    pass
