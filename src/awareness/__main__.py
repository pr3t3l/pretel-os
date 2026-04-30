"""Entry point: `python -m awareness.readme_consumer`.

A bare `python -m awareness` is also accepted for symmetry with other
worker modules; it dispatches into `readme_consumer.main()`.
"""
from __future__ import annotations

from awareness.readme_consumer import main


if __name__ == "__main__":
    main()
