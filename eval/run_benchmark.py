#!/usr/bin/env python3
"""Hammerstein v0 benchmark runner.

Reads `eval/BENCHMARK-v0.md`, extracts each non-stub question, dispatches
it across a configurable cell list, writes one response file per
(question, cell), and emits a per-run index plus a summary table for
the operator to score against `eval/BENCHMARK-v0.md`'s rubric.

Run (defaults):
    python eval/run_benchmark.py

Run a subset (e.g. smoke):
    python eval/run_benchmark.py --questions 1 --cells ollama-qwen3-8b openrouter-qwen36-plus

Cells are defined in `_CELLS` below. Add/remove freely; `--cells` filters
by slug. To run the cells against a specific question id, pass
`--questions 1 3 6` or `--questions 1`.

Each call's prompt + response + metadata is written to
`eval/results/<ts>/q<N>-<cell-slug>.md`. The full call log is the
existing JSONL at `logs/hammerstein-calls.jsonl` (the harness already
appends to it).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HARNESS_DIR = REPO_ROOT / "harness"
if str(HARNESS_DIR) not in sys.path:
    sys.path.insert(0, str(HARNESS_DIR))

from hammerstein import (  # noqa: E402
    backends,
    classifier,
    corpus as corpus_mod,
    logger as call_logger,
    prompt as prompt_mod,
)

import importlib.util  # noqa: E402

_CLI_PATH = HARNESS_DIR / "hammerstein.py"
_spec = importlib.util.spec_from_file_location("hammerstein_cli", _CLI_PATH)
assert _spec and _spec.loader
_cli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cli)


@dataclass
class Cell:
    slug: str  # filesystem-safe identifier
    backend: str
    model: str
    mode: str = "default"  # default | no-corpus | corpus-only
    template: str | None = None  # None means classifier-decide


_CELLS: list[Cell] = [
    Cell("ollama-qwen3-8b", "ollama", "qwen3:8b", mode="default"),
    Cell("openrouter-qwen36-plus", "openrouter", "qwen/qwen3.6-plus", mode="default"),
    Cell("ollama-qwen3-8b-no-corpus", "ollama", "qwen3:8b", mode="no-corpus"),
    Cell("ollama-qwen3-8b-corpus-only", "ollama", "qwen3:8b", mode="corpus-only"),
]


@dataclass
class Question:
    id: int
    title: str
    query: str  # may be empty if stubbed


_QUESTION_RE = re.compile(
    r"^## Question (\d+) — (.+?)\n(.*?)(?=^## Question \d+|^---\s*\n## What \"good\"|\Z)",
    re.DOTALL | re.MULTILINE,
)
_QUERY_BLOCK_RE = re.compile(
    r"\*\*Query:\*\*\s*\n+((?:>.*\n?)+)", re.MULTILINE
)
_STUB_RE = re.compile(r"_\[TBD", re.IGNORECASE)


def _extract_query(section_body: str) -> str:
    """Pull the blockquote following **Query:** and strip the > markers."""
    m = _QUERY_BLOCK_RE.search(section_body)
    if not m:
        return ""
    block = m.group(1)
    if _STUB_RE.search(block):
        return ""
    lines: list[str] = []
    for line in block.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(">"):
            lines.append(stripped[1:].strip())
        elif not stripped:
            lines.append("")
    return "\n".join(lines).strip()


def load_questions(path: Path) -> list[Question]:
    raw = path.read_text(encoding="utf-8")
    out: list[Question] = []
    for m in _QUESTION_RE.finditer(raw):
        qid = int(m.group(1))
        title = m.group(2).strip()
        body = m.group(3)
        query = _extract_query(body)
        out.append(Question(id=qid, title=title, query=query))
    return out


def _ts() -> str:
    return time.strftime("%Y-%m-%dT%H%M%SZ", time.gmtime())


def _format_metadata(cell: Cell, question: Question, template: str, retrieved: list[corpus_mod.CorpusEntry], result: backends.CallResult | None, error: str | None) -> str:
    lines = [
        f"# Q{question.id} · cell={cell.slug}",
        "",
        f"- backend: `{cell.backend}`",
        f"- model: `{cell.model}`",
        f"- mode: `{cell.mode}`",
        f"- template: `{template}`",
        f"- retrieved corpus: {', '.join('#' + e.id for e in retrieved) if retrieved else '(none)'}",
    ]
    if result is not None:
        lines += [
            f"- latency_ms: {result.latency_ms}",
            f"- cost_usd: ${result.cost_usd:.5f}",
            f"- prompt_tokens: {result.prompt_tokens}",
            f"- completion_tokens: {result.completion_tokens}",
        ]
    if error:
        lines += [f"- error: {error}"]
    lines += ["", "## Question", "", question.query, "", "## Response", ""]
    return "\n".join(lines)


def run_cell(
    question: Question,
    cell: Cell,
    *,
    out_dir: Path,
    log_path: Path,
) -> tuple[bool, str]:
    """Returns (ok, message)."""
    template_name = cell.template or classifier.classify(question.query)

    system_prompt = prompt_mod.load_system_prompt(_cli.DEFAULT_PROMPT_PATH)
    template_text = (
        None
        if cell.mode == "corpus-only"
        else prompt_mod.load_template(_cli.DEFAULT_TEMPLATES_DIR, template_name)
    )
    if cell.mode == "no-corpus":
        retrieved: list[corpus_mod.CorpusEntry] = []
    else:
        all_entries = corpus_mod.load_corpus(_cli.DEFAULT_CORPUS_DIR)
        retrieved = corpus_mod.retrieve(
            all_entries, question.query, template=template_name, top_k=4
        )

    full_prompt = prompt_mod.assemble_prompt(
        system_prompt=system_prompt,
        template_text=template_text,
        corpus_entries=retrieved,
        query=question.query,
        mode=cell.mode,
    )

    record = call_logger.CallRecord(
        timestamp=call_logger.now_iso(),
        backend=cell.backend,
        model=cell.model,
        system_prompt_version=prompt_mod.SYSTEM_PROMPT_VERSION,
        template=None if cell.mode == "corpus-only" else template_name,
        retrieved_corpus_ids=[e.id for e in retrieved],
        query=question.query,
        mode=cell.mode,
    )

    result: backends.CallResult | None = None
    error: str | None = None
    start = time.perf_counter()
    try:
        result = _cli._dispatch(cell.backend, cell.model, full_prompt)
    except backends.BackendError as exc:
        error = str(exc)
        record.error = error
        record.latency_ms = int((time.perf_counter() - start) * 1000)
    except SystemExit as exc:
        # API key missing or similar — record + skip cell.
        error = f"setup error: {exc}"
        record.error = error
        record.latency_ms = int((time.perf_counter() - start) * 1000)

    if result is not None:
        record.response = result.response
        record.response_length = len(result.response)
        record.latency_ms = result.latency_ms
        record.cost_usd = result.cost_usd

    call_logger.append(record, log_path)

    out_path = out_dir / f"q{question.id:02d}-{cell.slug}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    metadata = _format_metadata(cell, question, template_name, retrieved, result, error)
    response_body = result.response if result else f"_(no response: {error})_"
    out_path.write_text(metadata + response_body + "\n", encoding="utf-8")

    if error:
        return False, error
    return True, ""


def write_summary(out_dir: Path, results: list[dict]) -> None:
    """Compact markdown table summarising the run."""
    lines = [
        f"# Benchmark run · {out_dir.name}",
        "",
        "| Q | cell | template | corpus | latency_ms | cost_usd | status |",
        "| - | ---- | -------- | ------ | ---------- | -------- | ------ |",
    ]
    for r in results:
        lines.append(
            f"| Q{r['qid']} | `{r['cell']}` | `{r['template']}` | "
            f"{r['corpus_count']} | {r['latency_ms']} | "
            f"${r['cost_usd']:.5f} | {r['status']} |"
        )
    lines += [
        "",
        "Score with the rubric in `eval/BENCHMARK-v0.md` § 'Scoring template'.",
        "",
    ]
    (out_dir / "SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")
    (out_dir / "index.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in results) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--benchmark",
        type=Path,
        default=REPO_ROOT / "eval" / "BENCHMARK-v0.md",
    )
    p.add_argument(
        "--questions",
        type=int,
        nargs="*",
        help="Question ids to run. Default: all non-stub questions.",
    )
    p.add_argument(
        "--cells",
        nargs="*",
        help=f"Cell slugs to run. Default: all. Available: "
        f"{[c.slug for c in _CELLS]}",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output dir. Default: eval/results/<timestamp>/",
    )
    p.add_argument(
        "--log",
        type=Path,
        default=REPO_ROOT / "logs" / "hammerstein-calls.jsonl",
    )
    args = p.parse_args(argv)

    questions = load_questions(args.benchmark)
    if args.questions:
        wanted = set(args.questions)
        questions = [q for q in questions if q.id in wanted]
    questions = [q for q in questions if q.query]

    if args.cells:
        cells_by_slug = {c.slug: c for c in _CELLS}
        unknown = [s for s in args.cells if s not in cells_by_slug]
        if unknown:
            print(f"unknown cell slug(s): {unknown}", file=sys.stderr)
            return 2
        cells = [cells_by_slug[s] for s in args.cells]
    else:
        cells = list(_CELLS)

    if not questions:
        print("no questions to run after filtering", file=sys.stderr)
        return 2
    if not cells:
        print("no cells to run after filtering", file=sys.stderr)
        return 2

    out_dir = args.out or (REPO_ROOT / "eval" / "results" / _ts())
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"benchmark run -> {out_dir}", file=sys.stderr)
    print(f"questions: {[q.id for q in questions]}", file=sys.stderr)
    print(f"cells:     {[c.slug for c in cells]}", file=sys.stderr)

    results = []
    for q in questions:
        for cell in cells:
            template = cell.template or classifier.classify(q.query)
            print(f"  Q{q.id} × {cell.slug} (template={template}, mode={cell.mode})...", file=sys.stderr, flush=True)
            ok, msg = run_cell(q, cell, out_dir=out_dir, log_path=args.log)
            log_records = list(_read_last_record(args.log))
            last = log_records[-1] if log_records else {}
            results.append({
                "qid": q.id,
                "cell": cell.slug,
                "backend": cell.backend,
                "model": cell.model,
                "mode": cell.mode,
                "template": template,
                "corpus_count": len(last.get("retrieved_corpus_ids", [])),
                "latency_ms": last.get("latency_ms", 0),
                "cost_usd": last.get("cost_usd", 0.0),
                "status": "ok" if ok else f"error: {msg[:80]}",
            })

    write_summary(out_dir, results)
    print(f"done. summary at {out_dir / 'SUMMARY.md'}", file=sys.stderr)
    return 0


def _read_last_record(log_path: Path):
    """Yield the last record only (cheap; we only call once per cell)."""
    if not log_path.exists():
        return
    last_line = ""
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                last_line = line
    if last_line:
        try:
            yield json.loads(last_line)
        except json.JSONDecodeError:
            return


if __name__ == "__main__":
    raise SystemExit(main())
