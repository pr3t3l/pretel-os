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

from typing import Callable

from .types import ContextBlock, InvariantViolation, LayerBundle

CheckPerBlock = Callable[[ContextBlock, str], list[InvariantViolation]]
CheckPerBundle = Callable[[LayerBundle], list[InvariantViolation]]

INVARIANTS_PER_BLOCK: dict[str, CheckPerBlock] = {}
INVARIANTS_PER_BUNDLE: dict[str, CheckPerBundle] = {}
