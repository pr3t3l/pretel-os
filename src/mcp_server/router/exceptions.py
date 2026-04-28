"""Typed exceptions raised by the Router classifier path.

The orchestrator (Phase E) catches the base `ClassifierError` and routes
to the rule-based fallback per CONSTITUTION §8.43. Subclasses exist so
operator-facing telemetry can distinguish the failure mode without parsing
exception messages.

A.4.3 added an optional `telemetry: ChatJsonTelemetry | None` kwarg on every
classifier exception so the orchestrator can persist `routing_logs` /
`llm_calls` rows even when the call failed (per spec.md §9.1, §9.2).
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .litellm_client import ChatJsonTelemetry


class ClassifierError(Exception):
    """Base for every Router classifier failure.

    Catch this in the orchestrator to fall through to the rule-based
    fallback classifier per CONSTITUTION §8.43.
    """

    def __init__(
        self,
        *args: object,
        telemetry: "ChatJsonTelemetry | None" = None,
    ) -> None:
        super().__init__(*args)
        self.telemetry = telemetry


class ClassifierTimeout(ClassifierError):
    """Raised when the LiteLLM call exceeds its configured timeout.

    Caught by the orchestrator as a `ClassifierError` to fall through to
    the rule-based fallback per CONSTITUTION §8.43.
    """


class ClassifierTransportError(ClassifierError):
    """Raised on transport-level failures talking to the LiteLLM proxy.

    Examples: connection refused, DNS failure, persistent 5xx, TLS
    handshake error, unexpected `finish_reason` (e.g. Gemini RECITATION,
    tool_calls when tools are not configured). Caught by the orchestrator
    as a `ClassifierError` to fall through to the rule-based fallback per
    CONSTITUTION §8.43.
    """


class ClassifierParseError(ClassifierError):
    """Raised when the LiteLLM response body is not valid JSON.

    The unparsed body is preserved on `raw_response` so the operator can
    debug provider-specific malformations (e.g. trailing commentary,
    truncated output). Caught by the orchestrator as a `ClassifierError`
    to fall through to the rule-based fallback per CONSTITUTION §8.43.
    """

    def __init__(
        self,
        *args: object,
        raw_response: str | None = None,
        telemetry: "ChatJsonTelemetry | None" = None,
    ) -> None:
        super().__init__(*args, telemetry=telemetry)
        self.raw_response = raw_response


class ClassifierSchemaError(ClassifierError):
    """Raised when a parsed response fails schema validation.

    Triggers: bucket not in {personal, business, scout, null}, complexity
    outside {LOW, MEDIUM, HIGH}, missing required field, confidence
    outside [0.0, 1.0], hallucinated project not present in L0.

    The decoded dict is preserved on `parsed_response` so the operator
    can inspect the exact violation. Caught by the orchestrator as a
    `ClassifierError` to fall through to the rule-based fallback per
    CONSTITUTION §8.43.
    """

    def __init__(
        self,
        *args: object,
        parsed_response: dict[str, Any] | None = None,
        telemetry: "ChatJsonTelemetry | None" = None,
    ) -> None:
        super().__init__(*args, telemetry=telemetry)
        self.parsed_response = parsed_response


class ClassifierTruncatedError(ClassifierError):
    """Raised when the model response was truncated (`finish_reason='length'`).

    `partial_content` carries whatever visible text the provider managed to
    emit before hitting the limit (may be empty when reasoning tokens
    consumed the entire budget — see `telemetry.truncation_cause`).
    Caught by the orchestrator as a `ClassifierError` to fall through to
    the rule-based fallback per CONSTITUTION §8.43.
    """

    def __init__(
        self,
        message: str,
        telemetry: "ChatJsonTelemetry | None" = None,
        partial_content: str | None = None,
    ) -> None:
        super().__init__(message, telemetry=telemetry)
        self.partial_content = partial_content


class ClassifierContentFilterError(ClassifierError):
    """Raised when a provider safety filter blocked the response.

    Distinct from `ClassifierTransportError` so the operator dashboard
    can surface safety blocks separately from infra failures. Caught by
    the orchestrator as a `ClassifierError` to fall through to the
    rule-based fallback per CONSTITUTION §8.43.
    """

    def __init__(
        self,
        message: str,
        telemetry: "ChatJsonTelemetry | None" = None,
    ) -> None:
        super().__init__(message, telemetry=telemetry)
