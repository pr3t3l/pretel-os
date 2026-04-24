-- 0016_scout_denylist.sql
-- Source: DATA_MODEL.md §6.7

CREATE TABLE IF NOT EXISTS scout_denylist (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern    TEXT NOT NULL UNIQUE,
    reason     TEXT NOT NULL,
    added_by   TEXT NOT NULL DEFAULT 'operator',
    added_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
