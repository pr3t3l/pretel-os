-- 0001_extensions.sql
-- Source: DATA_MODEL.md §1.4

CREATE EXTENSION IF NOT EXISTS vector;       -- pgvector
CREATE EXTENSION IF NOT EXISTS pg_trgm;      -- trigram similarity for fuzzy text match
CREATE EXTENSION IF NOT EXISTS btree_gin;    -- GIN on scalar columns alongside arrays
