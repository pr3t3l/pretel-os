-- 0009_conversation_sessions.sql
-- Source: DATA_MODEL.md §4.6

CREATE TABLE IF NOT EXISTS conversation_sessions (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_origin    TEXT NOT NULL,
    operator_id      TEXT,
    client_id        UUID,
    bucket           TEXT,
    project          TEXT,
    started_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at        TIMESTAMPTZ,
    close_reason     TEXT,
    turn_count       INTEGER NOT NULL DEFAULT 0,
    transcript_path  TEXT,
    reflection_fired BOOLEAN NOT NULL DEFAULT false,
    metadata         JSONB NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_sessions_open ON conversation_sessions(last_seen_at DESC) WHERE closed_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_sessions_client_origin ON conversation_sessions(client_origin, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_needs_reflection ON conversation_sessions(closed_at) WHERE closed_at IS NOT NULL AND reflection_fired = false;
