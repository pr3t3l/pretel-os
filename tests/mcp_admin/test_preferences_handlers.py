"""Unit tests for the preferences handler — middleware + route shape.

These tests run without DB. The slow integration tests
(test_e2e_phase_a.py) cover the full request → DB round-trip.
"""
from __future__ import annotations

import pytest
from fastapi import FastAPI, Request
from starlette.testclient import TestClient

from mcp_admin.middleware import AccessIdentityMiddleware


def _make_probe_app() -> FastAPI:
    """Minimal app with the middleware attached + a probe endpoint."""
    app = FastAPI()
    app.add_middleware(AccessIdentityMiddleware)

    @app.get("/probe")
    def probe(request: Request) -> dict[str, str]:
        return {"email": request.state.user_email}

    return app


def test_middleware_reads_cf_access_email_header() -> None:
    """Middleware attaches the operator email from the Cf-Access header."""
    client = TestClient(_make_probe_app())
    r = client.get(
        "/probe",
        headers={"Cf-Access-Authenticated-User-Email": "operator@example.com"},
    )
    assert r.status_code == 200
    assert r.json() == {"email": "operator@example.com"}


def test_middleware_falls_back_to_anonymous_without_header() -> None:
    """No header + no DEV_FAKE → user is 'anonymous'."""
    client = TestClient(_make_probe_app())
    r = client.get("/probe")
    assert r.status_code == 200
    assert r.json() == {"email": "anonymous"}


def test_middleware_uses_dev_fake_user_when_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """For local dev, DEV_FAKE_USER_EMAIL injects identity."""
    monkeypatch.setenv("DEV_FAKE_USER_EMAIL", "dev@local")
    client = TestClient(_make_probe_app())
    r = client.get("/probe")  # no Cf-Access header
    assert r.status_code == 200
    assert r.json() == {"email": "dev@local"}


def test_app_factory_wires_preferences_routes() -> None:
    """build_app() exposes the /preferences GET + POST routes."""
    from mcp_admin.main import build_app

    app = build_app()
    paths = {getattr(r, "path", None) for r in app.routes}
    assert "/preferences" in paths
    assert "/preferences/{category}/{key}" in paths
    assert "/health" in paths
