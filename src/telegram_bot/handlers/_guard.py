"""Operator-only guard decorator for Telegram handlers.

Per `specs/telegram_bot/spec.md` §5: any chat_id ≠
`TELEGRAM_OPERATOR_CHAT_ID` gets a polite "private bot" reply and the
rejection logs at WARNING. Applied to every Phase-B handler including
`/start` — the welcome message is only sent to the operator.
"""
from __future__ import annotations

import functools
import logging
from typing import Any, Callable, Coroutine

from telegram import Update
from telegram.ext import ContextTypes

from .. import config as config_mod

log = logging.getLogger(__name__)

# CommandHandler in python-telegram-bot v21 expects Coroutine, not the
# broader Awaitable, hence the explicit Coroutine[Any, Any, None].
Handler = Callable[
    [Update, ContextTypes.DEFAULT_TYPE], Coroutine[Any, Any, None]
]


def operator_only(fn: Handler) -> Handler:
    """Wrap a handler so it only runs for the configured operator."""

    @functools.wraps(fn)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        cfg = config_mod.load_config()
        chat = update.effective_chat
        chat_id = chat.id if chat is not None else None
        if chat_id != cfg.telegram_operator_chat_id:
            log.warning(
                "rejected non-operator chat_id=%s (handler=%s)",
                chat_id,
                fn.__name__,
            )
            if update.message is not None:
                await update.message.reply_text(
                    "🔒 This is a private bot. Access denied."
                )
            return
        await fn(update, context)

    return wrapper
