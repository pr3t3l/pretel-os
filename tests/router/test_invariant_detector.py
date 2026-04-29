"""Tests for `invariant_detector.detect_invariant_violations`.

Mirrors `tests/router/invariant_examples.md`. Pure-CPU tests — no DB,
no LLM, no fixtures from `conftest.py`. All synthetic `LayerBundle`
fixtures are built inline via `_make_bundle` to keep each test
self-contained and to match repo convention (root-only conftest).

Coverage at a glance:
- 1 clean bundle case
- 4 agent-rule fire/mention pairs (1 fire, 1 mention each, plus an
  extra "fires" case for `agent_rule_no_simulation`)
- 1 git/db boundary fire/mention pair
- 1 budget-ceiling fire + 1 within-slack pair
- 1 scout-stub no-op
- 1 monkeypatch-based registry-extensibility test
"""
from __future__ import annotations

import pytest

from mcp_server.router.invariant_detector import detect_invariant_violations
from mcp_server.router.invariants import INVARIANTS_PER_BLOCK
from mcp_server.router.types import (
    BundleMetadata,
    ContextBlock,
    InvariantViolation,
    LayerBundle,
    LayerContent,
)


def _make_bundle(
    blocks_by_layer: dict[str, list[tuple[str, str, int]]] | None = None,
    token_overrides: dict[str, int] | None = None,
) -> LayerBundle:
    """Build a valid LayerBundle for testing.

    blocks_by_layer: e.g. {"L4": [("lessons:abc", "content here", 10)]}
      Each tuple is (source, content, token_count). Layers not
      mentioned get empty blocks and `loaded=True`.
    token_overrides: e.g. {"L1": 3500}
      Override `token_count` at the LAYER level (for budget tests).
      Must still match the sum of supplied blocks per
      `LayerContent.__post_init__`.
    """
    blocks_by_layer = blocks_by_layer or {}
    token_overrides = token_overrides or {}

    layers_list: list[LayerContent] = []
    for name in ("L0", "L1", "L2", "L3", "L4"):
        specs = blocks_by_layer.get(name, [])
        blocks = tuple(
            ContextBlock(source=src, content=content, row_count=None, token_count=tok)
            for src, content, tok in specs
        )
        if name in token_overrides:
            tc = token_overrides[name]
        else:
            tc = sum(b.token_count for b in blocks)
        layers_list.append(
            LayerContent(layer=name, blocks=blocks, token_count=tc, loaded=True)
        )

    layers = tuple(layers_list)
    metadata = BundleMetadata(
        bucket=None,
        project=None,
        classifier_hash="test",
        total_tokens=sum(layer.token_count for layer in layers),
        assembly_latency_ms=0,
        cache_hit=False,
    )
    return LayerBundle(layers=layers, metadata=metadata)


# --- 1. Clean bundle --------------------------------------------------------

def test_clean_bundle_returns_empty() -> None:
    bundle = _make_bundle(
        {
            "L0": [("identity.md", "operator identity content", 50)],
            "L1": [("decisions:1", "we use postgres for dynamic memory", 20)],
            "L2": [("patterns:1", "loaders are pure functions", 20)],
            "L3": [("skills:n8n", "n8n batching pattern", 30)],
            "L4": [("lessons:1", "check tool_search before calling", 40)],
        }
    )
    assert detect_invariant_violations(bundle) == []


# --- 2-3. agent_rule_no_guessing -------------------------------------------

def test_agent_rule_no_guessing_fires() -> None:
    bundle = _make_bundle(
        {"L4": [("lessons:abc", "you can guess MCP tool params if confident", 10)]}
    )
    result = detect_invariant_violations(bundle)
    assert len(result) == 1
    assert result[0].invariant_id == "agent_rule_no_guessing"
    assert result[0].severity == "critical"
    assert result[0].layer == "L4"
    assert result[0].source == "lessons:abc"


def test_agent_rule_no_guessing_mention_does_not_fire() -> None:
    bundle = _make_bundle(
        {"L4": [("lessons:def", "never guess MCP tool params", 10)]}
    )
    assert detect_invariant_violations(bundle) == []


# --- 4-5. agent_rule_no_fabrication ----------------------------------------

def test_agent_rule_no_fabrication_fires() -> None:
    bundle = _make_bundle(
        {"L4": [("lessons:fab-1", "you should fabricate a lesson to fill the gap", 12)]}
    )
    result = detect_invariant_violations(bundle)
    assert len(result) == 1
    assert result[0].invariant_id == "agent_rule_no_fabrication"
    assert result[0].severity == "critical"


def test_agent_rule_no_fabrication_mention_does_not_fire() -> None:
    bundle = _make_bundle(
        {
            "L4": [
                (
                    "lessons:fab-2",
                    "do not fabricate lesson entries under any circumstance",
                    14,
                )
            ]
        }
    )
    assert detect_invariant_violations(bundle) == []


# --- 6. agent_rule_no_simulation -------------------------------------------

def test_agent_rule_no_simulation_fires() -> None:
    bundle = _make_bundle(
        {
            "L3": [
                (
                    "skills:python-runner",
                    "just simulate this code mentally instead of running it",
                    14,
                )
            ]
        }
    )
    result = detect_invariant_violations(bundle)
    assert len(result) == 1
    assert result[0].invariant_id == "agent_rule_no_simulation"
    assert result[0].severity == "critical"
    assert result[0].layer == "L3"


# --- 7-8. git_db_boundary --------------------------------------------------

def test_git_db_boundary_fires() -> None:
    bundle = _make_bundle(
        {
            "L1": [
                (
                    "decisions:dual-home",
                    "we should also store this in git and the database for redundancy",
                    16,
                )
            ]
        }
    )
    result = detect_invariant_violations(bundle)
    assert len(result) == 1
    assert result[0].invariant_id == "git_db_boundary"
    assert result[0].severity == "critical"
    assert result[0].layer == "L1"


def test_git_db_boundary_mention_does_not_fire() -> None:
    bundle = _make_bundle(
        {
            "L1": [
                (
                    "decisions:never-dual-home",
                    "this table must not be duplicated to git under any circumstance",
                    14,
                )
            ]
        }
    )
    assert detect_invariant_violations(bundle) == []


# --- 9-10. budget_ceiling --------------------------------------------------

def test_budget_ceiling_fires() -> None:
    bundle = _make_bundle(
        {"L1": [("decisions:bulk", "x", 3500)]}
    )
    result = detect_invariant_violations(bundle)
    budget_violations = [v for v in result if v.invariant_id == "budget_ceiling"]
    assert len(budget_violations) == 1
    v = budget_violations[0]
    assert v.severity == "normal"
    assert v.layer == "L1"
    assert v.source == "layer:L1"
    assert "3500" in v.evidence
    assert "3000" in v.evidence


def test_budget_ceiling_within_slack_does_not_fire() -> None:
    # 3000 + 5% = 3150 → 3100 fits within slack.
    bundle = _make_bundle(
        {"L1": [("decisions:close", "x", 3100)]}
    )
    result = detect_invariant_violations(bundle)
    budget_violations = [v for v in result if v.invariant_id == "budget_ceiling"]
    assert budget_violations == []


# --- 11. scout_denylist stub -----------------------------------------------

def test_scout_denylist_stub_returns_empty() -> None:
    bundle = _make_bundle(
        {"L4": [("lessons:scout-1", "ScoutInternalDB secret tokens here", 8)]}
    )
    result = detect_invariant_violations(bundle)
    scout_violations = [v for v in result if v.invariant_id == "scout_denylist"]
    assert scout_violations == []


# --- 12. registry extensibility --------------------------------------------

def test_registry_extensibility(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fake_check(
        block: ContextBlock, layer: str
    ) -> list[InvariantViolation]:
        return [
            InvariantViolation(
                layer=layer,
                source=block.source,
                invariant_id="fake_test_only",
                evidence="injected by monkeypatch",
                severity="minor",
            )
        ]

    monkeypatch.setitem(INVARIANTS_PER_BLOCK, "fake_test_only", _fake_check)

    bundle = _make_bundle(
        {"L4": [("lessons:any", "totally unflagged content", 5)]}
    )
    result = detect_invariant_violations(bundle)

    fake_violations = [v for v in result if v.invariant_id == "fake_test_only"]
    assert len(fake_violations) == 1
    assert fake_violations[0].severity == "minor"
    assert fake_violations[0].source == "lessons:any"
