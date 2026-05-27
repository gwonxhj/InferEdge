#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPOS_ROOT="${INFEREDGE_REPOS_DIR:-$ROOT_DIR/repos}"
FULL=0

usage() {
  cat <<'USAGE'
Usage: bash scripts/smoke_all.sh [--full]

Run InferEdge cross-repo portfolio smoke checks.

Default checks:
  - Forge pytest + manifest validation
  - Runtime smoke + manifest identity test
  - Lab portfolio demo check + Core 4 conformance check
  - Lab Runtime Intelligence artifact smoke
  - AIGuard pytest + portfolio demo

Options:
  --full  Also run the full InferEdgeLab pytest suite.

Environment:
  INFEREDGE_REPOS_DIR  Override repository directory root.
  INFEREDGE_RUNTIME_INTELLIGENCE_SMOKE_OUT
                       Override Runtime Intelligence smoke output directory.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --full) FULL=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage; exit 2 ;;
  esac
  shift
done

require_repo() {
  local name="$1"
  local path="$REPOS_ROOT/$name"
  if [[ ! -d "$path/.git" ]]; then
    echo "missing repo: $path" >&2
    echo "run: bash scripts/clone_all.sh --locked" >&2
    exit 1
  fi
  printf '%s\n' "$path"
}

run_step() {
  local label="$1"
  shift
  echo
  echo "==> $label"
  "$@"
}

FORGE="$(require_repo InferEdgeForge)"
RUNTIME="$(require_repo InferEdge-Runtime)"
LAB="$(require_repo InferEdgeLab)"
AIGUARD="$(require_repo InferEdgeAIGuard)"
RUNTIME_INTELLIGENCE_SMOKE_OUT="${INFEREDGE_RUNTIME_INTELLIGENCE_SMOKE_OUT:-/tmp/inferedge_runtime_intelligence_chain_smoke}"

run_step "Forge tests" bash -lc "cd '$FORGE' && poetry run pytest -q"
run_step "Forge manifest validation" bash -lc "cd '$FORGE' && poetry run python -m inferedgeforge.cli validate-manifest --manifest tests/fixtures/runtime_handoff_manifest.json"

run_step "Runtime smoke" bash -lc "cd '$RUNTIME' && bash scripts/smoke_default.sh"
run_step "Runtime manifest identity" bash -lc "cd '$RUNTIME' && python3 tests/test_manifest_compare_identity.py"

run_step "Lab install" bash -lc "cd '$LAB' && poetry install --no-interaction"
run_step "Lab portfolio demo check" bash -lc "cd '$LAB' && poetry run inferedgelab portfolio-demo-check"
run_step "Lab Core 4 conformance check" bash -lc "cd '$LAB' && poetry run inferedgelab core4-conformance-check"
run_step "Lab Runtime Intelligence artifact smoke" bash -lc "cd '$LAB' && bash scripts/smoke_runtime_intelligence_chain.sh --output-dir '$RUNTIME_INTELLIGENCE_SMOKE_OUT'"
if [[ "$FULL" -eq 1 ]]; then
  run_step "Lab full pytest" bash -lc "cd '$LAB' && poetry run python3 -m pytest -q"
fi

run_step "AIGuard tests" bash -lc "cd '$AIGUARD' && python -m pytest -q -p no:cacheprovider"
run_step "AIGuard portfolio demo" bash -lc "cd '$AIGUARD' && python -m inferedge_aiguard.cli portfolio-demo --save-json /tmp/aiguard_portfolio_demo.json --save-md /tmp/aiguard_portfolio_demo.md"

echo
echo "InferEdge cross-repo smoke: pass"
