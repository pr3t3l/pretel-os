# specs/telegram_bot/tasks.md

**Module:** Module 5 — telegram_bot
**Status:** Draft (M5.T1.3)
**Last updated:** 2026-04-29
**Authority:** `specs/telegram_bot/spec.md`, `specs/telegram_bot/plan.md`, `CONSTITUTION.md §6 rule 31`.

> **Task gate (§6 rule 31):** every unchecked `[ ]` is completable in under 30 minutes by an operator with the spec + plan loaded. If a task balloons past 30 min, stop, split, revisit.

---

## 0. How to read this file

Per `runbooks/sdd_module_kickoff.md` §The rule item 5: atomic IDs are
`M5.<phase>.<n>.<sub>`. Root `tasks.md` carries milestone-level rows
only (M5.T1, M5.T2, ...). The first unchecked `[ ]` below is the
active task.

---

## M5.T1 — SDD trinity

- [x] **M5.T1.1** Author `specs/telegram_bot/spec.md`. Includes scope
  in/out, public interface (commands + new MCP tools), data contracts,
  failure modes, success criteria.
- [x] **M5.T1.2** Author `specs/telegram_bot/plan.md`. 6 phases (A–E
  + Phase F deferred), Q1–Q6 architectural decisions, exit gate.
- [x] **M5.T1.3** Author `specs/telegram_bot/tasks.md` (this file).
- [x] **M5.T1.4** Add Module 5 milestone section to root `tasks.md`
  per `runbooks/sdd_module_kickoff.md`.

---

## M5.T2 — Phase A — Review MCP tools

### A.1 — SDD trinity

Covered by M5.T1 above.

### A.2 — `list_pending_lessons` tool

- [x] **M5.A.2.1** Add `list_pending_lessons(bucket: str | None = None,
  limit: int = 10) -> dict` to `src/mcp_server/tools/lessons.py`.
  - SQL: `SELECT id, title, content, bucket, category, tags, created_at
    FROM lessons WHERE status='pending_review' AND deleted_at IS NULL
    [AND bucket=$1] ORDER BY created_at ASC LIMIT $N`.
  - Clamps: `1 <= limit <= 50`.
  - Returns `{status:'ok', results:[{id, title, content, bucket,
    category, tags, created_at}, ...]}`.
  - Degraded: `db_unavailable` payload when `db_mod.is_healthy()` is
    False.
  - Done when: function importable; calling it on a seeded test DB
    returns the seeded pending row(s).

### A.3 — `approve_lesson` tool

- [x] **M5.A.3.1** Add `approve_lesson(id: str) -> dict` to lessons.py.
  - SQL: `UPDATE lessons SET status='active', reviewed_at=now(),
    reviewed_by='operator' WHERE id=%s AND status='pending_review'
    RETURNING id`.
  - Returns `{status:'ok', approved: True}` on row update;
    `{status:'ok', approved: False}` if 0 rows (not found or already
    processed).
  - Done when: pending lesson → `approve_lesson(id)` → `search_lessons`
    finds it as active.

### A.4 — `reject_lesson` tool

- [x] **M5.A.4.1** Add `reject_lesson(id: str, reason: str) -> dict`
  to lessons.py.
  - Validate: `reason` non-empty string after strip.
  - SQL: `UPDATE lessons SET status='rejected', reviewed_at=now(),
    reviewed_by='operator', metadata=metadata ||
    jsonb_build_object('reject_reason', %s::text) WHERE id=%s AND
    status='pending_review' RETURNING id`.
  - Returns `{status:'ok', rejected: True}` / `{status:'ok',
    rejected: False}`.
  - Done when: pending lesson → reject → `search_lessons(...,
    include_archived=False)` excludes it.

### A.5 — `cross_pollination` tools file

- [x] **M5.A.5.1** Create `src/mcp_server/tools/cross_pollination.py`
  with `list_pending_cross_pollination(limit: int = 10) -> dict`.
  - SQL: `SELECT id, origin_bucket, origin_project, target_bucket, idea,
    reasoning, suggested_application, priority, confidence_score,
    impact_score, created_at FROM cross_pollination_queue WHERE
    status='pending' ORDER BY COALESCE(priority, 99) ASC, created_at
    ASC LIMIT $1`.
  - Clamps: `1 <= limit <= 50`.
  - Done when: function importable; returns seeded pending rows.

- [x] **M5.A.5.2** Add `resolve_cross_pollination(id: str, action: str,
  note: str | None = None) -> dict` to the same file.
  - Validate: `action ∈ {'approve','reject'}` (return error otherwise).
  - Map: `'approve' → 'applied'`, `'reject' → 'dismissed'`.
  - SQL: `UPDATE cross_pollination_queue SET status=%s::cross_poll_status,
    resolved_at=now(), reviewed_at=COALESCE(reviewed_at, now()),
    resolution_note=%s WHERE id=%s AND status IN ('pending',
    'under_review') RETURNING id, status`.
  - Returns `{status:'ok', resolved: True, new_status: '<applied|dismissed>'}`
    on update; `{status:'ok', resolved: False}` if 0 rows.
  - Done when: synthetic pending row → resolve(approve) → status='applied'
    + resolved_at populated.

### A.6 — Tool registration + tests

- [x] **M5.A.6.1** Register all 5 tools in `src/mcp_server/main.py`:
  `app.tool(list_pending_lessons)`, `app.tool(approve_lesson)`,
  `app.tool(reject_lesson)`, `app.tool(list_pending_cross_pollination)`,
  `app.tool(resolve_cross_pollination)`.
  - Done when: `python -c "from mcp_server.main import build_app;
    build_app()"` runs cleanly.

- [x] **M5.A.6.2** Write `tests/mcp_server/tools/test_review_tools.py` with 13 (≥8 required)
  `@pytest.mark.slow` tests against `pretel_os_test`:
  1. `test_list_pending_lessons_returns_pending` — seed 2 pending +
     1 active → list returns 2.
  2. `test_list_pending_lessons_bucket_filter` — seed in 2 buckets,
     filter by one returns only that bucket.
  3. `test_list_pending_lessons_limit_clamped` — limit=100 → at most
     50 returned.
  4. `test_approve_lesson_happy_path` — pending → approve → status
     active + reviewed_at populated.
  5. `test_approve_lesson_already_active_noop` — active row → approve
     → `approved: False`.
  6. `test_reject_lesson_writes_reason` — pending → reject(reason) →
     status rejected + metadata.reject_reason.
  7. `test_list_pending_cross_pollination_orders_by_priority` — seed 3
     rows with different priorities → returned ordered.
  8. `test_resolve_cross_pollination_approve_maps_to_applied` —
     pending row → resolve(approve) → status applied.
  9. `test_resolve_cross_pollination_invalid_action_errors` —
     `action='maybe'` → `{status:'error', ...}`.
  - Done when: `pytest tests/tools/test_review_tools.py -v` passes.

- [x] **M5.A.6.3** mypy clean across `tools/lessons.py`,
  `tools/cross_pollination.py`, `main.py`.
  - Done when: `mypy src/mcp_server/tools/lessons.py
    src/mcp_server/tools/cross_pollination.py src/mcp_server/main.py`
    returns Success.

---

## M5.T3 — Phase B — Bot skeleton + core commands

- [x] **M5.B.1.1** Create `src/telegram_bot/__init__.py`,
  `src/telegram_bot/__main__.py`, `src/telegram_bot/bot.py`,
  `src/telegram_bot/config.py`, `src/telegram_bot/handlers/__init__.py`.

- [x] **M5.B.1.2** ApplicationBuilder + long-poll entry point.
  `python -m telegram_bot` starts the bot. (`build_application(cfg)`
  is a pure factory; `main()` reads env via `load_config()` then
  `app.run_polling(...)`.)

- [x] **M5.B.2.1** Operator-only guard middleware in
  `handlers/_guard.py`. Decorator `operator_only` rejects any chat_id
  ≠ `TELEGRAM_OPERATOR_CHAT_ID` with "🔒 This is a private bot.
  Access denied." reply + WARNING log.

- [x] **M5.B.3.1** `/start` and `/help` handlers in `handlers/help.py`
  — `help_command = start_command` (alias). Operator-guarded; sends
  `WELCOME_MESSAGE` listing all 7 commands.

- [x] **M5.B.4.1** `/save <text>` handler in `handlers/save.py`. Two-step
  flow: command stashes text in `context.user_data`, inline keyboard
  prompts for bucket; `CallbackQueryHandler(pattern=r'^save:')` calls
  `save_lesson(category='OPS', tags=['telegram-capture'])` and reports
  saved/auto-approved/merge_candidate/degraded back to the operator.

- [x] **M5.B.5.1** `/idea <text>` handler in `handlers/idea.py`. Same
  two-step pattern as `/save`. Q3 fallback: routes to `save_lesson`
  with `category='PLAN'` and `tags=['idea','telegram-capture']` since
  no dedicated `ideas` MCP tool exists today.

- [x] **M5.B.6.1** `/status` handler in `handlers/status.py`. Parallel
  `asyncio.gather` of 4 checks (MCP `/health`, Postgres `SELECT 1`,
  LiteLLM `/health`, n8n `/healthz`); per-check 5s timeout. Reply is
  color-coded (🟢 all healthy / 🟡 partial / 🔴 all down) with a
  per-row marker + detail + latency_ms. Endpoint URLs are env-
  overridable (`MCP_HEALTH_URL`, `LITELLM_HEALTH_URL`, `N8N_HEALTH_URL`).

- [x] **M5.B.7.1** `infra/systemd/pretel-os-bot.service` shipped.
  Mirrors the existing `pretel-os-mcp.service` pattern
  (`/home/pretel/.venvs/pretel-os/bin/python`, `EnvironmentFile`,
  `Type=simple`, `Restart=on-failure`). Adds
  `pretel-os-mcp.service` to `After=` to ensure ordering.

- [x] **M5.B.8.1** `tests/telegram_bot/test_handlers.py` — 10 tests
  (start welcome, /help alias, unauthorized rejection, /save without
  text, /save stashes + keyboard, /save callback invokes save_lesson,
  /save callback without pending warns, /idea callback uses PLAN
  category + idea tag, /status full-healthy summary, _format_status
  partial-mode rendering). All pure mocks — no live Telegram, no live
  DB. mypy clean. 10/10 pass in 0.65s.

---

## M5.T4 — Phase C — Review flows

- [x] **M5.C.1.1** `/review_pending` flow in `handlers/review.py`.
  Walks pending lessons one-by-one with [✅ Aprobar][❌ Rechazar]
  [⏭ Saltar] inline buttons. Approve / skip cycle directly to the
  next item via `_send_next_or_empty`; reject stashes
  `awaiting_reason_for=<id>` in `user_data["review_state"]` and the
  next plain-text message becomes the reason (handled by the
  `MessageHandler(filters.TEXT & ~filters.COMMAND, ...)` registered
  in `bot.py`). Empty queue → "No hay lecciones pendientes 🎉".
  Note: chose simple `user_data` state over `ConversationHandler`
  per plan §11 risk register guidance — handler stayed under 200 LoC
  and is trivially mock-testable.

- [x] **M5.C.2.1** `/cross_poll_review` flow in `handlers/cross_poll.py`.
  Walks `cross_pollination_queue` rows with [✅ Aprobar][❌ Rechazar]
  inline buttons (no reason prompt — Phase C scope). Approve →
  `resolve_cross_pollination(id, 'approve')` → status `applied`;
  reject → `resolve_cross_pollination(id, 'reject')` → status
  `dismissed`. Empty queue → "No hay propuestas pendientes 🎉".

- [x] **M5.C.3.1** `tests/telegram_bot/test_review_flows.py` — 11
  pure-mock tests (≥4 required). Coverage: review empty queue +
  first-card render + approve path + reject-prompt path + reason-
  message path + plain-text-without-state no-op + skip path; cross-
  poll empty queue + first-proposal render + approve path + reject
  path. All 11 + 10 prior Phase B tests pass in 0.88s. mypy clean.

---

## M5.T5 — Phase D — Voice + session tracking

- [x] **M5.D.1.1** Voice handler in `handlers/voice.py`. Downloads
  the `.ogg` via `voice.get_file().download_as_bytearray()`, posts
  to Whisper (`model='whisper-1'`, `language='es'`,
  `response_format='text'`) via `AsyncOpenAI`, defensively strips the
  result, stashes in `user_data["voice_pending_text"]`, prompts for
  bucket. Bucket callback calls `save_lesson(category='OPS',
  tags=['voice-capture','telegram'])`. Failures (download error,
  Whisper error, empty transcription) degrade to "Envía /save
  <texto>" fallback so the operator's flow is never blocked.

- [ ] **M5.D.2.1** Session tracker: INSERT first message; UPDATE
  per turn; append JSONL transcript at
  `~/pretel-os-data/transcripts/{session_id}.jsonl`.

- [ ] **M5.D.2.2** Background idle-close task (asyncio loop, every
  5 min): close sessions with `last_seen_at < now() - 10 min`,
  `close_reason='idle_10min'`.

- [ ] **M5.D.3.1** Tests: ≥4 (mock Whisper for voice; real DB for
  session).

---

## M5.T6 — Phase E — Module 5 gate + cleanup

- [ ] **M5.E.1.1** Verify the 3 spec §7 success-criteria bullets via
  live operator demo.

- [ ] **M5.E.2.1** Mark all M5.A–M5.D atomic checkboxes `[x]` with
  commit hashes.

- [ ] **M5.E.3.1** Update root `tasks.md` — flip M5.T2…M5.T6 milestones
  to `[x]`.

- [ ] **M5.E.4.1** Update `SESSION_RESTORE.md` §2 (phase line + What
  is done + Top of stack + Where to find sources) and §13 (new
  last-session block).

- [ ] **M5.E.4.2** Update `tasks.archive.md` — append Module 5 closure
  summary in the same shape as Module 4 / Module 0.X Phase A.

- [ ] **M5.E.4.3** Update `docs/PROJECT_FOUNDATION.md` — flip
  `specs/telegram_bot/` registry row from `Pending` → `Active —
  Module 5 complete YYYY-MM-DD`.

- [ ] **M5.E.5.1** Tag candidate `module-5-complete` (operator-driven,
  not auto-pushed).

---

## M5.T9 — Open questions deferred

| # | Question | Resolution criterion |
|---|---|---|
| 1 | Webhook migration vs long polling | Phase F; only if Telegram-side reliability surfaces in `usage_logs` |
| 2 | Voice language auto-detect (vs `language=es` hardcode) | Phase F; only if operator regularly sends English voice |
| 3 | Group chat support | Out of scope for v1; future module if reflection-worker outputs warrant operator-team reviews |

---

**End of tasks.md.**
