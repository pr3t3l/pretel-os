-- 0037_embedding_invalidation_on_update.sql
-- Source: M8 pre-work / 2026-05-07 conversation closing the gap where editing
-- content of an embedded row leaves a stale vector.
--
-- Before this migration: every embedded table had an AFTER INSERT trigger
-- calling notify_missing_embedding() to detect rows born without embeddings.
-- UPDATEs were not covered, so any post-INSERT edit to title/content/etc.
-- left the original vector intact (and now misrepresentative of the row).
--
-- After this migration:
--   * BEFORE UPDATE trigger nulls NEW.embedding when *content* columns differ
--     from OLD (per-table list mirrors notify_missing_embedding's source_text
--     branches). Status / timestamp / counter UPDATEs do NOT trigger
--     re-embedding.
--   * AFTER INSERT OR UPDATE trigger queues to pending_embeddings only when
--     NEW.embedding IS NULL (WHEN clause), so the auto-index worker (M2
--     listener on embedding_queue) picks it up. Non-content UPDATEs are
--     no-ops at the trigger level — no function call cost.
--
-- Idempotent (DROP IF EXISTS + CREATE OR REPLACE FUNCTION).

BEGIN;

CREATE OR REPLACE FUNCTION invalidate_embedding_on_content_change()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    changed BOOLEAN := false;
BEGIN
    IF TG_TABLE_NAME = 'lessons' THEN
        changed := OLD.title   IS DISTINCT FROM NEW.title
                OR OLD.content IS DISTINCT FROM NEW.content;
    ELSIF TG_TABLE_NAME = 'tools_catalog' THEN
        changed := OLD.name             IS DISTINCT FROM NEW.name
                OR OLD.description_full IS DISTINCT FROM NEW.description_full;
    ELSIF TG_TABLE_NAME = 'projects_indexed' THEN
        changed := OLD.name        IS DISTINCT FROM NEW.name
                OR OLD.description IS DISTINCT FROM NEW.description;
    ELSIF TG_TABLE_NAME = 'conversations_indexed' THEN
        changed := OLD.content       IS DISTINCT FROM NEW.content
                OR OLD.topic_summary IS DISTINCT FROM NEW.topic_summary;
    ELSIF TG_TABLE_NAME = 'patterns' THEN
        changed := OLD.name        IS DISTINCT FROM NEW.name
                OR OLD.description IS DISTINCT FROM NEW.description
                OR OLD.use_case    IS DISTINCT FROM NEW.use_case;
    ELSIF TG_TABLE_NAME = 'decisions' THEN
        changed := OLD.title    IS DISTINCT FROM NEW.title
                OR OLD.context  IS DISTINCT FROM NEW.context
                OR OLD.decision IS DISTINCT FROM NEW.decision;
    ELSIF TG_TABLE_NAME = 'gotchas' THEN
        changed := OLD.title           IS DISTINCT FROM NEW.title
                OR OLD.trigger_context IS DISTINCT FROM NEW.trigger_context
                OR OLD.what_goes_wrong IS DISTINCT FROM NEW.what_goes_wrong;
    ELSIF TG_TABLE_NAME = 'contacts' THEN
        changed := OLD.name    IS DISTINCT FROM NEW.name
                OR OLD.role    IS DISTINCT FROM NEW.role
                OR OLD.company IS DISTINCT FROM NEW.company;
    ELSIF TG_TABLE_NAME = 'ideas' THEN
        changed := OLD.summary   IS DISTINCT FROM NEW.summary
                OR OLD.full_text IS DISTINCT FROM NEW.full_text;
    ELSIF TG_TABLE_NAME = 'best_practices' THEN
        changed := OLD.title     IS DISTINCT FROM NEW.title
                OR OLD.guidance  IS DISTINCT FROM NEW.guidance
                OR OLD.rationale IS DISTINCT FROM NEW.rationale;
    END IF;

    IF changed THEN
        NEW.embedding := NULL;
    END IF;

    RETURN NEW;
END;
$$;

-- lessons
DROP TRIGGER IF EXISTS trg_lessons_emb            ON lessons;
DROP TRIGGER IF EXISTS trg_lessons_emb_invalidate ON lessons;
CREATE TRIGGER trg_lessons_emb_invalidate
    BEFORE UPDATE ON lessons
    FOR EACH ROW EXECUTE FUNCTION invalidate_embedding_on_content_change();
CREATE TRIGGER trg_lessons_emb
    AFTER INSERT OR UPDATE ON lessons
    FOR EACH ROW
    WHEN (NEW.embedding IS NULL)
    EXECUTE FUNCTION notify_missing_embedding();

-- tools_catalog
DROP TRIGGER IF EXISTS trg_tools_emb            ON tools_catalog;
DROP TRIGGER IF EXISTS trg_tools_emb_invalidate ON tools_catalog;
CREATE TRIGGER trg_tools_emb_invalidate
    BEFORE UPDATE ON tools_catalog
    FOR EACH ROW EXECUTE FUNCTION invalidate_embedding_on_content_change();
CREATE TRIGGER trg_tools_emb
    AFTER INSERT OR UPDATE ON tools_catalog
    FOR EACH ROW
    WHEN (NEW.embedding IS NULL)
    EXECUTE FUNCTION notify_missing_embedding();

-- projects_indexed
DROP TRIGGER IF EXISTS trg_projects_emb            ON projects_indexed;
DROP TRIGGER IF EXISTS trg_projects_emb_invalidate ON projects_indexed;
CREATE TRIGGER trg_projects_emb_invalidate
    BEFORE UPDATE ON projects_indexed
    FOR EACH ROW EXECUTE FUNCTION invalidate_embedding_on_content_change();
CREATE TRIGGER trg_projects_emb
    AFTER INSERT OR UPDATE ON projects_indexed
    FOR EACH ROW
    WHEN (NEW.embedding IS NULL)
    EXECUTE FUNCTION notify_missing_embedding();

-- conversations_indexed
DROP TRIGGER IF EXISTS trg_conv_emb            ON conversations_indexed;
DROP TRIGGER IF EXISTS trg_conv_emb_invalidate ON conversations_indexed;
CREATE TRIGGER trg_conv_emb_invalidate
    BEFORE UPDATE ON conversations_indexed
    FOR EACH ROW EXECUTE FUNCTION invalidate_embedding_on_content_change();
CREATE TRIGGER trg_conv_emb
    AFTER INSERT OR UPDATE ON conversations_indexed
    FOR EACH ROW
    WHEN (NEW.embedding IS NULL)
    EXECUTE FUNCTION notify_missing_embedding();

-- patterns
DROP TRIGGER IF EXISTS trg_patterns_emb            ON patterns;
DROP TRIGGER IF EXISTS trg_patterns_emb_invalidate ON patterns;
CREATE TRIGGER trg_patterns_emb_invalidate
    BEFORE UPDATE ON patterns
    FOR EACH ROW EXECUTE FUNCTION invalidate_embedding_on_content_change();
CREATE TRIGGER trg_patterns_emb
    AFTER INSERT OR UPDATE ON patterns
    FOR EACH ROW
    WHEN (NEW.embedding IS NULL)
    EXECUTE FUNCTION notify_missing_embedding();

-- decisions
DROP TRIGGER IF EXISTS trg_decisions_emb            ON decisions;
DROP TRIGGER IF EXISTS trg_decisions_emb_invalidate ON decisions;
CREATE TRIGGER trg_decisions_emb_invalidate
    BEFORE UPDATE ON decisions
    FOR EACH ROW EXECUTE FUNCTION invalidate_embedding_on_content_change();
CREATE TRIGGER trg_decisions_emb
    AFTER INSERT OR UPDATE ON decisions
    FOR EACH ROW
    WHEN (NEW.embedding IS NULL)
    EXECUTE FUNCTION notify_missing_embedding();

-- gotchas
DROP TRIGGER IF EXISTS trg_gotchas_emb            ON gotchas;
DROP TRIGGER IF EXISTS trg_gotchas_emb_invalidate ON gotchas;
CREATE TRIGGER trg_gotchas_emb_invalidate
    BEFORE UPDATE ON gotchas
    FOR EACH ROW EXECUTE FUNCTION invalidate_embedding_on_content_change();
CREATE TRIGGER trg_gotchas_emb
    AFTER INSERT OR UPDATE ON gotchas
    FOR EACH ROW
    WHEN (NEW.embedding IS NULL)
    EXECUTE FUNCTION notify_missing_embedding();

-- contacts
DROP TRIGGER IF EXISTS trg_contacts_emb            ON contacts;
DROP TRIGGER IF EXISTS trg_contacts_emb_invalidate ON contacts;
CREATE TRIGGER trg_contacts_emb_invalidate
    BEFORE UPDATE ON contacts
    FOR EACH ROW EXECUTE FUNCTION invalidate_embedding_on_content_change();
CREATE TRIGGER trg_contacts_emb
    AFTER INSERT OR UPDATE ON contacts
    FOR EACH ROW
    WHEN (NEW.embedding IS NULL)
    EXECUTE FUNCTION notify_missing_embedding();

-- ideas
DROP TRIGGER IF EXISTS trg_ideas_emb            ON ideas;
DROP TRIGGER IF EXISTS trg_ideas_emb_invalidate ON ideas;
CREATE TRIGGER trg_ideas_emb_invalidate
    BEFORE UPDATE ON ideas
    FOR EACH ROW EXECUTE FUNCTION invalidate_embedding_on_content_change();
CREATE TRIGGER trg_ideas_emb
    AFTER INSERT OR UPDATE ON ideas
    FOR EACH ROW
    WHEN (NEW.embedding IS NULL)
    EXECUTE FUNCTION notify_missing_embedding();

-- best_practices
DROP TRIGGER IF EXISTS trg_best_practices_emb            ON best_practices;
DROP TRIGGER IF EXISTS trg_best_practices_emb_invalidate ON best_practices;
CREATE TRIGGER trg_best_practices_emb_invalidate
    BEFORE UPDATE ON best_practices
    FOR EACH ROW EXECUTE FUNCTION invalidate_embedding_on_content_change();
CREATE TRIGGER trg_best_practices_emb
    AFTER INSERT OR UPDATE ON best_practices
    FOR EACH ROW
    WHEN (NEW.embedding IS NULL)
    EXECUTE FUNCTION notify_missing_embedding();

INSERT INTO schema_migrations (version, checksum)
VALUES (
    '0037',
    md5('0037_embedding_invalidation_on_update_v1')
) ON CONFLICT (version) DO NOTHING;

COMMIT;
