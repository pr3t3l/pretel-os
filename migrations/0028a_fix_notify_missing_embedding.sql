-- Migration 0028a — fix notify_missing_embedding() polymorphic CASE bug
-- Module 2 regression fix (caught during M0X.A.5 0028 smoke test)
-- Created: 2026-04-28
--
-- BUG: Original implementation in 0019_functions_triggers.sql used
-- CASE TG_TABLE_NAME WHEN ... THEN NEW.<column> END. PL/pgSQL evaluates
-- every branch's NEW.<column> reference at runtime against the actual
-- row type. When the trigger fires for any table other than `lessons`,
-- references like NEW.content (lessons branch) fail with:
--     ERROR:  record "new" has no field "content"
--
-- The bug stayed latent until 2026-04-28 because Phase 2 tables
-- (decisions, patterns, gotchas, contacts, ideas, projects_indexed,
-- conversations_indexed, tools_catalog) were all empty. Module 0.X
-- decisions amendment + best_practices smoke tests would be the first
-- non-lessons inserts in production.
--
-- FIX: Rewrite using IF/ELSIF chain. PL/pgSQL evaluates only the matched
-- branch's expressions — no pre-validation issue. Semantically identical
-- to the original for the 9 attached tables.

BEGIN;

CREATE OR REPLACE FUNCTION public.notify_missing_embedding()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    source_text TEXT;
BEGIN
    IF NEW.embedding IS NOT NULL THEN
        RETURN NEW;
    END IF;

    IF TG_TABLE_NAME = 'lessons' THEN
        source_text := NEW.title || E'\n\n' || NEW.content;
    ELSIF TG_TABLE_NAME = 'tools_catalog' THEN
        source_text := NEW.name || E'\n' || NEW.description_full;
    ELSIF TG_TABLE_NAME = 'projects_indexed' THEN
        source_text := NEW.name || E'\n' || NEW.description;
    ELSIF TG_TABLE_NAME = 'conversations_indexed' THEN
        source_text := COALESCE(NEW.content, NEW.topic_summary);
    ELSIF TG_TABLE_NAME = 'patterns' THEN
        source_text := NEW.name || E'\n' || NEW.description || E'\n' || NEW.use_case;
    ELSIF TG_TABLE_NAME = 'decisions' THEN
        source_text := NEW.title || E'\n' || NEW.context || E'\n' || NEW.decision;
    ELSIF TG_TABLE_NAME = 'gotchas' THEN
        source_text := NEW.title || E'\n' || NEW.trigger_context || E'\n' || NEW.what_goes_wrong;
    ELSIF TG_TABLE_NAME = 'contacts' THEN
        source_text := NEW.name || ' ' || COALESCE(NEW.role, '') || ' ' || COALESCE(NEW.company, '');
    ELSIF TG_TABLE_NAME = 'ideas' THEN
        source_text := NEW.summary || E'\n' || COALESCE(NEW.full_text, '');
    ELSE
        RETURN NEW;
    END IF;

    IF source_text IS NOT NULL THEN
        INSERT INTO pending_embeddings (target_table, target_id, source_text)
        VALUES (TG_TABLE_NAME, NEW.id, source_text)
        ON CONFLICT (target_table, target_id) DO UPDATE
            SET source_text = EXCLUDED.source_text,
                attempts = 0,
                last_error = NULL;

        PERFORM pg_notify('embedding_queue', TG_TABLE_NAME || ':' || NEW.id::text);
    END IF;

    RETURN NEW;
END;
$$;

INSERT INTO schema_migrations (version, checksum)
VALUES (
    '0028a',
    md5('0028a_fix_notify_missing_embedding_v1')
)
ON CONFLICT (version) DO NOTHING;

COMMIT;
