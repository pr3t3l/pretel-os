-- 0038_fix_embedding_invalidation_app_override.sql
-- Source: bug found in `tests/mcp_server/tools/test_best_practices.py::test_best_practice_rollback_re_embeds_restored_content`
-- after applying migration 0037.
--
-- Problem: 0037's `invalidate_embedding_on_content_change()` nulls
-- NEW.embedding whenever content columns differ from OLD.* — including
-- the legitimate case where the application provided a fresh embedding
-- in the same UPDATE statement (e.g., `best_practice_record(update_id=...)`,
-- `best_practice_rollback(...)`).
--
-- This produced embedding=NULL for rows whose application code had
-- correctly computed and supplied the new vector, defeating the
-- atomic content+embedding update path that all the
-- *_record(update_id=...) tools rely on.
--
-- Fix: only null NEW.embedding if the application did NOT also update it.
-- The compound condition `content changed AND embedding NOT changed in
-- this UPDATE` is the safety-net case (manual SQL edit, app forgot to
-- recompute). When the app updates content AND embedding atomically,
-- trust the app's vector.
--
-- Detection: `NEW.embedding IS NOT DISTINCT FROM OLD.embedding` is true
-- when the UPDATE either omits the embedding column entirely (PG carries
-- OLD value forward) or explicitly sets it to the same value. Either way
-- means "app didn't provide a new vector here" → we null it for async
-- recomputation.
--
-- Idempotent CREATE OR REPLACE — no DDL changes needed for triggers
-- or the table itself.

BEGIN;

CREATE OR REPLACE FUNCTION invalidate_embedding_on_content_change()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    content_changed   BOOLEAN := false;
    embedding_updated BOOLEAN := NEW.embedding IS DISTINCT FROM OLD.embedding;
BEGIN
    IF TG_TABLE_NAME = 'lessons' THEN
        content_changed := OLD.title   IS DISTINCT FROM NEW.title
                        OR OLD.content IS DISTINCT FROM NEW.content;
    ELSIF TG_TABLE_NAME = 'tools_catalog' THEN
        content_changed := OLD.name             IS DISTINCT FROM NEW.name
                        OR OLD.description_full IS DISTINCT FROM NEW.description_full;
    ELSIF TG_TABLE_NAME = 'projects_indexed' THEN
        content_changed := OLD.name        IS DISTINCT FROM NEW.name
                        OR OLD.description IS DISTINCT FROM NEW.description;
    ELSIF TG_TABLE_NAME = 'conversations_indexed' THEN
        content_changed := OLD.content       IS DISTINCT FROM NEW.content
                        OR OLD.topic_summary IS DISTINCT FROM NEW.topic_summary;
    ELSIF TG_TABLE_NAME = 'patterns' THEN
        content_changed := OLD.name        IS DISTINCT FROM NEW.name
                        OR OLD.description IS DISTINCT FROM NEW.description
                        OR OLD.use_case    IS DISTINCT FROM NEW.use_case;
    ELSIF TG_TABLE_NAME = 'decisions' THEN
        content_changed := OLD.title    IS DISTINCT FROM NEW.title
                        OR OLD.context  IS DISTINCT FROM NEW.context
                        OR OLD.decision IS DISTINCT FROM NEW.decision;
    ELSIF TG_TABLE_NAME = 'gotchas' THEN
        content_changed := OLD.title           IS DISTINCT FROM NEW.title
                        OR OLD.trigger_context IS DISTINCT FROM NEW.trigger_context
                        OR OLD.what_goes_wrong IS DISTINCT FROM NEW.what_goes_wrong;
    ELSIF TG_TABLE_NAME = 'contacts' THEN
        content_changed := OLD.name    IS DISTINCT FROM NEW.name
                        OR OLD.role    IS DISTINCT FROM NEW.role
                        OR OLD.company IS DISTINCT FROM NEW.company;
    ELSIF TG_TABLE_NAME = 'ideas' THEN
        content_changed := OLD.summary   IS DISTINCT FROM NEW.summary
                        OR OLD.full_text IS DISTINCT FROM NEW.full_text;
    ELSIF TG_TABLE_NAME = 'best_practices' THEN
        content_changed := OLD.title     IS DISTINCT FROM NEW.title
                        OR OLD.guidance  IS DISTINCT FROM NEW.guidance
                        OR OLD.rationale IS DISTINCT FROM NEW.rationale;
    END IF;

    -- Only null the embedding when content changed AND the application
    -- did not also provide a fresh vector. If embedding_updated is true,
    -- the app handled it atomically — trust the app's vector.
    IF content_changed AND NOT embedding_updated THEN
        NEW.embedding := NULL;
    END IF;

    RETURN NEW;
END;
$$;

INSERT INTO schema_migrations (version, checksum)
VALUES (
    '0038',
    md5('0038_fix_embedding_invalidation_app_override_v1')
) ON CONFLICT (version) DO NOTHING;

COMMIT;
