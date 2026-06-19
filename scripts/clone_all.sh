#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCK_FILE="$ROOT_DIR/repos.lock"
MODE="latest"

usage() {
  cat <<'USAGE'
Usage: bash scripts/clone_all.sh [--locked|--latest]

Clone all InferEdge pinned smoke repositories into ./repos by default.

Options:
  --locked  Clone/fetch and checkout the verified smoke commit in repos.lock.
  --latest  Clone/fetch the latest main branch. This is the default.

Environment:
  INFEREDGE_REPOS_DIR  Override clone destination directory.
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
mkdir -p "$DEST_ROOT"

while IFS=$'\t' read -r name url branch commit path; do
  [[ -z "${name:-}" || "$name" == \#* || "$name" == "name" ]] && continue
  repo_dir="$DEST_ROOT/$name"

  if [[ -d "$repo_dir/.git" ]]; then
    echo "==> $name already exists: $repo_dir"
    git -C "$repo_dir" fetch origin "$branch"
  else
    echo "==> cloning $name"
    git clone "$url" "$repo_dir"
  fi

  if [[ "$MODE" == "locked" ]]; then
    git -C "$repo_dir" fetch origin "$commit" || true
    git -C "$repo_dir" checkout --detach "$commit"
  else
    git -C "$repo_dir" checkout "$branch"
    git -C "$repo_dir" pull --ff-only origin "$branch"
  fi
done < "$LOCK_FILE"

echo
echo "InferEdge pinned smoke repositories are ready in: $DEST_ROOT"
