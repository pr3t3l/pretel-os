-- Migration 0029 — data migration: lessons split + ADR seed
-- Module 0.X — Knowledge Architecture
-- Spec: specs/module-0x-knowledge-architecture/spec.md §7
-- Created: 2026-04-28
--
-- Two purposes:
--
-- 1. Seed `decisions` table with formal ADRs 020-024:
--    ADR-020: LiteLLM proxy gateway
--    ADR-021: Split lessons into typed stores (this module)
--    ADR-022: SOUL.md L0 voice file
--    ADR-023: best_practices new table (not patterns extension)
--    ADR-024: HNSW indexes deferred until pgvector >= 0.7
--
--    Source of truth for these is DECISIONS.md (committed b96fa84).
--    This migration loads them into the `decisions` table for queryability.
--
-- 2. Move 4 misclassified `lessons` rows to their proper homes:
--    - c40e09fc (verbal acknowledgment anti-pattern) → decisions scope=process
--    - d7f1e119 (LiteLLM concrete model gap)         → tasks  module=M4 phase=Phase D
--    - 89c11602 (pyproject.toml at repo root)        → tasks  module=M0.X phase=before Module 5
--    - 3d98464b (prompt caching investigation)       → tasks  module=M4 phase=Phase F
--
--    Originals marked status='archived' (lessons enum doesn't have 'superseded';
--    cross-table pointer lives in metadata.superseded_to_table + .superseded_to_id).
--    Idempotency gate uses status IN ('active','pending_review') for defense.
--
-- IDEMPOTENCY: Each section is gated. ADRs gate on adr_number existence.
-- Lessons split gates on lessons.status != 'superseded'. Re-running this
-- migration is a no-op.

BEGIN;

-- ════════════════════════════════════════════════════════════════
-- SECTION A — Seed ADRs into decisions table
-- ════════════════════════════════════════════════════════════════

-- ADR-020: LiteLLM proxy gateway
INSERT INTO decisions (
    bucket, project, title, context, decision, consequences, alternatives,
    scope, applicable_buckets, decided_by, tags, severity, adr_number, status
)
SELECT
    'business', 'pretel-os',
    'Router classifier and second_opinion route through LiteLLM proxy aliases',
    'The Router needs LLM access for classification (every turn) and second-opinion fallback (rare). Hardcoding model strings couples pretel-os to a specific vendor and forces code changes to swap models.',
    'All Router LLM calls route through LiteLLM proxy aliases: classifier_default and second_opinion_default. Underlying model selection is config-only via ~/.litellm/config.yaml. Router code never references concrete model identifiers.',
    'Model swaps become a YAML edit. Cascade fallback handled at proxy. Routing logs show alias not concrete model — concrete model identity must be extracted from provider_metadata jsonb.',
    'Direct vendor SDKs (Anthropic/OpenAI): rejected, vendor lock-in. LangChain ChatModel: rejected, heavyweight. Custom router class: rejected, duplicates LiteLLM.',
    'architectural',
    ARRAY['personal','business','scout'],
    'operator',
    ARRAY['router','litellm','model-routing','vendor-neutrality'],
    'critical',
    20,
    'active'
WHERE NOT EXISTS (SELECT 1 FROM decisions WHERE adr_number = 20);

-- ADR-021: Split lessons into typed stores
INSERT INTO decisions (
    bucket, project, title, context, decision, consequences, alternatives,
    scope, applicable_buckets, decided_by, tags, severity, adr_number, status
)
SELECT
    'business', 'pretel-os',
    'Split lessons into typed knowledge stores (Module 0.X)',
    'The single lessons table accumulated semantically distinct content types: post-hoc patterns, tasks, decisions, best-practice guidance, preferences. Each has different mutability, load triggers, and write provenance. One schema produced schema-violations-by-tag.',
    'Split into typed stores: tasks, operator_preferences, router_feedback, best_practices (new) + amendment of existing decisions table. lessons retains original scope: post-hoc reflection patterns only.',
    'Each table has correct lifecycle, CHECK constraints, load contract. Module 4 Phase B layer loader can map L0-L4 to specific tables. 4 misclassified lessons rows migrated. 17 new MCP tools required.',
    'Add columns to lessons: rejected (Appendix A of spec). Single typed-document collection: equivalent, same rejection.',
    'architectural',
    ARRAY['personal','business','scout'],
    'operator+claude',
    ARRAY['knowledge-architecture','lessons','schema','module-0x'],
    'critical',
    21,
    'active'
WHERE NOT EXISTS (SELECT 1 FROM decisions WHERE adr_number = 21);

-- ADR-022: SOUL.md as L0 voice file
INSERT INTO decisions (
    bucket, project, title, context, decision, consequences, alternatives,
    scope, applicable_buckets, decided_by, tags, severity, adr_number, status
)
SELECT
    'business', 'pretel-os',
    'SOUL.md as L0 voice file',
    'Operator communication style and behavioral preferences need to load every session via L0. CONSTITUTION is for system rules, IDENTITY for facts, AGENTS for read order. None is the right home for voice.',
    'Add SOUL.md at repo root, loaded into L0 alongside CONSTITUTION/IDENTITY/AGENTS. Claude.ai web/app uses operator userPreferences instead. SOUL.md applies to Claude Code, Telegram bot, MCP session callers.',
    'L0 budget remains 1200 tokens combined. Operator voice persists across sessions and clients (except Anthropic web/app). Sync between SOUL.md and userPreferences deferred.',
    'Inline voice in IDENTITY: rejected, pollutes facts file. operator_preferences table: rejected, voice too rich for k/v. userPreferences only: rejected, doesn''t apply to Claude Code or Telegram.',
    'architectural',
    ARRAY['personal','business','scout'],
    'operator+claude',
    ARRAY['l0','identity','soul','voice'],
    'normal',
    22,
    'active'
WHERE NOT EXISTS (SELECT 1 FROM decisions WHERE adr_number = 22);

-- ADR-023: best_practices is a new table
INSERT INTO decisions (
    bucket, project, title, context, decision, consequences, alternatives,
    scope, applicable_buckets, decided_by, tags, severity, adr_number, status
)
SELECT
    'business', 'pretel-os',
    'best_practices is a new table, not an extension of patterns',
    'M0.X needs to capture reusable PROCESS guidance (always X when Y, narrative). Existing patterns table holds CODE snippets with required code TEXT NOT NULL. Question (OQ-6): extend patterns with kind column or create new best_practices table.',
    'Create new best_practices table with prose guidance field, rationale, domain, scope, derived_from_lessons for reflection-worker provenance, and single-step rollback fields (previous_guidance, previous_rationale). patterns retained unchanged for code.',
    'Two tables for two distinct concepts; clean retrieval. L4 includes both lessons and best_practices. L2 includes both decisions and best_practices filtered by scope. 3 new MCP tools.',
    'Extend patterns with kind text CHECK: rejected. code TEXT NOT NULL incompatible with prose. L2/L4 want different result shapes. LL-DATA-001 (single table beats parallel) applies to lifecycle states of one type, not ontologically distinct types.',
    'architectural',
    ARRAY['personal','business','scout'],
    'operator+claude',
    ARRAY['knowledge-architecture','best-practices','patterns','module-0x'],
    'normal',
    23,
    'active'
WHERE NOT EXISTS (SELECT 1 FROM decisions WHERE adr_number = 23);

-- ADR-024: HNSW indexes deferred until pgvector >= 0.7 or volume justifies
INSERT INTO decisions (
    bucket, project, title, context, decision, consequences, alternatives,
    scope, applicable_buckets, decided_by, tags, severity, adr_number, status
)
SELECT
    'business', 'pretel-os',
    'HNSW indexes deferred until pgvector >= 0.7 or volume justifies',
    'pgvector 0.6.0 (Ubuntu 24.04 noble) limits HNSW indexes to vectors of <=2000 dimensions. pretel-os uses text-embedding-3-large at 3072 dimensions. HNSW indexes cannot be created with current pgvector on chosen embedding model.',
    'Omit all CREATE INDEX USING hnsw statements from migrations until pgvector upgraded to >=0.7.0 OR vector volume crosses threshold where seq scan exceeds 100ms (~50K rows for vector(3072)). Until then, queries use sequential scan with ORDER BY embedding <=> query LIMIT k. At <5K vectors, completes in 10-50ms.',
    'All migrations including M0.X 0024-0029 must NOT include HNSW CREATE INDEX. text-embedding-3-large at 3072 dims preserved per CONSTITUTION §2.5 invariant. Future migration re-adds HNSW once condition met.',
    'Reduce embeddings to vector(2000): rejected, requires constitutional amendment to §2.5; 1-2 percent quality loss not justified by current need. IVFFlat instead of HNSW: rejected, requires populated tables; lower recall. Build pgvector >=0.7 from source: deferred, no apt update tracking. PostgreSQL Apt PPA: deferred, apt-source drift risk.',
    'architectural',
    ARRAY['personal','business','scout'],
    'operator+claude',
    ARRAY['pgvector','hnsw','embeddings','retrieval','scaling'],
    'critical',
    24,
    'active'
WHERE NOT EXISTS (SELECT 1 FROM decisions WHERE adr_number = 24);

-- ════════════════════════════════════════════════════════════════
-- SECTION B — Lessons split (4 misclassified rows)
-- ════════════════════════════════════════════════════════════════
--
-- For each: capture original lesson UUID via subquery, INSERT into target
-- table, then UPDATE original lesson to status='superseded' with metadata
-- pointing to new row UUID.

-- B.1: c40e09fc (verbal acknowledgment anti-pattern) → decisions scope=process
DO $$
DECLARE
    src_lesson_id uuid;
    src_title text;
    src_content text;
    new_decision_id uuid;
BEGIN
    SELECT id, title, content INTO src_lesson_id, src_title, src_content
    FROM lessons
    WHERE id::text LIKE 'c40e09fc%' AND status IN ('active','pending_review')
    LIMIT 1;

    IF src_lesson_id IS NOT NULL THEN
        INSERT INTO decisions (
            bucket, project, title, context, decision, consequences,
            scope, decided_by, tags, severity, status, derived_from_lessons
        )
        VALUES (
            'business', 'pretel-os',
            COALESCE(src_title, 'Verbal acknowledgment is not persistence'),
            'Original lesson c40e09fc captured the anti-pattern of saying "I''ll keep this in mind" or "noted as tech debt" instead of using a tool call. Operator observed ~40 percent of such items get lost.',
            'Any deferred item, future-task, or technical-debt note must be persisted immediately to the appropriate MCP tool (save_lesson now, task_create after M0.X). Verbal acknowledgment alone is forbidden.',
            COALESCE(src_content, 'When discussion surfaces "we''ll handle this later", the right tool call IS the acknowledgment. Tag deferred items with deferred-todo. Title prefixed DEFERRED:.'),
            'process',
            'operator',
            ARRAY['process-discipline','deferral','m0x','migrated-from-lessons'],
            'critical',
            'active',
            ARRAY[src_lesson_id]
        )
        RETURNING id INTO new_decision_id;

        UPDATE lessons
        SET status = 'archived',
            metadata = COALESCE(metadata, '{}'::jsonb) || jsonb_build_object(
                'superseded_to_table', 'decisions',
                'superseded_to_id', new_decision_id,
                'superseded_at', now(),
                'superseded_by_migration', '0029'
            )
        WHERE id = src_lesson_id;

        RAISE NOTICE 'Migrated c40e09fc → decisions %', new_decision_id;
    ELSE
        RAISE NOTICE 'c40e09fc not in active/pending_review or missing — skipping (idempotent)';
    END IF;
END $$;

-- B.2: d7f1e119 (LiteLLM concrete model) → tasks module=M4 phase=Phase D
DO $$
DECLARE
    src_lesson_id uuid;
    src_title text;
    src_content text;
    new_task_id uuid;
BEGIN
    SELECT id, title, content INTO src_lesson_id, src_title, src_content
    FROM lessons
    WHERE id::text LIKE 'd7f1e119%' AND status IN ('active','pending_review')
    LIMIT 1;

    IF src_lesson_id IS NOT NULL THEN
        INSERT INTO tasks (
            title, description, bucket, project, module,
            status, priority, trigger_phase, source, metadata
        )
        VALUES (
            COALESCE(src_title, 'Extract concrete model identity from provider_metadata in routing_logs'),
            COALESCE(src_content, 'LiteLLM proxy returns response.model = alias rather than concrete provider model identifier. routing_logs.provider_metadata contains the concrete model in jsonb dump. Extract it for proper telemetry distinguishing primary from fallback.'),
            'business', 'pretel-os', 'M4',
            'open', 'normal', 'Phase D', 'migration',
            jsonb_build_object('migrated_from_lesson', src_lesson_id, 'migration', '0029', 'tag', 'deferred-todo')
        )
        RETURNING id INTO new_task_id;

        UPDATE lessons
        SET status = 'archived',
            metadata = COALESCE(metadata, '{}'::jsonb) || jsonb_build_object(
                'superseded_to_table', 'tasks',
                'superseded_to_id', new_task_id,
                'superseded_at', now(),
                'superseded_by_migration', '0029'
            )
        WHERE id = src_lesson_id;

        RAISE NOTICE 'Migrated d7f1e119 → tasks %', new_task_id;
    ELSE
        RAISE NOTICE 'd7f1e119 not in active/pending_review or missing — skipping (idempotent)';
    END IF;
END $$;

-- B.3: 89c11602 (pyproject.toml at repo root) → tasks module=M0.X phase=before Module 5
DO $$
DECLARE
    src_lesson_id uuid;
    src_title text;
    src_content text;
    new_task_id uuid;
BEGIN
    SELECT id, title, content INTO src_lesson_id, src_title, src_content
    FROM lessons
    WHERE id::text LIKE '89c11602%' AND status IN ('active','pending_review')
    LIMIT 1;

    IF src_lesson_id IS NOT NULL THEN
        INSERT INTO tasks (
            title, description, bucket, project, module,
            status, priority, trigger_phase, source, metadata
        )
        VALUES (
            COALESCE(src_title, 'Add pyproject.toml at repo root'),
            COALESCE(src_content, 'conftest.py at repo root + __init__.py in tests subdirs is the unblock for missing pyproject.toml. Tech debt deferred to M0.X cleanup. Required before Module 5 telegram_bot which has its own dependencies.'),
            'business', 'pretel-os', 'M0.X',
            'open', 'normal', 'before Module 5', 'migration',
            jsonb_build_object('migrated_from_lesson', src_lesson_id, 'migration', '0029', 'tag', 'deferred-todo')
        )
        RETURNING id INTO new_task_id;

        UPDATE lessons
        SET status = 'archived',
            metadata = COALESCE(metadata, '{}'::jsonb) || jsonb_build_object(
                'superseded_to_table', 'tasks',
                'superseded_to_id', new_task_id,
                'superseded_at', now(),
                'superseded_by_migration', '0029'
            )
        WHERE id = src_lesson_id;

        RAISE NOTICE 'Migrated 89c11602 → tasks %', new_task_id;
    ELSE
        RAISE NOTICE '89c11602 not in active/pending_review or missing — skipping (idempotent)';
    END IF;
END $$;

-- B.4: 3d98464b (prompt caching investigation) → tasks module=M4 phase=Phase F
DO $$
DECLARE
    src_lesson_id uuid;
    src_title text;
    src_content text;
    new_task_id uuid;
BEGIN
    SELECT id, title, content INTO src_lesson_id, src_title, src_content
    FROM lessons
    WHERE id::text LIKE '3d98464b%' AND status IN ('active','pending_review')
    LIMIT 1;

    IF src_lesson_id IS NOT NULL THEN
        INSERT INTO tasks (
            title, description, bucket, project, module,
            status, priority, trigger_phase, source, metadata
        )
        VALUES (
            COALESCE(src_title, 'Investigate Anthropic prompt caching for Router classifier turns'),
            COALESCE(src_content, 'Prompt caching can reduce per-turn latency on classifier_default after warmup. Cache warm-up takes a few calls. Worth investigating in M4 Phase F (cost/latency optimization).'),
            'business', 'pretel-os', 'M4',
            'open', 'low', 'Phase F', 'migration',
            jsonb_build_object('migrated_from_lesson', src_lesson_id, 'migration', '0029', 'tag', 'deferred-todo')
        )
        RETURNING id INTO new_task_id;

        UPDATE lessons
        SET status = 'archived',
            metadata = COALESCE(metadata, '{}'::jsonb) || jsonb_build_object(
                'superseded_to_table', 'tasks',
                'superseded_to_id', new_task_id,
                'superseded_at', now(),
                'superseded_by_migration', '0029'
            )
        WHERE id = src_lesson_id;

        RAISE NOTICE 'Migrated 3d98464b → tasks %', new_task_id;
    ELSE
        RAISE NOTICE '3d98464b not in active/pending_review or missing — skipping (idempotent)';
    END IF;
END $$;

-- ════════════════════════════════════════════════════════════════
-- Bookkeeping
-- ════════════════════════════════════════════════════════════════

INSERT INTO schema_migrations (version, checksum)
VALUES (
    '0029',
    md5('0029_data_migration_lessons_split_v2_archived_status')
)
ON CONFLICT (version) DO NOTHING;

COMMIT;
