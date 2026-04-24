-- 0005_project_state.sql
-- Source: DATA_MODEL.md §2.4

CREATE TABLE IF NOT EXISTS project_state (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bucket           TEXT NOT NULL,
    project          TEXT NOT NULL,
    client_id        UUID,
    state_key        TEXT NOT NULL,
    content          TEXT NOT NULL,
    status           TEXT NOT NULL DEFAULT 'open',
    priority         SMALLINT,
    related_lessons  UUID[] NOT NULL DEFAULT '{}',
    metadata         JSONB NOT NULL DEFAULT '{}',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at        TIMESTAMPTZ,

    UNIQUE(bucket, project, state_key, content)
);

CREATE INDEX IF NOT EXISTS idx_state_active ON project_state(bucket, project) WHERE status = 'open';
CREATE INDEX IF NOT EXISTS idx_state_priority ON project_state(priority, created_at) WHERE status = 'open';
CREATE INDEX IF NOT EXISTS idx_state_related_lessons ON project_state USING gin(related_lessons);
CREATE INDEX IF NOT EXISTS idx_state_client ON project_state(client_id) WHERE client_id IS NOT NULL;
