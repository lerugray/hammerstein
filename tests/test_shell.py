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


# ---------------------------------------------------------------------------
# Project state & root detection
# ---------------------------------------------------------------------------


def test_find_project_root_with_git(tmp_path) -> None:
    (tmp_path / ".git").mkdir()
    assert shell.find_project_root(tmp_path) == tmp_path


def test_find_project_root_with_pyproject(tmp_path) -> None:
    (tmp_path / "pyproject.toml").touch()
    assert shell.find_project_root(tmp_path) == tmp_path


def test_find_project_root_walks_up(tmp_path) -> None:
    sub = tmp_path / "sub"
    sub.mkdir()
    (tmp_path / ".git").mkdir()
    assert shell.find_project_root(sub) == tmp_path


def test_find_project_root_falls_back_to_cwd(tmp_path) -> None:
    assert shell.find_project_root(tmp_path) == tmp_path


def test_find_state_file_returns_expected_path(tmp_path) -> None:
    assert shell.find_state_file(tmp_path) == tmp_path / ".hammerstein-state.md"


def test_load_state_preamble_missing(tmp_path) -> None:
    assert shell.load_state_preamble(tmp_path / "nope.md") == ""


def test_load_state_preamble_reads_content(tmp_path) -> None:
    f = tmp_path / ".hammerstein-state.md"
    f.write_text("Current focus: auth refactor\n", encoding="utf-8")
    assert shell.load_state_preamble(f) == "Current focus: auth refactor"


def test_load_state_preamble_strips_whitespace(tmp_path) -> None:
    f = tmp_path / ".hammerstein-state.md"
    f.write_text("  \n  Focus: X  \n", encoding="utf-8")
    assert shell.load_state_preamble(f) == "Focus: X"


def test_show_or_edit_state_missing(capsys, tmp_path) -> None:
    shell.show_or_edit_state(tmp_path / "missing.md")
    out = capsys.readouterr().out
    assert "No state file found" in out


def test_show_or_edit_state_present(capsys, tmp_path) -> None:
    f = tmp_path / ".hammerstein-state.md"
    f.write_text("State content", encoding="utf-8")
    shell.show_or_edit_state(f)
    out = capsys.readouterr().out
    assert "State content" in out
    assert "---" in out


def test_find_project_root_with_package_json(tmp_path) -> None:
    (tmp_path / "package.json").touch()
    assert shell.find_project_root(tmp_path) == tmp_path


def test_find_project_root_with_cargo_toml(tmp_path) -> None:
    (tmp_path / "Cargo.toml").touch()
    assert shell.find_project_root(tmp_path) == tmp_path


def test_find_project_root_with_go_mod(tmp_path) -> None:
    (tmp_path / "go.mod").touch()
    assert shell.find_project_root(tmp_path) == tmp_path


def test_show_or_edit_state_edit_creates_missing(tmp_path, monkeypatch, capsys) -> None:
    """`:state edit` should create the file at the given path if missing,
    then attempt to invoke $EDITOR."""
    state_file = tmp_path / ".hammerstein-state.md"
    assert not state_file.exists()

    invoked = []

    def fake_run(cmd, **kwargs):
        invoked.append(cmd)
        class Res:
            returncode = 0
        return Res()

    monkeypatch.setattr(shell.subprocess, "run", fake_run)
    monkeypatch.setenv("EDITOR", "vi")

    shell.show_or_edit_state(state_file, mode="edit")

    assert state_file.exists()
    assert invoked, "editor was never invoked"
    assert invoked[0][0] == "vi"
    assert invoked[0][1] == str(state_file)


def test_show_or_edit_state_edit_uses_editor_env(tmp_path, monkeypatch) -> None:
    """`:state edit` should respect $EDITOR with nano fallback."""
    state_file = tmp_path / ".hammerstein-state.md"
    state_file.write_text("existing", encoding="utf-8")

    invoked = []
    monkeypatch.setattr(
        shell.subprocess,
        "run",
        lambda cmd, **kw: invoked.append(cmd) or type("R", (), {"returncode": 0})(),
    )
    monkeypatch.delenv("EDITOR", raising=False)

    shell.show_or_edit_state(state_file, mode="edit")
    assert invoked[0][0] == "nano"


def test_show_or_edit_state_unknown_arg(tmp_path, capsys) -> None:
    state_file = tmp_path / ".hammerstein-state.md"
    state_file.write_text("x", encoding="utf-8")
    shell.show_or_edit_state(state_file, mode="bogus")
    out = capsys.readouterr().out
    assert "unknown :state arg" in out


def test_parse_state_verb() -> None:
    verb, rest = shell.parse_line(":state")
    assert verb == "state"
    assert rest == ""


def test_parse_state_verb_with_args() -> None:
    verb, rest = shell.parse_line(":state edit")
    assert verb == "state"
    assert rest == "edit"


def test_run_template_injects_state_before_context(tmp_path, monkeypatch) -> None:
    (tmp_path / ".git").mkdir()
    state = tmp_path / ".hammerstein-state.md"
    state.write_text("Project state: active", encoding="utf-8")
    
    monkeypatch.chdir(tmp_path)
    
    ctx = shell.RollingContext()
    ctx.add("prev prose", "prev summary")
    
    captured_cmd = []
    def fake_run(cmd, **kwargs):
        captured_cmd.append(cmd)
        class Res: returncode = 0
        return Res()
    
    monkeypatch.setattr(shell.subprocess, "run", fake_run)
    monkeypatch.setattr(shell, "read_last_audit_response", lambda: "resp")
    monkeypatch.setattr(shell, "log_shell_turn", lambda r: None)
    
    shell.run_template("new query", "audit-this-plan", ctx)
    
    assert len(captured_cmd) == 1
    full_query = captured_cmd[0][1]
    state_idx = full_query.find("Project state: active")
    ctx_idx = full_query.find("prev prose")
    query_idx = full_query.find("new query")
    assert state_idx != -1
    assert ctx_idx != -1
    assert query_idx != -1
    assert state_idx < ctx_idx < query_idx


def test_run_template_no_state_skips_preamble(tmp_path, monkeypatch) -> None:
    (tmp_path / ".git").mkdir()
    # No state file created
    monkeypatch.chdir(tmp_path)
    
    ctx = shell.RollingContext()
    captured_cmd = []
    def fake_run(cmd, **kwargs):
        captured_cmd.append(cmd)
        class Res: returncode = 0
        return Res()
    
    monkeypatch.setattr(shell.subprocess, "run", fake_run)
    monkeypatch.setattr(shell, "read_last_audit_response", lambda: "resp")
    monkeypatch.setattr(shell, "log_shell_turn", lambda r: None)
    
    shell.run_template("query only", "audit-this-plan", ctx)
    
    full_query = captured_cmd[0][1]
    assert "Project state preamble" not in full_query
    assert full_query == "query only"


def test_run_template_state_and_context_both_present(tmp_path, monkeypatch) -> None:
    (tmp_path / ".git").mkdir()
    state = tmp_path / ".hammerstein-state.md"
    state.write_text("State: X", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    
    ctx = shell.RollingContext()
    ctx.add("turn1", "sum1")
    
    captured_cmd = []
    def fake_run(cmd, **kwargs):
        captured_cmd.append(cmd)
        class Res: returncode = 0
        return Res()
    
    monkeypatch.setattr(shell.subprocess, "run", fake_run)
    monkeypatch.setattr(shell, "read_last_audit_response", lambda: "resp")
    monkeypatch.setattr(shell, "log_shell_turn", lambda r: None)
    
    shell.run_template("final", "audit-this-plan", ctx)
    
    full_query = captured_cmd[0][1]
    assert full_query.startswith("[Project state preamble:]")
    assert "State: X" in full_query
    assert "[Recent operator-Hammerstein iteration context:]" in full_query
    assert full_query.endswith("final")


def test_run_template_injection_order_with_empty_context(tmp_path, monkeypatch) -> None:
    (tmp_path / ".git").mkdir()
    state = tmp_path / ".hammerstein-state.md"
    state.write_text("State only", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    
    ctx = shell.RollingContext()
    captured_cmd = []
    def fake_run(cmd, **kwargs):
        captured_cmd.append(cmd)
        class Res: returncode = 0
        return Res()
    monkeypatch.setattr(shell.subprocess, "run", fake_run)
    monkeypatch.setattr(shell, "read_last_audit_response", lambda: "resp")
    monkeypatch.setattr(shell, "log_shell_turn", lambda r: None)
    
    shell.run_template("query", "audit-this-plan", ctx)
    full_query = captured_cmd[0][1]
    assert full_query.startswith("[Project state preamble:]")
    assert full_query.endswith("query")
