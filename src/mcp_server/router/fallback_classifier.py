"""Pure-Python rule-based classifier for the LiteLLM-unreachable path.

Per spec §10.1: when `classify()` raises any `ClassifierError`, the
orchestrator falls through to `fallback_classify()`. This module is
deliberately I/O-free (no DB, no LLM, no embeddings) so it cannot
itself fail in the same way as the upstream classifier.

Output dict shape matches spec §5.1 exactly. `confidence` is fixed at
0.4 per spec §10. `complexity` never returns `HIGH` from rules — even
HIGH-keyword matches are capped at `MEDIUM` so the fallback path never
trips the budget-heavy HIGH RAG behavior with low-confidence rules.
"""
from __future__ import annotations

from .fallback_keywords import BUCKET_KEYWORDS, COMPLEXITY_KEYWORDS

_CONFIDENCE = 0.4


def _match_bucket(message_lower: str) -> str | None:
    """First bucket with any keyword match. Iteration = dict order."""
    for bucket, keywords in BUCKET_KEYWORDS.items():
        for keyword in keywords:
            if keyword in message_lower:
                return bucket
    return None


def _extract_projects(l0_content: str) -> list[str]:
    """Project slugs from a `## Projects` section's bullet list.

    Bullets are expected as ``- <slug>`` or ``- <slug> — <description>``;
    the slug is the first whitespace-delimited token after the dash.
    Returns an empty list if no `## Projects` heading is present.
    """
    projects: list[str] = []
    in_section = False
    for line in l0_content.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            in_section = stripped.lower() == "## projects"
            continue
        if not in_section:
            continue
        if stripped.startswith("- "):
            tokens = stripped[2:].split()
            if tokens:
                projects.append(tokens[0].lower())
    return projects


def _match_project(message_lower: str, l0_content: str) -> str | None:
    for slug in _extract_projects(l0_content):
        if slug in message_lower:
            return slug
    return None


def _match_complexity(message_lower: str) -> str:
    """HIGH keywords cap at MEDIUM; LOW keywords return LOW; default LOW."""
    if any(kw in message_lower for kw in COMPLEXITY_KEYWORDS["HIGH"]):
        return "MEDIUM"
    if any(kw in message_lower for kw in COMPLEXITY_KEYWORDS["LOW"]):
        return "LOW"
    return "LOW"


def fallback_classify(message: str, l0_content: str) -> dict[str, object]:
    """Rule-based classification when LiteLLM cannot be reached.

    Returns a dict matching spec.md §5.1. Pure: no DB, no LLM, no I/O
    beyond reading the strings passed in. `needs_lessons` is True only
    when bucket and project are both identified AND complexity is not
    LOW — otherwise the fallback would burn L4 cycles on greetings.
    """
    message_lower = message.lower()
    bucket = _match_bucket(message_lower)
    project = _match_project(message_lower, l0_content)
    complexity = _match_complexity(message_lower)
    needs_lessons = (
        bucket is not None
        and project is not None
        and complexity != "LOW"
    )
    return {
        "bucket": bucket,
        "project": project,
        "skill": None,
        "complexity": complexity,
        "needs_lessons": needs_lessons,
        "confidence": _CONFIDENCE,
    }
