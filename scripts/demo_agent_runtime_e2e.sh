#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPOS_ROOT="${INFEREDGE_REPOS_DIR:-$ROOT_DIR/repos}"
OUTPUT_DIR="$ROOT_DIR/reports/agent_runtime_e2e"
FRAMES=8
SUSTAINED_MODE="producer-backed"

usage() {
  cat <<'USAGE'
Usage: bash scripts/demo_agent_runtime_e2e.sh [--output-dir DIR] [--frames N] [--device-local]

Replay the Reliable Edge Agent Runtime contract chain:

  agent_manifest
  -> runtime result.agent
  -> orchestration_summary
  -> AIGuard guard_analysis
  -> Lab agent-runtime-report

This script is an extension smoke for local developer workspaces. It does not
replace the Core 4 portfolio smoke in scripts/smoke_all.sh.

Options:
  --output-dir DIR  Directory for generated evidence.
                    Default: ./reports/agent_runtime_e2e
  --frames N        Number of frame cycles for the Orchestrator sustained demo.
                    Default: 8
  --device-local   Use the Orchestrator device_local starter config.
                    Default uses the producer-backed sustained smoke config.
  -h, --help        Show this help.

Environment:
  INFEREDGE_REPOS_DIR          Override ./repos lookup root.
  INFEREDGE_FORGE_REPO         Override InferEdgeForge path.
  INFEREDGE_RUNTIME_REPO       Override InferEdge-Runtime path.
  INFEREDGE_ORCHESTRATOR_REPO  Override InferEdgeOrchestrator path.
  INFEREDGE_AIGUARD_REPO       Override InferEdgeAIGuard path.
  INFEREDGE_LAB_REPO           Override InferEdgeLab path.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir)
      OUTPUT_DIR="${2:?missing value for --output-dir}"
      shift 2
      ;;
    --frames)
      FRAMES="${2:?missing value for --frames}"
      shift 2
      ;;
    --device-local)
      SUSTAINED_MODE="device-local"
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

resolve_repo() {
  local env_value="$1"
  local repo_name="$2"
  local label="$3"
  local candidate

  if [[ -n "$env_value" ]]; then
    if [[ -d "$env_value/.git" ]]; then
      printf '%s\n' "$env_value"
      return 0
    fi
    echo "$label repo is not a git repository: $env_value" >&2
    exit 1
  fi

  for candidate in \
    "$REPOS_ROOT/$repo_name" \
    "$ROOT_DIR/../$repo_name" \
    "/Users/GwonHyeokJun/Documents/GitHub/$repo_name"
  do
    if [[ -d "$candidate/.git" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  echo "missing $label repo: $repo_name" >&2
  echo "set the matching INFEREDGE_*_REPO environment variable or clone it next to this repo." >&2
  exit 1
}

choose_python() {
  local repo="$1"
  if [[ -x "$repo/.venv/bin/python" ]]; then
    printf '%s\n' "$repo/.venv/bin/python"
  elif [[ -x "/opt/anaconda3/bin/python" ]]; then
    printf '%s\n' "/opt/anaconda3/bin/python"
  elif command -v python3 >/dev/null 2>&1; then
    command -v python3
  elif command -v python >/dev/null 2>&1; then
    command -v python
  else
    echo "python interpreter not found" >&2
    exit 1
  fi
}

require_file() {
  local path="$1"
  local label="$2"
  if [[ ! -f "$path" ]]; then
    echo "missing $label: $path" >&2
    exit 1
  fi
}

run_step() {
  local label="$1"
  shift
  echo
  echo "==> $label"
  "$@"
}

FORGE_REPO="$(resolve_repo "${INFEREDGE_FORGE_REPO:-}" InferEdgeForge "Forge")"
RUNTIME_REPO="$(resolve_repo "${INFEREDGE_RUNTIME_REPO:-}" InferEdge-Runtime "Runtime")"
ORCHESTRATOR_REPO="$(resolve_repo "${INFEREDGE_ORCHESTRATOR_REPO:-}" InferEdgeOrchestrator "Orchestrator")"
AIGUARD_REPO="$(resolve_repo "${INFEREDGE_AIGUARD_REPO:-}" InferEdgeAIGuard "AIGuard")"
LAB_REPO="$(resolve_repo "${INFEREDGE_LAB_REPO:-}" InferEdgeLab "Lab")"

ORCH_PYTHON="$(choose_python "$ORCHESTRATOR_REPO")"
AIGUARD_PYTHON="$(choose_python "$AIGUARD_REPO")"

FORGE_AGENT_MANIFEST="$FORGE_REPO/tests/fixtures/agent_manifest_vision.json"
RUNTIME_AGENT_RESULT="$ORCHESTRATOR_REPO/examples/agent_runtime/vision_runtime_result.json"

if [[ "$SUSTAINED_MODE" == "device-local" ]]; then
  ORCHESTRATOR_CONFIG="$ORCHESTRATOR_REPO/configs/agent_multi_workload_sustained_device_local.json"
  ORCHESTRATOR_CONFIG_LABEL="Orchestrator device_local sustained config"
  ORCHESTRATOR_MODE_MARKER="device_local"
  EXTRA_ORCHESTRATOR_MARKERS=("producer_sources" "device_local_producer_count")
else
  ORCHESTRATOR_CONFIG="$ORCHESTRATOR_REPO/configs/agent_multi_workload_sustained_safety_resource.json"
  ORCHESTRATOR_CONFIG_LABEL="Orchestrator producer-backed sustained config"
  ORCHESTRATOR_MODE_MARKER="sustained_high_load"
  EXTRA_ORCHESTRATOR_MARKERS=()
fi

require_file "$FORGE_AGENT_MANIFEST" "Forge agent_manifest fixture"
require_file "$RUNTIME_AGENT_RESULT" "Runtime result.agent fixture"
require_file "$ORCHESTRATOR_CONFIG" "$ORCHESTRATOR_CONFIG_LABEL"

mkdir -p "$OUTPUT_DIR"

FORGE_OUT="$OUTPUT_DIR/01_forge_agent_manifest_vision.json"
RUNTIME_OUT="$OUTPUT_DIR/02_runtime_result_agent.json"
ORCHESTRATION_OUT="$OUTPUT_DIR/03_orchestration_summary.json"
TEGRSTATS_SAMPLE_OUT="$OUTPUT_DIR/03_tegrastats_sample.log"
AIGUARD_JSON_OUT="$OUTPUT_DIR/04_aiguard_guard_analysis.json"
AIGUARD_MD_OUT="$OUTPUT_DIR/04_aiguard_guard_analysis.md"
LAB_JSON_OUT="$OUTPUT_DIR/05_lab_agent_runtime_report.json"
LAB_MD_OUT="$OUTPUT_DIR/05_lab_agent_runtime_report.md"

run_step "Record Forge agent_manifest contract input" cp "$FORGE_AGENT_MANIFEST" "$FORGE_OUT"
run_step "Record Runtime result.agent contract input" cp "$RUNTIME_AGENT_RESULT" "$RUNTIME_OUT"

cat > "$TEGRSTATS_SAMPLE_OUT" <<'EOF'
RAM 2048/7771MB SWAP 0/3885MB CPU [12%@1510] GR3D_FREQ 42% cpu@45.5C gpu@44.0C
EOF

run_step "Generate Orchestrator $SUSTAINED_MODE multi-workload sustained summary" \
  bash -lc "cd '$ORCHESTRATOR_REPO' && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src '$ORCH_PYTHON' -m inferedge_orchestrator run-multi-workload-sustained --config '$ORCHESTRATOR_CONFIG' --output '$ORCHESTRATION_OUT' --frames '$FRAMES' --tegrastats-log '$TEGRSTATS_SAMPLE_OUT'"

run_step "Generate AIGuard runtime reliability guard_analysis" \
  bash -lc "cd '$AIGUARD_REPO' && PYTHONDONTWRITEBYTECODE=1 '$AIGUARD_PYTHON' -m inferedge_aiguard.cli reason-orchestration --input '$ORCHESTRATION_OUT' --save-json '$AIGUARD_JSON_OUT' --save-md '$AIGUARD_MD_OUT'"

run_step "Generate Lab Agent Runtime Reliability report JSON" \
  bash -lc "cd '$LAB_REPO' && poetry run inferedgelab agent-runtime-report --orchestration-summary '$ORCHESTRATION_OUT' --guard-analysis '$AIGUARD_JSON_OUT' --format json --output '$LAB_JSON_OUT'"

run_step "Generate Lab Agent Runtime Reliability report Markdown" \
  bash -lc "cd '$LAB_REPO' && poetry run inferedgelab agent-runtime-report --orchestration-summary '$ORCHESTRATION_OUT' --guard-analysis '$AIGUARD_JSON_OUT' --format markdown --output '$LAB_MD_OUT'"

run_step "Validate schema markers" grep -q "inferedge-agent-manifest-v1" "$FORGE_OUT"
grep -q "inferedge-runtime-agent-task-v1" "$RUNTIME_OUT"
grep -q "inferedge-orchestration-summary-v1" "$ORCHESTRATION_OUT"
grep -q "inferedge-aiguard-diagnosis-v1" "$AIGUARD_JSON_OUT"
grep -q "inferedgelab-agent-runtime-reliability-report-v1" "$LAB_JSON_OUT"
grep -q "$ORCHESTRATOR_MODE_MARKER" "$ORCHESTRATION_OUT"
grep -q "multi_workload_sustained_summary" "$ORCHESTRATION_OUT"
if ((${#EXTRA_ORCHESTRATOR_MARKERS[@]} > 0)); then
  for marker in "${EXTRA_ORCHESTRATOR_MARKERS[@]}"; do
    grep -q "$marker" "$ORCHESTRATION_OUT"
  done
fi
grep -q "image_file" "$ORCHESTRATION_OUT"
grep -q "fastapi_request_fixture" "$ORCHESTRATION_OUT"
grep -q "resource_snapshot_fixture" "$ORCHESTRATION_OUT"
grep -q "resource_degradation_score" "$ORCHESTRATION_OUT"
grep -q "tegrastats_timeline" "$ORCHESTRATION_OUT"
grep -q "sustained_overload_risk" "$AIGUARD_JSON_OUT"
grep -q "profiled_workload_pressure" "$AIGUARD_JSON_OUT"
grep -q "thermal_resource_pressure" "$AIGUARD_JSON_OUT"
grep -q "max_total_queue_depth" "$LAB_JSON_OUT"
grep -q "profiled_workload_pressure" "$LAB_JSON_OUT"
grep -q "thermal_resource_pressure" "$LAB_JSON_OUT"
grep -q "sustained_overload_review" "$LAB_JSON_OUT"

echo
echo "Reliable Edge Agent Runtime e2e smoke ($SUSTAINED_MODE): pass"
echo
echo "Outputs:"
echo "  Forge agent manifest:       $FORGE_OUT"
echo "  Runtime result.agent:       $RUNTIME_OUT"
echo "  Orchestration summary:      $ORCHESTRATION_OUT"
echo "  Tegrastats sample:          $TEGRSTATS_SAMPLE_OUT"
echo "  AIGuard guard analysis:     $AIGUARD_JSON_OUT"
echo "  AIGuard Markdown report:    $AIGUARD_MD_OUT"
echo "  Lab report JSON:            $LAB_JSON_OUT"
echo "  Lab report Markdown:        $LAB_MD_OUT"
