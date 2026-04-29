-- Migration 0030 — best_practices embedding trigger
-- Module 0.X close-out — closes task 92cac1b3
-- Created: 2026-04-29
--
-- Attaches the notify_missing_embedding trigger to best_practices, replacing
-- the manual `INSERT INTO pending_embeddings ... ON CONFLICT DO UPDATE`
-- workaround that lived in best_practice_record (Phase C, commit aba04c7).
--
-- Why a fresh migration: best_practices was added in 0027, AFTER 0019's
-- bulk attachment of the embedding-queue trigger to all then-existing
-- tables, so it never received the trigger. The Phase C tool worked
-- around the gap. This migration replaces the workaround with the
-- proper trigger pattern, matching lessons / decisions / patterns / etc.
--
-- Two parts:
--
--   1. Extend public.notify_missing_embedding() with a `best_practices`
--      branch. The function (defined in 0019, fixed in 0028a) builds
--      `source_text` per-table via IF/ELSIF on TG_TABLE_NAME. Without
--      a matching branch, the ELSE clause RETURN NEW makes the trigger
--      a no-op — adding the trigger alone is insufficient.
--
--   2. Attach trg_best_practices_emb AFTER INSERT, mirroring 0019's
--      pattern verbatim (AFTER INSERT only, no WHEN predicate; the
--      function self-checks NEW.embedding IS NOT NULL up front).
--      Naming follows the trg_<short>_emb convention from 0019.
--
-- Behavioral note (UPDATE path, embed=None):
--   The Phase C workaround manually queued on both INSERT and UPDATE
--   paths of best_practice_record. With the trigger AFTER INSERT only,
--   UPDATE-with-embed=None becomes a silent no-op for queue refresh —
--   which is exactly what every other table in the system does. The
--   embedding worker's reconciliation pass picks up stale rows.

BEGIN;

-- 1. Extend the shared trigger function with a best_practices branch.
--    Mirrors 0028a's IF/ELSIF structure exactly; only adds one branch.
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
    ELSIF TG_TABLE_NAME = 'best_practices' THEN
        source_text := NEW.title || E'\n\n' || NEW.guidance || E'\n\n' || COALESCE(NEW.rationale, '');
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

-- 2. Attach the trigger to best_practices (mirrors 0019's AFTER INSERT pattern).
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_best_practices_emb') THEN
        CREATE TRIGGER trg_best_practices_emb AFTER INSERT ON best_practices
            FOR EACH ROW EXECUTE FUNCTION notify_missing_embedding();
    END IF;
END$$;

INSERT INTO schema_migrations (version, checksum)
VALUES (
    '0030',
    md5('0030_best_practices_embedding_trigger_v1')
)
ON CONFLICT (version) DO NOTHING;

COMMIT;
