"""/review_pending — walk pending lessons one-by-one (M5.C.1.1).

Flow per `specs/telegram_bot/plan.md` §5.2:

1. `/review_pending` → fetch first pending lesson → reply with title +
   content excerpt + inline keyboard `[✅ Aprobar] [❌ Rechazar]
   [⏭ Saltar]`.
2. ✅ Aprobar callback → `approve_lesson(id)` → "Aprobada ✅" → next.
3. ❌ Rechazar callback → stash `awaiting_reason_for=id` in
   `user_data` + prompt "Envía la razón:" → next free-form text
   message becomes the reason → `reject_lesson(id, reason)` → next.
4. ⏭ Saltar callback → skip without calling either tool → next.
5. When queue is empty → "No hay lecciones pendientes 🎉".

State machine intentionally avoids `ConversationHandler` — the
`user_data["review_state"]` dict captures the awaiting-reason cycle
in ~5 LoC and the resulting handlers are trivial to mock-test.
"""
from __future__ import annotations

import logging
from typing import Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from mcp_server.tools.lessons import (
    approve_lesson,
    list_pending_lessons,
    reject_lesson,
)

from ._guard import operator_only

log = logging.getLogger(__name__)

REVIEW_CALLBACK_PATTERN = r"^review:"
_REVIEW_PREFIX = "review:"
_STATE_KEY = "review_state"
_EXCERPT_CHARS = 200


def _build_keyboard(lesson_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Aprobar", callback_data=f"{_REVIEW_PREFIX}approve:{lesson_id}"
                ),
                InlineKeyboardButton(
                    "❌ Rechazar", callback_data=f"{_REVIEW_PREFIX}reject:{lesson_id}"
                ),
                InlineKeyboardButton(
                    "⏭ Saltar", callback_data=f"{_REVIEW_PREFIX}skip:{lesson_id}"
                ),
            ]
        ]
    )


def _format_lesson_card(lesson: dict[str, Any]) -> str:
    title = lesson.get("title", "(sin título)")
    content = lesson.get("content") or ""
    excerpt = content[:_EXCERPT_CHARS]
    if len(content) > _EXCERPT_CHARS:
        excerpt += "…"
    bucket = lesson.get("bucket", "?")
    category = lesson.get("category", "?")
    return (
        f"📋 *{title}*\n"
        f"_bucket:_ {bucket} · _category:_ {category}\n\n"
        f"{excerpt}"
    )


async def _send_next_or_empty(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    use_edit: bool,
) -> None:
    """Fetch the next pending lesson and reply / edit accordingly."""
    result = await list_pending_lessons(limit=1)
    if result.get("status") == "degraded":
        text = (
            f"🔴 DB degraded: {result.get('degraded_reason', '?')}. "
            "Try /review_pending again later."
        )
        await _reply(update, context, text, use_edit=use_edit)
        return

    pending = result.get("results") or []
    if not pending:
        await _reply(
            update, context,
            "No hay lecciones pendientes 🎉",
            use_edit=use_edit,
        )
        return

    lesson = pending[0]
    card = _format_lesson_card(lesson)
    keyboard = _build_keyboard(lesson["id"])
    await _reply(update, context, card, use_edit=use_edit,
                 reply_markup=keyboard, parse_mode="Markdown")


async def _reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    *,
    use_edit: bool,
    reply_markup: InlineKeyboardMarkup | None = None,
    parse_mode: str | None = None,
) -> None:
    """Reply via callback_query.edit when use_edit, else via message."""
    if use_edit and update.callback_query is not None:
        await update.callback_query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode=parse_mode
        )
    elif update.message is not None:
        await update.message.reply_text(
            text, reply_markup=reply_markup, parse_mode=parse_mode
        )


@operator_only
async def review_pending_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """`/review_pending` — kick off the review flow."""
    # Fresh start — clear any stale state.
    if context.user_data is not None:
        context.user_data.pop(_STATE_KEY, None)
    await _send_next_or_empty(update, context, use_edit=False)


@operator_only
async def review_pending_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the [✅ Aprobar] [❌ Rechazar] [⏭ Saltar] callback."""
    query = update.callback_query
    if query is None or query.data is None:
        return
    if not query.data.startswith(_REVIEW_PREFIX):
        return
    await query.answer()

    parts = query.data[len(_REVIEW_PREFIX):].split(":", 1)
    if len(parts) != 2:
        await query.edit_message_text(
            f"⚠️ Malformed callback data: {query.data!r}"
        )
        return
    action, lesson_id = parts

    if action == "approve":
        result = await approve_lesson(id=lesson_id)
        if result.get("status") == "ok" and result.get("approved"):
            await query.edit_message_text("Aprobada ✅")
        elif result.get("status") == "degraded":
            await query.edit_message_text(
                f"🔴 DB degraded: {result.get('degraded_reason', '?')}."
            )
            return
        else:
            await query.edit_message_text(
                "⚠️ No se aprobó (ya procesada o no existe)."
            )
        await _send_next_or_empty(update, context, use_edit=False)
        return

    if action == "skip":
        await query.edit_message_text("Saltada ⏭")
        await _send_next_or_empty(update, context, use_edit=False)
        return

    if action == "reject":
        if context.user_data is not None:
            context.user_data[_STATE_KEY] = {
                "awaiting_reason_for": lesson_id,
            }
        await query.edit_message_text(
            "❌ Envía la razón en el siguiente mensaje (texto libre)."
        )
        return

    await query.edit_message_text(f"⚠️ Acción desconocida: {action!r}")


@operator_only
async def review_pending_reason_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle a free-form text message that fills in a reject reason.

    Registered as `MessageHandler(filters.TEXT & ~filters.COMMAND, ...)`
    so it only fires for plain text (commands handled separately). The
    handler short-circuits when `user_data["review_state"]` doesn't
    indicate an awaiting-reason cycle, so plain operator chatter is a
    no-op.
    """
    state = (context.user_data or {}).get(_STATE_KEY) or {}
    awaiting = state.get("awaiting_reason_for")
    if not awaiting:
        return  # not in a reject-reason cycle; ignore.

    if update.message is None or update.message.text is None:
        return

    reason = update.message.text.strip()
    if not reason:
        await update.message.reply_text(
            "❌ La razón no puede estar vacía. Envía el texto otra vez."
        )
        return

    # Clear state BEFORE the reject call so a tool error doesn't leave
    # us stuck awaiting reason forever.
    if context.user_data is not None:
        context.user_data.pop(_STATE_KEY, None)

    result = await reject_lesson(id=awaiting, reason=reason)
    if result.get("status") == "ok" and result.get("rejected"):
        await update.message.reply_text("Rechazada ❌")
    elif result.get("status") == "degraded":
        await update.message.reply_text(
            f"🔴 DB degraded: {result.get('degraded_reason', '?')}."
        )
        return
    else:
        await update.message.reply_text(
            "⚠️ No se rechazó (ya procesada o no existe)."
        )

    await _send_next_or_empty(update, context, use_edit=False)
