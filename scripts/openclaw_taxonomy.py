"""scripts/openclaw_taxonomy.py — pure mapping module for openclaw migration.

No IO, no DB. Parses source files (YAML / JSON) into a normalized
`OpenclawLesson` dataclass, then maps into the kwargs accepted by the
`save_lesson` MCP tool.

Three source formats:
- LL-MASTER.yaml: top-level `meta:` + `lessons:` array (entries indented).
- LL-FORGE.yaml / LL-COPILOT-STUDIO.yaml: top-level array of mappings.
- workspace/cases/config/lessons_learned.json: `{"lessons": [...]}` with
  case-workflow specific fields.

LL-COPILOT-STUDIO uses `resolution` where the others use `solution`.
LL-FORGE adds categories BUILD/N8N/QUAL; LL-COPILOT-STUDIO adds
DEPLOY/DESIGN/PLATFORM/SEC/TECH. All remap to the pretel-os enum
(PLAN | ARCH | COST | INFRA | AI | CODE | DATA | OPS | PROC).

Bucket policy is knowledge-driven, not file-driven: every lesson goes
to `business` by default; Copilot Studio adds `applicable_buckets=['scout']`
because the platform knowledge applies wherever the operator uses it.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml


PRETEL_CATEGORIES = {"PLAN", "ARCH", "COST", "INFRA", "AI", "CODE", "DATA", "OPS", "PROC"}

CATEGORY_REMAP = {
    # LL-FORGE additions
    "BUILD": "OPS",
    "QUAL": "PROC",
    "N8N": "INFRA",
    # LL-COPILOT-STUDIO additions
    "DEPLOY": "OPS",
    "DESIGN": "ARCH",
    "PLATFORM": "INFRA",
    "SEC": "OPS",
    "TECH": "AI",
}

SEVERITY_REMAP: dict[str, str | None] = {
    "CRITICAL": "critical",
    "HIGH": "moderate",
    "MEDIUM": "moderate",
    "LOW": "minor",
}

JSON_CATEGORY_HEURISTICS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"schema|catalog|data|content|json|placeholder", re.I), "DATA"),
    (re.compile(r"image|coverage|template|render|quality", re.I), "PROC"),
    (re.compile(r"hardcoded|stub|code|bug", re.I), "CODE"),
    (re.compile(r"prompt|hallucinat|llm|model", re.I), "AI"),
    (re.compile(r"deploy|infra|build|operation", re.I), "OPS"),
]


@dataclass
class OpenclawLesson:
    source_file: str
    source_id: str
    title: str
    content: str
    next_time: str | None
    bucket: str
    applicable_buckets: list[str]
    category: str
    tags: list[str]
    severity: str | None
    needs_review: bool
    raw: dict[str, Any] = field(default_factory=dict)


def normalize_category(raw: str | None, *, default: str = "PROC") -> str:
    if not raw:
        return default
    up = raw.strip().upper()
    if up in PRETEL_CATEGORIES:
        return up
    return CATEGORY_REMAP.get(up, default)


def normalize_severity(raw: Any) -> str | None:
    if not raw:
        return None
    up = str(raw).strip().upper()
    if up in {"UNKNOWN", "TBD", "N/A"}:
        return None
    return SEVERITY_REMAP.get(up)


def derive_title(problem: str | None, fallback_id: str) -> str:
    if not problem:
        return fallback_id
    text = problem.strip().replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    first_sentence_match = re.search(r"^(.+?[.!?])(?:\s|$)", text)
    candidate = first_sentence_match.group(1) if first_sentence_match else text
    if len(candidate) <= 80:
        return candidate
    return candidate[:77].rstrip() + "..."


def derive_platform_tags(system_field: str | None) -> list[str]:
    """Tag derivation from openclaw `system` field.

    Returns platform/tech tags + knowledge-area tags. Examples:
      'OpenClaw/LiteLLM' -> ['litellm', 'agent-platform', 'llm-infra']
      'Forge/n8n' -> ['n8n', 'workflows-platform']
      'Copilot Studio / Teams' -> ['copilot-studio', 'teams', 'workflows-platform']
    """
    if not system_field:
        return []
    raw = system_field.strip()
    parts = [p.strip() for p in re.split(r"[/]", raw) if p.strip()]
    tags: list[str] = []
    knowledge_area: list[str] = []

    for part in parts:
        slug = part.lower().replace(" ", "-")
        if slug == "openclaw":
            knowledge_area += ["agent-platform", "llm-infra"]
        elif slug == "forge":
            knowledge_area += ["workflows-platform"]
        elif slug == "copilot-studio":
            tags.append("copilot-studio")
            knowledge_area += ["workflows-platform"]
        elif slug == "knowledge-base":
            tags.append("knowledge-base")
            knowledge_area += ["rag"]
        elif slug == "both":
            continue
        elif slug == "postgresql":
            tags.append("postgres")
        elif slug:
            tags.append(slug)

    return list(dict.fromkeys(tags + knowledge_area))


def _bullet_list(items: Iterable[Any]) -> str:
    rendered = []
    for it in items:
        text = str(it).strip()
        if text:
            rendered.append(f"- {text}")
    return "\n".join(rendered)


def assemble_yaml_content(entry: dict[str, Any]) -> str:
    sections: list[str] = []
    problem = (entry.get("problem_statement") or "").strip()
    if problem:
        sections.append(f"**Problem:** {problem}")

    immediate = (entry.get("immediate_cause") or "").strip()
    if immediate:
        sections.append(f"**Immediate cause:** {immediate}")

    root = (entry.get("root_cause") or "").strip()
    if root:
        sections.append(f"**Root cause:** {root}")

    factors = entry.get("contributing_factors")
    if isinstance(factors, list) and factors:
        sections.append("**Contributing factors:**\n" + _bullet_list(factors))

    failed = entry.get("failed_attempts")
    if isinstance(failed, list) and failed:
        sections.append("**Failed attempts:**\n" + _bullet_list(failed))
    elif isinstance(failed, str) and failed.strip() and failed.strip().lower() != "unknown":
        sections.append(f"**Failed attempts:** {failed.strip()}")

    solution = (entry.get("solution") or entry.get("resolution") or "").strip()
    if solution:
        sections.append(f"**Solution:** {solution}")

    refs = entry.get("references")
    if isinstance(refs, list) and refs:
        rendered = ", ".join(str(r) for r in refs)
        sections.append(f"**References:** {rendered}")

    return "\n\n".join(sections)


def assemble_json_content(entry: dict[str, Any]) -> str:
    sections: list[str] = []
    problem = (entry.get("problem") or "").strip()
    if problem:
        sections.append(f"**Problem:** {problem}")
    root = (entry.get("root_cause") or "").strip()
    if root:
        sections.append(f"**Root cause:** {root}")
    fix = (entry.get("fix_applied") or "").strip()
    if fix:
        sections.append(f"**Fix applied:** {fix}")
    return "\n\n".join(sections)


def _bucket_policy_for_yaml(source_file: str) -> tuple[str, list[str]]:
    """Knowledge-driven bucket assignment per source file.

    Returns (bucket, applicable_buckets). All openclaw-* lessons land in
    business by default; Copilot Studio cross-applies to scout because
    the platform knowledge applies wherever the operator uses it.
    """
    if "COPILOT-STUDIO" in source_file:
        return ("business", ["scout"])
    return ("business", [])


def _normalize_tag(raw: str) -> str:
    s = raw.strip().lower()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^a-z0-9:_\-./]", "", s)
    return s


def _normalize_keyword_list(raw: Any) -> list[str]:
    if not raw:
        return []
    if isinstance(raw, str):
        raw = [raw]
    out: list[str] = []
    for item in raw:
        norm = _normalize_tag(str(item))
        if norm:
            out.append(norm)
    return out


def yaml_entry_to_lesson(entry: dict[str, Any], *, source_file: str) -> OpenclawLesson:
    source_id = str(entry.get("id") or entry.get("old_id") or "").strip()
    if not source_id:
        raise ValueError(f"YAML entry missing id field: {entry!r}")

    problem = (entry.get("problem_statement") or "").strip()
    title = derive_title(problem, source_id)
    content = assemble_yaml_content(entry)
    if not content:
        content = f"(no narrative content in source entry {source_id})"

    prevention = (entry.get("prevention_action") or "").strip()
    if prevention.lower() in {"", "unknown"}:
        next_time: str | None = None
    else:
        next_time = prevention

    raw_severity = entry.get("severity")
    severity = normalize_severity(raw_severity)
    raw_status = str(entry.get("status") or "").strip().upper()

    needs_review = severity is None or raw_status == "DRAFT" or next_time is None

    bucket, applicable = _bucket_policy_for_yaml(source_file)

    keywords = _normalize_keyword_list(entry.get("keywords"))
    platform_tags = derive_platform_tags(entry.get("system"))
    provenance = [
        f"openclaw:{source_id.lower()}",
        "migration:openclaw",
        f"openclaw-source:{Path(source_file).stem.lower()}",
    ]
    triage = ["needs-review"] if needs_review else []
    tags = list(dict.fromkeys(keywords + platform_tags + provenance + triage))

    category = normalize_category(entry.get("category"), default="PROC")

    return OpenclawLesson(
        source_file=source_file,
        source_id=source_id,
        title=title,
        content=content,
        next_time=next_time,
        bucket=bucket,
        applicable_buckets=applicable,
        category=category,
        tags=tags,
        severity=severity,
        needs_review=needs_review,
        raw=entry,
    )


def json_entry_to_lesson(entry: dict[str, Any], *, source_file: str) -> OpenclawLesson:
    source_id = str(entry.get("id") or "").strip()
    if not source_id:
        raise ValueError(f"JSON entry missing id field: {entry!r}")

    problem = (entry.get("problem") or "").strip()
    title = derive_title(problem, source_id)
    content = assemble_json_content(entry)
    if not content:
        content = f"(no narrative content in source entry {source_id})"

    fix = (entry.get("fix_applied") or "").strip()
    next_time: str | None = fix if fix else None

    raw_category = str(entry.get("category") or "").strip()
    category = "PROC"
    if raw_category:
        for pat, mapped in JSON_CATEGORY_HEURISTICS:
            if pat.search(raw_category):
                category = mapped
                break
        else:
            category = "DATA"

    phase = str(entry.get("phase") or "").strip().lower()
    applies_to = entry.get("applies_to") or []
    raw_keyword_tags = []
    if phase:
        raw_keyword_tags.append(_normalize_tag(phase))
    raw_keyword_tags.extend(_normalize_tag(str(x)) for x in applies_to if str(x).strip())

    knowledge_tags = ["narrative-pipeline", "agent-orchestration", "declassified"]
    provenance = [
        f"openclaw:{source_id.lower()}",
        "migration:openclaw",
        "openclaw-source:workspace_cases",
    ]
    needs_review = next_time is None
    triage = ["needs-review"] if needs_review else []

    tags = list(dict.fromkeys(raw_keyword_tags + knowledge_tags + provenance + triage))

    return OpenclawLesson(
        source_file=source_file,
        source_id=source_id,
        title=title,
        content=content,
        next_time=next_time,
        bucket="business",
        applicable_buckets=[],
        category=category,
        tags=tags,
        severity=None,
        needs_review=needs_review,
        raw=entry,
    )


def parse_yaml_lessons_doc(text: str, *, source_file: str) -> list[OpenclawLesson]:
    """Parse either LL-MASTER (lessons: wrapper) or LL-FORGE / LL-COPILOT-STUDIO (top-level array)."""
    docs = list(yaml.safe_load_all(text))
    entries: list[dict[str, Any]] = []
    for doc in docs:
        if doc is None:
            continue
        if isinstance(doc, list):
            entries.extend([d for d in doc if isinstance(d, dict)])
        elif isinstance(doc, dict):
            if isinstance(doc.get("lessons"), list):
                entries.extend([d for d in doc["lessons"] if isinstance(d, dict)])
            elif "id" in doc:
                entries.append(doc)
    return [yaml_entry_to_lesson(e, source_file=source_file) for e in entries]


def parse_json_lessons_doc(text: str, *, source_file: str) -> list[OpenclawLesson]:
    payload = json.loads(text)
    if isinstance(payload, dict):
        entries = payload.get("lessons", [])
    elif isinstance(payload, list):
        entries = payload
    else:
        return []
    return [json_entry_to_lesson(e, source_file=source_file) for e in entries if isinstance(e, dict)]


def parse_source_file(path: Path) -> list[OpenclawLesson]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        return parse_yaml_lessons_doc(text, source_file=path.name)
    if path.suffix.lower() == ".json":
        return parse_json_lessons_doc(text, source_file=path.name)
    raise ValueError(f"Unsupported source format: {path.suffix} ({path})")


def build_save_lesson_kwargs(lesson: OpenclawLesson) -> dict[str, Any]:
    """Return kwargs ready to splat into save_lesson(...).

    Suppresses auto-approval for needs_review lessons by withholding
    next_time (per CONSTITUTION 5.2 rule 13, missing next_time forces
    pending_review). The prevention text is folded into content as a
    labeled section so the information is preserved — the operator can
    promote it to next_time during pending review.

    Keys not accepted by the tool are dropped.
    """
    content = lesson.content
    if lesson.needs_review and lesson.next_time:
        suffix = f"\n\n**Suggested prevention (needs review):** {lesson.next_time}"
        content = content + suffix

    payload: dict[str, Any] = {
        "title": lesson.title,
        "content": content,
        "bucket": lesson.bucket,
        "tags": lesson.tags,
        "category": lesson.category,
    }
    if lesson.next_time and not lesson.needs_review:
        payload["next_time"] = lesson.next_time
    if lesson.severity:
        payload["severity"] = lesson.severity
    if lesson.applicable_buckets:
        payload["applicable_buckets"] = lesson.applicable_buckets
    return payload


SOURCE_FILES = {
    "master": "lessons-learned/LL-MASTER.yaml",
    "forge": "lessons-learned/LL-FORGE.yaml",
    "copilot": "lessons-learned/LL-COPILOT-STUDIO.yaml",
    "cases": "workspace/cases/config/lessons_learned.json",
}


def collect_lessons(repo_root: Path, *, sources: Iterable[str]) -> list[OpenclawLesson]:
    out: list[OpenclawLesson] = []
    for key in sources:
        rel = SOURCE_FILES[key]
        path = repo_root / rel
        if not path.exists():
            raise FileNotFoundError(f"Expected source file missing: {path}")
        out.extend(parse_source_file(path))
    return out
