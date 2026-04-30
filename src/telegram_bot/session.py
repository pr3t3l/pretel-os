"""Session tracking for the Telegram bot (M5.D.2.1 + M5.D.2.2).

Three concerns live here:

1. **Per-turn `conversation_sessions` row management** — the
   `session_middleware` TypeHandler runs at group=-1 (before any
   command handler). For each operator turn it INSERTs a new row
   (first turn after a closed/no-prior session) or UPDATEs
   `last_seen_at` + `turn_count` on the existing open one.

2. **Per-turn JSONL transcript append** — the user's text (or
   `caption`, or a `<voice/audio>` placeholder for media-only turns)
   is appended to `~/pretel-os-data/transcripts/{session_id}.jsonl`.
   Bot replies are NOT captured today (simplification — the operator
   intent is what matters; reply-tracking lands in a future tweak).

3. **Idle-close background loop** — `idle_close_loop` runs every 5
   minutes (default) and closes any session whose `last_seen_at` is
   older than 10 minutes (default), tagging `close_reason='idle_10min'`.
   The loop is started by `bot._post_init` and stopped by
   `bot._post_shutdown`; both stash state in `app.bot_data` so tests
   can inspect / cancel without touching module-level globals.

Per phase_d_close.md (Module 4) Q5: this is the table the Router's
`_get_session_excerpt()` reads from at classifier time. Module 5
populates it; Module 4's Q8 deferral closes once Module 5 ships.
"""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from telegram import Update
from telegram.ext import ContextTypes

from . import config as config_mod

log = logging.getLogger(__name__)

_SESSION_KEY = "session_id"  # location in user_data
_DEFAULT_OPERATOR_ID = "alfredo"
_DEFAULT_CLIENT_ORIGIN = "telegram"


# --- sync DB helpers (run via asyncio.to_thread in async paths) ------------


def ensure_session_sync(
    conn: psycopg.Connection,
    *,
    operator_id: str = _DEFAULT_OPERATOR_ID,
    client_origin: str = _DEFAULT_CLIENT_ORIGIN,
) -> str:
    """Find or open a `conversation_sessions` row for this operator.

    Returns the session_id (UUID as str). When an open session exists
    for `(client_origin, operator_id)`, refreshes `last_seen_at` and
    bumps `turn_count`. Otherwise INSERTs a new row.

    `client_origin` is parametrized so tests can isolate by passing a
    unique value; production callers always use `'telegram'`.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id::text FROM conversation_sessions
            WHERE  client_origin = %s
              AND  operator_id = %s
              AND  closed_at IS NULL
            ORDER BY started_at DESC
            LIMIT 1
            FOR UPDATE
            """,
            (client_origin, operator_id),
        )
        row = cur.fetchone()
        if row is not None:
            session_id: str = str(row[0])
            cur.execute(
                """
                UPDATE conversation_sessions
                SET    last_seen_at = now(),
                       turn_count = turn_count + 1
                WHERE  id = %s
                """,
                (session_id,),
            )
            return session_id

        cur.execute(
            """
            INSERT INTO conversation_sessions
                (client_origin, operator_id, turn_count)
            VALUES (%s, %s, 1)
            RETURNING id::text
            """,
            (client_origin, operator_id),
        )
        new_row = cur.fetchone()
        if new_row is None:
            raise RuntimeError("INSERT ... RETURNING produced no row")
        return str(new_row[0])


def close_idle_sessions_sync(
    conn: psycopg.Connection,
    *,
    idle_minutes: int = 10,
    client_origin: str = _DEFAULT_CLIENT_ORIGIN,
) -> int:
    """Close `conversation_sessions` idle longer than `idle_minutes`.

    Sets `closed_at = now()` and `close_reason = 'idle_<n>min'`.
    Returns the number of rows closed.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE conversation_sessions
            SET    closed_at = now(),
                   close_reason = %s
            WHERE  client_origin = %s
              AND  closed_at IS NULL
              AND  last_seen_at < now() - (%s || ' minutes')::interval
            """,
            (f"idle_{idle_minutes}min", client_origin, str(idle_minutes)),
        )
        return cur.rowcount


def append_transcript(
    transcripts_dir: Path,
    session_id: str,
    role: str,
    content: str,
) -> None:
    """Append a `{role, content, timestamp}` JSONL line to the
    session's transcript file.

    Creates `transcripts_dir` if missing. Each line is a complete
    JSON object, newline-terminated, UTF-8.
    """
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    path = transcripts_dir / f"{session_id}.jsonl"
    payload = {
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with path.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(payload, ensure_ascii=False) + "\n")


# --- async wrappers --------------------------------------------------------


def _ensure_session_blocking(dsn: str) -> str:
    with psycopg.connect(dsn, autocommit=True) as conn:
        return ensure_session_sync(conn)


def _close_idle_blocking(dsn: str, idle_minutes: int) -> int:
    with psycopg.connect(dsn, autocommit=True) as conn:
        return close_idle_sessions_sync(conn, idle_minutes=idle_minutes)


async def session_middleware(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """TypeHandler middleware: ensure session + transcript-append.

    Registered at group=-1 so it runs before any command handler.
    Silent on error: DB or file-I/O failures log at WARNING and
    return, leaving downstream handlers unaffected. Non-operator
    chats short-circuit early — `operator_only` on individual
    handlers takes care of the rejection reply.
    """
    cfg = config_mod.load_config()
    chat = update.effective_chat
    if chat is None or chat.id != cfg.telegram_operator_chat_id:
        return

    msg = update.message
    if msg is None:
        return  # callback_query / edits / etc. — handler-level only

    try:
        session_id = await asyncio.to_thread(
            _ensure_session_blocking, cfg.database_url
        )
    except Exception as exc:
        log.warning("session_middleware: ensure_session failed: %s", exc)
        return

    if context.user_data is not None:
        context.user_data[_SESSION_KEY] = session_id

    transcript_text = msg.text or msg.caption or "<voice/audio>"
    try:
        await asyncio.to_thread(
            append_transcript,
            cfg.transcripts_dir,
            session_id,
            "user",
            transcript_text,
        )
    except Exception as exc:
        log.warning("session_middleware: append_transcript failed: %s", exc)


# --- idle-close background loop -------------------------------------------


async def idle_close_loop(
    stop_event: asyncio.Event,
    dsn: str,
    *,
    interval_s: int = 300,
    idle_minutes: int = 10,
) -> None:
    """Background loop that closes idle sessions every `interval_s`.

    Owned by `bot._post_init` / `bot._post_shutdown`. Cancellation
    is signaled by `stop_event.set()`; the loop exits at the next
    iteration boundary (within `interval_s` of the signal).
    """
    log.info(
        "idle_close_loop starting (interval=%ds, idle_minutes=%d)",
        interval_s,
        idle_minutes,
    )
    while not stop_event.is_set():
        try:
            count = await asyncio.to_thread(
                _close_idle_blocking, dsn, idle_minutes
            )
            if count > 0:
                log.info(
                    "idle_close_loop: closed %d idle session(s)", count
                )
        except Exception as exc:
            log.warning("idle_close_loop error: %s", exc)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval_s)
        except asyncio.TimeoutError:
            continue
    log.info("idle_close_loop stopped")
