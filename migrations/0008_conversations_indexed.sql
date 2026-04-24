-- 0008_conversations_indexed.sql
-- Source: DATA_MODEL.md §3.1

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'conversation_storage') THEN
        CREATE TYPE conversation_storage AS ENUM ('full', 'summarized');
    END IF;
END$$;

CREATE TABLE IF NOT EXISTS conversations_indexed (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id    TEXT NOT NULL,
    client_origin      TEXT NOT NULL,
    bucket             TEXT,
    project            TEXT,
    topic_summary      TEXT NOT NULL,
    content            TEXT,
    storage            conversation_storage NOT NULL DEFAULT 'full',
    turns_count        INTEGER NOT NULL DEFAULT 0,
    embedding          vector(3072),
    client_id          UUID,

    session_started_at TIMESTAMPTZ NOT NULL,
    session_ended_at   TIMESTAMPTZ,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    summarized_at      TIMESTAMPTZ
);

-- HNSW index deferred: pgvector 0.6.0 limits HNSW to 2000 dims; vector(3072) exceeds this.
-- At current scale (<5k vectors) sequential scan is sufficient.
-- Re-add when pgvector is upgraded or volume justifies IVFFlat.

CREATE INDEX IF NOT EXISTS idx_conv_bucket_project ON conversations_indexed(bucket, project);
CREATE INDEX IF NOT EXISTS idx_conv_date ON conversations_indexed(session_started_at DESC);
