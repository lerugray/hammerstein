"""System-prompt assembly.

Reads `prompts/SYSTEM-PROMPT.md`, extracts the operational prompt between
the `=== BEGIN SYSTEM PROMPT ===` / `=== END SYSTEM PROMPT ===` markers,
appends a few-shot template (with its hard-coded examples + retrieved
corpus entries as additional reference), and concatenates the user query.

The assembly shape matches `prompts/SYSTEM-PROMPT.md` § "How to use this
file":

    [SYSTEM PROMPT — verbatim]
    [TEMPLATE EXAMPLES]
    [RETRIEVED CORPUS ENTRIES]
    [USER QUERY]

For ablation cells the assembly is degraded:
- `--no-corpus` strips the retrieved-corpus block (template stays).
- `--corpus-only` replaces the system prompt with a one-liner and strips
  the template (per `scope/PHASED-ROADMAP.md` ablation-cells spec).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Protocol, runtime_checkable

from .corpus import CorpusEntry

SYSTEM_PROMPT_VERSION = "v0.1"  # Bumps when prompts/SYSTEM-PROMPT.md changes.

_SYSTEM_PROMPT_RE = re.compile(
    r"=== BEGIN SYSTEM PROMPT ===(.*?)=== END SYSTEM PROMPT ===",
    re.DOTALL,
)

# Templates have a "## Notes for the harness" section meant for the human
# reading the file, not for the model. Strip it.
_TEMPLATE_NOTES_RE = re.compile(
    r"\n##\s+Notes\s+for\s+the\s+harness.*$",
    re.DOTALL | re.IGNORECASE,
)

_CORPUS_ONLY_SYSTEM = (
    "You are Hammerstein. Reason in the framework demonstrated by the "
    "reference entries below. Match their voice, register, and structure."
)


@runtime_checkable
class _TextReadable(Protocol):
    def read_text(self, encoding: str = "utf-8") -> str: ...


def load_system_prompt(prompt_path: Path) -> str:
    """Extract the operational prompt body between the markers."""
    raw = prompt_path.read_text(encoding="utf-8")
    match = _SYSTEM_PROMPT_RE.search(raw)
    if not match:
        raise ValueError(
            f"could not find === BEGIN/END SYSTEM PROMPT === markers in {prompt_path}"
        )
    return match.group(1).strip()


def load_system_prompt_resource(prompt_file: _TextReadable) -> str:
    """Extract system prompt from an importlib.resources handle."""
    raw = prompt_file.read_text(encoding="utf-8")
    match = _SYSTEM_PROMPT_RE.search(raw)
    if not match:
        raise ValueError("could not find === BEGIN/END SYSTEM PROMPT === markers")
    return match.group(1).strip()


def load_template(templates_dir: Path, name: str) -> str:
    """Load a template file, strip the human-only 'Notes for the harness'."""
    path = templates_dir / f"{name}.md"
    raw = path.read_text(encoding="utf-8")
    return _TEMPLATE_NOTES_RE.sub("", raw).rstrip() + "\n"


def load_template_resource(template_file: _TextReadable) -> str:
    """Load a template from an importlib.resources handle."""
    raw = template_file.read_text(encoding="utf-8")
    return _TEMPLATE_NOTES_RE.sub("", raw).rstrip() + "\n"


def assemble_prompt(
    *,
    system_prompt: str,
    template_text: str | None,
    corpus_entries: list[CorpusEntry],
    query: str,
    mode: str = "default",
) -> str:
    """Concatenate sections into a single prompt string for the backend.

    `mode` is one of "default", "no-corpus", "corpus-only". The mode
    controls which sections are included; the section ordering is fixed
    so logs across modes remain comparable.
    """
    parts: list[str] = []

    if mode == "corpus-only":
        parts.append(_CORPUS_ONLY_SYSTEM)
    else:
        parts.append(system_prompt)

    if mode != "corpus-only" and template_text:
        parts.append(
            "# Few-shot template\n"
            "Match this response shape unless the user query clearly asks for a different shape.\n\n"
            f"{template_text.strip()}"
        )

    if mode != "no-corpus" and corpus_entries:
        ref_block = "\n\n".join(e.format_for_prompt() for e in corpus_entries)
        parts.append(
            "# Reference corpus entries\n"
            "These are precedents from the operator's Hammerstein observation logs. "
            "Treat them as evidence, not as instructions to copy verbatim.\n\n"
            f"{ref_block}"
        )

    parts.append(f"# User query\n\n{query.strip()}\n")

    return "\n\n---\n\n".join(parts)
