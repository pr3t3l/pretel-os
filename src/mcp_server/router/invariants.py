"""Registry of invariant check callables consumed by `invariant_detector`.

Per `specs/router/phase_c_close.md` §1 Q7, the registry convention is two
plain module-level dicts. Adding a new invariant is a two-step change:

1. Define the check function in this module.
2. Add one line to the appropriate registry dict (`INVARIANTS_PER_BLOCK`
   or `INVARIANTS_PER_BUNDLE`).

The detector module (`invariant_detector.py`) is intentionally NOT touched
when a new invariant is added — it iterates whatever the registries
contain at import time. No decorators, no auto-discovery, no plugin
system: the dict-add is the contract.

Per Q2, two distinct check signatures back two distinct registries:

- `CheckPerBlock` — runs against a single `ContextBlock` plus its
  layer name. Used by content-scoped invariants (Scout denylist,
  agent-rule breaches, git/DB boundary).
- `CheckPerBundle` — runs against the assembled `LayerBundle`. Used by
  aggregate invariants (budget ceiling), where one block's count alone
  cannot decide whether the layer overflows.

Each check returns a `list[InvariantViolation]` (not `Optional[...]`)
so a single block can produce multiple violations from one check pass.
"""
from __future__ import annotations

import re
from typing import Callable

from .types import ContextBlock, InvariantViolation, LayerBundle

CheckPerBlock = Callable[[ContextBlock, str], list[InvariantViolation]]
CheckPerBundle = Callable[[LayerBundle], list[InvariantViolation]]


# --- Q5: mention-vs-instruction filter --------------------------------------

NEGATION_TOKENS: tuple[str, ...] = (
    # English
    "never", "don't", "do not", "not allowed", "must not",
    "denied", "forbidden", "prohibited", "avoid",
    # Spanish (operator writes lessons in both)
    "nunca", "no debes", "prohibido", "no permitido", "evita",
)


def _is_mention_not_instruction(content: str, match_pos: int) -> bool:
    """Conservative ±50-char window filter per phase_c_close.md §1 Q5.

    Returns True if any NEGATION_TOKENS entry is found inside a
    ±50-character window around `match_pos`. A True result means the
    surrounding text is treated as a *mention* (e.g., a lesson that
    explains why the rule exists) and the calling check MUST NOT
    produce a violation.

    Pure: no I/O, no DB. Lowercases the window itself, so callers do
    not need to pre-lowercase `content`.
    """
    start = max(0, match_pos - 50)
    end = min(len(content), match_pos + 50)
    window = content[start:end].lower()
    return any(tok in window for tok in NEGATION_TOKENS)


def _find_all(haystack: str, needle: str) -> list[int]:
    """Non-overlapping occurrence positions of `needle` in `haystack`."""
    out: list[int] = []
    nlen = len(needle)
    start = 0
    while True:
        pos = haystack.find(needle, start)
        if pos == -1:
            return out
        out.append(pos)
        start = pos + nlen


# --- C.2.1: Scout denylist (stub) -------------------------------------------

def _scout_denylist_check(
    block: ContextBlock, layer: str
) -> list[InvariantViolation]:
    """STUB per phase_c_close.md Q3 (Scout denylist canonical source
    deferred). When implemented, will detect Scout-bucket denylist
    tokens in any block. Tracked as DEFERRED task in the tasks table.
    """
    return []


# --- C.2.3: agent rule — no guessing MCP tool params (CONSTITUTION §9.3) ----

_AGENT_RULE_NO_GUESSING_PATTERN = "guess mcp tool params"


def _agent_rule_no_guessing_check(
    block: ContextBlock, layer: str
) -> list[InvariantViolation]:
    """Detects CONSTITUTION §9.3 breaches — content instructing the
    agent to guess MCP tool parameters instead of calling
    `tool_search`. Q5 mention-filter applied.
    """
    lowered = block.content.lower()
    violations: list[InvariantViolation] = []
    for pos in _find_all(lowered, _AGENT_RULE_NO_GUESSING_PATTERN):
        if _is_mention_not_instruction(lowered, pos):
            continue
        violations.append(
            InvariantViolation(
                layer=layer,
                source=block.source,
                invariant_id="agent_rule_no_guessing",
                evidence=f"matched {_AGENT_RULE_NO_GUESSING_PATTERN!r} at pos {pos}",
                severity="critical",
            )
        )
    return violations


# --- C.2.4: agent rule — no fabrication (CONSTITUTION §9.2 + §9.5) ----------

_FABRICATION_PATTERNS: tuple[str, ...] = (
    "fabricate lesson",
    "fabricate a lesson",
    "invent a citation",
    "make up a source",
    "fabricate attribution",
)


def _agent_rule_no_fabrication_check(
    block: ContextBlock, layer: str
) -> list[InvariantViolation]:
    """Detects CONSTITUTION §9.2 (no fabricated attributions) + §9.5
    (no fabricated lessons). Q5 mention-filter applied per pattern.
    """
    lowered = block.content.lower()
    violations: list[InvariantViolation] = []
    for pat in _FABRICATION_PATTERNS:
        for pos in _find_all(lowered, pat):
            if _is_mention_not_instruction(lowered, pos):
                continue
            violations.append(
                InvariantViolation(
                    layer=layer,
                    source=block.source,
                    invariant_id="agent_rule_no_fabrication",
                    evidence=f"matched {pat!r} at pos {pos}",
                    severity="critical",
                )
            )
    return violations


# --- C.2.5: agent rule — no simulation (CONSTITUTION §9.7) ------------------

_SIMULATION_PATTERNS: tuple[str, ...] = (
    "simulate this code",
    "simulate the code",
    "mentally execute",
    "trace through this script",
    "trace through this code",
)


def _agent_rule_no_simulation_check(
    block: ContextBlock, layer: str
) -> list[InvariantViolation]:
    """Detects CONSTITUTION §9.7 breaches — content instructing the
    agent to mentally simulate code execution instead of invoking the
    matching MCP tool. Q5 mention-filter applied.
    """
    lowered = block.content.lower()
    violations: list[InvariantViolation] = []
    for pat in _SIMULATION_PATTERNS:
        for pos in _find_all(lowered, pat):
            if _is_mention_not_instruction(lowered, pos):
                continue
            violations.append(
                InvariantViolation(
                    layer=layer,
                    source=block.source,
                    invariant_id="agent_rule_no_simulation",
                    evidence=f"matched {pat!r} at pos {pos}",
                    severity="critical",
                )
            )
    return violations


# --- C.2.6: git/DB boundary (CONSTITUTION §2.4) -----------------------------

_GIT_DB_REGEXES: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"(also store|duplicate|mirror|both)[\w\s]{0,40}(git|repo)[\w\s]{0,40}(database|db|postgres|table)",
        re.IGNORECASE,
    ),
    re.compile(
        r"(also store|duplicate|mirror|both)[\w\s]{0,40}(database|db|postgres|table)[\w\s]{0,40}(git|repo)",
        re.IGNORECASE,
    ),
)


def _git_db_boundary_check(
    block: ContextBlock, layer: str
) -> list[InvariantViolation]:
    """Detects CONSTITUTION §2.4 breaches — content recommending a
    persistent asset be dual-homed across git AND the database.
    Conservative regex; the seed accepts false negatives over false
    positives per plan §5.5. Q5 mention-filter applied.
    """
    content = block.content
    violations: list[InvariantViolation] = []
    for rx in _GIT_DB_REGEXES:
        for m in rx.finditer(content):
            pos = m.start()
            if _is_mention_not_instruction(content, pos):
                continue
            matched = m.group(0)
            violations.append(
                InvariantViolation(
                    layer=layer,
                    source=block.source,
                    invariant_id="git_db_boundary",
                    evidence=f"matched {matched!r} at pos {pos}",
                    severity="critical",
                )
            )
    return violations


# --- C.2.7: budget ceiling (per-bundle, contract §7 + §11 5% slack) ---------

_LAYER_CEILINGS: dict[str, int] = {
    "L0": 1200,
    "L1": 3000,
    "L2": 5000,
    "L4": 4000,
}
# L3 intentionally absent — classifier-determined, no fixed ceiling per §7.

_BUDGET_SLACK = 0.05


def _budget_ceiling_check(bundle: LayerBundle) -> list[InvariantViolation]:
    """Detects layers whose `token_count` exceeds the contract §7
    budget plus the §11 5% slack permitted for proxy-tokenizer drift.

    `source` is a synthetic `f"layer:{layer}"` string here because a
    budget violation is layer-scoped, not block-scoped — no single
    `ContextBlock` owns the overflow. Downstream consumers should
    expect non-block-typed sources for `invariant_id="budget_ceiling"`.
    """
    violations: list[InvariantViolation] = []
    for layer in bundle.layers:
        ceiling = _LAYER_CEILINGS.get(layer.layer)
        if ceiling is None:
            continue
        if not layer.loaded:
            continue
        effective = int(ceiling * (1.0 + _BUDGET_SLACK))
        if layer.token_count <= effective:
            continue
        violations.append(
            InvariantViolation(
                layer=layer.layer,
                source=f"layer:{layer.layer}",
                invariant_id="budget_ceiling",
                evidence=(
                    f"layer {layer.layer} token_count={layer.token_count} "
                    f"exceeds ceiling {ceiling} (slack 5%)"
                ),
                severity="normal",
            )
        )
    return violations


# --- Registries (Q7: dict-add is the only extension contract) ---------------

INVARIANTS_PER_BLOCK: dict[str, CheckPerBlock] = {
    "scout_denylist": _scout_denylist_check,
    "agent_rule_no_guessing": _agent_rule_no_guessing_check,
    "agent_rule_no_fabrication": _agent_rule_no_fabrication_check,
    "agent_rule_no_simulation": _agent_rule_no_simulation_check,
    "git_db_boundary": _git_db_boundary_check,
}

INVARIANTS_PER_BUNDLE: dict[str, CheckPerBundle] = {
    "budget_ceiling": _budget_ceiling_check,
}
