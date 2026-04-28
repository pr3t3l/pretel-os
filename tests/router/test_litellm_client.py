"""Unit tests for `src.mcp_server.router.litellm_client.chat_json`.

Covers the retry policy added in A.4.2: success on first try,
retry-then-success on transport error, persistent transport failure.
"""
from __future__ import annotations

import os
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import httpx
import pytest
from openai import APIConnectionError

from src.mcp_server.router import litellm_client
from src.mcp_server.router.exceptions import ClassifierTransportError


@pytest.fixture(autouse=True)
def _set_api_key(monkeypatch):
    monkeypatch.setenv("LITELLM_API_KEY", "test-key")


def _fake_response(content: str):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


def _conn_error() -> APIConnectionError:
    return APIConnectionError(request=httpx.Request("POST", "http://127.0.0.1:4000/x"))


def test_success_first_try():
    fake_create = MagicMock(return_value=_fake_response('{"reply": "pong"}'))
    fake_client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=fake_create))
    )
    with patch.object(litellm_client, "_get_client", return_value=fake_client):
        result = litellm_client.chat_json(
            "classifier_default", "sys", "user", timeout_ms=1000, max_tokens=20
        )
    assert result == {"reply": "pong"}
    assert fake_create.call_count == 1


def test_retry_on_transport_error():
    fake_create = MagicMock(
        side_effect=[_conn_error(), _fake_response('{"reply": "pong"}')]
    )
    fake_client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=fake_create))
    )
    with patch.object(litellm_client, "_get_client", return_value=fake_client), patch.object(
        litellm_client.time, "sleep"
    ) as fake_sleep:
        result = litellm_client.chat_json(
            "classifier_default", "sys", "user", timeout_ms=1000, max_tokens=20
        )
    assert result == {"reply": "pong"}
    assert fake_create.call_count == 2
    fake_sleep.assert_called_once_with(litellm_client._RETRY_DELAY_S)


def test_persistent_transport_error():
    fake_create = MagicMock(side_effect=[_conn_error(), _conn_error()])
    fake_client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=fake_create))
    )
    with patch.object(litellm_client, "_get_client", return_value=fake_client), patch.object(
        litellm_client.time, "sleep"
    ):
        with pytest.raises(ClassifierTransportError) as exc_info:
            litellm_client.chat_json(
                "classifier_default", "sys", "user", timeout_ms=1000, max_tokens=20
            )
    assert "after 2 attempts" in str(exc_info.value)
    assert fake_create.call_count == 2
