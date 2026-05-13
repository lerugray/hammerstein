#!/usr/bin/env python3
"""Hammerstein human-judge interactive judging tool.

Standalone script for an external human judge. Reads a pairs.json
file (produced by `human_judge_runner.py generate`) and walks the
judge through blind A/B comparisons. Saves judgments to a JSON file
the judge sends back.

ZERO dependencies beyond Python 3.8+ stdlib. No API keys required.
No Hammerstein repo / harness needed. The pairs.json file contains
everything: questions, blind-labeled responses A and B.

USAGE
    python human_judge.py pairs.json
    python human_judge.py pairs.json --out my-judgments.json
    python human_judge.py pairs.json --resume   # continue an interrupted session

The output file (default: <pairs-basename>-judgments.json) holds your
judgments. Send that file back to Ray when done; he merges with the
private mapping table to compute results.

The judging is blind: you see Response A and Response B for each
question, but never see which model produced which response. The
randomization is per-pair, so A/B doesn't consistently mean any
specific cell.

FOR EACH PAIR you pick ONE of: a / b / tie / skip
plus an optional 1-line note (Enter to skip).

  a    — Response A is more useful for the operator
  b    — Response B is more useful
  tie  — both equally useful (or both equally unhelpful)
  skip — can't tell / would need more context

You can quit any time with Ctrl-C; judgments are saved after each
pair, so resuming with --resume picks up where you left off.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional


VERSION = "human-judge/1.0"


def load_pairs(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    pairs = data.get("pairs") if isinstance(data, dict) else data
    if not isinstance(pairs, list):
        sys.exit(f"FATAL: {path} is not a list of pairs (got {type(pairs).__name__})")
    for i, p in enumerate(pairs):
        for k in ("pair_id", "question", "response_a", "response_b"):
            if k not in p:
                sys.exit(f"FATAL: pair {i} missing required key '{k}'")
    return pairs


def load_existing_judgments(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return {}
    judgments = data.get("judgments") if isinstance(data, dict) else data
    if not isinstance(judgments, list):
        return {}
    return {j["pair_id"]: j for j in judgments if "pair_id" in j}


def save_judgments(path: Path, judge_name: str, judgments_by_id: dict[str, dict]) -> None:
    out = {
        "version": VERSION,
        "judge_name": judge_name,
        "judgments": list(judgments_by_id.values()),
    }
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    tmp.replace(path)


def print_pair(pair: dict, idx: int, total: int) -> None:
    print()
    print("=" * 78)
    print(f"  PAIR {idx + 1} of {total}  (pair_id: {pair['pair_id']})")
    print("=" * 78)
    print()
    print("QUESTION:")
    print()
    for line in pair["question"].rstrip().splitlines():
        print(f"  {line}")
    print()
    print("-" * 78)
    print(" RESPONSE A:")
    print("-" * 78)
    print()
    print(pair["response_a"].rstrip())
    print()
    print("-" * 78)
    print(" RESPONSE B:")
    print("-" * 78)
    print()
    print(pair["response_b"].rstrip())
    print()
    print("=" * 78)


def prompt_judgment() -> Optional[str]:
    while True:
        try:
            choice = input("Preference [a / b / tie / skip / q-to-quit]: ").strip().lower()
        except EOFError:
            return None
        if choice in ("a", "b", "tie", "skip"):
            return choice
        if choice in ("q", "quit", "exit"):
            return None
        print("  please enter one of: a, b, tie, skip, q")


def prompt_note() -> str:
    try:
        return input("Optional 1-line note (Enter to skip): ").strip()
    except EOFError:
        return ""


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Blind human-judge tool for the Hammerstein benchmark."
    )
    parser.add_argument("pairs", type=Path, help="Path to pairs.json from Ray")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output judgments file (default: <pairs-stem>-judgments.json)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume an interrupted session; skip pairs already judged",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="",
        help="Optional judge name to embed in the output JSON",
    )
    args = parser.parse_args(argv)

    if not args.pairs.exists():
        sys.exit(f"FATAL: pairs file not found: {args.pairs}")

    out_path = args.out or args.pairs.with_name(args.pairs.stem + "-judgments.json")
    pairs = load_pairs(args.pairs)

    existing = load_existing_judgments(out_path) if args.resume else {}

    judge_name = args.name
    if not judge_name:
        try:
            judge_name = input("Your name (for the record, optional — Enter to skip): ").strip()
        except EOFError:
            judge_name = ""

    print()
    print(f"  Hammerstein benchmark — human judging")
    print(f"  Pairs file: {args.pairs}")
    print(f"  Output:     {out_path}")
    print(f"  Judge:      {judge_name or '(anonymous)'}")
    print(f"  Total pairs: {len(pairs)}")
    if existing:
        print(f"  Resuming:   {len(existing)} pair(s) already judged")
    print()
    print("  For each pair, pick a / b / tie / skip.")
    print("  Optional 1-line note after the choice.")
    print("  Ctrl-C any time to quit; judgments save after each pair.")
    print()

    judgments_by_id = dict(existing)

    try:
        for idx, pair in enumerate(pairs):
            pid = pair["pair_id"]
            if pid in judgments_by_id:
                continue
            print_pair(pair, idx, len(pairs))
            choice = prompt_judgment()
            if choice is None:
                print("\n  Quit. Progress saved.")
                break
            note = prompt_note()
            judgments_by_id[pid] = {
                "pair_id": pid,
                "choice": choice,
                "note": note,
            }
            save_judgments(out_path, judge_name, judgments_by_id)
            print(f"  saved ({len(judgments_by_id)}/{len(pairs)})")
    except KeyboardInterrupt:
        print("\n  Interrupted. Progress saved.")

    print()
    print(f"  Output written to: {out_path}")
    print(f"  Judgments: {len(judgments_by_id)} / {len(pairs)}")
    if len(judgments_by_id) == len(pairs):
        print("  Send this file back to Ray.")
    else:
        print("  Run again with --resume to continue, or send what you have.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
