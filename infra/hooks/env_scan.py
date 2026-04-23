#!/usr/bin/env python3
"""Pre-commit hook: block commits containing secrets or .env files.

Per CONSTITUTION §3.4: secrets never live in git.
Scans for:
  - Files matching *.env* (except *.env.*.example)
  - Content containing sk-ant-, sk-proj-, sk-litellm- patterns
"""

import re
import sys
from pathlib import Path

# Filename patterns that should never be committed
BLOCKED_FILENAMES = re.compile(r"\.env(?!\.\w+\.example$)")

# Content patterns that indicate leaked secrets
SECRET_PATTERNS = [
    re.compile(r"sk-ant-api\w{2}-[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk-proj-[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk-litellm-[A-Za-z0-9_-]{5,}"),
    re.compile(r"TELEGRAM_BOT_TOKEN=\d+:[A-Za-z0-9_-]{30,}"),
]

# Files to skip content scanning (binary, etc.)
SKIP_EXTENSIONS = {".pyc", ".pyo", ".gz", ".zip", ".tar", ".png", ".jpg", ".gpg"}

def main() -> int:
    errors = []

    for filepath in sys.argv[1:]:
        path = Path(filepath)

        # Check 1: blocked filename pattern
        if BLOCKED_FILENAMES.search(path.name):
            errors.append(
                f"BLOCKED: {filepath} — .env files must not be committed. "
                f"Use .env.*.example for templates."
            )
            continue

        # Check 2: skip binary files
        if path.suffix in SKIP_EXTENSIONS:
            continue

        # Check 3: scan content for secret patterns
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except (OSError, UnicodeDecodeError):
            continue

        for pat in SECRET_PATTERNS:
            matches = pat.findall(content)
            if matches:
                # Don't print the actual secret — just the pattern name
                errors.append(
                    f"BLOCKED: {filepath} — contains what looks like a real "
                    f"secret matching pattern '{pat.pattern[:30]}...'. "
                    f"Remove the secret and use environment variables instead."
                )
                break  # One match per file is enough

    if errors:
        print("Environment/secret scan failed:\n")
        print("\n".join(errors))
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
