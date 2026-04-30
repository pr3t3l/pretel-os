-- 0034_awareness_layer.sql
-- Module 7.5 Phase A — awareness layer schema + lifecycle hooks.
--
-- Adds the wiring that lets the live `projects` table act as the
-- backbone of the bucket/project READMEs and the Router's per-bucket
-- skill/project injection.
--
-- Changes:
--   1. project_id UUID FK on lessons, tasks, decisions (NULLABLE +
--      ON DELETE SET NULL, since pre-existing rows reference projects
--      via free-text columns).
--   2. archived_at + archive_reason + applicable_skills on projects.
--   3. trigger_keywords on tools_catalog.
--   4. Best-effort backfill: populate project_id by joining on
--      (bucket, project_text) -> projects(bucket, slug). Rows with no
--      match keep project_id NULL; the legacy `project` text column is
--      retained for forensics (per Q1 in M7_5_plan.md).
--   5. Four NOTIFY trigger functions:
--        - notify_project_lifecycle  → 'project_lifecycle' channel
--        - notify_readme_dirty_bucket → 'readme_dirty' channel
--        - notify_readme_dirty_project → 'readme_dirty' channel
--        - notify_catalog_changed   → 'catalog_changed' channel
--      The readme_consumer worker LISTENs on 'readme_dirty' and
--      debounces dispatch (per Q2 + Q9). Layer cache invalidation
--      already lives on a separate trigger function from migration
--      0031; these new triggers do NOT replace it.
--
-- Idempotent: ALTER TABLE ... ADD COLUMN IF NOT EXISTS,
--             CREATE OR REPLACE FUNCTION,
--             DROP TRIGGER IF EXISTS + CREATE TRIGGER.

BEGIN;

-- ---------------------------------------------------------------------
-- 1. project_id FK columns on lessons, tasks, decisions.
-- ---------------------------------------------------------------------

ALTER TABLE lessons
    ADD COLUMN IF NOT EXISTS project_id UUID
    REFERENCES projects(id) ON DELETE SET NULL;

ALTER TABLE tasks
    ADD COLUMN IF NOT EXISTS project_id UUID
    REFERENCES projects(id) ON DELETE SET NULL;

ALTER TABLE decisions
    ADD COLUMN IF NOT EXISTS project_id UUID
    REFERENCES projects(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_lessons_project_id
    ON lessons(project_id) WHERE project_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_tasks_project_id
    ON tasks(project_id) WHERE project_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_decisions_project_id
    ON decisions(project_id) WHERE project_id IS NOT NULL;

-- ---------------------------------------------------------------------
-- 2. projects: archived_at, archive_reason, applicable_skills.
-- ---------------------------------------------------------------------

ALTER TABLE projects
    ADD COLUMN IF NOT EXISTS archived_at TIMESTAMPTZ;
ALTER TABLE projects
    ADD COLUMN IF NOT EXISTS archive_reason TEXT;
ALTER TABLE projects
    ADD COLUMN IF NOT EXISTS applicable_skills TEXT[] NOT NULL DEFAULT '{}';

-- ---------------------------------------------------------------------
-- 3. tools_catalog: trigger_keywords for recommend_skills_for_query.
-- ---------------------------------------------------------------------

ALTER TABLE tools_catalog
    ADD COLUMN IF NOT EXISTS trigger_keywords TEXT[] NOT NULL DEFAULT '{}';

-- ---------------------------------------------------------------------
-- 4. Backfill project_id from (bucket, project_text) -> projects(bucket, slug).
--    Idempotent: only updates rows where project_id IS NULL.
-- ---------------------------------------------------------------------

UPDATE lessons l
SET project_id = p.id
FROM projects p
WHERE l.project_id IS NULL
  AND l.project IS NOT NULL
  AND l.bucket = p.bucket
  AND l.project = p.slug;

UPDATE tasks t
SET project_id = p.id
FROM projects p
WHERE t.project_id IS NULL
  AND t.project IS NOT NULL
  AND t.bucket = p.bucket
  AND t.project = p.slug;

UPDATE decisions d
SET project_id = p.id
FROM projects p
WHERE d.project_id IS NULL
  AND d.project IS NOT NULL
  AND d.bucket = p.bucket
  AND d.project = p.slug;

-- ---------------------------------------------------------------------
-- 5. Trigger functions.
-- ---------------------------------------------------------------------

-- 5a. project_lifecycle: emit 'created' on INSERT, 'archived' when status
-- transitions active->archived, 'updated' otherwise.
CREATE OR REPLACE FUNCTION public.notify_project_lifecycle()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    v_event TEXT;
BEGIN
    IF TG_OP = 'INSERT' THEN
        v_event := 'created';
    ELSIF TG_OP = 'UPDATE' THEN
        IF NEW.status = 'archived'
           AND OLD.status IS DISTINCT FROM 'archived' THEN
            v_event := 'archived';
        ELSE
            v_event := 'updated';
        END IF;
    ELSE
        RETURN NEW;
    END IF;

    PERFORM pg_notify(
        'project_lifecycle',
        v_event || ':' || NEW.bucket || '/' || NEW.slug
    );
    RETURN NEW;
END;
$$;

-- 5b. readme_dirty_bucket: signals 'bucket:<name>' on lessons/tasks/
-- decisions/projects/tools_catalog INSERT or UPDATE. tools_catalog rows
-- carry an applicable_buckets array; the trigger fans out one notify
-- per bucket (union of OLD ∪ NEW so a skill removed from a bucket also
-- regenerates that bucket's README).
CREATE OR REPLACE FUNCTION public.notify_readme_dirty_bucket()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    v_buckets TEXT[];
    v_bucket TEXT;
BEGIN
    IF TG_TABLE_NAME = 'tools_catalog' THEN
        IF TG_OP = 'UPDATE' THEN
            v_buckets := ARRAY(
                SELECT DISTINCT b
                FROM unnest(
                    COALESCE(NEW.applicable_buckets, ARRAY[]::TEXT[])
                    || COALESCE(OLD.applicable_buckets, ARRAY[]::TEXT[])
                ) AS t(b)
                WHERE b IS NOT NULL
            );
        ELSE
            v_buckets := COALESCE(NEW.applicable_buckets, ARRAY[]::TEXT[]);
        END IF;

        IF v_buckets IS NOT NULL THEN
            FOREACH v_bucket IN ARRAY v_buckets LOOP
                PERFORM pg_notify('readme_dirty', 'bucket:' || v_bucket);
            END LOOP;
        END IF;
    ELSE
        IF NEW.bucket IS NOT NULL THEN
            PERFORM pg_notify('readme_dirty', 'bucket:' || NEW.bucket);
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

-- 5c. readme_dirty_project: signals 'project:<bucket>/<slug>' on
-- lessons/tasks/decisions INSERT/UPDATE when project_id IS NOT NULL.
-- The bucket+slug are looked up from projects so we always emit the
-- canonical FK-derived identity.
CREATE OR REPLACE FUNCTION public.notify_readme_dirty_project()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    v_bucket TEXT;
    v_slug TEXT;
BEGIN
    IF NEW.project_id IS NULL THEN
        RETURN NEW;
    END IF;
    SELECT bucket, slug INTO v_bucket, v_slug
    FROM projects
    WHERE id = NEW.project_id;
    IF v_bucket IS NULL OR v_slug IS NULL THEN
        RETURN NEW;
    END IF;
    PERFORM pg_notify(
        'readme_dirty',
        'project:' || v_bucket || '/' || v_slug
    );
    RETURN NEW;
END;
$$;

-- 5d. catalog_changed: advisory channel for downstream caches that
-- track tools_catalog. Payload: '<TG_OP>:<name>'.
CREATE OR REPLACE FUNCTION public.notify_catalog_changed()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    PERFORM pg_notify('catalog_changed', TG_OP || ':' || NEW.name);
    RETURN NEW;
END;
$$;

-- ---------------------------------------------------------------------
-- 6. Attach triggers (idempotent: DROP IF EXISTS + CREATE).
-- ---------------------------------------------------------------------

DROP TRIGGER IF EXISTS trg_projects_lifecycle ON projects;
CREATE TRIGGER trg_projects_lifecycle
    AFTER INSERT OR UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION notify_project_lifecycle();

-- readme_dirty_bucket on 5 tables.
DROP TRIGGER IF EXISTS trg_lessons_readme_dirty_bucket ON lessons;
CREATE TRIGGER trg_lessons_readme_dirty_bucket
    AFTER INSERT OR UPDATE ON lessons
    FOR EACH ROW EXECUTE FUNCTION notify_readme_dirty_bucket();

DROP TRIGGER IF EXISTS trg_tasks_readme_dirty_bucket ON tasks;
CREATE TRIGGER trg_tasks_readme_dirty_bucket
    AFTER INSERT OR UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION notify_readme_dirty_bucket();

DROP TRIGGER IF EXISTS trg_decisions_readme_dirty_bucket ON decisions;
CREATE TRIGGER trg_decisions_readme_dirty_bucket
    AFTER INSERT OR UPDATE ON decisions
    FOR EACH ROW EXECUTE FUNCTION notify_readme_dirty_bucket();

DROP TRIGGER IF EXISTS trg_projects_readme_dirty_bucket ON projects;
CREATE TRIGGER trg_projects_readme_dirty_bucket
    AFTER INSERT OR UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION notify_readme_dirty_bucket();

DROP TRIGGER IF EXISTS trg_tools_catalog_readme_dirty_bucket ON tools_catalog;
CREATE TRIGGER trg_tools_catalog_readme_dirty_bucket
    AFTER INSERT OR UPDATE ON tools_catalog
    FOR EACH ROW EXECUTE FUNCTION notify_readme_dirty_bucket();

-- readme_dirty_project on lessons/tasks/decisions (project_id-bearing).
DROP TRIGGER IF EXISTS trg_lessons_readme_dirty_project ON lessons;
CREATE TRIGGER trg_lessons_readme_dirty_project
    AFTER INSERT OR UPDATE ON lessons
    FOR EACH ROW EXECUTE FUNCTION notify_readme_dirty_project();

DROP TRIGGER IF EXISTS trg_tasks_readme_dirty_project ON tasks;
CREATE TRIGGER trg_tasks_readme_dirty_project
    AFTER INSERT OR UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION notify_readme_dirty_project();

DROP TRIGGER IF EXISTS trg_decisions_readme_dirty_project ON decisions;
CREATE TRIGGER trg_decisions_readme_dirty_project
    AFTER INSERT OR UPDATE ON decisions
    FOR EACH ROW EXECUTE FUNCTION notify_readme_dirty_project();

-- catalog_changed.
DROP TRIGGER IF EXISTS trg_tools_catalog_changed ON tools_catalog;
CREATE TRIGGER trg_tools_catalog_changed
    AFTER INSERT OR UPDATE ON tools_catalog
    FOR EACH ROW EXECUTE FUNCTION notify_catalog_changed();

-- ---------------------------------------------------------------------
-- 7. schema_migrations row (matches the manual convention 0033 used —
-- the migration runner bug tracked in task 7ce1f79e is still open).
-- ---------------------------------------------------------------------

INSERT INTO schema_migrations (version, checksum)
VALUES (
    '0034',
    md5('0034_awareness_layer_v1')
) ON CONFLICT (version) DO NOTHING;

COMMIT;

-- ---------------------------------------------------------------------
-- Verification queries (run after apply; see atomic task A.3):
--   SELECT count(*) FROM lessons   WHERE project_id IS NOT NULL;
--   SELECT count(*) FROM tasks     WHERE project_id IS NOT NULL;
--   SELECT count(*) FROM decisions WHERE project_id IS NOT NULL;
-- ---------------------------------------------------------------------
