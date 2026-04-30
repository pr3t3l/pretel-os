"""Unit tests for Phase C review flows (M5.C.3.1).

Pure-mock tests covering /review_pending and /cross_poll_review.
The Telegram Update / Message / CallbackQuery objects are MagicMocks
with AsyncMock-bound async methods; the underlying MCP tools
(`list_pending_lessons`, `approve_lesson`, `reject_lesson`,
`list_pending_cross_pollination`, `resolve_cross_pollination`) are
patched module-level so the tests run in <1s with zero DB / Telegram.

All tests run by default (no `slow` marker) — pure-CPU.
"""
from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

import telegram_bot.config as bot_config
import telegram_bot.handlers.cross_poll as xpoll_mod
import telegram_bot.handlers.review as review_mod

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


def _make_command_update(chat_id: int) -> tuple[Any, Any]:
    update = MagicMock()
    update.effective_chat = MagicMock()
    update.effective_chat.id = chat_id
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
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


def _make_text_message_update(chat_id: int, text: str) -> tuple[Any, Any]:
    update = MagicMock()
    update.effective_chat = MagicMock()
    update.effective_chat.id = chat_id
    update.message = MagicMock()
    update.message.text = text
    update.message.reply_text = AsyncMock()
    update.callback_query = None
    context = MagicMock()
    context.args = []
    context.user_data = {}
    return update, context


def _seed_pending_lesson(
    monkeypatch: pytest.MonkeyPatch,
    lessons: list[dict[str, Any]],
) -> AsyncMock:
    """Replace `list_pending_lessons` in `review_mod`. Returns the mock so
    callers can assert call args. Each invocation pops the next lesson;
    once empty, returns `{status:'ok', results:[]}`.
    """
    queue = list(lessons)

    async def _fake(bucket: Any = None, limit: int = 10) -> dict[str, Any]:
        if not queue:
            return {"status": "ok", "results": []}
        return {"status": "ok", "results": [queue.pop(0)]}

    mock = AsyncMock(side_effect=_fake)
    monkeypatch.setattr(review_mod, "list_pending_lessons", mock)
    return mock


def _seed_pending_xpoll(
    monkeypatch: pytest.MonkeyPatch,
    rows: list[dict[str, Any]],
) -> AsyncMock:
    queue = list(rows)

    async def _fake(limit: int = 10) -> dict[str, Any]:
        if not queue:
            return {"status": "ok", "results": []}
        return {"status": "ok", "results": [queue.pop(0)]}

    mock = AsyncMock(side_effect=_fake)
    monkeypatch.setattr(xpoll_mod, "list_pending_cross_pollination", mock)
    return mock


# --- /review_pending -------------------------------------------------------


async def test_review_pending_empty_queue(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)
    _seed_pending_lesson(monkeypatch, [])

    update, context = _make_command_update(_OPERATOR_CHAT_ID)
    await review_mod.review_pending_command(update, context)

    update.message.reply_text.assert_awaited_once()
    call = update.message.reply_text.await_args
    assert call is not None
    assert "No hay lecciones pendientes" in call.args[0]


async def test_review_pending_shows_first_card_with_keyboard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)
    _seed_pending_lesson(
        monkeypatch,
        [
            {
                "id": "abc-1",
                "title": "Don't trust mocks alone",
                "content": "Integration test caught a dataclass default-factory bug.",
                "bucket": "business",
                "category": "CODE",
                "tags": [],
                "created_at": "2026-04-29T00:00:00Z",
            }
        ],
    )

    update, context = _make_command_update(_OPERATOR_CHAT_ID)
    await review_mod.review_pending_command(update, context)

    update.message.reply_text.assert_awaited_once()
    call = update.message.reply_text.await_args
    assert call is not None
    text = call.args[0]
    assert "Don't trust mocks alone" in text
    assert "business" in text
    assert "reply_markup" in call.kwargs


async def test_review_pending_approve_path_invokes_approve_lesson(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)
    # After the approve, the next-fetch returns empty so we land on the
    # "no hay" reply via update.message (callback_query.message).
    _seed_pending_lesson(monkeypatch, [])

    fake_approve = AsyncMock(
        return_value={"status": "ok", "approved": True}
    )
    monkeypatch.setattr(review_mod, "approve_lesson", fake_approve)

    update, context = _make_callback_update(
        _OPERATOR_CHAT_ID, callback_data="review:approve:lesson-id-1"
    )
    # The callback path uses update.message for follow-up replies via
    # _send_next_or_empty(use_edit=False); construct one.
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()

    await review_mod.review_pending_callback(update, context)

    fake_approve.assert_awaited_once_with(id="lesson-id-1")
    # First edit: "Aprobada ✅"
    edit_call = update.callback_query.edit_message_text.await_args
    assert edit_call is not None
    assert "Aprobada" in edit_call.args[0]
    # Then a follow-up message with "no pending" since queue is empty.
    update.message.reply_text.assert_awaited()
    follow = update.message.reply_text.await_args
    assert follow is not None
    assert "No hay lecciones pendientes" in follow.args[0]


async def test_review_pending_reject_path_prompts_for_reason(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)

    update, context = _make_callback_update(
        _OPERATOR_CHAT_ID, callback_data="review:reject:lesson-id-2"
    )
    await review_mod.review_pending_callback(update, context)

    # State stashed
    assert context.user_data == {
        "review_state": {"awaiting_reason_for": "lesson-id-2"},
    }
    edit_call = update.callback_query.edit_message_text.await_args
    assert edit_call is not None
    assert "razón" in edit_call.args[0].lower()


async def test_review_pending_reason_message_invokes_reject_lesson(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)
    _seed_pending_lesson(monkeypatch, [])  # next-fetch empty
    fake_reject = AsyncMock(
        return_value={"status": "ok", "rejected": True}
    )
    monkeypatch.setattr(review_mod, "reject_lesson", fake_reject)

    update, context = _make_text_message_update(
        _OPERATOR_CHAT_ID, text="duplicate of LL-X-001"
    )
    # Pre-set state simulating the prior reject button tap.
    context.user_data["review_state"] = {
        "awaiting_reason_for": "lesson-id-2"
    }

    await review_mod.review_pending_reason_message(update, context)

    fake_reject.assert_awaited_once_with(
        id="lesson-id-2", reason="duplicate of LL-X-001"
    )
    # State cleared.
    assert "review_state" not in context.user_data
    # First reply: "Rechazada ❌"; then the empty-queue follow-up.
    assert update.message.reply_text.await_count >= 2
    first_reply = update.message.reply_text.await_args_list[0].args[0]
    assert "Rechazada" in first_reply


async def test_review_pending_text_without_state_is_noop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Plain text message with no review_state in user_data → handler
    returns silently (does NOT call reject_lesson, does NOT reply)."""
    _patch_config(monkeypatch)
    fake_reject = AsyncMock()
    monkeypatch.setattr(review_mod, "reject_lesson", fake_reject)

    update, context = _make_text_message_update(
        _OPERATOR_CHAT_ID, text="hello, just chatting"
    )

    await review_mod.review_pending_reason_message(update, context)

    fake_reject.assert_not_awaited()
    update.message.reply_text.assert_not_awaited()


async def test_review_pending_skip_advances_without_calling_tools(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)
    _seed_pending_lesson(monkeypatch, [])  # next-fetch empty

    fake_approve = AsyncMock()
    fake_reject = AsyncMock()
    monkeypatch.setattr(review_mod, "approve_lesson", fake_approve)
    monkeypatch.setattr(review_mod, "reject_lesson", fake_reject)

    update, context = _make_callback_update(
        _OPERATOR_CHAT_ID, callback_data="review:skip:lesson-id-3"
    )
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()

    await review_mod.review_pending_callback(update, context)

    fake_approve.assert_not_awaited()
    fake_reject.assert_not_awaited()
    edit_call = update.callback_query.edit_message_text.await_args
    assert edit_call is not None
    assert "Saltada" in edit_call.args[0]


# --- /cross_poll_review ----------------------------------------------------


async def test_cross_poll_empty_queue(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)
    _seed_pending_xpoll(monkeypatch, [])

    update, context = _make_command_update(_OPERATOR_CHAT_ID)
    await xpoll_mod.cross_poll_review_command(update, context)

    update.message.reply_text.assert_awaited_once()
    call = update.message.reply_text.await_args
    assert call is not None
    assert "No hay propuestas pendientes" in call.args[0]


async def test_cross_poll_shows_first_proposal_card(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)
    _seed_pending_xpoll(
        monkeypatch,
        [
            {
                "id": "xp-1",
                "origin_bucket": "business",
                "origin_project": "vett",
                "target_bucket": "scout",
                "idea": "Apply VETT pricing playbook to MTM audits",
                "reasoning": "Both share consultative-sale shape.",
                "suggested_application": "Quote 3-tier package",
                "priority": 1,
                "confidence_score": 0.7,
                "impact_score": 0.6,
                "created_at": "2026-04-29T00:00:00Z",
            }
        ],
    )

    update, context = _make_command_update(_OPERATOR_CHAT_ID)
    await xpoll_mod.cross_poll_review_command(update, context)

    update.message.reply_text.assert_awaited_once()
    call = update.message.reply_text.await_args
    assert call is not None
    text = call.args[0]
    assert "business → scout" in text
    assert "VETT pricing" in text
    assert "reply_markup" in call.kwargs


async def test_cross_poll_approve_invokes_resolve(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)
    _seed_pending_xpoll(monkeypatch, [])
    fake_resolve = AsyncMock(
        return_value={"status": "ok", "resolved": True, "new_status": "applied"}
    )
    monkeypatch.setattr(xpoll_mod, "resolve_cross_pollination", fake_resolve)

    update, context = _make_callback_update(
        _OPERATOR_CHAT_ID, callback_data="xpoll:approve:xp-1"
    )
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()

    await xpoll_mod.cross_poll_review_callback(update, context)

    fake_resolve.assert_awaited_once_with(id="xp-1", action="approve")
    edit_call = update.callback_query.edit_message_text.await_args
    assert edit_call is not None
    assert "applied" in edit_call.args[0]


async def test_cross_poll_reject_invokes_resolve_with_reject_action(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_config(monkeypatch)
    _seed_pending_xpoll(monkeypatch, [])
    fake_resolve = AsyncMock(
        return_value={"status": "ok", "resolved": True, "new_status": "dismissed"}
    )
    monkeypatch.setattr(xpoll_mod, "resolve_cross_pollination", fake_resolve)

    update, context = _make_callback_update(
        _OPERATOR_CHAT_ID, callback_data="xpoll:reject:xp-2"
    )
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()

    await xpoll_mod.cross_poll_review_callback(update, context)

    fake_resolve.assert_awaited_once_with(id="xp-2", action="reject")
