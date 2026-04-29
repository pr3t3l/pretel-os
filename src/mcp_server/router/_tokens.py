"""Token counting per contract §11.

Phase B uses tiktoken cl100k_base for ALL token counts to keep the
budget arithmetic consistent across layers and consistent with what
downstream LLM consumers will count.
"""
from __future__ import annotations

import functools

import tiktoken


@functools.lru_cache(maxsize=1)
def _encoder() -> tiktoken.Encoding:
    return tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Return the cl100k_base token count for `text`."""
    return len(_encoder().encode(text))
