"""hd — Hammerstein Dispatch.

Phase 1 of the Continuity Track (ham-013). Thin wrapper that:

1. Takes operator prose as input.
2. (default) Runs the prose through Hammerstein's audit-this-plan template
   for a pre-flight adversarial review, prints it, asks the operator to
   confirm / revise / abort.
3. Dispatches the operator's prose to aider with provider-specific flags
   so aider does the actual file editing, conversation, and git work.
4. Logs the dispatch to ~/.hammerstein/logs/dispatches.jsonl.

State-ownership boundary (load-bearing per Hammerstein's audit
2026-05-05 PM): Hammerstein owns audit/scope/route/dispatch. Aider owns
file editing, conversation state, tool-use loops, git operations. If
this wrapper starts tracking chat history or managing .git directly, it
has crossed into reinventing Claude Code. STOP at that boundary.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Provider routing table.
#
# Each entry maps a routing name (what operator types as `--provider X`) to
# the aider-CLI shape needed to invoke that provider:
#   - model: aider/litellm-format model spec
#   - api_key_env: env var name to read the key from (None = no key needed)
#   - aider_provider: provider name aider expects in `--api-key PROVIDER=KEY`
# ---------------------------------------------------------------------------

PROVIDERS: dict[str, dict] = {
    "openrouter": {
        "model": "openrouter/qwen/qwen3.6-plus",
        "api_key_env": "OPENROUTER_API_KEY",
        "aider_provider": "openrouter",
        "description": "Qwen3.6-plus via OpenRouter (general-purpose, paid).",
    },
    "openrouter-coder": {
        "model": "openrouter/qwen/qwen3-coder-plus",
        "api_key_env": "OPENROUTER_API_KEY",
        "aider_provider": "openrouter",
        "description": "Qwen3-coder-plus via OpenRouter (code-specific, paid).",
    },
    "deepseek": {
        "model": "deepseek/deepseek-chat",
        "api_key_env": "DEEPSEEK_API_KEY",
        "aider_provider": "deepseek",
        "description": "DeepSeek V3.5 via direct API (paid).",
    },
    "claude": {
        "model": "claude-sonnet-4-6",
        "api_key_env": "ANTHROPIC_API_KEY",
        "aider_provider": "anthropic",
        "description": "Claude Sonnet 4.6 via Anthropic API (requires API key, separate from CC subscription).",
    },
    "claude-opus": {
        "model": "claude-opus-4-7",
        "api_key_env": "ANTHROPIC_API_KEY",
        "aider_provider": "anthropic",
        "description": "Claude Opus 4.7 via Anthropic API (high-stakes; requires API key).",
    },
    "ollama": {
        "model": "ollama/qwen3:8b",
        "api_key_env": None,
        "aider_provider": None,
        "description": "Local Ollama (free, offline; quality depends on local model).",
    },
}

DEFAULT_PROVIDER = "openrouter"
DISPATCH_LOG_PATH = Path.home() / ".hammerstein" / "logs" / "dispatches.jsonl"


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


def log_dispatch(record: dict) -> None:
    """Append a dispatch record to the dispatches.jsonl log."""
    DISPATCH_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DISPATCH_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ---------------------------------------------------------------------------
# Audit step
# ---------------------------------------------------------------------------


def run_audit(prose: str) -> int:
    """Shell out to `hammerstein <prose> --template audit-this-plan`.

    Streams stdout/stderr live to the operator's terminal (better UX than
    waiting 30-90s blind). The audit text itself is logged structurally to
    ~/.hammerstein/logs/hammerstein-calls.jsonl by the hammerstein CLI; no
    need to capture it here.

    Returns the exit code. 127 means hammerstein is not on PATH.
    """
    try:
        result = subprocess.run(
            ["hammerstein", prose, "--template", "audit-this-plan"],
            check=False,  # stream live; no capture
        )
    except FileNotFoundError:
        return 127
    return result.returncode


# ---------------------------------------------------------------------------
# Aider invocation
# ---------------------------------------------------------------------------


def build_aider_command(
    prose: str,
    provider: str,
    files: list[str],
    read_files: list[str],
    no_auto_commits: bool,
    architect: bool,
) -> list[str]:
    """Build the aider subprocess invocation.

    Raises RuntimeError if the configured provider needs an API key that's
    missing from the environment. Caller should catch + render a friendly
    error.
    """
    cfg = PROVIDERS[provider]
    cmd: list[str] = ["aider"]
    cmd.extend(["--model", cfg["model"]])
    if cfg["api_key_env"]:
        key = os.environ.get(cfg["api_key_env"])
        if not key:
            raise RuntimeError(
                f"missing {cfg['api_key_env']} for provider '{provider}'. "
                f"set it in ~/.generalstaff/.env (or export it before running hd)."
            )
        cmd.extend(["--api-key", f"{cfg['aider_provider']}={key}"])
    cmd.extend(["--message", prose])
    cmd.extend(["--yes-always", "--exit"])
    if no_auto_commits:
        cmd.append("--no-auto-commits")
    if architect:
        cmd.append("--architect")
    for f in files:
        cmd.extend(["--file", f])
    for r in read_files:
        cmd.extend(["--read", r])
    return cmd


def redact_command_for_display(cmd: list[str]) -> str:
    """Return a printable version of the aider command with the API key masked."""
    out: list[str] = []
    skip_next = False
    for arg in cmd:
        if skip_next:
            # This is the value after --api-key — mask it
            if "=" in arg:
                provider_part, _key = arg.split("=", 1)
                out.append(f"{provider_part}=***REDACTED***")
            else:
                out.append("***REDACTED***")
            skip_next = False
            continue
        if arg == "--api-key":
            skip_next = True
        out.append(arg)
    return " ".join(out)


# ---------------------------------------------------------------------------
# Operator interaction
# ---------------------------------------------------------------------------


def confirm_proceed() -> str:
    """Prompt for Y/n/revise. Returns 'yes', 'no', or 'revise'."""
    while True:
        try:
            ans = input("\nProceed with dispatch? [Y/n/revise]: ").strip().lower()
        except EOFError:
            # Non-interactive — default to no
            print("(no terminal — aborting)")
            return "no"
        if ans in ("", "y", "yes"):
            return "yes"
        if ans in ("n", "no"):
            return "no"
        if ans in ("r", "revise"):
            return "revise"
        print("Please answer y, n, or revise.")


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="hd",
        description=(
            "Hammerstein Dispatch — strategic-reasoning layer + aider executor. "
            "Phase 1 of the Continuity Track (ham-013)."
        ),
    )
    parser.add_argument(
        "prose",
        nargs="+",
        help="The task to dispatch (plain English).",
    )
    parser.add_argument(
        "--provider",
        default=DEFAULT_PROVIDER,
        choices=list(PROVIDERS.keys()),
        help=f"Provider to dispatch through aider. Default: {DEFAULT_PROVIDER}.",
    )
    parser.add_argument(
        "--no-audit",
        action="store_true",
        help="Skip the Hammerstein audit pre-flight (faster, less framing).",
    )
    parser.add_argument(
        "--file",
        action="append",
        default=[],
        help="Editable file passed to aider (--file). Repeatable.",
    )
    parser.add_argument(
        "--read",
        action="append",
        default=[],
        help="Read-only context file passed to aider (--read). Repeatable.",
    )
    parser.add_argument(
        "--no-auto-commits",
        action="store_true",
        help="Pass --no-auto-commits to aider (you commit manually after review).",
    )
    parser.add_argument(
        "--architect",
        action="store_true",
        help="Use aider --architect mode (planning + edit split).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the audit + planned aider invocation; do not execute.",
    )
    parser.add_argument(
        "--list-providers",
        action="store_true",
        help="Show the provider routing table and exit.",
    )

    # Hack: support `--list-providers` without requiring a positional `prose` arg.
    if "--list-providers" in sys.argv:
        print(f"{'Provider':<22} {'Model':<48} {'Description'}")
        print("-" * 110)
        for name, cfg in PROVIDERS.items():
            print(f"{name:<22} {cfg['model']:<48} {cfg['description']}")
        return 0

    args = parser.parse_args()
    prose = " ".join(args.prose).strip()
    if not prose:
        print("error: empty prose. usage: hd \"<task>\"", file=sys.stderr)
        return 2

    # Validate the chosen provider's API key is available before doing anything else.
    cfg = PROVIDERS[args.provider]
    if cfg["api_key_env"] and not os.environ.get(cfg["api_key_env"]):
        print(
            f"error: missing {cfg['api_key_env']} for provider '{args.provider}'.",
            file=sys.stderr,
        )
        print(
            "set it in ~/.generalstaff/.env (or export it before running hd).",
            file=sys.stderr,
        )
        return 2

    # ------------------------------------------------------------------ audit
    audit_skipped = args.no_audit

    if not args.no_audit:
        print("Running Hammerstein audit on the dispatch prose...\n")
        audit_rc = run_audit(prose)
        if audit_rc == 127:
            print(
                "warning: `hammerstein` not on PATH — skipping audit and proceeding without it.",
                file=sys.stderr,
            )
            audit_skipped = True
        else:
            # If --dry-run, stop here after the audit
            if args.dry_run:
                print("\n--- DRY RUN ---")
                cmd = build_aider_command(
                    prose,
                    args.provider,
                    args.file,
                    args.read,
                    args.no_auto_commits,
                    args.architect,
                )
                print("Would run:", redact_command_for_display(cmd))
                return 0
            choice = confirm_proceed()
            if choice == "no":
                print("Dispatch aborted.")
                return 0
            if choice == "revise":
                try:
                    new_prose = input("New task description: ").strip()
                except EOFError:
                    new_prose = ""
                if new_prose:
                    prose = new_prose
                    print("\nRe-running audit on revised prose...\n")
                    audit_rc = run_audit(prose)
                    choice = confirm_proceed()
                    if choice != "yes":
                        print("Dispatch aborted.")
                        return 0
                else:
                    print("(empty input — keeping original prose)")
            # choice == "yes" falls through to dispatch

    # --------------------------------------------------------------- dispatch
    try:
        cmd = build_aider_command(
            prose,
            args.provider,
            args.file,
            args.read,
            args.no_auto_commits,
            args.architect,
        )
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    if args.dry_run:
        print("\n--- DRY RUN ---")
        print("Would run:", redact_command_for_display(cmd))
        return 0

    print(
        f"\nDispatching to aider via {args.provider} ({cfg['model']})...\n"
        + "-" * 60
    )
    start = time.time()
    try:
        result = subprocess.run(cmd, check=False)  # stream stdout/stderr live
        rc = result.returncode
    except FileNotFoundError:
        print("error: aider is not installed or not on PATH.", file=sys.stderr)
        print(
            "install on Mac: `brew install pipx python@3.12 && "
            "pipx install aider-chat --python /opt/homebrew/bin/python3.12`",
            file=sys.stderr,
        )
        return 3
    duration = time.time() - start

    log_dispatch(
        {
            "timestamp": now_iso(),
            "hostname": socket.gethostname(),
            "prose": prose,
            "provider": args.provider,
            "model": cfg["model"],
            "audit_skipped": audit_skipped,
            "duration_s": round(duration, 1),
            "exit_code": rc,
            "files": args.file,
            "read_files": args.read,
            "no_auto_commits": args.no_auto_commits,
            "architect": args.architect,
        }
    )

    print("-" * 60)
    print(
        f"Dispatch complete in {duration:.1f}s "
        f"(provider={args.provider}, exit={rc}). "
        f"Logged to {DISPATCH_LOG_PATH}."
    )
    return rc


if __name__ == "__main__":
    sys.exit(main())
