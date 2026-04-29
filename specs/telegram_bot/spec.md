# specs/telegram_bot/spec.md

**Module:** Module 5 — telegram_bot
**Status:** Draft (M5.T1.1)
**Last updated:** 2026-04-29
**Authority:** `PROJECT_FOUNDATION.md` §4 Module 5 · `INTEGRATIONS.md` §8 (Telegram Bot API) · `CONSTITUTION.md` §2.2 (MCP gateway), §3 (data sovereignty), §8.43 (degraded mode) · `DATA_MODEL.md` §4.6 (`conversation_sessions`), §3.9 (`cross_pollination_queue`).

---

## 1. Purpose

A mobile-first capture and review surface for pretel-os. Right now the
operator can talk to the system through Claude.ai (web), Claude Code
(terminal), and Claude mobile — all routed through the MCP server.
Module 5 adds Telegram as a fourth surface, optimized for **quick
capture from anywhere** (voice notes, one-line lessons) and **batch
review of pending knowledge** (lessons + cross-pollination proposals
queued by the Reflection worker).

The bot is a complement to Claude.ai, not a replacement. Claude.ai
remains the deep-work surface (architecture, debugging, planning).
Telegram covers the cases Claude can't: walking the dog, driving, in
the middle of work — moments when the operator notices something
worth capturing but won't open a laptop.

---

## 2. Scope

### 2.1 In scope

- **Capture:** `/save <text>` and voice messages → `save_lesson` via
  MCP tool import. Voice goes through OpenAI Whisper (`whisper-1`)
  before save.
- **Quick capture:** `/idea <text>` → `save_lesson(category='PLAN',
  tags=['idea','telegram-capture'])` (or dedicated `ideas` table tool
  if available — fallback to lessons).
- **Review:** `/review_pending` walks pending lessons one-by-one with
  inline `[✅ Aprobar]` `[❌ Rechazar]` `[⏭ Saltar]` buttons.
- **Cross-pollination review:** `/cross_poll_review` walks
  `cross_pollination_queue` rows one-by-one.
- **Health:** `/status` parallel-checks MCP server + DB + LiteLLM +
  n8n, returns color-coded summary (🟢/🟡/🔴) per integration.
- **Session tracking:** every bot turn creates / updates a
  `conversation_sessions` row with `client_origin='telegram'`.
  Per-turn transcript appended to a JSONL file at `transcript_path`.
  Idle sessions auto-close after 10 minutes via background task.
- **MCP tool extensions:** 5 new tools shipped by Phase A —
  `list_pending_lessons`, `approve_lesson`, `reject_lesson`,
  `list_pending_cross_pollination`, `resolve_cross_pollination`. These
  benefit ALL clients (Claude.ai can also approve lessons), not just
  the bot.

### 2.2 Out of scope

- **Real-time conversational Q&A.** The bot is for capture and review,
  not for interactive deep work. Use Claude.ai for that.
- **Multi-user.** Operator-only via `TELEGRAM_OPERATOR_CHAT_ID` guard
  on every command except `/start`. Group chat support is explicitly
  out of scope.
- **Webhook transport.** Long polling for v1 (zero config); webhook
  migration is a future task (no public subdomain needed today).
- **Voice synthesis replies.** Bot replies are text only.
- **Replacing Claude.ai.** The bot complements, never replaces.

---

## 3. Public interface

### 3.1 Telegram commands

| Command | Behavior |
|---|---|
| `/start` | Welcome message + command list. No operator guard (anyone can /start to see "private bot" rejection). |
| `/help` | Alias for `/start`. |
| `/save <text>` | Inline-keyboard bucket prompt → `save_lesson(...)`. |
| `/idea <text>` | Persisted via dedicated `ideas` tool if available, else `save_lesson(category='PLAN', tags=['idea','telegram-capture'])`. |
| `/status` | Health summary (4 integrations, parallel checks, ≤5s timeout each). |
| `/review_pending` | Walks pending lessons one-by-one with approve/reject/skip inline buttons. |
| `/cross_poll_review` | Walks `cross_pollination_queue` rows one-by-one. |
| (voice message) | Whisper-transcribed → bucket prompt → `save_lesson(category='OPS', tags=['voice-capture','telegram'])`. |

### 3.2 New MCP tools (Phase A)

```python
list_pending_lessons(bucket: str | None = None, limit: int = 10) -> dict
# returns {status, results: [{id, title, content, bucket, category, tags, created_at}, ...]}
# clamped: 1 ≤ limit ≤ 50; ordered by created_at ASC

approve_lesson(id: str) -> dict
# returns {status: 'ok', approved: bool}
# UPDATE lessons SET status='active', reviewed_at=now(), reviewed_by='operator'
# WHERE id=$1 AND status='pending_review'

reject_lesson(id: str, reason: str) -> dict
# returns {status: 'ok', rejected: bool}
# UPDATE lessons SET status='rejected', reviewed_at=now(), reviewed_by='operator',
#   metadata=metadata || jsonb_build_object('reject_reason', $2)
# WHERE id=$1 AND status='pending_review'

list_pending_cross_pollination(limit: int = 10) -> dict
# returns {status, results: [{id, origin_bucket, target_bucket, idea, reasoning,
#   suggested_application, priority, confidence_score, impact_score, created_at}, ...]}
# clamped: 1 ≤ limit ≤ 50

resolve_cross_pollination(id: str, action: str, note: str | None = None) -> dict
# returns {status: 'ok', resolved: bool, new_status: 'applied' | 'dismissed'}
# action ∈ {'approve', 'reject'} → maps to cross_poll_status 'applied' / 'dismissed'
# UPDATE cross_pollination_queue SET status=<mapped>, resolved_at=now(),
#   reviewed_at=now(), resolution_note=$3
# WHERE id=$1 AND status IN ('pending', 'under_review')
```

Status-enum mapping decisions:
- `lesson_status` enum has both `archived` and `rejected` values.
  `reject_lesson` writes `status='rejected'` (more accurate semantics
  than `archived`, which is for stale-but-once-active lessons).
- `cross_poll_status` enum: `pending → applied | dismissed`.
  `resolve_cross_pollination(action='approve')` writes `applied`;
  `action='reject'` writes `dismissed`.

### 3.3 Bot ↔ MCP boundary (Q2 architectural decision)

The bot imports tool functions directly from `src/mcp_server/tools/`
via Python imports (same virtualenv). It does NOT call the MCP server
over HTTP/MCP protocol. CONSTITUTION §2.2 protects EXTERNAL client
portability (Claude.ai, Claude Code) — the bot is an internal operator
interface, like the Reflection worker (Module 6) or Dream Engine.

Consequence: **bot-initiated tool calls do not generate `routing_logs`
rows.** Telemetry for bot calls lives in `usage_logs` (via the existing
`log_usage` helper) and `conversation_sessions` (per-turn metadata).
Acceptable trade-off — bot calls are operator-driven review actions,
not context-assembly turns.

---

## 4. Data contracts

### 4.1 Tables read

- `lessons` (read pending_review rows; write status updates).
- `cross_pollination_queue` (read pending rows; write status updates).
- `conversation_sessions` (read for resume; write on every turn).

### 4.2 Tables written

| Table | When | Columns touched |
|---|---|---|
| `lessons` | save / approve / reject | INSERT via `save_lesson`; UPDATE `status`, `reviewed_at`, `reviewed_by`, `metadata` |
| `cross_pollination_queue` | resolve | UPDATE `status`, `resolved_at`, `reviewed_at`, `resolution_note` |
| `conversation_sessions` | every turn | INSERT (first turn), UPDATE `last_seen_at`, `turn_count`, `closed_at` |
| `usage_logs` | every command | INSERT via `log_usage` |

### 4.3 External services

| Service | API | Auth | Cost |
|---|---|---|---|
| Telegram Bot API | python-telegram-bot v21 long-poll | `TELEGRAM_BOT_TOKEN` | $0 |
| OpenAI Whisper | `POST /v1/audio/transcriptions` | `OPENAI_API_KEY` | ~$0.006/minute |

---

## 5. Failure modes

Per CONSTITUTION §8.43. The bot never crashes the operator's flow —
every failure produces a Telegram reply describing what went wrong.

| Dependency | Failure mode | Bot behavior |
|---|---|---|
| Telegram API unreachable | Long-poll timeout / 5xx | python-telegram-bot retries with backoff; bot keeps running. |
| Postgres unreachable | `is_healthy()` returns False | All commands except `/start` and `/help` reply with `🔴 DB unavailable, try again in a moment`. Capture intents queue to `journal_mod` for replay. |
| Whisper API unreachable | API timeout / 5xx | Voice message reply: `🔴 No pude transcribir. Envía /save <texto> a mano por ahora.` |
| `OPENAI_API_KEY` missing | env-var unset at startup | Voice handler returns `🔴 Whisper no configurado.` Other commands work normally. |
| `MCP_SHARED_SECRET` missing | env-var unset at startup | Bot logs warning at startup but continues — bot doesn't call HTTP MCP, so the secret is irrelevant for bot operation. |
| `TELEGRAM_OPERATOR_CHAT_ID` mismatch | random user messages bot | Operator-guard rejects with `🔒 This is a private bot.` and logs to `usage_logs` with `success=False`. |
| n8n / LiteLLM unreachable during `/status` | health-check timeout | `/status` reply marks that integration 🔴 with reason; other rows still report. |

---

## 6. Non-goals

- **Reasoning about operator intent.** Bot parses commands and routes
  to MCP tools. Reasoning happens at `save_lesson` (auto-approval
  heuristic) or in Claude.ai.
- **Generating content for the operator.** Bot replies are
  confirmations and summaries only, never essays.
- **Cross-bucket inference.** That's the Reflection worker (Module 6).
- **Cost optimization beyond Whisper choice.** Whisper-1 is cheap
  enough at solo-operator scale (~$0.90/month at heavy use).

---

## 7. Success criteria (Module 5 exit gate)

The roadmap's three done-when bullets, made operationally testable:

1. **Approve / reject pending lessons from Telegram.** Demonstrated by:
   `save_lesson(...)` (status=`pending_review`) → operator
   `/review_pending` in Telegram → `[✅ Aprobar]` → `search_lessons`
   finds it as `active`. Same flow with `[❌ Rechazar]` → status
   `rejected` and `search_lessons(include_archived=False)` excludes it.

2. **Review cross-pollination from Telegram.** Demonstrated by: insert
   a synthetic `cross_pollination_queue` row → operator
   `/cross_poll_review` → `[✅ Approve]` → row status=`applied` with
   `resolved_at` populated.

3. **Voice note → persisted lesson.** Demonstrated by: operator sends
   30s voice note → bot transcribes via Whisper → bot prompts for
   bucket → operator picks → row appears in `lessons` table with
   `tags @> '{voice-capture,telegram}'`.

Plus: `conversation_sessions` row exists for every bot turn (verifies
M4 D.2 Q8 unblocking); `/status` reports all 4 integrations.

---

## 8. Open questions

None at spec time. Phase-specific Q-decisions (analogous to
`phase_b_close.md`, `phase_c_close.md`, `phase_d_close.md`) will be
captured in `phase_*_close.md` if they emerge during implementation.

---

## 9. Doc registry

This file is registered in `docs/PROJECT_FOUNDATION.md` §6 Doc registry
when Module 5 ships.

**End of spec.md.**
