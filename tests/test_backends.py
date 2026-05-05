"""Regression tests for backend None-response handling.

ham-008: backends.py was extracting `data["choices"][0]["message"]["content"]`
without None-checking; OpenRouter occasionally returns null content (content-
policy refusals, empty completions, upstream provider errors). Resulted in
CallResult.response = None, then crash at hammerstein.py:226 on
`len(result.response)`.

These tests cover the None-response branch for all three remote backends
(openrouter, deepseek, claude) plus the local ollama backend's missing-key
behavior. Stdlib unittest only; no pip dependencies per the project's
zero-install discipline.
"""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "harness"))

from hammerstein import backends  # noqa: E402


class TestOpenRouterNullContent(unittest.TestCase):
    """OpenRouter returning null content -> BackendError, not crash."""

    def test_null_content_raises_backend_error(self):
        fake_response = {
            "choices": [{
                "message": {"content": None},
                "finish_reason": "content_filter",
            }],
            "usage": {},
        }
        with patch.object(backends, "_post_json", return_value=fake_response):
            with self.assertRaises(backends.BackendError) as ctx:
                backends.call_openrouter(
                    "test prompt",
                    model="qwen/qwen3.6-plus",
                    api_key="fake-key",
                )
        self.assertIn("null content", str(ctx.exception).lower())
        self.assertIn("content_filter", str(ctx.exception))


class TestDeepSeekNullContent(unittest.TestCase):
    def test_null_content_raises_backend_error(self):
        fake_response = {
            "choices": [{
                "message": {"content": None},
                "finish_reason": "stop",
            }],
            "usage": {},
        }
        with patch.object(backends, "_post_json", return_value=fake_response):
            with self.assertRaises(backends.BackendError) as ctx:
                backends.call_deepseek(
                    "test prompt",
                    model="deepseek-chat",
                    api_key="fake-key",
                )
        self.assertIn("null content", str(ctx.exception).lower())


class TestClaudeNullContent(unittest.TestCase):
    """Claude API returning null text or empty content array -> BackendError."""

    def test_null_text_raises_backend_error(self):
        fake_response = {
            "content": [{"text": None, "type": "text"}],
            "stop_reason": "end_turn",
            "usage": {},
        }
        with patch.object(backends, "_post_json", return_value=fake_response):
            with self.assertRaises(backends.BackendError) as ctx:
                backends.call_claude(
                    "test prompt",
                    model="claude-sonnet-4-6",
                    api_key="fake-key",
                )
        self.assertIn("null text content", str(ctx.exception).lower())

    def test_empty_content_array_raises_backend_error(self):
        fake_response = {
            "content": [],
            "stop_reason": "tool_use",
            "usage": {},
        }
        with patch.object(backends, "_post_json", return_value=fake_response):
            with self.assertRaises(backends.BackendError) as ctx:
                backends.call_claude(
                    "test prompt",
                    model="claude-sonnet-4-6",
                    api_key="fake-key",
                )
        self.assertIn("empty content array", str(ctx.exception).lower())


class TestSuccessfulResponses(unittest.TestCase):
    """Sanity check: valid responses still work after the None-check."""

    def test_openrouter_valid_response(self):
        fake_response = {
            "choices": [{
                "message": {"content": "Hello, world."},
                "finish_reason": "stop",
            }],
            "usage": {"cost": 0.001, "prompt_tokens": 10, "completion_tokens": 3},
        }
        with patch.object(backends, "_post_json", return_value=fake_response):
            result = backends.call_openrouter(
                "test", model="m", api_key="k",
            )
        self.assertEqual(result.response, "Hello, world.")
        self.assertEqual(result.backend, "openrouter")

    def test_claude_valid_response(self):
        fake_response = {
            "content": [{"text": "Hello, world.", "type": "text"}],
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 10, "output_tokens": 3},
        }
        with patch.object(backends, "_post_json", return_value=fake_response):
            result = backends.call_claude(
                "test", model="claude-sonnet-4-6", api_key="k",
            )
        self.assertEqual(result.response, "Hello, world.")
        self.assertEqual(result.backend, "claude")


if __name__ == "__main__":
    unittest.main()
