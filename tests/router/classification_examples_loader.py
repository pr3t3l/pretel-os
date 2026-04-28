"""Parser for `tests/router/classification_examples.md`.

The markdown file is the single source of truth for the 10 worked
classifier examples (3 buckets x 3 complexity + 1 ambiguous). This
loader extracts (title, input, expected JSON) from the file so the
A.6.1 eval test can iterate over them without hardcoding strings.

If the file format ever drifts (heading style, fence language tag, etc.)
the parser fails loudly via assert. Update both this module and the
markdown together — the count assert (10 examples) is the canary.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

EXAMPLES_PATH = Path(__file__).parent / "classification_examples.md"
EXPECTED_COUNT = 10


@dataclass(frozen=True)
class ClassificationExample:
    title: str
    input_text: str
    expected: dict[str, Any]


_HEADING_RE = re.compile(r"^###\s+(Example\s+\d+:.*?)\s*$", re.MULTILINE)


def _extract_first_fenced_block(section: str, after_label: str) -> str:
    """Return the contents of the first ``` fenced block following `after_label`."""
    label_idx = section.find(after_label)
    if label_idx == -1:
        raise ValueError(f"section missing label {after_label!r}")
    rest = section[label_idx + len(after_label):]
    fence_match = re.search(r"```(?:\w+)?\n(.*?)\n```", rest, re.DOTALL)
    if not fence_match:
        raise ValueError(f"no fenced block after {after_label!r}")
    return fence_match.group(1).strip()


def load_examples() -> list[ClassificationExample]:
    """Parse the worked-examples markdown into ClassificationExample tuples.

    Asserts exactly EXPECTED_COUNT examples to catch silent drift
    (someone added an example to the markdown but forgot to bump the
    count, or vice versa).
    """
    text = EXAMPLES_PATH.read_text(encoding="utf-8")
    matches = list(_HEADING_RE.finditer(text))
    assert len(matches) == EXPECTED_COUNT, (
        f"expected {EXPECTED_COUNT} examples in {EXAMPLES_PATH.name}, "
        f"found {len(matches)}; update EXPECTED_COUNT or fix the file"
    )

    examples: list[ClassificationExample] = []
    for i, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section = text[start:end]

        input_text = _extract_first_fenced_block(section, "**Input:**")
        expected_raw = _extract_first_fenced_block(section, "**Expected output:**")
        expected: dict[str, Any] = json.loads(expected_raw)
        examples.append(
            ClassificationExample(
                title=title, input_text=input_text, expected=expected
            )
        )

    return examples
