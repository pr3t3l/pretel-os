"""Append-only fallback journal for mutations issued while DB is unhealthy.

Per CONSTITUTION §8.43 (b): each mutation is written as one JSONL line under
~/pretel-os-data/fallback-journal/YYYYMMDD.jsonl with mode 0600. The file's
idempotency_key lets a later replay worker skip already-applied writes.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import config as config_mod

log = logging.getLogger(__name__)

_lock = threading.Lock()


def _journal_path(ts: datetime) -> Path:
    cfg = config_mod.load_config()
    day = ts.strftime("%Y%m%d")
    return cfg.fallback_journal_dir / f"{day}.jsonl"


def _idempotency_key(operation: str, payload: dict[str, Any], ts: datetime) -> str:
    minute = ts.strftime("%Y%m%dT%H%M")
    material = operation + json.dumps(payload, sort_keys=True, default=str) + minute
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def record(operation: str, payload: dict[str, Any]) -> str:
    """Append one mutation to today's journal. Returns the journal_id."""
    ts = datetime.now(timezone.utc)
    entry = {
        "journal_id": str(uuid.uuid4()),
        "ts": ts.isoformat(),
        "operation": operation,
        "payload": payload,
        "idempotency_key": _idempotency_key(operation, payload, ts),
    }
    path = _journal_path(ts)
    with _lock:
        path.parent.mkdir(parents=True, exist_ok=True)
        existed = path.exists()
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
        if not existed:
            try:
                os.chmod(path, 0o600)
            except OSError as exc:
                log.warning("could not chmod %s: %s", path, exc)
    return entry["journal_id"]
