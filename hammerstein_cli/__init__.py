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
        None,
        "--model",
        help=(
            "Backend or backend:model spec. Default: HAMMERSTEIN_DEFAULT_MODEL "
            "env var if set, else ollama:qwen3:8b."
        ),
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
    context_mode: Optional[str] = typer.Option(
        None,
        "--context",
        help=(
            "Project context injection mode (none | minimal). If omitted, a "
            "template-level default may apply (audits default to minimal; "
            "pure queries default to none)."
        ),
    ),
    project_root: Optional[Path] = typer.Option(
        None,
        "--project-root",
        help="Override repo detection: build context from this project root path.",
    ),
    context_file: Optional[Path] = typer.Option(
        None,
        "--context-file",
        help=(
            "Explicit context preamble file to inject (preferred). If omitted, "
            "minimal mode may auto-discover a state file at project root. "
            "Refuses paths outside the project root."
        ),
    ),
    image: Optional[str] = typer.Option(
        None,
        "--image",
        help=(
            "Path to an image file (PNG/JPG/JPEG/WebP) to include as multimodal "
            "input. Only valid with --template audit-this-visual."
        ),
    ),
    backend_tier: Optional[str] = typer.Option(
        None,
        "--backend-tier",
        help=(
            "Explicit backend tier for vision-Hammerstein audits. 'free' routes "
            "through the free vision pool (Gemini Flash via OpenRouter); 'paid' "
            "forces the paid pool default. Default is None (use the "
            "providers.yaml fallback chain)."
        ),
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
    if backend_tier is not None and backend_tier not in ("free", "paid"):
        typer.echo(
            f"--backend-tier must be 'free' or 'paid', got {backend_tier!r}",
            err=True,
        )
        raise typer.Exit(code=2)
    if image is not None:
        if template != "audit-this-visual":
            typer.echo(
                "--image is only supported with --template audit-this-visual; "
                "use --template audit-this-visual to opt in",
                err=True,
            )
            raise typer.Exit(code=2)
        if not Path(image).is_file():
            typer.echo(f"--image path is not a readable file: {image!r}", err=True)
            raise typer.Exit(code=2)
    code = run(
        query,
        model_spec=model,
        template_name=template,
        no_corpus=no_corpus,
        corpus_only=corpus_only,
        top_k=top_k,
        show_prompt=show_prompt,
        log_path=log,
        context_mode=context_mode,
        project_root=project_root,
        context_file=context_file,
        image=image,
        backend_tier=backend_tier,
    )
    raise typer.Exit(code=code)


def main() -> None:
    typer.run(cli)


