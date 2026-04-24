-- 0013_llm_calls_partitioned.sql
-- Source: DATA_MODEL.md §4.3

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'llm_purpose') THEN
        CREATE TYPE llm_purpose AS ENUM (
            'classification',
            'embedding_write',
            'embedding_query',
            'client_reasoning',
            'reflection',
            'dream_engine',
            'morning_intel',
            'second_opinion'
        );
    END IF;
END$$;

CREATE TABLE IF NOT EXISTS llm_calls (
    id                UUID DEFAULT gen_random_uuid(),
    request_id        TEXT,
    purpose           llm_purpose NOT NULL,
    provider          TEXT NOT NULL,
    model             TEXT NOT NULL,
    input_tokens      INTEGER NOT NULL DEFAULT 0,
    output_tokens     INTEGER NOT NULL DEFAULT 0,
    cache_read_tokens INTEGER NOT NULL DEFAULT 0,
    cost_usd          NUMERIC(10, 6) NOT NULL DEFAULT 0,
    latency_ms        INTEGER,
    success           BOOLEAN NOT NULL DEFAULT true,
    error             TEXT,
    client_id         UUID,
    project           TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE INDEX IF NOT EXISTS idx_llm_calls_request ON llm_calls(request_id) WHERE request_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_llm_calls_purpose_date ON llm_calls(purpose, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_llm_calls_model_date ON llm_calls(model, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_llm_calls_failed ON llm_calls(created_at DESC) WHERE success = false;
CREATE INDEX IF NOT EXISTS idx_llm_calls_client ON llm_calls(client_id, created_at DESC) WHERE client_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_llm_calls_project ON llm_calls(project, created_at DESC) WHERE project IS NOT NULL;

DO $$
DECLARE
    cur_start DATE := date_trunc('month', now())::date;
    cur_end   DATE := (date_trunc('month', now()) + interval '1 month')::date;
    nxt_end   DATE := (date_trunc('month', now()) + interval '2 months')::date;
    cur_name  TEXT := 'llm_calls_' || to_char(cur_start, 'YYYY_MM');
    nxt_name  TEXT := 'llm_calls_' || to_char(cur_end, 'YYYY_MM');
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = cur_name) THEN
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF llm_calls FOR VALUES FROM (%L) TO (%L)',
            cur_name, cur_start, cur_end
        );
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = nxt_name) THEN
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF llm_calls FOR VALUES FROM (%L) TO (%L)',
            nxt_name, cur_end, nxt_end
        );
    END IF;
END$$;
