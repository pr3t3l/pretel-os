-- 0021_views.sql
-- Source: DATA_MODEL.md §7

CREATE OR REPLACE VIEW v_active_lessons AS
SELECT id, title, content, next_time, bucket, project, category, tags,
       usage_count, utility_score, last_used_at, embedding
FROM lessons
WHERE status = 'active' AND deleted_at IS NULL;

CREATE OR REPLACE VIEW v_recommendable_tools AS
SELECT id, name, kind, description_short, description_full, applicable_buckets,
       usage_count, utility_score, last_used_at, embedding
FROM tools_catalog
WHERE deprecated = false;

CREATE OR REPLACE VIEW v_open_state AS
SELECT bucket, project, state_key, content, priority, created_at
FROM project_state
WHERE status = 'open'
ORDER BY priority NULLS LAST, created_at DESC;

CREATE OR REPLACE VIEW v_crosspoll_inbox AS
SELECT target_bucket, count(*) AS pending_count,
       min(created_at) AS oldest,
       max(created_at) AS newest
FROM cross_pollination_queue
WHERE status = 'pending'
GROUP BY target_bucket;

CREATE OR REPLACE VIEW v_tool_lessons AS
SELECT
    unnest_tool AS tool_name,
    count(*) AS lesson_count,
    array_agg(l.id ORDER BY l.created_at DESC) AS lesson_ids,
    avg(l.utility_score) AS avg_lesson_utility
FROM lessons l, unnest(l.related_tools) AS unnest_tool
WHERE l.status = 'active' AND l.deleted_at IS NULL
GROUP BY unnest_tool
ORDER BY lesson_count DESC;

CREATE OR REPLACE VIEW v_daily_cost_by_purpose AS
SELECT
    date_trunc('day', created_at)::date AS day,
    purpose,
    model,
    sum(cost_usd) AS cost_usd,
    sum(input_tokens) AS input_tokens,
    sum(output_tokens) AS output_tokens,
    count(*) AS call_count
FROM llm_calls
WHERE created_at > now() - interval '60 days'
GROUP BY 1, 2, 3
ORDER BY 1 DESC, 4 DESC;
