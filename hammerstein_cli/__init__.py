from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Optional

import typer

from hammerstein.cli import DEFAULT_LOG_PATH, run
from hammerstein import classifier


def _pkg_version() -> str:
    try:
        return version("hammerstein-ai")
    except PackageNotFoundError:
        return "0.0.0"


def _templates_help() -> str:
    names = ", ".join(classifier.TEMPLATES)
    return f"Available templates: {names}."

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(_pkg_version())
        raise typer.Exit(code=0)


def cli(
    query: str = typer.Argument(..., help="Strategic-reasoning query."),
    model: Optional[str] = typer.Option(
        None, "--model", help="Backend or backend:model spec (default: ollama:qwen3:8b)."
    ),
    template: str = typer.Option(
        "auto",
        "--template",
        help=(
            "Few-shot template name. Use 'auto' to classify by query shape. "
            f"Templates: auto, {', '.join(classifier.TEMPLATES)}."
        ),
        show_default=True,
    ),
    top_k: int = typer.Option(
        4, "--top-k", min=0, help="Corpus entries to retrieve.", show_default=True
    ),
    no_corpus: bool = typer.Option(
        False,
        "--no-corpus",
        help="Ablation: skip corpus retrieval (prompt+template only).",
    ),
    corpus_only: bool = typer.Option(
        False,
        "--corpus-only",
        help="Ablation: minimal system prompt + corpus only (drop template).",
    ),
    show_prompt: bool = typer.Option(
        False,
        "--show-prompt",
        help="Print the assembled prompt and exit. Skips inference.",
    ),
    log: Path = typer.Option(
        DEFAULT_LOG_PATH, "--log", help="Path to JSONL call log.", show_default=True
    ),
    version: bool = typer.Option(
        False,
        "--version",
        help="Print version and exit.",
        is_eager=True,
        callback=_version_callback,
    ),
) -> None:
    """Hammerstein is a minimal strategic-reasoning harness: system prompt + few-shot template + small retrieved corpus.

    README: https://github.com/rayweiss/hammerstein
    """
    code = run(
        query,
        model_spec=model,
        template_name=template,
        no_corpus=no_corpus,
        corpus_only=corpus_only,
        top_k=top_k,
        show_prompt=show_prompt,
        log_path=log,
    )
    raise typer.Exit(code=code)


def main() -> None:
    typer.run(cli)


