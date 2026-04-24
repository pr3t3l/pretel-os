-- 0014_pending_embeddings.sql
-- Source: DATA_MODEL.md §4.4

CREATE TABLE IF NOT EXISTS pending_embeddings (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_table  TEXT NOT NULL,
    target_id     UUID NOT NULL,
    source_text   TEXT NOT NULL,
    attempts      INTEGER NOT NULL DEFAULT 0,
    last_error    TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_attempt  TIMESTAMPTZ,

    UNIQUE(target_table, target_id)
);

CREATE INDEX IF NOT EXISTS idx_pending_emb ON pending_embeddings(created_at);
