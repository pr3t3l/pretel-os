-- 0004_projects_indexed.sql
-- Source: DATA_MODEL.md §2.3

CREATE TABLE IF NOT EXISTS projects_indexed (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name              TEXT NOT NULL,
    bucket            TEXT NOT NULL,
    description       TEXT NOT NULL,
    outcome           TEXT,
    stack             TEXT[] NOT NULL DEFAULT '{}',
    skills_used       TEXT[] NOT NULL DEFAULT '{}',

    started_at        DATE,
    closed_at         DATE,
    closure_reason    TEXT,

    final_readme      TEXT,
    key_decisions     JSONB NOT NULL DEFAULT '[]',
    lessons_produced  UUID[] NOT NULL DEFAULT '{}',

    embedding         vector(3072),
    client_id         UUID,

    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- HNSW index deferred: pgvector 0.6.0 limits HNSW to 2000 dims; vector(3072) exceeds this.
-- At current scale (<5k vectors) sequential scan is sufficient.
-- Re-add when pgvector is upgraded or volume justifies IVFFlat.

CREATE INDEX IF NOT EXISTS idx_projects_bucket ON projects_indexed(bucket);
CREATE INDEX IF NOT EXISTS idx_projects_stack ON projects_indexed USING gin(stack);
CREATE INDEX IF NOT EXISTS idx_projects_name_trgm ON projects_indexed USING gin(name gin_trgm_ops);
