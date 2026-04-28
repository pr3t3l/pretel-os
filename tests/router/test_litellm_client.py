"""Unit tests for `src.mcp_server.router.litellm_client.chat_json`.

A.4.2 covers retry policy on transport errors (success-first-try,
retry-then-success, persistent-failure).

A.4.3 covers truncation detection, content-filter handling, unknown
`finish_reason` values, defensive markdown-fence stripping, and
LiteLLM bug #18896 (reasoning_tokens=None on non-thinking models).

The integration test at the bottom calls the live LiteLLM proxy at
127.0.0.1:4000 with `classifier_default` (Claude Haiku 4.5 per current
config) and is automatically skipped when the proxy is unreachable or
the real master key is not present in `~/.env.litellm`.
"""
from __future__ import annotations

import os
import socket
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest
from openai import APIConnectionError

from src.mcp_server.router import litellm_client
from src.mcp_server.router.exceptions import (
    ClassifierContentFilterError,
    ClassifierParseError,
    ClassifierTransportError,
    ClassifierTruncatedError,
)
from src.mcp_server.router.litellm_client import ChatJsonTelemetry, chat_json


@pytest.fixture(autouse=True)
def _set_api_key(monkeypatch):
    monkeypatch.setenv("LITELLM_API_KEY", "test-key")


def _fake_response(
    content: str | None = '{"reply": "pong"}',
    finish_reason: str | None = "stop",
    *,
    prompt_tokens: int | None = 10,
    completion_tokens: int | None = 5,
    reasoning_tokens: int | None = 0,
    total_tokens: int | None = 15,
    completion_tokens_details_present: bool = True,
    model: str = "test-model",
    response_id: str = "test-id",
) -> SimpleNamespace:
    """Build a fake OpenAI-SDK chat completion response.

    Mirrors the attribute shape the real SDK emits closely enough for
    `_build_telemetry` to walk it via `getattr`.
    """
    if completion_tokens_details_present:
        details: SimpleNamespace | None = SimpleNamespace(
            reasoning_tokens=reasoning_tokens
        )
    else:
        details = None
    usage = SimpleNamespace(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        completion_tokens_details=details,
        prompt_tokens_details=None,
        cache_read_input_tokens=None,
        cache_creation_input_tokens=None,
    )
    response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=content),
                finish_reason=finish_reason,
            )
        ],
        usage=usage,
        model=model,
        id=response_id,
    )
    response.model_dump = lambda: {"id": response_id, "model": model}
    return response


def _conn_error() -> APIConnectionError:
    return APIConnectionError(
        request=httpx.Request("POST", "http://127.0.0.1:4000/x")
    )


def _patched_client(create_mock: MagicMock) -> Any:
    return SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create_mock))
    )


# ---------------------------------------------------------------------------
# A.4.2 tests (updated to expect tuple return)
# ---------------------------------------------------------------------------


def test_success_first_try():
    fake_create = MagicMock(return_value=_fake_response())
    with patch.object(
        litellm_client, "_get_client", return_value=_patched_client(fake_create)
    ):
        result, telemetry = chat_json(
            "classifier_default", "sys", "user", timeout_ms=1000, max_tokens=20
        )
    assert result == {"reply": "pong"}
    assert fake_create.call_count == 1
    assert isinstance(telemetry, ChatJsonTelemetry)
    assert telemetry.finish_reason == "stop"
    assert telemetry.truncated is False
    assert telemetry.near_truncation is False


def test_retry_on_transport_error():
    fake_create = MagicMock(side_effect=[_conn_error(), _fake_response()])
    with patch.object(
        litellm_client, "_get_client", return_value=_patched_client(fake_create)
    ), patch.object(litellm_client.time, "sleep") as fake_sleep:
        result, telemetry = chat_json(
            "classifier_default", "sys", "user", timeout_ms=1000, max_tokens=20
        )
    assert result == {"reply": "pong"}
    assert fake_create.call_count == 2
    fake_sleep.assert_called_once_with(litellm_client._RETRY_DELAY_S)
    assert isinstance(telemetry, ChatJsonTelemetry)
    assert telemetry.finish_reason == "stop"
    assert telemetry.truncated is False
    assert telemetry.near_truncation is False


def test_persistent_transport_error():
    fake_create = MagicMock(side_effect=[_conn_error(), _conn_error()])
    with patch.object(
        litellm_client, "_get_client", return_value=_patched_client(fake_create)
    ), patch.object(litellm_client.time, "sleep"):
        with pytest.raises(ClassifierTransportError) as exc_info:
            chat_json(
                "classifier_default", "sys", "user", timeout_ms=1000, max_tokens=20
            )
    assert "after 2 attempts" in str(exc_info.value)
    assert fake_create.call_count == 2


# ---------------------------------------------------------------------------
# A.4.3 tests
# ---------------------------------------------------------------------------


def test_truncation_max_tokens():
    fake_create = MagicMock(
        return_value=_fake_response(
            content='{"reply": "incomp',
            finish_reason="length",
            completion_tokens=200,
            reasoning_tokens=0,
        )
    )
    with patch.object(
        litellm_client, "_get_client", return_value=_patched_client(fake_create)
    ):
        with pytest.raises(ClassifierTruncatedError) as exc_info:
            chat_json(
                "classifier_default", "sys", "user", timeout_ms=1000, max_tokens=200
            )
    assert exc_info.value.telemetry is not None
    assert exc_info.value.telemetry.truncation_cause == "max_tokens"
    assert exc_info.value.telemetry.truncated is True
    assert exc_info.value.partial_content == '{"reply": "incomp'
    assert exc_info.value.telemetry.headroom_used_ratio == 1.0
    assert exc_info.value.telemetry.near_truncation is True


def test_truncation_reasoning_overflow():
    fake_create = MagicMock(
        return_value=_fake_response(
            content="",
            finish_reason="length",
            completion_tokens=500,
            reasoning_tokens=500,
        )
    )
    with patch.object(
        litellm_client, "_get_client", return_value=_patched_client(fake_create)
    ):
        with pytest.raises(ClassifierTruncatedError) as exc_info:
            chat_json(
                "classifier_default", "sys", "user", timeout_ms=1000, max_tokens=500
            )
    telemetry = exc_info.value.telemetry
    assert telemetry is not None
    assert telemetry.truncation_cause == "reasoning_overflow"
    assert telemetry.visible_output_tokens == 0


def test_content_filter():
    fake_create = MagicMock(
        return_value=_fake_response(content=None, finish_reason="content_filter")
    )
    with patch.object(
        litellm_client, "_get_client", return_value=_patched_client(fake_create)
    ):
        with pytest.raises(ClassifierContentFilterError) as exc_info:
            chat_json(
                "classifier_default", "sys", "user", timeout_ms=1000, max_tokens=20
            )
    assert exc_info.value.telemetry is not None
    assert exc_info.value.telemetry.finish_reason == "content_filter"


def test_unknown_finish_reason():
    fake_create = MagicMock(
        return_value=_fake_response(content=None, finish_reason="RECITATION")
    )
    with patch.object(
        litellm_client, "_get_client", return_value=_patched_client(fake_create)
    ):
        with pytest.raises(ClassifierTransportError) as exc_info:
            chat_json(
                "classifier_default", "sys", "user", timeout_ms=1000, max_tokens=20
            )
    assert "unexpected finish_reason='RECITATION'" in str(exc_info.value)
    assert "tools" not in str(exc_info.value)
    assert exc_info.value.telemetry is not None
    assert exc_info.value.telemetry.raw_finish_reason == "RECITATION"


def test_markdown_fences_stripped():
    fake_create = MagicMock(
        return_value=_fake_response(content='```json\n{"reply":"pong"}\n```')
    )
    with patch.object(
        litellm_client, "_get_client", return_value=_patched_client(fake_create)
    ):
        result, telemetry = chat_json(
            "classifier_default", "sys", "user", timeout_ms=1000, max_tokens=20
        )
    assert result == {"reply": "pong"}
    assert telemetry.finish_reason == "stop"


def test_markdown_fences_stripped_no_newlines():
    """Stripper must also handle the inline ```{...}``` form without newlines."""
    fake_create = MagicMock(
        return_value=_fake_response(content='```{"reply":"pong"}```')
    )
    with patch.object(
        litellm_client, "_get_client", return_value=_patched_client(fake_create)
    ):
        result, telemetry = chat_json(
            "classifier_default", "sys", "user", timeout_ms=1000, max_tokens=20
        )
    assert result == {"reply": "pong"}
    assert telemetry.finish_reason == "stop"


def test_telemetry_reasoning_tokens_none_handled():
    """LiteLLM bug #18896: completion_tokens_details may be None on non-thinking models."""
    fake_create = MagicMock(
        return_value=_fake_response(completion_tokens_details_present=False)
    )
    with patch.object(
        litellm_client, "_get_client", return_value=_patched_client(fake_create)
    ):
        result, telemetry = chat_json(
            "classifier_default", "sys", "user", timeout_ms=1000, max_tokens=20
        )
    assert result == {"reply": "pong"}
    assert telemetry.reasoning_tokens == 0


# ---------------------------------------------------------------------------
# Integration test (live LiteLLM proxy)
# ---------------------------------------------------------------------------


def _proxy_reachable(host: str = "127.0.0.1", port: int = 4000, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _real_litellm_key() -> str | None:
    path = os.path.expanduser("~/.env.litellm")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        for line in f:
            if line.startswith("LITELLM_MASTER_KEY="):
                return line.split("=", 1)[1].strip()
    return None


@pytest.mark.skipif(
    not _proxy_reachable(), reason="LiteLLM proxy not reachable on 127.0.0.1:4000"
)
def test_integration_classifier_default_live(monkeypatch):
    key = _real_litellm_key()
    if not key:
        pytest.skip("real LITELLM_MASTER_KEY not present in ~/.env.litellm")
    monkeypatch.setenv("LITELLM_API_KEY", key)

    result, telemetry = chat_json(
        "classifier_default",
        'You return JSON like {"reply": "pong"} only.',
        "ping",
        timeout_ms=10000,
        max_tokens=200,
    )
    assert isinstance(result, dict)
    assert telemetry.finish_reason == "stop"
    assert telemetry.reasoning_tokens == 0
    assert isinstance(telemetry.model, str) and telemetry.model
    assert isinstance(telemetry.provider_metadata, dict)
    assert telemetry.provider_metadata
