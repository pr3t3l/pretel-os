-- 0036_seed_catalog_orphans.sql
-- M7.5 follow-up — close the discoverability gap surfaced 2026-04-30.
--
-- Three tools are registered in mcp_server/main.py via app.tool() but
-- never had a tools_catalog row:
--   - report_satisfaction
--   - list_pending_cross_pollination
--   - resolve_cross_pollination
-- This made them callable via MCP transport but invisible to
-- `tool_search`, `recommend_skills_for_query`, and the per-bucket
-- `available_skills` field that the Router injects into ContextBundle.
-- The discovery cycle (skills/skill_discovery.md) cannot surface them.
--
-- Also seeds the new `list_catalog` tool added in this same patch
-- (src/mcp_server/tools/catalog.py) — the canonical "what's in the
-- catalog" enumeration that complements `tool_search` (which is
-- query-filtered + capped at 50).
--
-- Idempotent: ON CONFLICT (name) DO UPDATE.

BEGIN;

INSERT INTO tools_catalog (
    name, kind, description_short, description_full,
    applicable_buckets, utility_score
)
VALUES
    ('list_catalog', 'tool',
     'Enumerate the full tools_catalog (paginated, filterable)',
     'Canonical catalog enumeration. Unlike tool_search (query-filtered, capped at 50), list_catalog returns the entire catalog with optional kind/bucket/include_archived filters and a total_count for pagination. Used by LLMs that need to know "what tools exist" deterministically.',
     ARRAY['personal', 'business', 'scout'], 0.85),

    ('report_satisfaction', 'tool',
     'Update routing_logs.user_satisfaction (1-5) for a given request_id',
     'Captures operator-supplied satisfaction signal post-turn. Module 4 Phase D wired this for the Router feedback loop; keyed by request_id so it associates with the exact ContextBundle the agent received.',
     ARRAY['personal', 'business', 'scout'], 0.60),

    ('list_pending_cross_pollination', 'tool',
     'List pending cross-pollination proposals',
     'Read-only listing of cross_pollination_queue rows with status=pending, ordered by priority ASC NULLS LAST then created_at ASC. Used by Telegram /cross_poll_review and Claude.ai review surfaces. Module 5 Phase A.',
     ARRAY['personal', 'business', 'scout'], 0.70),

    ('resolve_cross_pollination', 'tool',
     'Approve or reject a cross-pollination proposal',
     'Transitions a cross_pollination_queue row out of pending. approve → status=applied (the cross-bucket idea is committed); reject → status=dismissed (with operator-supplied reason persisted in metadata). Module 5 Phase A.',
     ARRAY['personal', 'business', 'scout'], 0.70)
ON CONFLICT (name) DO UPDATE SET
    description_short = EXCLUDED.description_short,
    description_full  = EXCLUDED.description_full,
    utility_score     = EXCLUDED.utility_score;

INSERT INTO schema_migrations (version, checksum)
VALUES (
    '0036',
    md5('0036_seed_catalog_orphans_v1')
) ON CONFLICT (version) DO NOTHING;

COMMIT;
