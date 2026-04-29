"""/start and /help — welcome + command list (M5.B.3.1)."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from ._guard import operator_only

WELCOME_MESSAGE = (
    "👋 pretel-os bot\n\n"
    "Available commands:\n"
    "  /save <text> — capture a lesson\n"
    "  /idea <text> — capture an idea\n"
    "  /status — health check across MCP + DB + LiteLLM + n8n\n"
    "  /review_pending — walk pending lessons (Phase C)\n"
    "  /cross_poll_review — review cross-pollination queue (Phase C)\n"
    "  /help — show this list\n\n"
    "Voice notes are also accepted (Whisper-transcribed, Phase D)."
)


@operator_only
async def start_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/start — sends the welcome message to the operator chat."""
    if update.message is not None:
        await update.message.reply_text(WELCOME_MESSAGE)


# /help is an alias for /start; the same operator guard applies.
help_command = start_command
