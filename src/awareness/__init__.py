"""Module 7.5 awareness layer.

Connects the live `projects` table to the bucket and project README files
on disk via deterministic, idempotent regeneration. The companion
`readme_consumer` LISTENs on the `readme_dirty` channel emitted by the
0034 triggers and dispatches debounced regeneration.
"""
