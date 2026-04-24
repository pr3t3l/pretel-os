#!/bin/bash
# infra/backup/pg_backup.sh
# Source: DATA_MODEL §10.1
set -euo pipefail

BACKUP_DIR="/home/pretel/backups/pretel-os-db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DUMP_FILE="${BACKUP_DIR}/pretel_os_${TIMESTAMP}.dump"

mkdir -p "${BACKUP_DIR}"

# Phase 1: target whatever DB exists (n8n for now, pretel_os once Module 2 creates it)
DB_NAME="${1:-pretel_os}"

pg_dump -Fc -d "${DB_NAME}" -f "${DUMP_FILE}"

# Verify dump integrity
if ! pg_restore --list "${DUMP_FILE}" > /dev/null 2>&1; then
    echo "ERROR: dump verification failed, aborting. File preserved: ${DUMP_FILE}" >&2
    exit 1
fi

# Encrypt (requires GPG key 'backup@pretel' to exist)
if gpg --list-keys backup@pretel > /dev/null 2>&1; then
    gpg --encrypt --recipient backup@pretel \
        --output "${DUMP_FILE}.gpg" "${DUMP_FILE}"

    if [ -s "${DUMP_FILE}.gpg" ]; then
        rm "${DUMP_FILE}"
        echo "Backup complete: ${DUMP_FILE}.gpg"
    else
        echo "ERROR: encrypted file is empty, preserving plaintext" >&2
        exit 1
    fi
else
    echo "WARNING: GPG key 'backup@pretel' not found. Backup saved unencrypted: ${DUMP_FILE}"
    echo "Generate key with: gpg --gen-key (use backup@pretel as email)"
fi

# Retention: 30 days local
find "${BACKUP_DIR}" -name "*.dump*" -mtime +30 -delete
