"""Telegram bot entry point — Application + long-poll runtime.

Per `specs/telegram_bot/plan.md` Q6: long polling for v1 (zero config,
no public subdomain). Migration to webhook is a follow-up after the
bot proves stable.
"""
from __future__ import annotations

import logging
from typing import Any

from telegram import Update
from telegram.ext import Application, CommandHandler

from . import config as config_mod
from .handlers.help import help_command, start_command

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
