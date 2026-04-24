-- 0002_lessons.sql
-- Source: DATA_MODEL.md §2.1

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'lesson_status') THEN
        CREATE TYPE lesson_status AS ENUM (
            'pending_review',
            'active',
            'archived',
            'merged_into',
            'rejected'
        );
    END IF;
END$$;

CREATE TABLE IF NOT EXISTS lessons (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title               TEXT NOT NULL,
    content             TEXT NOT NULL,
    next_time           TEXT,
    bucket              TEXT NOT NULL,
    project             TEXT,
    category            TEXT NOT NULL,
    tags                TEXT[] NOT NULL DEFAULT '{}',
    applicable_buckets  TEXT[] NOT NULL DEFAULT '{}',
    related_tools       TEXT[] NOT NULL DEFAULT '{}',
    metadata            JSONB NOT NULL DEFAULT '{}',
    status              lesson_status NOT NULL DEFAULT 'pending_review',
    merged_into_id      UUID REFERENCES lessons(id),

    source              TEXT,
    source_conversation UUID,
    evidence            JSONB NOT NULL DEFAULT '{}',

    usage_count         INTEGER NOT NULL DEFAULT 0,
    utility_score       REAL NOT NULL DEFAULT 0,
    last_used_at        TIMESTAMPTZ,

    embedding           vector(3072),
    client_id           UUID,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    reviewed_at         TIMESTAMPTZ,
    reviewed_by         TEXT,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at          TIMESTAMPTZ
);

-- HNSW index deferred: pgvector 0.6.0 limits HNSW to 2000 dims; vector(3072) exceeds this.
-- At current scale (<5k vectors) sequential scan is sufficient.
-- Re-add when pgvector is upgraded or volume justifies IVFFlat.

CREATE INDEX IF NOT EXISTS idx_lessons_bucket_status ON lessons(bucket, status) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_lessons_applicable_buckets ON lessons USING gin(applicable_buckets);
CREATE INDEX IF NOT EXISTS idx_lessons_project ON lessons(project) WHERE project IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_lessons_tags ON lessons USING gin(tags);
CREATE INDEX IF NOT EXISTS idx_lessons_related_tools ON lessons USING gin(related_tools);
CREATE INDEX IF NOT EXISTS idx_lessons_category ON lessons(category);
CREATE INDEX IF NOT EXISTS idx_lessons_utility ON lessons(utility_score DESC) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_lessons_title_trgm ON lessons USING gin(title gin_trgm_ops);
