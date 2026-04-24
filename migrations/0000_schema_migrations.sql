-- 0000_schema_migrations.sql
-- Source: DATA_MODEL.md §9.2
-- Tracking table for applied migrations.

CREATE TABLE IF NOT EXISTS schema_migrations (
    version    TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    checksum   TEXT NOT NULL
);
