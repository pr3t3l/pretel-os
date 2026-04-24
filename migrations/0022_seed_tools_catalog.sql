-- 0022_seed_tools_catalog.sql
-- Source: DATA_MODEL.md §2.2 (catalog will be populated by the skills/tools inventory work)
--
-- Placeholder: the canonical inventory of skills and MCP tools is tracked in
-- INTEGRATIONS.md and skills/*.md. Seeding happens in later modules once those
-- definitions are authoritative (Module 3 populates skills; Module 4 populates MCP tools).
-- No rows inserted here by design — keeping the migration file in sequence preserves
-- numbering and lets a future migration append seed rows idempotently.

SELECT 1 WHERE false; -- no-op so the runner sees a valid SQL statement
