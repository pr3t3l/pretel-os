-- 0015_reflection_pending.sql
-- Source: DATA_MODEL.md §4.5

CREATE TABLE IF NOT EXISTS reflection_pending (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id       UUID NOT NULL,
    trigger_event    TEXT NOT NULL,
    transcript_ref   TEXT NOT NULL,
    routing_context  JSONB NOT NULL,
    attempts         INTEGER NOT NULL DEFAULT 0,
    last_error       TEXT,
    status           TEXT NOT NULL DEFAULT 'pending',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_attempt     TIMESTAMPTZ,
    processed_at     TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_reflection_pending_status ON reflection_pending(status, created_at) WHERE status = 'pending';
