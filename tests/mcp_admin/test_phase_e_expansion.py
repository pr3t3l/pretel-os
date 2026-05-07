"""Phase E expansion view tests — smoke for the 4 new list/overview views."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


pytestmark = pytest.mark.slow


# ---------------------------------------------------------------- /skills (list)

def test_skills_list_renders(admin_client: TestClient) -> None:
    r = admin_client.get(
        "/skills",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 200
    assert "Skills catalog" in r.text


def test_skills_list_with_bucket_filter(admin_client: TestClient) -> None:
    r = admin_client.get(
        "/skills?bucket=personal",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 200


# ---------------------------------------------------------------- /tools (list)

def test_tools_list_renders(admin_client: TestClient) -> None:
    r = admin_client.get(
        "/tools",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 200
    assert "Tools catalog" in r.text


# ---------------------------------------------------------------- /buckets

def test_buckets_view_renders(admin_client: TestClient) -> None:
    r = admin_client.get(
        "/buckets",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 200
    assert "Buckets" in r.text
    # 3 fixed buckets always present
    for b in ("personal", "business", "scout"):
        assert b in r.text


# ---------------------------------------------------------------- /workers

def test_workers_view_renders_with_subprocess_mocked(
    admin_client: TestClient,
) -> None:
    """systemctl is-active is called per row; mock to avoid timing flakiness."""
    class FakeRun:
        def __init__(self, stdout: str = "active") -> None:
            self.stdout = stdout
            self.returncode = 0

    with patch(
        "mcp_admin.handlers.workers.subprocess.run",
        return_value=FakeRun("active"),
    ):
        r = admin_client.get(
            "/workers",
            headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
        )
    assert r.status_code == 200
    assert "Chartered workers" in r.text
    assert "Dream Engine" in r.text
    assert "README consumer" in r.text
    assert "Auto-index on save" in r.text
    assert "Morning intelligence" in r.text


def test_workers_view_handles_systemctl_unavailable(
    admin_client: TestClient,
) -> None:
    """When systemctl is missing/timeout, the view still renders with 'unknown'."""
    with patch(
        "mcp_admin.handlers.workers.subprocess.run",
        side_effect=FileNotFoundError(),
    ):
        r = admin_client.get(
            "/workers",
            headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
        )
    assert r.status_code == 200
    assert "Chartered workers" in r.text


# ---------------------------------------------------------------- nav

def test_base_nav_includes_expansion_views(admin_client: TestClient) -> None:
    """SC verification — sidebar lists all 9 views (5 MVP + 4 expansion)."""
    r = admin_client.get(
        "/preferences",
        headers={"Cf-Access-Authenticated-User-Email": "op@example.com"},
    )
    assert r.status_code == 200
    for path in (
        "/preferences", "/memory", "/pending", "/costs",
        "/buckets", "/skills", "/tools",
        "/workers", "/dream-engine",
    ):
        assert f'href="{path}"' in r.text, f"missing nav link {path}"
