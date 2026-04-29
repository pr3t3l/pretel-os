# Module 0.X — Knowledge Architecture (runbook)

**Status:** Phase A + Phase B + Phase C complete. Phases D–E pending.
**Owner:** Alfredo Pretel Vargas
**Created:** 2026-04-28
**Last updated:** 2026-04-28

This runbook captures what Module 0.X did, why it did it, and how to operate the artifacts it produced. It is the operational counterpart to the SDD trinity at `specs/module-0x-knowledge-architecture/{spec,plan,tasks}.md`. Module-wide (single file) per `runbooks/sdd_module_kickoff.md` because M0.X phases are tightly coupled stages of one cohesive buildout, not separate sub-components — schema (Phase A), tools (Phase C), and tests (Phase D) all serve the same operational surface. When Phase D + E close, this file gets the closure summaries appended.

---

## 1. What Module 0.X delivers

Module 0.X splits the single `lessons` table into typed knowledge stores. Each kind of durable knowledge — pending tasks, formal decisions, best-practice guidance, operator preferences, router feedback — has its own table with appropriate lifecycle, schema, and load contract. `lessons` retains its original scope: post-hoc reflection patterns only.

**Phase A (schema, closed 2026-04-28):**
- 4 new tables: `tasks`, `operator_preferences`, `router_feedback`, `best_practices`
- `decisions` table amended with 7 columns (scope, applicable_buckets, decided_by, tags, severity, adr_number, derived_from_lessons)
- 5 ADRs seeded into `decisions` table (020-024, canonical text in `DECISIONS.md`)
- 4 misclassified `lessons` rows archived with cross-table pointers in `metadata`
- `notify_missing_embedding` Module 2 trigger fixed (polymorphic CASE → IF/ELSIF)

**Phase B (SOUL.md, closed 2026-04-28):**
- `SOUL.md` at repo root — operator voice contract loaded into L0
- `AGENTS.md` updated to reference SOUL.md in L0 read order

**Phase C (MCP tools, closed 2026-04-28):**
- 18 MCP tools across 5 files (registered with FastMCP)
- mypy --strict clean on all 5 new files
- Degraded mode verified end-to-end (5 tools → fallback journal)

**Pending (Phase D–E):**
- Phase D — Tests (unit + integration, coverage ≥ 80%)
- Phase E — Docs, layer_loader_contract.md, DATA_MODEL §5.7-5.10 expansion, tag `module-0x-complete`

---

## 2. Architecture overview

```
                   Caller (operator / Claude / agent)
                              │
                              ▼
         ┌──────────────────────────────────────────┐
         │   FastMCP server (pretel-os-mcp)         │
         │   25 tools registered = 7 M3 + 18 M0.X   │
         └──────────────────────────────────────────┘
                              │
       ┌──────────────────────┼─────────────────────────┐
       ▼                      ▼                         ▼
  src/mcp_server/        _common.py:               db.py:
  tools/                 - Timer                   - get_pool()
  ├─ tasks.py            - degraded()              - is_healthy()
  ├─ preferences.py      - log_usage()             - 30s health poller
  ├─ router_feedback.py  - vector_literal()
  ├─ decisions.py
  └─ best_practices.py
       │                      │                         │
       │   Every tool: Timer wrap → is_healthy() guard  │
       │   → on degraded: journal_mod.record() +        │
       │     log_usage(success=False) + return degraded │
       │   → on success: pool.connection() + cur.exec   │
       │     → log_usage(success=True) + return ok      │
       │                                                │
       ▼                                                ▼
  Postgres (production)                       ~/pretel-os-data/
  ├─ tasks                                    fallback-journal/
  ├─ operator_preferences                     YYYYMMDD.jsonl
  ├─ router_feedback                          (mode 0600, idempotency_key
  ├─ best_practices                          + journal_id per row)
  ├─ decisions (amended +7 cols)
  ├─ pending_embeddings                       Replayed by future
  ├─ usage_logs (every tool exit)             auto-index worker (M6)
  └─ lessons (existing, scope tightened)

  Embedding flow (decisions / best_practices):
       │
       ▼
  emb_mod.embed(text)
       │
       ├─ success → vector_literal(emb) → INSERT with embedding
       │
       └─ None    → INSERT with embedding=NULL
                       │
                       ├─ decisions: trigger trg_decisions_emb fires
                       │             → INSERT into pending_embeddings
                       │
                       └─ best_practices: NO trigger (table created
                          post-0019). Tool manually INSERTs into
                          pending_embeddings with ON CONFLICT
                          (commit aba04c7).
```

---

## 3. Files in this component

```
~/dev/pretel-os/

├── DECISIONS.md                                  # canonical ADR log (020-024)
├── SOUL.md                                       # L0 voice file (Phase B)
├── AGENTS.md                                     # updated for SOUL.md (Phase B)
│
├── migrations/
│   ├── 0024_tasks.sql
│   ├── 0025_operator_preferences.sql
│   ├── 0026_router_feedback.sql
│   ├── 0027_best_practices.sql
│   ├── 0028_decisions_amendment.sql
│   ├── 0028a_fix_notify_missing_embedding.sql    # Module 2 regression fix
│   ├── 0029_data_migration_lessons_split.sql
│   └── audit/
│       └── 0029_post_state.md                    # \d+ snapshot pinned to commit
│
├── src/mcp_server/tools/                         # Phase C
│   ├── tasks.py                  (5 tools)
│   ├── preferences.py            (4 tools)
│   ├── router_feedback.py        (2 tools)
│   ├── decisions.py              (3 tools)
│   └── best_practices.py         (4 tools)
│
├── src/mcp_server/main.py                        # build_app() registers all 18
│
├── specs/module-0x-knowledge-architecture/
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md                                  # 141 atomic, M0X.A+B+C [x]
│
└── runbooks/
    └── module_0x_knowledge_architecture.md       # this file
```

---

## 4. Tables — operational reference

### 4.1 `tasks` (migration 0024)

Pending and in-progress work items. Replaces the `save_lesson` + tag `deferred-todo` workaround.

| Column | Notes |
|---|---|
| `bucket`, `project`, `module`, `trigger_phase` | scoping |
| `status` | CHECK: open \| in_progress \| blocked \| done \| cancelled |
| `priority` | CHECK: urgent \| high \| normal \| low |
| `blocked_by` | self-FK (`tasks.id`), `ON DELETE SET NULL` |
| `source` | CHECK: operator \| claude \| reflection_worker \| migration |
| `metadata` | jsonb — completion_note, reopened_history, etc. |

Indexes: `bucket+status` (filter-first), `open_by_phase` (partial), `module` (partial).

**No embedding.** Direct queries only.

Trigger: `trg_set_updated_at_tasks` reuses `set_updated_at()` from migration 0019.

### 4.2 `operator_preferences` (migration 0025)

Operator-controlled facts and overrides (communication style, tooling, language, schedule).

| Column | Notes |
|---|---|
| `category` | CHECK 6: communication \| tooling \| workflow \| identity \| language \| schedule |
| `key`, `value`, `scope` | scope = 'global' \| 'bucket:<name>' \| 'project:<bucket>/<name>' |
| `active` | soft-delete flag |
| `source` | CHECK 3: operator_explicit \| inferred \| migration |

**Constraint:** `UNIQUE(category, key, scope)` enables atomic UPSERT via `ON CONFLICT DO UPDATE`. `preference_set` uses the `xmax = 0` trick to report `action='inserted'` vs `'updated'`.

Soft-delete pattern: set `active=false`, never DELETE. `preference_set` resets `active=true` on conflict so re-setting an unset preference re-activates it.

### 4.3 `router_feedback` (migration 0026)

Explicit feedback signals from operator to Router. Categories: `missing_context`, `wrong_bucket`, `wrong_complexity`, `irrelevant_lessons`, `too_much_context`, `low_quality_response`.

| Column | Notes |
|---|---|
| `request_id` | **`text` (not uuid), no FK** — soft reference to `routing_logs.request_id`. See drift fix #1 below. |
| `feedback_type` | CHECK 6 values |
| `proposed_correction` | jsonb |
| `status` | CHECK 4: pending \| reviewed \| applied \| dismissed |
| `applied_at` | only set when `status='applied'` |

Indexes: `status`, `request_id` (partial WHERE NOT NULL), `feedback_type` (partial WHERE pending).

Workflow: `pending → reviewed | applied | dismissed`. `router_feedback_review` rejects `status='pending'` (you don't review *into* pending).

### 4.4 `best_practices` (migration 0027)

Reusable PROCESS guidance — narrative rules ("always X when Y"). Distinct from `patterns` (DATA_MODEL §5.1) which holds CODE snippets — see ADR-023.

| Column | Notes |
|---|---|
| `title`, `guidance`, `rationale` | guidance is prose, not code |
| `domain` | CHECK 4: process \| convention \| workflow \| communication |
| `scope`, `applicable_buckets`, `tags` | scoping + GIN-indexed |
| `previous_guidance`, `previous_rationale` | single-step rollback target |
| `superseded_by` | self-FK for replacement chain |
| `embedding` | vector(3072) |

**HNSW index DEFERRED per ADR-024.** Sequential scan via `ORDER BY embedding <=> query LIMIT k` is the retrieval path. EXPLAIN confirms Seq Scan; latency 10-50ms at <5K vectors.

Trigger: `trg_set_updated_at_best_practices`. **NO `notify_missing_embedding` trigger** (table created post-0019). On embedding failure, `best_practice_record` manually queues to `pending_embeddings` with `ON CONFLICT (target_table, target_id) DO UPDATE` (commit `aba04c7`). Tracked for trigger-via-migration cleanup as task `92cac1b3`.

### 4.5 `decisions` (migration 0028 — amendment to existing Module 2 table)

7 new columns added: `scope` (CHECK 4: architectural \| process \| product \| operational; DEFAULT `'operational'`), `applicable_buckets text[]`, `decided_by`, `tags text[]`, `severity`, `adr_number integer UNIQUE` (NULL allowed for non-formal), `derived_from_lessons uuid[]`.

3 new indexes: `scope+status`, `applicable_buckets` (GIN), `tags` (GIN).

Backward-compatible: existing rows get `scope='operational'` default applied automatically. UNIQUE on `adr_number` allows multiple NULLs (PostgreSQL semantics).

Trigger: `trg_decisions_emb` (existing from migration 0019, fixed in 0028a) handles `pending_embeddings` queueing automatically when embedding is NULL.

---

## 5. MCP tool inventory (18 tools, Phase C)

| File | Tool | Embedding? | Returns |
|---|---|---|---|
| `tasks.py` | `task_create(title, bucket, source, ...)` | no | `{status:ok, id, status_value}` |
| | `task_list(bucket?, status?, module?, ...)` | no | `{status:ok, results:[...]}` |
| | `task_update(id, **partial_fields)` | no | `{status:ok, id, status_value, found}` |
| | `task_close(id, completion_note?)` | no | `{status:ok, id, found}` |
| | `task_reopen(id, reason)` | no | `{status:ok, id, found}` |
| `preferences.py` | `preference_set(category, key, value, scope?)` | no | `{status:ok, id, action:inserted\|updated}` |
| | `preference_get(category, key, scope?)` | no | `{status:ok, value, active, found}` |
| | `preference_list(category?, scope?, active?)` | no | `{status:ok, results:[...]}` |
| | `preference_unset(category, key, scope?)` | no | `{status:ok, id, found}` |
| `router_feedback.py` | `router_feedback_record(feedback_type, ...)` | no | `{status:ok, id, status_value:pending}` |
| | `router_feedback_review(id, status, reviewed_by)` | no | `{status:ok, id, status_value, found}` |
| `decisions.py` | `decision_record(bucket, project, title, ...)` | yes | `{status:ok, id, adr_number, embedding_queued}` |
| | `decision_search(query, bucket?, scope?, top_k?)` | yes | `{status:ok, results:[...]}` |
| | `decision_supersede(old_id, new_decision_payload)` | yes | `{status:ok, new_id, old_id, embedding_queued}` |
| `best_practices.py` | `best_practice_record(title, guidance, domain, update_id?)` | yes | `{status:ok, id, action, embedding_queued, [rollback_available]}` |
| | `best_practice_search(query, scope?, domain?, bucket?, top_k?)` | yes | `{status:ok, results:[...]}` |
| | `best_practice_deactivate(id, reason)` | no | `{status:ok, id, found}` |
| | `best_practice_rollback(id)` | no (re-embed inline on success) | `{status:ok, id, action:rolled_back}` |

**Total tools registered:** 25 (7 M3 + 18 M0.X). Verify via `app.list_tools()` (Python from inside the venv) — `tools_catalog` is NOT auto-populated by `app.tool()` registration; that table is for the Module 3 `register_tool` MCP tool path.

**Common patterns across all 18:**

- All tools `async def`, return `dict[str, Any]` (mypy --strict requires explicit type parameter)
- Every path calls `log_usage(...)` before returning (success and failure)
- Degraded mode: `if not db_mod.is_healthy()` → `journal_mod.record(operation, payload)` → return `degraded(...)`
- INSERT pure: `assert row is not None` after `cur.fetchone()` (RETURNING always returns on success)
- UPDATE-WHERE: `if row is None: return {status:ok, found:False}` (zero rows is a legitimate not-found case, not an error)

---

## 6. Migrations applied (chronological)

| Migration | Purpose | Commit |
|---|---|---|
| 0024 | tasks table + 3 indexes + updated_at trigger | `db73a67` |
| 0025 | operator_preferences + UNIQUE upsert + 2 partial indexes | `394bf1a` |
| 0026 | router_feedback + soft request_id reference + 3 indexes | `fe923a9` |
| 0027 | best_practices + 6 indexes (no HNSW per ADR-024) + rollback fields | `885adba` |
| 0028a | fix(M2): notify_missing_embedding polymorphic CASE bug | `cb56311` |
| 0028 | decisions amendment (7 columns + 3 indexes) | `acac675` |
| 0029 | data migration: 5 ADRs seeded + 4 lessons split | `40d51cc` |
| audit | Phase A post-migration schema snapshot | `3e55baf` |

All applied to production. Schema audit at `migrations/audit/0029_post_state.md` pinned to its commit hash.

---

## 7. ADRs produced (canonical text in `DECISIONS.md`)

- **ADR-020** — Router classifier and second_opinion route through LiteLLM proxy aliases (architectural, critical)
- **ADR-021** — Split lessons into typed knowledge stores (architectural, critical)
- **ADR-022** — SOUL.md as L0 voice file (architectural, normal)
- **ADR-023** — best_practices is a new table, not extension of patterns (architectural, normal)
- **ADR-024** — HNSW indexes deferred until pgvector ≥ 0.7 or volume justifies (architectural, critical)

ADR-020-024 are also rows in the production `decisions` table (inserted by migration 0029). `DECISIONS.md` is the canonical text source; the table rows are the queryable copy for runtime lookup via `decision_search`.

---

## 8. Operational procedures

All procedures use the Phase C MCP tools — manual SQL is no longer needed. These snippets assume you're in a Python session with `mcp_server` importable (e.g., a smoke script with `sys.path.insert(0, '~/dev/pretel-os/src')` and `~/.env.pretel_os` loaded).

### 8.1 Capture a deferred task

```python
from mcp_server.tools.tasks import task_create
await task_create(
    title="DEFERRED: short headline",
    bucket="business",
    project="pretel-os",
    module="M4",
    trigger_phase="Phase D",
    source="operator",
    priority="normal",
    description="Full description with rationale and trigger condition.",
)
# → {status:'ok', id:uuid, status_value:'open'}
```

DO NOT use `save_lesson` for deferrals anymore. That was the LL-M4-PHASE-A-002 anti-pattern that motivated this module.

### 8.2 Record an ADR

```python
from mcp_server.tools.decisions import decision_record
await decision_record(
    bucket="business",
    project="pretel-os",
    title="ADR-025: <title>",
    context="<context>",
    decision="<decision>",
    consequences="<consequences>",
    alternatives="<alternatives>",
    scope="architectural",                  # or 'process', 'product', 'operational'
    applicable_buckets=["business","personal"],
    decided_by="operator",
    severity="critical",                    # 'critical' | 'normal' | 'minor'
    adr_number=25,                          # next available
    tags=["relevant","tags"],
)
# → {status:'ok', id:uuid, adr_number:25, embedding_queued:False}
```

Then mirror the canonical text into `DECISIONS.md` so git history carries the prose source. The table row is the queryable copy.

### 8.3 Supersede an ADR

```python
from mcp_server.tools.decisions import decision_supersede
await decision_supersede(
    old_id="<uuid of the ADR being replaced>",
    new_decision_payload={
        "bucket": "business",
        "project": "pretel-os",
        "title": "ADR-026: <new title>",
        "context": "...",
        "decision": "...",
        "consequences": "...",
        # optional: scope, severity, applicable_buckets, tags, adr_number, etc.
    },
)
# → {status:'ok', new_id:uuid, old_id:uuid, embedding_queued:False}
```

The transaction: verifies old row is `status='active'`, embeds new payload, INSERTs new row, UPDATEs old row to `status='superseded'` + `superseded_by_id=new_id`. Atomic — any failure rolls back both.

### 8.4 Iterate on a best practice (record → update → rollback)

```python
from mcp_server.tools.best_practices import best_practice_record, best_practice_rollback

# Initial record
r = await best_practice_record(
    title="<short title>",
    guidance="<the rule>",
    rationale="<why>",
    domain="process",                       # 'process' | 'convention' | 'workflow' | 'communication'
    scope="global",
    tags=["..."],
)
bp_id = r["id"]

# Iterate (UPDATE path) — copies current guidance/rationale into previous_*
await best_practice_record(
    title="<title>",
    guidance="<refined rule>",
    rationale="<refined why>",
    domain="process",
    update_id=bp_id,                        # presence triggers UPDATE path
)
# → {status:'ok', action:'updated', rollback_available:True}

# Rollback if needed (single-step only — no chain)
await best_practice_rollback(id=bp_id)
# → {status:'ok', action:'rolled_back'}
# previous_guidance + previous_rationale are now NULL; no further rollback possible.
```

Multi-step history is NOT supported (per spec §10 non-goals). For long-form change tracking use the supersession chain (`superseded_by` self-FK) — old row stays as `active=false`, new row points back via `superseded_by`.

### 8.5 Set / get / list operator preferences

```python
from mcp_server.tools.preferences import preference_set, preference_get, preference_list, preference_unset

# UPSERT — same (category, key, scope) updates in place
await preference_set(category="language", key="primary", value="es")
# → {status:'ok', action:'inserted'|'updated'}

# Direct lookup
await preference_get(category="language", key="primary")
# → {status:'ok', value:'es', active:True, found:True}

# Filter listing
await preference_list(category="language", active=True)
# → {status:'ok', results:[{...}, ...]}

# Soft delete (sets active=false, value preserved)
await preference_unset(category="language", key="primary")
# → {status:'ok', id, found:True}
```

### 8.6 Submit and review router feedback

```python
from mcp_server.tools.router_feedback import router_feedback_record, router_feedback_review

# Operator-side: report routing miss
await router_feedback_record(
    feedback_type="wrong_bucket",
    request_id="<routing_logs.request_id from the bad turn>",
    operator_note="should have been scout, not business",
    proposed_correction={"bucket": "scout"},
)
# → {status:'ok', id:uuid, status_value:'pending'}

# Reviewer-side: transition out of pending
await router_feedback_review(id="<feedback id>", status="applied", reviewed_by="operator")
# → {status:'ok', id, status_value:'applied', found:True}
# applied_at is automatically set when status='applied'
```

### 8.7 Verify schema state matches expectation

```bash
psql -h localhost -U pretel_os -d pretel_os -c "\d+ tasks"
psql -h localhost -U pretel_os -d pretel_os -c "\d+ operator_preferences"
psql -h localhost -U pretel_os -d pretel_os -c "\d+ router_feedback"
psql -h localhost -U pretel_os -d pretel_os -c "\d+ best_practices"
psql -h localhost -U pretel_os -d pretel_os -c "\d+ decisions"

# Compare against pinned snapshot
cat ~/dev/pretel-os/migrations/audit/0029_post_state.md
```

If production drifts from the audit snapshot, that's a problem worth investigating before any new migration.

### 8.8 Re-run migration 0029 idempotency check

```bash
psql -h localhost -U pretel_os -d pretel_os -v ON_ERROR_STOP=1 -f migrations/0029_data_migration_lessons_split.sql
```

Should produce 4 NOTICE lines ("not in active/pending_review or missing — skipping") and 5 NOT EXISTS gate skips for the ADR inserts. ADR count stays at 5, tasks count unchanged, lessons archived count unchanged.

---

## 9. Health checks (every session start)

```bash
# 1. MCP server is up
systemctl --user status pretel-os-mcp --no-pager | head -5

# 2. DB poller has flipped to healthy (look for "db_healthy transition: False -> True" in logs)
journalctl --user -u pretel-os-mcp -n 50 --no-pager | grep db_healthy

# 3. Tool registration count = 25
python3 - <<'PYEOF'
import asyncio, sys, os
sys.path.insert(0, os.path.expanduser('~/dev/pretel-os/src'))
import logging; logging.disable(logging.CRITICAL)
for envf in ['~/.env.pretel_os', '~/.env.litellm']:
    p = os.path.expanduser(envf)
    if os.path.exists(p):
        for line in open(p):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
from mcp_server.main import build_app
app = build_app()
async def n():
    return len(await app.list_tools())
print(f"Tools registered: {asyncio.run(n())}")
PYEOF
# Expected: Tools registered: 25

# 4. Phase A post-state still matches
cat ~/dev/pretel-os/migrations/audit/0029_post_state.md | head -5
```

---

## 10. Test suite

```bash
cd ~/dev/pretel-os

# Phase D will populate this. For now, smoke scripts in /tmp/ from Phase C close-out:
ls /tmp/smoke_*.py
# /tmp/smoke_preferences.py
# /tmp/smoke_tasks.py
# /tmp/smoke_router_feedback.py
# /tmp/smoke_decisions.py
# /tmp/smoke_best_practices.py
# /tmp/smoke_bp_queue.py            (forces embed=None, validates pending_embeddings queue)
# /tmp/smoke_degraded.py            (forces db_healthy=False, validates degraded path)

# mypy on the 5 Phase C files
mypy --strict src/mcp_server/tools/preferences.py
mypy --strict src/mcp_server/tools/tasks.py
mypy --strict src/mcp_server/tools/router_feedback.py
mypy --strict src/mcp_server/tools/decisions.py
mypy --strict src/mcp_server/tools/best_practices.py
# Expected: Success: no issues found in 1 source file (each)

# Verify no hardcoded model strings (CONSTITUTION rule per ADR-020)
grep -rnE "(claude-[0-9]|gpt-[0-9]|gemini-[0-9])" src/mcp_server/tools/*.py
# Expected: no output
```

Phase D will land `tests/mcp_server/tools/test_*.py` with proper pytest coverage. Until then, `/tmp/smoke_*.py` scripts are the validation surface.

---

## 11. Known operational signals

### 11.1 Healthy ranges

| Signal | Healthy |
|---|---|
| `db_healthy` (poller) | True |
| Tool registration count | 25 (7 M3 + 18 M0.X) |
| `usage_logs` rows per tool call | exactly 1 (success or failure path) |
| `pending_embeddings` backlog | < 100 rows; if growing, OpenAI rate limit or auto-index worker stalled |
| Fallback journal entries (`~/pretel-os-data/fallback-journal/YYYYMMDD.jsonl`) | 0 during normal operation; non-zero only when DB was down |
| Degraded responses in `usage_logs.metadata->>'degraded_reason'` | < 1% of writes |

### 11.2 Trouble signals

| Symptom | Likely cause | Action |
|---|---|---|
| `tools registered: < 25` | New tool failed to import or `app.tool()` line missing in `main.py` | Check `journalctl --user -u pretel-os-mcp` for ImportError; verify each tools file has its `app.tool(fn)` line in `build_app()` |
| Every tool returns `{status:'degraded', degraded_reason:'db_unavailable'}` | Postgres down OR poller hasn't flipped yet (30s cycle) | Verify `systemctl status postgresql` + wait one poller cycle; check `~/.pgpass` permissions if non-interactive |
| `decision_record` succeeds but search returns 0 hits | embedding=NULL row, never embedded | Check `pending_embeddings` for the row; auto-index worker (M6) has not flushed it yet |
| `best_practice_record` returns `embedding_queued:True` but no `pending_embeddings` row | should not happen post-`aba04c7` | Re-verify the ON CONFLICT block in `best_practices.py`; was the manual queue logic deleted? |
| `task_update` returns `{status:'error', error:'no fields to update'}` | All optional kwargs were None | Caller bug: pass at least one field |
| `decision_supersede` returns `{status:'error', error:"old decision status is 'superseded'"}` | Trying to supersede an already-superseded row | Find the head of the chain via `superseded_by_id` walk; supersede that |
| Schema diff vs `migrations/audit/0029_post_state.md` | Production schema drift | STOP; investigate before any new migration |

### 11.3 Cost tracking

Most M0.X tools have **zero LLM cost** — they're CRUD against Postgres.

Tools with embedding cost:

| Tool | Per-call cost (text-embedding-3-large @ ~50 input tokens) |
|---|---|
| `decision_record` | ~$0.00007 |
| `decision_search` | ~$0.00007 (embeds the query) |
| `decision_supersede` | ~$0.00007 (embeds the new payload) |
| `best_practice_record` (insert + update paths) | ~$0.00007 |
| `best_practice_search` | ~$0.00007 |
| `best_practice_rollback` | ~$0.00007 (re-embeds restored content) |

At realistic operator volume (~10-50 records + searches/day), monthly embedding cost from M0.X is **< $1.00**. Compare against M4 Phase A classifier (~$0.0008 per turn × N turns/day) which is the dominant cost.

---

## 12. Failure modes and recovery

### 12.1 Postgres down

**Symptom:** Every tool returns `{status:'degraded', degraded_reason:'db_unavailable', journal_id:...}`.

**Diagnosis:**
```bash
sudo systemctl status postgresql
journalctl -u postgresql -n 50 --no-pager
```

**Recovery:**
```bash
sudo systemctl start postgresql
# Wait one poller cycle (~30s) for db_healthy to flip
sleep 35
journalctl --user -u pretel-os-mcp -n 5 --no-pager | grep db_healthy
# Expected: "db_healthy transition: False -> True"
```

**Replay:** entries in `~/pretel-os-data/fallback-journal/YYYYMMDD.jsonl` need to be replayed. Until the auto-index/journal-replay worker (Module 6) ships, manual replay only — read the JSONL, dispatch to the named operation. Idempotency_key in each entry prevents double-apply on partial replay.

### 12.2 OpenAI embedding API down

**Symptom:** `decision_record` and `best_practice_record` return `{embedding_queued:True}`. Searches fail or return stale results.

**Diagnosis:**
```bash
curl -s -o /dev/null -w "%{http_code}\n" \
    -H "Authorization: Bearer $(grep OPENAI_API_KEY ~/.env.litellm | cut -d= -f2)" \
    https://api.openai.com/v1/models | head -1
# Expected: 200. Any other → OpenAI side issue.
```

**Recovery:** wait for OpenAI to return. Rows are in `pending_embeddings`; auto-index worker (M6) will backfill embeddings when it runs.

**Verify backlog drained later:**
```sql
SELECT target_table, count(*) FROM pending_embeddings GROUP BY target_table;
```

### 12.3 MCP server crash / restart needed

**Symptom:** Client connection errors; `app.list_tools()` from outside fails.

**Diagnosis:**
```bash
systemctl --user status pretel-os-mcp --no-pager
journalctl --user -u pretel-os-mcp -n 100 --no-pager
```

**Recovery:**
```bash
systemctl --user restart pretel-os-mcp
sleep 3
systemctl --user status pretel-os-mcp --no-pager | head -5
```

If restart loops (service goes Active → Failed repeatedly), check the journal for ImportError or uncaught exception in `build_app()` — most often a syntax error in a recently-edited tool file.

### 12.4 Schema drift detection

**Symptom:** Tool inserts fail with column-not-found or constraint violations against an unchanged tool — schema changed under us.

**Diagnosis:**
```bash
# Diff each new/amended table against the audit snapshot
for tbl in tasks operator_preferences router_feedback best_practices decisions; do
    diff <(psql -h localhost -U pretel_os -d pretel_os -c "\d+ $tbl" 2>&1) \
         <(grep -A 50 "## \\\\d+ $tbl" migrations/audit/0029_post_state.md)
done
```

**Recovery:** identify the drift source. If it's a manual ALTER outside a migration, undo it and put the change in a new migration. Schema must be migration-driven per CONSTITUTION §2.4.

### 12.5 `pending_embeddings` backlog stuck

**Symptom:** Backlog growing instead of draining. `SELECT count(*), max(attempts) FROM pending_embeddings;` shows attempts > 5 on many rows.

**Diagnosis:** `last_error` column reveals the recurring failure.
```sql
SELECT target_table, count(*), max(attempts), array_agg(DISTINCT last_error)
FROM pending_embeddings WHERE attempts > 0 GROUP BY target_table;
```

**Recovery:** depends on `last_error`. Common: rate-limit (wait + reduce concurrency), invalid input (purge dead rows after manual review), or auto-index worker offline (Module 6 not yet shipped — for now, manual replay).

---

## 13. Spec drifts caught (LL-M0X-001 territory)

Module 0.X surfaced 4 spec/schema mismatches at scratch test time. Each was caught BEFORE production damage. The pattern: spec was written referencing intended/remembered schema rather than actual schema.

| # | Drift | Caught at | Fix commit |
|---|---|---|---|
| 1 | `router_feedback.request_id uuid REFERENCES routing_logs(request_id)` — actual `routing_logs.request_id` is `text` and has no UNIQUE (partitioned table) | Pre-check on 0026 | `fe923a9` |
| 2 | `decisions.scope NOT NULL DEFAULT 'project'` — `'project'` not in CHECK enum (architectural\|process\|product\|operational) | Smoke test on 0028 | `acac675` |
| 3 | Lesson migration `WHERE status != 'superseded'` — `lessons.status` is enum `lesson_status` which doesn't include `'superseded'` | Smoke test on 0029 | `40d51cc` |
| 4 | M0.X plan + ADR-022 claimed "L0 budget 1,200 tokens combined" — CONSTITUTION §2.3 actually budgets only `identity.md` at 1,200 | Pre-check on Phase B | `26c7189` |

Plus a fifth caught in Phase C:

| # | Drift | Caught at | Fix |
|---|---|---|---|
| 5 | brief signature `decision_record(project: Optional[str] = None)` — schema has `decisions.project NOT NULL` | Schema verification before writing tool | `df53b57` (made required) + tracked task `80462622` to update spec doc |

**Discipline that made these caught:** every migration applied to scratch DB before production, with smoke tests asserting content (not just shape) per LL-M4-PHASE-A-001.

**Mitigation going forward:** before writing schema or spec referencing existing schema, run `\d <table>` against production and grep CONSTITUTION sections for invariants. Don't trust memory.

---

## 14. Module 2 regression caught (LL-M0X-002)

`notify_missing_embedding()` in migration 0019 used `CASE TG_TABLE_NAME WHEN x THEN NEW.<column>` over 9 tables. PL/pgSQL evaluates every branch's column references at runtime against the firing row's type. Bug: `NEW.content` (lessons branch) fails when the trigger fires for any of the 8 other tables.

Latent for ~6 months because Phase 2 tables (`decisions`, `patterns`, `gotchas`, `contacts`, `ideas`, `projects_indexed`, `conversations_indexed`, `tools_catalog`) were all empty. Would have detonated on first non-`lessons` insert anywhere.

Fix in commit `cb56311` (migration 0028a): rewrite using IF/ELSIF chain. PL/pgSQL evaluates only the matched branch's expressions. All 9 table branches preserved with identical semantics.

**Lesson:** polymorphic triggers over empty tables are time bombs. Any future cross-table function should use IF/ELSIF or per-table dispatch, never `CASE` with `NEW.<column>` references.

---

## 15. SOUL.md (Phase B)

`SOUL.md` at repo root: operator voice and behavior contract. Loaded into L0 alongside `CONSTITUTION.md`, `identity.md`, `AGENTS.md` by any LLM agent reading the repo (Claude Code, Telegram bot via OpenClaw, MCP callers).

Claude.ai web/app does NOT load `SOUL.md` — it uses Anthropic userPreferences. Keep both in sync manually until automated sync ships.

L0 budget per CONSTITUTION §2.3: only `identity.md` has the 1,200-token cap. SOUL.md, AGENTS.md, and CONSTITUTION.md load into L0 without per-file numerical caps; pre-commit hook §7.36 enforces only the `identity.md` cap.

Verify identity.md remains within budget:

```bash
python3 -c "
import tiktoken
enc = tiktoken.get_encoding('cl100k_base')
content = open('identity.md').read()
n = len(enc.encode(content))
print(f'identity.md: {n} / 1200 tokens [{ \"OK\" if n <= 1200 else \"OVER BUDGET\" }]')
"
```

---

## 16. Setup gaps (cross-reference)

Three gaps were discovered during M0.X pre-flight that future fresh setups must address. Full detail in [`module_2_data_layer.md`](module_2_data_layer.md) (commit `a507a86`):

1. `~/.pgpass` populated with role credentials (psql non-interactive)
2. `ALTER ROLE pretel_os CREATEDB` (scratch DB pattern requires it)
3. Pre-load extensions into `template1` (pgvector 0.6.0 not trusted in Ubuntu 24.04 noble — see ADR-024 alternatives)

If a future setup hits any of these, jump to `module_2_data_layer.md`.

---

## 17. Pending phases — high-level checkpoints

### Phase D — Tests

- Unit + integration tests per tool (LL-M4-PHASE-A-001 mandate: integration tests assert content, not just shape)
- Coverage ≥ 80% on new code
- Required: `test_best_practice_rollback_round_trip` (record → update → assert previous_* populated → rollback → assert content restored). Already mentally designed by the Phase C smoke at `/tmp/smoke_best_practices.py` — replicate in pytest.
- Migration 0029 idempotency test (re-run produces no duplicates and 4 NOTICE skips on the lessons split DO blocks)

### Phase E — Docs + tag

- `specs/module-0x-knowledge-architecture/layer_loader_contract.md` — frozen mapping for Module 4 Phase B planner
- `docs/DATA_MODEL.md` §5.7-5.10 expanded from current stubs to full schema docs
- `docs/INTEGRATIONS.md` MCP tool catalog updated
- `SESSION_RESTORE.md` §13 final snapshot
- Tag `module-0x-complete` on the final commit
- Resolve the 3 deferred-todo tasks below (all have trigger_phase pointing at this phase or new migration 0030)

### Module 0.X exit gate

```bash
cd ~/dev/pretel-os

# All Phase D + E gate tasks
grep -c "^- \[ \] M0X\.D\." specs/module-0x-knowledge-architecture/tasks.md
# Expected: 0

grep -c "^- \[ \] M0X\.E\." specs/module-0x-knowledge-architecture/tasks.md
# Expected: 0

# Tag exists
git tag -l 'module-0x-complete'
# Expected: module-0x-complete

# Layer loader contract frozen
test -f specs/module-0x-knowledge-architecture/layer_loader_contract.md && echo OK
```

When all four pass, M4 Phase B is unblocked.

---

## 18. Deferred technical debt

Six task rows tracked in the `tasks` table — three from this module's Phase C close-out, three migrated from M4 Phase A's `lessons` `deferred-todo` workaround into typed tasks via migration 0029.

| Task ID | Module | Trigger phase | Title |
|---|---|---|---|
| `16d4056e` | M0.X | Phase E or post-M0.X | DEFERRED: lessons.py no pasa mypy --strict |
| `92cac1b3` | M0.X | Phase E or new migration 0030 | Add notify_missing_embedding trigger to best_practices |
| `80462622` | M0.X | Phase E | Update spec.md §5.2 to mark decisions.project as NOT NULL |
| `bad37638` | M4 | Phase D | DEFERRED: LiteLLM returns alias not concrete model in response.model |
| `ae35eb8a` | M0.X | before Module 5 | DEFERRED: Add pyproject.toml + retire conftest.py hack |
| `d3c00a37` | M4 | Phase F | DEFERRED: Enable prompt caching when classify.txt grows past 1024 tokens |

Query current state:

```python
from mcp_server.tools.tasks import task_list
await task_list(status="open", limit=50)
```

Or filter to one module:

```python
await task_list(module="M0.X", status="open")
```

---

## 19. Quick reference card

```
Module:           Module 0.X — Knowledge Architecture
Tables:           tasks, operator_preferences, router_feedback, best_practices,
                  + decisions amendment
MCP tools:        18 (5 task_*, 4 preference_*, 2 router_feedback_*,
                  3 decision_*, 4 best_practice_*)
Total registered: 25 (7 M3 + 18 M0.X)
Migrations:       0024-0029 + 0028a
ADRs produced:    020-024 (canonical text in DECISIONS.md, queryable in decisions table)
Workspace files:  SOUL.md (Phase B)
Tests:            Phase D pending — currently /tmp/smoke_*.py
Spec drifts:      5 caught at scratch test time (LL-M0X-001 family) — zero
                  production damage
Module 2 fix:     notify_missing_embedding polymorphic CASE bug (0028a)
Cost (M0.X-only): < $1/month at realistic volume
Last reviewed:    2026-04-28
```

---

## 20. Change log

| Date | Commit | Change |
|---|---|---|
| 2026-04-28 | `b96fa84` | docs: capture ADR-024 HNSW deferred + sweep M0.X spec/tasks |
| 2026-04-28 | `8a6cf7d` | M0X.T1: revise spec — best_practices new table |
| 2026-04-28 | `ff81538` | M0X.T2: plan.md — 5 phases (A-E) |
| 2026-04-28 | `c4b4649` | M0X.T3: tasks.md — 141 atomic tasks |
| 2026-04-28 | `db73a67` | M0X.A.1: migration 0024 tasks table |
| 2026-04-28 | `394bf1a` | M0X.A.2: migration 0025 operator_preferences |
| 2026-04-28 | `fe923a9` | M0X.A.3: migration 0026 router_feedback + spec §5.4 amendment |
| 2026-04-28 | `885adba` | M0X.A.4: migration 0027 best_practices (HNSW deferred per ADR-024) |
| 2026-04-28 | `cb56311` | fix(M2): notify_missing_embedding polymorphic CASE bug (0028a) |
| 2026-04-28 | `acac675` | M0X.A.5: migration 0028 decisions amendment + spec §5.2 fix |
| 2026-04-28 | `40d51cc` | M0X.A.6: migration 0029 ADR seed + lessons split |
| 2026-04-28 | `3e55baf` | M0X.A.7: post-migration schema audit |
| 2026-04-28 | `bc4e5df` | M0X.A: mark Phase A tasks complete |
| 2026-04-28 | `26c7189` | M0X.B: SOUL.md added to L0 + spec/plan/ADR-022 budget drift fix |
| 2026-04-28 | `03f71f4` | M0X.C.3: implement preferences.py — 4 tools |
| 2026-04-28 | `b17dce1` | M0X.C.1: implement tasks.py — 5 tools |
| 2026-04-28 | `e5ae84b` | M0X.C.4: implement router_feedback.py — 2 tools |
| 2026-04-28 | `df53b57` | M0X.C.2: implement decisions.py — 3 tools |
| 2026-04-28 | `829686f` | M0X.C.5: implement best_practices.py — 4 tools |
| 2026-04-28 | `aba04c7` | M0X.C.5b: queue pending_embeddings manually for best_practices |
| 2026-04-28 | `b553fb0` | M0X.C close-out: 18 tools registered, mypy clean, degraded verified |
| 2026-04-28 | `076279b` | M0X.D conftest gate fix: truncate gated on `patched_db` not `test_pool` |
| 2026-04-28 | `9c08d2c` | M0X.D mypy.ini: per-module ignore_errors for transitive imports |
| 2026-04-28 | `591d477` | M0X.D.2: integration tests — full MCP protocol round-trip + degraded mode |
| 2026-04-28 | `6f07447` | M0X.D.3: migration 0029 idempotency test |
| 2026-04-28 | `59127aa` | M0X.D close-out: 47 tests green, coverage ≥80% on all 5 M0.X tool files |
| 2026-04-29 | `9cbc639` | chore: gitignore .coverage + htmlcov from pytest-cov runs |
| 2026-04-29 | `469e79e` | M0X.E.1: layer_loader_contract.md frozen — Phase B input spec complete |
| 2026-04-29 | `532581b` | M0X.E.1.1: contract patch — bundle shape, severity SQL CASE, token method (3 patches from operator review) |
| 2026-04-29 | `5d35835` | M0X.E.2: DATA_MODEL.md §5.7-5.10 full DDL + §5.2.1 amendment |
| 2026-04-29 | `714d1a9` | M0X.E.3: INTEGRATIONS.md §14 — 18 M0.X tool entries |
| 2026-04-29 | `93b1b43` | M0X.E.4: SESSION_RESTORE.md §13 Module 0.X complete snapshot |
| 2026-04-29 | `9a94e93` | M0X.E.5: spec.md drift fixes (tool count 18, decisions.project NOT NULL note) |
| 2026-04-29 | `85188db` | M0X.E.6: plan.md status complete + tasks.md M0X.* closed |
| 2026-04-29 | `49edc0c` | M0X.E.7: cross-ref consistency — fix two stale "17 tools" refs |
| 2026-04-29 | (tag) | **`module-0x-complete`** — Module 0.X COMPLETE, M4 Phase B unblocked |

---

## 21. Cross-references

- **Spec:** `specs/module-0x-knowledge-architecture/spec.md`
- **Plan:** `specs/module-0x-knowledge-architecture/plan.md`
- **Atomic tasks:** `specs/module-0x-knowledge-architecture/tasks.md`
- **Layer loader contract (frozen):** `specs/module-0x-knowledge-architecture/layer_loader_contract.md` — input contract for M4 Phase B
- **ADRs:** `DECISIONS.md` (canonical) + `decisions` table (queryable). M0.X-relevant ADRs: 020, 021, 022, 023, 024, 025
- **Schema audit:** `migrations/audit/0029_post_state.md`
- **DATA_MODEL §5.7–§5.10:** `docs/DATA_MODEL.md` (full DDL for the 4 new tables); decisions amendment lives in §5.2.1 (folded in during Phase E — was §5.11 before close-out)
- **MCP tool catalog:** `docs/INTEGRATIONS.md` §14 — 18 M0.X tools with input/return/degraded shapes
- **Setup gaps:** `runbooks/module_2_data_layer.md`
- **SDD trinity rule:** `runbooks/sdd_module_kickoff.md`
- **Module 4 (consumer of M0.X tables):** `runbooks/module_4_router.md`
- **Constitution layer rules:** `CONSTITUTION.md` §2.3, §7.36, §8.43
- **Lessons captured:** `docs/LESSONS_LEARNED.md` LL-M0X-001, LL-M0X-002
