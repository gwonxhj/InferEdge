#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DRY_RUN=0
SKIP_SMOKE=0
SKIP_PUBLISH_READY=0
FULL_SMOKE=0

usage() {
  cat <<'USAGE'
Usage: bash scripts/check_reviewer_verification_set.sh [options]

Run the InferEdge entrypoint reviewer verification set.

Default checks:
  - python -m pytest -q
  - git diff --check
  - bash scripts/smoke_all.sh
  - bash scripts/check_publish_ready.sh

Options:
  --dry-run              Print the command order without running checks.
  --skip-smoke           Skip the cross-repo portfolio smoke.
  --skip-publish-ready   Skip the publish readiness check.
  --full-smoke           Pass --full to scripts/smoke_all.sh.
  -h, --help             Show this help.

Notes:
  - Run scripts/clone_all.sh --locked before the smoke, or set
    INFEREDGE_REPOS_DIR to sibling InferEdge repositories.
  - For a local-only check when sibling repos or remote access are unavailable:
    bash scripts/check_reviewer_verification_set.sh --skip-smoke --skip-publish-ready
  - Jetson hardware is not required for this verification set.
  - Fresh sustained Jetson capture is a separate later evidence task.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --skip-smoke)
      SKIP_SMOKE=1
      shift
      ;;
    --skip-publish-ready)
      SKIP_PUBLISH_READY=1
      shift
      ;;
    --full-smoke)
      FULL_SMOKE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown option: $1" >&2
      usage
      exit 2
      ;;
  esac
done

cd "$ROOT_DIR"

run_step() {
  local label="$1"
  shift
  echo
  echo "==> $label"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf 'would_run:'
    printf ' %q' "$@"
    printf '\n'
    return 0
  fi
  "$@"
}

echo "InferEdge reviewer verification set"
echo "  root: $ROOT_DIR"
if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "  mode: dry-run"
fi
if [[ "$SKIP_SMOKE" -eq 1 ]]; then
  echo "  smoke: skipped"
fi
if [[ "$SKIP_PUBLISH_READY" -eq 1 ]]; then
  echo "  publish_readiness: skipped"
fi

run_step "Local pytest" python -m pytest -q
run_step "Patch whitespace check" git diff --check

if [[ "$SKIP_SMOKE" -eq 0 ]]; then
  smoke_cmd=(bash scripts/smoke_all.sh)
  if [[ "$FULL_SMOKE" -eq 1 ]]; then
    smoke_cmd+=(--full)
  fi
  run_step "Cross-repo portfolio smoke" "${smoke_cmd[@]}"
fi

if [[ "$SKIP_PUBLISH_READY" -eq 0 ]]; then
  run_step "Publish readiness" bash scripts/check_publish_ready.sh
fi

echo
echo "Reviewer verification set completed."
