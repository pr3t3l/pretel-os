-- Migration 0025 — operator_preferences table
-- Module 0.X — Knowledge Architecture
-- Spec: specs/module-0x-knowledge-architecture/spec.md §5.3
-- Created: 2026-04-28
--
-- Operator-controlled facts and overrides (communication style, tooling,
-- workflow, identity, language, schedule). Atomic upsert via UNIQUE
-- (category, key, scope). No embedding — direct lookup.

BEGIN;

CREATE TABLE IF NOT EXISTS operator_preferences (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    category        text NOT NULL
                    CHECK (category IN ('communication','tooling','workflow','identity','language','schedule')),
    key             text NOT NULL,
    value           text NOT NULL,
    scope           text NOT NULL DEFAULT 'global',
    active          boolean NOT NULL DEFAULT true,
    source          text NOT NULL
                    CHECK (source IN ('operator_explicit','inferred','migration')),
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now(),
    metadata        jsonb DEFAULT '{}'::jsonb,
    UNIQUE(category, key, scope)
);

CREATE INDEX IF NOT EXISTS idx_preferences_scope_active
    ON operator_preferences(scope)
    WHERE active;

CREATE INDEX IF NOT EXISTS idx_preferences_category_active
    ON operator_preferences(category)
    WHERE active;

CREATE TRIGGER trg_set_updated_at_operator_preferences
    BEFORE UPDATE ON operator_preferences
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();

INSERT INTO schema_migrations (version, checksum)
VALUES (
    '0025',
    md5('0025_operator_preferences_v1')
)
ON CONFLICT (version) DO NOTHING;

COMMIT;
