-- 0040_seed_update_tags_tools.sql
-- Source: 2026-06-01 operator conversation closing the gap where lessons /
-- decisions / best_practices entries had no way to amend `tags` without
-- re-creating the row.
--
-- Previously: best_practice_record(update_id=...) re-embedded + consumed
-- the rollback slot even for tag-only changes. save_lesson had no UPDATE
-- path at all and re-running it tripped the dup-check (>=0.92) returning
-- merge_candidate. decision_record only offered append-only supersession.
--
-- This patch adds three narrow tag-only mutation tools — no re-embedding,
-- no dup-check, no rollback-slot consumption — and registers them in
-- tools_catalog so they surface in tool_search / list_catalog /
-- recommend_skills_for_query / Router's available_skills injection.
--
-- Doctrine: lessons are no longer strictly immutable for tags+metadata.
-- A decision_record (queued in this same patch) captures the carve-out
-- and queues a CONSTITUTION §5.2 amendment for the next review pass.
--
-- Idempotent: ON CONFLICT (name) DO UPDATE.

BEGIN;

INSERT INTO tools_catalog (
    name, kind, description_short, description_full,
    applicable_buckets, utility_score
)
VALUES
    ('lesson_update_tags', 'tool',
     'Patch a lesson''s tags without re-embedding (add/remove sets)',
     'Tag-only mutation for lessons. tags_add unions in (idempotent); tags_remove subtracts (idempotent). Does NOT touch title/content/next_time/status/embedding — the BEFORE UPDATE trigger from migration 0037 only invalidates embeddings on content changes, so this is a no-op for the embedding queue. Narrow carve-out from the M5/CONSTITUTION §5.2 immutability contract: tags are metadata, not semantic content. Use this instead of save_lesson when correcting taxonomy on already-active rows (save_lesson re-trips the dup-check and blocks at >=0.92). For content edits the pending_review → archive → re-save path is still canonical.',
     ARRAY['personal', 'business', 'scout'], 0.70),

    ('decision_update_tags', 'tool',
     'Patch a decision''s tags without re-embedding (add/remove sets)',
     'Tag-only mutation for decisions. tags_add unions in (idempotent); tags_remove subtracts (idempotent). Does NOT touch title/context/decision/status/embedding — append-only ADR contract preserved. For semantic changes use decision_supersede (creates new row, marks old superseded). Works on rows in any status (active/superseded/etc) so historical decisions can also be retagged.',
     ARRAY['personal', 'business', 'scout'], 0.65),

    ('best_practice_update_tags', 'tool',
     'Patch a best_practice''s tags without re-embedding or consuming rollback slot',
     'Tag-only mutation for best_practices. tags_add unions in; tags_remove subtracts. Cheaper than best_practice_record(update_id=...) which re-embeds and copies guidance/rationale into previous_* (consuming the single-step rollback slot). Works on both active and deactivated rows so historical entries can be retagged.',
     ARRAY['personal', 'business', 'scout'], 0.65)
ON CONFLICT (name) DO UPDATE SET
    description_short = EXCLUDED.description_short,
    description_full  = EXCLUDED.description_full,
    utility_score     = EXCLUDED.utility_score;

INSERT INTO schema_migrations (version, checksum)
VALUES (
    '0040',
    md5('0040_seed_update_tags_tools_v1')
) ON CONFLICT (version) DO NOTHING;

COMMIT;
