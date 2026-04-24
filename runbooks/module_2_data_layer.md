# Module 2 Runbook: Data Layer

## Date: 2026-04-24

## Scope
Canonical schema per `docs/DATA_MODEL.md`: 21 tables, extensions, functions, triggers, views, monthly partitions, and seed data.

## Connection

The `pretel_os` database is owned by the `pretel_os` role. `~/.env.pretel_os` holds:

```
DATABASE_URL=postgresql://pretel_os:pretel_os_temp_2026@127.0.0.1:5432/pretel_os
```

### psql

```bash
set -a; . ~/.env.pretel_os; set +a
PGPASSWORD=$(echo "$DATABASE_URL" | sed 's|.*://[^:]*:\([^@]*\)@.*|\1|') \
  psql -U pretel_os -h 127.0.0.1 -d pretel_os
```

Or more simply, export `PGPASSWORD` once and use `psql -U pretel_os -h 127.0.0.1 -d pretel_os`.

### Python

```python
import os
os.environ["DATABASE_URL"]  # read from env
# use psycopg or psql subprocess
```

## Running migrations

```bash
set -a; . ~/.env.pretel_os; set +a
python3 infra/db/migrate.py
```

Output lines prefix with `skip` (already applied, checksum matches), `apply` (just applied), or `ERROR` (checksum drift on an already-applied file — refuse to re-run).

Each migration runs in a single transaction (`psql -1`). On failure, all DDL from that file rolls back.

## Adding a new migration

1. Pick the next available 4-digit prefix (currently `0024_*`).
2. Create `migrations/NNNN_short_description.sql`. Make it idempotent:
   - Tables: `CREATE TABLE IF NOT EXISTS …`
   - Enums: wrap in `DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname=…) THEN CREATE TYPE …; END IF; END $$;`
   - Triggers: `DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname=…) THEN CREATE TRIGGER …; END IF; END $$;`
   - Functions: `CREATE OR REPLACE FUNCTION …`
   - Indexes: `CREATE INDEX IF NOT EXISTS …`
3. Re-run `python3 infra/db/migrate.py`. New file applies; prior files skip.
4. Update `infra/db/health_check.py` if the new migration adds a canonical table, extension, function, trigger, or seeded row that should be verified.
5. Commit both the migration file and any health-check updates together.

## Running the health check

```bash
set -a; . ~/.env.pretel_os; set +a
python3 infra/db/health_check.py
```

Prints `[OK]` / `[FAIL]` per item. Exits non-zero on any failure.

## Rollback

`DATA_MODEL §9.3` is forward-only. Emergency rollback options:

1. **Inverse migration** (preferred). Create `migrations/NNNN_rollback_description.sql` with the undo statements (`DROP INDEX …`, `ALTER TABLE … DROP COLUMN …`). Document the reason inline.
2. **Partition drop** for retention: logs are kept via partitioning so `DROP TABLE routing_logs_YYYY_MM` is the supported way to purge — no DELETE.
3. **Full restore** from the daily pg_backup tarball (`infra/backup/pg_backup.sh`, runbook §5). Only if the database is unusable.

Never edit an already-applied migration file — the checksum guard in `migrate.py` will refuse the next run. If you must change a prior migration's intent, add a new migration that reshapes the schema.

## Schema state: documented deviations

Two deviations from `docs/DATA_MODEL.md` are baked into the current migrations. Both are explicit compromises with Postgres/pgvector constraints that the spec did not account for.

### 1. HNSW indexes omitted

Migrations 0002, 0003, 0004, 0008, 0018 intentionally skip `CREATE INDEX … USING hnsw (embedding vector_cosine_ops)`. Replacement comment in each file:

```
-- HNSW index deferred: pgvector 0.6.0 limits HNSW to 2000 dims; vector(3072) exceeds this.
-- At current scale (<5k vectors) sequential scan is sufficient.
-- Re-add when pgvector is upgraded or volume justifies IVFFlat.
```

Embedding columns remain `vector(3072)` as specified. Semantic search works via sequential scan (acceptable below ~10k vectors per `DATA_MODEL §8`).

**To re-enable** once pgvector is upgraded or an IVFFlat index is acceptable:
- Either upgrade pgvector to ≥0.7 and migrate columns to `halfvec(3072)` (breaking change — constitutional amendment per `DATA_MODEL §11.5`), or
- Add an IVFFlat index: `CREATE INDEX … USING ivfflat (embedding vector_cosine_ops) WITH (lists = N)`.

### 2. `control_registry.next_due_at` is trigger-maintained, not GENERATED STORED

The spec in `DATA_MODEL §5.6` defines:
```sql
next_due_at TIMESTAMPTZ GENERATED ALWAYS AS (last_completed_at + (cadence_days || ' days')::interval) STORED
```
Postgres rejects every variant of this because `timestamptz + interval` is classified as STABLE (day length depends on `TimeZone` — confirmed via `pg_proc.provolatile='s'` on `timestamptz_pl_interval`). STORED generation requires IMMUTABLE.

Migration `0017_control_registry.sql` instead defines `next_due_at` as a plain `TIMESTAMPTZ` plus:

```sql
CREATE FUNCTION set_control_next_due_at() -- sets NEW.next_due_at
CREATE TRIGGER trg_control_next_due_at BEFORE INSERT OR UPDATE OF last_completed_at, cadence_days …
```

Read contract is preserved: any `SELECT next_due_at FROM control_registry` returns the same value the spec promised. No application code touches `next_due_at` directly.

## Connection troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `password authentication failed for user "pretel_os"` | Wrong/missing `~/.env.pretel_os` | Re-source; check contents; rotate password via `ALTER ROLE pretel_os PASSWORD …` |
| `FATAL: role "pretel_os" does not exist` | Role not created | `sudo -u postgres psql -c "CREATE ROLE pretel_os LOGIN PASSWORD '…';"` |
| `permission denied to create extension "vector"` | `pretel_os` lacks superuser | Run `CREATE EXTENSION` as postgres once per database |
| `peer authentication failed for user "postgres"` | Trying peer auth as wrong OS user | Use `sudo -u postgres psql …` |

## Current state

- Role / DB: `pretel_os` / `pretel_os` (both created 2026-04-24)
- Extensions: `vector 0.6.0`, `pg_trgm`, `btree_gin`, `plpgsql`
- Migrations applied: 0000–0023 (24 files)
- Tables: 21 canonical + 6 monthly partition children + `schema_migrations` = 28 relations
- Controls seeded: 6 (scout_audit, restore_drill, key_rotation_anthropic, key_rotation_openai, pricing_verification, uptime_review)
- Partitions: `{routing_logs,usage_logs,llm_calls}_2026_04` and `_2026_05`

## Pending operator actions

1. Rotate `pretel_os` password away from `pretel_os_temp_2026`:
   ```
   sudo -u postgres psql -c "ALTER ROLE pretel_os PASSWORD '…';"
   ```
   Update `~/.env.pretel_os` with the new password.
2. Upgrade pgvector and re-enable HNSW indexes (or add IVFFlat) when vector volume warrants it.
3. Dream Engine (future module) creates next month's partitions on the 25th of each month via `CREATE TABLE … PARTITION OF …`.
