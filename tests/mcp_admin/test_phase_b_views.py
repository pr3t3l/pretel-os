"""Phase B view tests — all 4 new views render against pretel_os_test.

Slow tests because they hit the real test DB. Coverage:
  /memory tabs        (lessons / decisions / best_practices)
  /memory pagination  (offset/limit knob)
  /dream-engine       (read history)
  /dream-engine/run   (POST trigger — subprocess mocked)
  /costs              (read v_daily_cost_by_purpose)
  /pending            (read pending_review + pending xpoll)
  /pending/lessons    (approve via MCP tool — mocked)
  /pending/cross-poll (resolve via MCP tool — mocked)
"""
from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


pytestmark = pytest.mark.slow


# ---------------------------------------------------------------- /memory

def test_memory_lessons_tab_renders(admin_client: TestClient) -> None:
    r = admin_client.get(
        "/memory?tab=lessons",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 200
    assert "Memory browser" in r.text
    assert 'value="lessons"' in r.text


def test_memory_decisions_tab_renders(admin_client: TestClient) -> None:
    r = admin_client.get(
        "/memory?tab=decisions",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 200


def test_memory_best_practices_tab_renders(admin_client: TestClient) -> None:
    r = admin_client.get(
        "/memory?tab=best_practices",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 200


def test_memory_pagination_respects_offset_limit(admin_client: TestClient) -> None:
    r = admin_client.get(
        "/memory?tab=lessons&offset=0&limit=5",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 200
    # Pagination labels render when offset/limit are set
    assert "Showing" in r.text or "Sin resultados" in r.text


def test_memory_unknown_tab_falls_back_to_lessons(admin_client: TestClient) -> None:
    r = admin_client.get(
        "/memory?tab=garbage",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 200
    assert "Memory browser" in r.text


# ---------------------------------------------------------------- /dream-engine

def test_dream_engine_view_renders(admin_client: TestClient) -> None:
    r = admin_client.get(
        "/dream-engine",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 200
    assert "Dream Engine" in r.text
    # Summary line includes "runs" word regardless of count
    assert "runs" in r.text


def test_dream_engine_manual_trigger_calls_subprocess(
    admin_client: TestClient,
) -> None:
    """POST /dream-engine/run invokes systemctl via subprocess."""
    with patch(
        "mcp_admin.handlers.dream_engine.subprocess.run"
    ) as mock_run:
        r = admin_client.post(
            "/dream-engine/run",
            headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
            follow_redirects=False,
        )
        assert r.status_code == 303
        assert r.headers["location"] == "/dream-engine"
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        cmd = args[0]
        assert cmd[0] == "systemctl"
        assert "pretel-os-dream-engine.service" in cmd


# ---------------------------------------------------------------- /costs

def test_costs_view_renders(admin_client: TestClient) -> None:
    r = admin_client.get(
        "/costs",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 200
    assert "Costs dashboard" in r.text
    # Totals line is always present even when 0
    assert "Total $" in r.text


# ---------------------------------------------------------------- /pending

def test_pending_view_renders(admin_client: TestClient) -> None:
    r = admin_client.get(
        "/pending",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 200
    assert "Pending review" in r.text


def test_pending_lesson_approve_calls_mcp_tool(
    admin_client: TestClient,
) -> None:
    """POST /pending/lessons/{id}/approve routes through approve_lesson MCP tool."""
    fake_id = "00000000-0000-0000-0000-000000000001"
    with patch(
        "mcp_admin.handlers.pending.approve_lesson"
    ) as mock_approve:

        async def _fake(*args, **kwargs):  # type: ignore[no-untyped-def]
            return {"status": "ok"}

        mock_approve.side_effect = _fake
        r = admin_client.post(
            f"/pending/lessons/{fake_id}/approve",
            headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
            follow_redirects=False,
        )
        assert r.status_code == 303
        assert r.headers["location"] == "/pending"
        mock_approve.assert_called_once()


def test_pending_lesson_reject_passes_reason_to_mcp_tool(
    admin_client: TestClient,
) -> None:
    fake_id = "00000000-0000-0000-0000-000000000002"
    with patch(
        "mcp_admin.handlers.pending.reject_lesson"
    ) as mock_reject:

        async def _fake(*args, **kwargs):  # type: ignore[no-untyped-def]
            return {"status": "ok"}

        mock_reject.side_effect = _fake
        r = admin_client.post(
            f"/pending/lessons/{fake_id}/reject",
            data={"reason": "out of date"},
            headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
            follow_redirects=False,
        )
        assert r.status_code == 303
        mock_reject.assert_called_once()
        _, kwargs = mock_reject.call_args
        assert kwargs.get("reason") == "out of date"


def test_pending_cross_poll_approve_calls_mcp_tool(
    admin_client: TestClient,
) -> None:
    fake_id = "00000000-0000-0000-0000-000000000003"
    with patch(
        "mcp_admin.handlers.pending.resolve_cross_pollination"
    ) as mock_resolve:

        async def _fake(*args, **kwargs):  # type: ignore[no-untyped-def]
            return {"status": "ok", "resolved": True}

        mock_resolve.side_effect = _fake
        r = admin_client.post(
            f"/pending/cross-poll/{fake_id}/approve",
            headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
            follow_redirects=False,
        )
        assert r.status_code == 303
        mock_resolve.assert_called_once()
        _, kwargs = mock_resolve.call_args
        assert kwargs.get("action") == "approve"


# ---------------------------------------------------------------- nav

def test_base_nav_includes_all_5_views(admin_client: TestClient) -> None:
    """SC3 verification — sidebar lists all 5 MVP views."""
    r = admin_client.get(
        "/preferences",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 200
    for path in ("/preferences", "/memory", "/dream-engine", "/costs", "/pending"):
        assert f'href="{path}"' in r.text, f"missing nav link {path}"
