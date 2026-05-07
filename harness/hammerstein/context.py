"""Project context injection (v0).

Design constraints:
- Explicit and bounded (context injection must never silently bloat prompts).
- Safe by default: abort injection on possible secret signals (no redaction-by-regex).
- Minimal only in v0: no git diff/log/tree/caching.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

ContextMode = Literal["none", "minimal"]


@dataclass(frozen=True)
class ContextDisabled(Exception):
    reason: str


_AUTO_STATE_FILENAMES = (".hammerstein-state.md", "hammerstein_state.md")

# Never read these by accident.
_DENYLIST_NAME_RE = re.compile(
    r"(?i)(^\.env$|\.pem$|\.p12$|\.keystore$|id_rsa|credentials.*\.json$|secret|token|api[_-]?key)"
)

# Conservative "possible secret" signals. v0 prefers false positives (abort)
# over false negatives (leak).
_SECRET_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),  # OpenAI-style
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),  # GitHub PAT
    re.compile(r"\bAIza[0-9A-Za-z\-_]{20,}\b"),  # Google API key
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),  # AWS access key id
    re.compile(r"\bASIA[0-9A-Z]{16}\b"),  # AWS temp access key id
    re.compile(r"\b(xox[baprs]-[A-Za-z0-9-]{10,})\b"),  # Slack token
    re.compile(r"\b-----BEGIN [A-Z ]+PRIVATE KEY-----\b"),
    # High-entropy-ish blobs (hex/base64) with enough length to be a credential.
    re.compile(r"\b[0-9a-fA-F]{48,}\b"),
    re.compile(r"\b[A-Za-z0-9+/]{60,}={0,2}\b"),
]


def _run_git(args: list[str], cwd: Path) -> str | None:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def detect_git_root(cwd: Path) -> Path | None:
    out = _run_git(["rev-parse", "--show-toplevel"], cwd=cwd)
    if not out:
        return None
    try:
        return Path(out).resolve()
    except OSError:
        return None


def _git_identity(repo_root: Path) -> dict[str, str]:
    remote = _run_git(["remote", "get-url", "origin"], cwd=repo_root) or "none"
    branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root) or "unknown"
    head = _run_git(["rev-parse", "--short", "HEAD"], cwd=repo_root) or "unknown"
    status = _run_git(["status", "--porcelain"], cwd=repo_root)
    dirty = "true" if (status is not None and status.strip()) else "false"
    return {"remote": remote, "branch": branch, "head": head, "dirty": dirty}


def _read_capped(path: Path, cap: int) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    text = text.strip()
    if len(text) <= cap:
        return text
    # Prefer whole-line truncation.
    cut = text[:cap]
    if "\n" in cut:
        cut = cut.rsplit("\n", 1)[0]
    return cut.rstrip()


def _contains_possible_secret(text: str) -> bool:
    if not text:
        return False
    for pat in _SECRET_PATTERNS:
        if pat.search(text):
            return True
    return False


def _guard_file_ok(path: Path) -> None:
    name = path.name
    if _DENYLIST_NAME_RE.search(name):
        raise ContextDisabled(f"denylisted filename '{name}'")
    # Refuse symlinks to avoid surprising exfiltration outside root.
    if path.is_symlink():
        raise ContextDisabled(f"symlink refused '{name}'")


def _pick_project_root(project_root: Path | None) -> Path | None:
    if project_root is not None:
        return project_root.resolve()
    # Prefer git root if available.
    cwd = Path.cwd()
    return detect_git_root(cwd)


def _discover_state_file(root: Path) -> Path | None:
    for name in _AUTO_STATE_FILENAMES:
        p = root / name
        if p.exists() and p.is_file():
            return p
    return None


def build_project_context_preamble(
    *,
    mode: ContextMode,
    project_root: Path | None,
    context_file: Path | None,
) -> str:
    if mode == "none":
        return ""
    if mode != "minimal":
        raise ContextDisabled(f"unknown context mode '{mode}'")

    root = _pick_project_root(project_root)
    if root is None or not root.exists():
        raise ContextDisabled("no git repo detected (or project root missing)")

    # Resolve context file.
    state_path: Path | None = None
    if context_file is not None:
        state_path = context_file.resolve()
    else:
        state_path = _discover_state_file(root)

    # Read high-signal docs.
    doc_caps = {
        "MISSION.md": 600,
        "CLAUDE.md": 600,
        "AGENTS.md": 600,
        "README.md": 600,
    }
    total_docs_cap = 1600
    state_cap = 800
    hard_cap = 2200

    identity = _git_identity(root)
    repo_root_basename = root.name

    state_text = ""
    if state_path is not None:
        # Must be within root unless explicitly provided.
        if context_file is None:
            # auto-discovered; already under root
            pass
        else:
            try:
                state_path.relative_to(root)
            except ValueError:
                raise ContextDisabled("context file outside project root refused")
        _guard_file_ok(state_path)
        state_text = _read_capped(state_path, state_cap)

    docs: list[tuple[str, str]] = []
    remaining = total_docs_cap
    for fname in ("MISSION.md", "CLAUDE.md", "AGENTS.md", "README.md"):
        p = root / fname
        if not p.exists() or not p.is_file():
            continue
        _guard_file_ok(p)
        cap = min(doc_caps[fname], remaining)
        if cap <= 0:
            break
        t = _read_capped(p, cap)
        if not t:
            continue
        docs.append((fname, t))
        remaining -= len(t)
        if remaining <= 0:
            break

    # Secret-scan everything we might inject.
    combined_for_scan = "\n".join(
        [
            state_text,
            *(t for _, t in docs),
            identity.get("remote", ""),
        ]
    )
    if _contains_possible_secret(combined_for_scan):
        raise ContextDisabled("possible secret detected")

    parts: list[str] = []
    parts.append("[PROJECT_CONTEXT mode=minimal]")
    parts.append(f"repo_root: {repo_root_basename}")
    parts.append(f"remote: {identity['remote']}")
    parts.append(f"branch: {identity['branch']}")
    parts.append(f"head: {identity['head']}")
    parts.append(f"dirty: {identity['dirty']}")
    parts.append("")

    parts.append("## State (operator)")
    parts.append(state_text if state_text else "(none)")
    parts.append("")

    for fname, text in docs:
        parts.append(f"## {fname}")
        parts.append(text)
        parts.append("")

    parts.append("[/PROJECT_CONTEXT]")
    preamble = "\n".join(parts).rstrip()

    if len(preamble) > hard_cap:
        # v0 should never hit this due to caps, but keep a hard guardrail.
        preamble = preamble[:hard_cap].rstrip()

    # Extra paranoia: avoid leaking the absolute path.
    if str(root) in preamble:
        preamble = preamble.replace(str(root), repo_root_basename)

    return preamble

