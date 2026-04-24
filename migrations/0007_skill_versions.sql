-- 0007_skill_versions.sql
-- Source: DATA_MODEL.md §2.6

CREATE TABLE IF NOT EXISTS skill_versions (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_name     TEXT NOT NULL,
    version        INTEGER NOT NULL,
    content        TEXT NOT NULL,
    diff_summary   TEXT,
    changed_by     TEXT NOT NULL,
    reason         TEXT,

    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE(skill_name, version)
);

CREATE INDEX IF NOT EXISTS idx_skill_versions_lookup ON skill_versions(skill_name, version DESC);
