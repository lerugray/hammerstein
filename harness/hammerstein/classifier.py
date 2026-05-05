"""Keyword-based template classifier.

Maps a user query to one of the five templates in `prompts/templates/`.
Default = `scope-this-idea` per `tech/STACK-DECISION.md` ("Default is
scope-this-idea if no clear classifier match").

The classifier deliberately uses simple keyword cues rather than an LLM
call. v0's classifier is itself ablation-friendly: per the
review-from-different-angle template's example 1, "the v0 benchmark on
prompt-only / corpus-only / 8B vs 70B" is supposed to surface which
component does the work. Adding LLM-classified template selection would
add a moving part this v0 measurement isn't ready to interpret.
"""

from __future__ import annotations

import re

TEMPLATES = (
    "scope-this-idea",
    "audit-this-plan",
    "is-this-worth-doing",
    "what-should-we-do-next",
    "review-from-different-angle",
)

# Cue patterns. First match wins; ordering matters — the more specific
# templates are checked before the more general ones.
_CUES: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "review-from-different-angle",
        re.compile(
            r"\b("
            r"counter[-\s]?(?:frame|argument|observation|view)|"
            r"steel[-\s]?man|"
            r"sanity[-\s]?check|"
            r"argument[s]?\s+against|"
            r"opposite\s+view|"
            r"sharper\s+reviewer|"
            r"different\s+angle|"
            r"strongest\s+(?:argument|case)\s+against|"
            r"second[-\s]?opinion|"
            r"push\s+back\s+on"
            r")\b",
            re.IGNORECASE,
        ),
    ),
    (
        "audit-this-plan",
        re.compile(
            r"(?:^|\n)\s*plan\s*[:\-]"  # "Plan: ..." at start of line
            r"|\b("
            r"audit\s+(?:this|the|my)\s+plan|"
            r"audit[-\s]?pass|"
            r"review\s+(?:this|the|my)\s+plan|"
            r"sanity[-\s]?audit|"
            r"failure\s+modes?|"
            r"verification\s+gates?|"
            r"plan\s+for\s+(?:the\s+)?(?:next|overnight|weekend)"
            r")\b",
            re.IGNORECASE,
        ),
    ),
    (
        "is-this-worth-doing",
        re.compile(
            r"\b("
            r"is\s+(?:this|it)\s+worth|"
            r"worth\s+(?:doing|building|paying|the)|"
            r"should\s+i\s+(?:build|buy|pay|subscribe|invest|spend)|"
            r"cost[-\s]?benefit|"
            r"return\s+on\s+investment|"
            r"\broi\b|"
            r"\$\d+|"
            r"\bbudget\b|"
            r"is\s+\w+\s+worth"
            r")\b",
            re.IGNORECASE,
        ),
    ),
    (
        "what-should-we-do-next",
        re.compile(
            r"\b("
            r"what\s+(?:should|shall)\s+(?:i|we)\s+do\s+next|"
            r"what['\s]s\s+next|"
            r"prioriti[sz]e|"
            r"priority\s+order|"
            r"ranked?\s+(?:list|priority|priorities)|"
            r"highest\s+leverage|"
            r"next\s+(?:move|moves|step|steps)|"
            r"options\s+(?:are|for|this\s+week)|"
            r"this\s+week['\s]s\s+(?:options|priorities)"
            r")\b",
            re.IGNORECASE,
        ),
    ),
    (
        "scope-this-idea",
        re.compile(
            r"\b("
            r"i['\s]m\s+thinking\s+(?:of|about)\s+building|"
            r"what\s+if\s+(?:we|i)\s+(?:built|made|added)|"
            r"i\s+want\s+to\s+build|"
            r"we\s+could\s+try|"
            r"scope\s+(?:this|the)\s+idea|"
            r"minimum\s+viable|"
            r"\bmvp\b|"
            r"smallest\s+version"
            r")\b",
            re.IGNORECASE,
        ),
    ),
)


def classify(query: str) -> str:
    """Pick a template for the query. Default: scope-this-idea."""
    if not query.strip():
        return "scope-this-idea"
    for template, pattern in _CUES:
        if pattern.search(query):
            return template
    return "scope-this-idea"
