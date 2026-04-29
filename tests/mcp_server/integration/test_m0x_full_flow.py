"""Integration tests for M0.X tools through the FastMCP protocol.

Boots `build_app()` and connects an in-process `fastmcp.Client`. Tests
the full MCP round trip — what an external client (Claude.ai, Telegram
bot, MCP CLI) would actually experience — without HTTP/auth/middleware
overhead.

Per LL-M4-PHASE-A-001: integration tests must assert content of
returned payloads (not just shape) so contract drift is caught.
"""
from __future__ import annotations

import json
from typing import Any, AsyncIterator

import pytest_asyncio
from fastmcp import Client


def _unwrap(result: Any) -> Any:
    """Normalize FastMCP result to the plain payload dict.

    FastMCP wraps tool results in a CallToolResult; the actual dict the
    tool returned lives in `.data` (structured) or in `.content[0].text`
    (text-fallback) depending on the FastMCP version. Try both.
    """
    if hasattr(result, "data") and result.data is not None:
        return result.data
    if hasattr(result, "content"):
        content = result.content
        if content and hasattr(content[0], "text"):
            return json.loads(content[0].text)
    return result


@pytest_asyncio.fixture
async def mcp_client(patched_db: None) -> AsyncIterator["Client[Any]"]:
    """In-process MCP client connected to a freshly-built app.

    `patched_db` runs first so by the time `build_app()` is called the
    production db_mod is already pointing at the test pool — any tool
    invocation through the client lands on `pretel_os_test`.
    """
    # Import inside the fixture so the patched module state is in place
    from mcp_server.main import build_app

    app = build_app()
    async with Client(app) as client:
        yield client


async def test_all_18_m0x_tools_callable_through_mcp(mcp_client: "Client[Any]") -> None:
    """Smoke: every M0.X tool registers via FastMCP and is discoverable."""
    tools = await mcp_client.list_tools()
    names = {t.name for t in tools}

    expected = {
        "preference_set", "preference_get", "preference_list", "preference_unset",
        "task_create", "task_list", "task_update", "task_close", "task_reopen",
        "router_feedback_record", "router_feedback_review",
        "decision_record", "decision_search", "decision_supersede",
        "best_practice_record", "best_practice_search",
        "best_practice_deactivate", "best_practice_rollback",
    }
    missing = expected - names
    assert not missing, f"Tools missing from MCP registry: {missing}"
    assert len(expected) == 18


async def test_preference_set_through_mcp_protocol(mcp_client: "Client[Any]") -> None:
    """Full round-trip via MCP: payload fields, not just status."""
    result = await mcp_client.call_tool(
        "preference_set",
        {"category": "language", "key": "primary", "value": "es"},
    )
    payload = _unwrap(result)

    assert payload["status"] == "ok"
    assert payload["action"] == "inserted"
    assert isinstance(payload["id"], str)
    assert len(payload["id"]) == 36  # uuid string


async def test_decision_record_through_mcp_returns_embedding_metadata(
    mcp_client: "Client[Any]", patched_embed: Any
) -> None:
    """Content assertion (LL-M4-PHASE-A-001): payload includes
    embedding_queued flag accurately reflecting the embed call result.
    """
    result = await mcp_client.call_tool(
        "decision_record",
        {
            "bucket": "personal",
            "project": "pretel-os",
            "title": "MCP integration test ADR",
            "context": "ctx",
            "decision": "dec",
            "consequences": "csq",
        },
    )
    payload = _unwrap(result)

    assert payload["status"] == "ok"
    assert payload["embedding_queued"] is False  # patched_embed provides a vector
    assert isinstance(payload["id"], str)

    # Cleanup — decisions is NOT in the autotruncate list
    from psycopg_pool import AsyncConnectionPool
    from mcp_server import db as db_mod
    pool: AsyncConnectionPool = db_mod.get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM pending_embeddings WHERE target_id = %s", (payload["id"],))
            await cur.execute("DELETE FROM decisions WHERE id = %s", (payload["id"],))


async def test_degraded_mode_through_mcp(
    mcp_client: "Client[Any]", db_unhealthy: None, journal_dir: Any
) -> None:
    """End-to-end degraded mode: DB marked unhealthy → tool call returns
    {status:'degraded'} with journal_id, journal file written to tmp."""
    result = await mcp_client.call_tool(
        "preference_set",
        {"category": "language", "key": "primary", "value": "es"},
    )
    payload = _unwrap(result)

    assert payload["status"] == "degraded"
    assert "journal_id" in payload
    assert payload["degraded_reason"] == "db_unavailable"

    # Verify journal file exists in the tmp dir and contains the operation
    files = list(journal_dir.glob("*.jsonl"))
    assert len(files) == 1, f"expected 1 journal file, got {len(files)}: {files}"
    contents = files[0].read_text()
    assert "preference_set" in contents
    assert "language" in contents
    # Verify journal_id from response matches a line in the file
    assert payload["journal_id"] in contents
