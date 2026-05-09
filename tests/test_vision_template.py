"""Plumb tests for audit-this-visual template wiring (ham-022a commit 1)."""

from __future__ import annotations

from importlib import resources as importlib_resources
from pathlib import Path

from hammerstein import prompt as prompt_mod
from hammerstein.cli import build_parser
from hammerstein.corpus import _TEMPLATE_PRINCIPLE_BOOSTS


def test_audit_this_visual_template_loads() -> None:
    template_file = importlib_resources.files("prompts.templates").joinpath(
        "audit-this-visual.md"
    )
    text = prompt_mod.load_template_resource(template_file)
    assert isinstance(text, str) and text.strip() != ""


def test_audit_this_visual_template_has_negative_formatting_constraints() -> None:
    template_file = importlib_resources.files("prompts.templates").joinpath(
        "audit-this-visual.md"
    )
    raw = template_file.read_text(encoding="utf-8")
    assert "Do NOT add greetings" in raw
    assert "Plain English summary:" in raw
    assert r"[\s\S]" in raw
    assert "parser asserts on this shape" in raw


def test_audit_this_visual_in_template_help_string() -> None:
    parser = build_parser()
    action = parser._option_string_actions["--template"]
    assert action.help is not None
    assert "audit-this-visual" in action.help


def test_audit_this_visual_in_corpus_boosts() -> None:
    boosts = _TEMPLATE_PRINCIPLE_BOOSTS["audit-this-visual"]
    assert boosts["verification_first"] == 1.4
    assert boosts["counter_observation"] == 1.3


def test_audit_this_visual_in_minimal_context_set() -> None:
    import hammerstein.cli as cli_mod

    src = Path(cli_mod.__file__).read_text(encoding="utf-8")
    assert '"audit-this-visual"' in src
    assert '"audit-this-plan"' in src
    assert "context_mode = \"minimal\"" in src
