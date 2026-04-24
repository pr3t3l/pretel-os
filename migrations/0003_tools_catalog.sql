-- 0003_tools_catalog.sql
-- Source: DATA_MODEL.md §2.2

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'catalog_kind') THEN
        CREATE TYPE catalog_kind AS ENUM ('skill', 'tool', 'prompt');
    END IF;
END$$;

CREATE TABLE IF NOT EXISTS tools_catalog (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                 TEXT NOT NULL UNIQUE,
    kind                 catalog_kind NOT NULL,
    description_short    TEXT NOT NULL,
    description_full     TEXT NOT NULL,
    applicable_buckets   TEXT[] NOT NULL DEFAULT '{}',
    client_id            UUID,
    skill_file_path      TEXT,
    mcp_tool_name        TEXT,

    input_signature      JSONB NOT NULL DEFAULT '{}',
    output_signature     JSONB NOT NULL DEFAULT '{}',
    example_invocation   JSONB,

    usage_count          INTEGER NOT NULL DEFAULT 0,
    cross_bucket_count   INTEGER NOT NULL DEFAULT 0,
    last_used_at         TIMESTAMPTZ,
    manual_boost         REAL NOT NULL DEFAULT 0,
    utility_score        REAL NOT NULL DEFAULT 0,

    embedding            vector(3072),
    deprecated           BOOLEAN NOT NULL DEFAULT false,
    deprecation_reason   TEXT,
    archived_at          TIMESTAMPTZ,
    archive_reason       TEXT,

    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- HNSW index deferred: pgvector 0.6.0 limits HNSW to 2000 dims; vector(3072) exceeds this.
-- At current scale (<5k vectors) sequential scan is sufficient.
-- Re-add when pgvector is upgraded or volume justifies IVFFlat.

CREATE INDEX IF NOT EXISTS idx_tools_kind ON tools_catalog(kind);
CREATE INDEX IF NOT EXISTS idx_tools_buckets ON tools_catalog USING gin(applicable_buckets);
CREATE INDEX IF NOT EXISTS idx_tools_utility ON tools_catalog(utility_score DESC) WHERE deprecated = false AND archived_at IS NULL;
