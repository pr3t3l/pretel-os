-- 0018_phase2_tables.sql
-- Source: DATA_MODEL.md §5.1–5.5 (patterns, decisions, gotchas, contacts, ideas)

-- §5.1 patterns
CREATE TABLE IF NOT EXISTS patterns (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name               TEXT NOT NULL,
    description        TEXT NOT NULL,
    language           TEXT,
    code               TEXT NOT NULL,
    use_case           TEXT NOT NULL,
    applicable_buckets TEXT[] NOT NULL DEFAULT '{}',
    client_id          UUID,
    tags               TEXT[] NOT NULL DEFAULT '{}',
    embedding          vector(3072),
    usage_count        INTEGER NOT NULL DEFAULT 0,
    version            INTEGER NOT NULL DEFAULT 1,
    previous_content   TEXT,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- HNSW index deferred: pgvector 0.6.0 limits HNSW to 2000 dims; vector(3072) exceeds this.
-- At current scale (<5k vectors) sequential scan is sufficient.
-- Re-add when pgvector is upgraded or volume justifies IVFFlat.

CREATE INDEX IF NOT EXISTS idx_patterns_tags ON patterns USING gin(tags);
CREATE INDEX IF NOT EXISTS idx_patterns_client ON patterns(client_id) WHERE client_id IS NOT NULL;

-- §5.2 decisions
CREATE TABLE IF NOT EXISTS decisions (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bucket               TEXT NOT NULL,
    project              TEXT NOT NULL,
    projects_indexed_id  UUID REFERENCES projects_indexed(id),
    client_id            UUID,
    title                TEXT NOT NULL,
    context              TEXT NOT NULL,
    decision             TEXT NOT NULL,
    consequences         TEXT NOT NULL,
    alternatives         TEXT,
    status               TEXT NOT NULL DEFAULT 'active',
    superseded_by_id     UUID REFERENCES decisions(id),
    embedding            vector(3072),
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_decisions_project ON decisions(bucket, project);
CREATE INDEX IF NOT EXISTS idx_decisions_indexed_project ON decisions(projects_indexed_id) WHERE projects_indexed_id IS NOT NULL;
-- HNSW index deferred: pgvector 0.6.0 limits HNSW to 2000 dims; vector(3072) exceeds this.
-- At current scale (<5k vectors) sequential scan is sufficient.
-- Re-add when pgvector is upgraded or volume justifies IVFFlat.

CREATE INDEX IF NOT EXISTS idx_decisions_client ON decisions(client_id) WHERE client_id IS NOT NULL;

-- §5.3 gotchas
CREATE TABLE IF NOT EXISTS gotchas (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title              TEXT NOT NULL,
    trigger_context    TEXT NOT NULL,
    what_goes_wrong    TEXT NOT NULL,
    workaround         TEXT,
    severity           SMALLINT NOT NULL DEFAULT 3,
    applicable_buckets TEXT[] NOT NULL DEFAULT '{}',
    tags               TEXT[] NOT NULL DEFAULT '{}',
    embedding          vector(3072),
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- HNSW index deferred: pgvector 0.6.0 limits HNSW to 2000 dims; vector(3072) exceeds this.
-- At current scale (<5k vectors) sequential scan is sufficient.
-- Re-add when pgvector is upgraded or volume justifies IVFFlat.

CREATE INDEX IF NOT EXISTS idx_gotchas_severity ON gotchas(severity);

-- §5.4 contacts
CREATE TABLE IF NOT EXISTS contacts (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                TEXT NOT NULL,
    role                TEXT,
    company             TEXT,
    relationship        TEXT,
    email               TEXT,
    phone               TEXT,
    notes               TEXT,
    associated_buckets  TEXT[] NOT NULL DEFAULT '{}',
    associated_projects TEXT[] NOT NULL DEFAULT '{}',
    metadata            JSONB NOT NULL DEFAULT '{}',
    embedding           vector(3072),
    last_contact_at     TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at          TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_contacts_relationship ON contacts(relationship) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_contacts_projects ON contacts USING gin(associated_projects);
CREATE INDEX IF NOT EXISTS idx_contacts_name_trgm ON contacts USING gin(name gin_trgm_ops);

-- §5.5 ideas
CREATE TABLE IF NOT EXISTS ideas (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    summary            TEXT NOT NULL,
    full_text          TEXT,
    bucket_hint        TEXT,
    client_id          UUID,
    category           TEXT,
    effort_estimate    TEXT,
    status             TEXT NOT NULL DEFAULT 'new',
    promoted_to        TEXT,
    related_lessons    UUID[] NOT NULL DEFAULT '{}',
    related_tools      TEXT[] NOT NULL DEFAULT '{}',
    related_projects   TEXT[] NOT NULL DEFAULT '{}',
    embedding          vector(3072),
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    reviewed_at        TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_ideas_status ON ideas(status, created_at DESC);
-- HNSW index deferred: pgvector 0.6.0 limits HNSW to 2000 dims; vector(3072) exceeds this.
-- At current scale (<5k vectors) sequential scan is sufficient.
-- Re-add when pgvector is upgraded or volume justifies IVFFlat.

CREATE INDEX IF NOT EXISTS idx_ideas_related_lessons ON ideas USING gin(related_lessons);
CREATE INDEX IF NOT EXISTS idx_ideas_related_tools ON ideas USING gin(related_tools);
CREATE INDEX IF NOT EXISTS idx_ideas_related_projects ON ideas USING gin(related_projects);
CREATE INDEX IF NOT EXISTS idx_ideas_client ON ideas(client_id) WHERE client_id IS NOT NULL;
