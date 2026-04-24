"""Runtime configuration read from the environment.

Loads ~/.env.pretel_os on import so a plain `python -m mcp_server.main` picks up
credentials. systemd already sets EnvironmentFile, so the dotenv call is a
no-op in that path — intentional: works under both runtime modes.
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
    database_url: str
    mcp_shared_secret: str
    mcp_server_host: str
    mcp_server_port: int
    openai_api_key: str
    openai_embedding_model: str
    timeout_openai_embedding_ms: int
    fallback_journal_dir: Path
    identity_path: Path


def _require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def load_config() -> Config:
    return Config(
        database_url=_require("DATABASE_URL"),
        mcp_shared_secret=_require("MCP_SHARED_SECRET"),
        mcp_server_host=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        mcp_server_port=int(os.environ.get("MCP_SERVER_PORT", "8787")),
        openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
        openai_embedding_model=os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large"),
        timeout_openai_embedding_ms=int(os.environ.get("TIMEOUT_OPENAI_EMBEDDING_MS", "5000")),
        fallback_journal_dir=Path(
            os.environ.get("FALLBACK_JOURNAL_DIR", str(Path.home() / "pretel-os-data" / "fallback-journal"))
        ),
        identity_path=REPO_ROOT / "identity.md",
    )
