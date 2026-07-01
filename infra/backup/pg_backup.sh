#!/bin/bash
# infra/backup/pg_backup.sh
# Source: DATA_MODEL §10.1
set -euo pipefail

BACKUP_DIR="/home/pretel/backups/pretel-os-db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DUMP_FILE="${BACKUP_DIR}/pretel_os_${TIMESTAMP}.dump"
RCLONE_REMOTE="Pretel-os-backup:pretel-os-db"

mkdir -p "${BACKUP_DIR}"

# Load DATABASE_URL from operator env (owner credentials, not system user)
if [ -f "/home/pretel/.env.pretel_os" ]; then
    set -a
    source /home/pretel/.env.pretel_os
    set +a
else
    echo "ERROR: /home/pretel/.env.pretel_os not found" >&2
    exit 1
fi

if [ -z "${DATABASE_URL:-}" ]; then
    echo "ERROR: DATABASE_URL not set in /home/pretel/.env.pretel_os" >&2
    exit 1
fi

# Dump as the DB owner (pretel_os has pg_read_all_data, covers all schemas)
pg_dump -Fc -d "${DATABASE_URL}" -f "${DUMP_FILE}"

# Verify dump integrity
if ! pg_restore --list "${DUMP_FILE}" > /dev/null 2>&1; then
    echo "ERROR: dump verification failed, aborting. File preserved: ${DUMP_FILE}" >&2
    exit 1
fi

UPLOAD_FILE="${DUMP_FILE}"

# Encrypt with GPG if the key exists. Generate once with:
#   gpg --gen-key   (use backup@pretel as email)
if gpg --list-keys backup@pretel > /dev/null 2>&1; then
    gpg --batch --yes --encrypt --recipient backup@pretel \
        --output "${DUMP_FILE}.gpg" "${DUMP_FILE}"

    if [ ! -s "${DUMP_FILE}.gpg" ]; then
        echo "ERROR: encrypted file is empty, preserving plaintext" >&2
        exit 1
    fi

    rm "${DUMP_FILE}"
    UPLOAD_FILE="${DUMP_FILE}.gpg"
    echo "Encrypted: ${UPLOAD_FILE}"
else
    echo "WARNING: GPG key 'backup@pretel' not found. Uploading unencrypted." >&2
fi

# Off-site copy to Google Drive (folder created by rclone if missing)
if command -v rclone > /dev/null 2>&1; then
    rclone copy "${UPLOAD_FILE}" "${RCLONE_REMOTE}/" --quiet
    echo "Uploaded to ${RCLONE_REMOTE}/$(basename "${UPLOAD_FILE}")"
else
    echo "WARNING: rclone not installed, skipping off-site copy" >&2
fi

# Retention: 30 days local
find "${BACKUP_DIR}" -name "*.dump*" -mtime +30 -delete

echo "Backup complete: ${UPLOAD_FILE}"
