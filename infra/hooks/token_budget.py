#!/usr/bin/env python3
"""Pre-commit hook: enforce token budgets per CONSTITUTION §2.3.

L0 identity.md         <= 1,200 tokens
L1 buckets/*/README.md <= 1,500 tokens
L2 buckets/*/projects/*/README.md <= 2,000 tokens
L3 skills/*.md         <= 4,000 tokens
"""

import sys
import tiktoken

BUDGETS = {
    "identity.md": 1200,
    "buckets/": 1500,      # L1 — any README.md directly under a bucket
    "projects/": 2000,     # L2 — any README.md under projects/
    "skills/": 4000,       # L3
}

def get_budget(filepath: str) -> tuple[int, str] | None:
    """Return (budget, layer_name) for a file, or None if not budget-controlled."""
    if filepath == "identity.md":
        return 1200, "L0 identity"
    if "/skills/" in filepath or filepath.startswith("skills/"):
        return 4000, "L3 skill"
    # L2 must be checked before L1 (more specific path)
    if "/projects/" in filepath and filepath.endswith("README.md"):
        return 2000, "L2 project"
    if "/buckets/" in filepath or filepath.startswith("buckets/"):
        if filepath.endswith("README.md"):
            return 1500, "L1 bucket"
    return None

def count_tokens(filepath: str) -> int:
    enc = tiktoken.get_encoding("cl100k_base")
    with open(filepath, "r", encoding="utf-8") as f:
        return len(enc.encode(f.read()))

def main() -> int:
    errors = []
    for filepath in sys.argv[1:]:
        result = get_budget(filepath)
        if result is None:
            continue
        budget, layer = result
        tokens = count_tokens(filepath)
        if tokens > budget:
            pct = int(tokens / budget * 100)
            errors.append(
                f"BLOCKED: {filepath} ({layer}) has {tokens} tokens "
                f"({pct}% of {budget} budget).\n"
                f"  Action: refactor the file to fit within {budget} tokens. "
                f"Do not truncate — restructure content."
            )
    if errors:
        print("Token budget enforcement failed:\n")
        print("\n".join(errors))
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
