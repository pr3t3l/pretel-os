"""Keyword lists for the rule-based fallback classifier (spec §10.1).

Used by `fallback_classifier.py` when LiteLLM is unreachable or its
response cannot be parsed/validated. Keywords are derived from
`identity.md` bucket descriptions and the operator's stated domains.
A keyword change is a code change with a test (D.0.3).

Order of `BUCKET_KEYWORDS` keys matters: per spec §10.1 step 2,
iteration is in dict-insertion order and the first bucket with any
keyword match wins. `personal` is checked before `business` before
`scout` so generic life topics don't get pulled into work buckets.

Substring matching is intentional (spec algorithm: "if any keyword
appears in message"). Keyword choices avoid common English-word
collisions (no "the", no "and", etc.); we accept rare false positives
like "hi" inside "this" given fallback runs only when the LLM path is
already broken.
"""
from __future__ import annotations

BUCKET_KEYWORDS: dict[str, list[str]] = {
    "personal": [
        "personal", "family", "daughter", "kindergarten",
        "rental", "house", "home", "travel",
    ],
    "business": [
        "business", "freelance", "client", "n8n",
        "vett", "sdd", "declassified", "pretel-os",
        "consulting", "invoice",
    ],
    "scout": [
        "scout", "w2", "assembly", "manufacturing",
        "shift", "plant", "station",
    ],
}

COMPLEXITY_KEYWORDS: dict[str, list[str]] = {
    "HIGH": [
        "debug", "architect", "recommend", "design",
        "why does", "why is", "decide", "compare",
        "evaluate", "review",
    ],
    "LOW": [
        "hi", "hello", "hey", "thanks", "thank",
        "ok", "okay", "yes", "got it",
    ],
}
