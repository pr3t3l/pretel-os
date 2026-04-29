"""/idea <text> — capture an idea from Telegram (M5.B.5.1).

Plan §1 Q3 fallback: no `ideas` MCP tool exists today, so this
handler routes to `save_lesson` with `category='PLAN'` and
`tags=['idea','telegram-capture']`. When a dedicated `ideas` tool
ships, swap the import; the operator's interface stays identical.

Same two-step bucket-prompt flow as `/save` (see handlers/save.py).
"""
from __future__ import annotations

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from mcp_server.tools.lessons import save_lesson

from ._guard import operator_only

log = logging.getLogger(__name__)

_BUCKETS = ("personal", "business", "scout")
_PENDING_KEY = "idea_pending_text"
_IDEA_PREFIX = "idea:"
IDEA_CALLBACK_PATTERN = r"^idea:"


@operator_only
async def idea_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """`/idea <text>`. Stashes the idea and prompts for a bucket."""
    if update.message is None:
        return
    args = context.args or []
    if not args:
        await update.message.reply_text(
            "Usage: /idea <text>\n"
            "Example: /idea VETT Phase 2 — pricing playbook for solo agents."
        )
        return
    text = " ".join(args).strip()
    if context.user_data is not None:
        context.user_data[_PENDING_KEY] = text

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    bucket.title(), callback_data=f"{_IDEA_PREFIX}{bucket}"
                )
                for bucket in _BUCKETS
            ]
        ]
    )
    await update.message.reply_text(
        f"💡 Idea preview:\n\n{text}\n\nPick a bucket:",
        reply_markup=keyboard,
    )


@operator_only
async def idea_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the bucket-selection inline keyboard for /idea."""
    query = update.callback_query
    if query is None or query.data is None:
        return
    if not query.data.startswith(_IDEA_PREFIX):
        return
    await query.answer()
    bucket = query.data[len(_IDEA_PREFIX):]
    if bucket not in _BUCKETS:
        await query.edit_message_text(f"⚠️ Unknown bucket: {bucket!r}.")
        return
    text = (context.user_data or {}).pop(_PENDING_KEY, None)
    if not text:
        await query.edit_message_text(
            "⚠️ No pending idea — send /idea <text> first."
        )
        return

    title = " ".join(text.split()[:20])
    result = await save_lesson(
        title=title,
        content=text,
        bucket=bucket,
        tags=["idea", "telegram-capture"],
        category="PLAN",
    )

    status = result.get("status")
    if status == "saved":
        lid = result.get("id", "?")
        await query.edit_message_text(
            f"💡 Idea saved → ID `{lid}`\nBucket: {bucket}",
            parse_mode="Markdown",
        )
    elif status == "merge_candidate":
        await query.edit_message_text(
            f"🔁 Likely duplicate (merge candidate "
            f"`{result.get('candidate_id', '?')}`).",
            parse_mode="Markdown",
        )
    elif status == "degraded":
        await query.edit_message_text(
            f"🔴 DB degraded: {result.get('degraded_reason', '?')}."
        )
    else:
        await query.edit_message_text(
            f"❌ Save failed: {result.get('error', 'unknown error')}"
        )
