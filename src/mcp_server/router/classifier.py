"""Public Router classifier entry point (Phase A).

Calls LiteLLM via chat_json against the `classifier_default` alias,
validates the response against the schema documented in spec.md §5.1,
and returns the parsed dict alongside the per-call telemetry record.

Schema validation is strict: any deviation raises ClassifierSchemaError
with parsed_response and telemetry attached. The orchestrator (Phase E)
catches all ClassifierError subclasses and falls through to the rule-
based fallback per CONSTITUTION §8.43.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .exceptions import ClassifierSchemaError
from .litellm_client import ChatJsonTelemetry, chat_json

CLASSIFIER_MAX_TOKENS = 800
CLASSIFIER_TIMEOUT_MS = 5000

_VALID_BUCKETS: frozenset[str | None] = frozenset(
    {"personal", "business", "scout", None}
)
_VALID_COMPLEXITY: frozenset[str] = frozenset({"LOW", "MEDIUM", "HIGH"})

_PROMPT_PATH = Path(__file__).parent / "prompts" / "classify.txt"


def _load_system_prompt() -> str:
    """Read the classifier system prompt from disk.

    The prompt lives outside the .py file to allow operators to tweak it
    via git/diff review without touching code.
    """
    return _PROMPT_PATH.read_text(encoding="utf-8")


def _validate_response(
    parsed: dict[str, Any],
    telemetry: ChatJsonTelemetry,
) -> None:
    """Strict schema validation per spec.md §5.1.

    Raises ClassifierSchemaError with the parsed dict and telemetry
    preserved so the orchestrator can persist the failure to llm_calls
    and routing_logs before falling through to the rule-based fallback.
    """
    required_keys = {
        "bucket",
        "project",
        "skill",
        "complexity",
        "needs_lessons",
        "confidence",
    }
    actual_keys = set(parsed.keys())
    missing = required_keys - actual_keys
    if missing:
        raise ClassifierSchemaError(
            f"missing required keys: {sorted(missing)}",
            parsed_response=parsed,
            telemetry=telemetry,
        )

    if parsed["bucket"] not in _VALID_BUCKETS:
        valid_buckets = sorted(b for b in _VALID_BUCKETS if b is not None)
        raise ClassifierSchemaError(
            f"bucket must be one of {valid_buckets} or null, got {parsed['bucket']!r}",
            parsed_response=parsed,
            telemetry=telemetry,
        )

    if parsed["project"] is not None:
        raise ClassifierSchemaError(
            f"project must be null in v1, got {parsed['project']!r}",
            parsed_response=parsed,
            telemetry=telemetry,
        )
    if parsed["skill"] is not None:
        raise ClassifierSchemaError(
            f"skill must be null in v1, got {parsed['skill']!r}",
            parsed_response=parsed,
            telemetry=telemetry,
        )

    if parsed["complexity"] not in _VALID_COMPLEXITY:
        raise ClassifierSchemaError(
            f"complexity must be one of {sorted(_VALID_COMPLEXITY)}, got {parsed['complexity']!r}",
            parsed_response=parsed,
            telemetry=telemetry,
        )

    if not isinstance(parsed["needs_lessons"], bool):
        raise ClassifierSchemaError(
            f"needs_lessons must be bool, got {type(parsed['needs_lessons']).__name__}",
            parsed_response=parsed,
            telemetry=telemetry,
        )

    confidence = parsed["confidence"]
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        raise ClassifierSchemaError(
            f"confidence must be numeric, got {type(confidence).__name__}",
            parsed_response=parsed,
            telemetry=telemetry,
        )
    if not (0.0 <= float(confidence) <= 1.0):
        raise ClassifierSchemaError(
            f"confidence must be in [0.0, 1.0], got {confidence}",
            parsed_response=parsed,
            telemetry=telemetry,
        )


def classify(
    message: str,
    l0_content: str | None = None,
    session_excerpt: str | None = None,
    request_id: str | None = None,
) -> tuple[dict[str, Any], ChatJsonTelemetry]:
    """Classify the operator's message for context routing.

    Args:
        message: The operator's current turn (raw text).
        l0_content: Future use for project/skill scoping; ignored in v1.
        session_excerpt: Recent session ledger excerpt; appended to the
            user message if provided. Helps disambiguate follow-up turns
            that lack standalone signal.
        request_id: Caller-provided correlation id for telemetry; not
            used by chat_json directly but accepted for forward
            compatibility with the orchestrator (Phase E).

    Returns:
        Tuple of (validated dict per spec §5.1, telemetry record).

    Raises:
        ClassifierError or any subclass — caller falls through to the
        rule-based fallback per CONSTITUTION §8.43.
    """
    if not isinstance(message, str) or not message.strip():
        raise ClassifierSchemaError(
            "message must be a non-empty string",
            parsed_response=None,
            telemetry=None,
        )

    system_prompt = _load_system_prompt()

    if session_excerpt:
        user_content = (
            f"Recent session excerpt:\n{session_excerpt}\n\n"
            f"Current turn:\n{message}"
        )
    else:
        user_content = message

    _ = l0_content
    _ = request_id

    parsed, telemetry = chat_json(
        model_alias="classifier_default",
        system=system_prompt,
        user=user_content,
        timeout_ms=CLASSIFIER_TIMEOUT_MS,
        max_tokens=CLASSIFIER_MAX_TOKENS,
    )

    _validate_response(parsed, telemetry)

    return parsed, telemetry
