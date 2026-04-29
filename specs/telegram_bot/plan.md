# specs/telegram_bot/plan.md

**Module:** Module 5 — telegram_bot
**Status:** Draft (M5.T1.2)
**Last updated:** 2026-04-29
**Authority:** `specs/telegram_bot/spec.md` (M5.T1.1) · `CONSTITUTION.md §6 rule 31` (every phase has done-when).

> **Phase gate (SDD §6 rule 31):** Each phase below ends with an explicit done-when line. No phase advances without the prior gate met.

---

## 1. Architectural decisions (Q1–Q6)

### Q1 — Bot identity

Use the existing `@Robotin1620_Bot` token from `.env.pretel_os`
(`TELEGRAM_BOT_TOKEN`). Same token, new code. No BotFather interaction
unless rename is desired. The token + `TELEGRAM_OPERATOR_CHAT_ID` are
already provisioned and tested.

### Q2 — Bot ↔ MCP boundary: direct Python imports, not HTTP

The bot imports tool functions from `src/mcp_server/tools/` directly
(same virtualenv). No HTTP / MCP-protocol round-trips.

**Why:** the MCP protocol exists for EXTERNAL clients (Claude.ai,
Claude Code, mobile) that don't run on the same machine. The bot is
on the Vivobook, shares the venv, has direct DB access. HTTP would
add latency, require an async HTTP client, and protect nothing —
CONSTITUTION §2.2's "single MCP gateway" invariant is about CLIENT
portability, not about every internal component going through the
network. Same pattern as Reflection worker (M6) and Dream Engine.

**Trade-off:** bot-initiated tool calls do NOT generate `routing_logs`
rows (those are for context-assembly turns through the Router).
Telemetry lives in `usage_logs` + `conversation_sessions`. Acceptable
— bot calls are review actions, not Router turns.

**Alternatives rejected:** HTTP / MCP transport (latency, async-client
overhead, no functional gain at single-operator scale).

### Q3 — Missing MCP tools for review workflows

Five new tools shipped by Phase A:

| Tool | File | Purpose |
|---|---|---|
| `list_pending_lessons(bucket?, limit?)` | `tools/lessons.py` | SELECT WHERE status='pending_review' |
| `approve_lesson(id)` | `tools/lessons.py` | UPDATE status='active' + reviewed_at + reviewed_by |
| `reject_lesson(id, reason)` | `tools/lessons.py` | UPDATE status='rejected' + reason in metadata |
| `list_pending_cross_pollination(limit?)` | `tools/cross_pollination.py` (new) | SELECT WHERE status='pending' |
| `resolve_cross_pollination(id, action, note?)` | `tools/cross_pollination.py` | UPDATE status='applied' / 'dismissed' + resolved_at |

These benefit ALL clients (Claude.ai also gains approve/reject), not
just the bot. Registered with FastMCP via `app.tool(...)` in
`main.py` alongside existing tools.

**Status-enum decisions:**
- `lesson_status` includes both `'archived'` and `'rejected'`. We use
  `'rejected'` for operator rejection (more accurate semantics);
  `'archived'` is reserved for stale-but-once-active lessons.
- `cross_poll_status`: `pending → applied | dismissed` per
  `action='approve'` / `'reject'` arg. Never directly write
  `under_review` from this tool — that's a Reflection-worker state.

### Q4 — Voice transcription: OpenAI Whisper API

`whisper-1` via existing `OPENAI_API_KEY`. ~$0.006 per minute. A 30s
voice note costs ~$0.003. At 10 voice notes/day (heavy use), $0.90/mo.

**Alternatives rejected:**
- whisper.cpp (local): Vivobook has no GPU; ~30s per 30s clip.
  Spanish quality gap relative to whisper-1.
- Google Cloud Speech-to-Text: new API key + billing project.

### Q5 — Session tracking integration

Every bot turn touches `conversation_sessions`:

- First message (or `/start`) → INSERT new row, `client_origin='telegram'`,
  `operator_id='alfredo'`, `transcript_path='~/pretel-os-data/transcripts/{session_id}.jsonl'`.
- Subsequent messages → UPDATE `last_seen_at`, increment `turn_count`;
  append `{role, content, timestamp}` to the JSONL transcript.
- Idle 10 min → background task closes session with
  `close_reason='idle_10min'`, populates `closed_at`.

This unblocks the Router's `_get_session_excerpt()` deferral (M4 D.2
Q8). Future: when Claude.ai itself starts populating
`conversation_sessions` (transport-layer work in a Module 3 extension),
the Router will get session-excerpt context for every client — not just
Telegram. Out of scope for Module 5.

### Q6 — Long polling vs webhook

Long polling for v1 per `INTEGRATIONS §8.4`. Zero config — no public
subdomain, no SSL termination, no webhook registration, works behind
Tailscale-only.

**Migration path:** webhook later via cloudflared ingress rule +
`bot.set_webhook(url)`. python-telegram-bot v21 handles both
transparently. Not blocked.

---

## 2. Phase dependency graph

```
       ┌────────────────────────────────────┐
       │ Phase A — Review MCP tools + SDD   │
       │ trinity (no bot code yet)          │
       └────────────────┬───────────────────┘
                        ▼
       ┌────────────────────────────────────┐
       │ Phase B — Bot skeleton + core      │
       │ commands (/start, /save, /idea,    │
       │ /status) + systemd                 │
       └────────────────┬───────────────────┘
                        ▼
       ┌────────────────────────────────────┐
       │ Phase C — Review flows             │
       │ (/review_pending, /cross_poll_review)│
       └────────────────┬───────────────────┘
                        ▼
       ┌────────────────────────────────────┐
       │ Phase D — Voice + session tracking │
       └────────────────┬───────────────────┘
                        ▼
       ┌────────────────────────────────────┐
       │ Phase E — Module 5 gate + cleanup  │
       │ + tag                              │
       └────────────────────────────────────┘
```

A → B → C → D → E. No parallelism — each phase depends on the prior.

---

## 3. Phase A — Review MCP tools + SDD trinity

### 3.1 Goal

Ship the 5 new MCP tools the bot will need (and that Claude.ai
benefits from) BEFORE writing any bot code. SDD trinity in place per
`runbooks/sdd_module_kickoff.md`.

### 3.2 Scope

**In:**
- `specs/telegram_bot/{spec,plan,tasks}.md`
- Module 5 milestone section in root `tasks.md`
- `list_pending_lessons` + `approve_lesson` + `reject_lesson` added
  to `src/mcp_server/tools/lessons.py`
- `src/mcp_server/tools/cross_pollination.py` (new) with
  `list_pending_cross_pollination` + `resolve_cross_pollination`
- All 5 tools registered in `src/mcp_server/main.py`
- `tests/tools/test_review_tools.py` — ≥8 tests covering happy-path
  + not-found + already-processed edge cases

**Out:**
- Any `src/telegram_bot/` code (Phase B).
- Any voice handling (Phase D).

### 3.3 Done when

- Trinity files exist; root tasks.md has M5 section per kickoff convention.
- All 5 tools registered with FastMCP and importable from `tools/`.
- Test suite passes ≥8 tests against `pretel_os_test`.
- mypy clean across edited / new files.

---

## 4. Phase B — Bot skeleton + core commands

### 4.1 Goal

A running bot that responds to `/start`, `/help`, `/save`, `/idea`,
`/status`. Operator-only guard enforced. systemd service unit ready
for `systemctl --user start pretel-os-bot`.

### 4.2 Scope

**In:**
- `src/telegram_bot/` package (`__init__.py`, `bot.py`, `handlers/`,
  `config.py`)
- ApplicationBuilder + long-poll entry point (`python -m telegram_bot`)
- Operator-guard middleware (`update.effective_user.id ==
  TELEGRAM_OPERATOR_CHAT_ID`)
- `/start`, `/help`, `/save`, `/idea`, `/status` handlers
- `infra/systemd/pretel-os-bot.service`
- `tests/telegram_bot/test_handlers.py` — ≥5 tests

**Out:**
- Voice (Phase D).
- Review flows (Phase C).

### 4.3 Done when

- `python -m telegram_bot` starts and connects (visible online in
  Telegram).
- `/start` from operator chat returns command list.
- `/start` from random chat is rejected with "private bot" message.
- `/save test text` round-trip → row in `lessons` table.
- `/status` returns 4-integration health summary in <5s.
- systemd unit starts via `systemctl --user start pretel-os-bot`.
- Tests pass.

---

## 5. Phase C — Review flows

### 5.1 Goal

`/review_pending` and `/cross_poll_review` — interactive walks with
inline keyboards.

### 5.2 Scope

**In:**
- `/review_pending` ConversationHandler (or callback-query state
  machine) — walks pending lessons, inline buttons for approve / reject
  / skip.
- `/cross_poll_review` — same pattern over `cross_pollination_queue`.
- `tests/telegram_bot/test_review_flows.py` — ≥4 tests covering
  full walk, approve, reject (with reason prompt), skip, empty queue.

**Out:**
- Voice (Phase D).

### 5.3 Done when

- Operator walks all pending lessons via Telegram, approving / rejecting
  / skipping.
- Operator walks all `cross_pollination_queue` rows via Telegram.
- Tests pass.

---

## 6. Phase D — Voice + session tracking

### 6.1 Goal

Voice message → Whisper → save_lesson. Every turn tracked in
`conversation_sessions`. Idle sessions auto-close.

### 6.2 Scope

**In:**
- Voice handler: download .ogg → Whisper API → bucket prompt →
  `save_lesson(category='OPS', tags=['voice-capture','telegram'])`.
- Session tracker: INSERT on first message; UPDATE per turn;
  background asyncio task closes idle sessions every 5 min.
- JSONL transcript writer at `~/pretel-os-data/transcripts/{session_id}.jsonl`.
- Tests: ≥4 tests, mock Whisper for voice; real DB for session.

**Out:**
- Webhook migration.

### 6.3 Done when

- Voice note in operator chat → text in `lessons.content` with
  `tags @> '{voice-capture,telegram}'`.
- `conversation_sessions` row created on first message; updated on
  each subsequent; closed after 10 min idle.
- Transcript JSONL contains `{role, content, timestamp}` per turn.
- Tests pass.

---

## 7. Phase E — Module 5 gate + cleanup

### 7.1 Goal

Verify the 3 roadmap done-when bullets. Update the permanent docs.
Tag `module-5-complete`.

### 7.2 Scope

**In:**
- Operator demonstrates the 3 success-criteria bullets per spec §7.
- `specs/telegram_bot/tasks.md` — all atomic checkboxes `[x]` with
  commit hashes.
- Root `tasks.md` — Module 5 milestones `[x]`.
- `SESSION_RESTORE.md` §2 + §13 updated.
- `tasks.archive.md` — Module 5 closure summary.
- `docs/PROJECT_FOUNDATION.md` — `specs/telegram_bot/` registry row →
  Active.
- Tag candidate `module-5-complete` (operator-driven).

### 7.3 Done when

- All permanent docs reflect Module 5 closure.
- Tag exists locally (push deferred to operator).

---

## 8. Phase ordering & cost

| Slot | Phase | Cost |
|---|---|---|
| 1 | A — Review tools + SDD trinity | $0 (no LLM, no embed) |
| 2 | B — Bot skeleton + core commands | $0 |
| 3 | C — Review flows | $0 |
| 4 | D — Voice + session tracking | ~$0.01–0.05 (Whisper test calls) |
| 5 | E — Module 5 gate + tag | $0 |

**Total cost:** ~$0.01–0.05. **Claude Code sessions:** 5–7.

---

## 9. Pre-Module-5 task

The Module-4 follow-up `5db4bc6f` (LayerBundleCache listener +
`client_origin` plumb-through + sync pool) should ship before Phase B
begins, since the bot will be a new MCP-adjacent component generating
cache-invalidation events. Doable in a quick session. Not a blocker
for Phase A (no bot code yet).

---

## 10. Module 5 exit gate (re-stating spec §7)

Module 5 is done iff:

- Operator approves / rejects pending lessons from Telegram (live demo).
- Operator reviews `cross_pollination_queue` from Telegram (live demo).
- Voice note → persisted lesson via Whisper + `save_lesson` (live demo).
- `/status` reports all 4 integrations.
- `conversation_sessions` populated for every bot turn (Q5 verified).
- All Phase A–E checkboxes `[x]` in `specs/telegram_bot/tasks.md`.
- Tag `module-5-complete` candidate created on the closing commit.

---

## 11. Risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| `/review_pending` ConversationHandler complexity | Medium | python-telegram-bot v21 supports states natively. If hand-rolled callback-query state machine grows past ~150 LoC, refactor to `ConversationHandler`. |
| Whisper Spanish quality | Low | `whisper-1` is operator-tested in OpenClaw era. Fall back: bot reply asks operator to type when transcription is empty. |
| `ideas` table has no MCP tool yet | Low | Plan Q3 fallback: route `/idea` to `save_lesson(category='PLAN', tags=['idea','telegram-capture'])`. |
| Background idle-session task races on shutdown | Low | Use `asyncio.create_task` with cancellation + drain on bot stop. |
| systemd unit can't see env vars | Low | `EnvironmentFile=/home/pretel/.env.pretel_os` per existing pattern from MCP server unit. |

---

## 12. Doc registry

This file lands in `docs/PROJECT_FOUNDATION.md §6 Doc registry` when
Module 5 closes.

**End of plan.md.**
