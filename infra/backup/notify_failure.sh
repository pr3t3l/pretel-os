#!/bin/bash
# infra/backup/notify_failure.sh
# Posts a Telegram alert when a systemd unit fails. Invoked via
# OnFailure= handler on the failing unit. Reads TELEGRAM_BOT_TOKEN and
# TELEGRAM_OPERATOR_CHAT_ID from ~/.env.pretel_os.
set -euo pipefail

SERVICE="${1:?service name required}"
ENV_FILE="/home/pretel/.env.pretel_os"

if [ ! -f "${ENV_FILE}" ]; then
    echo "ERROR: env file not found: ${ENV_FILE}" >&2
    exit 1
fi

set -a
# shellcheck disable=SC1090
source "${ENV_FILE}"
set +a

if [ -z "${TELEGRAM_BOT_TOKEN:-}" ] || [ -z "${TELEGRAM_OPERATOR_CHAT_ID:-}" ]; then
    echo "ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_OPERATOR_CHAT_ID not set" >&2
    exit 1
fi

HOST="$(hostname -s)"
NOW="$(date '+%Y-%m-%d %H:%M:%S %Z')"
LOG_TAIL="$(journalctl --user -u "${SERVICE}" -n 8 --no-pager 2>/dev/null | tail -8 || echo '(no log available)')"

MESSAGE="❌ <b>${SERVICE}</b> failed
🖥 <code>${HOST}</code>
🕒 <code>${NOW}</code>

<pre>${LOG_TAIL}</pre>"

curl -sS --max-time 15 \
    -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    --data-urlencode "chat_id=${TELEGRAM_OPERATOR_CHAT_ID}" \
    --data-urlencode "parse_mode=HTML" \
    --data-urlencode "text=${MESSAGE}" \
    > /dev/null
