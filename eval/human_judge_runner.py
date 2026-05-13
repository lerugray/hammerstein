#!/usr/bin/env python3
"""Hammerstein human-judge benchmark runner — Ray-side tooling.

Two subcommands:

  generate  - reads a run dir produced by `run_benchmark.py` and emits
              a pairs.json file (for the external judge) plus a
              mapping.json file (Ray-private; tells you which cell is
              A vs B per pair).

  score     - merges pairs.json + judgments.json (from the judge) +
              mapping.json (your private file) and writes a results
              markdown file with per-pair-cell win counts + summary.

EXAMPLE FLOW

  # 1. Generate responses against the human-judge Q-set
  source ~/.generalstaff/.env
  python eval/run_benchmark.py \\
      --benchmark eval/BENCHMARK-human-judge-2026-05-13.md \\
      --cells or-claude-sonnet-raw or-claude-sonnet or-grok-raw or-grok

  # 2. Build the blind pairs file
  python eval/human_judge_runner.py generate \\
      --run-dir eval/results/<TS>/ \\
      --pairs-out human-judge-pairs.json \\
      --mapping-out human-judge-mapping.json \\
      --cell-pairs or-claude-sonnet-raw:or-claude-sonnet \\
                   or-grok-raw:or-grok

  # 3. Send human-judge-pairs.json to the external judge.
  #    They run `python eval/human_judge.py human-judge-pairs.json`
  #    and send back the resulting judgments file.

  # 4. Score
  python eval/human_judge_runner.py score \\
      --pairs human-judge-pairs.json \\
      --judgments human-judge-pairs-judgments.json \\
      --mapping human-judge-mapping.json \\
      --out eval/RESULTS-human-judge-2026-05-NN.md
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


VERSION = "human-judge-runner/1.0"

# Strip the metadata block that run_benchmark.py prepends to each
# response file. Pattern: starts with `---\n...\n---\n\n` at file top.
_METADATA_BLOCK_RE = re.compile(
    r"\A---\n.*?\n---\n+", re.DOTALL
)


def read_response_file(path: Path) -> str:
    """Load a response file from a benchmark run dir, stripping its
    metadata header. Returns the raw response body."""
    raw = path.read_text(encoding="utf-8")
    return _METADATA_BLOCK_RE.sub("", raw).rstrip() + "\n"


def discover_run_questions(run_dir: Path, cell_slug: str) -> dict[int, Path]:
    """Find all q{N:02d}-{cell-slug}.md files for one cell.

    Returns mapping qid -> path.
    """
    out: dict[int, Path] = {}
    for f in sorted(run_dir.glob(f"q*-{cell_slug}.md")):
        m = re.match(rf"q(\d+)-{re.escape(cell_slug)}\.md", f.name)
        if not m:
            continue
        out[int(m.group(1))] = f
    return out


def extract_question_text(benchmark_path: Path, qid: int) -> str:
    """Re-extract a question's query text from the benchmark MD for
    embedding in pairs.json. Avoids depending on run_benchmark.py
    internals (no harness import here)."""
    if not benchmark_path or not benchmark_path.exists():
        return f"(question {qid} text unavailable — benchmark file not found)"
    raw = benchmark_path.read_text(encoding="utf-8")
    section_re = re.compile(
        rf"^## Question {qid} — (.+?)\n(.*?)(?=^## Question \d+|^---\s*\n## What \"good\"|\Z)",
        re.DOTALL | re.MULTILINE,
    )
    m = section_re.search(raw)
    if not m:
        return f"(question {qid} text unavailable — section not found in {benchmark_path.name})"
    body = m.group(2)
    qmatch = re.search(r"\*\*Query:\*\*\s*\n+((?:>.*\n?)+)", body)
    if not qmatch:
        return f"(question {qid} text unavailable — query block not found)"
    block = qmatch.group(1)
    if re.search(r"_\[TBD", block, re.IGNORECASE):
        return f"(question {qid} is a stub — fill in BENCHMARK-human-judge-*.md before generating)"
    lines = []
    for line in block.splitlines():
        if line.startswith(">"):
            lines.append(line[1:].lstrip())
    return "\n".join(lines).strip() + "\n"


def cmd_generate(args: argparse.Namespace) -> int:
    run_dir: Path = args.run_dir
    if not run_dir.is_dir():
        sys.exit(f"FATAL: --run-dir not a directory: {run_dir}")

    cell_pairs: list[tuple[str, str]] = []
    for spec in args.cell_pairs:
        if ":" not in spec:
            sys.exit(f"FATAL: cell-pair must be 'cellA:cellB' (got {spec!r})")
        a, b = spec.split(":", 1)
        cell_pairs.append((a.strip(), b.strip()))

    # Resolve benchmark path: explicit flag wins; otherwise look in run dir
    # for a hint (run_benchmark.py writes the benchmark file name into
    # SUMMARY.md, but we'll just trust the CLI flag).
    benchmark_path: Optional[Path] = args.benchmark
    if not benchmark_path:
        # Default: look for a BENCHMARK-human-judge-*.md next to the eval/
        # dir.
        eval_dir = Path(__file__).resolve().parent
        candidates = sorted(eval_dir.glob("BENCHMARK-human-judge-*.md"))
        if candidates:
            benchmark_path = candidates[-1]
            print(f"  using benchmark: {benchmark_path}", file=sys.stderr)
        else:
            print(
                "  WARNING: no --benchmark and no BENCHMARK-human-judge-*.md "
                "found; question text will be marked unavailable",
                file=sys.stderr,
            )

    rng = random.Random(args.seed) if args.seed is not None else random.Random()

    pairs: list[dict] = []
    mapping: list[dict] = []
    pair_counter = 0

    for cell_a, cell_b in cell_pairs:
        a_files = discover_run_questions(run_dir, cell_a)
        b_files = discover_run_questions(run_dir, cell_b)
        common_qids = sorted(set(a_files) & set(b_files))
        if not common_qids:
            print(
                f"  WARNING: no overlapping question ids for cell-pair "
                f"{cell_a} vs {cell_b}",
                file=sys.stderr,
            )
            continue

        for qid in common_qids:
            pair_counter += 1
            pid = f"p{pair_counter:03d}"
            response_for_cell_a = read_response_file(a_files[qid])
            response_for_cell_b = read_response_file(b_files[qid])
            # Position-randomize: flip a coin per pair
            if rng.random() < 0.5:
                side_a_cell = cell_a
                side_a_text = response_for_cell_a
                side_b_cell = cell_b
                side_b_text = response_for_cell_b
            else:
                side_a_cell = cell_b
                side_a_text = response_for_cell_b
                side_b_cell = cell_a
                side_b_text = response_for_cell_a

            question_text = extract_question_text(benchmark_path, qid)
            pairs.append(
                {
                    "pair_id": pid,
                    "question_id": qid,
                    "cell_pair_group": f"{cell_a}_vs_{cell_b}",
                    "question": question_text,
                    "response_a": side_a_text,
                    "response_b": side_b_text,
                }
            )
            mapping.append(
                {
                    "pair_id": pid,
                    "question_id": qid,
                    "cell_pair_group": f"{cell_a}_vs_{cell_b}",
                    "side_a_cell": side_a_cell,
                    "side_b_cell": side_b_cell,
                }
            )

    if not pairs:
        sys.exit("FATAL: no pairs generated (no overlapping responses found)")

    # Shuffle pair display order so cell-pair groups are interleaved.
    # The judge sees mixed pairs, not all-Sonnet-then-all-Grok.
    order = list(range(len(pairs)))
    rng.shuffle(order)
    pairs_shuffled = [pairs[i] for i in order]
    # Mapping stays in pair-creation order (Ray-private; doesn't matter
    # since lookup is by pair_id).

    pairs_out = {
        "version": VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "cell_pairs": [{"a": a, "b": b} for a, b in cell_pairs],
        "rubric": "overall_preference",
        "pairs": pairs_shuffled,
    }
    mapping_out = {
        "version": VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "seed": args.seed,
        "mapping": mapping,
    }

    args.pairs_out.write_text(
        json.dumps(pairs_out, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    args.mapping_out.write_text(
        json.dumps(mapping_out, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"  pairs written: {args.pairs_out} ({len(pairs)} pairs)")
    print(f"  mapping written: {args.mapping_out} (KEEP THIS PRIVATE)")
    print(f"  send {args.pairs_out.name} to the external judge")
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    pairs_raw = json.loads(args.pairs.read_text(encoding="utf-8"))
    judgments_raw = json.loads(args.judgments.read_text(encoding="utf-8"))
    mapping_raw = json.loads(args.mapping.read_text(encoding="utf-8"))

    pairs = pairs_raw.get("pairs", [])
    judgments = judgments_raw.get("judgments", [])
    mapping = mapping_raw.get("mapping", [])
    judge_name = judgments_raw.get("judge_name") or "(anonymous)"

    mapping_by_id = {m["pair_id"]: m for m in mapping}
    pairs_by_id = {p["pair_id"]: p for p in pairs}

    # Per-cell-pair-group tally
    tallies: dict[str, dict[str, int]] = defaultdict(
        lambda: {"hammerstein_wins": 0, "raw_wins": 0, "tie": 0, "skip": 0, "n": 0}
    )
    detail_rows: list[str] = []

    # Hammerstein cell heuristic: the cell slug that does NOT end with
    # "-raw" is the Hammerstein-on-frontier side. The raw side ends "-raw".
    def is_hammerstein(cell: str) -> bool:
        return not cell.endswith("-raw")

    for j in judgments:
        pid = j["pair_id"]
        if pid not in mapping_by_id or pid not in pairs_by_id:
            print(f"  WARNING: judgment for unknown pair_id {pid}", file=sys.stderr)
            continue
        m = mapping_by_id[pid]
        p = pairs_by_id[pid]
        group = m["cell_pair_group"]
        choice = j["choice"]
        side_a_cell = m["side_a_cell"]
        side_b_cell = m["side_b_cell"]

        tallies[group]["n"] += 1
        if choice == "a":
            winner_cell = side_a_cell
            if is_hammerstein(winner_cell):
                tallies[group]["hammerstein_wins"] += 1
            else:
                tallies[group]["raw_wins"] += 1
        elif choice == "b":
            winner_cell = side_b_cell
            if is_hammerstein(winner_cell):
                tallies[group]["hammerstein_wins"] += 1
            else:
                tallies[group]["raw_wins"] += 1
        elif choice == "tie":
            tallies[group]["tie"] += 1
        elif choice == "skip":
            tallies[group]["skip"] += 1
        else:
            print(f"  WARNING: unknown choice {choice!r} for {pid}", file=sys.stderr)

        # Detail row for the results MD
        q_id = m["question_id"]
        note = (j.get("note") or "").replace("\n", " ").strip()
        detail_rows.append(
            f"| {pid} | Q{q_id} | `{group}` | `{side_a_cell}` | `{side_b_cell}` | "
            f"**{choice}** | "
            f"{('Hammerstein' if (choice in ('a','b') and is_hammerstein(side_a_cell if choice == 'a' else side_b_cell)) else 'Raw' if choice in ('a','b') else '—')} | "
            f"{note or '—'} |"
        )

    # Build results markdown
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines: list[str] = []
    lines.append(f"# Hammerstein human-judge results — {now}")
    lines.append("")
    lines.append(f"**Judge:** {judge_name}")
    lines.append(f"**Pairs file:** `{args.pairs.name}`")
    lines.append(f"**Judgments file:** `{args.judgments.name}`")
    lines.append(f"**Total judgments:** {sum(t['n'] for t in tallies.values())}")
    lines.append("")
    lines.append("## Summary by cell pair")
    lines.append("")
    lines.append("| Cell pair | n | Hammerstein wins | Raw wins | Tie | Skip | Ham win-rate (decided) |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    overall_ham = 0
    overall_raw = 0
    overall_tie = 0
    overall_skip = 0
    overall_n = 0
    for group, t in tallies.items():
        decided = t["hammerstein_wins"] + t["raw_wins"]
        rate = (
            f"{t['hammerstein_wins']}/{decided} = {(t['hammerstein_wins']/decided*100):.1f}%"
            if decided
            else "n/a"
        )
        lines.append(
            f"| `{group}` | {t['n']} | {t['hammerstein_wins']} | {t['raw_wins']} | "
            f"{t['tie']} | {t['skip']} | {rate} |"
        )
        overall_ham += t["hammerstein_wins"]
        overall_raw += t["raw_wins"]
        overall_tie += t["tie"]
        overall_skip += t["skip"]
        overall_n += t["n"]
    overall_decided = overall_ham + overall_raw
    overall_rate = (
        f"{overall_ham}/{overall_decided} = {(overall_ham/overall_decided*100):.1f}%"
        if overall_decided
        else "n/a"
    )
    lines.append(
        f"| **TOTAL** | **{overall_n}** | **{overall_ham}** | **{overall_raw}** | "
        f"**{overall_tie}** | **{overall_skip}** | **{overall_rate}** |"
    )
    lines.append("")
    lines.append("## Per-pair detail")
    lines.append("")
    lines.append("| pair | Q | group | side_A | side_B | choice | winner side | note |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    lines.extend(detail_rows)
    lines.append("")
    lines.append("## Interpretation cheatsheet")
    lines.append("")
    lines.append(
        "- The Hammerstein cell-slug for each pair does NOT end with `-raw`; the raw baseline ends `-raw`. The 'winner side' column reports which side the judge picked, mapped to whether that side is Hammerstein-on-X or raw-X."
    )
    lines.append(
        "- A 'tie' or 'skip' is data too — high tie rate suggests the human couldn't easily distinguish the responses, which is itself a useful signal about the framework's perceptual lift."
    )
    lines.append(
        "- For comparison against the LLM-judge baselines: v0 (Sonnet family in-distribution) showed 100% Hammerstein preference; v0.5 (Grok family) showed 91.7%. The human-judge equivalents here are smaller-n but the methodologically cleaner test."
    )

    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  results written: {args.out}")
    print(
        f"  overall: Hammerstein {overall_ham} / Raw {overall_raw} / Tie {overall_tie} "
        f"/ Skip {overall_skip}  (n={overall_n}, ham_rate_decided={overall_rate})"
    )
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Hammerstein human-judge runner (generate pairs + score judgments)."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    pg = sub.add_parser("generate", help="Build pairs.json + mapping.json from a run dir")
    pg.add_argument("--run-dir", type=Path, required=True, help="eval/results/<TS>/ from run_benchmark.py")
    pg.add_argument(
        "--cell-pairs",
        nargs="+",
        required=True,
        help="One or more cell pairs in 'rawCell:hammerCell' form, e.g. or-claude-sonnet-raw:or-claude-sonnet",
    )
    pg.add_argument(
        "--pairs-out",
        type=Path,
        default=Path("human-judge-pairs.json"),
        help="Output pairs file (send this to the human judge)",
    )
    pg.add_argument(
        "--mapping-out",
        type=Path,
        default=Path("human-judge-mapping.json"),
        help="Output private mapping file (keep this; do NOT send to the judge)",
    )
    pg.add_argument(
        "--benchmark",
        type=Path,
        default=None,
        help="Path to BENCHMARK-human-judge-*.md (to embed question text). "
        "Default: latest BENCHMARK-human-judge-*.md in eval/",
    )
    pg.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional RNG seed for reproducible position-randomization",
    )
    pg.set_defaults(func=cmd_generate)

    ps = sub.add_parser("score", help="Combine judgments with mapping and emit a results MD")
    ps.add_argument("--pairs", type=Path, required=True, help="The pairs.json sent to the judge")
    ps.add_argument(
        "--judgments",
        type=Path,
        required=True,
        help="The judgments JSON returned by the judge",
    )
    ps.add_argument("--mapping", type=Path, required=True, help="Your private mapping.json")
    ps.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output results markdown path (e.g. eval/RESULTS-human-judge-2026-05-NN.md)",
    )
    ps.set_defaults(func=cmd_score)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
