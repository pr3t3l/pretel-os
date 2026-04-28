"""Unit tests for `src.mcp_server.router.classifier.classify`.

A.5.1 + A.5.2 cover input validation, output schema validation, and
telemetry passthrough. All tests mock `chat_json` at the classifier
module level — no live LiteLLM calls happen here. Live integration
against the 10 worked examples is A.6.1 (separate file).
"""
from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from src.mcp_server.router.classifier import classify
from src.mcp_server.router.exceptions import ClassifierSchemaError
from src.mcp_server.router.litellm_client import ChatJsonTelemetry


def _ok_telemetry() -> ChatJsonTelemetry:
    return ChatJsonTelemetry(
        finish_reason="stop",
        raw_finish_reason="stop",
        truncated=False,
        truncation_cause=None,
        prompt_tokens=900,
        completion_tokens=30,
        reasoning_tokens=0,
        visible_output_tokens=30,
        total_tokens=930,
        max_tokens_requested=800,
        headroom_used_ratio=30 / 800,
        near_truncation=False,
        cache_creation_tokens=0,
        cache_read_tokens=0,
        cache_hit=False,
        model="anthropic/claude-haiku-4-5",
        response_id="resp_test",
        provider_metadata={"id": "resp_test"},
    )


def _valid_response() -> dict[str, Any]:
    return {
        "bucket": "business",
        "project": None,
        "skill": None,
        "complexity": "HIGH",
        "needs_lessons": True,
        "confidence": 0.92,
    }


def _patch_chat_json(parsed: dict[str, Any], telemetry: ChatJsonTelemetry) -> Any:
    return patch(
        "src.mcp_server.router.classifier.chat_json",
        MagicMock(return_value=(parsed, telemetry)),
    )


def test_happy_path_business_high():
    parsed = _valid_response()
    telemetry = _ok_telemetry()
    with _patch_chat_json(parsed, telemetry) as mock_chat:
        result, returned_telemetry = classify("Help me debug the Forge pipeline batching issue")
    assert result == parsed
    assert returned_telemetry is telemetry
    assert mock_chat.call_count == 1
    kwargs = mock_chat.call_args.kwargs
    assert kwargs["model_alias"] == "classifier_default"
    assert kwargs["max_tokens"] == 800
    assert kwargs["timeout_ms"] == 5000


def test_happy_path_null_bucket():
    parsed = {
        "bucket": None,
        "project": None,
        "skill": None,
        "complexity": "LOW",
        "needs_lessons": False,
        "confidence": 0.45,
    }
    telemetry = _ok_telemetry()
    with _patch_chat_json(parsed, telemetry):
        result, _ = classify("ok")
    assert result["bucket"] is None
    assert result["complexity"] == "LOW"


def test_missing_required_key():
    parsed = _valid_response()
    del parsed["complexity"]
    telemetry = _ok_telemetry()
    with _patch_chat_json(parsed, telemetry):
        with pytest.raises(ClassifierSchemaError) as exc_info:
            classify("anything")
    assert "complexity" in str(exc_info.value)
    assert exc_info.value.parsed_response == parsed
    assert exc_info.value.telemetry is telemetry


def test_invalid_bucket_value():
    parsed = _valid_response()
    parsed["bucket"] = "freelance"
    telemetry = _ok_telemetry()
    with _patch_chat_json(parsed, telemetry):
        with pytest.raises(ClassifierSchemaError) as exc_info:
            classify("anything")
    assert "freelance" in str(exc_info.value)
    assert exc_info.value.parsed_response == parsed


def test_project_not_null_v1():
    parsed = _valid_response()
    parsed["project"] = "some-project"
    telemetry = _ok_telemetry()
    with _patch_chat_json(parsed, telemetry):
        with pytest.raises(ClassifierSchemaError) as exc_info:
            classify("anything")
    assert "v1" in str(exc_info.value)
    assert "some-project" in str(exc_info.value)


def test_confidence_out_of_range():
    parsed = _valid_response()
    parsed["confidence"] = 1.5
    telemetry = _ok_telemetry()
    with _patch_chat_json(parsed, telemetry):
        with pytest.raises(ClassifierSchemaError) as exc_info:
            classify("anything")
    assert "[0.0, 1.0]" in str(exc_info.value)


def test_needs_lessons_not_bool():
    parsed = _valid_response()
    parsed["needs_lessons"] = "true"
    telemetry = _ok_telemetry()
    with _patch_chat_json(parsed, telemetry):
        with pytest.raises(ClassifierSchemaError) as exc_info:
            classify("anything")
    assert "needs_lessons" in str(exc_info.value)
    assert "bool" in str(exc_info.value)


def test_empty_message_raises():
    mock_chat = MagicMock()
    with patch("src.mcp_server.router.classifier.chat_json", mock_chat):
        with pytest.raises(ClassifierSchemaError):
            classify("")
        with pytest.raises(ClassifierSchemaError):
            classify("   ")
    assert mock_chat.call_count == 0
