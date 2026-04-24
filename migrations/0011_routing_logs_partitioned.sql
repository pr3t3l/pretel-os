-- 0011_routing_logs_partitioned.sql
-- Source: DATA_MODEL.md §4.1

CREATE TABLE IF NOT EXISTS routing_logs (
    id                       UUID DEFAULT gen_random_uuid(),
    request_id               TEXT NOT NULL,
    client_origin            TEXT NOT NULL,
    message_excerpt          TEXT NOT NULL,
    classification           JSONB NOT NULL,
    classification_mode      TEXT NOT NULL DEFAULT 'haiku',
    layers_loaded            TEXT[] NOT NULL,
    tokens_assembled_total   INTEGER NOT NULL,
    tokens_per_layer         JSONB NOT NULL DEFAULT '{}',
    over_budget_layers       TEXT[] NOT NULL DEFAULT '{}',
    rag_expected             BOOLEAN NOT NULL,
    rag_executed             BOOLEAN NOT NULL DEFAULT false,
    lessons_returned         INTEGER NOT NULL DEFAULT 0,
    tools_returned           INTEGER NOT NULL DEFAULT 0,
    source_conflicts         JSONB NOT NULL DEFAULT '[]',
    user_satisfaction        SMALLINT,
    degraded_mode            BOOLEAN NOT NULL DEFAULT false,
    degraded_reason          TEXT,
    latency_ms               INTEGER NOT NULL,

    created_at               TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE INDEX IF NOT EXISTS idx_routing_date ON routing_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_routing_complexity ON routing_logs USING gin(classification);
CREATE INDEX IF NOT EXISTS idx_routing_degraded ON routing_logs(created_at DESC) WHERE degraded_mode = true;
CREATE INDEX IF NOT EXISTS idx_routing_rag_mismatch ON routing_logs(created_at DESC) WHERE rag_expected <> rag_executed;

-- Partitions for current month and next month.
DO $$
DECLARE
    cur_start DATE := date_trunc('month', now())::date;
    cur_end   DATE := (date_trunc('month', now()) + interval '1 month')::date;
    nxt_end   DATE := (date_trunc('month', now()) + interval '2 months')::date;
    cur_name  TEXT := 'routing_logs_' || to_char(cur_start, 'YYYY_MM');
    nxt_name  TEXT := 'routing_logs_' || to_char(cur_end, 'YYYY_MM');
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = cur_name) THEN
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF routing_logs FOR VALUES FROM (%L) TO (%L)',
            cur_name, cur_start, cur_end
        );
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = nxt_name) THEN
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF routing_logs FOR VALUES FROM (%L) TO (%L)',
            nxt_name, cur_end, nxt_end
        );
    END IF;
END$$;
