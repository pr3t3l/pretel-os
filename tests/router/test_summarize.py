"""Tests for summarize_oversize (B.7).

Fast unit tests use monkeypatch on the chat_json helper — no real LLM
calls. ONE @pytest.mark.slow integration test exercises real
classifier_default to confirm prompt + parsing wiring.
"""
from __future__ import annotations

import os

import pytest

from mcp_server.router.exceptions import (
    ClassifierSchemaError,
    ClassifierTransportError,
)
from mcp_server.router.summarize import summarize_oversize


def _real_litellm_key() -> str | None:
    """Read LITELLM_MASTER_KEY from ~/.env.litellm (mirror of Phase A pattern)."""
    path = os.path.expanduser("~/.env.litellm")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        for line in f:
            if line.startswith("LITELLM_MASTER_KEY="):
                return line.split("=", 1)[1].strip()
    return None


def _fake_telemetry() -> object:
    """Build a stub telemetry object that satisfies typing without requiring
    full ChatJsonTelemetry construction in unit tests."""
    class _T:
        pass
    return _T()


# -----------------------------------------------------------------------------
# Happy path: chat_json returns {"summary": "..."} -> we get the string back
# -----------------------------------------------------------------------------


def test_happy_path_returns_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_chat_json(model_alias, system, user, timeout_ms, max_tokens):
        captured["model_alias"] = model_alias
        captured["max_tokens"] = max_tokens
        captured["user"] = user
        return ({"summary": "compressed content"}, _fake_telemetry())

    monkeypatch.setattr(
        "mcp_server.router.summarize.chat_json", fake_chat_json,
    )

    result = summarize_oversize("a long paragraph " * 50, target_tokens=200)

    assert result == "compressed content"
    assert captured["model_alias"] == "classifier_default"
    # max_tokens is at least target * 1.2 (=240) but floor of 256 wins.
    assert isinstance(captured["max_tokens"], int)
    assert captured["max_tokens"] >= 256
    # User message includes the TARGET_TOKENS preamble.
    assert "TARGET_TOKENS: 200" in str(captured["user"])
    assert "CONTENT:" in str(captured["user"])


# -----------------------------------------------------------------------------
# max_tokens scales with target above the 256 floor
# -----------------------------------------------------------------------------


def test_max_tokens_scales_above_floor(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_chat_json(model_alias, system, user, timeout_ms, max_tokens):
        captured["max_tokens"] = max_tokens
        return ({"summary": "x"}, _fake_telemetry())

    monkeypatch.setattr(
        "mcp_server.router.summarize.chat_json", fake_chat_json,
    )

    summarize_oversize("content", target_tokens=1000)
    assert captured["max_tokens"] == 1200  # 1000 * 1.2


# -----------------------------------------------------------------------------
# Schema deviation: chat_json returns a dict but missing 'summary' key
# -----------------------------------------------------------------------------


def test_missing_summary_key_raises_schema_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_chat_json(model_alias, system, user, timeout_ms, max_tokens):
        return ({"text": "wrong key"}, _fake_telemetry())

    monkeypatch.setattr(
        "mcp_server.router.summarize.chat_json", fake_chat_json,
    )

    with pytest.raises(ClassifierSchemaError) as exc_info:
        summarize_oversize("content", target_tokens=200)
    assert "summary" in str(exc_info.value)


# -----------------------------------------------------------------------------
# Schema deviation: 'summary' is non-string
# -----------------------------------------------------------------------------


def test_non_string_summary_raises_schema_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_chat_json(model_alias, system, user, timeout_ms, max_tokens):
        return ({"summary": ["a", "b"]}, _fake_telemetry())

    monkeypatch.setattr(
        "mcp_server.router.summarize.chat_json", fake_chat_json,
    )

    with pytest.raises(ClassifierSchemaError):
        summarize_oversize("content", target_tokens=200)


# -----------------------------------------------------------------------------
# Underlying transport errors propagate unchanged
# -----------------------------------------------------------------------------


def test_transport_error_propagates(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_chat_json(model_alias, system, user, timeout_ms, max_tokens):
        raise ClassifierTransportError("upstream down")

    monkeypatch.setattr(
        "mcp_server.router.summarize.chat_json", fake_chat_json,
    )

    with pytest.raises(ClassifierTransportError):
        summarize_oversize("content", target_tokens=200)


# -----------------------------------------------------------------------------
# Slow integration test: real LLM call
# -----------------------------------------------------------------------------


@pytest.mark.slow
def test_real_classifier_compresses_paragraph(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exercise the prompt + parsing against live classifier_default.

    Asserts the summary is shorter than the input and contains at least
    one signal-bearing keyword. Cost: ~$0.0005 per run.
    """
    key = _real_litellm_key()
    if not key:
        pytest.skip("real LITELLM_MASTER_KEY not present in ~/.env.litellm")
    monkeypatch.setenv("LITELLM_API_KEY", key)

    long_content = (
        "# Architectural decision: Postgres for embeddings\n\n"
        "We evaluated SQLite, DuckDB, Pinecone, and Postgres for the "
        "embeddings store. Postgres won on three criteria: a single "
        "operational surface, mature pgvector extension, and a "
        "transactional model that lets writes and reads share consistency "
        "guarantees. The downsides — manual index tuning at scale, no "
        "serverless tier on our self-host plan, and a more verbose client "
        "library — were judged tolerable at the current data volume "
        "(<5K vectors per table). Pinecone was rejected for cost. "
        "DuckDB was rejected for lack of a vector-search extension at "
        "evaluation time. SQLite was rejected because the existing "
        "Postgres deployment already serves five other production tables. "
    ) * 5  # ~500 tokens of repeated content

    result = summarize_oversize(long_content, target_tokens=150)

    assert isinstance(result, str)
    assert len(result) < len(long_content), (
        f"summary not shorter: {len(result)} vs {len(long_content)}"
    )
    # Signal keywords from the input must survive compression.
    lowered = result.lower()
    assert "postgres" in lowered or "pgvector" in lowered, (
        f"summary lost the load-bearing topic: {result!r}"
    )
