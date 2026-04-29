"""Over-budget layer compression helper (Phase B B.7).

Calls `chat_json('classifier_default', ...)` with the summarize prompt
from `prompts/summarize.txt`. The model returns `{"summary": "<text>"}`
and we extract the field.

Phase B's role per spec/router/spec.md §6.4: when a layer's content
exceeds its budget at read-time, the orchestrator (`assemble_bundle`)
calls this helper to compress to ≤80% of the target ceiling, replaces
the layer's blocks with the summarized content, and writes a `gotcha`
row suggesting the operator refactor the source. The gotcha-row write
is the orchestrator's responsibility, not this helper's.

Failure modes propagate the typed `Classifier*` exceptions from
`chat_json` unchanged — the caller decides whether to fall back to
truncation, surface a degraded response, or re-raise.
"""
from __future__ import annotations

from pathlib import Path

from mcp_server.router.litellm_client import chat_json


_PROMPT_PATH = Path(__file__).parent / "prompts" / "summarize.txt"


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def summarize_oversize(content: str, target_tokens: int) -> str:
    """Compress `content` to ~80% of `target_tokens` via classifier_default.

    Args:
        content: the over-budget layer content (markdown).
        target_tokens: the ceiling the layer must respect (cl100k_base).

    Returns:
        The compressed content as a string. Never returns None — on
        provider failure the underlying `chat_json` raises a typed
        Classifier* exception; the caller catches.
    """
    system = _load_prompt()
    user = (
        f"TARGET_TOKENS: {target_tokens}\n"
        f"CONTENT:\n{content}"
    )
    # max_tokens budget: a little above target so the model has room
    # to land at ~80%. Adding 20% headroom for the "summary" key,
    # quotes, escaping, and a small overshoot tolerance.
    max_tokens = max(int(target_tokens * 1.2), 256)
    result, _telemetry = chat_json(
        model_alias="classifier_default",
        system=system,
        user=user,
        timeout_ms=8000,
        max_tokens=max_tokens,
    )
    summary = result.get("summary")
    if not isinstance(summary, str):
        # Schema deviation — chat_json's parse succeeded (it returned a
        # dict) but the dict lacks the expected key. Treat as a parse
        # error from the caller's perspective.
        from mcp_server.router.exceptions import ClassifierSchemaError
        raise ClassifierSchemaError(
            f"summarize response missing 'summary' string field; got keys "
            f"{sorted(result.keys())!r}"
        )
    return summary
