-- Migration 0024 — tasks table
-- Module 0.X — Knowledge Architecture
-- Spec: specs/module-0x-knowledge-architecture/spec.md §5.1
-- Created: 2026-04-28

BEGIN;

CREATE TABLE IF NOT EXISTS tasks (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    title               text NOT NULL,
    description         text,
    bucket              text NOT NULL,
    project             text,
    module              text,
    status              text NOT NULL DEFAULT 'open'
                        CHECK (status IN ('open','in_progress','blocked','done','cancelled')),
    priority            text DEFAULT 'normal'
                        CHECK (priority IN ('urgent','high','normal','low')),
    blocked_by          uuid REFERENCES tasks(id) ON DELETE SET NULL,
    trigger_phase       text,
    source              text NOT NULL
                        CHECK (source IN ('operator','claude','reflection_worker','migration')),
    estimated_minutes   integer,
    github_issue_url    text,
    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now(),
    done_at             timestamptz,
    metadata            jsonb DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_tasks_bucket_status
    ON tasks(bucket, status);

CREATE INDEX IF NOT EXISTS idx_tasks_open_by_phase
    ON tasks(trigger_phase)
    WHERE status IN ('open','blocked');

CREATE INDEX IF NOT EXISTS idx_tasks_module
    ON tasks(module)
    WHERE module IS NOT NULL;

-- updated_at trigger (uses existing function from migration 0019)
CREATE TRIGGER trg_set_updated_at_tasks
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();

INSERT INTO schema_migrations (version, checksum)
VALUES (
    '0024',
    md5('0024_tasks_v1')
)
ON CONFLICT (version) DO NOTHING;

COMMIT;
