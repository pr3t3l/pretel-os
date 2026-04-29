"""Frozen dataclasses for the Layer Loader output bundle.

This module is the canonical implementation of the data shapes defined in
specs/module-0x-knowledge-architecture/layer_loader_contract.md §10.

Any change here is a contract change and requires a new ADR per contract §9.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContextBlock:
    """A single rendered chunk of context within a layer.

    Per contract §10. `row_count` is None for file-backed sources,
    int for table-backed sources.
    """
    source: str
    content: str
    row_count: int | None
    token_count: int


@dataclass(frozen=True)
class LayerContent:
    """One layer (L0..L4) with its ordered blocks.

    Per contract §10. `loaded=False` means the layer was skipped
    (classifier signal off, DB unhealthy, etc.); `blocks` may still
    be empty in that case.
    """
    layer: str
    blocks: tuple[ContextBlock, ...]
    token_count: int
    loaded: bool

    def __post_init__(self) -> None:
        if self.layer not in {"L0", "L1", "L2", "L3", "L4"}:
            raise ValueError(f"invalid layer: {self.layer!r}")
        expected = sum(b.token_count for b in self.blocks)
        if self.token_count != expected:
            raise ValueError(
                f"{self.layer} token_count={self.token_count} does not match "
                f"sum of blocks ({expected})"
            )


@dataclass(frozen=True)
class BundleMetadata:
    """Per-bundle metadata used for cache keys and telemetry.

    Per contract §10. `classifier_hash` is the Phase A output hash
    used for cache keys per contract §6. `over_budget_layers` (added
    in B.9 per plan §4.4 done-when) lists layers whose content was
    summarized at read-time because it exceeded the contract §7
    soft budget; default empty tuple for backward compatibility with
    bundles that never trigger summarization.
    """
    bucket: str | None
    project: str | None
    classifier_hash: str
    total_tokens: int
    assembly_latency_ms: int
    cache_hit: bool
    over_budget_layers: tuple[str, ...] = ()


@dataclass(frozen=True)
class ClassifierSignals:
    """The classifier's per-turn output as consumed by assemble_bundle.

    Per plan/router/plan.md §4.5: this shape feeds the cache-key derivation.
    Fields chosen for stability: any change here is a cache-busting change
    and a contract change visible to Phase D telemetry.

    `skill_ids` is a tuple (not a list) so the dataclass is hashable —
    the cache key can derive a stable hash without re-tupling.
    `classifier_domain` is forward-looking (contract §3.5 introduced
    it for L4 cross-cutting BP filtering); the current Phase A
    classifier output does not produce it. Defaults to None.
    """
    bucket: str | None
    project: str | None
    complexity: str
    needs_lessons: bool
    needs_skills: bool
    skill_ids: tuple[str, ...] | None
    classifier_domain: str | None = None


_REQUIRED_LAYER_ORDER = ("L0", "L1", "L2", "L3", "L4")


@dataclass(frozen=True)
class LayerBundle:
    """The complete output of the Layer Loader.

    Per contract §10. `layers` MUST always contain exactly 5 entries
    in order L0..L4; skipped layers are represented with loaded=False,
    not omitted. The consumer renders by iterating layers and blocks
    in order; Phase B does NOT pre-render.
    """
    layers: tuple[LayerContent, ...]
    metadata: BundleMetadata

    def __post_init__(self) -> None:
        if len(self.layers) != 5:
            raise ValueError(
                f"LayerBundle must have exactly 5 layers, got {len(self.layers)}"
            )
        actual_order = tuple(layer.layer for layer in self.layers)
        if actual_order != _REQUIRED_LAYER_ORDER:
            raise ValueError(
                f"LayerBundle layers must be in order L0..L4, got {actual_order}"
            )
        expected = sum(layer.token_count for layer in self.layers)
        if self.metadata.total_tokens != expected:
            raise ValueError(
                f"metadata.total_tokens={self.metadata.total_tokens} does not "
                f"match sum of layer.token_count ({expected})"
            )
