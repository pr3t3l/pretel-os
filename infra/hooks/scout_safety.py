#!/usr/bin/env python3
"""Pre-commit hook: block commits with Scout denylist patterns.

Per CONSTITUTION §3.2: any commit touching buckets/scout/ runs a keyword filter.
Denylist patterns loaded from infra/hooks/scout_denylist.yaml.
The denylist is operator-maintained, never edited by an LLM.
"""

import re
import sys
from pathlib import Path

import yaml

DENYLIST_PATH = Path(__file__).parent / "scout_denylist.yaml"

def load_denylist() -> list[re.Pattern]:
    """Load denylist patterns. If file missing, block nothing but warn."""
    if not DENYLIST_PATH.exists():
        print(
            "WARNING: scout_denylist.yaml not found at "
            f"{DENYLIST_PATH}. Scout safety check skipped.\n"
            "Create the file with a 'patterns' list to enable."
        )
        return []
    with open(DENYLIST_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    raw_patterns = data.get("patterns", [])
    compiled = []
    for p in raw_patterns:
        try:
            compiled.append(re.compile(p, re.IGNORECASE))
        except re.error as e:
            print(f"WARNING: invalid regex in scout_denylist.yaml: '{p}' — {e}")
    return compiled

def scan_file(filepath: str, patterns: list[re.Pattern]) -> list[str]:
    """Return list of matches found in file."""
    hits = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            for pat in patterns:
                if pat.search(line):
                    hits.append(
                        f"  Line {line_num}: pattern '{pat.pattern}' matched"
                    )
    return hits

def main() -> int:
    patterns = load_denylist()
    if not patterns:
        return 0  # No denylist = nothing to check (warning already printed)

    errors = []
    for filepath in sys.argv[1:]:
        hits = scan_file(filepath, patterns)
        if hits:
            errors.append(f"BLOCKED: {filepath}\n" + "\n".join(hits))

    if errors:
        print(
            "Scout safety check failed — potential proprietary content detected:\n"
        )
        print("\n".join(errors))
        print(
            "\nAction: reformulate content abstractly (patterns, not specifics) "
            "or remove the flagged content. The denylist is at "
            f"{DENYLIST_PATH}."
        )
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
