#!/usr/bin/env python3
"""Apply SQL migrations under migrations/ in numeric order against pretel_os.

Reads DATABASE_URL from the environment (set via ~/.env.pretel_os or CI).
Each migration is applied inside a single transaction via psql. A SHA256
checksum of the file bytes is recorded in schema_migrations so later changes
to an already-applied file raise a clear error.

Usage:
    DATABASE_URL=postgresql://... python3 infra/db/migrate.py
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = REPO_ROOT / "migrations"
VERSION_RE = re.compile(r"^(\d{4})_.+\.sql$")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def run_psql(database_url: str, sql: str) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["psql", "-v", "ON_ERROR_STOP=1", "-X", "-q", "-d", database_url, "-c", sql],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def run_psql_file(database_url: str, path: Path) -> tuple[int, str, str]:
    proc = subprocess.run(
        [
            "psql",
            "-v", "ON_ERROR_STOP=1",
            "-X",
            "-1",               # single transaction
            "-q",
            "-d", database_url,
            "-f", str(path),
        ],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def ensure_tracking_table(database_url: str) -> None:
    bootstrap = MIGRATIONS_DIR / "0000_schema_migrations.sql"
    rc, _out, err = run_psql_file(database_url, bootstrap)
    if rc != 0:
        print(f"Failed to create schema_migrations: {err}", file=sys.stderr)
        sys.exit(1)


def applied_versions(database_url: str) -> dict[str, str]:
    rc, out, err = run_psql(
        database_url,
        "COPY (SELECT version, checksum FROM schema_migrations ORDER BY version) TO STDOUT WITH (FORMAT csv)",
    )
    if rc != 0:
        print(f"Could not read schema_migrations: {err}", file=sys.stderr)
        sys.exit(1)
    result: dict[str, str] = {}
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        version, checksum = line.split(",", 1)
        result[version] = checksum
    return result


def migration_files() -> list[Path]:
    files = sorted(p for p in MIGRATIONS_DIR.glob("*.sql") if VERSION_RE.match(p.name))
    if not files:
        print(f"No migrations found in {MIGRATIONS_DIR}", file=sys.stderr)
        sys.exit(1)
    return files


def record_applied(database_url: str, version: str, checksum: str) -> None:
    rc, _out, err = run_psql(
        database_url,
        f"INSERT INTO schema_migrations (version, checksum) VALUES ('{version}', '{checksum}')",
    )
    if rc != 0:
        print(f"Failed to record {version}: {err}", file=sys.stderr)
        sys.exit(1)


def main() -> int:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is not set. Source ~/.env.pretel_os first.", file=sys.stderr)
        return 2

    ensure_tracking_table(database_url)
    already = applied_versions(database_url)

    applied = 0
    skipped = 0
    for path in migration_files():
        version = path.stem  # '0007_skill_versions'
        checksum = sha256_of(path)
        prior = already.get(version)
        if prior == checksum:
            print(f"skip   {version}")
            skipped += 1
            continue
        if prior and prior != checksum:
            print(
                f"ERROR  {version} already applied with a different checksum "
                f"(stored={prior[:8]}…, now={checksum[:8]}…). Refuse to re-run.",
                file=sys.stderr,
            )
            return 3

        print(f"apply  {version}")
        rc, _out, err = run_psql_file(database_url, path)
        if rc != 0:
            print(f"       FAILED: {err.strip()}", file=sys.stderr)
            return 4
        record_applied(database_url, version, checksum)
        applied += 1

    print(f"\nDone. {applied} applied, {skipped} skipped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
