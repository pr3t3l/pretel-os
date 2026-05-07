-- 0039_dream_engine_phase_a_schema.sql
-- Source: M8 Dream Engine fase 1, Phase A schema work.
-- Authority: specs/dream_engine/spec.md (success criteria + open Q's),
--            specs/dream_engine/phase_a_close.md (Q1/Q2/Q3/Q7 decisions),
--            CONSTITUTION §2.6 v5.2 (worker charter), §5.5 rule 22 v5.2
--            (parametrized archive thresholds).
--
-- Four schema changes in one transaction:
--
-- 1. cross_pollination_queue.target_lesson_id new column (UUID FK, NULLable,
--    ON DELETE CASCADE). NULL preserved for future 'manual' bucket-level
--    proposals; 'dream_engine_dedup' rows must be NON-NULL (worker enforces
--    in code; no schema CHECK to avoid over-constraining).
--
-- 2. UNIQUE constraint on cross_pollination_queue
--    (origin_lesson, target_lesson_id, proposed_by). PostgreSQL default
--    NULLs-distinct semantics mean multiple NULL-target rows coexist —
--    desired for 'manual' rows. Idempotency for nightly dedup pass:
--    second-night INSERT for the same pair becomes ON CONFLICT DO NOTHING.
--
-- 3. New table dream_engine_runs (telemetry per nightly worker invocation).
--    Slim schema: id, started_at, completed_at, status, jobs_run JSONB,
--    failures JSONB, worker_pid. Status CHECK = running|success|partial|failed.
--
-- 4. Seed operator_preferences with 3 archive thresholds (category='workflow'
--    chosen because the existing CHECK constraint accepts only 6 categories
--    and none mean 'lifecycle/archival' specifically; 'workflow' is the
--    closest semantic fit and avoids constraint-thrash):
--      archive.usage_window_days   = 500    (raised from 180 per ADR-029)
--      archive.utility_threshold   = 0.5
--      archive.utility_lookback_days = 90
--    All idempotent via ON CONFLICT (category, key, scope) DO NOTHING.
--    The Dream Engine worker reads these at run time and HARD-FAILS on
--    missing keys (no hardcoded fallback) per spec §7 risk row.

BEGIN;

-- 1 + 2: cross_pollination_queue extensions
ALTER TABLE cross_pollination_queue
    ADD COLUMN IF NOT EXISTS target_lesson_id UUID
    REFERENCES lessons(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_crosspoll_target_lesson
    ON cross_pollination_queue(target_lesson_id)
    WHERE target_lesson_id IS NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'cross_pollination_queue_pair_unique'
    ) THEN
        ALTER TABLE cross_pollination_queue
            ADD CONSTRAINT cross_pollination_queue_pair_unique
            UNIQUE (origin_lesson, target_lesson_id, proposed_by);
    END IF;
END $$;

-- 3: dream_engine_runs telemetry table
CREATE TABLE IF NOT EXISTS dream_engine_runs (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    started_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at  TIMESTAMPTZ,
    status        TEXT NOT NULL DEFAULT 'running'
                  CHECK (status IN ('running', 'success', 'partial', 'failed')),
    jobs_run      JSONB NOT NULL DEFAULT '{}'::jsonb,
    failures      JSONB NOT NULL DEFAULT '[]'::jsonb,
    worker_pid    INTEGER
);

CREATE INDEX IF NOT EXISTS idx_dream_engine_runs_started_at
    ON dream_engine_runs(started_at DESC);

CREATE INDEX IF NOT EXISTS idx_dream_engine_runs_status_started
    ON dream_engine_runs(status, started_at DESC)
    WHERE status IN ('partial', 'failed');

COMMENT ON TABLE  dream_engine_runs IS
    'Telemetry: one row per Dream Engine nightly invocation (M8 fase 1). '
    'Inserted at run start with status=running, finalized on completion.';
COMMENT ON COLUMN dream_engine_runs.jobs_run IS
    'JSONB: {job_name: {duration_ms, rows_affected, error?}, ...} '
    'where job_name in (utility_recompute, dedup_pass, archive_low_utility).';
COMMENT ON COLUMN dream_engine_runs.failures IS
    'JSONB: [{job, error_class, error_message, traceback?}, ...]. '
    'Empty array for status=success runs.';

-- 4: seed operator_preferences with archive thresholds
INSERT INTO operator_preferences (category, key, value, scope, source, metadata)
VALUES
    ('workflow', 'archive.usage_window_days',   '500', 'global', 'migration',
     '{"unit": "days", "set_by": "migration_0039", "constitutional_authority": "§5.5 rule 22 v5.2", "purpose": "Days-since-creation threshold for archive eligibility"}'::jsonb),
    ('workflow', 'archive.utility_threshold',   '0.5', 'global', 'migration',
     '{"unit": "score", "set_by": "migration_0039", "constitutional_authority": "§5.5 rule 22 v5.2", "purpose": "utility_score floor below which a low-usage lesson is archive-eligible"}'::jsonb),
    ('workflow', 'archive.utility_lookback_days', '90', 'global', 'migration',
     '{"unit": "days", "set_by": "migration_0039", "constitutional_authority": "§5.5 rule 22 v5.2", "purpose": "Lookback window over which utility_threshold is evaluated"}'::jsonb)
ON CONFLICT (category, key, scope) DO NOTHING;

INSERT INTO schema_migrations (version, checksum)
VALUES (
    '0039',
    md5('0039_dream_engine_phase_a_schema_v1')
) ON CONFLICT (version) DO NOTHING;

COMMIT;
