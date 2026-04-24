-- 0020_scout_safety_trigger.sql
-- Source: DATA_MODEL.md §6.7

CREATE OR REPLACE FUNCTION scout_safety_check()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    matched_pattern TEXT;
BEGIN
    IF NEW.bucket = 'scout' THEN
        SELECT pattern INTO matched_pattern
        FROM scout_denylist
        WHERE (COALESCE(NEW.title, '') || ' ' || COALESCE(NEW.content, '')) ~* pattern
        LIMIT 1;

        IF matched_pattern IS NOT NULL THEN
            RAISE EXCEPTION 'Scout denylist violation: pattern "%" matched. Reformulate abstractly per CONSTITUTION §3.', matched_pattern
                USING HINT = 'This is a DB-level guard; the MCP tool should have filtered earlier.';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_scout_safety_lessons') THEN
        CREATE TRIGGER trg_scout_safety_lessons
            BEFORE INSERT OR UPDATE ON lessons
            FOR EACH ROW EXECUTE FUNCTION scout_safety_check();
    END IF;
END$$;
