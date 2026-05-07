"""Cloudflare Access integration — read user identity from edge headers.

Cloudflare Access sits in front of `mcp-admin.alfredopretelvargas.com`
and forwards authenticated requests with these headers:

    Cf-Access-Authenticated-User-Email: <operator email>
    Cf-Access-Jwt-Assertion: <JWT for defense-in-depth validation>

Phase A trusts the edge (uvicorn binds to 127.0.0.1; only the Tunnel
can reach it; only Cloudflare Access can reach the Tunnel). Phase B
adds JWT signature validation against the team's JWKs endpoint as
defense in depth — see specs/mcp_admin/spec.md §6 Q1 + phase_a_close.md.

For local development without Cloudflare Access in front:
    DEV_FAKE_USER_EMAIL=you@example.com python -m mcp_admin.main
will inject the header so the app behaves as if logged in.
"""
from __future__ import annotations

import logging
import os
from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

log = logging.getLogger(__name__)

_HEADER_EMAIL = "Cf-Access-Authenticated-User-Email"


class AccessIdentityMiddleware(BaseHTTPMiddleware):
    """Attach `request.state.user_email` from the Cloudflare Access header.

    Falls back to env var `DEV_FAKE_USER_EMAIL` when the header is
    absent — that path is exclusively for local development; in
    production the only way to reach this middleware is through
    Cloudflare Access, which always sets the header.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        email = request.headers.get(_HEADER_EMAIL)
        if not email:
            email = os.environ.get("DEV_FAKE_USER_EMAIL", "anonymous")
            if email == "anonymous":
                log.debug("No Cf-Access header on %s %s", request.method, request.url.path)
        request.state.user_email = email
        return await call_next(request)
