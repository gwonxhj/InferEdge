#!/usr/bin/env bash
set -euo pipefail

FETCH_ORIGIN=0
BRANCH_PATTERN="codex/*"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/audit_branch_cleanup.sh [options]

Options:
  --fetch                 Fetch origin/main before building the inventory.
  --branch-pattern <glob> Local branch glob to inspect. Matching origin/<glob>
                          remote branches are also listed. Default: codex/*.
  -h, --help              Show this help.

This script prints a branch cleanup inventory only. It never deletes local or
remote branches. Treat the output as audit input, not a deletion list.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fetch)
      FETCH_ORIGIN=1
      shift
      ;;
    --branch-pattern)
      if [[ $# -lt 2 || -z "$2" ]]; then
        echo "Missing value for --branch-pattern" >&2
        exit 2
      fi
      BRANCH_PATTERN="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

if [[ "$FETCH_ORIGIN" -eq 1 ]]; then
  git fetch origin main
fi

echo "InferEdge branch cleanup audit"
CURRENT_BRANCH="$(git branch --show-current)"
echo "Current branch: $CURRENT_BRANCH"
echo "Branch pattern: $BRANCH_PATTERN"
if git rev-parse --verify --quiet origin/main >/dev/null; then
  echo "Origin main: $(git rev-parse --short origin/main) $(git log -1 --pretty=%s origin/main)"
else
  echo "Origin main: missing"
fi
echo

echo "Local cleanup inventory (audit input, not a deletion list):"
local_found=0
while IFS= read -r local_branch; do
  if [[ -z "$local_branch" ]]; then
    continue
  fi
  local_found=1
  if [[ "$local_branch" == "$CURRENT_BRANCH" ]]; then
    echo "- $local_branch (current; do not delete while checked out)"
  else
    echo "- $local_branch"
  fi
done < <(git branch --list "$BRANCH_PATTERN" --format='%(refname:short)')
if [[ "$local_found" -eq 0 ]]; then
  echo "- <none>"
fi
echo

echo "Remote cleanup inventory (audit input, not a deletion list):"
remote_found=0
while IFS= read -r remote_branch; do
  if [[ -z "$remote_branch" ]]; then
    continue
  fi
  remote_found=1
  echo "- $remote_branch"
done < <(git branch -r --list "origin/$BRANCH_PATTERN" --format='%(refname:short)')
if [[ "$remote_found" -eq 0 ]]; then
  echo "- <none>"
fi
echo

if git rev-parse --verify --quiet origin/main >/dev/null; then
  echo "Regular-merge ancestry candidates:"
  git branch --merged origin/main --format='%(refname:short)' \
    | grep -E "^${BRANCH_PATTERN//\*/.*}$" \
    | sed 's/^/- /' \
    || echo "- <none>"
else
  echo "Regular-merge ancestry candidates: origin/main missing"
fi
echo

cat <<'EOF'
Cleanup rule:
- Do not delete main.
- Do not delete the current checked-out branch.
- Do not delete any branch from this inventory alone.
- Remote inventory entries are branch refs to inspect, not proof of merged state.
- Squash-merged branches may not appear in git branch --merged origin/main.
- Verify the PR is closed as merged before deleting a local or remote branch.
- If the local gh token is invalid, use the authenticated GitHub connector/app
  or GitHub PR page to confirm the merged state.
EOF
