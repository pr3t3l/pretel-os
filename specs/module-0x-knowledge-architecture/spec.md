# Module 0.X — Knowledge Architecture

**Status:** DRAFT (review after Module 4 Phase A closes)
**Created:** 2026-04-28
**Position in roadmap:** Between Module 4 Phase A and Module 4 Phase B. Must close before Phase B starts.

## 1. Purpose

Split the single `lessons` table into four typed knowledge stores plus one workspace file, so that each kind of durable knowledge has its own lifecycle, schema, and load path. Today everything that survives a session — TODOs, decisions, best practices, post-hoc lessons, voice — is being written to `lessons` with workaround tags. This is unsustainable: each knowledge type has different mutability rules (tasks close, decisions get superseded, best practices update in place, lessons are immutable), different load triggers (preferences load every session, lessons load only when classifier says so), and different write provenance.

Module 0.X is the prerequisite for Phase B (Layer Loader). Phase B has to know what tables/files to read for each layer L0–L4. Designing four new tables after Phase B ships forces re-work.

**Important note from review (2026-04-28):** the `decisions` table already exists in DATA_MODEL §5.2 (project-scoped, ADR-style with embedding + status enum). The original spec proposed a new `decisions` table — that was wrong. M0.X amends the existing one. Similarly, `patterns` (§5.1) and `gotchas` (§5.3) already cover code-snippet best practices and anti-patterns. Whether a new `best_practices` table is needed for PROCESS guidance (vs CODE in patterns) is open question OQ-6.

## 2. Authority and references

| Source | Relevance |
|---|---|
| `CONSTITUTION §2.3` | Five layers L0–L4 with fixed budgets |
| `CONSTITUTION §2.7` | Source priority resolution |
| `CONSTITUTION §5.2` | Auto-approval rules for `lessons` (analogous needed for new tables) |
| `docs/DATA_MODEL.md` | Single source of truth for schemas — Module 0.X amends |
| `docs/INTEGRATIONS.md` | MCP tool catalog |
| ADR-021 (to be written) | Formal: split `lessons` into typed stores |
| ADR-022 (to be written) | Formal: SOUL.md voice file |

## 3. Scope

### 3.1 In scope

1. **Three new tables**:
   - `tasks` — pending and in-progress work items (no embedding)
   - `operator_preferences` — operator-controlled facts (UNIQUE on category+key+scope)
   - `router_feedback` — explicit feedback loop signals
2. **Amendments to existing tables**:
   - `decisions` (DATA_MODEL §5.2): add `scope`, `applicable_buckets`, `decided_by`, `tags`, `severity`, `adr_number`, `derived_from_lessons` columns. Existing `bucket`, `project`, `client_id`, `title`, `context`, `decision`, `consequences`, `alternatives`, `status`, `superseded_by_id`, `embedding`, `created_at` stay.
3. **One new workspace file**: `SOUL.md` (template + L0 loader integration)
4. **MCP tools** for each table (~13 tools total — see §6)
5. **Layer loader contract** for Phase B consumption
6. **Migration script** for the 4 misclassified `lessons` rows

### 3.2 Out of scope

- Reflection worker (Module 6) implementation
- Phase B Layer Loader implementation
- Replacement of existing `lessons` (it stays, scope tightened to "post-hoc patterns")
- UI/dashboard
- Sync between Anthropic userPreferences and `operator_preferences` table

### 3.3 Boundaries

| Adjacent | Relationship |
|---|---|
| Module 1 (Foundation) | Same Postgres, same migration framework |
| Module 3 (MCP server) | New tools register in existing catalog |
| Module 4 Phase A | Already shipped, no changes |
| Module 4 Phase B | Primary consumer; reads new tables |
| Module 6 (Reflection worker) | Reads `router_feedback`, writes lessons/best_practices |

## 4. Knowledge taxonomy — what goes where

| Phrase pattern | Tool | Rationale |
|---|---|---|
| "next time X happens, do Y" | `save_lesson` (existing) | Post-hoc pattern |
| "we should fix X later" / "DEFERRED" / "TODO when phase Y" | `task_create` | Pending work with trigger |
| "we decided X over Y because..." | `decision_record` | Choice between alternatives, immutable |
| "always do X when working with Y" | `best_practice_record` | Reusable domain guidance |
| "I prefer TypeScript" / "always answer in Spanish" | `preference_set` | Operator-controlled fact |
| "info incorrecta" / "te faltó contexto" mid-conversation | `router_feedback_record` | Real-time signal to improve Router |

**Rule for Claude:** never use verbal acknowledgment for any of these. The tool call IS the acknowledgment. Ask the operator if unclear.

## 5. Schemas

### 5.1 `tasks`

```sql
CREATE TABLE tasks (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title           text NOT NULL,
  description     text,
  bucket          text NOT NULL,
  project         text,
  module          text,
  status          text NOT NULL DEFAULT 'open'
                  CHECK (status IN ('open','in_progress','blocked','done','cancelled')),
  priority        text DEFAULT 'normal'
                  CHECK (priority IN ('urgent','high','normal','low')),
  blocked_by      uuid REFERENCES tasks(id) ON DELETE SET NULL,
  trigger_phase   text,
  source          text NOT NULL
                  CHECK (source IN ('operator','claude','reflection_worker','migration')),
  estimated_minutes integer,
  github_issue_url text,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now(),
  done_at         timestamptz,
  metadata        jsonb DEFAULT '{}'::jsonb
);

CREATE INDEX idx_tasks_bucket_status ON tasks(bucket, status);
CREATE INDEX idx_tasks_open_by_phase ON tasks(trigger_phase) WHERE status IN ('open','blocked');
CREATE INDEX idx_tasks_module ON tasks(module) WHERE module IS NOT NULL;
```

### 5.2 `decisions` table amendment

The `decisions` table exists at DATA_MODEL §5.2. M0.X migration adds these columns:

- `scope text NOT NULL DEFAULT 'project' CHECK (scope IN ('architectural','process','product','operational'))` — distinguishes ADR-level from process-level decisions
- `applicable_buckets text[] DEFAULT '{}'` — cross-bucket scope for decisions that affect more than one bucket
- `decided_by text NOT NULL DEFAULT 'operator'` — provenance
- `tags text[] DEFAULT '{}'` — for filtering
- `severity text DEFAULT 'normal'` — distinguishes load-bearing decisions from process tweaks
- `adr_number integer UNIQUE` — formal ADR numbering (NULL for non-formal)
- `derived_from_lessons uuid[] DEFAULT '{}'` — provenance when a decision crystallized from one or more lessons

Indexes added:
- `CREATE INDEX idx_decisions_scope_status ON decisions(scope, status)`
- `CREATE INDEX idx_decisions_applicable_buckets ON decisions USING GIN(applicable_buckets)`
- `CREATE INDEX idx_decisions_tags ON decisions USING GIN(tags)`

Migration writes (in order): ADR-020 (LiteLLM proxy gateway), ADR-021 (split lessons into typed stores — this M0.X), ADR-022 (SOUL.md voice file).

### 5.3 `operator_preferences`

```sql
CREATE TABLE operator_preferences (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  category        text NOT NULL
                  CHECK (category IN ('communication','tooling','workflow','identity','language','schedule')),
  key             text NOT NULL,
  value           text NOT NULL,
  scope           text NOT NULL DEFAULT 'global',
  active          boolean NOT NULL DEFAULT true,
  source          text NOT NULL
                  CHECK (source IN ('operator_explicit','inferred','migration')),
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now(),
  metadata        jsonb DEFAULT '{}'::jsonb,
  UNIQUE(category, key, scope)
);

CREATE INDEX idx_preferences_scope_active ON operator_preferences(scope) WHERE active;
CREATE INDEX idx_preferences_category_active ON operator_preferences(category) WHERE active;
```

Atomic update via `INSERT ... ON CONFLICT (category, key, scope) DO UPDATE`. No vector search — direct lookup.

### 5.4 `router_feedback`

```sql
CREATE TABLE router_feedback (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  request_id          uuid REFERENCES routing_logs(request_id) ON DELETE SET NULL,
  feedback_type       text NOT NULL
                      CHECK (feedback_type IN ('missing_context','wrong_bucket','wrong_complexity','irrelevant_lessons','too_much_context','low_quality_response')),
  operator_note       text,
  proposed_correction jsonb,
  status              text NOT NULL DEFAULT 'pending'
                      CHECK (status IN ('pending','reviewed','applied','dismissed')),
  reviewed_by         text,
  applied_at          timestamptz,
  created_at          timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_router_feedback_status ON router_feedback(status);
CREATE INDEX idx_router_feedback_request ON router_feedback(request_id);
CREATE INDEX idx_router_feedback_type ON router_feedback(feedback_type) WHERE status = 'pending';
```

### 5.5 `SOUL.md` workspace file

Flat file at `~/dev/pretel-os/SOUL.md`, committed to git. Loaded into L0 alongside `IDENTITY.md`, `CONSTITUTION.md`, `AGENTS.md`. Template content mirrors operator's stated `userPreferences`.

Note: Claude.ai web/app does NOT load `SOUL.md` — Anthropic uses operator's userPreferences for that surface. SOUL.md applies to Claude Code, Telegram bot via OpenClaw, and any MCP session caller that loads it.

## 6. MCP tools

| Table | Tools |
|---|---|
| Tasks | `task_create`, `task_list`, `task_update`, `task_close`, `task_reopen` |
| Decisions (existing, amended) | `decision_record`, `decision_search`, `decision_supersede` — point at the existing `decisions` table with the new columns from §5.2 |
| Preferences | `preference_set`, `preference_get`, `preference_list`, `preference_unset` |
| Router feedback | `router_feedback_record`, `router_feedback_review` |

Best-practice tooling deferred pending OQ-6 resolution (§12).

Total: 13 tools.

## 7. Migration plan

Single migration `M0X_001_knowledge_split.sql`:

1. Create 4 new tables + `router_feedback` with all indexes
2. Identify the 4 misclassified `lessons` rows by tag `deferred-todo`:
   - `c40e09fc` (anti-pattern: I'll register it mentally) → `decisions` scope='process'
   - `d7f1e119` (LiteLLM concrete model) → `tasks` module='M4', trigger_phase='Phase D'
   - `89c11602` (pyproject.toml) → `tasks` module='M0.X', trigger_phase='before Module 5'
   - `3d98464b` (prompt caching) → `tasks` module='M4', trigger_phase='Phase F'
3. Mark originals `status='superseded'` with metadata pointing to new rows
4. Insert ADR-021 into `decisions`: "Split lessons into typed stores"
5. Insert ADR-022 into `decisions`: "SOUL.md voice file"
6. Create initial `SOUL.md`
7. Seed 5–10 `operator_preferences` from operator's stated userPreferences

Idempotent: each step gates on `IF NOT EXISTS`.

## 8. Layer loader contract for Phase B

| Layer | Source | Filter |
|---|---|---|
| L0 | `CONSTITUTION.md` + `IDENTITY.md` + `AGENTS.md` + `SOUL.md` (full) + `operator_preferences WHERE scope='global' AND active` | All |
| L1 | `decisions WHERE bucket=current OR current=ANY(applicable_buckets) AND status='active'` (summaries, ranked by recency) + `operator_preferences WHERE scope LIKE 'bucket:<current>'` | Active only |
| L2 | `decisions` and `best_practices WHERE scope='project:<current>'` (pending OQ-6 — may collapse into patterns table; see §12) | Active only |
| L3 | `tools_catalog WHERE kind='skill'` (existing, no change) | Classifier-filtered |
| L4 | `lessons` (existing) + `best_practices WHERE domain matches OR bucket-applicable` (pending OQ-6 — may collapse into patterns table; see §12) | classifier `needs_lessons=true` only |

`tasks` and `router_feedback` are NOT loaded into context bundle — they're operational tables.

**Note on best_practices in this contract:** the L2 and L4 rows reference a `best_practices` table that is currently OQ-6 (open question — may be a new table, may be an extension of existing `patterns` per DATA_MODEL §5.1). The contract is written assuming a separate table; if OQ-6 resolves to "extend patterns", revise §8 to reference `patterns` filtered by `category='best_practice'` or similar. M0X.T1 (spec revision) is the gate to resolve this before plan.md is written.

## 9. Failure modes

- DB unavailable: fall back to journal at `~/.pretel-os/journal/{tool}.jsonl` (existing pattern)
- Embedding fails: row saved without embedding, queued in `pending_embeddings`
- Migration partial: each step idempotent, post-migration assertions verify
- Operator deletes a `decision` referenced by `supersedes`: soft-delete only
- `SOUL.md` missing: L0 loader logs warning, continues

## 10. Non-goals

- Web UI for browsing
- Multi-operator support
- Realtime sync to Anthropic userPreferences (deferred)
- Auto-import existing markdown ADRs (manual via tools)
- Best practices content versioning/history (update-in-place sufficient)

## 11. Success criteria

- Migration applies cleanly on fresh DB and production
- New tables queryable sub-100ms on representative load
- 13 MCP tools registered and callable
- 4 misclassified rows visible in proper tables, originals superseded
- `SOUL.md` committed, ADR-022 records provenance
- Phase B planner reads §8 and produces task list without questions back
- Unit + integration tests for every MCP tool, mypy --strict clean
- One full week of routine use without resorting to `save_lesson` for clearly-typed items

## 12. Open questions (resolve in planning)

1. Should `decisions` have `severity` like lessons?
2. Should `best_practices` track `derived_from_lessons uuid[]`?
3. Embedding model: same 3072-dim or smaller for HNSW capability?
4. `operator_preferences` value: text or jsonb for arrays?
5. Token budget for `decisions` in L1 — measure typical length × count
6. (OQ-6) Whether to add a new `best_practices` table for PROCESS guidance, or extend `patterns` (§5.1, currently CODE-focused). Pending review.

## Appendix A — Why not just add columns to `lessons`?

Considered and rejected. Different mutability rules, load triggers, search semantics. Single table = lowest-common-denominator semantics = wrong for ≥3 of 4 use cases.

## Appendix B — Comparison to OpenClaw.ai

OpenClaw.ai uses plain markdown for everything. Module 0.X borrows the file pattern for `SOUL.md` (voice IS naturally markdown) and rejects it for structured stores (typed schema + Postgres + embeddings beat plain text at scale). The OpenClaw Mem0/Supermemory plugin pattern addresses "default markdown unreliable" — Module 0.X is the equivalent at table level, owned by us, no external dependency.
