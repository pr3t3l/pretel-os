-- 0019_functions_triggers.sql
-- Source: DATA_MODEL.md §6.1–§6.6, §6.8
-- (The scout_safety_check function + trigger live in 0020.)

-- §6.1 updated_at auto-maintenance
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_lessons_updated_at') THEN
        CREATE TRIGGER trg_lessons_updated_at BEFORE UPDATE ON lessons
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_tools_updated_at') THEN
        CREATE TRIGGER trg_tools_updated_at BEFORE UPDATE ON tools_catalog
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_projects_updated_at') THEN
        CREATE TRIGGER trg_projects_updated_at BEFORE UPDATE ON projects_indexed
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_state_updated_at') THEN
        CREATE TRIGGER trg_state_updated_at BEFORE UPDATE ON project_state
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_patterns_updated_at') THEN
        CREATE TRIGGER trg_patterns_updated_at BEFORE UPDATE ON patterns
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_contacts_updated_at') THEN
        CREATE TRIGGER trg_contacts_updated_at BEFORE UPDATE ON contacts
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    END IF;
END$$;

-- §6.2 Auto-index on save
CREATE OR REPLACE FUNCTION notify_missing_embedding()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    source_text TEXT;
BEGIN
    IF NEW.embedding IS NULL THEN
        source_text := CASE TG_TABLE_NAME
            WHEN 'lessons' THEN NEW.title || E'\n\n' || NEW.content
            WHEN 'tools_catalog' THEN NEW.name || E'\n' || NEW.description_full
            WHEN 'projects_indexed' THEN NEW.name || E'\n' || NEW.description
            WHEN 'conversations_indexed' THEN COALESCE(NEW.content, NEW.topic_summary)
            WHEN 'patterns' THEN NEW.name || E'\n' || NEW.description || E'\n' || NEW.use_case
            WHEN 'decisions' THEN NEW.title || E'\n' || NEW.context || E'\n' || NEW.decision
            WHEN 'gotchas' THEN NEW.title || E'\n' || NEW.trigger_context || E'\n' || NEW.what_goes_wrong
            WHEN 'contacts' THEN NEW.name || ' ' || COALESCE(NEW.role, '') || ' ' || COALESCE(NEW.company, '')
            WHEN 'ideas' THEN NEW.summary || E'\n' || COALESCE(NEW.full_text, '')
            ELSE NULL
        END;

        IF source_text IS NOT NULL THEN
            INSERT INTO pending_embeddings (target_table, target_id, source_text)
            VALUES (TG_TABLE_NAME, NEW.id, source_text)
            ON CONFLICT (target_table, target_id) DO UPDATE
                SET source_text = EXCLUDED.source_text,
                    attempts = 0,
                    last_error = NULL;

            PERFORM pg_notify('embedding_queue', TG_TABLE_NAME || ':' || NEW.id::text);
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_lessons_emb') THEN
        CREATE TRIGGER trg_lessons_emb AFTER INSERT ON lessons
            FOR EACH ROW EXECUTE FUNCTION notify_missing_embedding();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_tools_emb') THEN
        CREATE TRIGGER trg_tools_emb AFTER INSERT ON tools_catalog
            FOR EACH ROW EXECUTE FUNCTION notify_missing_embedding();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_projects_emb') THEN
        CREATE TRIGGER trg_projects_emb AFTER INSERT ON projects_indexed
            FOR EACH ROW EXECUTE FUNCTION notify_missing_embedding();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_conv_emb') THEN
        CREATE TRIGGER trg_conv_emb AFTER INSERT ON conversations_indexed
            FOR EACH ROW EXECUTE FUNCTION notify_missing_embedding();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_patterns_emb') THEN
        CREATE TRIGGER trg_patterns_emb AFTER INSERT ON patterns
            FOR EACH ROW EXECUTE FUNCTION notify_missing_embedding();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_decisions_emb') THEN
        CREATE TRIGGER trg_decisions_emb AFTER INSERT ON decisions
            FOR EACH ROW EXECUTE FUNCTION notify_missing_embedding();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_gotchas_emb') THEN
        CREATE TRIGGER trg_gotchas_emb AFTER INSERT ON gotchas
            FOR EACH ROW EXECUTE FUNCTION notify_missing_embedding();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_contacts_emb') THEN
        CREATE TRIGGER trg_contacts_emb AFTER INSERT ON contacts
            FOR EACH ROW EXECUTE FUNCTION notify_missing_embedding();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_ideas_emb') THEN
        CREATE TRIGGER trg_ideas_emb AFTER INSERT ON ideas
            FOR EACH ROW EXECUTE FUNCTION notify_missing_embedding();
    END IF;
END$$;

-- §6.3 Duplicate detection
CREATE OR REPLACE FUNCTION find_duplicate_lesson(
    p_content TEXT,
    p_embedding vector(3072),
    p_bucket TEXT,
    p_threshold REAL DEFAULT 0.92
)
RETURNS TABLE (
    id UUID,
    title TEXT,
    similarity REAL
) LANGUAGE sql STABLE AS $$
    SELECT
        l.id,
        l.title,
        (1 - (l.embedding <=> p_embedding))::REAL AS similarity
    FROM lessons l
    WHERE l.status = 'active'
      AND l.bucket = p_bucket
      AND l.embedding IS NOT NULL
      AND (1 - (l.embedding <=> p_embedding)) >= p_threshold
    ORDER BY l.embedding <=> p_embedding
    LIMIT 5;
$$;

-- §6.4 Utility score recomputation
CREATE OR REPLACE FUNCTION recompute_utility_scores()
RETURNS void LANGUAGE plpgsql AS $$
BEGIN
    UPDATE tools_catalog tc
    SET utility_score =
        ln(1 + tc.usage_count)
        + CASE
            WHEN tc.last_used_at IS NULL THEN 0
            WHEN tc.last_used_at > now() - interval '7 days' THEN 2.0
            WHEN tc.last_used_at > now() - interval '30 days' THEN 1.0
            WHEN tc.last_used_at > now() - interval '90 days' THEN 0.5
            ELSE 0
          END
        + 2 * tc.cross_bucket_count
        + tc.manual_boost,
    updated_at = now()
    WHERE tc.deprecated = false;

    UPDATE lessons l
    SET utility_score =
        ln(1 + l.usage_count)
        + CASE
            WHEN l.last_used_at IS NULL THEN 0
            WHEN l.last_used_at > now() - interval '30 days' THEN 1.5
            WHEN l.last_used_at > now() - interval '90 days' THEN 0.5
            ELSE 0
          END,
    updated_at = now()
    WHERE l.status = 'active';
END;
$$;

-- §6.5 Archival pass for lessons
CREATE OR REPLACE FUNCTION archive_low_utility_lessons()
RETURNS INTEGER LANGUAGE plpgsql AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    UPDATE lessons
    SET status = 'archived',
        updated_at = now()
    WHERE status = 'active'
      AND usage_count = 0
      AND created_at < now() - interval '180 days'
      AND utility_score < 0.5
      AND NOT EXISTS (
          SELECT 1 FROM project_state ps
          WHERE lessons.id = ANY(ps.related_lessons)
            AND ps.status = 'open'
      );

    GET DIAGNOSTICS archived_count = ROW_COUNT;
    RETURN archived_count;
END;
$$;

-- §6.6 Conversation summarization
CREATE OR REPLACE FUNCTION summarize_old_conversation(
    p_id UUID,
    p_summary TEXT
)
RETURNS void LANGUAGE sql AS $$
    UPDATE conversations_indexed
    SET content = NULL,
        topic_summary = p_summary,
        storage = 'summarized',
        summarized_at = now()
    WHERE id = p_id
      AND storage = 'full'
      AND session_started_at < now() - interval '90 days';
$$;

-- §6.8 Tool archival pass
CREATE OR REPLACE FUNCTION archive_dormant_tools()
RETURNS INTEGER LANGUAGE plpgsql AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    UPDATE tools_catalog
    SET archived_at = now(),
        archive_reason = 'unused >180d with utility_score < 0.5',
        updated_at = now()
    WHERE deprecated = false
      AND archived_at IS NULL
      AND (last_used_at IS NULL OR last_used_at < now() - interval '180 days')
      AND utility_score < 0.5;

    GET DIAGNOSTICS archived_count = ROW_COUNT;
    RETURN archived_count;
END;
$$;
