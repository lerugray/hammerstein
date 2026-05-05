"""Tests for hammerstein_cli.shell — Phase 2 hsh interactive shell (ham-014)."""

from __future__ import annotations

from hammerstein_cli import shell


# ---------------------------------------------------------------------------
# Rolling context buffer
# ---------------------------------------------------------------------------


def test_rolling_context_capacity_enforced() -> None:
    ctx = shell.RollingContext(capacity=2)
    ctx.add("p1", "s1")
    ctx.add("p2", "s2")
    ctx.add("p3", "s3")
    assert ctx.size() == 2
    # First entry should have been evicted
    rendered = ctx.render_prefix()
    assert "p1" not in rendered
    assert "p2" in rendered
    assert "p3" in rendered


def test_rolling_context_clear() -> None:
    ctx = shell.RollingContext(capacity=3)
    ctx.add("p", "s")
    ctx.clear()
    assert ctx.size() == 0
    assert ctx.render_prefix() == ""


def test_rolling_context_render_prefix_empty() -> None:
    ctx = shell.RollingContext(capacity=3)
    assert ctx.render_prefix() == ""


def test_rolling_context_render_prefix_format() -> None:
    ctx = shell.RollingContext(capacity=3)
    ctx.add("first prose", "first summary")
    out = ctx.render_prefix()
    assert "[Recent operator-Hammerstein iteration context:]" in out
    assert "Turn 1 — operator: first prose" in out
    assert "Turn 1 — Hammerstein (summary): first summary" in out
    assert "[Operator's current iteration:]" in out


# ---------------------------------------------------------------------------
# Response summarization
# ---------------------------------------------------------------------------


def test_summarize_short_response_unchanged() -> None:
    text = "This is a short response."
    assert shell.summarize_response(text) == text


def test_summarize_strips_chain_step_header() -> None:
    text = "[chain_step=1/4 provider=openrouter-primary cost=$0.007]\nReal content here."
    result = shell.summarize_response(text)
    assert "chain_step" not in result
    assert "Real content here." in result


def test_summarize_caps_at_sentence_boundary() -> None:
    text = "First sentence. " * 100  # way over cap
    result = shell.summarize_response(text, cap=80)
    # Should end with sentence boundary + ellipsis marker
    assert result.endswith("[...]")
    assert len(result) < 200


def test_summarize_empty_response() -> None:
    assert shell.summarize_response("") == "(empty response)"


# ---------------------------------------------------------------------------
# Line parsing
# ---------------------------------------------------------------------------


def test_parse_empty_line() -> None:
    verb, rest = shell.parse_line("")
    assert verb == "noop"


def test_parse_plain_prose() -> None:
    verb, rest = shell.parse_line("should I refactor the parser")
    assert verb == "prose"
    assert rest == "should I refactor the parser"


def test_parse_audit_short_form() -> None:
    verb, rest = shell.parse_line(":a should I refactor")
    assert verb == "template:audit-this-plan"
    assert rest == "should I refactor"


def test_parse_audit_long_form() -> None:
    verb, rest = shell.parse_line(":audit should I refactor")
    assert verb == "template:audit-this-plan"


def test_parse_scope_verb() -> None:
    verb, rest = shell.parse_line(":s explore this")
    assert verb == "template:scope-this-idea"


def test_parse_dispatch() -> None:
    verb, rest = shell.parse_line(":d fix the typo in README")
    assert verb == "dispatch"
    assert rest == "fix the typo in README"


def test_parse_bash() -> None:
    verb, rest = shell.parse_line("!ls -la")
    assert verb == "bash"
    assert rest == "ls -la"


def test_parse_exit() -> None:
    for cmd in (":exit", ":quit", ":q"):
        verb, _ = shell.parse_line(cmd)
        assert verb == "exit"


def test_parse_help() -> None:
    for cmd in (":help", ":?", ":h"):
        verb, _ = shell.parse_line(cmd)
        assert verb == "help"


def test_parse_unknown_verb() -> None:
    verb, rest = shell.parse_line(":nonsense some args")
    assert verb == "unknown:nonsense"
    assert rest == "some args"


# ---------------------------------------------------------------------------
# Template verb table
# ---------------------------------------------------------------------------


def test_template_verbs_cover_all_short_forms() -> None:
    for short in ("a", "s", "w", "n", "r"):
        assert short in shell.TEMPLATE_VERBS


def test_template_verbs_cover_all_long_forms() -> None:
    for long in ("audit", "scope", "worth", "next", "sharper"):
        assert long in shell.TEMPLATE_VERBS
