# Module 0.X — Knowledge Architecture — Tasks

**Status:** DRAFT
**Created:** 2026-04-28
**Spec:** `spec.md` | **Plan:** `plan.md`

Each task is atomic — completable in one focused work session. Format: `[ ] M0X.{phase}.{n} — short imperative`. Sub-tasks indented with two spaces.

---

## Pre-flight

- [ ] M0X.PRE.1 — Verify branch `main` is at commit with M0X.T1 + M0X.T2 (run `git log --oneline -3`)
- [ ] M0X.PRE.2 — Verify Postgres healthy: `psql -h localhost -U pretel_os -d pretel_os -c "\dt" | wc -l` returns >= 16 (Phase 1 + base Phase 2 tables present)
- [ ] M0X.PRE.3 — Verify pgvector extension: `psql -c "\dx" | grep vector` shows installed
- [ ] M0X.PRE.4 — Confirm `OPENAI_API_KEY` in `~/.env.litellm` for embedding generation in Phase C
- [ ] M0X.PRE.5 — Confirm scratch test DB available: `psql -c "CREATE DATABASE pretel_os_scratch"` (drop after Phase A)

---

## Phase A — Schema migrations

### Migration 0024 — tasks table

- [x] M0X.A.1.1 — Create `migrations/0024_tasks.sql` with table DDL per spec §5.1
- [x] M0X.A.1.2 — Add 3 indexes: `idx_tasks_bucket_status`, `idx_tasks_open_by_phase`, `idx_tasks_module`
- [x] M0X.A.1.3 — Add CHECK constraints on status and priority enums
- [x] M0X.A.1.4 — Add self-referential FK `blocked_by REFERENCES tasks(id) ON DELETE SET NULL`
- [x] M0X.A.1.5 — Wrap in `BEGIN ... COMMIT` transaction with `IF NOT EXISTS` guards
- [x] M0X.A.1.6 — Apply on scratch DB, verify with `\d+ tasks` matches spec
- [x] M0X.A.1.7 — Insert into `schema_migrations` on success

### Migration 0025 — operator_preferences table

- [x] M0X.A.2.1 — Create `migrations/0025_operator_preferences.sql` per spec §5.3
- [x] M0X.A.2.2 — Add UNIQUE constraint on (category, key, scope)
- [x] M0X.A.2.3 — Add 2 partial indexes: `idx_preferences_scope_active`, `idx_preferences_category_active`
- [x] M0X.A.2.4 — Add CHECK on category enum (6 values)
- [x] M0X.A.2.5 — Apply on scratch DB, verify with `\d+ operator_preferences`

### Migration 0026 — router_feedback table

- [x] M0X.A.3.1 — Create `migrations/0026_router_feedback.sql` per spec §5.4
- [x] M0X.A.3.2 — Add FK `request_id REFERENCES routing_logs(request_id) ON DELETE SET NULL`
- [x] M0X.A.3.3 — Verify FK works against partitioned parent table on PG16 (not just a partition)
- [x] M0X.A.3.4 — Add 3 indexes: `idx_router_feedback_status`, `idx_router_feedback_request`, `idx_router_feedback_type` (partial)
- [x] M0X.A.3.5 — Add CHECK on feedback_type (6 values) and status (4 values)
- [x] M0X.A.3.6 — Apply on scratch DB, verify

### Migration 0027 — best_practices table

- [x] M0X.A.4.1 — Create `migrations/0027_best_practices.sql` per spec §5.5
- [x] M0X.A.4.2 — Include `previous_guidance` and `previous_rationale` columns for rollback
- [x] M0X.A.4.3 — Include `superseded_by uuid REFERENCES best_practices(id)` self-ref FK
- [x] M0X.A.4.4 — Include `derived_from_lessons uuid[] DEFAULT '{}'`
- [x] M0X.A.4.5 — SKIP HNSW index per ADR-024 (DECISIONS.md). Add commented-out CREATE INDEX with rationale.
- [x] M0X.A.4.6 — Add 5 more indexes per spec §5.5
- [x] M0X.A.4.7 — Add CHECK on domain (4 values) and source (3 values)
- [x] M0X.A.4.8 — Apply on scratch DB, verify with `\d+ best_practices`

### Migration 0028 — decisions amendment

- [x] M0X.A.5.1 — Create `migrations/0028_decisions_amendment.sql` per spec §5.2
- [x] M0X.A.5.2 — Add columns: scope, applicable_buckets, decided_by, tags, severity, adr_number, derived_from_lessons
- [x] M0X.A.5.3 — Add CHECK on scope enum (4 values)
- [x] M0X.A.5.4 — Add UNIQUE on adr_number (allows NULL for non-formal decisions)
- [x] M0X.A.5.5 — Add 3 indexes: `idx_decisions_scope_status`, `idx_decisions_applicable_buckets` (GIN), `idx_decisions_tags` (GIN)
- [x] M0X.A.5.6 — Apply on scratch DB, verify column additions with `\d+ decisions`
- [x] M0X.A.5.7 — Verify existing `decisions` rows still query cleanly (defaults applied correctly)

### Migration 0029 — data migration (lessons split)

- [x] M0X.A.6.1 — Create `migrations/0029_data_migration_lessons_split.sql`
- [x] M0X.A.6.2 — Insert ADR-021 into decisions: "Split lessons into typed stores"
- [x] M0X.A.6.3 — Insert ADR-022 into decisions: "SOUL.md voice file"
- [x] M0X.A.6.4 — Insert ADR-023 into decisions: "best_practices as new table (not extension of patterns)"
- [x] M0X.A.6.5 — Migrate `c40e09fc` (verbal acknowledgment anti-pattern) → decisions with scope='process'
- [x] M0X.A.6.6 — Migrate `d7f1e119` (LiteLLM concrete model) → tasks with module='M4', trigger_phase='Phase D'
- [x] M0X.A.6.7 — Migrate `89c11602` (pyproject.toml) → tasks with module='M0.X', trigger_phase='before Module 5'
- [x] M0X.A.6.8 — Migrate `3d98464b` (prompt caching) → tasks with module='M4', trigger_phase='Phase F'
- [x] M0X.A.6.9 — Mark all 4 source `lessons` rows: `status='superseded'`, metadata.superseded_to=<new_uuid>
- [x] M0X.A.6.10 — Migration is idempotent: re-running is no-op (gate on source row status)
- [x] M0X.A.6.11 — Apply on scratch DB, verify all 4 rows landed in correct tables, originals marked superseded

### Phase A close-out

- [x] M0X.A.7.1 — Apply migrations 0024–0029 in order on production DB
- [x] M0X.A.7.2 — Run post-migration assertion script: row counts, indexes present, ADRs visible, supersession metadata correct
- [x] M0X.A.7.3 — Capture `\d+` output for each new/amended table to `migrations/0029_post_state.txt` for audit
- [x] M0X.A.7.4 — Drop scratch DB
- [x] M0X.A.7.5 — Commit migrations + assertion script with message "M0X.A: schema migrations 0024-0029 applied"
- [x] M0X.A.7.6 — **Gate A passed**: schema verified, ADRs present, 4 rows migrated

---

## Phase B — SOUL.md

- [ ] M0X.B.1 — Draft `SOUL.md` content covering: communication style, language preference, tooling preferences, deferral discipline, opinion-required convention
- [ ] M0X.B.2 — Measure token count with `python -c "import tiktoken; enc=tiktoken.get_encoding('cl100k_base'); print(len(enc.encode(open('SOUL.md').read())))"`
- [ ] M0X.B.3 — Measure combined L0 token count: CONSTITUTION + IDENTITY + AGENTS + SOUL — must be under 1,200
- [ ] M0X.B.4 — If over budget, trim IDENTITY.md or SOUL.md (do NOT trim CONSTITUTION); re-measure
- [ ] M0X.B.5 — Run pre-commit token-budget hook manually: `infra/hooks/pre-commit-token-budget.sh`
- [ ] M0X.B.6 — Update AGENTS.md to add SOUL.md to the L0 read-order list
- [ ] M0X.B.7 — Commit with message "M0X.B: SOUL.md added to L0, AGENTS.md updated"
- [ ] M0X.B.8 — **Gate B passed**: file exists, L0 budget respected, hook clean

---

## Phase C — MCP tools

### C.1 — Tasks tools (5)

- [ ] M0X.C.1.1 — Create `src/mcp_server/tools/tasks.py` skeleton with imports and FastMCP decorator setup
- [ ] M0X.C.1.2 — Implement `task_create(title, bucket, description?, project?, module?, priority?, trigger_phase?, source, estimated_minutes?)` — returns `{id, status}` or degraded
- [ ] M0X.C.1.3 — Implement `task_list(bucket?, status?, module?, limit?)` — returns ordered list
- [ ] M0X.C.1.4 — Implement `task_update(id, ...fields)` — partial update with `updated_at` refresh
- [ ] M0X.C.1.5 — Implement `task_close(id, completion_note?)` — sets status='done', done_at=now()
- [ ] M0X.C.1.6 — Implement `task_reopen(id, reason)` — sets status='open', clears done_at, appends to metadata.reopened_history
- [ ] M0X.C.1.7 — Add degraded-mode wrapper to all 5 tools (CONSTITUTION §8.43(b))
- [ ] M0X.C.1.8 — Register all 5 in MCP server entrypoint

### C.2 — Decisions tools (3)

- [ ] M0X.C.2.1 — Create `src/mcp_server/tools/decisions.py`
- [ ] M0X.C.2.2 — Implement `decision_record(bucket, project, title, context, decision, consequences, scope, applicable_buckets?, decided_by, severity?, adr_number?, derived_from_lessons?, tags?, alternatives?)` — generates embedding, returns `{id, adr_number}`
- [ ] M0X.C.2.3 — Implement `decision_search(query, bucket?, scope?, status?, top_k=5)` — semantic search via sequential scan with `ORDER BY embedding <=> query_embedding LIMIT top_k` (HNSW deferred per ADR-024) + scalar filters
- [ ] M0X.C.2.4 — Implement `decision_supersede(old_id, new_decision_payload)` — atomically marks old superseded, inserts new with link
- [ ] M0X.C.2.5 — Add degraded-mode wrapper
- [ ] M0X.C.2.6 — Register in MCP server

### C.3 — Preferences tools (4)

- [ ] M0X.C.3.1 — Create `src/mcp_server/tools/preferences.py`
- [ ] M0X.C.3.2 — Implement `preference_set(category, key, value, scope='global')` — UPSERT via `ON CONFLICT (category, key, scope) DO UPDATE`
- [ ] M0X.C.3.3 — Implement `preference_get(category, key, scope='global')` — direct lookup, returns value or null
- [ ] M0X.C.3.4 — Implement `preference_list(category?, scope?, active=true)` — filter list
- [ ] M0X.C.3.5 — Implement `preference_unset(category, key, scope)` — sets active=false (soft delete)
- [ ] M0X.C.3.6 — Add degraded-mode wrapper
- [ ] M0X.C.3.7 — Register in MCP server

### C.4 — Router feedback tools (2)

- [ ] M0X.C.4.1 — Create `src/mcp_server/tools/router_feedback.py`
- [ ] M0X.C.4.2 — Implement `router_feedback_record(request_id?, feedback_type, operator_note?, proposed_correction?)` — inserts pending row
- [ ] M0X.C.4.3 — Implement `router_feedback_review(id, status, reviewed_by)` — transitions pending→reviewed/applied/dismissed
- [ ] M0X.C.4.4 — Add degraded-mode wrapper
- [ ] M0X.C.4.5 — Register in MCP server

### C.5 — Best practices tools (3)

- [ ] M0X.C.5.1 — Create `src/mcp_server/tools/best_practices.py`
- [ ] M0X.C.5.2 — Implement `best_practice_record(title, guidance, domain, scope='global', rationale?, applicable_buckets?, tags?, source='operator', derived_from_lessons?)`
  - [ ] M0X.C.5.2a — On UPDATE path: copy current `guidance`/`rationale` into `previous_guidance`/`previous_rationale` BEFORE overwrite (single-step rollback)
  - [ ] M0X.C.5.2b — On INSERT and UPDATE: generate embedding via OpenAI text-embedding-3-large; on API failure, queue to `pending_embeddings` and write row without embedding
- [ ] M0X.C.5.3 — Implement `best_practice_search(query, scope?, domain?, top_k=5)` — sequential-scan vector similarity with `ORDER BY embedding <=> query_embedding LIMIT top_k` (HNSW deferred per ADR-024) + scalar filters
- [ ] M0X.C.5.4 — Implement `best_practice_deactivate(id, reason)` — sets active=false, records reason in metadata
- [ ] M0X.C.5.5 — Implement `best_practice_rollback(id)` — restores previous_guidance → guidance, previous_rationale → rationale; returns error if previous_* are NULL
- [ ] M0X.C.5.6 — Add degraded-mode wrapper to all
- [ ] M0X.C.5.7 — Register in MCP server

### Phase C close-out

- [ ] M0X.C.6.1 — Run `mypy --strict src/mcp_server/tools/` — must be clean
- [ ] M0X.C.6.2 — Restart MCP server: `systemctl --user restart pretel-os-mcp`
- [ ] M0X.C.6.3 — Verify all 17 tools registered: query `tools_catalog` for new tool names
- [ ] M0X.C.6.4 — Smoke-test each tool via Claude.ai connector or `claude` CLI: one minimal call per tool returning success
- [ ] M0X.C.6.5 — Verify no hardcoded model strings in any new file: `grep -rn "claude-\|gpt-\|gemini-" src/mcp_server/tools/` returns nothing (LiteLLM aliases only — but no chat completions in M0.X tools, so should be empty regardless)
- [ ] M0X.C.6.6 — Test degraded mode: stop Postgres, call one tool per file, verify returns `{status:'degraded', journal_id:...}` and journal file written
- [ ] M0X.C.6.7 — Restart Postgres, run journal_replay worker, verify rows landed
- [ ] M0X.C.6.8 — Commit with message "M0X.C: 17 MCP tools implemented and registered"
- [ ] M0X.C.6.9 — **Gate C passed**: tools registered, mypy clean, degraded mode verified

---

## Phase D — Tests

### D.1 — Unit tests per tool file

- [ ] M0X.D.1.1 — `tests/mcp_server/tools/test_tasks.py` — 5 tests, one per tool, happy path + error cases
- [ ] M0X.D.1.2 — `tests/mcp_server/tools/test_decisions.py` — 3 tests; `test_decision_supersede` asserts atomicity
- [ ] M0X.D.1.3 — `tests/mcp_server/tools/test_preferences.py` — 4 tests; `test_preference_set_upsert` asserts UPSERT behavior
- [ ] M0X.D.1.4 — `tests/mcp_server/tools/test_router_feedback.py` — 2 tests
- [ ] M0X.D.1.5 — `tests/mcp_server/tools/test_best_practices.py` — 4 tests, including:
  - [ ] M0X.D.1.5a — `test_best_practice_rollback_round_trip`: record → update → assert previous_* populated → rollback → assert content restored
  - [ ] M0X.D.1.5b — `test_best_practice_supersede`: record A → record B with superseded_by=A.id → query A returns superseded chain

### D.2 — Integration tests (LL-M4-PHASE-A-001 mandate)

- [ ] M0X.D.2.1 — `tests/mcp_server/integration/test_m0x_full_flow.py` — boots full MCP server, registers tools, calls each through MCP protocol
- [ ] M0X.D.2.2 — Each integration test asserts CONTENT of returned payload (not just shape) — includes embedding dimensionality for best_practices
- [ ] M0X.D.2.3 — Test degraded mode end-to-end: integration test stops DB, calls tool, asserts journal file content matches intended write

### D.3 — Migration tests

- [ ] M0X.D.3.1 — `tests/migrations/test_0029_lessons_split.py` — runs migration on scratch, asserts 4 rows in correct destinations + originals superseded
- [ ] M0X.D.3.2 — Re-run test: assert idempotency (second run is no-op)

### Phase D close-out

- [ ] M0X.D.4.1 — Run `pytest tests/mcp_server/tools/ tests/mcp_server/integration/ tests/migrations/` — all green
- [ ] M0X.D.4.2 — Run `pytest --cov=src/mcp_server/tools` — coverage >= 80% on new files
- [ ] M0X.D.4.3 — Commit with message "M0X.D: unit + integration tests, coverage >= 80%"
- [ ] M0X.D.4.4 — **Gate D passed**: all tests green, coverage threshold met

---

## Phase E — Layer loader contract + docs

- [ ] M0X.E.1 — Create `specs/module-0x-knowledge-architecture/layer_loader_contract.md` — frozen mapping per spec §8 (L0–L4 sources and filters)
- [ ] M0X.E.2 — Update `docs/DATA_MODEL.md`:
  - [ ] M0X.E.2.1 — Add §5.7 `tasks` schema documentation
  - [ ] M0X.E.2.2 — Add §5.8 `operator_preferences` schema documentation
  - [ ] M0X.E.2.3 — Add §5.9 `router_feedback` schema documentation
  - [ ] M0X.E.2.4 — Add §5.10 `best_practices` schema documentation
  - [ ] M0X.E.2.5 — Amend §5.2 `decisions` to reflect 7 new columns
  - [ ] M0X.E.2.6 — Update §1.2 table count: 21 → 25 tables
- [ ] M0X.E.3 — Update `docs/INTEGRATIONS.md` MCP tool catalog: add 17 new tool entries
- [ ] M0X.E.4 — Update `SESSION_RESTORE.md` §13: new last-known state snapshot with module-0x-complete
- [ ] M0X.E.5 — Update `plan.md §6` Module 0.X entry: status "in progress" → "complete"
- [ ] M0X.E.6 — Update top-level `tasks.md`: mark M0X.T1, T2, T3, T4 closed
- [ ] M0X.E.7 — Verify spec.md §6 says "17 tools" not "16" (side-fix from plan.md)
- [ ] M0X.E.8 — Commit with message "M0X.E: layer_loader_contract.md frozen, DATA_MODEL/INTEGRATIONS updated"
- [ ] M0X.E.9 — Tag: `git tag module-0x-complete -m "Module 0.X: knowledge architecture complete"`
- [ ] M0X.E.10 — Push: `git push origin main && git push origin module-0x-complete`
- [ ] M0X.E.11 — **Gate E passed**: contract frozen, docs synced, tag created
- [ ] M0X.E.12 — **Module 0.X COMPLETE** — Module 4 Phase B unblocked

---

## Total task count

- Pre-flight: 5
- Phase A: 7 sub-sections, ~50 atomic tasks
- Phase B: 8 atomic tasks
- Phase C: 5 sub-sections, ~38 atomic tasks
- Phase D: 4 sub-sections, ~12 atomic tasks
- Phase E: 12 atomic tasks
