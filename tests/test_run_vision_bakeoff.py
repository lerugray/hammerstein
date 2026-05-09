"""Unit tests for tools/run_vision_bakeoff.py (ham-022e commit 5)."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "tools"))

from run_vision_bakeoff import (  # noqa: E402
    BAKEOFF_GPT_OPENROUTER_MODEL,
    BAKEOFF_QWEN_OPENROUTER_MODEL,
    QWEN_LABEL,
    apply_decision_tree,
    _is_placeholder_png,
)


def _case_result(
    *,
    shape: bool,
    semantic: bool,
) -> dict[str, object]:
    return {
        "provider_label": QWEN_LABEL,
        "shape_gate_passed": shape,
        "semantic_passed": semantic,
    }


def _fixture(
    name: str,
    kind: str,
    expected: list[list[str]] | None,
    qwen_shape: bool,
    qwen_semantic: bool,
) -> dict[str, object]:
    return {
        "name": name,
        "real_or_placeholder": kind,
        "expected_substrings_or_null": expected,
        "results_by_provider": [_case_result(shape=qwen_shape, semantic=qwen_semantic)],
    }


def test_apply_decision_tree_qwen_passes_full_lock() -> None:
    doc = {
        "fixtures": [
            _fixture("a", "real", [["hex"], ["area"]], True, True),
            _fixture("b", "real", [["craft"], ["shade"]], True, True),
            _fixture("c", "real", [["z"], ["w"]], True, True),
        ]
    }
    dec = apply_decision_tree(doc)
    assert dec["primary_backend"] == "openrouter"
    assert dec["primary_model"] == BAKEOFF_QWEN_OPENROUTER_MODEL
    assert dec["failover_backend"] == "openrouter"
    assert dec["failover_model"] == BAKEOFF_GPT_OPENROUTER_MODEL
    assert "failover-on-shape-fail to GPT-4o" in dec["rationale"]


def test_apply_decision_tree_qwen_shape_fails_one_case() -> None:
    doc = {
        "fixtures": [
            _fixture("a", "real", [["a"], ["b"]], True, True),
            _fixture("b", "real", [["a"], ["b"]], True, True),
            _fixture("c", "real", [["a"], ["b"]], False, True),
        ]
    }
    dec = apply_decision_tree(doc)
    assert dec["primary_model"] == BAKEOFF_GPT_OPENROUTER_MODEL
    assert dec["failover_backend"] is None
    assert dec["failover_model"] is None
    assert "failed shape or semantic" in dec["rationale"]


def test_apply_decision_tree_qwen_semantic_below_half() -> None:
    doc = {
        "fixtures": [
            _fixture("a", "real", [["a"], ["b"]], True, True),
            _fixture("b", "real", [["a"], ["b"]], True, False),
            _fixture("c", "real", [["a"], ["b"]], True, False),
        ]
    }
    dec = apply_decision_tree(doc)
    assert dec["primary_model"] == BAKEOFF_GPT_OPENROUTER_MODEL
    assert dec["failover_model"] is None


def test_apply_decision_tree_skips_placeholder_cases() -> None:
    doc = {
        "fixtures": [
            {
                "name": "tiny",
                "real_or_placeholder": "placeholder",
                "expected_substrings_or_null": None,
                "results_by_provider": [],
            },
            _fixture("r1", "real", [["a"], ["b"]], True, True),
            _fixture("r2", "real", [["a"], ["b"]], True, True),
        ]
    }
    dec = apply_decision_tree(doc)
    assert dec["primary_model"] == BAKEOFF_QWEN_OPENROUTER_MODEL
    assert dec["failover_model"] == BAKEOFF_GPT_OPENROUTER_MODEL
    assert "Excluded 1 placeholder" in dec["rationale"]


def test_apply_decision_tree_no_real_fixtures() -> None:
    doc = {
        "fixtures": [
            {
                "name": "p1",
                "real_or_placeholder": "placeholder",
                "expected_substrings_or_null": None,
                "results_by_provider": [],
            },
        ]
    }
    dec = apply_decision_tree(doc)
    assert dec["primary_model"] == BAKEOFF_GPT_OPENROUTER_MODEL
    assert dec["failover_model"] is None
    assert "no real fixtures" in dec["rationale"]


def test_is_placeholder_png_detects_67_byte_file(tmp_path: Path) -> None:
    small = tmp_path / "p.png"
    small.write_bytes(b"x" * 67)
    big = tmp_path / "b.png"
    big.write_bytes(b"y" * 101)
    assert _is_placeholder_png(small) is True
    assert _is_placeholder_png(big) is False
