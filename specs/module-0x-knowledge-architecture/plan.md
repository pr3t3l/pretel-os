# Module 0.X — Knowledge Architecture — Plan

**Status:** DRAFT
**Created:** 2026-04-28
**Spec:** `specs/module-0x-knowledge-architecture/spec.md`
**Position in roadmap:** Inserted between Module 4 Phase A (complete) and Module 4 Phase B (blocked on this module).

---

## 1. Purpose of this plan

The spec defines WHAT Module 0.X delivers. This plan defines HOW it gets built — what order, what gates, what dependencies, and what each phase produces. tasks.md (M0X.T3) will then break each phase into atomic checkbox tasks.

---

## 2. Module state snapshot

**Current state of Module 0.X: COMPLETE (tagged `module-0x-complete`).**

- Spec: COMPLETE (commit `8a6cf7d`)
- Plan: COMPLETE (this document, M0X.T2 — `ff81538`)
- Tasks: COMPLETE (M0X.T3 — `c4b4649`)
- Implementation: COMPLETE (M0X.T4 — Phases A→E shipped; see §3 for per-phase commit chain)

**Repo state at module start:**
- Branch: `main`
- Last commit before M0.X work: `28fec7b` (M4 Phase A complete)
- Existing migrations: 0001–0023 (Phase 1 + Phase 2 base tables, including `patterns` and `decisions` base schemas)
- New migrations added in this module: 0024–0029 (+ 0028a M2 trigger fix). Migration 0030 (notify_missing_embedding trigger for best_practices) deferred to a follow-up; tracked as task `92cac1b3`.

---

## 3. Phase breakdown

Module 0.X ships in 5 phases. Each phase has its own gate. Phases run sequentially — no phase starts until prior phase's gate passes.

### Phase A: Schema migrations

**Deliverable:** SQL migration files + applied DDL + verified schema state.

**Outputs:**
- `migrations/0024_tasks.sql` — creates `tasks` table + 3 indexes
- `migrations/0025_operator_preferences.sql` — creates `operator_preferences` table + 2 indexes + UNIQUE constraint
- `migrations/0026_router_feedback.sql` — creates `router_feedback` table + 3 indexes + FK to `routing_logs`
- `migrations/0027_best_practices.sql` — creates `best_practices` table + 6 indexes
- `migrations/0028_decisions_amendment.sql` — adds 7 columns to existing `decisions` + 3 indexes
- `migrations/0029_data_migration_lessons_split.sql` — moves the 4 misclassified `lessons` rows + writes ADR-021/ADR-022/ADR-023

**Gate A:**
- All 6 migrations apply cleanly on a scratch database (drop + recreate test)
- All 6 migrations apply cleanly on production database
- Post-migration assertions pass: row counts match, indexes exist, ADR rows present in `decisions`
- 4 originally-misclassified `lessons` rows now have `status='superseded'` with metadata pointing to new rows
- `\d+` of every new/amended table matches spec §5

### Phase B: SOUL.md workspace file

**Deliverable:** `SOUL.md` at repo root, committed, with content seeded from operator's stated voice/preferences.

**Outputs:**
- `SOUL.md` (new file)
- ADR-022 already inserted in Phase A migration; this phase just creates the markdown file referenced by it

**Gate B:**
- File `~/dev/pretel-os/SOUL.md` exists
- Content covers: communication style, language preference (Spanish/English), deferral discipline (no verbal acknowledgment), tooling conventions
- `identity.md` token count remains <= 1,200 (per CONSTITUTION §7.36 — unchanged by this phase)
- SOUL.md kept lean by convention (~150-200 tokens; no enforced cap per CONSTITUTION §2.3 spec drift fix)
- `AGENTS.md` updated to reference SOUL.md in the L0 read order

### Phase C: MCP tools — write & register

**Deliverable:** 17 new MCP tools implemented in `src/mcp_server/tools/` and registered with FastMCP.

**Tool inventory (per spec §6):**
- Tasks (5): `task_create`, `task_list`, `task_update`, `task_close`, `task_reopen`
- Decisions (3): `decision_record`, `decision_search`, `decision_supersede`
- Preferences (4): `preference_set`, `preference_get`, `preference_list`, `preference_unset`
- Router feedback (2): `router_feedback_record`, `router_feedback_review`
- Best practices (3): `best_practice_record`, `best_practice_search`, `best_practice_deactivate` — with rollback semantics (copy current → previous_* before overwrite) and embedding generation via OpenAI

**Outputs:**
- `src/mcp_server/tools/tasks.py`
- `src/mcp_server/tools/decisions.py`
- `src/mcp_server/tools/preferences.py`
- `src/mcp_server/tools/router_feedback.py`
- `src/mcp_server/tools/best_practices.py`
- Tools registered in MCP server registry (FastMCP `@mcp.tool()` decorator pattern)
- Each tool inserts a row in `tools_catalog` on first registration
- Embedding generation only for `best_practices` (no other new table has embeddings)
- All tools follow degraded-mode contract per CONSTITUTION §8.43(b) — write to fallback journal when `db_healthy=false`

**Gate C:**
- mypy --strict clean across all new files
- All 17 tools registered in `tools_catalog` and discoverable via `tool_search`
- Each tool callable via MCP protocol (verified by smoke test)
- LiteLLM aliases used for any LLM calls (no hardcoded model strings — CONSTITUTION rule)
- Degraded-mode tested: tools queue to fallback journal when DB stopped

### Phase D: Tests

**Deliverable:** Unit + integration tests covering every tool and migration.

**Outputs:**
- `tests/mcp_server/tools/test_tasks.py`
- `tests/mcp_server/tools/test_decisions.py`
- `tests/mcp_server/tools/test_preferences.py`
- `tests/mcp_server/tools/test_router_feedback.py`
- `tests/mcp_server/tools/test_best_practices.py` — covers rollback semantics + supersession chain
- `tests/migrations/test_0029_lessons_split.py` — verifies 4 misclassified rows moved correctly
- Per LL-M4-PHASE-A-001: each tool has at least one integration test through full MCP server with real DB (not just mocks)

**Gate D:**
- All tests green (`pytest tests/mcp_server/tools/ tests/migrations/`)
- Coverage on new code ≥ 80%
- Integration tests assert content of returned payloads (not just shape) per LL-M4-PHASE-A-001
- Rollback test for `best_practices`: record → update → assert previous_* populated → rollback → assert content restored

### Phase E: Layer loader contract documentation

**Deliverable:** A consumable artifact for Module 4 Phase B planner — what Phase B reads from each table.

**Outputs:**
- `specs/module-0x-knowledge-architecture/layer_loader_contract.md` — frozen mapping per spec §8
- Update to `docs/INTEGRATIONS.md` — add new tables to MCP tool catalog
- Update to `docs/DATA_MODEL.md` — add §5.7 `tasks`, §5.8 `operator_preferences`, §5.9 `router_feedback`, §5.10 `best_practices`, and amend §5.2 `decisions` to reflect new columns
- Update to `SESSION_RESTORE.md` §13 — last-known state snapshot with module 0.X complete tag

**Gate E:**
- Phase B planner can read `layer_loader_contract.md` and write its own spec without questions back to operator
- DATA_MODEL.md is the canonical schema source after this phase (no contradictions with migration files)

---

## 4. Phase dependency graph

```
Phase A (schema)
    │
    ├──> Phase B (SOUL.md)         — independent, can run in parallel after A
    │
    └──> Phase C (tools)
              │
              └──> Phase D (tests)
                        │
                        └──> Phase E (docs / contract)
                                  │
                                  └──> module-0x-complete tag
                                            │
                                            └──> unblocks M4 Phase B
```

Phase B can run in parallel with C if convenient, but B's gate must close before module completion. C must close before D (can't test what doesn't exist). D before E (don't write the consumable contract until tests prove it works).

---

## 5. Cross-module concerns

### 5.1 LiteLLM proxy usage

`best_practice_record` generates embeddings via OpenAI directly (per existing pattern in `lessons` and `patterns`). It does NOT route embeddings through LiteLLM. Reason: embeddings are a single-vendor concern (OpenAI text-embedding-3-large), and LiteLLM proxy is for completion/chat models per ADR-020.

If at any point a tool in this module needs a chat completion (e.g., a future LLM-assisted decision summarization), it MUST go through `classifier_default` or `second_opinion_default` LiteLLM aliases — never hardcoded model strings. This is a CONSTITUTION rule, not a preference.

### 5.2 Degraded mode

Every new tool must respect CONSTITUTION §8.43(b): when `db_healthy=false`, persist intended write to `/home/operator/pretel-os-data/fallback-journal/YYYYMMDD.jsonl` and return `{status: 'degraded', journal_id: ...}`. Existing journal_replay worker handles recovery.

`best_practice_record` with embedding generation has an additional failure mode: OpenAI embeddings API unreachable. Per existing pattern, the row is written without embedding and queued in `pending_embeddings`. The Auto-index worker (Module 6) flushes the queue.

### 5.3 Routing log FK

`router_feedback.request_id` references `routing_logs.request_id`. Because `routing_logs` is monthly-partitioned, the FK must reference the partitioned parent table, not a partition. Phase A migration must verify this works in Postgres 16 (it does — partitioned FK references are supported since PG12).

### 5.4 Scout safety

None of the new tables have direct Scout exposure (no `bucket='scout'` content is gated differently from other buckets). Existing `scout_safety_check` trigger on `lessons` does not need to be replicated on these tables because they don't accept free-form lesson content. `tasks` and `decisions` MAY have `bucket='scout'` rows; the bucket boundary alone is enforced by RLS-equivalent filtering at retrieval time, not by content scanning.

If a future audit shows operator pasting Scout-identifying detail into a `task.description` or `decision.context`, we add the trigger. Not pre-emptively.

### 5.5 The 4 misclassified lessons

Migration `0029_data_migration_lessons_split.sql` is the data migration. The 4 rows are identified in spec §7:
- `c40e09fc` (anti-pattern: verbal acknowledgment) → `decisions` with scope='process'
- `d7f1e119` (LiteLLM concrete model) → `tasks` with module='M4', trigger_phase='Phase D'
- `89c11602` (pyproject.toml) → `tasks` with module='M0.X', trigger_phase='before Module 5'
- `3d98464b` (prompt caching) → `tasks` with module='M4', trigger_phase='Phase F'

Migration is idempotent (gates on `IF NOT EXISTS` and source row `status != 'superseded'`).

---

## 6. Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Migration fails mid-flight on production | Low | High | Test on scratch DB first (Gate A); each migration is idempotent |
| Embedding generation cost spike on bulk best_practice insert | Low | Low | Phase C tests use ≤10 fixture rows; production seeding is operator-paced |
| FK to partitioned `routing_logs` rejected by PG | Low | Medium | Verified supported PG12+; if fails, falls back to soft reference (uuid only, no FK) |
| Tool count balloons context for `tool_search` results | Low | Low | 17 new tools is incremental; classifier already filters |
| `SOUL.md` pushes L0 over budget | Medium | Low | Pre-commit hook blocks commit; refactor by trimming IDENTITY.md if needed |
| Module 4 Phase B planner reads incomplete `layer_loader_contract.md` | Medium | High | Gate E explicitly requires Phase B planner to consume it without questions back |

---

## 7. Definition of "Module 0.X complete" — ACHIEVED

All 5 gates passed:
- ✅ Gate A: 7 migrations applied (0024–0029 + 0028a M2 trigger fix), schema verified
- ✅ Gate B: SOUL.md exists (324 tok), L0 within budget (per CONSTITUTION §2.3 only `identity.md` has a hard cap)
- ✅ Gate C: 18 tools registered (4 best_practice tools after the rollback split), mypy --strict clean, degraded mode tested
- ✅ Gate D: tests green (47), coverage ≥80% per file, integration tests assert content
- ✅ Gate E: `layer_loader_contract.md` frozen, `DATA_MODEL.md` updated, `SESSION_RESTORE.md` snapshot updated

Closure actions (this Phase E):
- ✅ Tag `module-0x-complete` on the final commit (created locally, push pending operator approval per Gate E protocol)
- ✅ Update `tasks.md` to mark M0X.T1–T4 closed
- ✅ Update plan.md §2 Module 0.X status: "in progress" → "complete"
- ✅ M4 Phase B is now unblocked — `layer_loader_contract.md` is the input contract

---

## 8. Non-goals of this plan

- Building a UI for any of these tools (Telegram + Claude.ai are the surfaces; M0.X is backend-only)
- Reflection worker integration (writes lessons → best_practices) — that's Module 6
- Synchronizing `operator_preferences` with Anthropic userPreferences — deferred per spec §3.2
- Backfilling existing markdown ADRs into `decisions` — manual, via tools, not auto

---

## 9. Cross-references

- Spec: `specs/module-0x-knowledge-architecture/spec.md`
- Constitution: `CONSTITUTION §2.3` (layers), `§2.7` (source priority), `§5.2` (lesson auto-approval — analog needed), `§7.36` (cross-layer sync), `§8.43` (degraded mode)
- Data model: `docs/DATA_MODEL.md §5.1` (patterns — sister table), `§5.2` (decisions — being amended)
- Lessons: `LL-M4-PHASE-A-001` (integration tests), `LL-M4-PHASE-A-002` (verbal acknowledgment), `LL-DATA-001` (single table with status enum — the rule that DOES NOT apply here, per OQ-6 resolution)
- ADR-020 (LiteLLM proxy gateway), ADR-021 (split lessons — this module), ADR-022 (SOUL.md), ADR-023 (best_practices new table — this module)
