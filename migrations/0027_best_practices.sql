-- Migration 0027 — best_practices table
-- Module 0.X — Knowledge Architecture
-- Spec: specs/module-0x-knowledge-architecture/spec.md §5.5
-- Created: 2026-04-28
--
-- Reusable PROCESS guidance — narrative rules ("always X when Y"). Distinct
-- from `patterns` (DATA_MODEL §5.1) which holds CODE snippets and templates.
--
-- HNSW index deferred per ADR-024 (DECISIONS.md):
--   pgvector 0.6.0 limits HNSW to 2000 dims; embedding is vector(3072).
--   At current scale (<5K vectors) sequential scan is sufficient (10-50ms).
--   Re-add when pgvector >= 0.7 or volume crosses ~50K threshold.
--
-- Rollback semantics: previous_guidance + previous_rationale columns
-- enable single-step rollback. The MCP tool best_practice_record copies
-- current values to previous_* BEFORE overwriting on UPDATE.

BEGIN;

CREATE TABLE IF NOT EXISTS best_practices (
    id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    title                text NOT NULL,
    guidance             text NOT NULL,                              -- "always X when Y", prose
    rationale            text,                                       -- why this works
    domain               text NOT NULL                               -- categorization
                         CHECK (domain IN ('process','convention','workflow','communication')),
    scope                text NOT NULL DEFAULT 'global',             -- 'global' | 'bucket:<name>' | 'project:<bucket>/<name>'
    applicable_buckets   text[] NOT NULL DEFAULT '{}',
    tags                 text[] NOT NULL DEFAULT '{}',
    active               boolean NOT NULL DEFAULT true,
    source               text NOT NULL
                         CHECK (source IN ('operator','derived_from_lessons','migration')),
    derived_from_lessons uuid[] DEFAULT '{}',                        -- provenance from reflection worker
    previous_guidance    text,                                       -- single-step rollback target
    previous_rationale   text,                                       -- single-step rollback companion
    superseded_by        uuid REFERENCES best_practices(id),         -- explicit replacement chain
    embedding            vector(3072),                               -- text-embedding-3-large
    created_at           timestamptz NOT NULL DEFAULT now(),
    updated_at           timestamptz NOT NULL DEFAULT now()
);

-- HNSW index deferred per ADR-024:
-- CREATE INDEX idx_best_practices_embedding_hnsw
--   ON best_practices USING hnsw (embedding vector_cosine_ops)
--   WHERE active;

CREATE INDEX IF NOT EXISTS idx_best_practices_scope
    ON best_practices(scope)
    WHERE active;

CREATE INDEX IF NOT EXISTS idx_best_practices_applicable_buckets
    ON best_practices USING gin(applicable_buckets);

CREATE INDEX IF NOT EXISTS idx_best_practices_tags
    ON best_practices USING gin(tags);

CREATE INDEX IF NOT EXISTS idx_best_practices_domain
    ON best_practices(domain)
    WHERE active;

CREATE INDEX IF NOT EXISTS idx_best_practices_superseded
    ON best_practices(superseded_by)
    WHERE superseded_by IS NOT NULL;

CREATE TRIGGER trg_set_updated_at_best_practices
    BEFORE UPDATE ON best_practices
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();

INSERT INTO schema_migrations (version, checksum)
VALUES (
    '0027',
    md5('0027_best_practices_v1_hnsw_deferred')
)
ON CONFLICT (version) DO NOTHING;

COMMIT;
