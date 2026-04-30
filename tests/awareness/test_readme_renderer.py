"""Tests for `awareness.readme_renderer` — Module 7.5 Phase E E.1.

Pure tests: parse_readme, render_*, round-trip, idempotency. No DB
required — `regenerate_*` is exercised via test_awareness.py (E.3).
The renderer itself is sync and side-effect-free except for the atomic
write inside `regenerate_*`, which is covered indirectly here through
`render_*` + `parse_readme` round-trip plus a tmp_path round-trip on
the marker layer.

Idempotency note: the renderer embeds `**Last regenerated:** <ISO>` in
the summary auto section. The orchestrator (`regenerate_*`) keeps the
old timestamp when the rest of the content matches, which is what
delivers the byte-identical idempotency contract. The pure render
functions take a `timestamp` parameter, so the tests pin a frozen
timestamp and assert byte-equality directly.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from awareness.readme_renderer import (
    parse_readme,
    render_bucket_readme,
    render_project_readme,
)


_FROZEN = datetime(2026, 4, 30, 14, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------
# parse_readme.
# ---------------------------------------------------------------------

def test_parse_readme_brand_new_file_has_no_markers(tmp_path: Path) -> None:
    """A non-existent path returns empty auto_sections and notes_block."""
    p = tmp_path / "fresh.md"
    parsed = parse_readme(p)
    assert parsed["raw"] == ""
    assert parsed["auto_sections"] == {}
    assert parsed["notes_block"] == ""


def test_parse_readme_with_only_notes_block_no_auto_sections(
    tmp_path: Path,
) -> None:
    """Legacy READMEs wrapped via the D.0 step have notes but no auto.

    Mirrors what the operator's pre-marker bucket README looks like
    after the one-time D.0 wrap. The renderer must read the notes
    block intact and yield empty auto_sections.
    """
    legacy = (
        "<!-- pretel:notes:start -->\n"
        "# Bucket: legacy\n\n"
        "Operator wrote this by hand months ago.\n"
        "<!-- pretel:notes:end -->\n"
    )
    p = tmp_path / "legacy.md"
    p.write_text(legacy, encoding="utf-8")

    parsed = parse_readme(p)
    assert parsed["raw"] == legacy
    assert parsed["auto_sections"] == {}
    assert "Operator wrote this by hand" in parsed["notes_block"]


def test_parse_readme_with_both_auto_and_notes(tmp_path: Path) -> None:
    """A regenerated README round-trips both sections."""
    body = (
        "# Bucket: business\n\n"
        "<!-- pretel:auto:start summary -->\n"
        "**Active projects:** 1\n"
        "<!-- pretel:auto:end summary -->\n\n"
        "<!-- pretel:notes:start -->\n"
        "## Operator notes\nKeep me\n"
        "<!-- pretel:notes:end -->\n"
    )
    p = tmp_path / "both.md"
    p.write_text(body, encoding="utf-8")

    parsed = parse_readme(p)
    assert "summary" in parsed["auto_sections"]
    assert "Active projects" in parsed["auto_sections"]["summary"]
    assert "Keep me" in parsed["notes_block"]


# ---------------------------------------------------------------------
# render_*.
# ---------------------------------------------------------------------

def test_render_bucket_readme_produces_expected_structure() -> None:
    """Rendered README carries the five auto sections + notes block."""
    out = render_bucket_readme(
        bucket="business",
        active_projects=[
            {
                "slug": "demo",
                "name": "Demo",
                "status": "active",
                "objective": "X",
            }
        ],
        archived_projects=[],
        skills=[
            {"name": "vett", "description_short": "Vendor eval"},
        ],
        recent_decisions=[
            {"adr_number": 1, "title": "T", "created_at": "2026-04-30"},
        ],
        count_open_tasks=3,
        notes_block="\n## Operator notes\nKEEP\n",
        timestamp=_FROZEN,
    )

    assert out.startswith("# Bucket: business")
    for section in (
        "summary",
        "active_projects",
        "archived_projects",
        "applicable_skills",
        "recent_decisions",
    ):
        assert f"<!-- pretel:auto:start {section} -->" in out
        assert f"<!-- pretel:auto:end {section} -->" in out
    assert "<!-- pretel:notes:start -->" in out
    assert "KEEP" in out
    assert "**Active projects:** 1" in out
    assert "ADR-1 — T (2026-04-30)" in out


def test_render_project_readme_default_notes_when_empty() -> None:
    """An empty notes_block falls back to the default Operator notes
    placeholder so the markers are always present in the file."""
    out = render_project_readme(
        project={
            "bucket": "scout",
            "slug": "demo",
            "name": "Demo",
            "status": "active",
            "objective": "Goal",
            "stack": ["py"],
            "applicable_skills": ["vett"],
            "created_at": "2026-04-30",
        },
        open_tasks=[{"priority": "high", "title": "do X"}],
        recent_decisions=[],
        recent_lessons=[],
        notes_block="",
        timestamp=_FROZEN,
    )

    assert "<!-- pretel:notes:start -->" in out
    assert "## Operator notes" in out
    assert "(operator-edited content preserved across regenerations)" in out
    assert "## Open tasks" in out
    assert "- high — do X" in out


# ---------------------------------------------------------------------
# Round-trip + idempotency.
# ---------------------------------------------------------------------

def test_round_trip_preserves_notes_block_byte_for_byte(
    tmp_path: Path,
) -> None:
    """Render → write → parse returns the exact notes_block we passed in.

    This is the byte-for-byte contract that the operator-notes-survive-
    regeneration guarantee depends on (rationale doc §3 success
    criterion #4 implicitly + §2 design principle "git/DB boundary").
    """
    notes = "\n## Operator notes\n\nMy verbatim text\nsecond line\n"
    out = render_bucket_readme(
        bucket="personal",
        active_projects=[],
        archived_projects=[],
        skills=[],
        recent_decisions=[],
        count_open_tasks=0,
        notes_block=notes,
        timestamp=_FROZEN,
    )
    p = tmp_path / "rt.md"
    p.write_text(out, encoding="utf-8")
    parsed = parse_readme(p)

    assert parsed["notes_block"] == notes


def test_render_is_byte_identical_with_same_inputs() -> None:
    """The pure render function is deterministic given a fixed timestamp.

    The orchestrator-level idempotency (regenerate_* keeping the old
    timestamp when data unchanged) is exercised in test_awareness.py.
    Here we just confirm the pure layer has no hidden non-determinism
    (e.g., hash-order over a dict).
    """
    args = dict(
        bucket="personal",
        active_projects=[
            {"slug": "a", "name": "A", "status": "active", "objective": None},
            {"slug": "b", "name": "B", "status": "active", "objective": None},
        ],
        archived_projects=[],
        skills=[
            {"name": "sdd", "description_short": "Spec-driven"},
            {"name": "vett", "description_short": "Vendor eval"},
        ],
        recent_decisions=[],
        count_open_tasks=2,
        notes_block="\n## Operator notes\n\n(empty)\n",
        timestamp=_FROZEN,
    )

    first = render_bucket_readme(**args)  # type: ignore[arg-type]
    second = render_bucket_readme(**args)  # type: ignore[arg-type]
    assert first == second
