#!/usr/bin/env bash
set -euo pipefail

ALLOW_DIRTY=0
ALLOW_MISSING_REMOTE=0
ALLOW_PLACEHOLDER_REMOTE=0
SKIP_REMOTE_CHECK=0

usage() {
  cat <<'EOF'
Usage:
  bash scripts/check_publish_ready.sh [options]

Options:
  --allow-dirty           Do not fail when the working tree has local changes.
  --allow-missing-remote  Do not fail when origin is not configured.
  --allow-placeholder-remote
                          Do not fail when origin still uses a documented
                          placeholder URL.
  --skip-remote-check     Do not contact origin to verify repository access.
  -h, --help              Show this help.

Checks:
  - current branch
  - latest commit
  - working tree cleanliness
  - origin remote presence
  - origin remote placeholder detection
  - origin remote reachability
  - origin branch fast-forward safety
  - local main checkout safety
  - suggested push command
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --allow-dirty)
      ALLOW_DIRTY=1
      shift
      ;;
    --allow-missing-remote)
      ALLOW_MISSING_REMOTE=1
      shift
      ;;
    --allow-placeholder-remote)
      ALLOW_PLACEHOLDER_REMOTE=1
      shift
      ;;
    --skip-remote-check)
      SKIP_REMOTE_CHECK=1
      shift
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

is_placeholder_remote() {
  case "$1" in
    *"<"*|*">"*|*"OWNER"*|*"REPO"*|*"owner/repo"*|*"YOUR_"*|*"EXAMPLE"*|*"example"*)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

check_origin_branch_state() {
  local branch_name="$1"
  local remote_url="$2"
  local remote_ref="refs/remotes/origin/$branch_name"

  if ! git ls-remote --exit-code --heads "$remote_url" "$branch_name" >/dev/null 2>&1; then
    echo "Origin branch: missing"
    return 0
  fi

  echo "Origin branch: exists"
  if ! git fetch --quiet origin "$branch_name"; then
    echo "Publish readiness: blocked"
    echo "Reason: could not fetch origin/$branch_name to verify publish safety." >&2
    exit 2
  fi

  if ! git rev-parse --verify --quiet "$remote_ref" >/dev/null; then
    echo "Publish readiness: blocked"
    echo "Reason: origin/$branch_name was not available after fetch." >&2
    exit 2
  fi

  if git merge-base --is-ancestor "$remote_ref" HEAD; then
    echo "Origin branch state: publishable"
  elif git merge-base --is-ancestor HEAD "$remote_ref"; then
    echo "Origin branch state: local-behind"
    echo "Publish readiness: blocked"
    echo "Reason: origin/$branch_name contains commits not present locally; integrate remote changes before publishing." >&2
    exit 2
  elif git merge-base HEAD "$remote_ref" >/dev/null 2>&1; then
    echo "Origin branch state: diverged"
    echo "Publish readiness: blocked"
    echo "Reason: local $branch_name and origin/$branch_name have diverged; integrate remote changes before publishing." >&2
    exit 2
  else
    echo "Origin branch state: unrelated-history"
    echo "Publish readiness: blocked"
    echo "Reason: origin/$branch_name exists but has no common history with local $branch_name; do not force push." >&2
    exit 2
  fi
}

print_push_guidance() {
  local branch_name="$1"
  local upstream

  if git rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1; then
    upstream="$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}')"
    echo "Upstream: $upstream"
    if [[ "$upstream" == "origin/$branch_name" ]]; then
      echo "Suggested publish command: git push"
    else
      echo "Upstream status: different branch"
      echo "Suggested publish command: git push -u origin $branch_name"
    fi
  else
    echo "Upstream: missing"
    echo "Suggested publish command: git push -u origin $branch_name"
  fi
}

print_local_main_safety() {
  local branch_name="$1"
  local upstream="${2:-}"

  if [[ "$branch_name" != "main" ]]; then
    return 0
  fi

  if [[ "$upstream" == "origin/main" ]]; then
    echo "Local main safety: upstream matches origin/main"
  else
    echo "Local main safety: review before publishing"
    echo "Reason: local main is not tracking origin/main; start review work from origin/main instead of pushing local main."
  fi
}

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

branch="$(git branch --show-current)"
if [[ -z "$branch" ]]; then
  echo "Publish readiness: failed"
  echo "Reason: detached HEAD; switch to a branch before publishing." >&2
  exit 1
fi

upstream_ref="$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)"
latest_commit="$(git rev-parse --short HEAD)"
latest_subject="$(git log -1 --pretty=%s)"
status_short="$(git status --short)"

echo "InferEdge publish readiness"
echo "Branch: $branch"
print_local_main_safety "$branch" "$upstream_ref"
echo "Latest commit: $latest_commit $latest_subject"

if [[ -n "$status_short" ]]; then
  echo "Working tree: dirty"
  if [[ "$ALLOW_DIRTY" -eq 0 ]]; then
    echo "Publish readiness: failed"
    echo "Reason: commit or clean local changes before publishing." >&2
    git status --short >&2
    exit 1
  fi
else
  echo "Working tree: clean"
fi

origin_url="$(git remote get-url origin 2>/dev/null || true)"
if [[ -z "$origin_url" ]]; then
  echo "Origin remote: missing"
  echo 'Next step: REMOTE_URL="<paste-real-git-remote-url-here>"'
  echo 'Then run: git remote add origin "$REMOTE_URL"'
  if [[ "$ALLOW_MISSING_REMOTE" -eq 0 ]]; then
    echo "Publish readiness: blocked"
    echo "Reason: origin remote is not configured." >&2
    exit 2
  fi
else
  echo "Origin remote: $origin_url"
  if is_placeholder_remote "$origin_url"; then
    echo "Origin remote status: placeholder"
    echo 'Next step: REMOTE_URL="<paste-real-git-remote-url-here>"'
    echo 'Then run: git remote set-url origin "$REMOTE_URL"'
    if [[ "$ALLOW_PLACEHOLDER_REMOTE" -eq 0 ]]; then
      echo "Publish readiness: blocked"
      echo "Reason: origin remote still uses a placeholder URL." >&2
      exit 2
    fi
    echo "Suggested publish command: replace placeholder origin first"
    echo "Publish readiness check completed."
    exit 0
  fi
  if [[ "$SKIP_REMOTE_CHECK" -eq 1 ]]; then
    echo "Origin reachability: skipped"
  elif git ls-remote "$origin_url" >/dev/null 2>&1; then
    echo "Origin reachability: ok"
    check_origin_branch_state "$branch" "$origin_url"
  else
    echo "Origin reachability: failed"
    echo "Publish readiness: blocked"
    echo "Reason: origin remote is not reachable; verify repository existence and access rights." >&2
    exit 2
  fi
  print_push_guidance "$branch"
fi

echo "Publish readiness check completed."
