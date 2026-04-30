"""Unit tests for Module 5 Phase B handlers (M5.B.8.1).

Pure-Python tests — no live Telegram, no live DB calls. The Telegram
`Update` / `Message` / `Chat` / `CallbackQuery` objects are mocked
with `unittest.mock.MagicMock` (spec'd to the real classes) and the
async response methods (`reply_text`, `answer`, `edit_message_text`)
are `AsyncMock`s. `mcp_server.tools.lessons.save_lesson` and the
`/status` integration probes are also mocked, so the test suite has
zero external dependencies and runs fast (`< 1s`).
"""
from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

import telegram_bot.config as bot_config
import telegram_bot.handlers.idea as idea_mod
import telegram_bot.handlers.save as save_mod
import telegram_bot.handlers.status as status_mod
from telegram_bot.handlers.help import (
    WELCOME_MESSAGE,
    help_command,
    start_command,
)

_OPERATOR_CHAT_ID = 12345


def _fake_config() -> bot_config.Config:
    """Return a Config with operator_chat_id = _OPERATOR_CHAT_ID."""
    from pathlib import Path

    return bot_config.Config(
        telegram_bot_token="fake-token",
        telegram_operator_chat_id=_OPERATOR_CHAT_ID,
        database_url="postgresql://invalid:1@localhost/x",
        transcripts_dir=Path("/tmp/pretel-os-test-transcripts"),
    )


def _patch_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace `load_config` on the shared `telegram_bot.config` module.

    All handler modules import the same module object via
    `from .. import config as config_mod`, so a single setattr here
    flows through to every consumer.
    """
    fake = _fake_config()
    monkeypatch.setattr(bot_config, "load_config", lambda: fake)


def _make_command_update(
    chat_id: int, args: list[str] | None = None
) -> tuple[Any, Any]:
    """Build (update, context) for a CommandHandler invocation."""
    update = MagicMock()
    update.effective_chat = MagicMock()
    update.effective_chat.id = chat_id
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.callback_query = None

    context = MagicMock()
    context.args = args or []
    context.user_data = {}
    return update, context


def _make_callback_update(chat_id: int, callback_data: str) -> tuple[Any, Any]:
    """Build (update, context) for a CallbackQueryHandler invocation."""
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


# --- /start + /help --------------------------------------------------------


async def test_start_sends_welcome_to_operator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)
    update, context = _make_command_update(_OPERATOR_CHAT_ID)

    await start_command(update, context)

    update.message.reply_text.assert_awaited_once_with(WELCOME_MESSAGE)


async def test_help_is_alias_of_start() -> None:
    """help_command and start_command are the same function object."""
    assert help_command is start_command


async def test_unauthorized_chat_rejected_with_private_bot_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)
    update, context = _make_command_update(chat_id=99999)

    await start_command(update, context)

    update.message.reply_text.assert_awaited_once()
    msg = update.message.reply_text.await_args.args[0]
    assert "private bot" in msg.lower()
    # WELCOME_MESSAGE must NOT have leaked
    assert WELCOME_MESSAGE not in msg


# --- /save -----------------------------------------------------------------


async def test_save_without_text_replies_with_usage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)
    update, context = _make_command_update(_OPERATOR_CHAT_ID, args=[])

    await save_mod.save_command(update, context)

    update.message.reply_text.assert_awaited_once()
    call_args = update.message.reply_text.await_args
    assert call_args is not None
    msg = call_args.args[0]
    assert "Usage: /save" in msg
    # No bucket keyboard sent because no text to save.
    assert "reply_markup" not in call_args.kwargs


async def test_save_with_text_stashes_and_shows_keyboard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)
    update, context = _make_command_update(
        _OPERATOR_CHAT_ID, args=["postgres", "deadlock", "with", "pgbouncer"]
    )

    await save_mod.save_command(update, context)

    assert context.user_data == {
        "save_pending_text": "postgres deadlock with pgbouncer"
    }
    update.message.reply_text.assert_awaited_once()
    call_args = update.message.reply_text.await_args
    assert call_args is not None
    assert "reply_markup" in call_args.kwargs


async def test_save_callback_invokes_save_lesson_with_chosen_bucket(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)

    fake_save = AsyncMock(
        return_value={"status": "saved", "id": "abc-123", "auto_approved": True}
    )
    monkeypatch.setattr(save_mod, "save_lesson", fake_save)

    update, context = _make_callback_update(
        _OPERATOR_CHAT_ID, callback_data="save:business"
    )
    context.user_data = {"save_pending_text": "n8n batching debug"}

    await save_mod.save_callback(update, context)

    fake_save.assert_awaited_once()
    save_call = fake_save.await_args
    assert save_call is not None
    call_kwargs = save_call.kwargs
    assert call_kwargs["bucket"] == "business"
    assert call_kwargs["category"] == "OPS"
    assert "telegram-capture" in call_kwargs["tags"]
    assert call_kwargs["content"] == "n8n batching debug"

    update.callback_query.edit_message_text.assert_awaited_once()
    edit_call = update.callback_query.edit_message_text.await_args
    assert edit_call is not None
    reply = edit_call.args[0]
    assert "active" in reply  # auto_approved=True path
    assert "abc-123" in reply


async def test_save_callback_without_pending_text_warns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)
    fake_save = AsyncMock()
    monkeypatch.setattr(save_mod, "save_lesson", fake_save)

    update, context = _make_callback_update(
        _OPERATOR_CHAT_ID, callback_data="save:personal"
    )
    # context.user_data starts empty — no pending text.

    await save_mod.save_callback(update, context)

    fake_save.assert_not_awaited()
    update.callback_query.edit_message_text.assert_awaited_once()
    msg = update.callback_query.edit_message_text.await_args.args[0]
    assert "No pending lesson" in msg


# --- /idea -----------------------------------------------------------------


async def test_idea_callback_uses_plan_category_and_idea_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)
    fake_save = AsyncMock(
        return_value={"status": "saved", "id": "idea-1", "auto_approved": False}
    )
    monkeypatch.setattr(idea_mod, "save_lesson", fake_save)

    update, context = _make_callback_update(
        _OPERATOR_CHAT_ID, callback_data="idea:business"
    )
    context.user_data = {"idea_pending_text": "VETT pricing playbook"}

    await idea_mod.idea_callback(update, context)

    fake_save.assert_awaited_once()
    idea_call = fake_save.await_args
    assert idea_call is not None
    call_kwargs = idea_call.kwargs
    assert call_kwargs["category"] == "PLAN"
    assert "idea" in call_kwargs["tags"]
    assert "telegram-capture" in call_kwargs["tags"]


# --- /status ---------------------------------------------------------------


async def test_status_runs_4_checks_and_renders_summary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)
    # _litellm_check reads LITELLM_API_KEY at call time; set it so the
    # check goes through _http_check (which the test patches below)
    # rather than short-circuiting to the 🟡 unconfigured path.
    monkeypatch.setenv("LITELLM_API_KEY", "test-key")

    healthy = status_mod.Check(
        name="placeholder", healthy=True, detail="HTTP 200", latency_ms=42
    )

    async def _fake_http_check(
        name: str, _url: str, *, headers: dict[str, str] | None = None
    ) -> status_mod.Check:
        return status_mod.Check(
            name=name, healthy=True, detail="HTTP 200", latency_ms=42
        )

    async def _fake_db_check(_dsn: str) -> status_mod.Check:
        return status_mod.Check(
            name="postgres", healthy=True, detail="SELECT 1 OK", latency_ms=8
        )

    monkeypatch.setattr(status_mod, "_http_check", _fake_http_check)
    monkeypatch.setattr(status_mod, "_db_check", _fake_db_check)

    update, context = _make_command_update(_OPERATOR_CHAT_ID)

    await status_mod.status_command(update, context)

    update.message.reply_text.assert_awaited_once()
    msg = update.message.reply_text.await_args.args[0]
    assert "🟢 All systems healthy" in msg
    # All 4 integrations show in the per-row breakdown.
    for name in ("mcp_server", "postgres", "litellm", "n8n"):
        assert name in msg


async def test_status_renders_partial_when_one_down(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Direct _format_status check — pure function, no mocks needed."""
    out = status_mod._format_status(
        [
            status_mod.Check("mcp_server", True, "HTTP 200", 100),
            status_mod.Check("postgres", True, "SELECT 1 OK", 8),
            status_mod.Check("litellm", False, "ConnectError", 5000),
            status_mod.Check("n8n", True, "HTTP 200", 42),
        ]
    )
    assert "🟡 Partial availability" in out
    assert "🔴 litellm" in out
    assert "🟢 mcp_server" in out
