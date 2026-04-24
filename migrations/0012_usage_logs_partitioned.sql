-- 0012_usage_logs_partitioned.sql
-- Source: DATA_MODEL.md §4.2

CREATE TABLE IF NOT EXISTS usage_logs (
    id           UUID DEFAULT gen_random_uuid(),
    tool_name    TEXT NOT NULL,
    bucket       TEXT,
    project      TEXT,
    invoked_by   TEXT NOT NULL,
    success      BOOLEAN NOT NULL DEFAULT true,
    duration_ms  INTEGER,
    metadata     JSONB NOT NULL DEFAULT '{}',

    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE INDEX IF NOT EXISTS idx_usage_tool_date ON usage_logs(tool_name, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_bucket ON usage_logs(bucket, created_at DESC);

DO $$
DECLARE
    cur_start DATE := date_trunc('month', now())::date;
    cur_end   DATE := (date_trunc('month', now()) + interval '1 month')::date;
    nxt_end   DATE := (date_trunc('month', now()) + interval '2 months')::date;
    cur_name  TEXT := 'usage_logs_' || to_char(cur_start, 'YYYY_MM');
    nxt_name  TEXT := 'usage_logs_' || to_char(cur_end, 'YYYY_MM');
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = cur_name) THEN
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF usage_logs FOR VALUES FROM (%L) TO (%L)',
            cur_name, cur_start, cur_end
        );
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = nxt_name) THEN
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF usage_logs FOR VALUES FROM (%L) TO (%L)',
            nxt_name, cur_end, nxt_end
        );
    END IF;
END$$;
