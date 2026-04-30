-- 0035_seed_awareness.sql
-- Module 7.5 Phase D — seed the awareness layer's catalog.
--
-- Three blocks:
--   1. INSERT skill_discovery (the new skill that teaches LLMs how to
--      use the awareness layer; utility_score=1.0 so it always loads
--      first).
--   2. UPSERT vett + sdd with utility_score per Q6 + trigger_keywords
--      for recommend_skills_for_query.
--   3. Seed/upsert utility_score across every other catalog entry
--      mentioned in the Q6 table. Tools that do not yet have a row
--      (the new awareness/projects/lessons-review tools registered
--      by main.py during M7 + M7.5) are inserted with placeholder
--      descriptions; existing rows keep their authored descriptions
--      and only get utility_score updated.
--
-- All INSERTs are ON CONFLICT (name) DO UPDATE — the migration is
-- idempotent end-to-end, safe to re-apply.

BEGIN;

-- ---------------------------------------------------------------------
-- 1. skill_discovery — the new top-utility skill.
-- ---------------------------------------------------------------------

INSERT INTO tools_catalog (
    name, kind, description_short, description_full,
    applicable_buckets, utility_score, skill_file_path, trigger_keywords
)
VALUES (
    'skill_discovery',
    'skill',
    'How to discover and use registered skills',
    'Teaches an LLM running on pretel-os how to read available_skills from get_context, when to call recommend_skills_for_query, and how to load and execute a registered skill. Loaded by default in every bucket so the LLM never has to ask the operator which tool to use.',
    ARRAY['personal', 'business', 'scout'],
    1.0,
    'skills/skill_discovery.md',
    ARRAY['skills', 'tools', 'capabilities', 'what can i', 'what tools',
          'what skills', 'discovery', 'available']
)
ON CONFLICT (name) DO UPDATE SET
    kind                = EXCLUDED.kind,
    description_short   = EXCLUDED.description_short,
    description_full    = EXCLUDED.description_full,
    applicable_buckets  = EXCLUDED.applicable_buckets,
    utility_score       = EXCLUDED.utility_score,
    skill_file_path     = EXCLUDED.skill_file_path,
    trigger_keywords    = EXCLUDED.trigger_keywords;

-- ---------------------------------------------------------------------
-- 2. vett + sdd — utility_score + trigger_keywords + skill_file_path.
-- Preserves the existing applicable_buckets (vett is narrower than the
-- default) by NOT including it in the SET clause.
-- ---------------------------------------------------------------------

INSERT INTO tools_catalog (
    name, kind, description_short, description_full,
    applicable_buckets, utility_score, skill_file_path, trigger_keywords
)
VALUES (
    'vett',
    'skill',
    'Vendor Evaluation & Technology Triage framework',
    'Generic vendor evaluation methodology with bucket-specific overlays. Drives the full eval lifecycle (intake, scoring, governance review, decision) and produces a presentation-ready output. Scout overlay supplies the organization-specific tech stack, governance teams, compliance, and data taxonomy.',
    ARRAY['business', 'scout'],
    0.85,
    'skills/vett.md',
    ARRAY['evaluate', 'evaluation', 'vendor', 'vendors',
          'evaluación', 'evaluar', 'vendedor', 'proveedor',
          'tool review', 'platform review', 'vett']
)
ON CONFLICT (name) DO UPDATE SET
    utility_score    = EXCLUDED.utility_score,
    skill_file_path  = EXCLUDED.skill_file_path,
    trigger_keywords = EXCLUDED.trigger_keywords;

INSERT INTO tools_catalog (
    name, kind, description_short, description_full,
    applicable_buckets, utility_score, skill_file_path, trigger_keywords
)
VALUES (
    'sdd',
    'skill',
    'Spec-Driven Development process',
    'Discipline for planning, building, and shipping software-shaped work without rebuilding the same thing 10+ times. Drives the SDD lifecycle (foundation → spec → plan → tasks → execution → close-out) with explicit gates and lessons capture. Applies across all buckets.',
    ARRAY['personal', 'business', 'scout'],
    0.90,
    'skills/sdd.md',
    ARRAY['spec', 'specification', 'plan', 'tasks', 'sdd',
          'module', 'phase', 'gate', 'spec-driven', 'atomic',
          'close-out']
)
ON CONFLICT (name) DO UPDATE SET
    utility_score    = EXCLUDED.utility_score,
    skill_file_path  = EXCLUDED.skill_file_path,
    trigger_keywords = EXCLUDED.trigger_keywords;

-- ---------------------------------------------------------------------
-- 3. Tool rows — seed/upsert utility_score per Q6 table.
-- Existing rows: only utility_score is overwritten (descriptions kept).
-- Missing rows (the M7 / M7.5 additions): inserted with the values
-- below, applicable_buckets defaulting to all three core buckets.
-- ---------------------------------------------------------------------

INSERT INTO tools_catalog (
    name, kind, description_short, description_full,
    applicable_buckets, utility_score
)
VALUES
    ('save_lesson', 'tool',
     'Persist a lesson with embedding + dedup + auto-approval gate',
     'Insert a lesson row with status=pending_review, generate the OpenAI embedding, run the find_duplicate_lesson dedup check, and auto-promote when the four CONSTITUTION §5.2 rule 13 conditions hold.',
     ARRAY['personal', 'business', 'scout'], 0.95),

    ('search_lessons', 'tool',
     'Semantic search over active lessons',
     'Embed the query via text-embedding-3-large; filter-first (bucket + tags + status) per CONSTITUTION §5.6; sort by cosine similarity. Sequential scan — pgvector 3072-dim cannot HNSW.',
     ARRAY['personal', 'business', 'scout'], 0.85),

    ('create_project', 'tool',
     'Register a new live project with bucket+slug',
     'Validate bucket; normalize slug; INSERT into projects; write the initial L2 README on disk; seed project_state and project_versions. Idempotent on (bucket, slug). Triggers bucket README regeneration via M7.5 trigger 0034.',
     ARRAY['personal', 'business', 'scout'], 0.80),

    ('get_project', 'tool',
     'Look up a live project by (bucket, slug) and return README content',
     'Read-only fetch of the projects row plus the on-disk README content when readme_path is populated.',
     ARRAY['personal', 'business', 'scout'], 0.70),

    ('list_projects', 'tool',
     'List projects with optional bucket / status filters',
     'Read-only listing ordered by created_at DESC. Limit clamped to 200.',
     ARRAY['personal', 'business', 'scout'], 0.70),

    ('archive_project', 'tool',
     'Mark an active project as archived (Module 7.5)',
     'UPDATE projects SET status=archived, archived_at=now(), archive_reason. Idempotent — second archive returns clean error. Emits project_lifecycle pg_notify; calls regenerate_bucket_readme inline.',
     ARRAY['personal', 'business', 'scout'], 0.70),

    ('task_create', 'tool',
     'Create a task',
     'INSERT into tasks. Resolves project_id from (bucket, project) when both are provided; legacy text column kept for forensics. Default status=open; status=blocked when blocked_by is set.',
     ARRAY['personal', 'business', 'scout'], 0.85),

    ('task_list', 'tool',
     'List tasks with optional filters',
     'Filter by bucket / status / module / trigger_phase. Priority order (urgent → low) by default; done_at DESC when status=done.',
     ARRAY['personal', 'business', 'scout'], 0.75),

    ('task_close', 'tool',
     'Mark a task done',
     'UPDATE tasks SET status=done, done_at=now(). Optional completion_note merges into metadata.',
     ARRAY['personal', 'business', 'scout'], 0.75),

    ('decision_record', 'tool',
     'Record an architectural / process / product / operational decision (ADR)',
     'INSERT into decisions with embedding on title+context+decision. Resolves project_id from (bucket, project) when both are provided.',
     ARRAY['personal', 'business', 'scout'], 0.85),

    ('decision_search', 'tool',
     'Semantic search over decisions',
     'Filter-first (bucket + scope + status), sort by embedding cosine similarity. HNSW deferred per ADR-024.',
     ARRAY['personal', 'business', 'scout'], 0.80),

    ('best_practice_record', 'tool',
     'Persist a reusable best practice',
     'INSERT into best_practices. Embedding via OpenAI; auto-queued via trg_best_practices_emb (migration 0030).',
     ARRAY['personal', 'business', 'scout'], 0.75),

    ('best_practice_search', 'tool',
     'Semantic search over best practices',
     'Filter-first by category/applicable_buckets/active; sort by embedding similarity. Sequential scan per ADR-024.',
     ARRAY['personal', 'business', 'scout'], 0.75),

    ('register_skill', 'tool',
     'Register a new skill in tools_catalog',
     'INSERT into tools_catalog with kind=skill, embedding queued for the missing-embedding worker.',
     ARRAY['personal', 'business', 'scout'], 0.60),

    ('register_tool', 'tool',
     'Register a new tool in tools_catalog',
     'INSERT into tools_catalog with kind=tool, embedding queued for the missing-embedding worker.',
     ARRAY['personal', 'business', 'scout'], 0.60),

    ('load_skill', 'tool',
     'Fetch the full markdown content of a registered skill',
     'Read-only filesystem fetch of skills/<name>.md after a tools_catalog lookup confirms the row exists and is not deprecated.',
     ARRAY['personal', 'business', 'scout'], 0.85),

    ('tool_search', 'tool',
     'Semantic search over tools_catalog (skills + tools)',
     'Embed the query and rank against tools_catalog.embedding. Pre-filter by deprecated=false / archived_at IS NULL.',
     ARRAY['personal', 'business', 'scout'], 0.85),

    ('recommend_skills_for_query', 'tool',
     'Score skills against a user message via keyword + utility (Module 7.5)',
     'Pure SQL + Python: score = 1.0 * keyword_hit + 0.3 * utility_score. Threshold 1.0; top 3 returned. No LLM call.',
     ARRAY['personal', 'business', 'scout'], 0.95),

    ('regenerate_bucket_readme', 'tool',
     'Regenerate buckets/<bucket>/README.md from current DB state',
     'Idempotent: re-runs with no DB change produce a byte-identical file (stable timestamp). Operator notes preserved between pretel:notes markers.',
     ARRAY['personal', 'business', 'scout'], 0.50),

    ('regenerate_project_readme', 'tool',
     'Regenerate buckets/<bucket>/projects/<slug>/README.md',
     'Idempotent project README regeneration mirroring regenerate_bucket_readme. Returns project_not_found when no projects row matches.',
     ARRAY['personal', 'business', 'scout'], 0.50),

    ('get_context', 'tool',
     'Router orchestrator — classify + assemble + invariants + telemetry',
     'Async pipeline producing a ContextBundle. Module 7.5 added available_skills + active_projects to the response shape.',
     ARRAY['personal', 'business', 'scout'], 0.95),

    ('preference_get', 'tool',
     'Read an operator_preferences row',
     'Read-only lookup keyed by name.',
     ARRAY['personal', 'business', 'scout'], 0.60),

    ('preference_set', 'tool',
     'Upsert an operator_preferences row',
     'INSERT ... ON CONFLICT DO UPDATE. Loaded into L0 by the Layer Loader.',
     ARRAY['personal', 'business', 'scout'], 0.70),

    ('list_pending_lessons', 'tool',
     'List lessons awaiting operator review',
     'WHERE status = pending_review, ordered by created_at ASC. Used by Telegram /review_pending and Claude.ai surfaces.',
     ARRAY['personal', 'business', 'scout'], 0.70),

    ('approve_lesson', 'tool',
     'Approve a pending lesson — flip status to active',
     'UPDATE only fires when the row is currently pending_review. Returns approved=False otherwise.',
     ARRAY['personal', 'business', 'scout'], 0.80),

    ('reject_lesson', 'tool',
     'Reject a pending lesson with reason — flip status to rejected',
     'UPDATE only fires on pending_review rows. Reason persists into metadata.reject_reason.',
     ARRAY['personal', 'business', 'scout'], 0.70)
ON CONFLICT (name) DO UPDATE SET
    utility_score = EXCLUDED.utility_score;

-- ---------------------------------------------------------------------
-- 4. schema_migrations row.
-- ---------------------------------------------------------------------

INSERT INTO schema_migrations (version, checksum)
VALUES (
    '0035',
    md5('0035_seed_awareness_v1')
) ON CONFLICT (version) DO NOTHING;

COMMIT;
