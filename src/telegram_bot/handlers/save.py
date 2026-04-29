"""/save <text> — capture a lesson from Telegram (M5.B.4.1).

Two-step flow:
1. Operator types `/save my lesson text` → bot stashes the text in
   `context.user_data` and replies with an inline keyboard listing
   the three buckets.
2. Operator taps a bucket button → bot pops the stashed text and
   calls `mcp_server.tools.lessons.save_lesson(...)` with
   `tags=['telegram-capture']` and `category='OPS'`.

`save_lesson` is imported directly per `specs/telegram_bot/plan.md`
Q2 (no HTTP / MCP-protocol round-trip from internal components).
"""
from __future__ import annotations

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from mcp_server.tools.lessons import save_lesson

from ._guard import operator_only

log = logging.getLogger(__name__)

_BUCKETS = ("personal", "business", "scout")
_PENDING_KEY = "save_pending_text"
_SAVE_PREFIX = "save:"
SAVE_CALLBACK_PATTERN = r"^save:"


@operator_only
async def save_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """`/save <text>`. Stashes the text and prompts for a bucket."""
    if update.message is None:
        return
    args = context.args or []
    if not args:
        await update.message.reply_text(
            "Usage: /save <text>\n"
            "Example: /save Postgres dropped queries when pgbouncer was "
            "in transaction mode."
        )
        return
    text = " ".join(args).strip()
    if context.user_data is not None:
        context.user_data[_PENDING_KEY] = text

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    bucket.title(), callback_data=f"{_SAVE_PREFIX}{bucket}"
                )
                for bucket in _BUCKETS
            ]
        ]
    )
    await update.message.reply_text(
        f"📝 Lesson preview:\n\n{text}\n\nPick a bucket:",
        reply_markup=keyboard,
    )


@operator_only
async def save_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the bucket-selection inline keyboard for /save."""
    query = update.callback_query
    if query is None or query.data is None:
        return
    if not query.data.startswith(_SAVE_PREFIX):
        return
    await query.answer()
    bucket = query.data[len(_SAVE_PREFIX):]
    if bucket not in _BUCKETS:
        await query.edit_message_text(f"⚠️ Unknown bucket: {bucket!r}.")
        return
    text = (context.user_data or {}).pop(_PENDING_KEY, None)
    if not text:
        await query.edit_message_text(
            "⚠️ No pending lesson — send /save <text> first."
        )
        return

    title = " ".join(text.split()[:20])
    result = await save_lesson(
        title=title,
        content=text,
        bucket=bucket,
        tags=["telegram-capture"],
        category="OPS",
    )

    status = result.get("status")
    if status == "saved":
        approved = result.get("auto_approved", False)
        marker = "✅ active" if approved else "⏳ pending review"
        lid = result.get("id", "?")
        await query.edit_message_text(
            f"💾 Lesson saved → {marker}\nID: `{lid}`\nBucket: {bucket}",
            parse_mode="Markdown",
        )
    elif status == "merge_candidate":
        await query.edit_message_text(
            f"🔁 Likely duplicate (merge candidate "
            f"`{result.get('candidate_id', '?')}`).\nNo new row inserted.",
            parse_mode="Markdown",
        )
    elif status == "degraded":
        reason = result.get("degraded_reason", "?")
        await query.edit_message_text(f"🔴 DB degraded: {reason}.")
    else:
        await query.edit_message_text(
            f"❌ Save failed: {result.get('error', 'unknown error')}"
        )
