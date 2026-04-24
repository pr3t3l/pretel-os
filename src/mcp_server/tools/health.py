"""/health route handler — unauthenticated HTTP 200 with db_healthy flag."""
from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse

from .. import db as db_mod


async def health(request: Request) -> JSONResponse:
    """Liveness + db readiness.

    Always returns HTTP 200 so systemd / Cloudflare / uptime monitors see
    the process is alive. `db_healthy` surfaces DB state separately for
    degraded-mode visibility per CONSTITUTION §8.43.
    """
    return JSONResponse({"status": "ok", "db_healthy": db_mod.is_healthy()})
