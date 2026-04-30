"""Telegram bot entry point — Application + long-poll runtime.

Per `specs/telegram_bot/plan.md` Q6: long polling for v1 (zero config,
no public subdomain). Migration to webhook is a follow-up after the
bot proves stable.
"""
from __future__ import annotations

import logging
from typing import Any

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from . import config as config_mod
from .handlers.cross_poll import (
    XPOLL_CALLBACK_PATTERN,
    cross_poll_review_callback,
    cross_poll_review_command,
)
from .handlers.help import help_command, start_command
from .handlers.idea import (
    IDEA_CALLBACK_PATTERN,
    idea_callback,
    idea_command,
)
from .handlers.review import (
    REVIEW_CALLBACK_PATTERN,
    review_pending_callback,
    review_pending_command,
    review_pending_reason_message,
)
from .handlers.save import (
    SAVE_CALLBACK_PATTERN,
    save_callback,
    save_command,
)
from .handlers.status import status_command
from .handlers.voice import (
    VOICE_CALLBACK_PATTERN,
    voice_callback,
    voice_message_handler,
)

log = logging.getLogger(__name__)

# python-telegram-bot's Application is generic over 6 type params
# (BT, CCT, UD, CD, BD, JQ); we don't customize any of them, so Any is
# the honest annotation. Stubs shipped with python-telegram-bot 21+
# require an explicit parametrization in --strict mode.
AppT = Application[Any, Any, Any, Any, Any, Any]


def build_application(cfg: config_mod.Config) -> AppT:
    """Construct the Application + register Phase-B command handlers.

    Pure function — does not start polling. Tests call this to inspect
    handler registration without needing a live Telegram connection.
    """
    app = Application.builder().token(cfg.telegram_bot_token).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("save", save_command))
    app.add_handler(CommandHandler("idea", idea_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("review_pending", review_pending_command))
    app.add_handler(
        CommandHandler("cross_poll_review", cross_poll_review_command)
    )
    app.add_handler(
        CallbackQueryHandler(save_callback, pattern=SAVE_CALLBACK_PATTERN)
    )
    app.add_handler(
        CallbackQueryHandler(idea_callback, pattern=IDEA_CALLBACK_PATTERN)
    )
    app.add_handler(
        CallbackQueryHandler(
            review_pending_callback, pattern=REVIEW_CALLBACK_PATTERN
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            cross_poll_review_callback, pattern=XPOLL_CALLBACK_PATTERN
        )
    )
    app.add_handler(
        CallbackQueryHandler(voice_callback, pattern=VOICE_CALLBACK_PATTERN)
    )
    # Voice / audio messages → Whisper → save_lesson (Phase D.1).
    app.add_handler(
        MessageHandler(filters.VOICE | filters.AUDIO, voice_message_handler)
    )
    # Plain-text fallback — picks up the reject-reason from
    # /review_pending. The handler short-circuits when no review state
    # is set, so it's a no-op for any other free-form text.
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND, review_pending_reason_message
        )
    )
    return app


def main() -> None:
    """Entry point invoked by `python -m telegram_bot`."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    cfg = config_mod.load_config()
    app = build_application(cfg)
    log.info(
        "telegram bot starting (long-poll, operator_chat_id=%s)",
        cfg.telegram_operator_chat_id,
    )
    app.run_polling(allowed_updates=Update.ALL_TYPES)
