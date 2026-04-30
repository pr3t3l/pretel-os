"""/cross_poll_review — walk cross_pollination_queue rows (M5.C.2.1).

Simpler than /review_pending — no reason prompt. Each pending row
shows with `[✅ Aprobar] [❌ Rechazar]`; the callback invokes
`resolve_cross_pollination(id, action)` (action ∈ {'approve','reject'}
mapping to status 'applied' / 'dismissed' on the server side).

Flow:
1. `/cross_poll_review` → fetch first pending → reply with origin →
   target / idea / reasoning + inline keyboard.
2. ✅ Aprobar → `resolve_cross_pollination(id, 'approve')` → next.
3. ❌ Rechazar → `resolve_cross_pollination(id, 'reject')` → next.
4. Empty queue → "No hay propuestas pendientes 🎉".
"""
from __future__ import annotations

import logging
from typing import Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from mcp_server.tools.cross_pollination import (
    list_pending_cross_pollination,
    resolve_cross_pollination,
)

from ._guard import operator_only

log = logging.getLogger(__name__)

XPOLL_CALLBACK_PATTERN = r"^xpoll:"
_XPOLL_PREFIX = "xpoll:"
_REASONING_CHARS = 200


def _build_keyboard(row_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Aprobar", callback_data=f"{_XPOLL_PREFIX}approve:{row_id}"
                ),
                InlineKeyboardButton(
                    "❌ Rechazar", callback_data=f"{_XPOLL_PREFIX}reject:{row_id}"
                ),
            ]
        ]
    )


def _format_proposal_card(row: dict[str, Any]) -> str:
    origin = row.get("origin_bucket", "?")
    target = row.get("target_bucket", "?")
    idea = row.get("idea", "(sin idea)")
    reasoning = row.get("reasoning") or ""
    excerpt = reasoning[:_REASONING_CHARS]
    if len(reasoning) > _REASONING_CHARS:
        excerpt += "…"
    suggestion = row.get("suggested_application")
    parts = [
        f"🔁 *{origin} → {target}*",
        "",
        f"*Idea:* {idea}",
        "",
        f"*Reasoning:* {excerpt}",
    ]
    if suggestion:
        parts.append("")
        parts.append(f"*Suggested application:* {suggestion}")
    return "\n".join(parts)


async def _reply(
    update: Update,
    text: str,
    *,
    use_edit: bool,
    reply_markup: InlineKeyboardMarkup | None = None,
    parse_mode: str | None = None,
) -> None:
    if use_edit and update.callback_query is not None:
        await update.callback_query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode=parse_mode
        )
    elif update.message is not None:
        await update.message.reply_text(
            text, reply_markup=reply_markup, parse_mode=parse_mode
        )


async def _send_next_or_empty(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    use_edit: bool,
) -> None:
    result = await list_pending_cross_pollination(limit=1)
    if result.get("status") == "degraded":
        await _reply(
            update,
            f"🔴 DB degraded: {result.get('degraded_reason', '?')}.",
            use_edit=use_edit,
        )
        return

    rows = result.get("results") or []
    if not rows:
        await _reply(
            update,
            "No hay propuestas pendientes 🎉",
            use_edit=use_edit,
        )
        return

    row = rows[0]
    card = _format_proposal_card(row)
    keyboard = _build_keyboard(row["id"])
    await _reply(
        update, card, use_edit=use_edit,
        reply_markup=keyboard, parse_mode="Markdown",
    )


@operator_only
async def cross_poll_review_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """`/cross_poll_review` — kick off the cross-pollination flow."""
    await _send_next_or_empty(update, context, use_edit=False)


@operator_only
async def cross_poll_review_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the [✅ Aprobar] [❌ Rechazar] callback for cross-poll."""
    query = update.callback_query
    if query is None or query.data is None:
        return
    if not query.data.startswith(_XPOLL_PREFIX):
        return
    await query.answer()

    parts = query.data[len(_XPOLL_PREFIX):].split(":", 1)
    if len(parts) != 2:
        await query.edit_message_text(
            f"⚠️ Malformed callback data: {query.data!r}"
        )
        return
    action, row_id = parts

    if action not in ("approve", "reject"):
        await query.edit_message_text(f"⚠️ Acción desconocida: {action!r}")
        return

    result = await resolve_cross_pollination(id=row_id, action=action)
    status = result.get("status")
    if status == "ok" and result.get("resolved"):
        new_status = result.get("new_status", "?")
        marker = "✅" if action == "approve" else "❌"
        await query.edit_message_text(
            f"{marker} Resuelta — nuevo estado: {new_status}"
        )
    elif status == "degraded":
        await query.edit_message_text(
            f"🔴 DB degraded: {result.get('degraded_reason', '?')}."
        )
        return
    else:
        await query.edit_message_text(
            f"⚠️ No se resolvió (ya procesada o error: "
            f"{result.get('error', '?')})."
        )

    await _send_next_or_empty(update, context, use_edit=False)
