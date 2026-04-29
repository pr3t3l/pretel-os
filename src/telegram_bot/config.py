"""Runtime configuration for the Telegram bot.

Loads `~/.env.pretel_os` on import so `python -m telegram_bot` picks up
`TELEGRAM_BOT_TOKEN` + `TELEGRAM_OPERATOR_CHAT_ID` + `DATABASE_URL`
alongside the MCP server's existing env vars. systemd already sets
`EnvironmentFile`, so the dotenv call is a no-op there — intentional
parity with `src/mcp_server/config.py`.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ENV_FILE = Path.home() / ".env.pretel_os"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Config:
    telegram_bot_token: str
    telegram_operator_chat_id: int
    database_url: str
    transcripts_dir: Path


def _require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Set it in {ENV_FILE} (e.g., {name}=...)."
        )
    return value


def _require_int(name: str) -> int:
    raw = _require(name)
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(
            f"Environment variable {name} must be an integer (got {raw!r})."
        ) from exc


def load_config() -> Config:
    return Config(
        telegram_bot_token=_require("TELEGRAM_BOT_TOKEN"),
        telegram_operator_chat_id=_require_int("TELEGRAM_OPERATOR_CHAT_ID"),
        database_url=_require("DATABASE_URL"),
        transcripts_dir=Path(
            os.environ.get(
                "TELEGRAM_TRANSCRIPTS_DIR",
                str(Path.home() / "pretel-os-data" / "transcripts"),
            )
        ),
    )
