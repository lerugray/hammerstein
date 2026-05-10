#!/usr/bin/env python3
"""LLM-judge layer for the Hammerstein v0 benchmark.

Reads response files from a benchmark run dir, pairs raw-frontier with
Hammerstein-on-frontier per (question, frontier-family), and asks
blind LLM judges to score each pair on the BENCHMARK-v0.md rubric
(framework-fidelity / usefulness / voice-match) plus overall
preference. Position-bias mitigation: randomize which side gets A vs
B per pair (judge doesn't see which response is raw vs Hammerstein).

Run:
    source ~/.generalstaff/.env
    python eval/judge_pairs.py --run benchmark-v0-full
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_ROOT = REPO_ROOT / "eval" / "results"

OR_URL = "https://openrouter.ai/api/v1/chat/completions"

# Judge models (different from cell models to avoid self-judging)
JUDGES = [
    "anthropic/claude-opus-4.7",       # paid, strong reasoning
    "openai/gpt-5",                    # paid, different vendor
    "anthropic/claude-sonnet-4.6",     # paid, fallback when opus returns empty (observed Q5/Q6)
    "deepseek/deepseek-chat",          # 4th vendor (DeepSeek) — Caveat 3 judge-bias robustness
]

# Frontier families being judged (each pairs raw vs Hammerstein)
FAMILIES = [
    ("or-claude-opus-raw", "or-claude-opus", "Claude Opus 4.7"),
    ("or-claude-sonnet-raw", "or-claude-sonnet", "Claude Sonnet 4.6"),
    ("or-gpt5-raw", "or-gpt5", "GPT-5"),
]

# Ablation families: full Hammerstein vs prompt-only vs corpus-only (Caveat 2).
# Left cell = "baseline" (A in pair), right cell = "Hammerstein full" (B in pair).
# a_is_raw=True semantics reused: left side is the "lesser" cell being compared
# against the full Hammerstein (right side). Win counts reflect how often
# full Hammerstein wins over the ablated variant.
ABLATION_FAMILIES = [
    ("or-claude-sonnet-no-corpus", "or-claude-sonnet", "Sonnet: prompt-only vs full"),
    ("or-claude-sonnet-corpus-only", "or-claude-sonnet", "Sonnet: corpus-only vs full"),
    # v0.2: ablation extended to Opus + GPT-5 to test cross-family generalization
    ("or-claude-opus-no-corpus", "or-claude-opus", "Opus: prompt-only vs full"),
    ("or-claude-opus-corpus-only", "or-claude-opus", "Opus: corpus-only vs full"),
    ("or-gpt5-no-corpus", "or-gpt5", "GPT-5: prompt-only vs full"),
    ("or-gpt5-corpus-only", "or-gpt5", "GPT-5: corpus-only vs full"),
]


@dataclass
class Verdict:
    question: int
    family: str
    judge: str
    a_is_raw: bool  # True if A is raw (B is Hammerstein); False if flipped
    pick_overall: str | None  # 'A' or 'B' or None on parse fail
    pick_framework: str | None
    pick_usefulness: str | None
    pick_voice: str | None
    rationale: str
    raw: str = field(default="")
    error: str | None = None


def or_request(prompt: str, model: str, key: str, retries: int = 3) -> tuple[str, dict]:
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 8192,
    }).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://hammerstein.ai",
        "X-Title": "hammerstein-benchmark-judge",
    }
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(OR_URL, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
            text = data["choices"][0]["message"]["content"] or ""
            return text, data
        except urllib.error.HTTPError as e:
            body_text = e.read().decode("utf-8", errors="replace")
            last_err = f"HTTP {e.code}: {body_text[:300]}"
            if e.code == 429:
                time.sleep(15 * (2 ** attempt))
                continue
            return "", {"error": last_err}
        except Exception as e:
            last_err = str(e)
            time.sleep(5)
    return "", {"error": last_err}


JUDGE_PROMPT = """You are a blind LLM judge scoring two responses to the same strategic-reasoning question. The question and responses are below. Score per the rubric.

# Rubric (1-5 each, integer)

- **framework-fidelity** — does the response operate as a Hammerstein-style strategic audit? (clever-lazy / stupid-industrious vocabulary; verification gates; counter-observation; structural-fix preference; refuse-pragmatic-v0; BYOI ceiling respect; legible-failure framing)
- **usefulness** — would the operator have ACTED on this response? Would it have changed their next move?
- **voice-match** — does the response read like sober strategic reasoning? Telegraphic; specific-over-generic; no padding; no toxic positivity; no GPT-cadence pivots ("It's not just X — it's Y")

# Question

{question}

# Response A

{response_a}

# Response B

{response_b}

# Output format (RESPECT EXACTLY — machine-parsed)

framework-A: <1-5>
framework-B: <1-5>
usefulness-A: <1-5>
usefulness-B: <1-5>
voice-A: <1-5>
voice-B: <1-5>
overall: <A|B|tie>
rationale: <one sentence, max 200 chars, no line breaks>
"""


_FIELD_RE = re.compile(
    r"^(framework-A|framework-B|usefulness-A|usefulness-B|voice-A|voice-B|overall|rationale):\s*(.*)$",
    re.MULTILINE,
)


def parse_verdict(text: str) -> dict:
    out: dict = {}
    for m in _FIELD_RE.finditer(text):
        out[m.group(1)] = m.group(2).strip()
    return out


def read_response(run_dir: Path, q: int, cell: str) -> tuple[str, str]:
    """Returns (question_text, response_text)."""
    path = run_dir / f"q{q:02d}-{cell}.md"
    if not path.exists():
        return "", ""
    text = path.read_text(encoding="utf-8")
    # split by '## Question' / '## Response'
    q_match = re.search(r"## Question\s*\n+(.*?)(?=\n## Response)", text, re.DOTALL)
    r_match = re.search(r"## Response\s*\n+(.*?)$", text, re.DOTALL)
    return (
        (q_match.group(1).strip() if q_match else ""),
        (r_match.group(1).strip() if r_match else ""),
    )


def aggregate(verdicts: list[Verdict]) -> dict:
    """Compute win-rates per family (Hammerstein wins / total) for overall +
    each axis. Position bias: a_is_raw True/False is symmetric in the count."""
    by_family: dict[str, dict] = defaultdict(lambda: {
        "n": 0, "n_parsed": 0,
        "ham_wins": 0, "raw_wins": 0, "ties": 0,
        "framework_ham_better": 0, "framework_raw_better": 0, "framework_tie": 0,
        "usefulness_ham_better": 0, "usefulness_raw_better": 0, "usefulness_tie": 0,
        "voice_ham_better": 0, "voice_raw_better": 0, "voice_tie": 0,
    })
    for v in verdicts:
        b = by_family[v.family]
        b["n"] += 1
        if v.error or v.pick_overall is None:
            continue
        b["n_parsed"] += 1
        # interpret picks: A is raw if v.a_is_raw, else B is raw.
        ham_label = "B" if v.a_is_raw else "A"
        raw_label = "A" if v.a_is_raw else "B"
        if v.pick_overall == ham_label:
            b["ham_wins"] += 1
        elif v.pick_overall == raw_label:
            b["raw_wins"] += 1
        else:
            b["ties"] += 1
        # axis comparisons via int diffs
        for axis in ("framework", "usefulness", "voice"):
            a_val = _safe_int(getattr(v, f"pick_{axis}", None), 0) if False else None
        # Simpler: stored picks are A or B at the picked-side level. We keep just overall here.
    return by_family


def _safe_int(s: str | None, default: int) -> int:
    if s is None:
        return default
    try:
        return int(s)
    except (TypeError, ValueError):
        return default


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--run", default="benchmark-v0-full", help="results subdir name")
    p.add_argument("--questions", type=int, nargs="*", default=[1, 2, 3, 4, 5, 6])
    p.add_argument("--families", nargs="*", default=None,
                   help="restrict to families; default = all 3")
    p.add_argument("--judges", nargs="*", default=None,
                   help="restrict to judge models; default = all configured")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--append", action="store_true", help="append to existing JSONL log instead of truncating")
    p.add_argument("--ablation", action="store_true",
                   help="Judge ablation cells (prompt-only vs full, corpus-only vs full) instead of raw-vs-Hammerstein pairs")
    args = p.parse_args()

    random.seed(args.seed)
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key.startswith("sk-or-"):
        print("ERR: OPENROUTER_API_KEY not set", file=sys.stderr)
        return 1

    run_dir = RESULTS_ROOT / args.run
    if not run_dir.is_dir():
        print(f"ERR: run dir not found: {run_dir}", file=sys.stderr)
        return 1

    active_families = ABLATION_FAMILIES if args.ablation else FAMILIES
    families = active_families
    if args.families:
        families = [f for f in active_families if f[2] in args.families or f[1] in args.families]
    judges = JUDGES if not args.judges else [j for j in JUDGES if j in args.judges]

    out_path = run_dir / "JUDGE-VERDICTS.md"
    log_path = run_dir / "judge-verdicts.jsonl"
    if not args.append:
        log_path.write_text("", encoding="utf-8")

    verdicts: list[Verdict] = []
    n_total = len(args.questions) * len(families) * len(judges)
    n_done = 0
    total_cost_estimate_usd = 0.0
    print(f"Judge plan: {len(args.questions)} Qs x {len(families)} families x {len(judges)} judges = {n_total} ratings", file=sys.stderr)

    for q in args.questions:
        for raw_cell, ham_cell, family_label in families:
            q_text, raw_text = read_response(run_dir, q, raw_cell)
            _, ham_text = read_response(run_dir, q, ham_cell)
            if not (q_text and raw_text and ham_text):
                print(f"  SKIP Q{q} {family_label}: missing files", file=sys.stderr)
                continue
            a_is_raw = random.choice([True, False])
            response_a = raw_text if a_is_raw else ham_text
            response_b = ham_text if a_is_raw else raw_text
            prompt = JUDGE_PROMPT.format(question=q_text, response_a=response_a, response_b=response_b)
            for judge_model in judges:
                n_done += 1
                t0 = time.time()
                text, meta = or_request(prompt, judge_model, key)
                dt = time.time() - t0
                parsed = parse_verdict(text) if text else {}
                v = Verdict(
                    question=q,
                    family=family_label,
                    judge=judge_model,
                    a_is_raw=a_is_raw,
                    pick_overall=parsed.get("overall"),
                    pick_framework=None,  # parsed scores stored in raw, computed in render
                    pick_usefulness=None,
                    pick_voice=None,
                    rationale=parsed.get("rationale", "")[:300],
                    raw=text[:2000],
                    error=meta.get("error") if "error" in meta else None,
                )
                # Stash full parsed scores in rationale tail so render() can pick up
                v.pick_overall = v.pick_overall  # kept
                # Append all parsed fields to a structured JSON line
                row = {
                    "q": q, "family": family_label, "judge": judge_model,
                    "a_is_raw": a_is_raw,
                    "parsed": parsed, "rationale": v.rationale,
                    "latency_s": round(dt, 1), "raw_excerpt": text[:300],
                    "error": v.error,
                }
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
                verdicts.append(v)
                ovr = parsed.get("overall", "?")
                err = v.error or ""
                print(f"  [{n_done}/{n_total}] Q{q} {family_label} judge={judge_model.split('/')[-1]:20s} overall={ovr:5s} {err}", file=sys.stderr)

    render_summary(verdicts, args.run, out_path, log_path, active_families=families)
    print(f"\nWrote {out_path}", file=sys.stderr)
    print(f"Wrote {log_path}", file=sys.stderr)
    return 0


def render_summary(
    verdicts: list[Verdict],
    run_name: str,
    out_path: Path,
    log_path: Path,
    active_families: list[tuple[str, str, str]] | None = None,
) -> None:
    """Render JUDGE-VERDICTS.md from in-memory verdicts + jsonl log for axis scores."""
    if active_families is None:
        active_families = FAMILIES
    rows_by_family: dict[str, list[dict]] = defaultdict(list)
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            rows_by_family[row["family"]].append(row)

    lines = [f"# Hammerstein benchmark · LLM-judge verdicts ({run_name})", ""]
    lines.append(f"Judges: {', '.join(JUDGES)}")
    lines.append(f"Position-bias mitigation: per-pair randomization of A/B order; judge sees blind labels.")
    lines.append("")
    lines.append("## Per-family results")
    lines.append("")
    lines.append("| Family | n | Ham wins | Raw wins | Ties | Win-rate (Ham over Raw, ties as 0.5) | Mean framework Δ (Ham−Raw) | Mean usefulness Δ | Mean voice Δ |")
    lines.append("|---|---|---|---|---|---|---|---|---|")

    overall_ham = overall_raw = overall_tie = overall_n = 0

    for raw_cell, ham_cell, family_label in active_families:
        rows = rows_by_family.get(family_label, [])
        n = len(rows)
        if n == 0:
            lines.append(f"| {family_label} | 0 | - | - | - | - | - | - | - |")
            continue
        ham_w = raw_w = ties = 0
        framework_deltas: list[int] = []
        usefulness_deltas: list[int] = []
        voice_deltas: list[int] = []
        for row in rows:
            parsed = row.get("parsed", {})
            a_is_raw = row.get("a_is_raw")
            ham_label = "B" if a_is_raw else "A"
            raw_label = "A" if a_is_raw else "B"
            ovr = parsed.get("overall", "")
            if ovr == ham_label:
                ham_w += 1
            elif ovr == raw_label:
                raw_w += 1
            elif ovr.lower() == "tie":
                ties += 1
            # axis deltas
            for axis_name, axis_list in (
                ("framework", framework_deltas),
                ("usefulness", usefulness_deltas),
                ("voice", voice_deltas),
            ):
                a_score = _safe_int(parsed.get(f"{axis_name}-A"), -1)
                b_score = _safe_int(parsed.get(f"{axis_name}-B"), -1)
                if a_score == -1 or b_score == -1:
                    continue
                ham_score = b_score if a_is_raw else a_score
                raw_score = a_score if a_is_raw else b_score
                axis_list.append(ham_score - raw_score)
        win_rate = (ham_w + 0.5 * ties) / n if n else 0
        f_delta = sum(framework_deltas) / len(framework_deltas) if framework_deltas else 0
        u_delta = sum(usefulness_deltas) / len(usefulness_deltas) if usefulness_deltas else 0
        v_delta = sum(voice_deltas) / len(voice_deltas) if voice_deltas else 0
        lines.append(
            f"| {family_label} | {n} | {ham_w} | {raw_w} | {ties} | "
            f"{win_rate:.1%} | {f_delta:+.2f} | {u_delta:+.2f} | {v_delta:+.2f} |"
        )
        overall_ham += ham_w
        overall_raw += raw_w
        overall_tie += ties
        overall_n += n

    if overall_n:
        overall_win_rate = (overall_ham + 0.5 * overall_tie) / overall_n
        lines.append(f"| **all** | **{overall_n}** | **{overall_ham}** | **{overall_raw}** | **{overall_tie}** | **{overall_win_rate:.1%}** | - | - | - |")
    lines.append("")
    lines.append("## Per-question detail")
    lines.append("")
    lines.append("| Q | family | judge | overall (HAM=H, RAW=R, tie=T) | rationale |")
    lines.append("|---|--------|-------|-------------------------------|-----------|")
    all_rows: list[dict] = []
    for f_rows in rows_by_family.values():
        all_rows.extend(f_rows)
    all_rows.sort(key=lambda r: (r["q"], r["family"], r["judge"]))
    for row in all_rows:
        parsed = row.get("parsed", {})
        a_is_raw = row.get("a_is_raw")
        ham_label = "B" if a_is_raw else "A"
        raw_label = "A" if a_is_raw else "B"
        ovr = parsed.get("overall", "?")
        if ovr == ham_label:
            verdict = "H"
        elif ovr == raw_label:
            verdict = "R"
        elif ovr.lower() == "tie":
            verdict = "T"
        else:
            verdict = f"?({ovr})"
        rationale = (row.get("rationale") or "").replace("|", "\\|")[:150]
        lines.append(f"| Q{row['q']} | {row['family']} | {row['judge'].split('/')[-1]} | {verdict} | {rationale} |")
    lines.append("")
    lines.append(f"Raw verdicts: `{log_path.name}`")
    out_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
