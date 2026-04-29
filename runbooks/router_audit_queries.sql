-- runbooks/router_audit_queries.sql
--
-- Spec §9.3 audit queries for the Router (Phase D telemetry).
-- Saved as part of D.5.2 close-out per phase_d_close.md.
--
-- Run against the production DB (or pretel_os_test for verification):
--   psql "$DATABASE_URL" -f runbooks/router_audit_queries.sql
--
-- All three queries must execute cleanly against the routing_logs +
-- llm_calls schema. A query returning zero rows is a valid empty
-- signal (e.g., "no RAG mismatches" is the healthy state for query 3).


-- ===========================================================================
-- 1. Classifier uptime (last 30 days)
-- ===========================================================================
-- What share of recent turns went through the LLM classifier vs the
-- rule-based fallback? The fallback path indicates LiteLLM proxy
-- unavailability or schema-validation failures (spec §10).
--
-- Healthy: 'llm' >> 'fallback_rules'. A persistent fallback share
-- suggests a degraded LiteLLM upstream (cost-spiking model, throttling)
-- or a schema drift in classifier output.
--
-- Note: rows with classification_mode='haiku' are pre-Phase-D writes
-- from the Module 3 stub; Phase D writes only 'llm' or 'fallback_rules'.

SELECT classification_mode,
       count(*),
       round(100.0 * count(*) / sum(count(*)) over (), 2) AS pct
FROM   routing_logs
WHERE  created_at > now() - interval '30 days'
GROUP BY classification_mode;


-- ===========================================================================
-- 2. Per-model classification cost and quality
-- ===========================================================================
-- For every concrete model the LiteLLM cascade resolved to, how many
-- classifications did we get, what's the average user satisfaction, and
-- what did it cost? Drives provider-cascade tuning decisions.
--
-- avg_satisfaction is NULL for models that never got an explicit
-- report_satisfaction call — ranked NULLS LAST so models with feedback
-- come first.
--
-- avg_cost / total_cost are 0.000000 today because the LiteLLM proxy
-- doesn't surface cost_usd to the SDK response (Phase F follow-up to
-- wire). Keeping the columns now so historic data accumulates against
-- the right shape.

SELECT lc.model,
       count(*)                     AS classifications,
       avg(rl.user_satisfaction)    AS avg_satisfaction,
       avg(lc.cost_usd)             AS avg_cost,
       sum(lc.cost_usd)             AS total_cost
FROM   routing_logs rl
JOIN   llm_calls    lc USING (request_id)
WHERE  lc.purpose = 'classification'
  AND  rl.created_at > now() - interval '30 days'
GROUP BY lc.model
ORDER BY avg_satisfaction DESC NULLS LAST;


-- ===========================================================================
-- 3. RAG mismatch detection (rag_expected ≠ rag_executed)
-- ===========================================================================
-- When the classifier asked for L4 lessons (rag_expected=true) but L4
-- did not actually load (rag_executed=false), or vice versa. Both
-- directions are signal:
--   - expected=true, executed=false → embedding API down, L4 SQL drift,
--     bucket filter excluding everything
--   - expected=false, executed=true → classifier said LOW but L4 fired
--     (shouldn't happen; possible logic bug)
--
-- A zero-row result is the healthy state. Spike investigation: drill
-- into routing_logs.degraded_reason for the matching day.

SELECT date_trunc('day', created_at) AS day,
       count(*)
FROM   routing_logs
WHERE  rag_expected <> rag_executed
GROUP BY day
ORDER BY day DESC;
