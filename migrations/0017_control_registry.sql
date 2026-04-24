-- 0017_control_registry.sql
-- Source: DATA_MODEL.md §5.6
--
-- Deviation from spec: next_due_at is a plain TIMESTAMPTZ with a BEFORE INSERT/UPDATE
-- trigger, not a GENERATED STORED column. Reason: Postgres classifies
-- (timestamptz + interval) as STABLE (day-length depends on timezone), and STORED
-- generated columns require IMMUTABLE expressions. The trigger preserves the read
-- contract of the spec: next_due_at stays in sync with last_completed_at + cadence_days
-- without application code needing to touch it.

CREATE TABLE IF NOT EXISTS control_registry (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    control_name      TEXT NOT NULL UNIQUE,
    description       TEXT NOT NULL,
    cadence_days      INTEGER NOT NULL,
    owner             TEXT NOT NULL DEFAULT 'operator',
    evidence_required TEXT NOT NULL,
    last_completed_at TIMESTAMPTZ,
    last_evidence     TEXT,
    next_due_at       TIMESTAMPTZ,
    alert_sent_at     TIMESTAMPTZ,
    active            BOOLEAN NOT NULL DEFAULT true,
    notes             TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_control_overdue ON control_registry(next_due_at) WHERE active = true;

CREATE OR REPLACE FUNCTION set_control_next_due_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.next_due_at :=
        CASE
            WHEN NEW.last_completed_at IS NULL THEN NULL
            ELSE NEW.last_completed_at + make_interval(days => NEW.cadence_days)
        END;
    RETURN NEW;
END;
$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_control_next_due_at') THEN
        CREATE TRIGGER trg_control_next_due_at
            BEFORE INSERT OR UPDATE OF last_completed_at, cadence_days
            ON control_registry
            FOR EACH ROW EXECUTE FUNCTION set_control_next_due_at();
    END IF;
END$$;
