-- Migration 0028 — decisions table amendment
-- Module 0.X — Knowledge Architecture
-- Spec: specs/module-0x-knowledge-architecture/spec.md §5.2
-- Created: 2026-04-28
--
-- Adds 7 columns to existing `decisions` (DATA_MODEL §5.2, created in
-- migration 0018_phase2_tables.sql). Existing columns unchanged:
-- id, bucket, project, projects_indexed_id, client_id, title, context,
-- decision, consequences, alternatives, status, superseded_by_id,
-- embedding, created_at.
--
-- New columns enable typed decision capture (scope=architectural|process|
-- product|operational), cross-bucket applicability, formal ADR numbering,
-- severity ranking, and provenance from lessons that crystallized into
-- a decision.

BEGIN;

-- 1. scope: distinguishes architectural ADRs from process/product/operational decisions.
-- DEFAULT 'operational' is the catch-all for legacy rows and inserts without
-- explicit scope. Formal ADRs MUST set scope='architectural' explicitly.
ALTER TABLE decisions
    ADD COLUMN IF NOT EXISTS scope text NOT NULL DEFAULT 'operational'
    CHECK (scope IN ('architectural','process','product','operational'));

-- 2. applicable_buckets: cross-bucket scope (empty = scoped to bucket of origin)
ALTER TABLE decisions
    ADD COLUMN IF NOT EXISTS applicable_buckets text[] NOT NULL DEFAULT '{}';

-- 3. decided_by: provenance
ALTER TABLE decisions
    ADD COLUMN IF NOT EXISTS decided_by text NOT NULL DEFAULT 'operator';

-- 4. tags: free-form filtering
ALTER TABLE decisions
    ADD COLUMN IF NOT EXISTS tags text[] NOT NULL DEFAULT '{}';

-- 5. severity: load-bearing decision vs minor process tweak
ALTER TABLE decisions
    ADD COLUMN IF NOT EXISTS severity text DEFAULT 'normal';

-- 6. adr_number: formal ADR numbering. NULL allowed for non-formal.
-- UNIQUE in Postgres allows multiple NULLs.
ALTER TABLE decisions
    ADD COLUMN IF NOT EXISTS adr_number integer;

ALTER TABLE decisions
    DROP CONSTRAINT IF EXISTS decisions_adr_number_key;

ALTER TABLE decisions
    ADD CONSTRAINT decisions_adr_number_key UNIQUE (adr_number);

-- 7. derived_from_lessons: provenance from one or more lessons
ALTER TABLE decisions
    ADD COLUMN IF NOT EXISTS derived_from_lessons uuid[] DEFAULT '{}';

-- New indexes per spec §5.2
CREATE INDEX IF NOT EXISTS idx_decisions_scope_status
    ON decisions(scope, status);

CREATE INDEX IF NOT EXISTS idx_decisions_applicable_buckets
    ON decisions USING gin(applicable_buckets);

CREATE INDEX IF NOT EXISTS idx_decisions_tags
    ON decisions USING gin(tags);

INSERT INTO schema_migrations (version, checksum)
VALUES (
    '0028',
    md5('0028_decisions_amendment_v2_default_operational')
)
ON CONFLICT (version) DO NOTHING;

COMMIT;
