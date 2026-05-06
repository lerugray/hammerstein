"""Tests for hammerstein_cli.dispatch — Phase 1 dispatch wrapper (ham-013)."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from hammerstein_cli import dispatch


# ---------------------------------------------------------------------------
# Provider table integrity
# ---------------------------------------------------------------------------


def test_provider_table_well_formed() -> None:
    """Every provider entry must have model + api_key_env + aider_provider + executor + description."""
    required = {"model", "api_key_env", "aider_provider", "executor", "description"}
    for name, cfg in dispatch.PROVIDERS.items():
        missing = required - cfg.keys()
        assert not missing, f"provider {name!r} missing keys: {missing}"
        assert isinstance(cfg["model"], str) and cfg["model"], f"provider {name!r} bad model"
        assert cfg["executor"] in ("aider", "claude-code"), (
            f"provider {name!r} has unknown executor {cfg['executor']!r}"
        )


def test_default_provider_in_table() -> None:
    assert dispatch.DEFAULT_PROVIDER in dispatch.PROVIDERS


def test_claude_code_provider_uses_subscription_executor() -> None:
    """The claude-code provider must route through the claude-code executor (not aider)."""
    cfg = dispatch.PROVIDERS["claude-code"]
    assert cfg["executor"] == "claude-code"
    assert cfg["api_key_env"] is None, "claude-code uses subscription, not API key"
    assert cfg["aider_provider"] is None, "claude-code bypasses aider entirely"


# ---------------------------------------------------------------------------
# build_aider_command
# ---------------------------------------------------------------------------


def test_build_aider_command_with_key() -> None:
    """API-keyed provider produces expected aider invocation shape."""
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test-123"}, clear=False):
        cmd = dispatch.build_aider_command(
            prose="rename foo to bar",
            provider="openrouter",
            files=[],
            read_files=[],
            no_auto_commits=False,
            architect=False,
        )
    assert cmd[0] == "aider"
    assert "--model" in cmd
    model_index = cmd.index("--model")
    assert cmd[model_index + 1] == "openrouter/qwen/qwen3.6-plus"
    assert "--api-key" in cmd
    key_index = cmd.index("--api-key")
    assert cmd[key_index + 1] == "openrouter=sk-test-123"
    assert "--message" in cmd
    msg_index = cmd.index("--message")
    assert cmd[msg_index + 1] == "rename foo to bar"
    assert "--yes-always" in cmd
    assert "--exit" in cmd


def test_build_aider_command_missing_key_raises() -> None:
    """Missing API key env var should raise RuntimeError."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError, match="missing OPENROUTER_API_KEY"):
            dispatch.build_aider_command(
                prose="x",
                provider="openrouter",
                files=[],
                read_files=[],
                no_auto_commits=False,
                architect=False,
            )


def test_build_aider_command_ollama_no_key_required() -> None:
    """Ollama provider should not require an API key."""
    with patch.dict(os.environ, {}, clear=True):
        cmd = dispatch.build_aider_command(
            prose="local task",
            provider="ollama",
            files=[],
            read_files=[],
            no_auto_commits=False,
            architect=False,
        )
    assert "--api-key" not in cmd


def test_build_aider_command_with_files() -> None:
    """--file and --read flags should pass through, repeatable."""
    with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "sk-deep"}, clear=False):
        cmd = dispatch.build_aider_command(
            prose="x",
            provider="deepseek",
            files=["a.py", "b.py"],
            read_files=["c.md"],
            no_auto_commits=True,
            architect=True,
        )
    assert cmd.count("--file") == 2
    assert "a.py" in cmd
    assert "b.py" in cmd
    assert cmd.count("--read") == 1
    assert "c.md" in cmd
    assert "--no-auto-commits" in cmd
    assert "--architect" in cmd


# ---------------------------------------------------------------------------
# redact_command_for_display
# ---------------------------------------------------------------------------


def test_redact_command_masks_api_key_value() -> None:
    cmd = [
        "aider",
        "--model",
        "openrouter/qwen/qwen3.6-plus",
        "--api-key",
        "openrouter=sk-secret-abc",
        "--message",
        "task",
        "--yes-always",
        "--exit",
    ]
    out = dispatch.redact_command_for_display(cmd)
    assert "sk-secret-abc" not in out
    assert "openrouter=***REDACTED***" in out
    assert "--model" in out
    assert "task" in out


def test_redact_command_no_api_key_unchanged() -> None:
    """Ollama-style command with no --api-key should round-trip unchanged."""
    cmd = ["aider", "--model", "ollama/qwen3:8b", "--message", "x", "--exit"]
    out = dispatch.redact_command_for_display(cmd)
    assert out == "aider --model ollama/qwen3:8b --message x --exit"


# ---------------------------------------------------------------------------
# build_claude_code_command
# ---------------------------------------------------------------------------


def test_build_claude_code_command_shape() -> None:
    """claude-code executor produces `claude -p <prose> --dangerously-skip-permissions ...`."""
    cmd = dispatch.build_claude_code_command("rename foo to bar in cli.py")
    assert cmd[0] == "claude"
    assert cmd[1] == "-p"
    assert cmd[2] == "rename foo to bar in cli.py"
    assert "--dangerously-skip-permissions" in cmd
    assert "--output-format" in cmd
    fmt_index = cmd.index("--output-format")
    assert cmd[fmt_index + 1] == "text"
    # Critically: NOT an aider invocation
    assert "aider" not in cmd
    assert "--api-key" not in cmd
    assert "--message" not in cmd
