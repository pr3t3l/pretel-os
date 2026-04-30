"""Voice message handler — Whisper → bucket prompt → save_lesson (M5.D.1.1).

Flow per `specs/telegram_bot/plan.md` §6.2:

1. Operator sends a voice note → bot downloads the `.ogg` from
   Telegram → posts it to OpenAI Whisper (`whisper-1`, `language=es`,
   `response_format=text`) → replies with the transcription.
2. Bot stashes the transcription in `user_data["voice_pending_text"]`
   and shows an inline keyboard with the three buckets.
3. Operator taps a bucket → bot calls `save_lesson(category='OPS',
   tags=['voice-capture','telegram'])` and confirms.

Whisper failures (network, missing OPENAI_API_KEY, content filter)
degrade to a "🔴 No pude transcribir — manda /save <texto> a mano"
reply. The bot never crashes the operator's flow; failures fall back
to the explicit /save path.
"""
from __future__ import annotations

import io
import logging
import os
from typing import Any

from openai import AsyncOpenAI
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from mcp_server.tools.lessons import save_lesson

from ._guard import operator_only

log = logging.getLogger(__name__)

VOICE_CALLBACK_PATTERN = r"^voice:"
_VOICE_PREFIX = "voice:"
_PENDING_KEY = "voice_pending_text"
_BUCKETS = ("personal", "business", "scout")
_WHISPER_MODEL = "whisper-1"
_WHISPER_LANGUAGE = "es"  # operator writes / speaks Spanish primarily.


async def _transcribe_audio(audio_bytes: bytes) -> str:
    """Send `audio_bytes` (.ogg) to OpenAI Whisper. Returns the text.

    The SDK expects a file-like object with a `.name` attribute; we
    wrap the bytes in `BytesIO` and assign `.name = "voice.ogg"` so
    Whisper picks the right decoder.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    client = AsyncOpenAI(api_key=api_key)
    buf = io.BytesIO(audio_bytes)
    buf.name = "voice.ogg"
    response = await client.audio.transcriptions.create(
        model=_WHISPER_MODEL,
        file=buf,
        language=_WHISPER_LANGUAGE,
        response_format="text",
    )
    # When response_format='text', the SDK returns a string.
    return str(response).strip()


def _bucket_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    bucket.title(), callback_data=f"{_VOICE_PREFIX}{bucket}"
                )
                for bucket in _BUCKETS
            ]
        ]
    )


@operator_only
async def voice_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Receive a voice note → transcribe → stash → prompt for bucket."""
    msg = update.message
    if msg is None:
        return
    voice = msg.voice or msg.audio
    if voice is None:
        return  # not a voice/audio update — silently skip.

    try:
        tg_file = await voice.get_file()
        audio_bytes = bytes(await tg_file.download_as_bytearray())
    except Exception as exc:
        log.exception("voice_message_handler: download failed")
        await msg.reply_text(
            f"🔴 No pude descargar el audio: {type(exc).__name__}. "
            "Envía /save <texto> a mano."
        )
        return

    try:
        raw_text = await _transcribe_audio(audio_bytes)
    except Exception as exc:
        log.exception("voice_message_handler: Whisper failed")
        await msg.reply_text(
            f"🔴 No pude transcribir ({type(exc).__name__}). "
            "Envía /save <texto> a mano."
        )
        return

    # Defensive strip so whitespace-only Whisper output is treated as empty.
    text = (raw_text or "").strip()
    if not text:
        await msg.reply_text(
            "🔴 La transcripción quedó vacía. Envía /save <texto>."
        )
        return

    if context.user_data is not None:
        context.user_data[_PENDING_KEY] = text

    await msg.reply_text(
        f"🎙️ Transcripción:\n\n{text}\n\nPick a bucket:",
        reply_markup=_bucket_keyboard(),
    )


@operator_only
async def voice_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Bucket-selection callback for a voice-captured lesson."""
    query = update.callback_query
    if query is None or query.data is None:
        return
    if not query.data.startswith(_VOICE_PREFIX):
        return
    await query.answer()
    bucket = query.data[len(_VOICE_PREFIX):]
    if bucket not in _BUCKETS:
        await query.edit_message_text(f"⚠️ Unknown bucket: {bucket!r}.")
        return

    text = (context.user_data or {}).pop(_PENDING_KEY, None)
    if not text:
        await query.edit_message_text(
            "⚠️ No hay transcripción pendiente — envía un audio primero."
        )
        return

    title = " ".join(text.split()[:20])
    result = await save_lesson(
        title=title,
        content=text,
        bucket=bucket,
        tags=["voice-capture", "telegram"],
        category="OPS",
    )

    status = result.get("status")
    if status == "saved":
        approved = result.get("auto_approved", False)
        marker = "✅ active" if approved else "⏳ pending review"
        lid = result.get("id", "?")
        await query.edit_message_text(
            f"💾 Lección guardada → {marker}\nID: `{lid}`\nBucket: {bucket}",
            parse_mode="Markdown",
        )
    elif status == "merge_candidate":
        await query.edit_message_text(
            f"🔁 Posible duplicado (merge candidate "
            f"`{result.get('candidate_id', '?')}`). No se insertó.",
            parse_mode="Markdown",
        )
    elif status == "degraded":
        await query.edit_message_text(
            f"🔴 DB degraded: {result.get('degraded_reason', '?')}."
        )
    else:
        await query.edit_message_text(
            f"❌ Save falló: {result.get('error', 'unknown error')}"
        )
