"""hsh — Hammerstein Shell.

Phase 2 of the Continuity Track (ham-014). Interactive REPL that holds
shell-state (cwd, rolling context buffer of last N=3 turns) while keeping
each Hammerstein-template call as a discrete fresh invocation.

Architectural choice: this OVERRIDES audit 3's strict "no context injection"
verdict, in favor of the operator-iteration pattern that's been the actual
value-driver across every Hammerstein consult today. Bounded context (last
3 turns, capped) is treated as iteration background, not conversation
hosting. Each LLM call still gets the audit-this-plan few-shot template +
fresh corpus retrieval.

Falsification gate: if `hsh` produces noticeably worse audits than fresh
`hammerstein` calls, kill the rolling-context injection and fall back to
verb-only mode. Empirically testable: compare hsh audit quality vs fresh
audit on the same query, end of week 1.
"""

from __future__ import annotations

import json
import os
import readline  # noqa: F401  -- side effect: enables arrow-key history
import shlex
import socket
import subprocess
import sys
import time
from collections import deque
from pathlib import Path

# Default config
ROLLING_CONTEXT_TURNS = 3
SUMMARY_CHAR_CAP = 400
HAMMERSTEIN_LOG_PATH = Path.home() / ".hammerstein" / "logs" / "hammerstein-calls.jsonl"
SHELL_LOG_PATH = Path.home() / ".hammerstein" / "logs" / "shell.jsonl"
HISTORY_FILE = Path.home() / ".hammerstein" / "shell_history"

# Built-in template-shortcut verbs (after `:` prefix)
TEMPLATE_VERBS: dict[str, str] = {
    "a": "audit-this-plan",
    "audit": "audit-this-plan",
    "s": "scope-this-idea",
    "scope": "scope-this-idea",
    "w": "is-this-worth-doing",
    "worth": "is-this-worth-doing",
    "n": "what-should-we-do-next",
    "next": "what-should-we-do-next",
    "r": "review-from-different-angle",
    "sharper": "review-from-different-angle",
}


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ---------------------------------------------------------------------------
# Project state & root detection
# ---------------------------------------------------------------------------


def find_project_root(start_dir: Path | None = None) -> Path:
    """Walk up from start_dir looking for .git or pyproject.toml."""
    if start_dir is None:
        start_dir = Path.cwd()
    current = start_dir.resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
            return parent
    return current


def find_state_file(root: Path) -> Path:
    return root / ".hammerstein-state.md"


def load_state_preamble(state_file: Path) -> str:
    if not state_file.exists():
        return ""
    try:
        return state_file.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def show_or_edit_state(state_file: Path) -> None:
    if state_file.exists():
        print(f"--- {state_file} ---")
        print(state_file.read_text(encoding="utf-8"))
        print("--- end ---")
    else:
        print(f"No state file found at {state_file}")
        print("Create it to persist project context across hsh sessions.")


# ---------------------------------------------------------------------------
# Rolling context buffer
# ---------------------------------------------------------------------------


class RollingContext:
    """Capped deque of recent (operator_prose, response_summary) pairs.

    Bounded at ROLLING_CONTEXT_TURNS to prevent unbounded conversation
    hosting. Each entry's response is summarized to SUMMARY_CHAR_CAP to
    keep injected prefix small.
    """

    def __init__(self, capacity: int = ROLLING_CONTEXT_TURNS) -> None:
        self.capacity = capacity
        self._buf: deque[tuple[str, str]] = deque(maxlen=capacity)

    def add(self, prose: str, response_summary: str) -> None:
        self._buf.append((prose, response_summary))

    def clear(self) -> None:
        self._buf.clear()

    def size(self) -> int:
        return len(self._buf)

    def render_prefix(self) -> str:
        """Render context as a prefix block. Empty string if buffer empty."""
        if not self._buf:
            return ""
        lines = ["[Recent operator-Hammerstein iteration context:]"]
        for i, (prose, summary) in enumerate(self._buf, start=1):
            lines.append(f"Turn {i} — operator: {prose}")
            lines.append(f"Turn {i} — Hammerstein (summary): {summary}")
        lines.append("")
        lines.append("[Operator's current iteration:]")
        return "\n".join(lines) + "\n"


def summarize_response(text: str, cap: int = SUMMARY_CHAR_CAP) -> str:
    """Truncate response to first sentence-boundary <= cap. Best-effort.

    Strips chain_step header line if present (it's not part of the actual
    audit content).
    """
    if not text:
        return "(empty response)"
    # Strip header line like "[chain_step=1/4 provider=... cost=$0.007]"
    lines = text.lstrip("\n").split("\n", 1)
    if lines[0].startswith("[chain_step="):
        text = lines[1] if len(lines) > 1 else ""
    text = text.strip()
    if len(text) <= cap:
        return text
    # Truncate at last sentence boundary <= cap
    truncated = text[:cap]
    for sep in (". ", ".\n", "! ", "? "):
        idx = truncated.rfind(sep)
        if idx > cap // 2:
            return truncated[: idx + 1] + " [...]"
    return truncated + " [...]"


def read_last_audit_response() -> str:
    """Read the most recent entry from hammerstein-calls.jsonl and return
    its response field. Returns empty string if log missing or empty."""
    if not HAMMERSTEIN_LOG_PATH.exists():
        return ""
    try:
        # Read backwards (last line); JSONL is append-only so last is most recent
        with HAMMERSTEIN_LOG_PATH.open("r", encoding="utf-8") as f:
            lines = f.readlines()
        if not lines:
            return ""
        last = json.loads(lines[-1])
        return last.get("response", "") or ""
    except (OSError, json.JSONDecodeError):
        return ""


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


def log_shell_turn(record: dict) -> None:
    SHELL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SHELL_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Action handlers
# ---------------------------------------------------------------------------


def run_template(prose: str, template: str, ctx: RollingContext) -> int:
    """Invoke `hammerstein <query> --template <template>`, streams live.

    Adds (prose, summary) to rolling context after the call completes.
    Returns the subprocess exit code.
    """
    # Inject project state preamble if available
    state_file = find_state_file(find_project_root())
    state_preamble = load_state_preamble(state_file)
    
    parts = []
    if state_preamble:
        parts.append("[Project state preamble:]")
        parts.append(state_preamble)
        parts.append("")
    
    ctx_prefix = ctx.render_prefix()
    if ctx_prefix:
        parts.append(ctx_prefix)
        
    full_query = "\n".join(parts) + prose
    
    start = time.time()
    try:
        result = subprocess.run(
            ["hammerstein", full_query, "--template", template],
            check=False,
        )
    except FileNotFoundError:
        print("error: hammerstein not on PATH", file=sys.stderr)
        return 127
    duration = time.time() - start

    # Read the response we just generated and summarize for next turn
    response_text = read_last_audit_response()
    summary = summarize_response(response_text)
    ctx.add(prose, summary)

    log_shell_turn(
        {
            "timestamp": now_iso(),
            "hostname": socket.gethostname(),
            "kind": "template",
            "template": template,
            "prose_chars": len(prose),
            "context_turns": ctx.size() - 1,  # turns BEFORE this one
            "duration_s": round(duration, 1),
            "exit_code": result.returncode if hasattr(result, "returncode") else 1,
            "summary_chars": len(summary),
        }
    )
    return result.returncode


def run_dispatch(task: str, args: list[str]) -> int:
    """Invoke `hd <task> <args...>` — dispatch to aider for actual code work."""
    cmd = ["hd"] + args + [task]
    start = time.time()
    try:
        result = subprocess.run(cmd, check=False)
    except FileNotFoundError:
        print("error: hd not on PATH (is hammerstein-ai installed?)", file=sys.stderr)
        return 127
    duration = time.time() - start

    log_shell_turn(
        {
            "timestamp": now_iso(),
            "hostname": socket.gethostname(),
            "kind": "dispatch",
            "task_chars": len(task),
            "extra_args": args,
            "duration_s": round(duration, 1),
            "exit_code": result.returncode,
        }
    )
    return result.returncode


def run_bash(cmd_string: str) -> int:
    """Run a bash command via subprocess. Handle `cd` specially since it
    can't persist via subprocess; we update Python's cwd directly."""
    cmd_string = cmd_string.strip()
    if cmd_string.startswith("cd "):
        target = cmd_string[3:].strip().strip('"').strip("'")
        target = os.path.expanduser(target)
        try:
            os.chdir(target)
            return 0
        except (OSError, FileNotFoundError) as e:
            print(f"cd: {e}", file=sys.stderr)
            return 1
    if cmd_string == "cd":
        os.chdir(os.path.expanduser("~"))
        return 0
    try:
        result = subprocess.run(cmd_string, shell=True, check=False)
        return result.returncode
    except Exception as e:  # noqa: BLE001
        print(f"bash error: {e}", file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------


HELP_TEXT = """\
Hammerstein Shell — verbs and patterns:

  <plain prose>           Run audit-this-plan on your prose. Default action.
                          Bounded prior-turn context (last 3 turns) is
                          injected automatically so iteration works.

  :a <prose>              Force audit-this-plan template (same as default).
  :s <prose>              scope-this-idea template.
  :w <prose>              is-this-worth-doing template.
  :n <prose>              what-should-we-do-next template.
  :r <prose>              review-from-different-angle template.

  :d <task>               Dispatch to aider via `hd`. Use for actual code
                          work (file edits + git commits). Aider does the
                          execution; Hammerstein's audit pre-flight runs.
  :d --no-audit <task>    Skip the pre-flight audit (trivial tasks).
  :d --provider X <task>  Force a specific provider (claude, deepseek, etc.).

  !<cmd>                  Run a bash command (cd, ls, git, cat, grep, etc.).
                          `cd` persists across turns within the session.

  :context                Show the current rolling-context buffer.
  :clear                  Reset the rolling-context buffer.
  :state                  Show project state file (.hammerstein-state.md)
                          if present in the project root.
  :help, :?               This message.
  :exit, :quit            Quit. Ctrl-D also works.

The rolling context (last 3 turns of prose + response summaries) is the
mechanism that lets you iterate / push back / refine. Each Hammerstein
template call is still a discrete fresh invocation — no conversation
state in the LLM call itself, just operator-iteration background.
"""


def show_context(ctx: RollingContext) -> None:
    if ctx.size() == 0:
        print("(rolling context is empty)")
        return
    print(f"Rolling context — {ctx.size()} turn(s) buffered (cap {ctx.capacity}):")
    for i, (prose, summary) in enumerate(ctx._buf, start=1):
        print(f"\n  Turn {i}:")
        print(f"    operator: {prose[:120]}{'...' if len(prose) > 120 else ''}")
        print(f"    summary : {summary[:200]}{'...' if len(summary) > 200 else ''}")


def get_prompt() -> str:
    """Build the shell prompt: hsh:dirname>"""
    cwd = Path.cwd().name or "/"
    return f"hsh:{cwd}> "


def parse_line(line: str) -> tuple[str, str]:
    """Return (verb, rest) where verb is one of:
        - 'prose'           => default audit on prose
        - 'template:<name>' => run named template
        - 'dispatch'        => :d
        - 'bash'            => !
        - 'context'         => :context
        - 'clear'           => :clear
        - 'state'           => :state
        - 'help'            => :help / :?
        - 'exit'            => :exit / :quit
        - 'unknown:<verb>'  => unknown : verb
    """
    line = line.strip()
    if not line:
        return ("noop", "")
    if line.startswith("!"):
        return ("bash", line[1:].lstrip())
    if line.startswith(":"):
        parts = line[1:].split(None, 1)
        verb = parts[0].lower() if parts else ""
        rest = parts[1] if len(parts) > 1 else ""
        if verb in ("exit", "quit", "q"):
            return ("exit", "")
        if verb in ("help", "?", "h"):
            return ("help", "")
        if verb == "context":
            return ("context", "")
        if verb == "clear":
            return ("clear", "")
        if verb == "state":
            return ("state", "")
        if verb in ("d", "dispatch"):
            return ("dispatch", rest)
        if verb in TEMPLATE_VERBS:
            return (f"template:{TEMPLATE_VERBS[verb]}", rest)
        return (f"unknown:{verb}", rest)
    return ("prose", line)


def main() -> int:
    # Welcome banner
    print("Hammerstein Shell (hsh) — interactive strategic-reasoning environment")
    print("Type :help for commands, :exit or Ctrl-D to quit.")
    print(f"Rolling context capped at {ROLLING_CONTEXT_TURNS} turns.")
    print()

    # readline history (optional; doesn't crash if file is unreadable)
    try:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        if HISTORY_FILE.exists():
            readline.read_history_file(str(HISTORY_FILE))
        readline.set_history_length(1000)
    except OSError:
        pass

    ctx = RollingContext()

    try:
        while True:
            try:
                line = input(get_prompt())
            except EOFError:
                print()  # newline after ^D
                break
            except KeyboardInterrupt:
                # Ctrl-C aborts current input but stays in the shell
                print()
                continue

            verb, rest = parse_line(line)

            if verb == "noop":
                continue
            if verb == "exit":
                break
            if verb == "help":
                print(HELP_TEXT)
                continue
            if verb == "context":
                show_context(ctx)
                continue
            if verb == "clear":
                ctx.clear()
                print("(context cleared)")
                continue
            if verb == "state":
                show_or_edit_state(find_state_file(find_project_root()))
                continue
            if verb == "bash":
                run_bash(rest)
                continue
            if verb == "dispatch":
                if not rest:
                    print("usage: :d <task>  (or :d --provider X <task>)")
                    continue
                # Allow :d --provider X <task> by passing through args
                tokens = shlex.split(rest)
                pass_args: list[str] = []
                while tokens and tokens[0].startswith("--"):
                    flag = tokens.pop(0)
                    if flag in ("--no-audit", "--no-auto-commits", "--architect", "--dry-run"):
                        pass_args.append(flag)
                    elif flag in ("--provider", "--file", "--read"):
                        if not tokens:
                            print(f"flag {flag} requires a value")
                            tokens = []
                            break
                        pass_args.append(flag)
                        pass_args.append(tokens.pop(0))
                    else:
                        # unknown flag — pass through and let hd error
                        pass_args.append(flag)
                task = " ".join(tokens)
                if not task:
                    print("usage: :d <task>")
                    continue
                run_dispatch(task, pass_args)
                continue
            if verb.startswith("template:"):
                template = verb.split(":", 1)[1]
                if not rest:
                    print(f"usage: :{template[:1]} <prose>")
                    continue
                run_template(rest, template, ctx)
                continue
            if verb.startswith("unknown:"):
                bad = verb.split(":", 1)[1]
                print(f"unknown verb :{bad} (try :help)")
                continue
            if verb == "prose":
                # Default action: audit-this-plan on the prose
                run_template(rest, "audit-this-plan", ctx)
                continue

    finally:
        try:
            readline.write_history_file(str(HISTORY_FILE))
        except OSError:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
