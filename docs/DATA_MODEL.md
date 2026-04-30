# DATA MODEL — pretel-os

**Status:** Active
**Last updated:** 2026-04-30
**Owner:** Alfredo Pretel Vargas
**Database:** PostgreSQL 16 + pgvector
**Embeddings:** `text-embedding-3-large` (OpenAI), 3072 dimensions

This document defines every table, index, trigger, and function that constitutes the dynamic memory of pretel-os. Schema lives in migration files under `migrations/`; this document is the canonical explanation.

All assets described here belong to the database per `CONSTITUTION §2.4`. Git-resident content (skills, bucket READMEs, project READMEs, foundation docs) is out of scope for this document.

---

## 1. Overview

### 1.1 Purpose

The database holds every asset that is:
- **Dynamic** — changes more than once a week (counters, logs, queues)
- **Retrieval-optimized** — has embeddings for semantic search
- **Subject to lifecycle rules** — archive, dedup, summarize per `CONSTITUTION §5.5`
- **Machine-queried at request time** — not read by humans as canonical docs

Everything else stays in git.

### 1.2 Tables

Twenty-six tables across four tiers (21 base + 4 added by Module 0.X Phase A on 2026-04-28 + 1 added by Module 7 Phase B on 2026-04-30):

**Phase 1 (MVP — required for `Module 2: data_layer`):**

| # | Table | Purpose |
|---|-------|---------|
| 1 | `lessons` | Lessons learned, with full lifecycle status |
| 2 | `tools_catalog` | Registered skills and tools with utility score |
| 3 | `projects_indexed` | Historical/closed projects for recall |
| 4 | `project_state` | Live TODOs and decisions for active projects |
| 5 | `project_versions` | Snapshots at decision boundaries |
| 6 | `skill_versions` | History of skill file changes |
| 7 | `conversations_indexed` | Indexed past chats for semantic recall |
| 8 | `conversation_sessions` | Live session ledger (open/closed, reflection triggers) |
| 9 | `cross_pollination_queue` | Pending cross-bucket transfer proposals |
| 10 | `routing_logs` | Every Router decision for cost audit (monthly partitioned) |
| 11 | `usage_logs` | Tool and skill invocation records (monthly partitioned) |
| 12 | `llm_calls` | Per-call LLM cost audit (monthly partitioned) |
| 13 | `pending_embeddings` | Degraded-mode queue for failed embedding calls |
| 14 | `reflection_pending` | Degraded-mode queue for Reflection worker when Sonnet unreachable |
| 15 | `scout_denylist` | Operator-managed denylist for Scout safety trigger |
| 16 | `control_registry` | Manual-control cadence tracking (Scout audit, restore drill, key rotation, etc.) |

**Phase 2 (extended knowledge — added when patterns emerge):**

| # | Table | Purpose |
|---|-------|---------|
| 17 | `patterns` | Reusable code snippets, templates, UI patterns |
| 18 | `decisions` | ADR-style architectural records tied to projects (M0.X amended: +7 columns) |
| 19 | `gotchas` | Anti-patterns, "never do this" records |
| 20 | `contacts` | People: clients, collaborators, vendors |
| 21 | `ideas` | Unprocessed ideas, backlog for future exploration |

**Module 0.X (Knowledge architecture split — added 2026-04-28):**

| # | Table | Purpose |
|---|-------|---------|
| 22 | `tasks` | Pending and in-progress work items (no embedding, structured query only) |
| 23 | `operator_preferences` | Operator-controlled facts and overrides (UNIQUE on category+key+scope, atomic upsert) |
| 24 | `router_feedback` | Explicit feedback loop signals for Router improvement |
| 25 | `best_practices` | Reusable PROCESS guidance (prose, not code; distinct from `patterns`) |

**Module 7 Phase B (live project registry — added 2026-04-30):**

| # | Table | Purpose |
|---|-------|---------|
| 26 | `projects` | LIVE active-project registry (bucket+slug unique). Distinct from `projects_indexed` (#3, closed/archived with embeddings) per ADR-027. |

### 1.3 Conventions

- **Primary keys:** `UUID` generated via `gen_random_uuid()`. Never integer sequences (not portable across environments).
- **Timestamps:** `TIMESTAMPTZ` (timezone-aware). Operator runs in America/New_York; stored in UTC, rendered in local.
- **Text columns:** `TEXT` always (no `VARCHAR(n)` — Postgres handles both identically, `TEXT` is the idiomatic choice).
- **Tags and arrays:** `TEXT[]` with GIN indexes where queried.
- **Metadata:** `JSONB` for flexible extension without migrations. GIN indexed when accessed by inner keys.
- **Embeddings:** `vector(3072)` from `pgvector` extension. Indexed with HNSW for sub-millisecond cosine similarity at this scale.
- **Soft deletes:** Where recoverability matters, `deleted_at TIMESTAMPTZ` nullable. Hard deletes only for logs past retention.
- **Multi-tenancy hook:** `client_id UUID NULL` on knowledge tables. NULL means operator's own knowledge. Never used in phase 1; present so freelance client-scoped rows never require a migration.
- **Naming:** plural for tables (`lessons`, `tools_catalog`, `routing_logs`) per Postgres convention. Foreign-key columns use singular plus `_id` (`merged_into_id`, `client_id`, `projects_indexed_id`).

### 1.4 Extensions required

```sql
CREATE EXTENSION IF NOT EXISTS vector;       -- pgvector
CREATE EXTENSION IF NOT EXISTS pg_trgm;      -- trigram similarity for fuzzy text match
CREATE EXTENSION IF NOT EXISTS btree_gin;    -- GIN on scalar columns alongside arrays
```

`pgcrypto` is not required because `gen_random_uuid()` is built into PostgreSQL 13+.

---

## 2. Core knowledge tables

### 2.1 `lessons`

Everything the system has learned. Single table with `status` enum covering the full lifecycle from proposal to archive, avoiding parallel `_pending` / `_archive` tables.

```sql
CREATE TYPE lesson_status AS ENUM (
    'pending_review',  -- proposed by reflection worker, not yet approved
    'active',          -- approved, eligible for retrieval
    'archived',        -- low-utility, moved out of default retrieval per §5.5
    'merged_into',     -- superseded by another lesson (see merged_into_id)
    'rejected'         -- operator rejected the proposal
);

CREATE TABLE lessons (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title               TEXT NOT NULL,
    content             TEXT NOT NULL,
    next_time           TEXT,                              -- the "next time X, do Y" clause
    bucket              TEXT NOT NULL,                     -- personal | business | scout | freelance:<client>
    project             TEXT,                              -- optional project association
    category            TEXT NOT NULL,                     -- PLAN | ARCH | COST | INFRA | AI | CODE | DATA | OPS | PROC
    tags                TEXT[] NOT NULL DEFAULT '{}',
    applicable_buckets  TEXT[] NOT NULL DEFAULT '{}',      -- empty means bucket of origin only; ['personal','business'] means cross-bucket lesson
    related_tools       TEXT[] NOT NULL DEFAULT '{}',      -- FK-ish to tools_catalog.name; enables reverse query "which tool has the most lessons"
    metadata            JSONB NOT NULL DEFAULT '{}',       -- { severity: 'critical'|'moderate'|'minor', validated: bool, system: str, references: [...] } per LESSONS_LEARNED §2
    status              lesson_status NOT NULL DEFAULT 'pending_review',
    merged_into_id      UUID REFERENCES lessons(id),       -- set when status='merged_into'

    source              TEXT,                              -- 'reflection_worker' | 'manual' | 'migration_LL-MASTER'
    source_conversation UUID,                              -- optional FK to conversations_indexed
    evidence            JSONB NOT NULL DEFAULT '{}',       -- error messages, code snippets, links

    usage_count         INTEGER NOT NULL DEFAULT 0,
    utility_score       REAL NOT NULL DEFAULT 0,
    last_used_at        TIMESTAMPTZ,

    embedding           vector(3072),
    client_id           UUID,                              -- multi-tenancy hook, phase 2+

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    reviewed_at         TIMESTAMPTZ,
    reviewed_by         TEXT,                              -- 'operator' | 'auto_approved'
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at          TIMESTAMPTZ
);

-- Retrieval index (cosine similarity via HNSW)
CREATE INDEX idx_lessons_embedding_hnsw
    ON lessons USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64)
    WHERE status = 'active' AND deleted_at IS NULL;

-- Filter-first indexes per CONSTITUTION §5.6 rule 26
CREATE INDEX idx_lessons_bucket_status ON lessons(bucket, status) WHERE deleted_at IS NULL;
CREATE INDEX idx_lessons_applicable_buckets ON lessons USING gin(applicable_buckets);
CREATE INDEX idx_lessons_project ON lessons(project) WHERE project IS NOT NULL;
CREATE INDEX idx_lessons_tags ON lessons USING gin(tags);
CREATE INDEX idx_lessons_related_tools ON lessons USING gin(related_tools);
CREATE INDEX idx_lessons_category ON lessons(category);
CREATE INDEX idx_lessons_utility ON lessons(utility_score DESC) WHERE status = 'active';

-- Trigram index for fuzzy title search (UI/review tooling)
CREATE INDEX idx_lessons_title_trgm ON lessons USING gin(title gin_trgm_ops);
```

**Example row:**

```sql
INSERT INTO lessons (title, content, next_time, bucket, category, tags, source) VALUES (
    'Cowork Dispatch times out on LiteLLM calls',
    'The Cowork Dispatch path has a short timeout and cannot wait for Opus/GPT/Gemini calls that run for minutes. Attempts to chain long LiteLLM calls through Dispatch hang silently.',
    'Use Termius SSH + tmux for long-running LLM commands. Dispatch is for quick status checks and file operations only.',
    'business',
    'INFRA',
    ARRAY['cowork', 'litellm', 'tmux', 'timeouts'],
    'migration_LL-MASTER'
);
```

### 2.2 `tools_catalog`

Every reusable tool or skill. Unified table per `CONSTITUTION §5.2` rule 17. `kind` column distinguishes skills (methodologies in `skills/*.md`) from tools (MCP tool wrappers or external functions).

```sql
CREATE TYPE catalog_kind AS ENUM ('skill', 'tool', 'prompt');

CREATE TABLE tools_catalog (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                 TEXT NOT NULL UNIQUE,             -- 'vett' | 'sdd' | 'run_forge_pipeline'
    kind                 catalog_kind NOT NULL,
    description_short    TEXT NOT NULL,                    -- ≤80 chars, lives in L0
    description_full     TEXT NOT NULL,                    -- loaded when detail needed
    applicable_buckets   TEXT[] NOT NULL DEFAULT '{}',
    client_id            UUID,                             -- NULL = global tool; set when tool is client-specific (e.g., custom analyzer for one freelance client)
    skill_file_path      TEXT,                             -- 'skills/vett.md' when kind='skill'
    mcp_tool_name        TEXT,                             -- MCP tool identifier when kind='tool'

    input_signature      JSONB NOT NULL DEFAULT '{}',      -- JSON schema of inputs
    output_signature     JSONB NOT NULL DEFAULT '{}',      -- JSON schema of outputs
    example_invocation   JSONB,                            -- sample call for docs

    usage_count          INTEGER NOT NULL DEFAULT 0,
    cross_bucket_count   INTEGER NOT NULL DEFAULT 0,       -- array_length(distinct buckets used in) from usage_logs
    last_used_at         TIMESTAMPTZ,
    manual_boost         REAL NOT NULL DEFAULT 0,          -- operator thumb-on-scale
    utility_score        REAL NOT NULL DEFAULT 0,          -- recomputed nightly, per §5.2 rule 18

    embedding            vector(3072),
    deprecated           BOOLEAN NOT NULL DEFAULT false,
    deprecation_reason   TEXT,
    archived_at          TIMESTAMPTZ,                      -- set by Dream Engine when unused > 180 days + low utility
    archive_reason       TEXT,                             -- 'unused >180d' | 'superseded:<name>' | 'operator'

    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_tools_embedding_hnsw
    ON tools_catalog USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64)
    WHERE deprecated = false AND archived_at IS NULL;

CREATE INDEX idx_tools_kind ON tools_catalog(kind);
CREATE INDEX idx_tools_buckets ON tools_catalog USING gin(applicable_buckets);
CREATE INDEX idx_tools_utility ON tools_catalog(utility_score DESC) WHERE deprecated = false AND archived_at IS NULL;
```

### 2.3 `projects_indexed`

Historical project index for recall per `CONSTITUTION §5.6` rule 30. Active projects live in git (`buckets/{b}/projects/{p}/README.md`); closed projects get their last state snapshot stored here with embeddings for semantic retrieval.

```sql
CREATE TABLE projects_indexed (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name              TEXT NOT NULL,                     -- 'scout_mtm_sales'
    bucket            TEXT NOT NULL,
    description       TEXT NOT NULL,                     -- what this project was
    outcome           TEXT,                              -- how it ended
    stack             TEXT[] NOT NULL DEFAULT '{}',      -- technologies used
    skills_used       TEXT[] NOT NULL DEFAULT '{}',      -- FK-ish to tools_catalog.name

    started_at        DATE,
    closed_at         DATE,
    closure_reason    TEXT,                              -- 'completed' | 'abandoned' | 'pivoted'

    final_readme      TEXT,                              -- last L2 README content at closure
    key_decisions     JSONB NOT NULL DEFAULT '[]',       -- array of {decision, rationale, date}
    lessons_produced  UUID[] NOT NULL DEFAULT '{}',      -- FK-ish to lessons.id

    embedding         vector(3072),
    client_id         UUID,

    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_projects_embedding_hnsw
    ON projects_indexed USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_projects_bucket ON projects_indexed(bucket);
CREATE INDEX idx_projects_stack ON projects_indexed USING gin(stack);
CREATE INDEX idx_projects_name_trgm ON projects_indexed USING gin(name gin_trgm_ops);
```

### 2.4 `project_state`

Live state of active projects. High churn (TODOs flipping, decisions added). Kept out of git to avoid 100-commits-per-day noise.

```sql
CREATE TABLE project_state (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bucket           TEXT NOT NULL,
    project          TEXT NOT NULL,
    client_id        UUID,                                  -- multi-tenancy hook (Phase 4+); NULL for operator-internal projects
    state_key        TEXT NOT NULL,                         -- 'todo' | 'decision' | 'blocker' | 'focus'
    content          TEXT NOT NULL,
    status           TEXT NOT NULL DEFAULT 'open',          -- 'open' | 'closed' | 'deferred'
    priority         SMALLINT,                              -- 1 (high) to 5 (low), NULL if unprioritized
    related_lessons  UUID[] NOT NULL DEFAULT '{}',          -- structured refs to lessons.id; used by archive_low_utility_lessons()
    metadata         JSONB NOT NULL DEFAULT '{}',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at        TIMESTAMPTZ,

    UNIQUE(bucket, project, state_key, content)             -- prevent exact duplicates
);

CREATE INDEX idx_state_active ON project_state(bucket, project) WHERE status = 'open';
CREATE INDEX idx_state_priority ON project_state(priority, created_at) WHERE status = 'open';
CREATE INDEX idx_state_related_lessons ON project_state USING gin(related_lessons);
CREATE INDEX idx_state_client ON project_state(client_id) WHERE client_id IS NOT NULL;
```

### 2.5 `project_versions`

Snapshots at decision boundaries per `CONSTITUTION §5.5` rule 25. Answers "how did we do it before this architecture change" without git archaeology.

```sql
CREATE TABLE project_versions (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bucket            TEXT NOT NULL,
    project           TEXT NOT NULL,
    client_id         UUID,                                -- inherited from project_state at snapshot time
    snapshot_reason   TEXT NOT NULL,                       -- 'added_module:payments' | 'stack_change_mongo_to_postgres'
    readme_content    TEXT NOT NULL,                       -- full L2 README at snapshot time
    modules_content   JSONB NOT NULL DEFAULT '{}',         -- { module_name: content }
    state_content     JSONB NOT NULL DEFAULT '{}',         -- project_state rows at snapshot time
    triggered_by      TEXT NOT NULL,                       -- 'add_module' | 'change_stack' | 'manual'

    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_versions_project ON project_versions(bucket, project, created_at DESC);
CREATE INDEX idx_versions_client ON project_versions(client_id) WHERE client_id IS NOT NULL;
```

### 2.5.1 `projects` — live active-project registry (Module 7 Phase B, migration 0033)

Live registry of currently-active projects. Distinct from `projects_indexed` (§2.3, which holds closed/archived projects with embeddings for semantic recall) per ADR-027. Written by the `create_project` MCP tool; read by the Router when checking the `unknown_project` hint condition; read by `get_project` / `list_projects` MCP tools.

```sql
CREATE TABLE projects (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bucket       TEXT NOT NULL,
    slug         TEXT NOT NULL,
    name         TEXT NOT NULL,
    description  TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'active',
    stack        TEXT[] NOT NULL DEFAULT '{}',
    skills_used  TEXT[] NOT NULL DEFAULT '{}',
    objective    TEXT,
    client_id    UUID,                                   -- multi-tenancy hook (Phase 4+); NULL for operator-internal projects
    readme_path  TEXT,                                   -- relative to REPO_ROOT (e.g. 'buckets/business/projects/declassified/README.md')
    metadata     JSONB NOT NULL DEFAULT '{}',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX idx_projects_bucket_slug ON projects(bucket, slug);
CREATE INDEX idx_projects_bucket_status ON projects(bucket, status);

-- Trigger filtered by tgrelid because trg_projects_updated_at also exists on projects_indexed.
CREATE TRIGGER trg_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
```

**Conventions:**
- `slug` is normalized client-side by `create_project`: lowercase, non-`[a-z0-9-]` runs collapsed to single hyphens, repeated hyphens collapsed, leading/trailing hyphens stripped. Stored verbatim after normalization.
- `bucket` validation accepts `personal`, `business`, `scout`, or `freelance:<client-name>` (non-empty suffix). The DB does not enforce this — application layer does.
- `status` defaults to `'active'`. Non-default values (`'paused'`, `'closed'`, `'archived'`) are reserved for future close-out flows; M7.B does not write them.
- `readme_path` is set by `create_project` after the README is written to disk (a two-step INSERT then UPDATE within the same transaction). Tests monkeypatch `config_mod.REPO_ROOT` to redirect writes.

**Lifecycle relative to `projects_indexed`:**
A project is created in `projects` (live) and remains there for its working lifetime. When closed, a future tool (`close_project(...)`) copies the row to `projects_indexed` with closure narrative + embedding generation, optionally deleting from `projects`. M7.B did not ship that tool — it is captured as a backlog item.

**Side effects of `create_project`:**
- Inserts an initial `project_state` row (`state_key='status', content='active', status='open'`) — see §2.4.
- Writes a `project_versions` snapshot (`snapshot_reason='project_created', triggered_by='create_project_tool'`) — see §2.5.
- Writes the L2 README to `{REPO_ROOT}/buckets/{bucket}/projects/{slug}/README.md` (filesystem, outside the DB).

### 2.6 `skill_versions`

History of changes to skill files per `CONSTITUTION §2.3` rule 13 (versioning). Enables rollback and "when did we change VETT phase 3" recall.

```sql
CREATE TABLE skill_versions (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_name     TEXT NOT NULL,                       -- FK-ish to tools_catalog.name where kind='skill'
    version        INTEGER NOT NULL,                    -- monotonic per skill_name
    content        TEXT NOT NULL,                       -- full skill file content at this version
    diff_summary   TEXT,                                -- human summary of what changed
    changed_by     TEXT NOT NULL,                       -- 'operator' | 'migration' | MCP tool name
    reason         TEXT,

    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE(skill_name, version)
);

CREATE INDEX idx_skill_versions_lookup ON skill_versions(skill_name, version DESC);
```

---

## 3. Memory and retrieval

### 3.1 `conversations_indexed`

Indexed past conversations for semantic recall. Per `CONSTITUTION §5.5` rule 23, rows older than 90 days have their `content` replaced by a summary while preserving the embedding.

```sql
CREATE TYPE conversation_storage AS ENUM ('full', 'summarized');

CREATE TABLE conversations_indexed (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id TEXT NOT NULL,                       -- client-provided identifier
    client_origin   TEXT NOT NULL,                       -- 'claude.ai' | 'claude_code' | 'telegram' | 'claude_mobile'
    bucket          TEXT,                                -- inferred at ingest
    project         TEXT,
    topic_summary   TEXT NOT NULL,                       -- always present, short
    content         TEXT,                                -- NULL after summarization
    storage         conversation_storage NOT NULL DEFAULT 'full',
    turns_count     INTEGER NOT NULL DEFAULT 0,
    embedding       vector(3072),
    client_id       UUID,                                -- multi-tenancy hook, consistent with lessons/projects/contacts

    session_started_at TIMESTAMPTZ NOT NULL,
    session_ended_at   TIMESTAMPTZ,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    summarized_at      TIMESTAMPTZ                       -- set when storage flipped to 'summarized'
);

CREATE INDEX idx_conv_embedding_hnsw
    ON conversations_indexed USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_conv_bucket_project ON conversations_indexed(bucket, project);
CREATE INDEX idx_conv_date ON conversations_indexed(session_started_at DESC);
```

### 3.2 `cross_pollination_queue`

Pending cross-bucket transfer proposals per `CONSTITUTION §5.4`. Queue entries never expire silently — operator reviews via Telegram `/cross_poll_review`.

```sql
CREATE TYPE cross_poll_status AS ENUM (
    'pending',      -- newly proposed
    'under_review', -- operator acknowledged but not decided
    'applied',      -- idea was implemented in target bucket
    'dismissed',    -- operator rejected
    'merged'        -- merged with another queue entry
);

CREATE TABLE cross_pollination_queue (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    origin_bucket   TEXT NOT NULL,
    origin_project  TEXT,
    origin_lesson   UUID REFERENCES lessons(id),
    target_bucket   TEXT NOT NULL,
    idea            TEXT NOT NULL,
    reasoning       TEXT NOT NULL,
    suggested_application TEXT,                          -- specific "do this in target_bucket" proposal

    status              cross_poll_status NOT NULL DEFAULT 'pending',
    priority            SMALLINT,                              -- 1 (high) to 5 (low), operator-assigned
    confidence_score    REAL,                                  -- reflection worker's self-assessed confidence, 0.0–1.0
    impact_score        REAL,                                  -- estimated value if applied, 0.0–1.0 (feeds Dream Engine sort for morning brief)
    resolution_note     TEXT,                                  -- set when status → applied | dismissed | merged
    merged_into_id      UUID REFERENCES cross_pollination_queue(id),

    proposed_by     TEXT NOT NULL DEFAULT 'reflection_worker',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    reviewed_at     TIMESTAMPTZ,
    resolved_at     TIMESTAMPTZ
);

CREATE INDEX idx_crosspoll_status ON cross_pollination_queue(status, created_at);
CREATE INDEX idx_crosspoll_target ON cross_pollination_queue(target_bucket) WHERE status IN ('pending', 'under_review');
```

---

## 4. Operations and audit

### 4.1 `routing_logs`

Every Router decision, for cost audit and tuning per `CONSTITUTION §2.2` responsibility 5.

```sql
CREATE TABLE routing_logs (
    id                       UUID DEFAULT gen_random_uuid(),
    request_id               TEXT NOT NULL,                    -- correlates client request to server processing; also joins to llm_calls
    client_origin            TEXT NOT NULL,
    message_excerpt          TEXT NOT NULL,                    -- first ~200 chars, for pattern discovery
    classification           JSONB NOT NULL,                   -- {bucket, project, skill, complexity, needs_lessons}
    classification_mode      TEXT NOT NULL DEFAULT 'llm',      -- 'llm' (via LiteLLM alias classifier_default) | 'fallback_rules' (regex over L0)
    layers_loaded            TEXT[] NOT NULL,                  -- ['L0', 'L1', 'L2', 'L4']
    tokens_assembled_total   INTEGER NOT NULL,                 -- total context bundle returned to client
    tokens_per_layer         JSONB NOT NULL DEFAULT '{}',      -- {'L0': 480, 'L1': 1200, ...}
    over_budget_layers       TEXT[] NOT NULL DEFAULT '{}',     -- layers that required summarization before serving
    rag_expected             BOOLEAN NOT NULL,                 -- computed from complexity: HIGH=true, LOW=false, MEDIUM=depends
    rag_executed             BOOLEAN NOT NULL DEFAULT false,   -- did RAG actually fire?
    lessons_returned         INTEGER NOT NULL DEFAULT 0,
    tools_returned           INTEGER NOT NULL DEFAULT 0,
    source_conflicts         JSONB NOT NULL DEFAULT '[]',      -- [{topic, winning_source, losing_sources}] when source priority §2.7 engaged
    user_satisfaction        SMALLINT,                          -- optional 1-5 feedback from client/operator; feeds Dream Engine's classifier-quality tuning per llm_calls.model
    degraded_mode            BOOLEAN NOT NULL DEFAULT false,
    degraded_reason          TEXT,
    latency_ms               INTEGER NOT NULL,

    created_at               TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (id, created_at)                              -- partition key must be part of PK
) PARTITION BY RANGE (created_at);

-- Monthly partitions: Dream Engine creates next month's partition on the 25th of each month;
-- drops partitions older than retention window via DROP TABLE (O(1), no vacuum overhead).
-- Example partition for the first month:
-- CREATE TABLE routing_logs_2026_04 PARTITION OF routing_logs
--     FOR VALUES FROM ('2026-04-01') TO ('2026-05-01');

CREATE INDEX idx_routing_date ON routing_logs(created_at DESC);
CREATE INDEX idx_routing_complexity ON routing_logs USING gin(classification);
CREATE INDEX idx_routing_degraded ON routing_logs(created_at DESC) WHERE degraded_mode = true;
-- Mismatch detection: rag_expected != rag_executed, for audit
CREATE INDEX idx_routing_rag_mismatch ON routing_logs(created_at DESC) WHERE rag_expected <> rag_executed;
```

Retention: 90 days, enforced by Dream Engine via `DROP TABLE routing_logs_YYYY_MM` of partitions older than the window. No DELETE statements — partitioning sidesteps vacuum overhead entirely per Gemini-adv FINDING-002.

### 4.2 `usage_logs`

Tool and skill invocation records. Source of truth for `tools_catalog.usage_count` and `cross_bucket_count`.

```sql
CREATE TABLE usage_logs (
    id           UUID DEFAULT gen_random_uuid(),
    tool_name    TEXT NOT NULL,                         -- FK-ish to tools_catalog.name
    bucket       TEXT,                                  -- bucket in which it was invoked
    project      TEXT,
    invoked_by   TEXT NOT NULL,                         -- 'operator' | 'agent:opus-4.7' | 'worker:reflection'
    success      BOOLEAN NOT NULL DEFAULT true,
    duration_ms  INTEGER,
    metadata     JSONB NOT NULL DEFAULT '{}',

    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Monthly partitions created by Dream Engine on the 25th; retention by DROP TABLE.

CREATE INDEX idx_usage_tool_date ON usage_logs(tool_name, created_at DESC);
CREATE INDEX idx_usage_bucket ON usage_logs(bucket, created_at DESC);
```

Retention: 365 days, enforced by `DROP TABLE usage_logs_YYYY_MM` on old partitions. Aggregate stats rolled up to `tools_catalog` nightly before partition drop.

### 4.3 `llm_calls`

Per-call audit of every LLM invocation in the system. Separates input/output tokens so the operator can see exactly where the monthly budget goes (context assembly vs classification vs reflection vs client reasoning). Joinable to `routing_logs` via `request_id` when applicable.

```sql
CREATE TYPE llm_purpose AS ENUM (
    'classification',      -- Router classify via LiteLLM alias classifier_default
    'embedding_write',     -- OpenAI embedding on insert
    'embedding_query',     -- OpenAI embedding on retrieval
    'client_reasoning',    -- main Opus/Sonnet response (when reported by client)
    'reflection',          -- Reflection worker
    'dream_engine',        -- Nightly consolidation LLM calls (summarization, merge proposals)
    'morning_intel',       -- Morning Intelligence generation
    'second_opinion'       -- Operator-invoked cross-model validation via LiteLLM (see PROJECT_FOUNDATION §2.5)
);

CREATE TABLE llm_calls (
    id                UUID DEFAULT gen_random_uuid(),
    request_id        TEXT,                              -- joins to routing_logs when call happens mid-request; NULL for background workers
    purpose           llm_purpose NOT NULL,
    provider          TEXT NOT NULL,                     -- 'anthropic' | 'openai'
    model             TEXT NOT NULL,                     -- concrete model behind the LiteLLM alias: 'gemini/gemini-2.5-flash' | 'claude-haiku-4-5-20251001' | 'text-embedding-3-large' | 'claude-opus-4-7' | ...
    input_tokens      INTEGER NOT NULL DEFAULT 0,
    output_tokens     INTEGER NOT NULL DEFAULT 0,
    cache_read_tokens INTEGER NOT NULL DEFAULT 0,        -- Anthropic prompt caching hits
    cost_usd          NUMERIC(10, 6) NOT NULL DEFAULT 0,
    latency_ms        INTEGER,
    success           BOOLEAN NOT NULL DEFAULT true,
    error             TEXT,
    client_id         UUID,                              -- billing attribution for freelance per GPT FINDING-007 + Gemini CONCERN-003
    project           TEXT,                              -- 'bucket/project' for margin tracking
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Monthly partitions created by Dream Engine on the 25th.

CREATE INDEX idx_llm_calls_request ON llm_calls(request_id) WHERE request_id IS NOT NULL;
CREATE INDEX idx_llm_calls_purpose_date ON llm_calls(purpose, created_at DESC);
CREATE INDEX idx_llm_calls_model_date ON llm_calls(model, created_at DESC);
CREATE INDEX idx_llm_calls_failed ON llm_calls(created_at DESC) WHERE success = false;
CREATE INDEX idx_llm_calls_client ON llm_calls(client_id, created_at DESC) WHERE client_id IS NOT NULL;
CREATE INDEX idx_llm_calls_project ON llm_calls(project, created_at DESC) WHERE project IS NOT NULL;
```

Retention: 180 days, enforced by `DROP TABLE llm_calls_YYYY_MM` of old partitions. Client/project attribution enables freelance margin calculations without joining to `routing_logs`.

### 4.4 `pending_embeddings`

Degraded-mode queue per `CONSTITUTION §8.43`. When OpenAI embeddings API is unreachable, writes that need an embedding queue here and are flushed when the API returns.

```sql
CREATE TABLE pending_embeddings (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_table  TEXT NOT NULL,                        -- 'lessons' | 'tools_catalog' | 'projects_indexed' | ...
    target_id     UUID NOT NULL,
    source_text   TEXT NOT NULL,                        -- exact text to embed
    attempts      INTEGER NOT NULL DEFAULT 0,
    last_error    TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_attempt  TIMESTAMPTZ,

    UNIQUE(target_table, target_id)
);

CREATE INDEX idx_pending_emb ON pending_embeddings(created_at);
```

### 4.5 `reflection_pending`

Degraded-mode queue per `CONSTITUTION §8.43` for the Reflection worker. When Sonnet 4.6 is unreachable or rate-limited, the worker persists its input payload (transcript reference, routing context, error diagnostics) here. The Dream Engine's nightly pass re-attempts the reflection call against accumulated entries.

```sql
CREATE TABLE reflection_pending (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id       UUID NOT NULL,                       -- FK-ish to conversation_sessions.id
    trigger_event    TEXT NOT NULL,                       -- 'close_session' | 'task_complete' | 'turn_fallback' | 'time_fallback_60min'
    transcript_ref   TEXT NOT NULL,                       -- pointer to stored transcript (conversation_sessions.transcript_path)
    routing_context  JSONB NOT NULL,                      -- classification + layers loaded at time of trigger
    attempts         INTEGER NOT NULL DEFAULT 0,
    last_error       TEXT,
    status           TEXT NOT NULL DEFAULT 'pending',     -- 'pending' | 'processed' | 'abandoned'
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_attempt     TIMESTAMPTZ,
    processed_at     TIMESTAMPTZ
);

CREATE INDEX idx_reflection_pending_status ON reflection_pending(status, created_at) WHERE status = 'pending';
```

Retention: entries with `status='processed'` older than 30 days are deleted by Dream Engine. Entries with `attempts >= 5` transition to `abandoned` and generate a `gotcha` entry for operator review — the cause matters (persistent Sonnet outage? payload corruption? quota?).

### 4.6 `conversation_sessions`

Live session ledger — the model of "what conversation is currently open" that Reflection triggers depend on. Per GPT audit FINDING-008, idle-based and turn-based reflection cannot work without a first-class session entity.

```sql
CREATE TABLE conversation_sessions (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_origin    TEXT NOT NULL,                       -- 'claude_web' | 'claude_code' | 'claude_mobile' | 'telegram' | 'api'
    operator_id      TEXT,                                -- operator identifier if multi-operator; default 'alfredo' in Phase 1
    client_id        UUID,                                -- populated when session is scoped to a freelance client
    bucket           TEXT,                                -- last known classified bucket
    project          TEXT,                                -- last known classified project
    started_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at        TIMESTAMPTZ,                         -- set on explicit close or idle detection
    close_reason     TEXT,                                -- 'explicit' | 'idle_10min' | 'reflection_fallback_60min' | 'operator_forced'
    turn_count       INTEGER NOT NULL DEFAULT 0,
    transcript_path  TEXT,                                -- /home/operator/pretel-os-data/transcripts/{session_id}.jsonl
    reflection_fired BOOLEAN NOT NULL DEFAULT false,
    metadata         JSONB NOT NULL DEFAULT '{}'
);

CREATE INDEX idx_sessions_open ON conversation_sessions(last_seen_at DESC) WHERE closed_at IS NULL;
CREATE INDEX idx_sessions_client_origin ON conversation_sessions(client_origin, started_at DESC);
CREATE INDEX idx_sessions_needs_reflection ON conversation_sessions(closed_at) WHERE closed_at IS NOT NULL AND reflection_fired = false;
```

Behavior:
- Each MCP `get_context()` call either attaches to an open session (by client-provided session token) or creates a new one.
- Every call updates `last_seen_at` and increments `turn_count`.
- The Dream Engine's idle-check pass runs every 5 minutes: any open session with `last_seen_at < now() - interval '10 minutes'` is closed with `close_reason='idle_10min'` and queued for reflection.
- An open session that exceeds 60 minutes of lifespan fires a mid-session reflection (does not close), setting `reflection_fired=true` and creating a new sub-session for continued turns.
- Transcripts are append-only JSONL files on the Vivobook, referenced by `transcript_path`. The DB does not store transcript text — only pointers.
- Retention: closed sessions older than 180 days have their `transcript_path` file compressed and `reflection_fired` flag locked. Content stays queryable via `conversations_indexed` after the Auto-index worker processes them.

---

## 5. Extended knowledge (Phase 2+)

These tables are defined now for schema completeness but are populated only when the corresponding need emerges. No `Module 2: data_layer` task is blocked on them.

### 5.1 `patterns`

Reusable code snippets, templates, UI components.

```sql
CREATE TABLE patterns (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name           TEXT NOT NULL,
    description    TEXT NOT NULL,
    language       TEXT,                                -- 'python' | 'javascript' | 'sql' | 'n8n-json'
    code           TEXT NOT NULL,
    use_case       TEXT NOT NULL,
    applicable_buckets TEXT[] NOT NULL DEFAULT '{}',
    client_id      UUID,                                -- NULL = operator's general pattern; set when client-specific
    tags           TEXT[] NOT NULL DEFAULT '{}',
    embedding      vector(3072),
    usage_count    INTEGER NOT NULL DEFAULT 0,
    version          INTEGER NOT NULL DEFAULT 1,        -- bumped on meaningful change
    previous_content TEXT,                              -- prior version's code, enables single-step rollback without a full versions table
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_patterns_embedding_hnsw ON patterns USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_patterns_tags ON patterns USING gin(tags);
CREATE INDEX idx_patterns_client ON patterns(client_id) WHERE client_id IS NOT NULL;
```

### 5.2 `decisions`

ADR-style architectural decisions tied to projects. Separate from `project_versions` (which snapshots files) — this records the reasoning.

```sql
CREATE TABLE decisions (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bucket               TEXT NOT NULL,
    project              TEXT NOT NULL,                   -- active project name (git-resident)
    projects_indexed_id  UUID REFERENCES projects_indexed(id),  -- populated when the project closes and moves to projects_indexed
    client_id            UUID,                             -- inherited from project_state when project is client-scoped
    title                TEXT NOT NULL,
    context              TEXT NOT NULL,
    decision             TEXT NOT NULL,
    consequences         TEXT NOT NULL,
    alternatives         TEXT,
    status               TEXT NOT NULL DEFAULT 'active',  -- 'active' | 'superseded'
    superseded_by_id     UUID REFERENCES decisions(id),
    embedding            vector(3072),
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_decisions_project ON decisions(bucket, project);
CREATE INDEX idx_decisions_indexed_project ON decisions(projects_indexed_id) WHERE projects_indexed_id IS NOT NULL;
CREATE INDEX idx_decisions_embedding_hnsw ON decisions USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_decisions_client ON decisions(client_id) WHERE client_id IS NOT NULL;
```

### 5.2.1 Amendment (M0.X, migration 0028)

Seven columns added to support the typed-decision capture model that ADR-021 introduced:

| Column | Type | Default | Purpose |
|---|---|---|---|
| `scope` | `text NOT NULL` | `'operational'` | CHECK ∈ {`architectural`, `process`, `product`, `operational`}. Distinguishes ADR-level from day-to-day. Default chosen for legacy rows; formal ADRs MUST set `'architectural'` explicitly. |
| `applicable_buckets` | `text[] NOT NULL` | `'{}'` | Cross-bucket scope. GIN-indexed. |
| `decided_by` | `text NOT NULL` | `'operator'` | Provenance. |
| `tags` | `text[] NOT NULL` | `'{}'` | Free-form filter tags. GIN-indexed. |
| `severity` | `text` | `'normal'` | CHECK ∈ {`critical`, `normal`, `minor`}. Distinguishes load-bearing decisions from process tweaks. |
| `adr_number` | `integer` | `NULL` | UNIQUE constraint allows NULL for non-formal decisions (multiple NULLs OK in PG). |
| `derived_from_lessons` | `uuid[]` | `'{}'` | Provenance when crystallized from lessons (reflection worker pathway). |

```sql
ALTER TABLE decisions ADD COLUMN scope                TEXT    NOT NULL DEFAULT 'operational';
ALTER TABLE decisions ADD COLUMN applicable_buckets   TEXT[]  NOT NULL DEFAULT '{}';
ALTER TABLE decisions ADD COLUMN decided_by           TEXT    NOT NULL DEFAULT 'operator';
ALTER TABLE decisions ADD COLUMN tags                 TEXT[]  NOT NULL DEFAULT '{}';
ALTER TABLE decisions ADD COLUMN severity             TEXT             DEFAULT 'normal';
ALTER TABLE decisions ADD COLUMN adr_number           INTEGER UNIQUE;
ALTER TABLE decisions ADD COLUMN derived_from_lessons UUID[]           DEFAULT '{}';

ALTER TABLE decisions ADD CONSTRAINT decisions_scope_check
    CHECK (scope IN ('architectural','process','product','operational'));
ALTER TABLE decisions ADD CONSTRAINT decisions_severity_check
    CHECK (severity IN ('critical','normal','minor'));

CREATE INDEX idx_decisions_scope_status        ON decisions(scope, status);
CREATE INDEX idx_decisions_applicable_buckets  ON decisions USING gin(applicable_buckets);
CREATE INDEX idx_decisions_tags                ON decisions USING gin(tags);
```

**Note on `project`:** Per Phase C smoke test discovery (task `80462622`), the `project` column is `NOT NULL` in production (and shown as such in the §5.2 SQL block above). Some early spec drafts called it Optional; production DDL is the source of truth.

ADRs 020–024 seeded by `migrations/0029_data_migration_lessons_split.sql`. Full post-amendment schema dump: `migrations/audit/0029_post_state.md`.

### 5.3 `gotchas`

Anti-patterns and traps.

```sql
CREATE TABLE gotchas (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title          TEXT NOT NULL,
    trigger_context TEXT NOT NULL,                      -- "when you do X with Y"
    what_goes_wrong TEXT NOT NULL,
    workaround     TEXT,
    severity       SMALLINT NOT NULL DEFAULT 3,         -- 1 (fatal) to 5 (annoying)
    applicable_buckets TEXT[] NOT NULL DEFAULT '{}',
    tags           TEXT[] NOT NULL DEFAULT '{}',
    embedding      vector(3072),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_gotchas_embedding_hnsw ON gotchas USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_gotchas_severity ON gotchas(severity);
```

### 5.4 `contacts`

People: clients, vendors, collaborators, subject-matter experts.

```sql
CREATE TABLE contacts (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name           TEXT NOT NULL,
    role           TEXT,
    company        TEXT,
    relationship   TEXT,                                -- 'freelance_client' | 'vendor' | 'collaborator' | 'advisor'
    email          TEXT,
    phone          TEXT,
    notes          TEXT,
    associated_buckets TEXT[] NOT NULL DEFAULT '{}',
    associated_projects TEXT[] NOT NULL DEFAULT '{}',
    metadata       JSONB NOT NULL DEFAULT '{}',         -- LinkedIn, Twitter, preferred channel, timezone, etc.
    embedding      vector(3072),
    last_contact_at TIMESTAMPTZ,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at     TIMESTAMPTZ
);

CREATE INDEX idx_contacts_relationship ON contacts(relationship) WHERE deleted_at IS NULL;
CREATE INDEX idx_contacts_projects ON contacts USING gin(associated_projects);
CREATE INDEX idx_contacts_name_trgm ON contacts USING gin(name gin_trgm_ops);
```

### 5.5 `ideas`

Unprocessed ideas, backlog for future exploration. Operator dumps them via Telegram `/idea <text>`; Dream Engine groups and ranks.

```sql
CREATE TABLE ideas (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    summary        TEXT NOT NULL,
    full_text      TEXT,
    bucket_hint    TEXT,                                -- operator's guess at bucket
    client_id      UUID,                                -- NULL = operator's idea; set when idea is for a specific client
    category       TEXT,                                -- 'product' | 'workflow' | 'skill' | 'content' | 'freelance_offering'
    effort_estimate TEXT,                               -- 'trivial' | 'hours' | 'days' | 'weeks'
    status             TEXT NOT NULL DEFAULT 'new',         -- 'new' | 'explored' | 'promoted' | 'dismissed'
    promoted_to        TEXT,                                -- 'project:name' | 'lesson:uuid' | 'pattern:uuid'
    related_lessons    UUID[] NOT NULL DEFAULT '{}',        -- lessons that sparked this idea or would inform it
    related_tools      TEXT[] NOT NULL DEFAULT '{}',        -- tools the idea builds on (FK-ish to tools_catalog.name)
    related_projects   TEXT[] NOT NULL DEFAULT '{}',        -- projects the idea relates to, format 'bucket/project'
    embedding          vector(3072),
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    reviewed_at        TIMESTAMPTZ
);

CREATE INDEX idx_ideas_status ON ideas(status, created_at DESC);
CREATE INDEX idx_ideas_embedding_hnsw ON ideas USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_ideas_related_lessons ON ideas USING gin(related_lessons);
CREATE INDEX idx_ideas_related_tools ON ideas USING gin(related_tools);
CREATE INDEX idx_ideas_related_projects ON ideas USING gin(related_projects);
CREATE INDEX idx_ideas_client ON ideas(client_id) WHERE client_id IS NOT NULL;
```

### 5.6 `control_registry`

Tracks manual operational controls that the constitution requires the operator to run on a cadence (Scout audits, restore drills, key rotation, quarterly price verification, etc.). Per GPT audit FINDING-012: manual controls are acceptable if they're tracked as weak controls, not invisible. The Dream Engine checks this table nightly and alerts on overdue items via Telegram.

```sql
CREATE TABLE control_registry (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    control_name      TEXT NOT NULL UNIQUE,                  -- 'scout_audit' | 'restore_drill' | 'key_rotation_anthropic' | ...
    description       TEXT NOT NULL,
    cadence_days      INTEGER NOT NULL,                      -- 90 for quarterly, 180 for key rotation, etc.
    owner             TEXT NOT NULL DEFAULT 'operator',
    evidence_required TEXT NOT NULL,                         -- 'screenshot' | 'git commit' | 'log entry' | 'operator attestation'
    last_completed_at TIMESTAMPTZ,
    last_evidence     TEXT,                                  -- link, path, or note pointing to proof
    next_due_at       TIMESTAMPTZ GENERATED ALWAYS AS (last_completed_at + (cadence_days || ' days')::interval) STORED,
    alert_sent_at     TIMESTAMPTZ,                           -- to prevent alert spam; reset when control is completed
    active            BOOLEAN NOT NULL DEFAULT true,
    notes             TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_control_overdue ON control_registry(next_due_at) WHERE active = true;

-- Seed rows inserted during Module 2 migration:
-- ('scout_audit', 'Review Scout bucket for leaked employer data', 90, 'operator', 'operator attestation + git log of any corrections', ...)
-- ('restore_drill', 'Restore most recent backup to scratch DB, validate pg_restore', 90, 'operator', 'log of successful restore', ...)
-- ('key_rotation_anthropic', 'Rotate ANTHROPIC_API_KEY', 180, 'operator', 'env file diff + smoke test log', ...)
-- ('key_rotation_openai', 'Rotate OPENAI_API_KEY', 180, 'operator', 'env file diff + smoke test log', ...)
-- ('pricing_verification', 'Re-verify Anthropic + OpenAI pricing pages vs INTEGRATIONS §2.6 and §3.6', 90, 'operator', 'screenshot or updated doc', ...)
-- ('uptime_review', 'Review 30-day uptime from UptimeRobot, reconcile with SLO target', 30, 'operator', 'dashboard screenshot', ...)
```

### 5.7 `tasks` (M0.X Phase A)

Pending and in-progress work items. No embedding — structured query only. Self-referential FK on `blocked_by` for dependency chains.

```sql
CREATE TABLE tasks (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title             TEXT NOT NULL,
    description       TEXT,
    bucket            TEXT NOT NULL,
    project           TEXT,
    module            TEXT,                                    -- 'M0.X', 'M4', etc.
    status            TEXT NOT NULL DEFAULT 'open',            -- open | in_progress | blocked | done | cancelled
    priority          TEXT      DEFAULT 'normal',              -- urgent | high | normal | low
    blocked_by        UUID REFERENCES tasks(id) ON DELETE SET NULL,
    trigger_phase     TEXT,                                    -- 'Phase D', 'before-M5', etc.
    source            TEXT NOT NULL,                           -- operator | claude | reflection_worker | migration
    estimated_minutes INTEGER,
    github_issue_url  TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    done_at           TIMESTAMPTZ,
    metadata          JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_tasks_bucket_status   ON tasks(bucket, status);
CREATE INDEX idx_tasks_module          ON tasks(module) WHERE module IS NOT NULL;
CREATE INDEX idx_tasks_open_by_phase   ON tasks(trigger_phase) WHERE status IN ('open','blocked');

-- updated_at maintained by trg_set_updated_at_tasks (see §6.1).
```

**Lifecycle:** `open → in_progress → done` is the happy path; `open → blocked` when a dependency exists; reopen via `task_reopen` MCP tool, which clears `done_at` and appends an entry to `metadata.reopened_history` JSON array. Status transitions are enforced by `task_*` MCP tools — no DB-level state machine.

**Not loaded into context** per `layer_loader_contract.md §4` — surfaced only via `task_list` tool when operator asks.

**Migration:** `migrations/0024_tasks.sql`. **Spec:** `specs/module-0x-knowledge-architecture/spec.md §5.1`. **Full schema dump:** `migrations/audit/0029_post_state.md`.

### 5.8 `operator_preferences` (M0.X Phase A)

Operator-controlled facts and overrides. Atomic upsert via `UNIQUE(category, key, scope)`. No embedding — direct lookup.

```sql
CREATE TABLE operator_preferences (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category   TEXT NOT NULL,                                  -- communication | tooling | workflow | identity | language | schedule
    key        TEXT NOT NULL,
    value      TEXT NOT NULL,
    scope      TEXT NOT NULL DEFAULT 'global',                 -- 'global' or 'bucket:<name>' (e.g. 'bucket:business')
    active     BOOLEAN NOT NULL DEFAULT true,
    source     TEXT NOT NULL,                                  -- operator_explicit | inferred | migration
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata   JSONB DEFAULT '{}'::jsonb,
    UNIQUE(category, key, scope)
);

CREATE INDEX idx_preferences_category_active ON operator_preferences(category) WHERE active;
CREATE INDEX idx_preferences_scope_active    ON operator_preferences(scope) WHERE active;

-- updated_at maintained by trg_set_updated_at_operator_preferences (see §6.1).
```

**Soft-delete semantics:** `preference_unset` MCP tool sets `active = false` rather than `DELETE` — the value is preserved for audit and possible reactivation.

**Layer load:** L0 reads rows where `scope = 'global'`; L1 reads rows where `scope LIKE 'bucket:<bucket>%'`. See `layer_loader_contract.md §3.1, §3.2`.

**Migration:** `migrations/0025_operator_preferences.sql`. **Spec:** `specs/module-0x-knowledge-architecture/spec.md §5.3`. **Full schema dump:** `migrations/audit/0029_post_state.md`.

### 5.9 `router_feedback` (M0.X Phase A)

Explicit feedback loop signals from operator to Router. Consumed by Module 6 reflection worker to derive lessons or `operator_preferences` updates. Status workflow: `pending → reviewed → applied | dismissed`.

```sql
CREATE TABLE router_feedback (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id          TEXT,                                  -- soft reference to routing_logs.request_id (see note)
    feedback_type       TEXT NOT NULL,                         -- missing_context | wrong_bucket | wrong_complexity |
                                                               -- irrelevant_lessons | too_much_context | low_quality_response
    operator_note       TEXT,
    proposed_correction JSONB,
    status              TEXT NOT NULL DEFAULT 'pending',       -- pending | reviewed | applied | dismissed
    reviewed_by         TEXT,
    applied_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_router_feedback_request ON router_feedback(request_id) WHERE request_id IS NOT NULL;
CREATE INDEX idx_router_feedback_status  ON router_feedback(status);
CREATE INDEX idx_router_feedback_type    ON router_feedback(feedback_type) WHERE status = 'pending';
```

**Note on `request_id` (no FK):** `request_id` is `TEXT` with no foreign key. `routing_logs` is monthly-partitioned by `created_at`, and any FK from a non-partitioned table to a partitioned one requires a compound key including the partition column. The cost (compound FK + retention coupling) is not justified for a soft-correlation field. Rationale: `specs/module-0x-knowledge-architecture/spec.md §5.4`.

**Not loaded into context** per `layer_loader_contract.md §4`.

**Migration:** `migrations/0026_router_feedback.sql`. **Full schema dump:** `migrations/audit/0029_post_state.md`.

### 5.10 `best_practices` (M0.X Phase A)

Reusable PROCESS guidance ("always X when Y", narrative form). Distinct from `patterns` (§5.1) which holds CODE snippets — see ADR-023 for the new-table-vs-extend-patterns decision.

```sql
CREATE TABLE best_practices (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title                TEXT NOT NULL,
    guidance             TEXT NOT NULL,
    rationale            TEXT,
    domain               TEXT NOT NULL,                        -- process | convention | workflow | communication
    scope                TEXT NOT NULL DEFAULT 'global',       -- 'global' | 'bucket:<bucket>' | 'project:<bucket>/<project>'
    applicable_buckets   TEXT[] NOT NULL DEFAULT '{}',
    tags                 TEXT[] NOT NULL DEFAULT '{}',
    active               BOOLEAN NOT NULL DEFAULT true,
    source               TEXT NOT NULL,                        -- operator | derived_from_lessons | migration
    derived_from_lessons UUID[]   DEFAULT '{}',
    previous_guidance    TEXT,                                 -- single-step rollback (see lifecycle below)
    previous_rationale   TEXT,
    superseded_by        UUID REFERENCES best_practices(id),
    embedding            vector(3072),
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_best_practices_applicable_buckets ON best_practices USING gin(applicable_buckets);
CREATE INDEX idx_best_practices_domain             ON best_practices(domain) WHERE active;
CREATE INDEX idx_best_practices_scope              ON best_practices(scope) WHERE active;
CREATE INDEX idx_best_practices_superseded         ON best_practices(superseded_by) WHERE superseded_by IS NOT NULL;
CREATE INDEX idx_best_practices_tags               ON best_practices USING gin(tags);

-- HNSW index INTENTIONALLY OMITTED per ADR-024:
--   pgvector 0.6.0 caps HNSW at ≤2000 dims; embedding is vector(3072).
--   At <5K rows, sequential scan latency is 10–50 ms. Re-add when
--   pgvector ≥0.7 supports 3072-dim HNSW or volume crosses ~50K rows.

-- updated_at maintained by trg_set_updated_at_best_practices (see §6.1).
```

**Single-step rollback semantics:** the `best_practice_record` MCP tool, on UPDATE, copies the current `guidance` / `rationale` into `previous_guidance` / `previous_rationale` BEFORE overwriting. The `best_practice_rollback` tool restores from those fields. Only ONE step of history is preserved — multi-step versioning would require a separate history table.

**Supersession chain:** the `superseded_by` self-ref FK plus the `active` flag together model "this practice replaced that one and the old one is no longer applied."

**Layer load:** L2 reads `WHERE active AND scope = 'project:<bucket>/<project>'`; L4 reads `WHERE active AND (domain = $classifier_domain OR $bucket = ANY(applicable_buckets))`. See `layer_loader_contract.md §3.3, §3.5`.

**Known workaround — `pending_embeddings` queueing:** As of `module-0x-complete` tag, this table has NO `notify_missing_embedding` trigger. The migration 0019 trigger covers nine tables but does not yet cover `best_practices`. The `best_practice_record` MCP tool manually inserts into `pending_embeddings` on embedding failure, using `ON CONFLICT (target_id, target_table) DO NOTHING` to remain idempotent. **Migration 0030** (task `92cac1b3`) will replace the manual logic with a trigger consistent with §6.2 patterns.

**Migration:** `migrations/0027_best_practices.sql`. **Spec:** `specs/module-0x-knowledge-architecture/spec.md §5.5`. **Full schema dump:** `migrations/audit/0029_post_state.md`.

---

## 6. Functions and triggers

### 6.1 `updated_at` auto-maintenance

Standard trigger applied to every table with an `updated_at` column.

```sql
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_lessons_updated_at BEFORE UPDATE ON lessons
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_tools_updated_at BEFORE UPDATE ON tools_catalog
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_projects_updated_at BEFORE UPDATE ON projects_indexed
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_state_updated_at BEFORE UPDATE ON project_state
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_patterns_updated_at BEFORE UPDATE ON patterns
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_contacts_updated_at BEFORE UPDATE ON contacts
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
```

### 6.2 Auto-index on save (Worker 4 per `CONSTITUTION §2.6`)

When a row is inserted without an embedding, queue it for embedding computation. The Auto-index worker (Python listener on `pg_notify`, or `pg_cron` running every minute) processes the queue.

```sql
CREATE OR REPLACE FUNCTION notify_missing_embedding()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    source_text TEXT;
BEGIN
    IF NEW.embedding IS NULL THEN
        -- Derive source text per table
        source_text := CASE TG_TABLE_NAME
            WHEN 'lessons' THEN NEW.title || E'\n\n' || NEW.content
            WHEN 'tools_catalog' THEN NEW.name || E'\n' || NEW.description_full
            WHEN 'projects_indexed' THEN NEW.name || E'\n' || NEW.description
            WHEN 'conversations_indexed' THEN COALESCE(NEW.content, NEW.topic_summary)
            WHEN 'patterns' THEN NEW.name || E'\n' || NEW.description || E'\n' || NEW.use_case
            WHEN 'decisions' THEN NEW.title || E'\n' || NEW.context || E'\n' || NEW.decision
            WHEN 'gotchas' THEN NEW.title || E'\n' || NEW.trigger_context || E'\n' || NEW.what_goes_wrong
            WHEN 'contacts' THEN NEW.name || ' ' || COALESCE(NEW.role, '') || ' ' || COALESCE(NEW.company, '')
            WHEN 'ideas' THEN NEW.summary || E'\n' || COALESCE(NEW.full_text, '')
            ELSE NULL
        END;

        IF source_text IS NOT NULL THEN
            INSERT INTO pending_embeddings (target_table, target_id, source_text)
            VALUES (TG_TABLE_NAME, NEW.id, source_text)
            ON CONFLICT (target_table, target_id) DO UPDATE
                SET source_text = EXCLUDED.source_text,
                    attempts = 0,
                    last_error = NULL;

            PERFORM pg_notify('embedding_queue', TG_TABLE_NAME || ':' || NEW.id::text);
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_lessons_emb AFTER INSERT ON lessons
    FOR EACH ROW EXECUTE FUNCTION notify_missing_embedding();
CREATE TRIGGER trg_tools_emb AFTER INSERT ON tools_catalog
    FOR EACH ROW EXECUTE FUNCTION notify_missing_embedding();
CREATE TRIGGER trg_projects_emb AFTER INSERT ON projects_indexed
    FOR EACH ROW EXECUTE FUNCTION notify_missing_embedding();
CREATE TRIGGER trg_conv_emb AFTER INSERT ON conversations_indexed
    FOR EACH ROW EXECUTE FUNCTION notify_missing_embedding();
CREATE TRIGGER trg_patterns_emb AFTER INSERT ON patterns
    FOR EACH ROW EXECUTE FUNCTION notify_missing_embedding();
CREATE TRIGGER trg_decisions_emb AFTER INSERT ON decisions
    FOR EACH ROW EXECUTE FUNCTION notify_missing_embedding();
CREATE TRIGGER trg_gotchas_emb AFTER INSERT ON gotchas
    FOR EACH ROW EXECUTE FUNCTION notify_missing_embedding();
CREATE TRIGGER trg_contacts_emb AFTER INSERT ON contacts
    FOR EACH ROW EXECUTE FUNCTION notify_missing_embedding();
CREATE TRIGGER trg_ideas_emb AFTER INSERT ON ideas
    FOR EACH ROW EXECUTE FUNCTION notify_missing_embedding();
```

### 6.3 Duplicate detection (pre-save)

Called by the MCP `save_lesson` tool before insert. Returns any existing lesson above similarity threshold.

```sql
CREATE OR REPLACE FUNCTION find_duplicate_lesson(
    p_content TEXT,
    p_embedding vector(3072),
    p_bucket TEXT,
    p_threshold REAL DEFAULT 0.92
)
RETURNS TABLE (
    id UUID,
    title TEXT,
    similarity REAL
) LANGUAGE sql STABLE AS $$
    SELECT
        l.id,
        l.title,
        (1 - (l.embedding <=> p_embedding))::REAL AS similarity
    FROM lessons l
    WHERE l.status = 'active'
      AND l.bucket = p_bucket
      AND l.embedding IS NOT NULL
      AND (1 - (l.embedding <=> p_embedding)) >= p_threshold
    ORDER BY l.embedding <=> p_embedding
    LIMIT 5;
$$;
```

### 6.4 Utility score recomputation (Dream Engine)

Called nightly. Implements the formula in `CONSTITUTION §5.2` rule 18.

```sql
CREATE OR REPLACE FUNCTION recompute_utility_scores()
RETURNS void LANGUAGE plpgsql AS $$
BEGIN
    UPDATE tools_catalog tc
    SET utility_score =
        ln(1 + tc.usage_count)
        + CASE
            WHEN tc.last_used_at IS NULL THEN 0
            WHEN tc.last_used_at > now() - interval '7 days' THEN 2.0
            WHEN tc.last_used_at > now() - interval '30 days' THEN 1.0
            WHEN tc.last_used_at > now() - interval '90 days' THEN 0.5
            ELSE 0
          END
        + 2 * tc.cross_bucket_count
        + tc.manual_boost,
    updated_at = now()
    WHERE tc.deprecated = false;

    UPDATE lessons l
    SET utility_score =
        ln(1 + l.usage_count)
        + CASE
            WHEN l.last_used_at IS NULL THEN 0
            WHEN l.last_used_at > now() - interval '30 days' THEN 1.5
            WHEN l.last_used_at > now() - interval '90 days' THEN 0.5
            ELSE 0
          END,
    updated_at = now()
    WHERE l.status = 'active';
END;
$$;
```

### 6.5 Archival pass (Dream Engine)

Archives low-utility lessons per `CONSTITUTION §5.5` rule 22.

```sql
CREATE OR REPLACE FUNCTION archive_low_utility_lessons()
RETURNS INTEGER LANGUAGE plpgsql AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    UPDATE lessons
    SET status = 'archived',
        updated_at = now()
    WHERE status = 'active'
      AND usage_count = 0
      AND created_at < now() - interval '180 days'
      AND utility_score < 0.5
      AND NOT EXISTS (
          SELECT 1 FROM project_state ps
          WHERE lessons.id = ANY(ps.related_lessons)
            AND ps.status = 'open'
      );

    GET DIAGNOSTICS archived_count = ROW_COUNT;
    RETURN archived_count;
END;
$$;
```

### 6.6 Conversation summarization (Dream Engine)

Replaces raw content of old conversations with summary, preserving embedding per `CONSTITUTION §5.5` rule 23. The actual summary is produced by an LLM call from the Dream Engine Python code; this function is invoked with the summary already prepared.

```sql
CREATE OR REPLACE FUNCTION summarize_old_conversation(
    p_id UUID,
    p_summary TEXT
)
RETURNS void LANGUAGE sql AS $$
    UPDATE conversations_indexed
    SET content = NULL,
        topic_summary = p_summary,
        storage = 'summarized',
        summarized_at = now()
    WHERE id = p_id
      AND storage = 'full'
      AND session_started_at < now() - interval '90 days';
$$;
```

### 6.7 Scout safety trigger (defense in depth)

Database-level enforcement of `CONSTITUTION §3` rules 1–3. The MCP tool `save_lesson` already filters Scout content on insert, but the DB trigger is a second line of defense for any future code path or direct SQL (e.g., an operator making a mistake) that tries to insert Scout-labeled content.

The `scout_denylist` table is the source of regex patterns. Only the operator edits it (no MCP tool exposes writes to it). The trigger fires on every INSERT or UPDATE to `lessons` where `bucket='scout'`.

```sql
CREATE TABLE scout_denylist (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern    TEXT NOT NULL UNIQUE,                    -- POSIX regex, case-insensitive match
    reason     TEXT NOT NULL,
    added_by   TEXT NOT NULL DEFAULT 'operator',
    added_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE OR REPLACE FUNCTION scout_safety_check()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    matched_pattern TEXT;
BEGIN
    IF NEW.bucket = 'scout' THEN
        SELECT pattern INTO matched_pattern
        FROM scout_denylist
        WHERE (COALESCE(NEW.title, '') || ' ' || COALESCE(NEW.content, '')) ~* pattern
        LIMIT 1;

        IF matched_pattern IS NOT NULL THEN
            RAISE EXCEPTION 'Scout denylist violation: pattern "%" matched. Reformulate abstractly per CONSTITUTION §3.', matched_pattern
                USING HINT = 'This is a DB-level guard; the MCP tool should have filtered earlier.';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_scout_safety_lessons
    BEFORE INSERT OR UPDATE ON lessons
    FOR EACH ROW EXECUTE FUNCTION scout_safety_check();
```

Seed entries for `scout_denylist` are operator-specific and not committed to this repo. They live in an operator-private provisioning script.

### 6.8 Tool archival pass (Dream Engine)

Archives tools that have gone dormant (zombie detection). Called nightly.

```sql
CREATE OR REPLACE FUNCTION archive_dormant_tools()
RETURNS INTEGER LANGUAGE plpgsql AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    UPDATE tools_catalog
    SET archived_at = now(),
        archive_reason = 'unused >180d with utility_score < 0.5',
        updated_at = now()
    WHERE deprecated = false
      AND archived_at IS NULL
      AND (last_used_at IS NULL OR last_used_at < now() - interval '180 days')
      AND utility_score < 0.5;

    GET DIAGNOSTICS archived_count = ROW_COUNT;
    RETURN archived_count;
END;
$$;
```

Archived tools remain queryable with explicit `include_archived=true` on `recommend_tools()`. The operator can unarchive manually by clearing `archived_at`.

---

## 7. Views

Convenience views for common queries and for the Reflection worker.

```sql
-- Active lessons eligible for retrieval
CREATE VIEW v_active_lessons AS
SELECT id, title, content, next_time, bucket, project, category, tags,
       usage_count, utility_score, last_used_at, embedding
FROM lessons
WHERE status = 'active' AND deleted_at IS NULL;

-- High-utility tools for recommendation
CREATE VIEW v_recommendable_tools AS
SELECT id, name, kind, description_short, description_full, applicable_buckets,
       usage_count, utility_score, last_used_at, embedding
FROM tools_catalog
WHERE deprecated = false;

-- Open project state for daily review
CREATE VIEW v_open_state AS
SELECT bucket, project, state_key, content, priority, created_at
FROM project_state
WHERE status = 'open'
ORDER BY priority NULLS LAST, created_at DESC;

-- Pending cross-pollination by target bucket
CREATE VIEW v_crosspoll_inbox AS
SELECT target_bucket, count(*) AS pending_count,
       min(created_at) AS oldest,
       max(created_at) AS newest
FROM cross_pollination_queue
WHERE status = 'pending'
GROUP BY target_bucket;

-- Reverse index: which tools have the most lessons about them (zombie detection for tools with many gotchas)
CREATE VIEW v_tool_lessons AS
SELECT
    unnest_tool AS tool_name,
    count(*) AS lesson_count,
    array_agg(l.id ORDER BY l.created_at DESC) AS lesson_ids,
    avg(l.utility_score) AS avg_lesson_utility
FROM lessons l, unnest(l.related_tools) AS unnest_tool
WHERE l.status = 'active' AND l.deleted_at IS NULL
GROUP BY unnest_tool
ORDER BY lesson_count DESC;

-- Daily cost roll-up by purpose for budget tracking
CREATE VIEW v_daily_cost_by_purpose AS
SELECT
    date_trunc('day', created_at)::date AS day,
    purpose,
    model,
    sum(cost_usd) AS cost_usd,
    sum(input_tokens) AS input_tokens,
    sum(output_tokens) AS output_tokens,
    count(*) AS call_count
FROM llm_calls
WHERE created_at > now() - interval '60 days'
GROUP BY 1, 2, 3
ORDER BY 1 DESC, 4 DESC;
```

---

## 8. Indexes summary

| Table | HNSW vector | Filter indexes |
|-------|:-:|-------|
| `lessons` | ✓ (partial, status='active') | bucket+status, applicable_buckets(GIN), project, tags(GIN), related_tools(GIN), category, utility, title(trgm) |
| `tools_catalog` | ✓ (partial, active + non-archived) | kind, buckets(GIN), utility, client(partial) |
| `projects_indexed` | ✓ | bucket, stack(GIN), name(trgm) |
| `project_state` | — | bucket+project(partial open), priority, related_lessons(GIN), client(partial) |
| `project_versions` | — | project+created_at DESC, client(partial) |
| `skill_versions` | — | skill_name+version DESC |
| `conversations_indexed` | ✓ | bucket+project, session_started_at DESC |
| `conversation_sessions` | — | last_seen_at DESC(partial open), client_origin+started_at DESC, needs_reflection(partial) |
| `cross_pollination_queue` | — | status+created_at, target(partial pending) |
| `routing_logs` (partitioned) | — | created_at DESC, classification(GIN), degraded (partial), rag_mismatch (partial) |
| `usage_logs` (partitioned) | — | tool+date, bucket+date |
| `llm_calls` (partitioned) | — | request_id (partial), purpose+date, model+date, failed (partial), client+date (partial), project+date (partial) |
| `pending_embeddings` | — | created_at |
| `reflection_pending` | — | status+created_at(partial pending) |
| `scout_denylist` | — | unique(pattern) |
| `control_registry` | — | next_due_at(partial active) |
| `patterns` | ✓ | tags(GIN), client(partial) |
| `decisions` | ✓ | bucket+project, projects_indexed_id (partial), client(partial) |
| `gotchas` | ✓ | severity |
| `contacts` | — | relationship(partial active), projects(GIN), name(trgm) |
| `ideas` | ✓ | status+created_at DESC, related_lessons(GIN), related_tools(GIN), related_projects(GIN), client(partial) |

HNSW parameters: `m=16, ef_construction=64`. These are pgvector defaults, tuned for under 100k vectors. Revisit at 1M+.

---

## 9. Migrations strategy

### 9.1 Structure

Migration files live in `migrations/`, numbered sequentially:

```
migrations/
├── 0001_extensions.sql
├── 0002_lessons.sql
├── 0003_tools_catalog.sql
├── 0004_projects_indexed.sql
├── 0005_project_state.sql
├── 0006_project_versions.sql
├── 0007_skill_versions.sql
├── 0008_conversations_indexed.sql
├── 0009_conversation_sessions.sql
├── 0010_cross_pollination_queue.sql
├── 0011_routing_logs_partitioned.sql
├── 0012_usage_logs_partitioned.sql
├── 0013_llm_calls_partitioned.sql
├── 0014_pending_embeddings.sql
├── 0015_reflection_pending.sql
├── 0016_scout_denylist.sql
├── 0017_control_registry.sql
├── 0018_phase2_tables.sql
├── 0019_functions_triggers.sql
├── 0020_scout_safety_trigger.sql
├── 0021_views.sql
├── 0022_seed_tools_catalog.sql
└── 0023_seed_control_registry.sql
```

Applied in order by the migration runner (simple Python script wrapping `psql`, or `alembic` if Python-native preferred). Each migration is idempotent (`CREATE IF NOT EXISTS`) and logs to `schema_migrations` table.

### 9.2 Schema migrations table

```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    checksum TEXT NOT NULL
);
```

### 9.3 Forward-only discipline

Migrations are forward-only. Schema changes require a new numbered migration, never editing an applied one. Rollback via inverse migration if absolutely necessary, documented in the migration file itself.

---

## 10. Backup and recovery

### 10.1 Daily backup

`pg_dump` runs nightly via systemd timer at 03:30 local:

```bash
#!/bin/bash
# infra/backup/pg_backup.sh
set -euo pipefail                 # fail fast on any error, undefined var, or pipe failure

BACKUP_DIR="/home/operator/backups/pretel-os-db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DUMP_FILE="${BACKUP_DIR}/pretel_os_${TIMESTAMP}.dump"

pg_dump -Fc -d pretel_os -f "${DUMP_FILE}"

# Verify dump integrity before touching the plaintext (pg_dump with large vector columns
# is sensitive to mid-write interruptions; a truncated file would encrypt cleanly but
# fail on restore — we want to know now, not at recovery time)
if ! pg_restore --list "${DUMP_FILE}" > /dev/null 2>&1; then
    echo "ERROR: dump verification failed, aborting backup. File preserved for inspection: ${DUMP_FILE}" >&2
    exit 1
fi

# Optional deeper check: dry-run restore to a scratch db (expensive, run weekly not daily)
# if [ "$(date +%u)" = "7" ]; then  # Sundays only
#     pg_restore --dbname="${BACKUP_DIR}/scratch_restore_check" --clean --if-exists "${DUMP_FILE}" || exit 1
# fi

gpg --encrypt --recipient backup@pretel \
    --output "${DUMP_FILE}.gpg" "${DUMP_FILE}"

# Only delete plaintext after successful encryption
if [ -s "${DUMP_FILE}.gpg" ]; then
    rm "${DUMP_FILE}"
else
    echo "ERROR: encrypted file is empty, preserving plaintext" >&2
    exit 1
fi

rclone copy "${DUMP_FILE}.gpg" supabase-storage:backups/pretel-os/

# Retention: 30 days local, 90 days remote (remote purged by Supabase lifecycle rule, not here)
find "${BACKUP_DIR}" -name "*.gpg" -mtime +30 -delete
```

Retention: 30 days local, 90 days remote (Supabase Storage).

### 10.2 Recovery

```bash
gpg --decrypt pretel_os_20260418_033000.dump.gpg > pretel_os.dump
pg_restore -d pretel_os_new pretel_os.dump
```

Tested quarterly by operator running a recovery drill to a throwaway database.

### 10.3 Migration to Supabase (Phase 4)

Once schema is stable:

```bash
# Export from local
pg_dump -d pretel_os -f pretel_os_export.sql

# Import to Supabase
psql "postgresql://postgres:[pass]@db.xxx.supabase.co:5432/postgres" < pretel_os_export.sql
```

HNSW indexes transfer correctly. Embeddings are just floats — no re-computation needed. Update connection string in `src/mcp_server/config.py`; restart MCP server.

---

## 11. Future-proofing notes

### 11.1 Multi-tenancy

`client_id UUID NULL` is already present on `lessons`, `projects_indexed`, `contacts`. When freelance productization starts needing per-client isolation, a single `UPDATE` backfills `client_id = operator_default_uuid` on existing rows, and row-level security policies gate access:

```sql
-- Example RLS policy (activated in Phase 4+)
ALTER TABLE lessons ENABLE ROW LEVEL SECURITY;
CREATE POLICY lessons_client_isolation ON lessons
    USING (client_id = current_setting('app.current_client_id')::UUID
           OR client_id IS NULL);
```

### 11.2 Audit trail

If regulatory needs ever require full audit: add a generic `audit_log` table with `(entity_type, entity_id, action, before, after, actor, timestamp)` and a generic trigger. Not needed now.

### 11.3 Sharding

Not needed below 10M rows per table. Current projections put us 2 orders of magnitude below that in 5 years. Revisit only if projections change.

### 11.4 Vector quantization

pgvector supports binary quantization and `halfvec` (16-bit floats) to reduce storage 2–4x at small precision cost. At current scale (< 100 MB of vectors), not worth it. Revisit at 1M+ rows.

### 11.5 Hard-coded dimension warning

Every embedding column across every table declares `vector(3072)` to match `text-embedding-3-large`. This is load-bearing.

If the embeddings model ever changes — to a local model (768 or 1024 dim, e.g., `bge-large-en-v1.5`), to Voyage (1024), to OpenAI `text-embedding-3-small` (1536), or to any future model — the migration is **not a drop-in swap**. Required steps:

1. Constitutional amendment to `CONSTITUTION §2.5` with rationale.
2. A dedicated migration file that:
   - Alters every `vector(3072)` column to the new dimensionality (Postgres cannot change vector dimensions in place; requires column drop + recreate + re-embed).
   - Clears every `embedding` column (null out).
   - Drops and recreates every HNSW index.
3. A full re-embedding pass of every row in `lessons`, `tools_catalog`, `projects_indexed`, `conversations_indexed`, `patterns`, `decisions`, `gotchas`, `contacts`, `ideas`. This queues through `pending_embeddings` and runs via the Auto-index worker — at current scale (~5k vectors) this completes in minutes and costs under $1.

The migration template is kept at `migrations/template_reindex_embeddings.sql.txt` in the repo. Do not run it silently; a model change is a whole-system event, not a config tweak.
