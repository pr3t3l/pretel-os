# Module 2: Data Layer

## What
Implement the PostgreSQL schema defined in `docs/DATA_MODEL.md` — 21 canonical tables across Phase 1 (MVP) and Phase 2 (extended knowledge), extensions, functions, triggers, views, seed data, and a migration runner.

## Authority
`docs/DATA_MODEL.md` is the canonical specification. Every table, column, index, function, trigger, and view comes from that document. Deviations are explicit and documented in the runbook.

## Inputs
- Live Postgres 16 instance with pgvector 0.6.0, pg_trgm, btree_gin available
- `pretel_os` role with LOGIN + password, `pretel_os` database owned by that role
- `~/.env.pretel_os` supplying `DATABASE_URL`

## Outputs
- 24 migration files in `migrations/` (0000–0023), each idempotent
- `infra/db/migrate.py` — runs pending migrations, records SHA256 checksums in `schema_migrations`
- `infra/db/health_check.py` — verifies tables, extensions, functions, triggers, seeds, partitions
- Monthly partitions for `routing_logs`, `usage_logs`, `llm_calls` (current + next month)
- `control_registry` seeded with 6 operator controls
- `runbooks/module_2_data_layer.md` — connect / migrate / add-migration / rollback

## Documented deviations from DATA_MODEL.md
1. **HNSW indexes omitted.** pgvector 0.6.0 caps HNSW at 2000 dimensions; `vector(3072)` exceeds that. Re-enable when pgvector is upgraded or volume justifies IVFFlat.
2. **`control_registry.next_due_at` is maintained by a trigger**, not `GENERATED ALWAYS AS ... STORED`. Postgres classifies `timestamptz + interval` as STABLE (day length is timezone-dependent), which STORED generation rejects. A `BEFORE INSERT/UPDATE` trigger preserves the exact read contract (`next_due_at = last_completed_at + cadence_days`).

## Constraints
- Forward-only migrations per `DATA_MODEL §9.3`
- No secrets in git (`CONSTITUTION §3.4`)
- Every migration idempotent (`IF NOT EXISTS` / `DO $$ ... IF NOT EXISTS ... END $$`)
- Each migration records checksum so later edits to an applied file fail loudly
