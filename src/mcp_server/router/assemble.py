"""Bundle orchestrator: assemble_bundle (B.9).

Async function that owns the per-turn flow:
    1. Compute classifier_hash, look up cache.
    2. On miss, embed query if needs_lessons.
    3. Call all 5 sync loaders.
    4. Detect over-budget layers per contract §7; summarize via
       classifier_default in a thread; write a gotcha row per fire.
    5. Build BundleMetadata + LayerBundle, store in cache, return.

Connection lifecycle is the caller's responsibility (Phase D's
router.py owns one or more sync psycopg.Connection per turn).

Per Q4 decision (specs/router/phase_b_close.md §1): async function
with sync connection parameter. embed() and summarize_oversize are
bridged via asyncio.to_thread to keep the event loop unblocked.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import psycopg

from mcp_server.embeddings import embed
from mcp_server.router._classifier_hash import classifier_hash
from mcp_server.router._tokens import count_tokens
from mcp_server.router.cache import LayerBundleCache
from mcp_server.router.exceptions import ClassifierError
from mcp_server.router.load_l0 import load_l0
from mcp_server.router.load_l1 import load_l1
from mcp_server.router.load_l2 import load_l2
from mcp_server.router.load_l3 import load_l3
from mcp_server.router.load_l4 import load_l4
from mcp_server.router.summarize import summarize_oversize
from mcp_server.router.types import (
    BundleMetadata,
    ClassifierSignals,
    ContextBlock,
    LayerBundle,
    LayerContent,
)


log = logging.getLogger(__name__)


# Soft budgets per contract §7. L0 has only a hard per-file cap on
# identity.md (write-time, pre-commit). L3 is classifier-determined.
# Phase B applies summarization at read-time only to L1/L2/L4.
_LAYER_SOFT_BUDGETS: dict[str, int] = {
    "L1": 3000,
    "L2": 5000,
    "L4": 4000,
}


def _empty_layer(layer: str) -> LayerContent:
    return LayerContent(layer=layer, blocks=(), token_count=0, loaded=False)


def _with_cache_hit(bundle: LayerBundle) -> LayerBundle:
    """Return a copy of `bundle` with metadata.cache_hit=True.

    The dataclasses are frozen, so we rebuild from the existing fields.
    """
    md = bundle.metadata
    return LayerBundle(
        layers=bundle.layers,
        metadata=BundleMetadata(
            bucket=md.bucket,
            project=md.project,
            classifier_hash=md.classifier_hash,
            total_tokens=md.total_tokens,
            assembly_latency_ms=md.assembly_latency_ms,
            cache_hit=True,
            over_budget_layers=md.over_budget_layers,
        ),
    )


def _write_oversize_gotcha(
    conn: psycopg.Connection,
    layer: str,
    actual_tokens: int,
    budget_tokens: int,
    bucket: str | None,
) -> None:
    """Write a gotcha row when summarize_oversize fires (per spec §6.4)."""
    title = f"Over-budget layer at read-time: {layer}"
    trigger_context = (
        f"Layer {layer} loaded at {actual_tokens} cl100k_base tokens, "
        f"exceeding the {budget_tokens}-token soft budget per contract §7. "
        f"Bucket: {bucket!r}."
    )
    what_goes_wrong = (
        "summarize_oversize compressed the layer to ~80% of budget, but the "
        "underlying source content is too large. Future turns will keep "
        "paying the summarization cost. Refactor the source to fit budget "
        "(split decisions/best_practices into bucket- or project-scoped "
        "rows; trim verbose patterns; archive stale lessons)."
    )
    applicable_buckets = [bucket] if bucket else []
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO gotchas "
                "(title, trigger_context, what_goes_wrong, applicable_buckets, tags) "
                "VALUES (%s, %s, %s, %s, %s)",
                (title, trigger_context, what_goes_wrong,
                 applicable_buckets, ["over-budget", layer.lower()]),
            )
    except psycopg.Error as exc:
        log.warning("gotcha write failed for %s: %s", layer, exc)


async def _maybe_summarize(
    layer: LayerContent,
    bucket: str | None,
    conn: psycopg.Connection,
) -> tuple[LayerContent, bool]:
    """Return (possibly-summarized layer, was_summarized).

    No-op when the layer has no soft budget (L0, L3), is unloaded,
    or is within budget. Failure of the LLM call leaves the layer
    unsummarized but still flagged as over-budget — caller decides
    how to surface that.
    """
    budget = _LAYER_SOFT_BUDGETS.get(layer.layer)
    if budget is None or not layer.loaded:
        return layer, False
    if layer.token_count <= budget:
        return layer, False

    full_content = "\n\n".join(b.content for b in layer.blocks)
    target = int(budget * 0.8)
    try:
        summary = await asyncio.to_thread(summarize_oversize, full_content, target)
    except ClassifierError as exc:
        log.warning(
            "summarize_oversize failed for %s (%d tokens, budget %d): %s",
            layer.layer, layer.token_count, budget, exc,
        )
        return layer, True   # flag as over-budget even though we couldn't compress

    new_block = ContextBlock(
        source=f"{layer.layer.lower()}_summarized",
        content=summary,
        row_count=None,
        token_count=count_tokens(summary),
    )
    summarized = LayerContent(
        layer=layer.layer,
        blocks=(new_block,),
        token_count=new_block.token_count,
        loaded=True,
    )
    _write_oversize_gotcha(
        conn=conn, layer=layer.layer, actual_tokens=layer.token_count,
        budget_tokens=budget, bucket=bucket,
    )
    return summarized, True


async def assemble_bundle(
    conn: psycopg.Connection,
    bucket: str | None,
    project: str | None,
    classifier_signals: ClassifierSignals,
    repo_root: Path,
    query_text: str,
    current_time: datetime,
    cache: LayerBundleCache,
) -> LayerBundle:
    """Build a complete LayerBundle for one turn.

    Args:
        conn: caller-managed sync psycopg connection. Phase D's router.py
            opens it; this function does not close it.
        bucket: workspace bucket; passes through to L1, L2, L4.
        project: project slug within bucket; passes through to L2.
        classifier_signals: Phase A classifier output, fields per
            ClassifierSignals docstring.
        repo_root: filesystem root for L0 file-backed blocks.
        query_text: raw turn text used to derive the L4 query embedding.
        current_time: turn-start timestamp; assembly_latency_ms is
            derived as (now - current_time).
        cache: caller-managed cache instance; the same instance must be
            used across turns so cache hits work.

    Returns:
        A LayerBundle with exactly 5 LayerContent entries in order
        L0..L4 (some may have loaded=False) and a populated
        BundleMetadata. cache_hit indicates whether this bundle was
        served from the cache.
    """
    h = classifier_hash(
        bucket=classifier_signals.bucket,
        project=classifier_signals.project,
        complexity=classifier_signals.complexity,
        needs_lessons=classifier_signals.needs_lessons,
        needs_skills=classifier_signals.needs_skills,
        skill_ids=classifier_signals.skill_ids,
        classifier_domain=classifier_signals.classifier_domain,
    )

    cache_key = (bucket, project, h)
    cached = cache.get(cache_key)
    if cached is not None:
        return _with_cache_hit(cached)

    # L4 needs an embedding; embed only when classifier asked for lessons.
    query_embedding: list[float] | None = None
    if classifier_signals.needs_lessons:
        query_embedding = await embed(query_text)
        # If embed returned None (OpenAI down, key missing), load_l4 will
        # short-circuit to loaded=False on its own. No special handling here.

    # Sync loaders — fast against the local DB; not worth the to_thread overhead.
    l0 = load_l0(conn, repo_root)
    l1 = load_l1(conn, bucket) if bucket is not None else _empty_layer("L1")
    l2 = (
        load_l2(conn, bucket, project)
        if (bucket is not None and project is not None)
        else _empty_layer("L2")
    )
    l3_skill_ids: list[str] | None = (
        list(classifier_signals.skill_ids)
        if (classifier_signals.needs_skills and classifier_signals.skill_ids)
        else None
    )
    l3 = load_l3(conn, l3_skill_ids)
    l4 = load_l4(
        conn,
        bucket=bucket,
        query_embedding=query_embedding,
        needs_lessons=classifier_signals.needs_lessons,
        classifier_domain=classifier_signals.classifier_domain,
    )

    # Over-budget pass — only L1/L2/L4 have soft budgets.
    layers_list: list[LayerContent] = [l0, l1, l2, l3, l4]
    over_budget: list[str] = []
    for idx, layer in enumerate(layers_list):
        new_layer, was_over = await _maybe_summarize(layer, bucket, conn)
        layers_list[idx] = new_layer
        if was_over:
            over_budget.append(layer.layer)

    end_time = datetime.now(tz=current_time.tzinfo)
    latency_ms = int((end_time - current_time).total_seconds() * 1000)
    total_tokens = sum(layer.token_count for layer in layers_list)

    metadata = BundleMetadata(
        bucket=bucket,
        project=project,
        classifier_hash=h,
        total_tokens=total_tokens,
        assembly_latency_ms=max(latency_ms, 0),
        cache_hit=False,
        over_budget_layers=tuple(over_budget),
    )
    bundle = LayerBundle(layers=tuple(layers_list), metadata=metadata)
    cache.put(cache_key, bundle)
    return bundle
