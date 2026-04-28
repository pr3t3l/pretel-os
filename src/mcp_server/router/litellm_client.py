"""Thin wrapper around the OpenAI SDK pointing at the LiteLLM proxy.

Exposes a single function `chat_json` that issues a JSON-mode chat
completion against `http://127.0.0.1:4000` and returns
`(parsed_dict, ChatJsonTelemetry)`.

Provider-agnostic: the function takes a LiteLLM model alias only and
never references concrete model names. Telemetry is extracted defensively
so a missing field on any provider (Anthropic, OpenAI, Gemini, etc.) does
not blow up the call site — every numeric token field can be `None`.

SDK exceptions and provider failure modes are converted to typed
`Classifier*` exceptions per `src/mcp_server/router/exceptions.py`. Schema
validation is deferred to `classifier.py` (Phase A.5); this module only
guarantees the response parses as JSON.

Authority: specs/router/spec.md §5.3 (call shape), §9.1/§9.2 (telemetry
contract for `routing_logs` and `llm_calls`), §10 (failure modes).
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any

from openai import (
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    OpenAI,
)

from .exceptions import (
    ClassifierContentFilterError,
    ClassifierParseError,
    ClassifierTimeout,
    ClassifierTransportError,
    ClassifierTruncatedError,
)

_BASE_URL = "http://127.0.0.1:4000"
_MAX_ATTEMPTS = 2
_RETRY_DELAY_S = 0.5

NEAR_TRUNCATION_THRESHOLD = 0.7
DEFAULT_MAX_TOKENS = 800


@dataclass
class ChatJsonTelemetry:
    """Per-call telemetry feeding `routing_logs` / `llm_calls` (spec §9).

    Every numeric token field may be `None` when the upstream provider
    omits it. Code consuming this dataclass MUST treat numeric fields as
    `Optional[int]` and not assume reporting parity across providers.
    """

    finish_reason: str
    raw_finish_reason: str | None
    truncated: bool
    truncation_cause: str | None

    prompt_tokens: int | None
    completion_tokens: int | None
    reasoning_tokens: int
    visible_output_tokens: int | None
    total_tokens: int | None
    max_tokens_requested: int
    headroom_used_ratio: float
    near_truncation: bool

    cache_creation_tokens: int
    cache_read_tokens: int
    cache_hit: bool

    model: str
    response_id: str | None

    provider_metadata: dict[str, Any] = field(default_factory=dict)


def _get_client() -> OpenAI:
    api_key = os.environ.get("LITELLM_API_KEY")
    if not api_key:
        raise RuntimeError(
            "LITELLM_API_KEY is not set. Export it from ~/.env.litellm "
            "before calling the classifier."
        )
    return OpenAI(base_url=_BASE_URL, api_key=api_key)


def _strip_markdown_fences(s: str) -> str:
    """Remove ```json...``` or ```...``` wrappers if present.

    Anthropic Claude occasionally wraps JSON in markdown fences despite
    `response_format={"type": "json_object"}` and explicit instructions
    in the system prompt. Strip them defensively before `json.loads`.
    """
    s = s.strip()
    if s.startswith("```"):
        if "\n" in s:
            s = s.split("\n", 1)[1]
        else:
            s = s[3:]
        if s.endswith("```"):
            s = s[:-3]
    return s.strip()


def _build_telemetry(
    response: Any,
    model_alias: str,
    max_tokens_requested: int,
) -> ChatJsonTelemetry:
    """Extract telemetry from an SDK response object defensively.

    Any provider-specific field may be missing or `None`; in particular
    LiteLLM bug #18896 emits `completion_tokens_details.reasoning_tokens
    = None` for non-thinking models, which the `or 0` coerces to 0.
    """
    choice = response.choices[0] if getattr(response, "choices", None) else None
    raw_finish = getattr(choice, "finish_reason", None) if choice else None
    finish_reason_norm = str(raw_finish) if raw_finish is not None else "stop"
    raw_finish_str = str(raw_finish) if raw_finish is not None else None

    usage = getattr(response, "usage", None)
    prompt_tokens = getattr(usage, "prompt_tokens", None) if usage else None
    completion_tokens = getattr(usage, "completion_tokens", None) if usage else None
    total_tokens = getattr(usage, "total_tokens", None) if usage else None

    details = (
        getattr(usage, "completion_tokens_details", None) if usage else None
    )
    reasoning_tokens = (
        (getattr(details, "reasoning_tokens", 0) or 0) if details else 0
    )

    if completion_tokens is not None:
        visible_output_tokens: int | None = max(
            0, completion_tokens - reasoning_tokens
        )
    else:
        visible_output_tokens = None

    anthropic_cache_read = (
        getattr(usage, "cache_read_input_tokens", 0) or 0 if usage else 0
    )
    prompt_details = getattr(usage, "prompt_tokens_details", None) if usage else None
    openai_cache_read = (
        (getattr(prompt_details, "cached_tokens", 0) or 0) if prompt_details else 0
    )
    cache_read_tokens = max(anthropic_cache_read, openai_cache_read)
    cache_creation_tokens = (
        getattr(usage, "cache_creation_input_tokens", 0) or 0 if usage else 0
    )
    cache_hit = cache_read_tokens > 0

    if completion_tokens is not None and max_tokens_requested > 0:
        headroom_used_ratio = completion_tokens / max_tokens_requested
    else:
        headroom_used_ratio = 0.0
    near_truncation = headroom_used_ratio > NEAR_TRUNCATION_THRESHOLD

    truncated = finish_reason_norm == "length"
    truncation_cause: str | None = None
    if truncated:
        if reasoning_tokens > 0 and (visible_output_tokens in (0, None)):
            truncation_cause = "reasoning_overflow"
        else:
            truncation_cause = "max_tokens"

    response_model = getattr(response, "model", None)
    model_name = response_model if response_model else model_alias
    response_id = getattr(response, "id", None)

    if hasattr(response, "model_dump"):
        try:
            provider_metadata = response.model_dump()
        except Exception:
            provider_metadata = {}
    else:
        provider_metadata = {}

    return ChatJsonTelemetry(
        finish_reason=finish_reason_norm,
        raw_finish_reason=raw_finish_str,
        truncated=truncated,
        truncation_cause=truncation_cause,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        reasoning_tokens=reasoning_tokens,
        visible_output_tokens=visible_output_tokens,
        total_tokens=total_tokens,
        max_tokens_requested=max_tokens_requested,
        headroom_used_ratio=headroom_used_ratio,
        near_truncation=near_truncation,
        cache_creation_tokens=cache_creation_tokens,
        cache_read_tokens=cache_read_tokens,
        cache_hit=cache_hit,
        model=str(model_name),
        response_id=str(response_id) if response_id is not None else None,
        provider_metadata=provider_metadata,
    )


def chat_json(
    model_alias: str,
    system: str,
    user: str,
    timeout_ms: int = 3000,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> tuple[dict[str, Any], ChatJsonTelemetry]:
    """Call LiteLLM proxy expecting a JSON-object response.

    Args:
        model_alias: LiteLLM alias (e.g. 'classifier_default'). Concrete
            model name is resolved by the proxy and surfaced via
            `telemetry.model`.
        system: system prompt content.
        user: user message content.
        timeout_ms: request timeout in milliseconds.
        max_tokens: response token limit (must accommodate any reasoning
            budget the provider needs — `DEFAULT_MAX_TOKENS=800` is a
            safe floor for both Claude Haiku 4.5 and Gemini 2.5 Flash).

    Returns:
        Tuple of (parsed dict, telemetry record).

    Raises:
        ClassifierTimeout: call exceeded `timeout_ms` (no retry).
        ClassifierTransportError: connection refused, persistent 5xx, or
            unexpected `finish_reason` (e.g. RECITATION, tool_calls).
        ClassifierTruncatedError: `finish_reason='length'`. `telemetry.
            truncation_cause` distinguishes 'max_tokens' from
            'reasoning_overflow'.
        ClassifierContentFilterError: provider safety filter blocked.
        ClassifierParseError: visible content is empty or not valid JSON.

    Note: schema validation is the caller's job (classifier.py). This
    function only guarantees the response parses as JSON.
    """
    client = _get_client()
    timeout_s = timeout_ms / 1000.0

    last_transport_error: Exception | None = None
    response = None
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            response = client.chat.completions.create(
                model=model_alias,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
                max_tokens=max_tokens,
                timeout=timeout_s,
            )
            break
        except APITimeoutError as e:
            raise ClassifierTimeout(str(e)) from e
        except (APIConnectionError, InternalServerError) as e:
            last_transport_error = e
            if attempt < _MAX_ATTEMPTS:
                time.sleep(_RETRY_DELAY_S)
                continue
            raise ClassifierTransportError(
                "transport failure after 2 attempts"
            ) from e

    if response is None:
        raise ClassifierTransportError(
            "transport failure after 2 attempts"
        ) from last_transport_error

    telemetry = _build_telemetry(response, model_alias, max_tokens)
    choice = response.choices[0]
    content = getattr(choice.message, "content", None)
    raw_finish = getattr(choice, "finish_reason", None)

    if raw_finish == "length":
        cause = telemetry.truncation_cause or "max_tokens"
        raise ClassifierTruncatedError(
            f"response truncated (cause={cause})",
            telemetry=telemetry,
            partial_content=content,
        )
    if raw_finish == "content_filter":
        raise ClassifierContentFilterError(
            "provider content filter blocked the response",
            telemetry=telemetry,
        )
    if raw_finish in ("tool_calls", "function_call"):
        raise ClassifierTransportError(
            f"unexpected finish_reason={raw_finish!r}: classifier never calls tools",
            telemetry=telemetry,
        )
    if raw_finish is not None and raw_finish != "stop":
        raise ClassifierTransportError(
            f"unexpected finish_reason={raw_finish!r}",
            telemetry=telemetry,
        )

    if content is None:
        raise ClassifierParseError(
            "response content is empty despite finish_reason='stop'",
            raw_response=None,
            telemetry=telemetry,
        )

    cleaned = _strip_markdown_fences(content)
    try:
        parsed = json.loads(cleaned)
    except (json.JSONDecodeError, TypeError) as e:
        raise ClassifierParseError(
            str(e),
            raw_response=content,
            telemetry=telemetry,
        ) from e

    return parsed, telemetry
