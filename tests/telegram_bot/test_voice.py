"""Unit tests for the voice handler (M5.D.3.1 voice slice).

Whisper API is mocked so the tests are $0 cost. The Telegram
`update.message.voice.get_file()` and `file.download_as_bytearray()`
calls are mocked. `save_lesson` is patched.

Tests:
1. test_voice_transcribes_and_prompts_for_bucket — voice flow
   stashes transcription + shows bucket keyboard.
2. test_voice_callback_invokes_save_lesson_with_voice_tags — bucket
   tap calls `save_lesson(tags=['voice-capture','telegram'])`.
3. test_voice_whisper_failure_replies_with_fallback — Whisper raises
   → reply mentions "/save <texto>".
4. test_voice_empty_transcription_short_circuits — empty/whitespace
   transcription → fallback reply, no save.
5. test_voice_callback_without_pending_warns — bucket tap without
   stashed transcription → "no hay transcripción" warning.
"""
from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

import telegram_bot.config as bot_config
import telegram_bot.handlers.voice as voice_mod

_OPERATOR_CHAT_ID = 12345


def _fake_config() -> bot_config.Config:
    from pathlib import Path

    return bot_config.Config(
        telegram_bot_token="fake-token",
        telegram_operator_chat_id=_OPERATOR_CHAT_ID,
        database_url="postgresql://invalid:1@localhost/x",
        transcripts_dir=Path("/tmp/pretel-os-test-transcripts"),
    )


def _patch_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bot_config, "load_config", lambda: _fake_config())


def _make_voice_update(chat_id: int) -> tuple[Any, Any]:
    update = MagicMock()
    update.effective_chat = MagicMock()
    update.effective_chat.id = chat_id

    msg = MagicMock()
    msg.text = None
    msg.caption = None
    msg.reply_text = AsyncMock()

    voice = MagicMock()
    tg_file = MagicMock()
    tg_file.download_as_bytearray = AsyncMock(return_value=bytearray(b"\x00\x01\x02"))
    voice.get_file = AsyncMock(return_value=tg_file)
    msg.voice = voice
    msg.audio = None

    update.message = msg
    update.callback_query = None

    context = MagicMock()
    context.args = []
    context.user_data = {}
    return update, context


def _make_callback_update(chat_id: int, callback_data: str) -> tuple[Any, Any]:
    update = MagicMock()
    update.effective_chat = MagicMock()
    update.effective_chat.id = chat_id
    update.message = None
    update.callback_query = MagicMock()
    update.callback_query.data = callback_data
    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()
    context = MagicMock()
    context.args = []
    context.user_data = {}
    return update, context


# --- voice message handler -------------------------------------------------


async def test_voice_transcribes_and_prompts_for_bucket(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)
    fake_transcribe = AsyncMock(
        return_value="Postgres se cuelga cuando pgbouncer está en transaction mode."
    )
    monkeypatch.setattr(voice_mod, "_transcribe_audio", fake_transcribe)

    update, context = _make_voice_update(_OPERATOR_CHAT_ID)
    await voice_mod.voice_message_handler(update, context)

    fake_transcribe.assert_awaited_once()
    transcribe_call = fake_transcribe.await_args
    assert transcribe_call is not None
    audio_bytes_arg = transcribe_call.args[0]
    assert isinstance(audio_bytes_arg, bytes)

    # Transcription stashed for the next-step bucket pick.
    assert context.user_data["voice_pending_text"].startswith("Postgres se cuelga")

    # Reply has the transcription + an inline keyboard.
    update.message.reply_text.assert_awaited_once()
    call = update.message.reply_text.await_args
    assert call is not None
    text = call.args[0]
    assert "🎙️ Transcripción" in text
    assert "Postgres se cuelga" in text
    assert "reply_markup" in call.kwargs


async def test_voice_callback_invokes_save_lesson_with_voice_tags(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)
    fake_save = AsyncMock(
        return_value={"status": "saved", "id": "voice-1", "auto_approved": False}
    )
    monkeypatch.setattr(voice_mod, "save_lesson", fake_save)

    update, context = _make_callback_update(
        _OPERATOR_CHAT_ID, callback_data="voice:business"
    )
    context.user_data = {
        "voice_pending_text": "VETT pricing playbook idea capturada por voz."
    }

    await voice_mod.voice_callback(update, context)

    fake_save.assert_awaited_once()
    save_call = fake_save.await_args
    assert save_call is not None
    kwargs = save_call.kwargs
    assert kwargs["bucket"] == "business"
    assert kwargs["category"] == "OPS"
    assert "voice-capture" in kwargs["tags"]
    assert "telegram" in kwargs["tags"]
    assert kwargs["content"].startswith("VETT pricing playbook")

    edit_call = update.callback_query.edit_message_text.await_args
    assert edit_call is not None
    assert "voice-1" in edit_call.args[0]


async def test_voice_whisper_failure_replies_with_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)
    fake_transcribe = AsyncMock(side_effect=RuntimeError("Whisper boom"))
    monkeypatch.setattr(voice_mod, "_transcribe_audio", fake_transcribe)

    update, context = _make_voice_update(_OPERATOR_CHAT_ID)
    await voice_mod.voice_message_handler(update, context)

    update.message.reply_text.assert_awaited_once()
    msg = update.message.reply_text.await_args.args[0]
    assert "🔴" in msg
    assert "/save" in msg  # operator falls back to text capture
    # No transcription stashed on failure.
    assert "voice_pending_text" not in context.user_data


async def test_voice_empty_transcription_short_circuits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)
    fake_transcribe = AsyncMock(return_value="   ")  # whitespace only
    monkeypatch.setattr(voice_mod, "_transcribe_audio", fake_transcribe)

    update, context = _make_voice_update(_OPERATOR_CHAT_ID)
    await voice_mod.voice_message_handler(update, context)

    update.message.reply_text.assert_awaited_once()
    msg = update.message.reply_text.await_args.args[0]
    assert "transcripción" in msg.lower() or "transcription" in msg.lower()
    assert "voice_pending_text" not in context.user_data


async def test_voice_callback_without_pending_warns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)
    fake_save = AsyncMock()
    monkeypatch.setattr(voice_mod, "save_lesson", fake_save)

    update, context = _make_callback_update(
        _OPERATOR_CHAT_ID, callback_data="voice:personal"
    )
    # context.user_data starts empty.

    await voice_mod.voice_callback(update, context)

    fake_save.assert_not_awaited()
    edit_call = update.callback_query.edit_message_text.await_args
    assert edit_call is not None
    assert "transcripción pendiente" in edit_call.args[0].lower()
