"""Thin wrapper around the OpenAI SDK pointing at the LiteLLM proxy.

Exposes a single function `chat_json` that issues a JSON-mode chat
completion against `http://127.0.0.1:4000` and returns the parsed dict.

SDK exceptions are converted to typed `Classifier*` exceptions per
`src/mcp_server/router/exceptions.py`. Schema validation is deferred to
`classifier.py` (Phase A.5); this module only guarantees the response
parses as JSON.

Authority: specs/router/spec.md §5.3 (call shape), §10 (failure modes).
"""
from __future__ import annotations

import json
import os
import time

from openai import (
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    OpenAI,
)

from .exceptions import (
    ClassifierParseError,
    ClassifierTimeout,
    ClassifierTransportError,
)

_BASE_URL = "http://127.0.0.1:4000"
_MAX_ATTEMPTS = 2
_RETRY_DELAY_S = 0.5


def _get_client() -> OpenAI:
    api_key = os.environ.get("LITELLM_API_KEY")
    if not api_key:
        raise RuntimeError(
            "LITELLM_API_KEY is not set. Export it from ~/.env.litellm "
            "before calling the classifier."
        )
    return OpenAI(base_url=_BASE_URL, api_key=api_key)


def chat_json(
    model_alias: str,
    system: str,
    user: str,
    timeout_ms: int = 3000,
    max_tokens: int = 300,
) -> dict:
    """Call LiteLLM proxy with JSON response mode.

    Args:
        model_alias: LiteLLM alias (e.g. 'classifier_default').
        system: system prompt content.
        user: user message content.
        timeout_ms: request timeout in milliseconds.
        max_tokens: response token limit.

    Returns:
        Parsed dict from the JSON response content.

    Raises:
        ClassifierTimeout: when the call exceeds timeout_ms.
        ClassifierTransportError: connection refused, 5xx persisting after retry, network error.
        ClassifierParseError: response content is not valid JSON. raw_response attached.

    Note: schema validation is the caller's job (classifier.py). This function only
    guarantees the response parses as JSON.
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

    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError) as e:
        raise ClassifierParseError(str(e), raw_response=content) from e
