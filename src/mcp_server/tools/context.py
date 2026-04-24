"""get_context stub — Part 1 returns only L0 (identity.md)."""
from __future__ import annotations

import json
import logging
import uuid
from typing import Optional

from .. import config as config_mod
from .. import db as db_mod
from ._common import Timer, degraded, log_usage

log = logging.getLogger(__name__)


async def get_context(message: str, session_id: Optional[str] = None) -> dict:
    """Return L0 identity context for a turn.

    Part 1 is a stub: the Router (L1–L4 assembly) lands in Module 4. This
    version reads identity.md from disk and returns it, and logs the call to
    routing_logs with classification_mode='stub' so future routing analytics
    can distinguish Part-1 traffic from real Router turns.

    Args:
        message: the operator's turn text (used only for the excerpt in logs).
        session_id: optional client-provided session id; logged if supplied.

    Returns:
        {layers_loaded: ['L0'], identity: str, classification_mode: 'stub'}
        or a degraded payload when identity.md is unreadable.
    """
    request_id = str(uuid.uuid4())
    cfg = config_mod.load_config()

    with Timer() as t:
        try:
            identity_text = cfg.identity_path.read_text(encoding="utf-8")
            ok = True
            err: Optional[str] = None
        except OSError as exc:
            identity_text = ""
            ok = False
            err = f"could not read identity.md: {exc}"
            log.error(err)

    response: dict
    if ok:
        response = {
            "status": "ok",
            "layers_loaded": ["L0"],
            "classification_mode": "stub",
            "identity": identity_text,
            "session_id": session_id,
            "request_id": request_id,
        }
    else:
        response = degraded(
            "identity_unreadable",
            error=err,
            layers_loaded=[],
            classification_mode="stub",
            session_id=session_id,
            request_id=request_id,
        )

    await _log_routing(request_id=request_id, message=message, latency_ms=t.ms, ok=ok, degraded_reason=err)
    await log_usage(
        tool_name="get_context",
        bucket=None,
        project=None,
        invoked_by="client",
        success=ok,
        duration_ms=t.ms,
        metadata={"request_id": request_id, "session_id": session_id},
    )
    return response


async def _log_routing(
    *, request_id: str, message: str, latency_ms: int, ok: bool, degraded_reason: Optional[str]
) -> None:
    if not db_mod.is_healthy():
        return
    pool = db_mod.get_pool()
    excerpt = (message or "")[:200]
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
                        request_id,
                        "unknown",
                        excerpt,
                        json.dumps({"stub": True}),
                        "stub",
                        ["L0"] if ok else [],
                        0,
                        False,
                        not ok,
                        degraded_reason,
                        latency_ms,
                    ),
                )
    except Exception as exc:
        log.debug("routing_logs insert failed: %s", exc)
