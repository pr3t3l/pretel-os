"""Tests for the openclaw -> pretel-os taxonomy module.

Covers:
- Category remap (openclaw -> pretel-os enum) for every variant.
- Severity normalization (CRITICAL/HIGH/MEDIUM/LOW/unknown).
- Title derivation (short, long, multi-sentence).
- Platform tag derivation from `system` field for each source family.
- Content assembly with all fields and with optional fields missing.
- YAML entry parsing for LL-MASTER (lessons: wrapper) and
  LL-FORGE / LL-COPILOT-STUDIO (top-level array, `resolution` field).
- JSON workspace-cases parsing.
- needs_review flag for DRAFT / unknown severity / missing prevention.
- Bucket policy: Copilot Studio adds applicable_buckets=['scout'].
- Provenance tags always present.
- build_save_lesson_kwargs drops empty optional fields.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import openclaw_taxonomy as tx  # noqa: E402


# -------------------------------------------------- category remap


def test_category_remap_passthrough():
    for cat in ["PLAN", "ARCH", "COST", "INFRA", "AI", "CODE", "DATA", "OPS", "PROC"]:
        assert tx.normalize_category(cat) == cat


def test_category_remap_forge_extras():
    assert tx.normalize_category("BUILD") == "OPS"
    assert tx.normalize_category("QUAL") == "PROC"
    assert tx.normalize_category("N8N") == "INFRA"


def test_category_remap_copilot_extras():
    assert tx.normalize_category("DEPLOY") == "OPS"
    assert tx.normalize_category("DESIGN") == "ARCH"
    assert tx.normalize_category("PLATFORM") == "INFRA"
    assert tx.normalize_category("SEC") == "OPS"
    assert tx.normalize_category("TECH") == "AI"


def test_category_remap_unknown_falls_through_to_default():
    assert tx.normalize_category("UNKNOWN_CAT") == "PROC"
    assert tx.normalize_category(None) == "PROC"
    assert tx.normalize_category(None, default="DATA") == "DATA"


# -------------------------------------------------- severity


def test_severity_normalization():
    assert tx.normalize_severity("CRITICAL") == "critical"
    assert tx.normalize_severity("HIGH") == "moderate"
    assert tx.normalize_severity("MEDIUM") == "moderate"
    assert tx.normalize_severity("LOW") == "minor"


def test_severity_unknown_returns_none():
    assert tx.normalize_severity("unknown") is None
    assert tx.normalize_severity("") is None
    assert tx.normalize_severity(None) is None
    assert tx.normalize_severity("TBD") is None


# -------------------------------------------------- title


def test_title_short_passthrough():
    assert tx.derive_title("Short title.", "LL-X") == "Short title."


def test_title_long_truncates_with_ellipsis():
    long = "a" * 120 + "."
    out = tx.derive_title(long, "LL-X")
    assert out.endswith("...")
    assert len(out) == 80


def test_title_uses_first_sentence():
    text = "First sentence here. Second sentence is longer and not used."
    assert tx.derive_title(text, "LL-X") == "First sentence here."


def test_title_falls_back_to_id_when_empty():
    assert tx.derive_title("", "LL-PLAN-001") == "LL-PLAN-001"
    assert tx.derive_title(None, "LL-PLAN-001") == "LL-PLAN-001"


# -------------------------------------------------- platform tags


def test_platform_tags_openclaw_litellm():
    tags = tx.derive_platform_tags("OpenClaw/LiteLLM")
    assert "litellm" in tags
    assert "agent-platform" in tags
    assert "llm-infra" in tags


def test_platform_tags_openclaw_postgresql_normalizes():
    tags = tx.derive_platform_tags("OpenClaw/PostgreSQL")
    assert "postgres" in tags
    assert "agent-platform" in tags


def test_platform_tags_openclaw_both_skipped():
    tags = tx.derive_platform_tags("OpenClaw/both")
    assert "both" not in tags
    assert "agent-platform" in tags


def test_platform_tags_forge_n8n():
    tags = tx.derive_platform_tags("Forge/n8n")
    assert "n8n" in tags
    assert "workflows-platform" in tags


def test_platform_tags_copilot_studio_with_teams():
    tags = tx.derive_platform_tags("Copilot Studio / Teams")
    assert "copilot-studio" in tags
    assert "teams" in tags
    assert "workflows-platform" in tags


def test_platform_tags_knowledge_base_implies_rag():
    tags = tx.derive_platform_tags("Knowledge Base")
    assert "knowledge-base" in tags
    assert "rag" in tags


def test_platform_tags_empty_input():
    assert tx.derive_platform_tags(None) == []
    assert tx.derive_platform_tags("") == []


# -------------------------------------------------- content assembly


def test_yaml_content_full_fields():
    entry = {
        "problem_statement": "Pipeline broke.",
        "immediate_cause": "Bad input.",
        "root_cause": "No schema validation.",
        "contributing_factors": ["No tests", "Time pressure"],
        "failed_attempts": ["Tried X", "Tried Y"],
        "solution": "Add JSON schema validator.",
        "references": ["LL-AI-001"],
    }
    out = tx.assemble_yaml_content(entry)
    assert "**Problem:** Pipeline broke." in out
    assert "**Immediate cause:** Bad input." in out
    assert "**Root cause:** No schema validation." in out
    assert "**Contributing factors:**" in out
    assert "- No tests" in out
    assert "**Failed attempts:**" in out
    assert "- Tried X" in out
    assert "**Solution:** Add JSON schema validator." in out
    assert "**References:** LL-AI-001" in out


def test_yaml_content_uses_resolution_when_solution_missing():
    entry = {
        "problem_statement": "Card click does nothing.",
        "resolution": "Use Ask with Adaptive Card node.",
    }
    out = tx.assemble_yaml_content(entry)
    assert "Use Ask with Adaptive Card node." in out


def test_yaml_content_skips_unknown_failed_attempts():
    entry = {
        "problem_statement": "Bug",
        "failed_attempts": "unknown",
        "solution": "Fix",
    }
    out = tx.assemble_yaml_content(entry)
    assert "Failed attempts" not in out


def test_yaml_content_omits_empty_sections():
    entry = {"problem_statement": "Bug", "solution": "Fix"}
    out = tx.assemble_yaml_content(entry)
    assert "Immediate cause" not in out
    assert "Root cause" not in out
    assert "Contributing factors" not in out


def test_json_content_assembly():
    entry = {
        "problem": "Stub data passed validation.",
        "root_cause": "No placeholder check.",
        "fix_applied": "Added validate_placeholders.py.",
    }
    out = tx.assemble_json_content(entry)
    assert "**Problem:** Stub data passed validation." in out
    assert "**Root cause:** No placeholder check." in out
    assert "**Fix applied:** Added validate_placeholders.py." in out


# -------------------------------------------------- yaml entry -> lesson


def test_yaml_entry_master_basic():
    entry = {
        "id": "LL-PLAN-001",
        "category": "PLAN",
        "severity": "HIGH",
        "system": "OpenClaw/both",
        "status": "CONFIRMED",
        "problem_statement": "Orphan artifacts existed without consumers.",
        "root_cause": "No producer-consumer contract.",
        "solution": "Plan data flow before building.",
        "prevention_action": "Fail pipeline on orphans.",
        "keywords": ["data-flow", "planning"],
    }
    lesson = tx.yaml_entry_to_lesson(entry, source_file="LL-MASTER.yaml")
    assert lesson.source_id == "LL-PLAN-001"
    assert lesson.bucket == "business"
    assert lesson.applicable_buckets == []
    assert lesson.category == "PLAN"
    assert lesson.severity == "moderate"
    assert lesson.next_time == "Fail pipeline on orphans."
    assert lesson.needs_review is False
    assert "data-flow" in lesson.tags
    assert "planning" in lesson.tags
    assert "agent-platform" in lesson.tags
    assert "llm-infra" in lesson.tags
    assert "openclaw:ll-plan-001" in lesson.tags
    assert "migration:openclaw" in lesson.tags
    assert "openclaw-source:ll-master" in lesson.tags
    assert "needs-review" not in lesson.tags


def test_yaml_entry_marks_needs_review_when_severity_unknown():
    entry = {
        "id": "LL-PLAN-002",
        "category": "PLAN",
        "severity": "unknown",
        "system": "OpenClaw/both",
        "status": "CONFIRMED",
        "problem_statement": "Pipeline broke.",
        "solution": "Fix it.",
        "prevention_action": "Test first.",
    }
    lesson = tx.yaml_entry_to_lesson(entry, source_file="LL-MASTER.yaml")
    assert lesson.severity is None
    assert lesson.needs_review is True
    assert "needs-review" in lesson.tags


def test_yaml_entry_marks_needs_review_when_prevention_missing():
    entry = {
        "id": "LL-PLAN-003",
        "category": "PLAN",
        "severity": "HIGH",
        "system": "OpenClaw/both",
        "problem_statement": "Issue.",
        "solution": "Fix.",
        "prevention_action": "unknown",
    }
    lesson = tx.yaml_entry_to_lesson(entry, source_file="LL-MASTER.yaml")
    assert lesson.next_time is None
    assert lesson.needs_review is True


def test_yaml_entry_marks_needs_review_when_status_draft():
    entry = {
        "id": "LL-PLAN-004",
        "category": "PLAN",
        "severity": "HIGH",
        "system": "OpenClaw/both",
        "status": "DRAFT",
        "problem_statement": "Issue.",
        "solution": "Fix.",
        "prevention_action": "Add gate.",
    }
    lesson = tx.yaml_entry_to_lesson(entry, source_file="LL-MASTER.yaml")
    assert lesson.needs_review is True
    assert "needs-review" in lesson.tags


def test_yaml_entry_forge_with_n8n_category():
    entry = {
        "id": "LL-N8N-001",
        "category": "N8N",
        "severity": "MEDIUM",
        "system": "Forge/n8n",
        "status": "VALIDATED",
        "problem_statement": "n8n does not auto-throttle HTTP nodes.",
        "solution": "Add Wait node.",
        "prevention_action": "Wait node always inside the loop.",
        "keywords": ["rate-limit", "n8n"],
    }
    lesson = tx.yaml_entry_to_lesson(entry, source_file="LL-FORGE.yaml")
    assert lesson.category == "INFRA"  # N8N -> INFRA
    assert lesson.bucket == "business"
    assert lesson.applicable_buckets == []
    assert "n8n" in lesson.tags
    assert "workflows-platform" in lesson.tags
    assert "openclaw-source:ll-forge" in lesson.tags


def test_yaml_entry_copilot_studio_with_resolution_field():
    entry = {
        "id": "LL-CS-001",
        "category": "ARCH",
        "severity": "HIGH",
        "system": "Copilot Studio",
        "status": "VALIDATED",
        "problem_statement": "Adaptive Card buttons don't fire.",
        "resolution": "Use Ask with Adaptive Card node.",
        "prevention_action": "RULE: Action.Submit must use Ask node.",
        "keywords": ["adaptive-card", "action-submit"],
    }
    lesson = tx.yaml_entry_to_lesson(entry, source_file="LL-COPILOT-STUDIO.yaml")
    assert lesson.bucket == "business"
    assert lesson.applicable_buckets == ["scout"]  # cross-bucket policy
    assert "copilot-studio" in lesson.tags
    assert "workflows-platform" in lesson.tags
    assert "openclaw-source:ll-copilot-studio" in lesson.tags
    # `resolution` should appear in content (not `solution`)
    assert "Use Ask with Adaptive Card node." in lesson.content


def test_yaml_entry_copilot_design_remaps_to_arch():
    entry = {
        "id": "LL-CS-005",
        "category": "DESIGN",
        "severity": "HIGH",
        "system": "Copilot Studio",
        "problem_statement": "Topic was bypassed.",
        "resolution": "Aggressive trigger description.",
        "prevention_action": "Verify enabled.",
    }
    lesson = tx.yaml_entry_to_lesson(entry, source_file="LL-COPILOT-STUDIO.yaml")
    assert lesson.category == "ARCH"


def test_yaml_entry_missing_id_raises():
    import pytest

    with pytest.raises(ValueError):
        tx.yaml_entry_to_lesson({"problem_statement": "x"}, source_file="x.yaml")


# -------------------------------------------------- json entry -> lesson


def test_json_entry_basic():
    entry = {
        "id": "LL-001",
        "date": "2026-03-12",
        "case_slug": "el-asesinato-en-la-casa-inteligente",
        "phase": "narrative_architect",
        "category": "clue_catalog_quality",
        "problem": "Stub entries passed.",
        "root_cause": "No structural validator.",
        "fix_applied": "Add validate_narrative.py.",
        "applies_to": ["narrative-architect", "validate_narrative"],
    }
    lesson = tx.json_entry_to_lesson(entry, source_file="lessons_learned.json")
    assert lesson.source_id == "LL-001"
    assert lesson.bucket == "business"
    assert lesson.applicable_buckets == []
    assert lesson.next_time == "Add validate_narrative.py."
    assert lesson.needs_review is False
    assert "narrative-pipeline" in lesson.tags
    assert "agent-orchestration" in lesson.tags
    assert "declassified" in lesson.tags
    assert "narrative_architect" in lesson.tags
    assert "narrative-architect" in lesson.tags
    assert "validate_narrative" in lesson.tags
    # case_slug must NOT become a literal tag (anti-particularization rule)
    assert not any(t.startswith("el-asesinato") for t in lesson.tags)
    assert "openclaw-source:workspace_cases" in lesson.tags


def test_json_entry_no_fix_marks_pending():
    entry = {
        "id": "LL-099",
        "category": "schema_mismatch",
        "problem": "x",
        "root_cause": "y",
    }
    lesson = tx.json_entry_to_lesson(entry, source_file="lessons_learned.json")
    assert lesson.next_time is None
    assert lesson.needs_review is True
    assert "needs-review" in lesson.tags


def test_json_category_heuristic_routes_schema_to_data():
    entry = {
        "id": "LL-SCHEMA",
        "category": "schema_mismatch",
        "problem": "x",
        "fix_applied": "y",
    }
    lesson = tx.json_entry_to_lesson(entry, source_file="lessons_learned.json")
    assert lesson.category == "DATA"


def test_json_category_heuristic_routes_image_to_proc():
    entry = {
        "id": "LL-IMG",
        "category": "incomplete_image_coverage",
        "problem": "x",
        "fix_applied": "y",
    }
    lesson = tx.json_entry_to_lesson(entry, source_file="lessons_learned.json")
    assert lesson.category == "PROC"


# -------------------------------------------------- doc parsers


def test_parse_yaml_master_style_lessons_wrapper():
    text = """
meta:
  total_entries: 1
lessons:
  - id: LL-PLAN-001
    category: PLAN
    severity: HIGH
    system: OpenClaw/both
    problem_statement: Orphan artifacts existed.
    solution: Plan data flow.
    prevention_action: Fail on orphans.
    keywords: [planning, orphan]
"""
    out = tx.parse_yaml_lessons_doc(text, source_file="LL-MASTER.yaml")
    assert len(out) == 1
    assert out[0].source_id == "LL-PLAN-001"
    assert out[0].category == "PLAN"


def test_parse_yaml_top_level_array():
    text = """
- id: LL-ARCH-001
  category: ARCH
  severity: HIGH
  system: Forge/n8n
  problem_statement: Issue.
  solution: Fix.
  prevention_action: Add wait node.
  keywords:
    - n8n
    - rate-limit
- id: LL-ARCH-002
  category: BUILD
  severity: MEDIUM
  system: Forge/Docker
  problem_statement: Build.
  solution: Pin version.
  prevention_action: Lock dockerfile.
  keywords:
    - docker
"""
    out = tx.parse_yaml_lessons_doc(text, source_file="LL-FORGE.yaml")
    assert len(out) == 2
    assert out[0].source_id == "LL-ARCH-001"
    assert out[0].category == "ARCH"
    assert out[1].category == "OPS"  # BUILD -> OPS


def test_parse_json_workspace_cases():
    text = """
{
  "lessons": [
    {
      "id": "LL-001",
      "category": "schema_mismatch",
      "phase": "narrative_architect",
      "problem": "Stubs.",
      "root_cause": "No validator.",
      "fix_applied": "Validator added.",
      "applies_to": ["narrative-architect"]
    }
  ]
}
"""
    out = tx.parse_json_lessons_doc(text, source_file="lessons_learned.json")
    assert len(out) == 1
    assert out[0].source_id == "LL-001"
    assert out[0].category == "DATA"


# -------------------------------------------------- save_lesson kwargs


def test_build_kwargs_includes_required_fields():
    lesson = tx.OpenclawLesson(
        source_file="x",
        source_id="LL-001",
        title="t",
        content="c",
        next_time="n",
        bucket="business",
        applicable_buckets=[],
        category="PLAN",
        tags=["a"],
        severity="moderate",
        needs_review=False,
    )
    out = tx.build_save_lesson_kwargs(lesson)
    assert out["title"] == "t"
    assert out["content"] == "c"
    assert out["bucket"] == "business"
    assert out["category"] == "PLAN"
    assert out["tags"] == ["a"]
    assert out["next_time"] == "n"
    assert out["severity"] == "moderate"
    assert "applicable_buckets" not in out


def test_build_kwargs_drops_empty_optionals():
    lesson = tx.OpenclawLesson(
        source_file="x",
        source_id="LL-001",
        title="t",
        content="c",
        next_time=None,
        bucket="business",
        applicable_buckets=[],
        category="PLAN",
        tags=["a"],
        severity=None,
        needs_review=True,
    )
    out = tx.build_save_lesson_kwargs(lesson)
    assert "next_time" not in out
    assert "severity" not in out
    assert "applicable_buckets" not in out


def test_build_kwargs_includes_applicable_buckets_when_set():
    lesson = tx.OpenclawLesson(
        source_file="x",
        source_id="LL-001",
        title="t",
        content="c",
        next_time="n",
        bucket="business",
        applicable_buckets=["scout"],
        category="ARCH",
        tags=["a"],
        severity="moderate",
        needs_review=False,
    )
    out = tx.build_save_lesson_kwargs(lesson)
    assert out["applicable_buckets"] == ["scout"]


def test_build_kwargs_suppresses_next_time_for_needs_review_and_folds_into_content():
    """needs_review=True forces pending_review by withholding next_time;
    the prevention text gets preserved in content as a labeled section."""
    lesson = tx.OpenclawLesson(
        source_file="x",
        source_id="LL-001",
        title="t",
        content="**Problem:** something broke.",
        next_time="Add validation gate.",
        bucket="business",
        applicable_buckets=[],
        category="PLAN",
        tags=["a"],
        severity=None,
        needs_review=True,
    )
    out = tx.build_save_lesson_kwargs(lesson)
    assert "next_time" not in out
    assert "**Suggested prevention (needs review):** Add validation gate." in out["content"]
    assert "**Problem:** something broke." in out["content"]


def test_build_kwargs_passes_next_time_when_not_needs_review():
    lesson = tx.OpenclawLesson(
        source_file="x",
        source_id="LL-002",
        title="t",
        content="**Problem:** ok",
        next_time="Add gate.",
        bucket="business",
        applicable_buckets=[],
        category="PLAN",
        tags=["a"],
        severity="moderate",
        needs_review=False,
    )
    out = tx.build_save_lesson_kwargs(lesson)
    assert out["next_time"] == "Add gate."
    assert "Suggested prevention" not in out["content"]
