-- 0006_project_versions.sql
-- Source: DATA_MODEL.md §2.5

CREATE TABLE IF NOT EXISTS project_versions (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bucket            TEXT NOT NULL,
    project           TEXT NOT NULL,
    client_id         UUID,
    snapshot_reason   TEXT NOT NULL,
    readme_content    TEXT NOT NULL,
    modules_content   JSONB NOT NULL DEFAULT '{}',
    state_content     JSONB NOT NULL DEFAULT '{}',
    triggered_by      TEXT NOT NULL,

    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_versions_project ON project_versions(bucket, project, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_versions_client ON project_versions(client_id) WHERE client_id IS NOT NULL;
