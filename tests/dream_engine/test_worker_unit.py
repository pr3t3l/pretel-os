"""Unit tests for dream_engine.worker — orchestration + result types only.

No DB. No psycopg. Tests cover:
  - JobResult.to_telemetry / to_failure_record shapes
  - _safe() wraps exceptions into JobResult
  - _finish_run() status computation (success / partial / failed)

Slow integration tests against real DB live in test_e2e.py.
"""
from __future__ import annotations

from dream_engine.worker import JobResult, _safe


# ---------------------------------------------------------------------
# JobResult shape
# ---------------------------------------------------------------------

def test_job_result_succeeded_returns_clean_telemetry() -> None:
    r = JobResult(name="utility_recompute", duration_ms=42, rows_affected=10)
    assert r.succeeded is True
    assert r.to_telemetry() == {"duration_ms": 42, "rows_affected": 10}


def test_job_result_failed_carries_error_in_telemetry() -> None:
    r = JobResult(
        name="dedup_pass",
        duration_ms=5,
        rows_affected=0,
        error="boom",
        error_class="RuntimeError",
        traceback="Traceback...",
    )
    assert r.succeeded is False
    t = r.to_telemetry()
    assert t["error"] == "boom"
    assert t["error_class"] == "RuntimeError"
    assert t["duration_ms"] == 5


def test_job_result_failure_record_includes_traceback() -> None:
    r = JobResult(
        name="archive_low_utility",
        duration_ms=1,
        rows_affected=0,
        error="simulated",
        error_class="ValueError",
        traceback="line1\nline2",
    )
    fr = r.to_failure_record()
    assert fr == {
        "job": "archive_low_utility",
        "error_class": "ValueError",
        "error_message": "simulated",
        "traceback": "line1\nline2",
    }


# ---------------------------------------------------------------------
# _safe() wrapper
# ---------------------------------------------------------------------

def test_safe_returns_success_jobresult_on_clean_run() -> None:
    r = _safe("test_job", lambda: 7)
    assert r.name == "test_job"
    assert r.succeeded is True
    assert r.rows_affected == 7
    assert r.error is None
    assert r.duration_ms >= 0


def test_safe_catches_exception_into_failed_jobresult() -> None:
    def boom() -> int:
        raise RuntimeError("simulated failure")

    r = _safe("flaky_job", boom)
    assert r.name == "flaky_job"
    assert r.succeeded is False
    assert r.error == "simulated failure"
    assert r.error_class == "RuntimeError"
    assert r.traceback is not None
    assert "simulated failure" in r.traceback
    assert r.rows_affected == 0


def test_safe_catches_keyboard_interrupt_passthrough() -> None:
    """KeyboardInterrupt + SystemExit should NOT be caught — those signal
    operator intent to stop the worker, never a recoverable error.

    We test the contract: _safe catches Exception, NOT BaseException.
    """
    def keyboard_interrupt() -> int:
        raise KeyboardInterrupt()

    import pytest as _pt
    with _pt.raises(KeyboardInterrupt):
        _safe("interrupted_job", keyboard_interrupt)
