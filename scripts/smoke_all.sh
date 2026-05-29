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
  INFEREDGE_REMOTE_FALLBACK_REGISTRY_SMOKE_OUT
                       Override fixture-only remote fallback registry smoke output directory.
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

require_marker() {
  local file="$1"
  local marker="$2"
  if [[ ! -f "$file" ]]; then
    echo "missing required artifact: $file" >&2
    exit 1
  fi
  if ! grep -qF "$marker" "$file"; then
    echo "missing required marker in $file: $marker" >&2
    exit 1
  fi
}

require_runtime_intelligence_remote_fallback_markers() {
  local bundle_summary="$RUNTIME_INTELLIGENCE_SMOKE_OUT/runtime_intelligence_bundle_manifest_gate_summary.md"
  local summary_md="$RUNTIME_INTELLIGENCE_SMOKE_OUT/runtime_anomaly_summary.md"
  local summary_html="$RUNTIME_INTELLIGENCE_SMOKE_OUT/runtime_anomaly_summary.html"

  require_marker "$bundle_summary" "expected_report_markers: remote fallback Lab context row declared"
  require_marker "$summary_md" "Remote fallback starter evidence"
  require_marker "$summary_md" "lab=Remote fallback starter evidence; evidence=remote_execution_recovered_by_fallback"
  require_marker "$summary_md" "remote_execution_recovered_by_fallback"
  require_marker "$summary_html" "Remote fallback starter evidence"
  require_marker "$summary_html" "lab=Remote fallback starter evidence; evidence=remote_execution_recovered_by_fallback"
}

FORGE="$(require_repo InferEdgeForge)"
RUNTIME="$(require_repo InferEdge-Runtime)"
LAB="$(require_repo InferEdgeLab)"
AIGUARD="$(require_repo InferEdgeAIGuard)"
RUNTIME_INTELLIGENCE_SMOKE_OUT="${INFEREDGE_RUNTIME_INTELLIGENCE_SMOKE_OUT:-/tmp/inferedge_runtime_intelligence_chain_smoke}"
REMOTE_FALLBACK_REGISTRY_SMOKE_OUT="${INFEREDGE_REMOTE_FALLBACK_REGISTRY_SMOKE_OUT:-/tmp/inferedge_remote_fallback_registry_marker_smoke}"

run_step "Remote fallback registry marker smoke" bash "$ROOT_DIR/scripts/smoke_remote_fallback_registry_marker.sh" --output-dir "$REMOTE_FALLBACK_REGISTRY_SMOKE_OUT"

run_step "Forge tests" bash -lc "cd '$FORGE' && poetry run pytest -q"
run_step "Forge manifest validation" bash -lc "cd '$FORGE' && poetry run python -m inferedgeforge.cli validate-manifest --manifest tests/fixtures/runtime_handoff_manifest.json"

run_step "Runtime smoke" bash -lc "cd '$RUNTIME' && bash scripts/smoke_default.sh"
run_step "Runtime manifest identity" bash -lc "cd '$RUNTIME' && python3 tests/test_manifest_compare_identity.py"

run_step "Lab install" bash -lc "cd '$LAB' && poetry install --no-interaction"
run_step "Lab portfolio demo check" bash -lc "cd '$LAB' && poetry run inferedgelab portfolio-demo-check"
run_step "Lab Core 4 conformance check" bash -lc "cd '$LAB' && poetry run inferedgelab core4-conformance-check"
run_step "Lab Runtime Intelligence artifact smoke" bash -lc "cd '$LAB' && bash scripts/smoke_runtime_intelligence_chain.sh --output-dir '$RUNTIME_INTELLIGENCE_SMOKE_OUT'"
run_step "Lab Runtime Intelligence remote fallback report marker gate" require_runtime_intelligence_remote_fallback_markers
if [[ "$FULL" -eq 1 ]]; then
  run_step "Lab full pytest" bash -lc "cd '$LAB' && poetry run python3 -m pytest -q"
fi

run_step "AIGuard tests" bash -lc "cd '$AIGUARD' && python -m pytest -q -p no:cacheprovider"
run_step "AIGuard portfolio demo" bash -lc "cd '$AIGUARD' && python -m inferedge_aiguard.cli portfolio-demo --save-json /tmp/aiguard_portfolio_demo.json --save-md /tmp/aiguard_portfolio_demo.md"

echo
echo "InferEdge cross-repo smoke: pass"
