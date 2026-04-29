"""Unit tests for `fallback_classifier` per phase_d_close.md D.0.3.

Pure-Python tests — no DB, no LLM, no `slow` markers. Covers the seven
cases in plan §7.4: clear bucket, unknown bucket, project found in
L0, project not in L0, HIGH-keyword cap, LOW-keyword detect, default
LOW path. All fixtures inline.
"""
from __future__ import annotations

from mcp_server.router.fallback_classifier import fallback_classify


_L0_WITH_DECLASSIFIED = "## Projects\n- declassified\n- pretel-os\n"


def test_clear_bucket_match() -> None:
    result = fallback_classify("debug my n8n batching", "")
    assert result["bucket"] == "business"
    assert result["complexity"] != "HIGH"
    assert result["confidence"] == 0.4


def test_unknown_bucket() -> None:
    result = fallback_classify("what's the weather", "")
    assert result["bucket"] is None
    assert result["confidence"] == 0.4


def test_project_found_in_l0() -> None:
    result = fallback_classify(
        "summarize the declassified case status",
        _L0_WITH_DECLASSIFIED,
    )
    assert result["project"] == "declassified"


def test_project_not_in_l0() -> None:
    result = fallback_classify(
        "what is random-unknown-slug",
        _L0_WITH_DECLASSIFIED,
    )
    assert result["project"] is None


def test_high_keyword_caps_at_medium() -> None:
    result = fallback_classify("help me architect", "")
    assert result["complexity"] == "MEDIUM"
    assert result["complexity"] != "HIGH"


def test_low_keyword_detection() -> None:
    result = fallback_classify("hi", "")
    assert result["complexity"] == "LOW"


def test_default_low() -> None:
    result = fallback_classify("today the temperature is 75 degrees", "")
    assert result["complexity"] == "LOW"
