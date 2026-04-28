"""Phase A.6.1 — Live classifier evaluation against the 10 worked examples.

Marked `@pytest.mark.eval` so it's OUT of the default pytest run (see
pytest.ini `addopts = -m "not eval"`). Run with `pytest -m eval`.

Skip guards (same pattern as A.4.3 integration test):
    - LiteLLM proxy must be reachable on 127.0.0.1:4000
    - ~/.env.litellm must contain LITELLM_MASTER_KEY=...

Per run: 10 live calls against `classifier_default` (currently Claude
Haiku 4.5 via LiteLLM cascade). Cost ~$0.003. A JSON report is written
to `tests/router/eval_results/eval_<UTC_TIMESTAMP>.json` BEFORE
threshold assertions so it persists even on failure.

Thresholds (binding):
    - bucket accuracy >= 0.80
    - complexity accuracy >= 0.70
    - schema violations == 0
"""
from __future__ import annotations

import json
import os
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from src.mcp_server.router.classifier import classify
from src.mcp_server.router.exceptions import (
    ClassifierError,
    ClassifierSchemaError,
)
from src.mcp_server.router.litellm_client import ChatJsonTelemetry
from tests.router.classification_examples_loader import (
    ClassificationExample,
    load_examples,
)

# Haiku 4.5 unit pricing (USD per token). Update when the cascade head
# changes. Source: Anthropic published pricing at A.4.3 ship date —
# $0.80/MTok input, $4.00/MTok output.
_PRICE_INPUT_PER_TOKEN = 0.80 / 1_000_000
_PRICE_OUTPUT_PER_TOKEN = 4.00 / 1_000_000

_REPORT_DIR = Path(__file__).parent / "eval_results"


def _proxy_reachable(
    host: str = "127.0.0.1", port: int = 4000, timeout: float = 0.5
) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _real_litellm_key() -> str | None:
    path = os.path.expanduser("~/.env.litellm")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        for line in f:
            if line.startswith("LITELLM_MASTER_KEY="):
                return line.split("=", 1)[1].strip()
    return None


def _telemetry_to_dict(t: ChatJsonTelemetry) -> dict[str, Any]:
    return {
        "finish_reason": t.finish_reason,
        "model": t.model,
        "prompt_tokens": t.prompt_tokens,
        "completion_tokens": t.completion_tokens,
        "reasoning_tokens": t.reasoning_tokens,
        "headroom_used_ratio": t.headroom_used_ratio,
        "near_truncation": t.near_truncation,
        "cache_hit": t.cache_hit,
    }


def _safe_avg(values: list[float | int | None]) -> float:
    clean = [float(v) for v in values if v is not None]
    return round(sum(clean) / len(clean), 4) if clean else 0.0


def _evaluate_one(
    example: ClassificationExample,
) -> dict[str, Any]:
    """Run one example through classify() and return a result record."""
    record: dict[str, Any] = {
        "title": example.title,
        "input": example.input_text,
        "expected": example.expected,
        "actual": None,
        "telemetry": None,
        "matches": {},
        "error": None,
    }
    try:
        actual, telemetry = classify(message=example.input_text)
    except ClassifierSchemaError as e:
        record["error"] = {
            "type": "ClassifierSchemaError",
            "message": str(e),
            "parsed_response": e.parsed_response,
        }
        if e.telemetry is not None:
            record["telemetry"] = _telemetry_to_dict(e.telemetry)
        return record
    except ClassifierError as e:
        tele_dict = (
            _telemetry_to_dict(e.telemetry) if e.telemetry is not None else None
        )
        record["error"] = {
            "type": type(e).__name__,
            "message": str(e),
        }
        record["telemetry"] = tele_dict
        return record

    record["actual"] = actual
    record["telemetry"] = _telemetry_to_dict(telemetry)
    record["matches"] = {
        "bucket": actual.get("bucket") == example.expected["bucket"],
        "complexity": actual.get("complexity") == example.expected["complexity"],
        "needs_lessons": (
            actual.get("needs_lessons") == example.expected["needs_lessons"]
        ),
        "project": actual.get("project") is None,
        "skill": actual.get("skill") is None,
    }
    return record


def _build_summary(
    results: list[dict[str, Any]], n_examples: int
) -> dict[str, Any]:
    schema_violations = sum(
        1
        for r in results
        if r["error"] and r["error"]["type"] == "ClassifierSchemaError"
    )
    provider_errors = sum(
        1
        for r in results
        if r["error"] and r["error"]["type"] != "ClassifierSchemaError"
    )

    successful = [r for r in results if r["actual"] is not None]

    def _accuracy(field: str) -> float:
        if not results:
            return 0.0
        hits = sum(1 for r in results if r["matches"].get(field) is True)
        return round(hits / len(results), 4)

    confidences = [
        r["actual"].get("confidence")
        for r in successful
        if isinstance(r["actual"].get("confidence"), (int, float))
    ]
    prompt_tokens = [
        r["telemetry"]["prompt_tokens"]
        for r in successful
        if r["telemetry"] is not None
    ]
    completion_tokens = [
        r["telemetry"]["completion_tokens"]
        for r in successful
        if r["telemetry"] is not None
    ]
    reasoning_tokens = [
        r["telemetry"]["reasoning_tokens"]
        for r in successful
        if r["telemetry"] is not None
    ]

    avg_prompt = _safe_avg(prompt_tokens)
    avg_completion = _safe_avg(completion_tokens)
    total_cost = round(
        n_examples
        * (
            avg_prompt * _PRICE_INPUT_PER_TOKEN
            + avg_completion * _PRICE_OUTPUT_PER_TOKEN
        ),
        6,
    )

    return {
        "bucket_accuracy": _accuracy("bucket"),
        "complexity_accuracy": _accuracy("complexity"),
        "needs_lessons_accuracy": _accuracy("needs_lessons"),
        "schema_violations": schema_violations,
        "provider_errors": provider_errors,
        "avg_confidence": _safe_avg(confidences),
        "avg_prompt_tokens": avg_prompt,
        "avg_completion_tokens": avg_completion,
        "avg_reasoning_tokens": _safe_avg(reasoning_tokens),
        "total_cost_usd_est": total_cost,
    }


@pytest.mark.eval
@pytest.mark.skipif(
    not _proxy_reachable(),
    reason="LiteLLM proxy not reachable on 127.0.0.1:4000",
)
def test_classifier_eval_against_worked_examples(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    key = _real_litellm_key()
    if not key:
        pytest.skip("real LITELLM_MASTER_KEY not present in ~/.env.litellm")
    monkeypatch.setenv("LITELLM_API_KEY", key)

    examples = load_examples()
    n_examples = len(examples)
    assert n_examples == 10, (
        f"eval expects exactly 10 examples; loader yielded {n_examples}"
    )

    _REPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = _REPORT_DIR / f"eval_{timestamp}.json"

    with capsys.disabled():
        print(f"\nEval report: {report_path}")

    results: list[dict[str, Any]] = [_evaluate_one(ex) for ex in examples]
    summary = _build_summary(results, n_examples)
    concrete_models_seen = sorted(
        {
            r["telemetry"]["model"]
            for r in results
            if r["telemetry"] is not None and r["telemetry"].get("model")
        }
    )

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "model_alias": "classifier_default",
        "concrete_models_seen": concrete_models_seen,
        "n_examples": n_examples,
        "summary": summary,
        "results": results,
    }

    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    assert summary["schema_violations"] == 0, (
        f"{summary['schema_violations']} schema violations seen — "
        f"see {report_path}"
    )
    assert summary["bucket_accuracy"] >= 0.80, (
        f"bucket accuracy {summary['bucket_accuracy']} below 0.80 threshold — "
        f"see {report_path}"
    )
    assert summary["complexity_accuracy"] >= 0.70, (
        f"complexity accuracy {summary['complexity_accuracy']} below 0.70 threshold — "
        f"see {report_path}"
    )
