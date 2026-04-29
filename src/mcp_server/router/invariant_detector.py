"""Phase C invariant-violation detector — passive bundle scanner.

Per `specs/router/phase_c_close.md` §2 C.3.1: this module exposes one
public function, `detect_invariant_violations`, that walks an
already-assembled `LayerBundle` and returns the concatenated output of
every check registered in `invariants.py`.

Phase C is intentionally *passive* — the detector neither mutates the
bundle nor blocks the request. Phase D consumes the returned list and
serializes it into `routing_logs.source_conflicts`. Adding a new
invariant requires editing `invariants.py` only; this module never
needs to change (the registries are iterated, not enumerated).

Determinism: per-block checks run before per-bundle checks. Within
each phase, the order is (a) registry insertion order, then (b) layer
order L0..L4, then (c) block order within each layer. Python ≥3.7
dict iteration preserves insertion order, so the resulting list is
reproducible across runs given identical inputs.

Pure function — no DB, no I/O, no LLM calls, no logging.
"""
from __future__ import annotations

from .invariants import INVARIANTS_PER_BLOCK, INVARIANTS_PER_BUNDLE
from .types import InvariantViolation, LayerBundle


def detect_invariant_violations(bundle: LayerBundle) -> list[InvariantViolation]:
    """Run every registered invariant check against `bundle`.

    Returns a flat list of `InvariantViolation`s in deterministic
    order (see module docstring). An empty list means the bundle is
    clean — same shape as a no-op `INSERT` into `source_conflicts`.
    """
    violations: list[InvariantViolation] = []
    for layer in bundle.layers:
        for block in layer.blocks:
            for check_fn in INVARIANTS_PER_BLOCK.values():
                violations.extend(check_fn(block, layer.layer))
    for bundle_check_fn in INVARIANTS_PER_BUNDLE.values():
        violations.extend(bundle_check_fn(bundle))
    return violations
