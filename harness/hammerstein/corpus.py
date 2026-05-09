"""Corpus loading + keyword-based RAG retrieval.

v0 retrieval uses tag+keyword overlap scoring, no embeddings. The corpus is
~50 entries × ~250-400 tokens each; brute-force scoring fits in <50ms and
keeps the dependency tree at zero. Migration to embeddings is reserved for
v1 if the corpus grows past ~80 entries (`tech/STACK-DECISION.md`).

Retrieval is the judgment-loaded part of the harness: which entries surface
for a given query determines whether the few-shot context steers the model
toward the right reasoning shape. The scoring rules below codify the
template-specific biases documented in the "Notes for the harness" sections
of each `prompts/templates/*.md`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Protocol, runtime_checkable

# Stop words deliberately small. Keeping framework-vocabulary words
# (verify, premise, gate, ceiling, quadrant, etc.) as scoring features.
_STOP_WORDS = frozenset(
    """
    a an and are as at be been being but by could did do does for from had
    has have how i if in into is it its just may me might my of on or over
    so than that the their them then there these they this those to was
    we were what when where which who why will with would you your
    """.split()
)

_TOKEN_RE = re.compile(r"[a-z0-9_]+")
_FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


@runtime_checkable
class _TextReadable(Protocol):
    def read_text(self, encoding: str = "utf-8") -> str: ...


@runtime_checkable
class _DirLike(Protocol):
    def iterdir(self): ...


@dataclass
class CorpusEntry:
    """One corpus entry loaded from `corpus/entries/NN-*.md`."""

    id: str  # zero-padded like "01", "27"
    title: str
    quadrant: str  # clever_lazy | clever_industrious | stupid_lazy | stupid_industrious
    principle: str
    source: str
    quality: str  # high | medium | low
    body: str  # markdown body after front-matter
    path: Path | None
    tokens: frozenset[str] = field(default_factory=frozenset)

    def format_for_prompt(self) -> str:
        """Format the entry as a few-shot reference block."""
        return (
            f"## Reference: corpus #{self.id} — {self.title}\n"
            f"[quadrant: {self.quadrant}; principle: {self.principle}; "
            f"quality: {self.quality}]\n\n"
            f"{self.body.strip()}\n"
        )


def _tokenize(text: str) -> set[str]:
    """Lowercase + word-tokenize + stop-word strip + length>=3."""
    return {
        t for t in _TOKEN_RE.findall(text.lower())
        if t not in _STOP_WORDS and len(t) >= 3
    }


def _parse_front_matter(raw: str) -> tuple[dict[str, str], str]:
    """Parse YAML-ish front-matter. Hand-rolled to avoid PyYAML dependency."""
    match = _FRONT_MATTER_RE.match(raw)
    if not match:
        raise ValueError("missing front-matter")
    block = match.group(1)
    body = raw[match.end():]
    fm: dict[str, str] = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, val = line.partition(":")
        fm[key.strip()] = val.strip()
    return fm, body


def load_corpus(entries_dir: Path | _DirLike) -> list[CorpusEntry]:
    """Load all corpus entries from a directory or package resource."""
    entries: list[CorpusEntry] = []
    if isinstance(entries_dir, Path):
        items: list[tuple[str, _TextReadable, Path | None]] = [
            (p.name, p, p) for p in sorted(entries_dir.glob("*.md"))
        ]
    else:
        # importlib.resources Traversable
        items = []
        for p in entries_dir.iterdir():
            name = getattr(p, "name", "")
            if name.endswith(".md"):
                items.append((name, p, None))
        items.sort(key=lambda x: x[0])

    for name, readable, real_path in items:
        raw = readable.read_text(encoding="utf-8")
        try:
            fm, body = _parse_front_matter(raw)
        except ValueError:
            # Skip files without front-matter (e.g. README in entries dir).
            continue
        entry = CorpusEntry(
            id=str(fm.get("id", "")).zfill(2),
            title=fm.get("title", Path(name).stem),
            quadrant=fm.get("quadrant", ""),
            principle=fm.get("principle", ""),
            source=fm.get("source", ""),
            quality=fm.get("quality", "medium"),
            body=body,
            path=real_path,
        )
        # Cache tokenization. Title gets double weight via duplication;
        # tags (quadrant, principle) get encoded as their own tokens.
        token_text = (
            f"{entry.title} {entry.title} "
            f"{entry.quadrant} {entry.principle} "
            f"{entry.body}"
        )
        entry.tokens = frozenset(_tokenize(token_text))
        entries.append(entry)
    return entries


# Per-template principle boosts, drawn verbatim from each template's
# "Notes for the harness" section. These are the corpus-author-stated
# retrieval biases that the harness honors.
_TEMPLATE_PRINCIPLE_BOOSTS: dict[str, dict[str, float]] = {
    "scope-this-idea": {
        "bring_your_own_imagination": 1.4,
        "verification_first": 1.2,
    },
    "audit-this-plan": {
        "verification_first": 1.4,
        "legible_failure": 1.3,
    },
    "audit-this-visual": {
        "verification_first": 1.4,
        "counter_observation": 1.3,
    },
    "is-this-worth-doing": {
        "counter_observation": 1.4,
        "bring_your_own_imagination": 1.3,
    },
    "what-should-we-do-next": {
        "bring_your_own_imagination": 1.3,
        "cross_project_compounding": 1.4,
    },
    "review-from-different-angle": {
        "counter_observation": 1.5,
    },
}

_QUALITY_MULT = {"high": 1.0, "medium": 0.7, "low": 0.35}


def score_entry(
    entry: CorpusEntry,
    query_tokens: set[str],
    template: str | None = None,
) -> float:
    """Score one entry against the query.

    Score = (token-overlap-count) × (quality multiplier) × (template boost).

    Token overlap counts how many query tokens appear in the entry's
    tokenized representation (which already double-weights the title and
    inlines the quadrant + principle tags). Quality and template boost
    are multiplicative — high-quality entries dominate; medium thicken;
    low only surface when nothing else matches.
    """
    if not query_tokens:
        return 0.0
    overlap = len(query_tokens & entry.tokens)
    if overlap == 0:
        return 0.0
    score = float(overlap)
    score *= _QUALITY_MULT.get(entry.quality, 0.7)
    if template:
        boost = _TEMPLATE_PRINCIPLE_BOOSTS.get(template, {}).get(entry.principle, 1.0)
        score *= boost
    return score


def retrieve(
    entries: Iterable[CorpusEntry],
    query: str,
    template: str | None = None,
    top_k: int = 5,
) -> list[CorpusEntry]:
    """Top-k retrieval by tag+keyword overlap. Returns at most top_k entries.

    Empty query or zero-overlap query returns []. The harness must handle
    that case; the right shape is "no corpus retrieved" not "fallback
    arbitrary entries", since arbitrary corpus entries dilute the framework
    register more than they help.
    """
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []
    scored = [
        (score_entry(e, query_tokens, template), e)
        for e in entries
    ]
    scored.sort(key=lambda x: (-x[0], x[1].id))
    top = [e for s, e in scored if s > 0][:top_k]
    return top
