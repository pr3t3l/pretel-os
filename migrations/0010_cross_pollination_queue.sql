-- 0010_cross_pollination_queue.sql
-- Source: DATA_MODEL.md §3.2

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'cross_poll_status') THEN
        CREATE TYPE cross_poll_status AS ENUM (
            'pending',
            'under_review',
            'applied',
            'dismissed',
            'merged'
        );
    END IF;
END$$;

CREATE TABLE IF NOT EXISTS cross_pollination_queue (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    origin_bucket         TEXT NOT NULL,
    origin_project        TEXT,
    origin_lesson         UUID REFERENCES lessons(id),
    target_bucket         TEXT NOT NULL,
    idea                  TEXT NOT NULL,
    reasoning             TEXT NOT NULL,
    suggested_application TEXT,

    status                cross_poll_status NOT NULL DEFAULT 'pending',
    priority              SMALLINT,
    confidence_score      REAL,
    impact_score          REAL,
    resolution_note       TEXT,
    merged_into_id        UUID REFERENCES cross_pollination_queue(id),

    proposed_by           TEXT NOT NULL DEFAULT 'reflection_worker',
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    reviewed_at           TIMESTAMPTZ,
    resolved_at           TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_crosspoll_status ON cross_pollination_queue(status, created_at);
CREATE INDEX IF NOT EXISTS idx_crosspoll_target ON cross_pollination_queue(target_bucket) WHERE status IN ('pending', 'under_review');
