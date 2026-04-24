"""OpenAI embedding calls for lesson / tool / context indexing.

Returns None on failure — the caller decides whether to queue to
pending_embeddings, fall back to degraded mode, or surface the error.
"""
from __future__ import annotations

import logging
from typing import Optional

from openai import AsyncOpenAI

from . import config as config_mod

log = logging.getLogger(__name__)

_client: Optional[AsyncOpenAI] = None


def _get_client() -> Optional[AsyncOpenAI]:
    global _client
    cfg = config_mod.load_config()
    if not cfg.openai_api_key:
        return None
    if _client is None:
        _client = AsyncOpenAI(
            api_key=cfg.openai_api_key,
            timeout=cfg.timeout_openai_embedding_ms / 1000.0,
        )
    return _client


async def embed(text: str) -> Optional[list[float]]:
    """Return an embedding vector for `text`, or None on any failure."""
    if not text or not text.strip():
        return None
    client = _get_client()
    if client is None:
        log.warning("OPENAI_API_KEY not set — skipping embed")
        return None
    cfg = config_mod.load_config()
    try:
        resp = await client.embeddings.create(model=cfg.openai_embedding_model, input=text)
        return list(resp.data[0].embedding)
    except Exception as exc:
        log.warning("embedding call failed: %s", exc)
        return None
