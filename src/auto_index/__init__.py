"""Auto-index worker (CONSTITUTION §2.6).

Drains `pending_embeddings` rows by calling OpenAI text-embedding-3-large
for each row's `source_text` and writing the resulting vector back to the
target table's `embedding` column. Listens on the `embedding_queue`
NOTIFY channel for real-time wakeups; falls back to a periodic scan to
catch rows missed when the daemon was down (Postgres does not replay
missed NOTIFYs).

Run as:  python -m auto_index
Stop as: SIGTERM (the systemd unit sends this on stop/restart).
"""
