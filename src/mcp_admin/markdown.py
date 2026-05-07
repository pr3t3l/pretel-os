"""Markdown → HTML rendering for the admin console.

markdown-it-py with the GFM-table + linkify + strikethrough plugins.
Used by drill-down views that show skill .md files and project READMEs.
Phase C decision Q2 (default per spec.md §6).
"""
from __future__ import annotations

from markdown_it import MarkdownIt
from mdit_py_plugins.tasklists import tasklists_plugin

_md = (
    MarkdownIt("commonmark", {"html": False, "linkify": True, "typographer": True})
    .enable("table")
    .enable("strikethrough")
    .use(tasklists_plugin)
)


def render(content: str) -> str:
    """Render markdown to HTML. Empty input returns empty string."""
    if not content:
        return ""
    html: str = _md.render(content)
    return html
