#!/usr/bin/env bash
# Create (or reuse) a git worktree checked out at a given ref, so evidence
# gathered from it is a real git checkout, not a copy or a description.
#
# Usage: checkout_worktree.sh <repo_root> <label> [ref]
#   repo_root  path to the repo working tree
#   label      short identifier for this checkout, e.g. qa-baseline
#   ref        ref to check out (defaults to HEAD)
#
# Prints the resulting worktree path on the last line of stdout.

set -euo pipefail

REPO_ROOT="${1:?Usage: checkout_worktree.sh <repo_root> <label> [ref]}"
LABEL="${2:?label required, e.g. qa-baseline}"
REF="${3:-HEAD}"

cd "$REPO_ROOT"

REPO_NAME="$(basename "$(pwd)")"
WORKTREE_DIR="../${REPO_NAME}-${LABEL}"

if [ -d "$WORKTREE_DIR" ]; then
  echo "[front-end-qa] Worktree already exists at $WORKTREE_DIR — reusing." >&2
else
  git worktree add "$WORKTREE_DIR" "$REF" >&2
  echo "[front-end-qa] Created worktree at $WORKTREE_DIR (ref: $REF)" >&2
fi

if [ -d "node_modules" ] && [ ! -e "$WORKTREE_DIR/node_modules" ]; then
  ln -s "$(pwd)/node_modules" "$WORKTREE_DIR/node_modules"
  echo "[front-end-qa] Symlinked node_modules into worktree (skipped reinstall)." >&2
fi

cd "$WORKTREE_DIR"
pwd
