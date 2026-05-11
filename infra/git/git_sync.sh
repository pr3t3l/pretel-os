#!/usr/bin/env bash
# Hourly git sync for pretel-os main: pull (rebase + autostash) then push
# when the local branch is ahead. Invoked by pretel-os-gitsync.service via
# the matching .timer.
#
# Safe to run unattended:
#   - aborts if not on the expected branch (operator may be on a feature branch).
#   - uses --rebase --autostash so a dirty working tree is stashed and re-applied.
#   - if rebase conflicts, git aborts and restores state; this script exits non-zero
#     and the operator triages via `journalctl --user -u pretel-os-gitsync.service`.

set -euo pipefail

REPO="/home/pretel/dev/pretel-os"
BRANCH="main"
REMOTE="origin"

cd "$REPO"

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$CURRENT_BRANCH" != "$BRANCH" ]]; then
    echo "[git-sync] skip: HEAD is $CURRENT_BRANCH, not $BRANCH"
    exit 0
fi

git fetch --quiet "$REMOTE" "$BRANCH"

LOCAL=$(git rev-parse HEAD)
REMOTE_HEAD=$(git rev-parse "$REMOTE/$BRANCH")
BASE=$(git merge-base HEAD "$REMOTE/$BRANCH")

if [[ "$LOCAL" == "$REMOTE_HEAD" ]]; then
    echo "[git-sync] up-to-date with $REMOTE/$BRANCH"
    exit 0
fi

if [[ "$LOCAL" == "$BASE" ]]; then
    echo "[git-sync] behind — pulling"
    git pull --rebase --autostash "$REMOTE" "$BRANCH"
elif [[ "$REMOTE_HEAD" == "$BASE" ]]; then
    echo "[git-sync] ahead — pushing"
    git push "$REMOTE" "$BRANCH"
else
    echo "[git-sync] diverged — rebasing then pushing"
    git pull --rebase --autostash "$REMOTE" "$BRANCH"
    git push "$REMOTE" "$BRANCH"
fi

echo "[git-sync] done at $(date -Iseconds)"
