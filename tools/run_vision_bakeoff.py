"""Vision bake-off runner for Hammerstein v0 (ham-022e).

Records per-provider shape-gate and semantic outcomes on the locked
benchmark fixtures, writes JSON for the parent session to consume, and
applies the release decision tree from scope/VISION-SUPPORT.md (private).

Decision tree (summary):
- On non-placeholder fixtures only, if Qwen3-VL-Plus achieves 100% shape
  passes and at least half semantic passes, lock OpenRouter Qwen3-VL-Plus as
  primary with OpenRouter GPT-4o failover.
- Otherwise lock GPT-4o flat on OpenRouter with no failover.

Examples::

    python tools/run_vision_bakeoff.py
    python tools/run_vision_bakeoff.py --dry-run
    python tools/run_vision_bakeoff.py --skip-probe --output /tmp/out.json
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TypedDict

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from hammerstein import backends  # noqa: E402
from hammerstein import prompt as prompt_mod  # noqa: E402
from hammerstein import shape_gate  # noqa: E402

log = logging.getLogger("run_vision_bakeoff")

# OpenRouter slugs used for the bake-off matrix (parent session may revise).
BAKEOFF_QWEN_OPENROUTER_MODEL = "qwen/qwen3-vl-plus"
BAKEOFF_GPT_OPENROUTER_MODEL = "openai/gpt-4o"

QWEN_LABEL = "qwen3-vl-plus"
GPT_LABEL = "gpt-4o"
DEEPSEEK_LABEL = "deepseek-vision"

OPENROUTER_KEY_ENV = "OPENROUTER_API_KEY"
DEEPSEEK_KEY_ENV = "DEEPSEEK_API_KEY"

_PLACEHOLDER_REASON = "placeholder fixture"


class BenchmarkCase(TypedDict):
    name: str
    fixture: str
    brief: str
    expected_substring_sets: tuple[tuple[str, ...], tuple[str, ...]] | None


BENCHMARK_CASES: list[BenchmarkCase] = [
    {
        "name": "twar-pc-hex-vs-area-brief",
        "fixture": "tests/fixtures/vision-audit/twar-pc-s5-hex-grid.png",
        "brief": (
            "Audit this visual: [screenshot of TWAR PC operational map showing a "
            "hex-grid overlay with 12 hexes spanning the Crimean peninsula, units "
            "on hex centers, a sidebar with 'Move Phase 1/3' counter]. Brief: "
            "REGISTER-LOCKED.md specifies area-based province nodes per ROTK IV "
            "reverse-engineering thesis, NOT hex."
        ),
        "expected_substring_sets": (
            ("hex",),
            ("area", "province", "register", "mismatch", "redo"),
        ),
    },
    {
        "name": "retrogaze-rg-023-craft-floor",
        "fixture": "tests/fixtures/vision-audit/retrogaze-rg-023-sprite.png",
        "brief": (
            "Audit this visual: [retrogaze rg-023 sprite — hero idle, 16×16 NES "
            "tile, 4-color hardware constraint]. Rubric: >=7/10 craft floor on "
            "shade-discipline / clean-pixels / silhouette axes."
        ),
        "expected_substring_sets": (
            ("craft",),
            ("shade", "silhouette", "reroll", "below"),
        ),
    },
    {
        "name": "fnordos-dept-23-panel",
        "fixture": "tests/fixtures/vision-audit/fnordos-dept-23-panel.png",
        "brief": (
            "Audit this visual: [FnordOS cinematic intro — post-DEPT-23 panel, "
            "title card over scanline field]. Design/REGISTER.md locks the "
            "16-color Bureau Palette, IBM Plex Mono for UI chrome, and "
            "chromatic-aberration scanline filter on cinematic glass."
        ),
        "expected_substring_sets": None,
    },
]


class ProviderSpec(TypedDict):
    key: str
    label: str
    backend: str
    model: str
    api_key_env: str


def _provider_specs_base() -> list[ProviderSpec]:
    return [
        {
            "key": "qwen",
            "label": QWEN_LABEL,
            "backend": "openrouter",
            "model": BAKEOFF_QWEN_OPENROUTER_MODEL,
            "api_key_env": OPENROUTER_KEY_ENV,
        },
        {
            "key": "gpt-4o",
            "label": GPT_LABEL,
            "backend": "openrouter",
            "model": BAKEOFF_GPT_OPENROUTER_MODEL,
            "api_key_env": OPENROUTER_KEY_ENV,
        },
    ]


def _deepseek_first_vision_model(api_key: str, *, timeout: int = 5) -> str | None:
    """Return first DeepSeek model id whose name contains 'vision', or None."""
    url = "https://api.deepseek.com/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            data = json.loads(raw)
    except Exception:
        return None
    for entry in data.get("data", []) or []:
        mid = (entry.get("id") or "").lower()
        if "vision" in mid:
            return str(entry.get("id"))
    return None


def _is_placeholder_png(path: str | Path) -> bool:
    """True when the file is missing or tiny (benchmark placeholder PNG)."""
    p = Path(path)
    if not p.is_file():
        return True
    return p.stat().st_size <= 100


def _load_audit_template_text() -> str:
    templates_dir = _REPO_ROOT / "prompts" / "templates"
    return prompt_mod.load_template(templates_dir, "audit-this-visual")


def _assemble_query(brief: str, template_text: str) -> str:
    return f"{brief.strip()}\n\n{template_text.strip()}\n"


def _check_semantic_substrings(
    response: str,
    expected: tuple[tuple[str, ...], tuple[str, ...]],
) -> tuple[bool, list[str]]:
    """Each inner tuple is an OR-group; every group must match (case-insensitive)."""
    hay = response.lower()
    missing: list[str] = []
    for group in expected:
        if not any(sub.lower() in hay for sub in group):
            missing.append(
                f"none of {group!r} found (case-insensitive substring match)"
            )
    return (len(missing) == 0, missing)


def _dispatch_vision(
    spec: ProviderSpec,
    prompt: str,
    image_path: str,
) -> backends.CallResult:
    key = os.environ.get(spec["api_key_env"], "")
    if not key:
        raise backends.BackendError(
            f"missing API key env {spec['api_key_env']!r} for {spec['label']}"
        )
    if spec["backend"] == "openrouter":
        return backends.call_openrouter(
            prompt,
            model=spec["model"],
            api_key=key,
            image_path=image_path,
        )
    if spec["backend"] == "deepseek":
        return backends.call_deepseek(
            prompt,
            model=spec["model"],
            api_key=key,
            image_path=image_path,
        )
    raise backends.BackendError(f"unsupported backend {spec['backend']!r}")


def _excerpt(text: str, limit: int = 500) -> str:
    return text[:limit] if text else ""


def apply_decision_tree(results_doc: dict[str, Any]) -> dict[str, Any]:
    """Apply VISION-SUPPORT.md bake-off lock rules to a results document."""
    fixtures: list[dict[str, Any]] = results_doc.get("fixtures", [])
    placeholder_n = sum(
        1 for fx in fixtures if fx.get("real_or_placeholder") == "placeholder"
    )
    real_fixtures = [fx for fx in fixtures if fx.get("real_or_placeholder") == "real"]
    n_real = len(real_fixtures)

    qwen_shape = 0
    qwen_semantic = 0
    for fx in real_fixtures:
        row = next(
            (
                r
                for r in fx.get("results_by_provider", [])
                if r.get("provider_label") == QWEN_LABEL
            ),
            None,
        )
        if row is None:
            continue
        if row.get("shape_gate_passed") is True:
            qwen_shape += 1
        exp = fx.get("expected_substrings_or_null")
        sem_ok = row.get("semantic_passed") is True
        if exp is None:
            if row.get("shape_gate_passed") is True:
                qwen_semantic += 1
        elif sem_ok:
            qwen_semantic += 1

    shape_ratio = qwen_shape / n_real if n_real else 0.0
    sem_ratio = qwen_semantic / n_real if n_real else 0.0

    if n_real >= 1 and shape_ratio == 1.0 and sem_ratio >= 0.5:
        rationale = (
            f"Qwen passed {qwen_shape}/{n_real} shape AND {qwen_semantic}/{n_real} "
            f"semantic on real fixtures; failover-on-shape-fail to GPT-4o per spec. "
            f"Excluded {placeholder_n} placeholder case(s) from threshold math."
        )
        return {
            "primary_backend": "openrouter",
            "primary_model": BAKEOFF_QWEN_OPENROUTER_MODEL,
            "failover_backend": "openrouter",
            "failover_model": BAKEOFF_GPT_OPENROUTER_MODEL,
            "rationale": rationale,
        }

    if n_real == 0:
        why = "no real fixtures (all placeholder); GPT-4o flat per spec ELSE branch."
    else:
        why = (
            "Qwen failed shape or semantic on real fixtures; "
            "GPT-4o flat per spec ELSE branch."
        )
    rationale = (
        f"{why} Excluded {placeholder_n} placeholder case(s) from threshold math."
    )
    return {
        "primary_backend": "openrouter",
        "primary_model": BAKEOFF_GPT_OPENROUTER_MODEL,
        "failover_backend": None,
        "failover_model": None,
        "rationale": rationale,
    }


def _build_provider_list(
    *,
    provider_keys: list[str],
    skip_probe: bool,
) -> list[ProviderSpec]:
    specs = _provider_specs_base()
    key_set = set(provider_keys)

    if not skip_probe and "deepseek" in key_set:
        ds_key = os.environ.get(DEEPSEEK_KEY_ENV, "")
        if not ds_key:
            log.info("DeepSeek skipped: %s not set", DEEPSEEK_KEY_ENV)
        elif not backends.deepseek_supports_vision(ds_key):
            log.info("DeepSeek skipped: vision probe returned False")
        else:
            model = _deepseek_first_vision_model(ds_key)
            if model:
                specs.append(
                    {
                        "key": "deepseek",
                        "label": DEEPSEEK_LABEL,
                        "backend": "deepseek",
                        "model": model,
                        "api_key_env": DEEPSEEK_KEY_ENV,
                    }
                )
            else:
                log.info("DeepSeek skipped: no vision model id in /v1/models")

    return [s for s in specs if s["key"] in key_set]


def _run_single_case(
    spec: ProviderSpec,
    case: BenchmarkCase,
    abs_image: Path,
    query: str,
    *,
    dry_run: bool,
) -> dict[str, Any]:
    placeholder = _is_placeholder_png(abs_image)
    if placeholder:
        return {
            "provider_label": spec["label"],
            "model": spec["model"],
            "shape_gate_passed": False,
            "semantic_passed": False,
            "semantic_missing": [_PLACEHOLDER_REASON],
            "raw_response_excerpt": "",
            "latency_ms": 0,
            "cost_usd": 0.0,
        }

    if dry_run:
        return {
            "provider_label": spec["label"],
            "model": spec["model"],
            "shape_gate_passed": True,
            "semantic_passed": True,
            "semantic_missing": [],
            "raw_response_excerpt": "[dry-run synthetic]",
            "latency_ms": 0,
            "cost_usd": 0.0,
        }

    try:
        result = _dispatch_vision(spec, query, str(abs_image))
    except Exception as exc:
        return {
            "provider_label": spec["label"],
            "model": spec["model"],
            "shape_gate_passed": False,
            "semantic_passed": False,
            "semantic_missing": [str(exc)],
            "raw_response_excerpt": _excerpt(str(exc)),
            "latency_ms": 0,
            "cost_usd": 0.0,
        }

    raw = result.response or ""
    shaped = shape_gate.is_well_shaped(raw)
    exp = case["expected_substring_sets"]
    sem_ok = False
    missing: list[str] = []
    if not shaped:
        sem_ok = False
        missing = ["shape gate failed; semantic not evaluated"]
    elif exp is None:
        sem_ok = True
    else:
        sem_ok, missing = _check_semantic_substrings(raw, exp)

    return {
        "provider_label": spec["label"],
        "model": result.model,
        "shape_gate_passed": shaped,
        "semantic_passed": sem_ok,
        "semantic_missing": missing,
        "raw_response_excerpt": _excerpt(raw),
        "latency_ms": result.latency_ms,
        "cost_usd": result.cost_usd,
    }


def _print_summary(results_doc: dict[str, Any]) -> None:
    for fx in results_doc.get("fixtures", []):
        name = fx.get("name")
        for row in fx.get("results_by_provider", []):
            lab = row.get("provider_label")
            sp = row.get("shape_gate_passed")
            se = row.get("semantic_passed")
            print(f"[case={name}] {lab}: shape={sp} semantic={se}", file=sys.stderr)
    dec = results_doc.get("decision", {})
    print(
        "decision: primary="
        f"{dec.get('primary_backend')}:{dec.get('primary_model')} "
        f"failover={dec.get('failover_backend')}:{dec.get('failover_model')}",
        file=sys.stderr,
    )
    print(f"rationale: {dec.get('rationale')}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hammerstein vision bake-off v0.")
    parser.add_argument(
        "--providers",
        nargs="+",
        default=["qwen", "gpt-4o"],
        help="Provider keys to exercise (default: qwen gpt-4o).",
    )
    parser.add_argument(
        "--output",
        default="tests/fixtures/vision-audit/bakeoff-results.json",
        help="JSON output path.",
    )
    parser.add_argument(
        "--skip-probe",
        action="store_true",
        help="Do not probe DeepSeek vision; omit DeepSeek from the matrix.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip API calls; emit synthetic passes (except placeholder fixtures).",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    provider_keys = list(args.providers)
    default_set = {"qwen", "gpt-4o"}
    if (
        not args.skip_probe
        and set(provider_keys) == default_set
        and "deepseek" not in provider_keys
    ):
        provider_keys.append("deepseek")

    specs = _build_provider_list(provider_keys=provider_keys, skip_probe=args.skip_probe)
    template_text = _load_audit_template_text()

    fixtures_out: list[dict[str, Any]] = []
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for case in BENCHMARK_CASES:
        abs_image = _REPO_ROOT / case["fixture"]
        query = _assemble_query(case["brief"], template_text)
        placeholder = _is_placeholder_png(abs_image)
        kind = "placeholder" if placeholder else "real"
        exp_json: list[list[str]] | None
        if case["expected_substring_sets"] is None:
            exp_json = None
        else:
            exp_json = [list(g) for g in case["expected_substring_sets"]]

        rows: list[dict[str, Any]] = []
        for spec in specs:
            rows.append(_run_single_case(spec, case, abs_image, query, dry_run=args.dry_run))

        fixtures_out.append(
            {
                "name": case["name"],
                "fixture_path": case["fixture"],
                "real_or_placeholder": kind,
                "expected_substrings_or_null": exp_json,
                "results_by_provider": rows,
            }
        )

    results_doc: dict[str, Any] = {
        "timestamp": ts,
        "fixtures": fixtures_out,
    }
    results_doc["decision"] = apply_decision_tree(results_doc)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results_doc, indent=2), encoding="utf-8")

    _print_summary(results_doc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
