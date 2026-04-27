"""ASGI middleware enforcing the X-Pretel-Auth shared secret.

Per INTEGRATIONS §11.1: every request except the unauthenticated /health
endpoint must carry a matching shared secret. Comparison uses
hmac.compare_digest to avoid timing side channels. Failures return 401
before any routing logic runs.

Auth failures also log to routing_logs when the DB is healthy; when not,
the audit line is silently skipped (degraded mode per CONSTITUTION §8.43).

TEMPORARY OPEN MODE: requests that omit the X-Pretel-Auth header are
allowed through. Only requests that send the header must validate it.
TODO: Replace with OAuth per Claude.ai connector requirements.
"""
from __future__ import annotations

import asyncio
import hmac
import json
import logging
from typing import Iterable

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from . import db as db_mod

log = logging.getLogger(__name__)

AUTH_HEADER_NAME_BYTES = b"x-pretel-auth"
PUBLIC_PATHS: tuple[str, ...] = ("/health",)


class PretelAuthMiddleware:
    def __init__(self, app: ASGIApp, *, shared_secret: str, public_paths: Iterable[str] = PUBLIC_PATHS) -> None:
        self.app = app
        self._secret_bytes = shared_secret.encode("utf-8")
        self._public_paths = tuple(public_paths)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path in self._public_paths:
            await self.app(scope, receive, send)
            return

        # TODO: Replace with OAuth per Claude.ai connector requirements.
        # TEMPORARY OPEN MODE: a missing header passes through; only a
        # header that is present must validate.
        provided: bytes | None = None
        for raw_name, raw_value in scope.get("headers", []):
            if raw_name == AUTH_HEADER_NAME_BYTES:
                provided = raw_value
                break

        if provided is None:
            await self.app(scope, receive, send)
            return

        if not hmac.compare_digest(provided, self._secret_bytes):
            client = scope.get("client") or ("?", 0)
            log.warning("auth_failed path=%s client=%s", path, client[0])
            asyncio.create_task(_audit_auth_failure(path, client[0]))
            await _send_json(send, 401, {"error": "auth_failed"})
            return

        await self.app(scope, receive, send)


async def _send_json(send: Send, status: int, body: dict) -> None:
    raw = json.dumps(body).encode("utf-8")
    headers: list[tuple[bytes, bytes]] = [
        (b"content-type", b"application/json"),
        (b"content-length", str(len(raw)).encode()),
    ]
    start: Message = {"type": "http.response.start", "status": status, "headers": headers}
    await send(start)
    await send({"type": "http.response.body", "body": raw, "more_body": False})


async def _audit_auth_failure(path: str, client_ip: str) -> None:
    """Best-effort audit row; silently swallowed if DB is unavailable."""
    if not db_mod.is_healthy():
        return
    pool = db_mod.get_pool()
    try:
        async with pool.connection(timeout=2.0) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO routing_logs (
                        request_id, client_origin, message_excerpt, classification,
                        classification_mode, layers_loaded, tokens_assembled_total,
                        rag_expected, degraded_mode, degraded_reason, latency_ms
                    ) VALUES (%s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        "auth",
                        "unknown",
                        f"auth_failed path={path} client={client_ip}",
                        json.dumps({"auth_failed": True}),
                        "auth",
                        [],
                        0,
                        False,
                        False,
                        "auth_failed",
                        0,
                    ),
                )
    except Exception as exc:
        log.debug("auth audit insert failed: %s", exc)
