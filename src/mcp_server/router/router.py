"""Router orchestrator (Phase D.2.2 per `specs/router/phase_d_close.md`).

DISCOVERY (D.2.1, 2026-04-29) — interfaces wired by this module:

- `litellm_client.chat_json(model_alias, system, user, timeout_ms,
  max_tokens) -> tuple[dict, ChatJsonTelemetry]`. Telemetry already
  exposes `prompt_tokens` / `completion_tokens` / `cache_read_tokens` /
  `model`. **No modification needed.**
- `classifier.classify(message, l0_content=None, session_excerpt=None,
  request_id=None) -> tuple[dict, ChatJsonTelemetry]`. **Q6 already
  satisfied via option (b)** — `classify` returns the tuple as
  shipped in A.4.3. The orchestrator destructures and converts the
  telemetry record to the `llm_call_data` dict that `log_classification`
  expects.
- `assemble.assemble_bundle(conn, bucket, project, classifier_signals,
  repo_root, query_text, current_time, cache) -> LayerBundle` (async).
- `invariant_detector.detect_invariant_violations(bundle) ->
  list[InvariantViolation]` (sync, pure).
- `cache.LayerBundleCache(max_entries=...)` — instantiated by the MCP
  lifespan hook with `start_listener(conninfo)`. This module does NOT
  manage the cache lifetime.
- `tools/context.py` is the existing Module-3 stub. D.3 replaces it
  to call `get_context()` here; out of scope for D.2.
- `conversation_sessions` schema (Q8): stores session metadata only
  (`started_at`, `last_seen_at`, `turn_count`, etc.), NOT per-turn
  message content as of 2026-04-29. `_get_session_excerpt` returns ''
  for now; per-turn content lands when Module 5 (Telegram bot) writes
  actual conversation turns.

DESIGN (per phase_d_close.md Q4, Q5, Q6, Q7, Q8):

- Async function with sync `psycopg.Connection` per Q4. The connection
  lifecycle belongs to the caller (the MCP tool wrapper in D.3).
- `try/finally` with `degraded_mode` + `reasons` accumulator per Q5;
  this function NEVER raises to the MCP tool. It returns a
  possibly-degraded `ContextBundle` dict instead.
- Tool recommendations via direct SQL against `tools_catalog` per Q7
  (Router never invokes other MCP tools).
"""
from __future__ import annotations

import logging
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psycopg

from .assemble import assemble_bundle
from .cache import LayerBundleCache
from .classifier import classify
from .exceptions import ClassifierError
from .fallback_classifier import fallback_classify
from .invariant_detector import detect_invariant_violations
from .litellm_client import ChatJsonTelemetry
from .telemetry import (
    log_classification,
    log_completion,
    log_conflicts,
    log_layers,
    log_rag,
    start_request,
)
from .types import (
    BundleMetadata,
    ClassifierSignals,
    ContextBlock,
    InvariantViolation,
    LayerBundle,
    LayerContent,
)

log = logging.getLogger(__name__)


def _read_identity(repo_root: Path) -> str:
    """Read identity.md content for classifier input. Returns '' on failure."""
    try:
        return (repo_root / "identity.md").read_text(encoding="utf-8")
    except OSError as exc:
        log.warning("identity.md unreadable: %s", exc)
        return ""


def _get_session_excerpt(
    conn: psycopg.Connection, session_id: str | None
) -> str:
    """Return last 3 turns of the session, or '' if unavailable.

    Per phase_d_close.md Q8: `conversation_sessions` stores session
    metadata (started_at, last_seen_at, turn_count) but does NOT
    store per-turn message content as of 2026-04-29. Returning '' is
    the correct degraded behavior. Tracked as deferred follow-up for
    Module 5 (Telegram bot writes per-turn content).
    """
    return ""


def _provider_from_model(model: str) -> str:
    """Best-effort provider inference from a LiteLLM-resolved model name."""
    m = model.lower()
    if "claude" in m or "anthropic" in m:
        return "anthropic"
    if "gemini" in m or "google" in m:
        return "google"
    if "gpt" in m or "openai" in m:
        return "openai"
    if "kimi" in m or "moonshot" in m:
        return "moonshot"
    return "unknown"


def _telemetry_to_llm_call_data(
    telemetry: ChatJsonTelemetry,
    classification: dict[str, Any],
    latency_ms: int,
) -> dict[str, Any]:
    """Convert `ChatJsonTelemetry` into the dict `log_classification` expects.

    `cost_usd` is set to 0 because `ChatJsonTelemetry` does not carry
    it today — LiteLLM proxy may compute it server-side; surfacing it
    is a Phase F follow-up.
    """
    bucket = classification.get("bucket")
    project_slug = classification.get("project")
    project_str: str | None
    if bucket and project_slug:
        project_str = f"{bucket}/{project_slug}"
    elif bucket:
        project_str = bucket
    else:
        project_str = None
    return {
        "provider": _provider_from_model(telemetry.model),
        "model": telemetry.model,
        "input_tokens": telemetry.prompt_tokens or 0,
        "output_tokens": telemetry.completion_tokens or 0,
        "cache_read_tokens": telemetry.cache_read_tokens,
        "cost_usd": 0,
        "latency_ms": latency_ms,
        "success": True,
        "error": None,
        "project": project_str,
    }


def _recommend_tools(
    conn: psycopg.Connection,
    complexity: str,
    needs_lessons: bool,
) -> list[dict[str, Any]]:
    """Top 5 tools by `utility_score` per spec §7.2 + Q7.

    Direct SQL — the Router does NOT call other MCP tools (spec §11).
    Returns `[]` for LOW complexity and for MEDIUM without
    `needs_lessons`.
    """
    if complexity == "LOW":
        return []
    if complexity == "MEDIUM" and not needs_lessons:
        return []
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT name, description_short, utility_score
                FROM tools_catalog
                WHERE kind = 'tool'
                ORDER BY utility_score DESC NULLS LAST
                LIMIT 5
                """
            )
            return [
                {
                    "name": row[0],
                    "description": row[1],
                    "utility_score": (
                        float(row[2]) if row[2] is not None else None
                    ),
                }
                for row in cur.fetchall()
            ]
    except psycopg.Error as exc:
        log.warning("recommend_tools failed: %s", exc)
        return []


def _compute_rag_expected(classification: dict[str, Any]) -> bool:
    """Per spec §5.2: HIGH always; MEDIUM only when needs_lessons."""
    complexity = classification.get("complexity")
    if complexity == "HIGH":
        return True
    if complexity == "MEDIUM" and classification.get("needs_lessons"):
        return True
    return False


def _empty_bundle() -> LayerBundle:
    """Sentinel bundle used as the initial value before assembly runs."""
    layers = tuple(
        LayerContent(layer=name, blocks=(), token_count=0, loaded=False)
        for name in ("L0", "L1", "L2", "L3", "L4")
    )
    metadata = BundleMetadata(
        bucket=None,
        project=None,
        classifier_hash="empty",
        total_tokens=0,
        assembly_latency_ms=0,
        cache_hit=False,
        over_budget_layers=(),
    )
    return LayerBundle(layers=layers, metadata=metadata)


def _build_degraded_bundle(repo_root: Path) -> LayerBundle:
    """L0-only bundle when `assemble_bundle` raises (spec §10 row 3).

    `token_count=0` placeholder — accurate counts require a tiktoken
    pass that's unwarranted in the degraded path. Telemetry will show
    `over_budget_layers=[]` and `tokens_assembled_total=0`, which is
    correct: nothing measurable was assembled.
    """
    blocks: tuple[ContextBlock, ...] = ()
    try:
        identity = (repo_root / "identity.md").read_text(encoding="utf-8")
        blocks = (
            ContextBlock(
                source="identity.md",
                content=identity,
                row_count=None,
                token_count=0,
            ),
        )
    except OSError:
        pass
    layers = (
        LayerContent(layer="L0", blocks=blocks, token_count=0, loaded=bool(blocks)),
        LayerContent(layer="L1", blocks=(), token_count=0, loaded=False),
        LayerContent(layer="L2", blocks=(), token_count=0, loaded=False),
        LayerContent(layer="L3", blocks=(), token_count=0, loaded=False),
        LayerContent(layer="L4", blocks=(), token_count=0, loaded=False),
    )
    metadata = BundleMetadata(
        bucket=None,
        project=None,
        classifier_hash="degraded",
        total_tokens=0,
        assembly_latency_ms=0,
        cache_hit=False,
        over_budget_layers=(),
    )
    return LayerBundle(layers=layers, metadata=metadata)


async def get_context(
    conn: psycopg.Connection,
    message: str,
    session_id: str | None,
    client_origin: str,
    repo_root: Path,
    cache: LayerBundleCache,
) -> dict[str, Any]:
    """Public Router entry point — assembles and logs a ContextBundle.

    Wraps the entire pipeline in `try/finally` so `log_completion`
    always fires even on internal failure. Per Q5, this function
    NEVER raises to the MCP tool layer; it returns a possibly-degraded
    `ContextBundle` dict matching `spec.md §4.2`.
    """
    t0 = time.monotonic()
    request_id = start_request(conn, message, session_id, client_origin)

    degraded = False
    reasons: list[str] = []
    classification: dict[str, Any] = {}
    classification_mode = "fallback_rules"
    llm_call_data: dict[str, Any] | None = None
    bundle: LayerBundle = _empty_bundle()
    violations: list[InvariantViolation] = []
    tools_recommended: list[dict[str, Any]] = []

    try:
        identity_content = _read_identity(repo_root)
        session_excerpt = _get_session_excerpt(conn, session_id)

        classify_t0 = time.monotonic()
        try:
            classification, telemetry = classify(
                message=message,
                l0_content=identity_content,
                session_excerpt=session_excerpt,
                request_id=request_id,
            )
            classification_mode = "llm"
            classify_latency_ms = int(
                (time.monotonic() - classify_t0) * 1000
            )
            llm_call_data = _telemetry_to_llm_call_data(
                telemetry, classification, classify_latency_ms
            )
        except ClassifierError as exc:
            classification = fallback_classify(message, identity_content)
            classification_mode = "fallback_rules"
            llm_call_data = None
            degraded = True
            reasons.append(f"classifier_fallback: {type(exc).__name__}")

        log_classification(
            conn, request_id, classification,
            classification_mode, llm_call_data,
        )

        signals = ClassifierSignals(
            bucket=classification.get("bucket"),
            project=classification.get("project"),
            complexity=classification.get("complexity", "LOW"),
            needs_lessons=bool(classification.get("needs_lessons", False)),
            needs_skills=False,
            skill_ids=None,
            classifier_domain=None,
        )

        try:
            bundle = await assemble_bundle(
                conn=conn,
                bucket=signals.bucket,
                project=signals.project,
                classifier_signals=signals,
                repo_root=repo_root,
                query_text=message,
                current_time=datetime.now(tz=timezone.utc),
                cache=cache,
            )
        except Exception as exc:
            log.warning("assemble_bundle failed: %s", exc)
            bundle = _build_degraded_bundle(repo_root)
            degraded = True
            reasons.append(f"bundle_assembly_failed: {type(exc).__name__}")

        log_layers(conn, request_id, bundle)

        try:
            violations = detect_invariant_violations(bundle)
        except Exception as exc:
            log.warning("detect_invariant_violations failed: %s", exc)
            violations = []
            degraded = True
            reasons.append(
                f"invariant_detection_failed: {type(exc).__name__}"
            )

        log_conflicts(conn, request_id, violations)

        tools_recommended = _recommend_tools(
            conn, signals.complexity, signals.needs_lessons
        )

        rag_expected = _compute_rag_expected(classification)
        l4_layer = next(
            (layer for layer in bundle.layers if layer.layer == "L4"), None
        )
        rag_executed = bool(l4_layer and l4_layer.loaded)
        lessons_returned = 0
        if l4_layer:
            lessons_returned = sum(
                1 for block in l4_layer.blocks if "lessons" in block.source
            )

        log_rag(
            conn, request_id, rag_expected, rag_executed,
            lessons_returned, len(tools_recommended),
        )

    finally:
        latency_ms = int((time.monotonic() - t0) * 1000)
        log_completion(
            conn, request_id, degraded,
            "; ".join(reasons) if reasons else None,
            latency_ms,
        )

    return {
        "request_id": request_id,
        "session_id": session_id,
        "classification": classification,
        "classification_mode": classification_mode,
        "bundle": asdict(bundle),
        "tools_recommended": tools_recommended,
        "source_conflicts": [asdict(v) for v in violations],
        "over_budget_layers": list(bundle.metadata.over_budget_layers),
        "degraded_mode": degraded,
        "degraded_reason": "; ".join(reasons) if reasons else None,
        "latency_ms": latency_ms,
    }
