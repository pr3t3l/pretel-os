-- Migration 0031 — layer-loader cache invalidation triggers
-- Module 4 Phase B B.8 — closes M4 Phase B Layer Loader cache wiring
-- Created: 2026-04-29
--
-- Adds AFTER INSERT OR UPDATE OR DELETE triggers on the four tables
-- listed in layer_loader_contract.md §6 (operator_preferences, decisions,
-- best_practices, lessons). Each trigger invokes the shared function
-- notify_cache_invalidate() which emits:
--
--   pg_notify('layer_loader_cache', '<table>:<op>')
--
-- The Router's cache.py listens on the 'layer_loader_cache' channel from
-- a daemon thread and clears the in-memory LayerBundle cache on receipt.
-- Per Q2 decision (specs/router/phase_b_close.md §1): one shared trigger
-- function attached to four tables — keeps the contract surface narrow
-- and avoids spreading NOTIFY calls across every MCP tool that mutates
-- these tables.
--
-- Idempotent: DROP TRIGGER IF EXISTS + CREATE OR REPLACE FUNCTION.

BEGIN;

CREATE OR REPLACE FUNCTION public.notify_cache_invalidate()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- Single channel name; the payload identifies the table and op for
    -- listeners that want fine-grained invalidation. The Router's
    -- cache.py treats any payload as "clear all" for now.
    PERFORM pg_notify(
        'layer_loader_cache',
        TG_TABLE_NAME || ':' || TG_OP
    );
    -- Return value matters for INSERT/UPDATE (NEW) vs DELETE (OLD).
    IF (TG_OP = 'DELETE') THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$;

-- Attach to the four contract §6 tables. AFTER fires post-commit-of-row
-- so listeners only see committed state.
DO $$
BEGIN
    -- operator_preferences (L0 + L1)
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'trg_op_prefs_cache_invalidate'
    ) THEN
        CREATE TRIGGER trg_op_prefs_cache_invalidate
            AFTER INSERT OR UPDATE OR DELETE ON operator_preferences
            FOR EACH ROW EXECUTE FUNCTION notify_cache_invalidate();
    END IF;

    -- decisions (L1 + L2)
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'trg_decisions_cache_invalidate'
    ) THEN
        CREATE TRIGGER trg_decisions_cache_invalidate
            AFTER INSERT OR UPDATE OR DELETE ON decisions
            FOR EACH ROW EXECUTE FUNCTION notify_cache_invalidate();
    END IF;

    -- best_practices (L2 + L4)
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'trg_best_practices_cache_invalidate'
    ) THEN
        CREATE TRIGGER trg_best_practices_cache_invalidate
            AFTER INSERT OR UPDATE OR DELETE ON best_practices
            FOR EACH ROW EXECUTE FUNCTION notify_cache_invalidate();
    END IF;

    -- lessons (L4)
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'trg_lessons_cache_invalidate'
    ) THEN
        CREATE TRIGGER trg_lessons_cache_invalidate
            AFTER INSERT OR UPDATE OR DELETE ON lessons
            FOR EACH ROW EXECUTE FUNCTION notify_cache_invalidate();
    END IF;
END$$;

INSERT INTO schema_migrations (version, checksum)
VALUES (
    '0031',
    md5('0031_layer_cache_invalidation_triggers_v1')
)
ON CONFLICT (version) DO NOTHING;

COMMIT;
