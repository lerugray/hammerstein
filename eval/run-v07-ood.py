#!/usr/bin/env python3
"""Hammerstein v0.7 OOD stress test — cell runner.

Runs 4 cells × 8 questions from QSET-v0.7-OOD.md.

Cells:
  - or-sonnet-raw        : Claude Sonnet 4.6 via OR, no framework (raw baseline)
  - or-sonnet-ham        : Claude Sonnet 4.6 via OR + full Hammerstein wrap
  - rp-7b-raw            : Qwen2.5-7B-Instruct via RunPod pod (adapter disabled)
  - rp-7b-ham            : Qwen2.5-7B-Instruct + hammerstein-7b-lora via RunPod pod

RunPod cells require POD_ENDPOINT env var (the pod's public HTTP endpoint).
If not set, those cells are skipped with a logged error.

Output: eval/results/<run-name>/ one markdown file per (question, cell).
Same format as run_benchmark.py for compatibility with judge_pairs.py.

Usage:
    source ~/.generalstaff/.env
    export POD_ENDPOINT=<pod-ip:port>   # e.g. 12.34.56.78:8080
    python eval/run-v07-ood.py --run v07-ood-2026-05-21
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from importlib import resources as importlib_resources
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
from hammerstein.cli import _dispatch  # noqa: E402

QSET_PATH = REPO_ROOT / "eval" / "QSET-v0.7-OOD.md"

OR_URL = "https://openrouter.ai/api/v1/chat/completions"


# ---------------------------------------------------------------------------
# Resource helpers (mirrors run_benchmark.py)
# ---------------------------------------------------------------------------

def _load_system_prompt() -> str:
    return prompt_mod.load_system_prompt_resource(
        importlib_resources.files("prompts").joinpath("SYSTEM-PROMPT.md")
    )


def _load_template(template_name: str) -> str:
    return prompt_mod.load_template_resource(
        importlib_resources.files("prompts.templates").joinpath(f"{template_name}.md")
    )


def _load_all_corpus() -> list[corpus_mod.CorpusEntry]:
    return corpus_mod.load_corpus(importlib_resources.files("corpus.entries"))


# ---------------------------------------------------------------------------
# Question parsing — QSET-v0.7-OOD.md uses a slightly simpler format
# ---------------------------------------------------------------------------

@dataclass
class Question:
    id: int
    title: str
    domain: str
    query: str


_Q_RE = re.compile(
    r"^## Question (\d+) — (.+?)\n(.*?)(?=^## Question \d+|^---\s*\n## What|\Z)",
    re.DOTALL | re.MULTILINE,
)
_DOMAIN_RE = re.compile(r"\*\*Domain:\*\*\s*(.+)")
_QUERY_RE = re.compile(r"\*\*Query:\*\*\s*\n+((?:>.*\n?)+)", re.MULTILINE)


def _strip_blockquote(block: str) -> str:
    lines = []
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
    for m in _Q_RE.finditer(raw):
        qid = int(m.group(1))
        title = m.group(2).strip()
        body = m.group(3)
        domain_m = _DOMAIN_RE.search(body)
        domain = domain_m.group(1).strip() if domain_m else ""
        query_m = _QUERY_RE.search(body)
        query = _strip_blockquote(query_m.group(1)) if query_m else ""
        if query:
            out.append(Question(id=qid, title=title, domain=domain, query=query))
    return out


# ---------------------------------------------------------------------------
# RunPod cell: POST to pod HTTP endpoint
# ---------------------------------------------------------------------------

def _pod_request(endpoint: str, cell_name: str, question: str) -> tuple[str, float, str | None]:
    """POST to pod inference server. Returns (response, latency_ms, error|None)."""
    url = f"http://{endpoint}/generate"
    payload = json.dumps({"cell": cell_name, "question": question}).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    start = time.perf_counter()
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read())
            elapsed_ms = (time.perf_counter() - start) * 1000
            return data.get("response", ""), elapsed_ms, None
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            if e.code == 429 and attempt < 2:
                time.sleep(15 * (2 ** attempt))
                continue
            return "", 0.0, f"HTTP {e.code}: {body[:200]}"
        except Exception as e:
            if attempt < 2:
                time.sleep(5)
                continue
            return "", 0.0, str(e)
    return "", 0.0, "max retries"


# ---------------------------------------------------------------------------
# Cell definitions
# ---------------------------------------------------------------------------

@dataclass
class Cell:
    slug: str
    kind: str   # "or-raw" | "or-ham" | "pod"
    model: str


CELLS = [
    Cell("or-sonnet-raw",   "or-raw",  "anthropic/claude-sonnet-4.6"),
    Cell("or-sonnet-ham",   "or-ham",  "anthropic/claude-sonnet-4.6"),
    Cell("rp-7b-raw",       "pod",     "rp-7b-raw"),
    Cell("rp-7b-ham",       "pod",     "rp-7b-ham"),
]


# ---------------------------------------------------------------------------
# Cell runner
# ---------------------------------------------------------------------------

def _ts() -> str:
    return time.strftime("%Y-%m-%dT%H%M%SZ", time.gmtime())


def run_cell(
    question: Question,
    cell: Cell,
    *,
    out_dir: Path,
    log_path: Path,
    or_key: str,
    pod_endpoint: str | None,
) -> tuple[bool, float, str]:
    """Run one cell × question. Returns (ok, cost_usd, error_msg)."""

    response_text = ""
    cost_usd = 0.0
    latency_ms = 0
    prompt_tokens = 0
    completion_tokens = 0
    error: str | None = None
    template_name = "unknown"
    retrieved: list[corpus_mod.CorpusEntry] = []

    if cell.kind == "pod":
        if not pod_endpoint:
            error = "POD_ENDPOINT not set — skipping 7B cell"
        else:
            resp, lat, err = _pod_request(pod_endpoint, cell.model, question.query)
            latency_ms = int(lat)
            if err:
                error = err
            else:
                response_text = resp
    elif cell.kind == "or-raw":
        # Raw frontier: no framework, bare question
        payload = json.dumps({
            "model": cell.model,
            "messages": [{"role": "user", "content": question.query}],
            "temperature": 0,
            "max_tokens": 4096,
        }).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {or_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://hammerstein.ai",
            "X-Title": "hammerstein-benchmark-v07",
        }
        start = time.perf_counter()
        for attempt in range(4):
            try:
                req = urllib.request.Request(OR_URL, data=payload, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=180) as resp:
                    data = json.loads(resp.read())
                latency_ms = int((time.perf_counter() - start) * 1000)
                response_text = data["choices"][0]["message"]["content"] or ""
                usage = data.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                cost_info = data.get("usage", {})
                # OR may return cost directly
                cost_usd = float(data.get("x_groq", {}).get("usage", {}).get("total_time", 0)) * 0 or 0.0
                # Estimate: Sonnet raw ~$0.003/1k input + $0.015/1k output
                cost_usd = (prompt_tokens / 1000 * 0.003) + (completion_tokens / 1000 * 0.015)
                break
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", errors="replace")
                if e.code == 429 and attempt < 3:
                    wait = 10 * (2 ** attempt)
                    print(f"    429 on {cell.slug} Q{question.id} attempt {attempt+1}, sleeping {wait}s", file=sys.stderr)
                    time.sleep(wait)
                    continue
                error = f"HTTP {e.code}: {body[:200]}"
                break
            except Exception as e:
                error = str(e)
                break
    elif cell.kind == "or-ham":
        # Hammerstein-on-frontier: full system prompt + corpus + template
        try:
            template_name = cell.kind or classifier.classify(question.query)
            template_name = classifier.classify(question.query)
            system_prompt = _load_system_prompt()
            template_text = _load_template(template_name)
            all_entries = _load_all_corpus()
            retrieved = corpus_mod.retrieve(all_entries, question.query, template=template_name, top_k=4)
            full_prompt = prompt_mod.assemble_prompt(
                system_prompt=system_prompt,
                template_text=template_text,
                corpus_entries=retrieved,
                query=question.query,
                mode="default",
            )
            start = time.perf_counter()
            result: backends.CallResult | None = None
            for attempt in range(4):
                try:
                    result = _dispatch("openrouter", cell.model, full_prompt, timeout_seconds=180)
                    break
                except backends.RateLimitError:
                    if attempt < 3:
                        wait = 10 * (2 ** attempt)
                        print(f"    429 on {cell.slug} Q{question.id} attempt {attempt+1}, sleeping {wait}s", file=sys.stderr)
                        time.sleep(wait)
                    else:
                        error = "rate-limit after 4 attempts"
                except backends.BackendError as exc:
                    error = str(exc)
                    break
            if result:
                response_text = result.response
                latency_ms = result.latency_ms
                cost_usd = result.cost_usd
                prompt_tokens = result.prompt_tokens
                completion_tokens = result.completion_tokens
        except Exception as e:
            error = str(e)

    # Write result file
    out_path = out_dir / f"q{question.id:02d}-{cell.slug}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    corpus_ids = ", ".join("#" + e.id for e in retrieved) if retrieved else "(none)"
    metadata_lines = [
        f"# Q{question.id} · cell={cell.slug}",
        "",
        f"- backend: `{cell.kind}`",
        f"- model: `{cell.model}`",
        f"- domain: {question.domain}",
        f"- template: `{template_name}`",
        f"- retrieved corpus: {corpus_ids}",
        f"- latency_ms: {latency_ms}",
        f"- cost_usd: ${cost_usd:.5f}",
        f"- prompt_tokens: {prompt_tokens}",
        f"- completion_tokens: {completion_tokens}",
    ]
    if error:
        metadata_lines.append(f"- error: {error}")
    metadata_lines += ["", "## Question", "", question.query, "", "## Response", ""]
    body = response_text if response_text else f"_(no response: {error})_"
    out_path.write_text("\n".join(metadata_lines) + body + "\n", encoding="utf-8")

    if error:
        return False, cost_usd, error
    return True, cost_usd, ""


# ---------------------------------------------------------------------------
# Summary writer
# ---------------------------------------------------------------------------

def write_summary(out_dir: Path, results: list[dict], total_cost: float) -> None:
    lines = [
        f"# v0.7 OOD run summary · {out_dir.name}",
        "",
        f"Total estimated cost: ${total_cost:.4f}",
        "",
        "| Q | domain | cell | latency_ms | cost_usd | status |",
        "| - | ------ | ---- | ---------- | -------- | ------ |",
    ]
    for r in results:
        lines.append(
            f"| Q{r['qid']} | {r['domain'][:20]} | `{r['cell']}` | "
            f"{r['latency_ms']} | ${r['cost_usd']:.5f} | {r['status']} |"
        )
    (out_dir / "SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")
    (out_dir / "index.jsonl").write_text(
        "\n".join(json.dumps(r) for r in results) + "\n", encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", default=None, help="Run name (subdir under eval/results/)")
    p.add_argument("--questions", type=int, nargs="*", default=None)
    p.add_argument("--cells", nargs="*", default=None)
    p.add_argument("--pod-endpoint", default=None)
    args = p.parse_args(argv)

    or_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not or_key.startswith("sk-or-"):
        print("ERR: OPENROUTER_API_KEY not set or malformed", file=sys.stderr)
        return 1

    pod_endpoint = args.pod_endpoint or os.environ.get("POD_ENDPOINT", "").strip() or None

    questions = load_questions(QSET_PATH)
    if args.questions:
        wanted = set(args.questions)
        questions = [q for q in questions if q.id in wanted]
    if not questions:
        print("no questions loaded", file=sys.stderr)
        return 2

    cells = CELLS
    if args.cells:
        slugs = set(args.cells)
        cells = [c for c in CELLS if c.slug in slugs]
    if not cells:
        print("no cells selected", file=sys.stderr)
        return 2

    run_name = args.run or f"v07-ood-{time.strftime('%Y-%m-%dT%H%M%SZ', time.gmtime())}"
    out_dir = REPO_ROOT / "eval" / "results" / run_name
    out_dir.mkdir(parents=True, exist_ok=True)

    log_path = REPO_ROOT / "logs" / "hammerstein-calls.jsonl"

    print(f"v0.7 OOD run -> {out_dir}", file=sys.stderr)
    print(f"questions: {[q.id for q in questions]}", file=sys.stderr)
    print(f"cells:     {[c.slug for c in cells]}", file=sys.stderr)
    print(f"pod_endpoint: {pod_endpoint or 'NOT SET — 7B cells will error'}", file=sys.stderr)

    run_results = []
    total_cost = 0.0

    for q in questions:
        for cell in cells:
            print(f"  Q{q.id} × {cell.slug} [{q.domain}]...", file=sys.stderr, flush=True)
            ok, cost, err = run_cell(
                q, cell,
                out_dir=out_dir,
                log_path=log_path,
                or_key=or_key,
                pod_endpoint=pod_endpoint,
            )
            total_cost += cost
            run_results.append({
                "qid": q.id,
                "domain": q.domain,
                "cell": cell.slug,
                "model": cell.model,
                "cost_usd": cost,
                "latency_ms": 0,  # filled from file if needed
                "status": "ok" if ok else f"error: {err[:80]}",
            })
            print(f"    -> {'ok' if ok else 'ERR: '+err[:60]} cost=${cost:.5f}", file=sys.stderr)

    write_summary(out_dir, run_results, total_cost)
    print(f"\ndone. total_cost=${total_cost:.4f}", file=sys.stderr)
    print(f"summary at {out_dir / 'SUMMARY.md'}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
