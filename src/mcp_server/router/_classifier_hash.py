"""Deterministic classifier-signal hash for the layer-bundle cache key.

Per plan/router/plan.md §4.5: cache invalidation requires a stable hash
over the classifier-driven signals that change which layers (and which
filter shapes) Phase B emits. Two turns with identical signals must
produce identical hashes; any field change must produce a different
hash. Hash truncated to 16 hex chars — sufficient namespace at the
expected cardinality (single operator).

Inputs are typed primitives so this helper stays independent of
ClassifierSignals (B.9). The orchestrator (assemble_bundle) calls this
with fields extracted from the dataclass.
"""
from __future__ import annotations

import hashlib
import json


def classifier_hash(
    *,
    bucket: str | None,
    project: str | None,
    complexity: str,
    needs_lessons: bool,
    needs_skills: bool,
    skill_ids: tuple[str, ...] | None,
    classifier_domain: str | None = None,
) -> str:
    """Return a 16-hex-char SHA-256 prefix over the canonical signals.

    The argument order is irrelevant — `sort_keys=True` ensures a stable
    JSON serialization. `skill_ids` is normalized to `None` when empty
    to make `[] == None == "no skills"` for cache-key purposes (caller
    semantics: both produce no L3 block).
    """
    payload = {
        "bucket": bucket,
        "project": project,
        "complexity": complexity,
        "needs_lessons": needs_lessons,
        "needs_skills": needs_skills,
        "skill_ids": list(skill_ids) if skill_ids else None,
        "classifier_domain": classifier_domain,
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]
