-- 0033_projects_table.sql
-- Module 7 Phase B — live projects registry.
--
-- `projects_indexed` (migration 0003) holds CLOSED/archived projects with
-- embeddings for semantic recall. This table holds LIVE projects with a
-- bucket+slug unique key so the create_project MCP tool, the Router's
-- unknown_project detector, and the L2 loader can all agree on identity.
--
-- Idempotent: re-running this migration is a no-op.

CREATE TABLE IF NOT EXISTS projects (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bucket       TEXT NOT NULL,
    slug         TEXT NOT NULL,
    name         TEXT NOT NULL,
    description  TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'active',
    stack        TEXT[] NOT NULL DEFAULT '{}',
    skills_used  TEXT[] NOT NULL DEFAULT '{}',
    objective    TEXT,
    client_id    UUID,
    readme_path  TEXT,
    metadata     JSONB NOT NULL DEFAULT '{}',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_projects_bucket_slug
    ON projects(bucket, slug);

CREATE INDEX IF NOT EXISTS idx_projects_bucket_status
    ON projects(bucket, status);

-- Trigger name `trg_projects_updated_at` is already in use on
-- `projects_indexed` (migration 0019). PostgreSQL allows the same trigger
-- name on different tables, but the bare `tgname` guard in 0019 would
-- short-circuit creation here. Filter by `tgrelid` so this trigger is
-- created on `projects` independently.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger
        WHERE tgname = 'trg_projects_updated_at'
          AND tgrelid = 'projects'::regclass
    ) THEN
        CREATE TRIGGER trg_projects_updated_at BEFORE UPDATE ON projects
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    END IF;
END$$;
