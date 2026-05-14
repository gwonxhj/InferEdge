#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCK_FILE="$ROOT_DIR/repos.lock"
MODE="latest"

usage() {
  cat <<'USAGE'
Usage: bash scripts/update_all.sh [--locked|--latest]

Update existing InferEdge Core repository clones.

Options:
  --locked  Checkout the verified commit in repos.lock.
  --latest  Fast-forward the main branch. This is the default.

Environment:
  INFEREDGE_REPOS_DIR  Override repository directory root.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --locked) MODE="locked" ;;
    --latest) MODE="latest" ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage; exit 2 ;;
  esac
  shift
done

DEST_ROOT="${INFEREDGE_REPOS_DIR:-$ROOT_DIR/repos}"

while IFS=$'\t' read -r name url branch commit path; do
  [[ -z "${name:-}" || "$name" == \#* || "$name" == "name" ]] && continue
  repo_dir="$DEST_ROOT/$name"

  if [[ ! -d "$repo_dir/.git" ]]; then
    echo "missing repo: $repo_dir" >&2
    echo "run: bash scripts/clone_all.sh --$MODE" >&2
    exit 1
  fi

  echo "==> updating $name"
  git -C "$repo_dir" fetch origin "$branch"
  if [[ "$MODE" == "locked" ]]; then
    git -C "$repo_dir" checkout --detach "$commit"
  else
    git -C "$repo_dir" checkout "$branch"
    git -C "$repo_dir" pull --ff-only origin "$branch"
  fi
done < "$LOCK_FILE"

echo
echo "InferEdge repositories updated in: $DEST_ROOT"

